import whisper
import os

model = whisper.load_model("base", device="cpu")


def transcribe_file(audio_path: str) -> str:
    print("[STT] Transcribing...")
    if not os.path.exists(audio_path):
        print(f"[STT Error] Expected file missing: {audio_path}")
        return ""

    try:
        result = model.transcribe(audio_path, fp16=False, language="en")
        transcript = result.get("text", "")
        print(f"[STT] Transcript: {transcript}")
        return transcript
    except Exception as e:
        print(f"[STT Error] {e}")
        return ""
