"""
SIPcity SMS API — Authentication Test Script

Tests all four authentication approaches against the live SMS API.
Use this to verify your credentials before building your integration.

Usage:
    1. Replace the placeholder values below with your real credentials
    2. Run: python test_sms_auth.py
    3. Check the summary to see which auth method succeeded
"""

import requests
import hmac
import hashlib
import base64
import json

# ─── Configuration ────────────────────────────────────────────────────────────
# Replace these values with your real credentials from Tools → Integrations → CDR

API_URL    = "https://sms.sipcity.com.au/api/v2/client/bulk-message"
API_KEY    = "<your-api-key>"
API_SECRET = "<your-api-secret>"

BODY_DATA = {
    "source": "<your-source-number>",
    "destinations": [
        "<destination-number-1>",
        "<destination-number-2>",
    ],
    "content": "This is a test SMS. Just making sure everything is working fine!"
}
# ─────────────────────────────────────────────────────────────────────────────


def test_hmac_case1():
    """
    Case 1: HMAC-SHA256(api_key, api_secret)
    api_secret as key, api_key as message.
    Included for completeness — this is NOT the correct approach for outbound requests.
    """
    print("\nTEST 1: HMAC-SHA256 — Case 1 (api_key as message)")
    signature = base64.b64encode(
        hmac.new(
            API_SECRET.encode("utf-8"),
            API_KEY.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")
    headers = {
        "X-SMS-Api-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": API_KEY,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=BODY_DATA, timeout=30)
        print(f"  Status: {response.status_code}  |  {response.text[:120]}")
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_hmac_case2():
    """
    Case 2: HMAC-SHA256(api_secret, api_key)
    api_key as key, api_secret as message.
    Included for completeness — this is NOT the correct approach for outbound requests.
    """
    print("\nTEST 2: HMAC-SHA256 — Case 2 (api_secret as message)")
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode("utf-8"),
            API_SECRET.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")
    headers = {
        "X-SMS-Api-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": API_KEY,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=BODY_DATA, timeout=30)
        print(f"  Status: {response.status_code}  |  {response.text[:120]}")
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_hmac_case3():
    """
    Case 3: HMAC-SHA256(body, api_secret)
    api_secret as key, raw JSON body as message.
    This is the correct approach for signing outbound webhook requests.

    IMPORTANT: Use data= (raw bytes) not json= so the body is not re-serialised
    by the requests library. The signature must match the exact bytes sent.
    """
    print("\nTEST 3: HMAC-SHA256 — Case 3 (body as message) ← correct for webhooks")
    body_json = json.dumps(BODY_DATA, separators=(",", ":"), ensure_ascii=False)
    signature = base64.b64encode(
        hmac.new(
            API_SECRET.encode("utf-8"),
            body_json.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")
    headers = {
        "X-SMS-Api-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": API_KEY,
    }
    try:
        # Use data= with raw bytes — do NOT use json= or the body will be re-serialised
        response = requests.post(
            API_URL,
            headers=headers,
            data=body_json.encode("utf-8"),
            timeout=30
        )
        print(f"  Status: {response.status_code}  |  {response.text[:120]}")
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_basic_auth():
    """
    Case 4: Basic Authentication
    base64(api_key:api_secret) in the Authorization header.
    This is the required auth method for all SIPcity API calls.
    """
    print("\nTEST 4: Basic Authentication ← required for all API calls")
    encoded = base64.b64encode(
        f"{API_KEY}:{API_SECRET}".encode("utf-8")
    ).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": API_KEY,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=BODY_DATA, timeout=30)
        print(f"  Status: {response.status_code}  |  {response.text[:120]}")
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 60)
    print("  SIPcity SMS API — Authentication Test")
    print("=" * 60)
    print(f"  API URL: {API_URL}")
    print(f"  API Key: {API_KEY}")

    results = {
        "HMAC Case 1 (api_key as message)":    test_hmac_case1(),
        "HMAC Case 2 (api_secret as message)": test_hmac_case2(),
        "HMAC Case 3 (body as message)":       test_hmac_case3(),
        "Basic Auth":                          test_basic_auth(),
    }

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for name, ok in results.items():
        status = "✓ SUCCESS" if ok else "✗ FAILED"
        print(f"  {name:40} {status}")
    print()


if __name__ == "__main__":
    main()
