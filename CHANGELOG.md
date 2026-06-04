# Changelog

All notable changes to the SIPcity Developer Documentation are recorded here.

---

## Version 2 — June 2026

### Added
- **Section 7 — SMS Webhooks** (new section, split out from Section 6)
  - HMAC signature validation (`X-SMS-Api-Signature`) with PHP and JavaScript code examples and a worked example with known body, secret, and expected signature output
  - `status-update` event — full payload schema and field table, including note on asynchronous batch processing
  - `new-message` event — inbound SMS and MMS support, previously undocumented
  - Full error code table (11 codes)
  - Best practices including idempotency guidance
- **Section 7.2 — Testing Your Integration** — Python script testing all four authentication approaches against the live API
- **Section 1** — Added HMAC validation and inbound SMS to capability list
- **Section 3** — Added API secret one-time visibility warning to Authentication section
- **Section 6** — Added note on Scribe double-quoting artefact in source parameter examples
- `examples/test_sms_auth.py` — standalone Python auth test script

### Fixed
- SMS delivery status values corrected from `delivered / failed / pending` to `sent / readable / failed` to match the live API

### Nothing removed
All v1 content is preserved unchanged.

---

## Version 1 — April 2026

Initial release covering:
- CDR API and webhooks (`new-cdr` event)
- Recording download API
- Transcription with speaker diarisation and sentiment analysis
- SMS bulk messaging API
- SMS webhook subscription management (CRUD)
- Zapier and N8N integration guide
