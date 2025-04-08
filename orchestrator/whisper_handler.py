import whisper
import os

# ✅ Force model to load on CPU
model = whisper.load_model("base", device="cpu")


def transcribe_file(audio_path: str) -> str:
    print("[STT] Transcribing...")
    if not os.path.exists(audio_path):
        print(f"[STT Error] Expected file missing: {audio_path}")
        return ""

    try:
        # ✅ Force CPU again and disable fp16 explicitly
        result = model.transcribe(audio_path, fp16=False)
        transcript = result.get("text", "")
        print(f"[STT] Transcript: {transcript}")
        return transcript
    except Exception as e:
        print(f"[STT Error] {e}")
        return ""
