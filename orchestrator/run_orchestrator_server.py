from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os

from orchestrator.whisper_handler import transcribe_file
from orchestrator.llm_streamer import stream_llm_tokens
from orchestrator.tts_streamer import synthesize_audio_stream
from orchestrator.asterisk_streamer import stream_to_asterisk

AUDIO_STREAM_DIR = "/var/lib/asterisk/sounds/stream_audio"

app = FastAPI()


# --- Request Schema ---
class CallRequest(BaseModel):
    audio_path: str


# --- Token Grouping ---
def group_tokens(token_stream, max_words=8):
    buffer = []
    for token in token_stream:
        if not token.strip():
            continue
        buffer.append(token)
        if len(buffer) >= max_words or token.strip().endswith(('.', '!', '?', ',')):
            yield " ".join(buffer).strip()
            buffer.clear()
    if buffer:
        yield " ".join(buffer).strip()


# --- API Endpoint ---
@app.post("/call")
def process_call(req: CallRequest):
    audio_path = req.audio_path

    if not os.path.exists(audio_path):
        return {"status": "error", "message": f"File not found: {audio_path}"}

    print(f"[API] Processing audio: {audio_path}")
    transcript = transcribe_file(audio_path)
    print(f"[API] Transcript: {transcript}")

    token_stream = stream_llm_tokens(transcript)
    index = 0
    for phrase in group_tokens(token_stream, max_words=8):
        print(f"[LLM] {phrase}")
        audio_bytes = synthesize_audio_stream(phrase)
        if audio_bytes:
            filename = f"stream_{index:08d}.wav"
            filepath = os.path.join(AUDIO_STREAM_DIR, filename)
            stream_to_asterisk(audio_bytes, filepath)
            print(f"[TTS] Audio chunk written: {filename}")
            index += 1

    return {"status": "ok"}


# --- Run the server ---
if __name__ == "__main__":
    print("[Server] Starting AI orchestrator service on http://localhost:8100")
    uvicorn.run("orchestrator.run_orchestrator_server:app", host="0.0.0.0",
                port=8100, reload=False, access_log=True, log_level="info")
