"""
Yeastar <-> SIPcity SMS Adapter
================================
A lightweight Flask adapter that bridges the authentication and payload
format differences between Yeastar P-Series and the SIPcity SMS API.

PROBLEM
-------
Yeastar sends outbound SMS requests using:
    Authorization: Bearer {api_key}
    Body: { "from": "...", "to": "...", "text": "..." }

SIPcity expects:
    Authorization: Basic {base64(api_key:api_secret)}
    X-Api-Key: {api_key}
    Body: { "source": "...", "destinations": [...], "content": "..." }

This adapter sits between the two systems, translating both directions.

ARCHITECTURE
------------
Yeastar  -->  This Adapter  -->  SIPcity SMS API
                    |
SIPcity Webhook  -->  This Adapter  -->  Yeastar Webhook URL

SETUP
-----
1. Install dependencies:
       pip install flask requests

2. Set your credentials as environment variables:
       export SIPCITY_API_KEY=your-api-key
       export SIPCITY_API_SECRET=your-api-secret
       export YEASTAR_WEBHOOK_URL=https://your-yeastar-pbx/webhook/url
       export YEASTAR_SECRET=your-yeastar-secret   # optional

3. Run the adapter:
       python yeastar_sipcity_adapter.py

4. In Yeastar PBX portal (Messaging -> Message Channel -> Authentication):
       API Address for Sending Messages: https://your-adapter-host/send
       API Address for Verifying Authentication: https://your-adapter-host/verify
       Webhook URL: copy from Yeastar and set as YEASTAR_WEBHOOK_URL above

5. In SIPcity portal, register your adapter's inbound webhook URL:
       https://your-adapter-host/inbound

NOTES
-----
- This adapter must be hosted at a publicly accessible HTTPS endpoint
- For local testing use ngrok: ngrok http 5000
- See https://github.com/kiwibro01/sipcity-developer-docs for full API docs
"""

import os
import hmac
import hashlib
import base64
import uuid
import json
import logging
from flask import Flask, request, jsonify
import requests

# ── Configuration ─────────────────────────────────────────────────────────────
SIPCITY_API_KEY     = os.environ.get("SIPCITY_API_KEY", "<your-api-key>")
SIPCITY_API_SECRET  = os.environ.get("SIPCITY_API_SECRET", "<your-api-secret>")
SIPCITY_SEND_URL    = "https://sms.sipcity.com.au/api/v2/client/bulk-message"
YEASTAR_WEBHOOK_URL = os.environ.get("YEASTAR_WEBHOOK_URL", "<your-yeastar-webhook-url>")
YEASTAR_SECRET      = os.environ.get("YEASTAR_SECRET", "")  # optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def sipcity_auth_headers():
    """Build the two auth headers required by SIPcity."""
    token = base64.b64encode(
        f"{SIPCITY_API_KEY}:{SIPCITY_API_SECRET}".encode()
    ).decode()
    return {
        "Authorization": f"Basic {token}",
        "X-Api-Key": SIPCITY_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def verify_sipcity_signature(raw_body: bytes, provided_signature: str) -> bool:
    """
    Verify the X-SMS-Api-Signature header on incoming SIPcity webhooks.
    Signature = base64(HMAC-SHA256(raw_body, api_secret))
    """
    expected = base64.b64encode(
        hmac.new(
            SIPCITY_API_SECRET.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).digest()
    ).decode("utf-8")
    return hmac.compare_digest(expected, provided_signature)


def sign_for_yeastar(raw_body: bytes) -> str:
    """
    Generate the X-Signature-256 header value for outbound Yeastar webhooks.
    Format: sha256={lowercase-hex-signature}
    """
    sig = hmac.new(
        YEASTAR_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={sig}"


def extract_bearer_token(auth_header: str) -> str | None:
    """Extract the API key from a Bearer auth header."""
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/verify", methods=["GET"])
def verify():
    """
    Optional channel connectivity verification endpoint.
    Yeastar periodically calls this with a challenge code to verify the channel is live.
    Validates the Bearer token and echoes back the challenge code.
    """
    auth_header = request.headers.get("Authorization", "")
    token = extract_bearer_token(auth_header)

    if token != SIPCITY_API_KEY:
        log.warning("Verify: invalid Bearer token")
        return jsonify({
            "errors": [{
                "code": "10004",
                "title": "Authentication failed",
                "detail": "Invalid API key."
            }]
        }), 401

    challenge = request.args.get("challenge", "")
    log.info(f"Verify: challenge={challenge}")
    return challenge, 200


@app.route("/send", methods=["POST"])
def send():
    """
    Outbound SMS handler.
    Receives a Yeastar send request, translates it, and forwards to SIPcity.

    Yeastar sends:
        Authorization: Bearer {api_key}
        { "from": "...", "to": "...", "text": "..." }

    SIPcity expects:
        Authorization: Basic {base64(api_key:api_secret)}
        X-Api-Key: {api_key}
        { "source": "...", "destinations": ["..."], "content": "..." }
    """
    # Validate Bearer token from Yeastar
    auth_header = request.headers.get("Authorization", "")
    token = extract_bearer_token(auth_header)
    if token != SIPCITY_API_KEY:
        log.warning("Send: invalid Bearer token")
        return jsonify({
            "errors": [{"code": "10004", "title": "Authentication failed", "detail": "Invalid API key."}]
        }), 401

    # Parse Yeastar request body
    data = request.get_json()
    if not data:
        return jsonify({
            "errors": [{"code": "10002", "title": "Invalid parameter", "detail": "Request body is required."}]
        }), 400

    from_number = data.get("from", "")
    to_number   = data.get("to", "")
    text        = data.get("text", "")

    if not from_number or not to_number or not text:
        return jsonify({
            "errors": [{"code": "10002", "title": "Invalid parameter", "detail": "from, to, and text are required."}]
        }), 400

    # Translate to SIPcity format
    sipcity_body = {
        "source":       from_number,
        "destinations": [to_number],
        "content":      text,
    }

    log.info(f"Send: {from_number} -> {to_number} ({len(text)} chars)")

    # Forward to SIPcity
    try:
        response = requests.post(
            SIPCITY_SEND_URL,
            headers=sipcity_auth_headers(),
            json=sipcity_body,
            timeout=30
        )
        log.info(f"SIPcity response: {response.status_code} {response.text[:100]}")
    except requests.RequestException as e:
        log.error(f"SIPcity request failed: {e}")
        return jsonify({
            "errors": [{"code": "10007", "title": "Service unavailable", "detail": str(e)}]
        }), 500

    if response.status_code not in (200, 201):
        return jsonify({
            "errors": [{"code": "10007", "title": "Send failed", "detail": response.text}]
        }), response.status_code

    # Return Yeastar-compatible success response
    sipcity_data = response.json()
    message_id = sipcity_data.get("data", {}).get("message", {}).get("id", str(uuid.uuid4()))

    return jsonify({"data": {"id": message_id}}), 200


@app.route("/inbound", methods=["POST"])
def inbound():
    """
    Inbound webhook handler.
    Receives a SIPcity new-message webhook, verifies the HMAC signature,
    reformats, and forwards to Yeastar.

    SIPcity sends:
        X-SMS-Api-Signature: {base64(HMAC-SHA256(body, api_secret))}
        { "event_type": "new-message", "message": { ... } }

    Yeastar expects:
        X-Signature-256: sha256={lowercase-hex-signature}
        { "data": { "event_type": "message.received", "payload": { ... } } }
    """
    raw_body  = request.get_data()
    signature = request.headers.get("X-SMS-Api-Signature", "")

    # Verify SIPcity signature
    if not verify_sipcity_signature(raw_body, signature):
        log.warning("Inbound: invalid SIPcity signature")
        return jsonify({"error": "Invalid signature"}), 401

    data       = request.get_json()
    event_type = data.get("event_type", "")

    log.info(f"Inbound: event_type={event_type}")

    # status-update events are delivery receipts — log only, don't forward
    if event_type == "status-update":
        log.info("Inbound: status-update received, logging only")
        return "", 200

    if event_type != "new-message":
        log.warning(f"Inbound: unknown event_type={event_type}")
        return "", 200

    # Extract SIPcity message fields
    message      = data.get("message", {})
    destinations = message.get("destinations", [{}])
    to_number    = destinations[0].get("destination", "") if destinations else ""

    # Build Yeastar webhook payload
    yeastar_payload = {
        "data": {
            "event_type": "message.received",
            "id":         str(uuid.uuid4()),
            "occurred_at": message.get("received_at", ""),
            "payload": {
                "id":          message.get("id", str(uuid.uuid4())),
                "from": {"phone_number": message.get("source", "")},
                "to":   {"phone_number": to_number},
                "text":        message.get("content", ""),
                "media":       [{"url": u} for u in message.get("media_urls", [])],
                "received_at": message.get("received_at", ""),
                "record_type": "message",
                "type":        message.get("type", "sms").upper(),
            }
        }
    }

    # Serialise and sign for Yeastar
    yeastar_body = json.dumps(yeastar_payload, separators=(",", ":")).encode("utf-8")
    yeastar_headers = {
        "Content-Type":    "application/json",
        "X-Signature-256": sign_for_yeastar(yeastar_body) if YEASTAR_SECRET else "",
    }

    # Forward to Yeastar
    try:
        yeastar_response = requests.post(
            YEASTAR_WEBHOOK_URL,
            headers=yeastar_headers,
            data=yeastar_body,
            timeout=30
        )
        log.info(f"Yeastar response: {yeastar_response.status_code}")
    except requests.RequestException as e:
        log.error(f"Yeastar forward failed: {e}")

    # Always return 200 to SIPcity to prevent retries
    return "", 200


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Starting Yeastar <-> SIPcity adapter on port 5000")
    log.info("  /verify  — Yeastar channel connectivity check")
    log.info("  /send    — Outbound SMS (Yeastar -> SIPcity)")
    log.info("  /inbound — Inbound webhook (SIPcity -> Yeastar)")
    app.run(host="0.0.0.0", port=5000, debug=False)
