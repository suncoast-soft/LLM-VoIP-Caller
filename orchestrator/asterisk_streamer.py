import os
import tempfile
import subprocess

AUDIO_STREAM_DIR = "/var/lib/asterisk/stream_audio"


def stream_to_asterisk(audio_bytes: bytes, filepath: str):
    print(f"[DEBUG] Starting stream_to_asterisk → {filepath}")

    if not os.path.exists(AUDIO_STREAM_DIR):
        print("[DEBUG] Creating stream_audio dir...")
        os.makedirs(AUDIO_STREAM_DIR, exist_ok=True)

    # Write bytes to temp raw file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        raw_path = tmp.name

    print(f"[DEBUG] Written temp WAV: {raw_path}")

    # Convert to ulaw WAV for Asterisk
    converted_path = filepath
    try:
        result = subprocess.run([
            "sox", raw_path,
            "-r", "8000", "-c", "1", "-e", "u-law",
            "-t", "wav", converted_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[SOX ERROR] {result.stderr}")
        else:
            print(f"[TTS] Audio chunk written: {converted_path}")

    except Exception as e:
        print(f"[TTS ERROR] Exception: {e}")

    finally:
        os.remove(raw_path)
        print(f"[DEBUG] Deleted temp file: {raw_path}")
