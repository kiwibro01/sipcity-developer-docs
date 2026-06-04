# Zapier & N8N

Both the CDR webhook and SMS API work out of the box with no-code automation platforms like Zapier and N8N. Once connected, completed calls or sent messages can automatically trigger actions in HubSpot, Salesforce, or any other supported platform — no developer required.

## How it works

```
CDR:  Call ends  →  new-cdr webhook  →  Zapier / N8N  →  HubSpot / Salesforce
SMS:  Message sent  →  delivery webhook  →  Zapier / N8N  →  HubSpot / Salesforce
```

---

## 8.1 Zapier

Zapier's built-in Webhooks trigger can receive CDR or SMS payloads and pass the data to any of the apps in the Zapier ecosystem. Setup takes around 15 minutes and requires no coding.

1. Log in to Zapier and click **Create Zap**
2. Choose **Webhooks by Zapier** as the trigger and select **Catch Hook**
3. Copy the unique webhook URL Zapier provides
4. **CDR:** Register the URL in the portal under **Tools → Integrations → CDR**.  
   **SMS:** Use the [Subscribe a Webhook](sms-api.md#subscribe-a-webhook) endpoint
5. Make a test call or send a test SMS — Zapier captures the payload and maps all fields
6. Add your action step (HubSpot, Salesforce, etc.) and map the fields
7. Turn on the Zap

### Field Mapping Example (CDR → HubSpot)

| HubSpot Field | CDR Webhook Field | Notes |
|---------------|-------------------|-------|
| Contact phone number | `fromNumber` | Matches or creates contact |
| Call duration | `seconds` | Stored in seconds |
| Call direction | `direction` | `inbound` or `outbound` |
| Call outcome | `disconnectCause` | e.g. `Normal Clearing` |
| Call notes | `transcription.summary` | AI-generated summary |
| Recording link | `callRecordedFile` | Use with [recording API](cdr-api.md#42-download-a-call-recording) to fetch MP3 |

---

## 8.2 N8N

N8N is an open-source automation platform that offers more flexibility than Zapier, including self-hosting, conditional logic, and multi-step data transformation. It's ideal for teams who want full control over their automation workflows.

1. In N8N, create a new workflow and add a **Webhook** node as the trigger
2. Set HTTP method to **POST** and copy the generated URL
3. Register the URL as a CDR webhook in the portal (**Tools → Integrations → CDR**), or as an SMS webhook via the [API](sms-api.md#subscribe-a-webhook)
4. Click **Listen for test event** in N8N, then trigger a test call or SMS
5. Add downstream nodes — HubSpot, Salesforce, HTTP Request, etc.
6. Map CDR or SMS fields, add conditional logic, then activate the workflow

### N8N Tip — Fetching Recordings

Add an **HTTP Request** node after your CRM node. Set the URL to:

```
https://arena.yourcloudtelco.com.au/api/v1/recording/download/{{$json.callRecordedFile}}
```

Include your `X-Api-Key` and `Authorization` headers. The response `data` field contains the base64-encoded MP3 content.
