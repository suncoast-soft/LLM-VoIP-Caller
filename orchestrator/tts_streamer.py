import io
import tempfile
import os
from TTS.api import TTS

# Load the TTS model once
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
print(f"[DEBUG] Available speakers: {tts.speakers}")


def synthesize_audio_stream(text: str) -> bytes:
    if not text.strip():
        return None

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        tts.tts_to_file(text=text, file_path=tmp_path, speaker="p225")
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.remove(tmp_path)
        return audio_bytes

    except Exception as e:
        print(f"[TTS Error] {e}")
        return None
