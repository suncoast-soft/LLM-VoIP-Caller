from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os

from orchestrator.whisper_handler import transcribe_file
from orchestrator.llm_streamer import stream_llm_tokens
from orchestrator.tts_streamer import synthesize_full_response_audio

AUDIO_STREAM_DIR = "/var/lib/asterisk/sounds"
USER_INPUT_DIR = "/tmp"

app = FastAPI()


# --- Request Schema ---
class CallRequest(BaseModel):
    call_id: str
    intro_text: str | None = None


# --- API Endpoint ---
@app.post("/call")
def process_call(req: CallRequest):
    call_id = req.call_id

    if req.intro_text:
        intro_path = os.path.join(AUDIO_STREAM_DIR, f"intro_{call_id}.wav")
        success = synthesize_full_response_audio(req.intro_text, intro_path)
        if not success:
            return {"status": "error", "message": "Failed to generate intro."}
        print(f"[TTS] Intro generated for call {call_id}")
    else:
        user_audio_path = os.path.join(
            USER_INPUT_DIR, f"user_input_{call_id}.wav")
        if not os.path.exists(user_audio_path):
            return {"status": "error", "message": f"Missing user input: {user_audio_path}"}

        transcript = transcribe_file(user_audio_path)
        print(f"[STT] Transcript: {transcript}")

        full_text = "".join(stream_llm_tokens(transcript))
        print(f"[LLM] Response: {full_text}")

        response_path = os.path.join(
            AUDIO_STREAM_DIR, f"response_{call_id}.wav")
        success = synthesize_full_response_audio(full_text, response_path)
        if not success:
            return {"status": "error", "message": "Failed to generate response."}

    return {"status": "ok", "message": f"Call {call_id} processed."}


# --- Run the server ---
if __name__ == "__main__":
    print("[Server] Starting AI orchestrator service on http://localhost:8100")
    uvicorn.run("orchestrator.main:app", host="0.0.0.0",
                port=8100, reload=False, access_log=True, log_level="info")
