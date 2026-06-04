# Qwen TTS Wrapper

OpenAI-compatible API wrapper for Qwen-TTS with voice cloning support, designed for LiveKit integration.

## Features

- ✅ OpenAI-compatible `/v1/audio/speech` endpoint
- ✅ Voice cloning via `/v1/audio/voice-clone`
- ✅ STT wrapper via `/v1/audio/transcriptions`
- ✅ Persistent voice storage
- ✅ Docker support

## Quick Start

### Docker Compose

```bash
# Copy environment example
cp .env.example .env

# Edit .env with your backend URLs
# VOICE_CLONE_URL=http://your-qwen-tts:8889/v1/audio/voice-clone
# WHISPER_URL=http://your-whisper:8001/v1/audio/transcriptions

# Start the wrapper + Gradio UI
docker-compose up -d

# Check logs
docker-compose logs -f

# Access:
# - API: http://localhost:8880
# - Gradio UI: http://localhost:7860
```

### Manual

```bash
pip install fastapi uvicorn httpx python-multipart pydantic gradio
python3 app.py
```

### Gradio UI

```bash
# Start only Gradio (API must be running)
python3 gradio_app.py

# Access: http://localhost:7860
```

## Gradio Interface Features

The web interface provides:

1. **🔊 Clone Voice** - Upload audio samples and create cloned voices
2. **📝 Generate Speech** - Convert text to speech using cloned voices
3. **📋 Manage Voices** - View, test, and delete cloned voices
4. **⚙️ Settings** - View configuration and connection status

## API Endpoints

### 1. Create Custom Voice

Clone a voice from an audio sample (WAV, MP3, etc.)

```bash
curl -X POST http://localhost:8880/v1/audio/voice-clone \
  -F "voice_name=myvoice" \
  -F "file=@sample.wav"
```

Response:
```json
{
  "status": "success",
  "voice_name": "myvoice",
  "reference_file": "voices/myvoice_reference.wav"
}
```

### 2. Text-to-Speech (with cloned voice)

```bash
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, this is my cloned voice!", "voice_name": "myvoice"}' \
  --output output.wav
```

### 3. Speech-to-Text

```bash
curl -X POST http://localhost:8880/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "language=en"
```

## LiveKit Integration

### LiveKit Agents Setup

In your LiveKit agent, configure the TTS client to use the wrapper:

```python
from livekit.agents import tts
import httpx

# Configure OpenAI-compatible client
tts_client = tts.OpenAITTS(
    base_url="http://qwen-tts-wrapper:8880/v1",
    api_key="not-needed",  # Not required
    model="qwen3-tts"
)

# Use a cloned voice
voice = tts.OpenAIVoice(id="myvoice")

# Generate speech
async for chunk in tts_client.synthesize(
    text="Hello from LiveKit with cloned voice!",
    voice=voice
):
    # Process audio chunks
    pass
```

### LiveKit Server Configuration

Add to your `livekit.yaml` or environment:

```yaml
# Or via environment variables
LIVEKIT_TTS_BASE_URL: http://qwen-tts-wrapper:8880/v1
LIVEKIT_TTS_API_KEY: not-needed
LIVEKIT_TTS_MODEL: qwen3-tts
```

### Using Custom Voices in LiveKit

1. **Clone the voice first:**
```bash
curl -X POST http://qwen-tts-wrapper:8880/v1/audio/voice-clone \
  -F "voice_name=agent_voice" \
  -F "file=@/path/to/voice_sample.wav"
```

2. **Use in your agent:**
```python
from livekit.plugins import openai

tts = openai.TTS(
    base_url="http://qwen-tts-wrapper:8880/v1",
    voice="agent_voice"  # Use cloned voice name
)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VOICE_CLONE_URL` | `http://10.224.0.190:8889/v1/audio/voice-clone` | Qwen-TTS voice clone endpoint |
| `WHISPER_URL` | `http://10.224.0.190:8001/v1/audio/transcriptions` | Whisper STT endpoint |
| `TTS_URL` | `http://10.224.0.190:8889/v1/audio/speech` | Qwen-TTS standard synthesis |
| `FIXED_REFERENCE_TEXT` | `Hello, this is a standard reference voice sample.` | Reference text for voice cloning |

## Testing

### Latency Test

```bash
# Run 10 latency tests
./latency_test.sh

# Custom configuration
VOICE_NAME=myvoice RUNS=20 ./latency_test.sh
```

### Full Benchmark

```bash
# TTS only (5 runs)
RUNS=5 MODE=tts-only ./benchmark_pipeline-nocache.sh

# Full pipeline (LLM + TTS + STT)
RUNS=100 MODE=full ./benchmark_pipeline-nocache.sh
```

## Directory Structure

```
qwen-tts-wrapper/
├── app.py                 # Main wrapper application
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker image
├── .env.example          # Environment variables template
├── voices/               # Cloned voice storage
│   ├── {name}_reference.wav
│   └── {name}_transcript.txt
├── latency_test.sh       # Latency testing script
└── benchmark_pipeline-nocache.sh  # Full benchmark
```

