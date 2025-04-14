# AI Call Center Backend

**Overview:**
This project is the backend engine for a fully autonomous AI-powered call center. It integrates a large language model (LLM), speech recognition, and text-to-speech to manage real-time phone conversations via Asterisk.

The system is designed to orchestrate and stream AI responses in live phone calls using:
- Whisper for speech-to-text (STT)
- DeepSeek LLM for conversation logic
- Coqui TTS for natural-sounding audio synthesis
- Asterisk for SIP media and call control

**Project Structure:**
- `orchestrator/` – Core Python modules handling LLM, TTS, STT, and Asterisk streaming logic
- `scripts/` – Utility shell and Python scripts to start calls, launch LLM, and AGI interaction
- `conf/` – Asterisk configuration
- `.vscode/` – Development environment settings
- `.gitignore` – Standard Git exclusions

**Key Components:**
- `orchestrator/main.py`: Entry point for FastAPI app orchestrating AI call flow
- `scripts/prepare_call.py`: Initiates outbound calls via `.call` files
- `scripts/agi_handler.sh`: Asterisk AGI script to control call flow
- `orchestrator/llm_streamer.py`: Streams LLM tokens during conversation
- `orchestrator/whisper_handler.py`: Transcribes recorded voice to text
- `orchestrator/tts_streamer.py`: Converts LLM response into audio using Coqui TTS
- `orchestrator/asterisk_streamer.py`: Handles audio segment playback via Asterisk

**Setup & Usage:**
```bash
# Install Python dependencies (make sure virtualenv is active)
pip install -r requirements.txt

# Start the orchestrator API server
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8100

# Start outbound call
python scripts/prepare_call.py +11234567890
```

**Tech Stack:**
- Python 3.10+
- FastAPI
- Whisper by OpenAI (STT)
- DeepSeek or Open LLM via vLLM (LLM)
- Coqui TTS
- Asterisk PBX

**Author:**
Dewayne Johnson (<dj@suncoast-software.com>)
