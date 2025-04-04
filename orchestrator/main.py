# ai_call_center/orchestrator/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from stt import transcribe_audio
from llm import generate_response
from tts import synthesize_audio
import os
from pathlib import Path

app = FastAPI()
INPUT_PATH = "audio/inputs/user.wav"
OUTPUT_PATH = "audio/outputs/response.wav"


@app.post("/process_audio")
async def process_audio(audio: UploadFile = File(...)):
    input_path = Path(INPUT_PATH)
    output_path = Path(OUTPUT_PATH)

    # Save uploaded audio
    with open(input_path, "wb") as f:
        f.write(await audio.read())

    # Transcribe → Generate → Synthesize
    transcript = transcribe_audio(str(input_path))
    ai_response = generate_response(transcript)
    synthesize_audio(ai_response, str(output_path))

    # Return audio file as response
    return FileResponse(output_path, media_type="audio/wav")
