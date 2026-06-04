# SMS API

The SMS API lets you send bulk messages and manage webhook subscriptions for delivery status and inbound message notifications.

**Base URL:** `https://sms.sipcity.com.au`

> **Different base domain**
> The SMS API uses a different base domain (`https://sms.sipcity.com.au`) to the CDR API. This is expected — both services share the same authentication model. See [Authentication](authentication.md).

---

## 6.1 Send Bulk Message

Send the same SMS to multiple destination numbers in a single request. Delivery status notifications for each destination will be sent to your registered webhook.

```
POST api/v2/client/bulk-message
```

### Body Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | string | The sender number or ID. Example: `14809925966` |
| `destinations` | string[] | Array of destination phone numbers |
| `content` | string | The message text to send |

### Example Request (JavaScript)

```javascript
fetch('https://sms.sipcity.com.au/api/v2/client/bulk-message', {
  method: 'POST',
  headers: {
    'Authorization': 'Basic {token}',
    'X-Api-Key': 'your-api-key',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    source: '14809925966',
    destinations: ['1234567890', '0987654321'],
    content: 'Hello, this is a test message.'
  })
});
```

### Example Request (cURL)

```bash
curl --request POST \
  --url "https://sms.sipcity.com.au/api/v2/client/bulk-message" \
  --header "Authorization: Basic {token}" \
  --header "X-Api-Key: your-api-key" \
  --header "Content-Type: application/json" \
  --data '{
    "source": "14809925966",
    "destinations": ["1234567890", "0987654321"],
    "content": "Hello, this is a test message."
  }'
```

### Responses

**200 OK**
```json
{
  "success": true,
  "data": {
    "message": {
      "id": "97aaaa75-30ba-46f9-8d8f-f28b66827619",
      "source": "14809925966",
      "content": "Hello, this is a test message"
    }
  }
}
```

**403 Forbidden**
```json
{
  "success": false,
  "message": "Unauthorized action. Unable to send SMS with 14809925966."
}
```

**422 Unprocessable Entity**
```json
{
  "success": false,
  "message": "The given data was invalid.",
  "errors": {
    "content": ["The content field is required."],
    "destinations": ["The destinations field is required."]
  }
}
```

> **Source parameter format**
> Pass the source number as a plain string (e.g. `'14809925966'`). The auto-generated Scribe API reference may show the value with extra quotes — this is a documentation artefact; do not double-quote the value in your requests.

---

## 6.2 SMS Webhook Subscriptions

SMS webhooks are managed via the API rather than the portal. You can create, list, update, test, and delete subscriptions via the API.

### List Webhook Subscriptions

Retrieve all webhook subscriptions for your account.

```
GET api/v2/client/webhook-subscriptions
```

**Example response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "webhook_endpoint": "https://example.com/webhook",
      "created_at": "2025-05-01T12:00:00Z",
      "updated_at": "2025-05-01T12:00:00Z"
    }
  ]
}
```

---

### Subscribe a Webhook

Register a new webhook endpoint to receive SMS notifications.

```
POST api/v2/client/webhook-subscriptions
```

| Body Parameter | Description |
|----------------|-------------|
| `webhook_endpoint` | The publicly accessible HTTPS URL to receive webhook events |

**Example response (201 Created)**
```json
{
  "id": 1,
  "webhook_endpoint": "https://example.com/webhook",
  "created_at": "2025-05-01T12:00:00Z",
  "updated_at": "2025-05-01T12:00:00Z"
}
```

---

### Update a Webhook Subscription

Update the endpoint URL for an existing webhook subscription.

```
PUT /api/v2/client/webhook-subscriptions/{id}
PATCH /api/v2/client/webhook-subscriptions/{id}
```

| URL Parameter | Type | Description |
|---------------|------|-------------|
| `id` | integer | The ID of the webhook subscription to update |

| Body Parameter | Description |
|----------------|-------------|
| `webhook_endpoint` | The new HTTPS URL for the webhook endpoint |

---

### Delete a Webhook Subscription

Remove a webhook subscription permanently.

```
DELETE api/v2/client/webhook-subscriptions/{id}
```

**Response: 204 No Content**

---

### Test a Webhook Subscription

Send a test payload to a registered webhook to verify it is reachable.

```
POST api/v2/client/test-webhook-subscription/{id}
```

The test payload contains a fixed structure:

| Field | Value |
|-------|-------|
| `event_id` | uuid |
| `event_type` | `test-event` |
| `description` | `This is a test webhook payload.` |

**Example response (200 OK)**
```json
{
  "message": "Webhook test sent successfully.",
  "body": {
    "status": "success"
  }
}
```
