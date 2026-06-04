# Transcription

> **Processed on private infrastructure**
> Transcription is processed entirely on SIPcity's private GPU infrastructure. Your call data is never sent to a third-party AI service — ensuring full data sovereignty and compliance with your privacy obligations.

When enabled on your CDR webhook, every completed call automatically generates a full transcription object included in the `new-cdr` payload. The transcription includes a verbatim transcript with speaker diarisation, per-utterance sentiment analysis, and an AI-generated summary of the call.

---

## 5.1 Enabling Transcription

Transcription is enabled per webhook. When registering or editing a CDR webhook in the portal:

1. Go to **Tools → Integrations → CDR**
2. Create a new webhook or edit an existing one
3. Enable the **Send Transcription & Media** toggle
4. Click **Save** — transcription will be included in all subsequent `new-cdr` payloads

---

## 5.2 Transcription Object

The `transcription` field is returned as an object within the `new-cdr` webhook payload. It contains three top-level fields:

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | AI-generated plain-language summary of the call |
| `sentimentAnalysisSummary` | object | Aggregate sentiment breakdown for the entire call (Neutral, Positive, Negative) expressed as percentage strings |
| `logs` | array | Ordered array of utterances — one entry per speaker turn, with speaker label, message text, and per-utterance sentiment |

---

## 5.3 Log Entry (Speaker Turn)

Each entry in the `logs` array represents a single speaker turn:

| Field | Type | Description |
|-------|------|-------------|
| `speaker` | string | Speaker label assigned by diarisation (e.g. `Speaker 0`, `Speaker 1`). Speaker 0 is typically the first voice heard on the call. |
| `message` | string | Verbatim transcribed text for this utterance |
| `sentimentAnalysis` | object | Per-utterance sentiment result — contains `category` (Neutral / Positive / Negative) and `strength` (float 0–1) |

---

## 5.4 Full Transcription Payload Example

```json
{
  "transcription": {
    "summary": "The caller enquired about their outstanding invoice. The agent confirmed the amount and advised payment could be made via the portal.",
    "sentimentAnalysisSummary": {
      "Neutral": "72.50",
      "Positive": "22.00",
      "Negative": "5.50"
    },
    "logs": [
      {
        "speaker": "Speaker 0",
        "message": "Hi, I'm calling about invoice number 4821.",
        "sentimentAnalysis": { "category": "Neutral", "strength": 0.82 }
      },
      {
        "speaker": "Speaker 1",
        "message": "Of course, I can see that invoice. The amount is $240.00.",
        "sentimentAnalysis": { "category": "Neutral", "strength": 0.91 }
      },
      {
        "speaker": "Speaker 0",
        "message": "Great, I'll get that sorted through the portal today.",
        "sentimentAnalysis": { "category": "Positive", "strength": 0.74 }
      }
    ]
  }
}
```

---

## 5.5 Speaker Diarisation

Speaker labels (`Speaker 0`, `Speaker 1`, etc.) are assigned automatically based on voice separation. On an inbound call, Speaker 0 is typically the caller and Speaker 1 is the agent, but this may vary depending on call routing. Labels are consistent within a single call but not across calls.

The `transcription` field will be `null` if:
- Transcription is not enabled on the webhook, or
- The call duration was too short to generate a meaningful transcript

---

> **Transcription pricing**
> API transcription is billed separately. Contact our sales team for pricing.
