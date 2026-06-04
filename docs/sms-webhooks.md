# SMS Webhooks

The SMS service delivers two types of webhook events to your registered endpoint: delivery status updates for outbound messages, and notifications when inbound messages are received. Each request is signed using HMAC-SHA256 so you can verify it genuinely came from SIPcity.

---

## 7.1 Authentication & HMAC Signature Validation

> **⚠️ Always validate the signature before processing any webhook payload**
> Every webhook POST from the SMS service includes an `X-SMS-Api-Signature` header. You must verify this signature before acting on the payload to ensure the request is genuine and has not been tampered with.

Each incoming webhook request includes an `X-SMS-Api-Signature` header containing an HMAC-SHA256 signature of the raw request body, encoded in base64, using your `api_secret` as the key.

### How to Validate

1. Receive the raw request body — do not parse or reformat the JSON before hashing.
2. Calculate HMAC-SHA256 of the raw body using your `api_secret` as the key.
3. Base64-encode the result.
4. Compare it with the value of the `X-SMS-Api-Signature` header using a constant-time comparison.

> **JSON serialisation rules**
> The signature will only match if the JSON body is serialised exactly as sent:
> - Slashes `/` are **not** escaped (no `\/`) — use the raw body as received
> - Unicode characters are **not** escaped — `á` not `\u00e1`
>
> Do not re-serialise the JSON before computing the signature. Always hash the raw bytes of the received body.

### Validation Example (PHP)

```php
$body = file_get_contents('php://input');
$expectedSignature = base64_encode(
    hash_hmac('sha256', $body, $apiSecret, true)
);
$providedSignature = $_SERVER['HTTP_X_SMS_API_SIGNATURE'] ?? '';
if (!hash_equals($expectedSignature, $providedSignature)) {
    http_response_code(401);
    exit('Invalid signature');
}
```

### Validation Example (JavaScript / Node.js)

```javascript
const crypto = require('crypto');

function verifySignature(rawBody, apiSecret, providedSignature) {
  const expected = crypto
    .createHmac('sha256', apiSecret)
    .update(rawBody)
    .digest('base64');
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(providedSignature)
  );
}
```

### Worked Example

Given the following request body and `api_secret` of `mySecretKey123`:

```json
{
  "event_id": "b7e2d8c2-1234-4f7a-9e2a-abcdef123456",
  "event_type": "new-message",
  "message": {
    "id": "c1a2b3d4-5678-4e9f-8a7b-abcdef654321",
    "source": "+5511999999999",
    "content": "Hello, world! 😀",
    "type": "sms",
    "media_urls": []
  }
}
```

Expected `X-SMS-Api-Signature` value:

```
HFyijwA5UBlxgLyR5n15S0sqFtCyX/Uks3H/oHyU2ZE=
```

---

## 7.2 Testing Your Integration

The following Python script tests all four authentication approaches against the live SMS API. Use it to verify your credentials and confirm which auth method works before building your integration.

| Test | What it verifies |
|------|-----------------|
| Case 1 — HMAC(api_key) | `api_secret` as key, `api_key` as message — incorrect for outbound, included for completeness |
| Case 2 — HMAC(api_secret) | `api_key` as key, `api_secret` as message — incorrect for outbound, included for completeness |
| Case 3 — HMAC(body) | `api_secret` as key, raw JSON body as message — correct approach for outbound requests |
| Case 4 — Basic Auth | `base64(api_key:api_secret)` in Authorization header — required for all API calls |

See [examples/test_sms_auth.py](../examples/test_sms_auth.py) for the full script.

> **⚠️ Before running**
> Replace `<your-api-key>`, `<your-api-secret>`, `<your-source-number>`, and the destination numbers with your real values. Never commit credentials to source control.

---

## 7.3 Delivery Status Update (`status-update`)

Sent when there is a status change in outbound message destinations. Bulk message destinations are processed in batches and statuses may arrive asynchronously — handle each event independently and idempotently.

### Payload Example

```json
{
  "event_id": "<uuid>",
  "event_type": "status-update",
  "messages": [
    {
      "id": "<uuid>",
      "destinations": [
        {
          "id": "<uuid>",
          "status": "sent",
          "error_code": null,
          "status_updated_at": "2025-05-13T10:00:00Z"
        },
        {
          "id": "<uuid>",
          "status": "failed",
          "error_code": 1,
          "status_updated_at": "2025-05-13T10:01:00Z"
        }
      ]
    }
  ]
}
```

### Fields

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `event_id` | string | Unique identifier of the event | |
| `event_type` | string | Always `status-update` for this event | |
| `messages` | array | List of affected messages | |
| `messages[].id` | string | Message ID | |
| `destinations[].id` | string | Destination ID | |
| `destinations[].status` | string | New status of the destination | See [status table](#75-possible-statuses) |
| `destinations[].error_code` | int\|null | Error code if sending failed | See [error code table](#76-error-codes) |
| `status_updated_at` | string | Date/time of the status update | ISO 8601 |

---

## 7.4 Inbound Message Received (`new-message`)

Sent when a new inbound message is received by the system. This event supports both SMS and MMS.

### Payload Example

```json
{
  "event_id": "<uuid>",
  "event_type": "new-message",
  "message": {
    "id": "<uuid>",
    "source": "+61411000000",
    "content": "Hello, world!",
    "type": "sms",
    "media_urls": [],
    "received_at": "2025-05-13T10:05:00Z",
    "destinations": [
      {
        "id": "<uuid>",
        "destination": "+61480039847",
        "status": "readable",
        "status_updated_at": "2025-05-13T10:05:01Z"
      }
    ]
  }
}
```

### Fields

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `event_id` | string | Unique identifier of the event | |
| `event_type` | string | Always `new-message` for this event | |
| `message.id` | string | Message ID | |
| `message.source` | string | Source (sender) number | |
| `message.content` | string | Message content | |
| `message.type` | string | Message type | `sms` or `mms` |
| `media_urls` | array | URLs of attached media (empty for SMS) | MMS only |
| `received_at` | string | Date/time of receipt | ISO 8601 |
| `destinations[].destination` | string | The number that received the message | |
| `destinations[].status` | string | Current status | `readable` for inbound |

---

## 7.5 Possible Statuses

| Status | Description |
|--------|-------------|
| `sent` | Message successfully sent |
| `readable` | Available for reading (inbound or on-net messages only) |
| `failed` | Message sending failed — check the `error_code` field |

---

## 7.6 Error Codes

The following error codes may appear in the `error_code` field of a `status-update` event when `status` is `failed`:

| Code | Error | Description |
|------|-------|-------------|
| 1 | `SERVICE_UNAVAILABLE` | Service unavailable or unknown error during the request |
| 2 | `NUMBER_INVALID` | Invalid, not found, not allowed, or inactive number |
| 3 | `VALIDATION_ERROR` | The sending provider reported a validation error in the internal request |
| 4 | `REJECTED` | Message or number rejected by the destination provider |
| 5 | `UNAUTHORIZED` | Destination provider did not authorise due to account issues or other reasons |
| 6 | `INTERNAL_ERROR` | Internal server error |
| 7 | `UNDELIVERABLE` | Message could not be delivered (destination does not exist or route not found) |
| 8 | `DELETED_BY_PROVIDER` | Manually deleted by the provider (rare) |
| 9 | `EXPIRED` | Message expiration date exceeded |
| 10 | `TOO_LONG` | Message text too long |
| 11 | `INSUFFICIENT_BALANCE` | Insufficient balance to send the message |

---

## 7.7 Best Practices

- Always validate the HMAC signature before processing the payload.
- Respond quickly with HTTP 200 to avoid event resending.
- Implement logs to track received events and facilitate troubleshooting.
- The endpoint must be publicly accessible and accept HTTPS requests.
- Handle each event idempotently — bulk messages may generate multiple status events per destination.
- In case of delivery failure, the system may attempt to resend the event.
