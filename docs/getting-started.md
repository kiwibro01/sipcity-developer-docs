# Getting Started

Complete the following steps once to connect either or both services.

---

## 2.1 Create an API Key

1. Go to **Tools → Integrations → CDR** in the portal
2. Click **Create New Key**
3. Give the key a name and click **Create**
4. Copy your **API Key** and **API Secret** from the confirmation dialog
5. Click **Download Credentials** and store them securely

> **⚠️ Your API Secret is only shown once**
> The API Secret is displayed in the confirmation dialog only. Once you close it, the secret cannot be retrieved. Download your credentials immediately and store them in a secrets manager or secure vault.

---

## 2.2 Register a CDR Webhook

1. On the CDR page, click **Create New Webhook URL**
2. Enter your publicly accessible HTTPS endpoint URL
3. Enable **Send Transcription & Media** to include transcription data in the payload
4. Click **Create**

---

## 2.3 Register an SMS Webhook

SMS webhooks are managed via the API rather than the portal. Use the [Subscribe a Webhook](sms-api.md#subscribe-a-webhook) endpoint to register your endpoint programmatically after your API key is created.

---

## 2.4 Verify Your Setup

**CDR:** Make a test call. Within seconds of it ending, your endpoint should receive a POST with a `new-cdr` payload.

**SMS:** Use the [Test a Webhook Subscription](sms-api.md#test-a-webhook-subscription) endpoint to send a `test-event` payload to your registered URL and confirm receipt.
