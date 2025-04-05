# ai_call_center/orchestrator/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
from stt import transcribe_audio
from llm import stream_response
from tts import synthesize_audio_streaming
import os

app = FastAPI()

# Directories
INPUT_DIR = Path("audio/inputs")
OUTPUT_DIR = Path("audio/outputs")
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/process_audio")
async def process_audio(audio: UploadFile = File(...)):
    # Use uploaded filename (e.g., user_1.wav → response_1_segment_*.wav)
    original_name = Path(audio.filename).stem  # e.g., "user_1"
    turn_id = original_name.split("_")[-1]     # e.g., "1"
    input_path = INPUT_DIR / f"{original_name}.wav"
    base_output_path = OUTPUT_DIR / f"response_{turn_id}"

    # Save the uploaded audio
    with open(input_path, "wb") as f:
        f.write(await audio.read())

    # Step 1: Transcribe with Whisper
    transcript = transcribe_audio(str(input_path))
    if not transcript.strip():
        transcript = "Sorry, I didn't catch that."
    print(f"[STT] Transcript: {transcript}")

    # Step 2: Stream LLM tokens and synthesize audio chunks
    segment_paths = synthesize_audio_streaming(
        stream_response(transcript), str(base_output_path))
    print(f"[TTS] Generated {len(segment_paths)} audio segments.")

    # Return just the first audio segment to confirm AGI flow (rest played from disk)
    return FileResponse(segment_paths[0], media_type="audio/wav")
