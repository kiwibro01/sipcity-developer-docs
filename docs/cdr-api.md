# CDR API & Webhooks

The CDR service gives you real-time call data and access to call recordings. When a call ends, a webhook fires automatically to your registered endpoint. You can then use the recording download API to fetch the audio.

## End-to-End Flow

```
Call ends  →  new-cdr webhook fires  →  Your system receives payload
           →  Use callRecordedFile to download recording
```

---

## 4.1 CDR Record Event (`new-cdr`)

Sent automatically via HTTP POST to your registered endpoint whenever a call finishes.

### Key Payload Fields

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `direction` | string | `inbound` or `outbound` | |
| `fromNumber` | string | Originating number | |
| `dstNumber` | string | Destination number | |
| `utcDateTime` | string | Call start time in UTC | ISO 8601 |
| `seconds` | string | Total call duration in seconds | |
| `charge` | string | Amount charged (inc. tax) | |
| `currencyUsed` | string | Currency code | e.g. `AUD` |
| `callRecorded` | string | `True` if a recording was captured | |
| `callRecordedFile` | string | Base64-encoded recording filename | Use as `{id}` in download API |
| `disconnectCause` | string | Reason the call ended | e.g. `Normal Clearing` |
| `rawID` | string | Unique call identifier | Use to detect duplicates |
| `transcription` | object | Transcription, sentiment, AI summary | See [Transcription](transcription.md) |

### Payload Example

```json
{
  "event_type": "new-cdr",
  "message": {
    "direction": "outbound",
    "fromNumber": "61480039847",
    "dstNumber": "61296679111",
    "utcDateTime": "2026-03-26 18:16:07",
    "seconds": "60",
    "charge": "0.0396",
    "currencyUsed": "AUD",
    "callRecorded": "True",
    "callRecordedFile": "MjAyNjA0MTAvNjE...",
    "rawID": "9fa892ac5f7aac55718cb1cd5dd736af",
    "_id": "69c577eea058f3abab889092",
    "disconnectCause": "Normal Clearing",
    "transcription": { }
  }
}
```

### Best Practices

- Respond with HTTP 200 immediately. The system may retry on delivery failure — check `rawID` or `_id` and skip events you have already processed (idempotency).
- Your endpoint must be publicly accessible and accept HTTPS POST requests.
- Log all received events to assist with troubleshooting.
- Fields may contain `null` values when not applicable.

---

## 4.2 Download a Call Recording

Retrieves the binary content of a call recording. Pass the `callRecordedFile` value from the CDR webhook payload as the `{id}` parameter.

```
GET api/v1/recording/download/{id}
```

**Base URL:** `https://arena.yourcloudtelco.com.au`

### Required Headers

| Header | Value |
|--------|-------|
| `Content-Type` | `application/json` |
| `Accept` | `application/json` |
| `Authorization` | `Basic base64(api_key:api_secret)` |
| `X-Api-Key` | Your API key |

### Responses

**200 OK**
```json
{
  "success": true,
  "message": "Media download requested",
  "data": "base64_encoded_binary_content..."
}
```

**401 Unauthorized**
```json
{ "success": false, "message": "Invalid credentials" }
```

**404 Not Found**
```json
{ "success": false, "message": "File not found" }
```

### Example Request (cURL)

```bash
curl --request GET \
  --url "https://arena.yourcloudtelco.com.au/api/v1/recording/download/{id}" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json" \
  --header "Authorization: Basic base64(api_key:api_secret)" \
  --header "X-Api-Key: your-api-key"
```
