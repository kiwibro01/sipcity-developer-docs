# SIPcity Developer Documentation

**API & Webhooks Integration Guide**

> Version 2 · June 2026

This repository contains the official developer documentation for the SIPcity platform API and webhook services.

## What you can do

- Receive real-time webhook notifications when a call completes, including metadata, transcription, and sentiment analysis
- Download call recordings programmatically via the CDR API
- Transcribe calls automatically with speaker diarisation, sentiment analysis, and AI-generated summaries — processed entirely on SIPcity's private infrastructure
- Send bulk SMS messages to multiple destinations in a single request
- Manage SMS webhook subscriptions to receive delivery status and inbound message notifications
- Validate incoming webhook requests using HMAC signature verification
- Connect any service to HubSpot, Salesforce, or any other platform using Zapier or N8N

## Base URLs

| Service | Base URL |
|---------|----------|
| CDR API | https://arena.yourcloudtelco.com.au |
| SMS API | https://sms.sipcity.com.au |

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](docs/getting-started.md) | Create API keys, register webhooks, verify your setup |
| [Authentication](docs/authentication.md) | Headers, Base64 encoding, credential security |
| [CDR API & Webhooks](docs/cdr-api.md) | Call detail records, webhook payloads, recording download |
| [Transcription](docs/transcription.md) | Speaker diarisation, sentiment analysis, AI summaries |
| [SMS API](docs/sms-api.md) | Bulk messaging, webhook subscription management |
| [SMS Webhooks](docs/sms-webhooks.md) | HMAC validation, event payloads, error codes |
| [Zapier & N8N](docs/zapier-n8n.md) | No-code automation, HubSpot and Salesforce integration |

## Examples

| File | Description |
|------|-------------|
| [examples/test_sms_auth.py](examples/test_sms_auth.py) | Python script to test all four SMS API authentication methods |

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

> **Your API Secret is only shown once.** When you create an API key, the secret is displayed only at that moment. Download your credentials immediately and store them securely. If you lose it, you will need to create a new key.
