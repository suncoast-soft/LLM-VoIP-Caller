import os
import uuid
from orchestrator.whisper_handler import transcribe_file
from orchestrator.llm_streamer import stream_llm_tokens
from orchestrator.tts_streamer import synthesize_audio_stream
from orchestrator.asterisk_streamer import stream_to_asterisk

AUDIO_FILE = "/tmp/user_input.wav"
AUDIO_STREAM_DIR = "/var/lib/asterisk/stream_audio"


def main():
    if not os.path.exists(AUDIO_FILE):
        print(f"[ERROR] Audio file not found: {AUDIO_FILE}")
        return

    print("[STT] Transcribing...")
    transcript = transcribe_file(AUDIO_FILE)
    print(f"[STT] Transcript: {transcript}")

    print("[LLM] Streaming response...")
    for token in stream_llm_tokens(transcript):
        print(f"[LLM] {token}", flush=True)
        audio_bytes = synthesize_audio_stream(token)
        if audio_bytes:
            filename = f"stream_{uuid.uuid4().hex[:8]}.wav"
            filepath = os.path.join(AUDIO_STREAM_DIR, filename)
            stream_to_asterisk(audio_bytes, filepath)
            print(f"[TTS] Audio chunk written: {filename}")
        else:
            print("[TTS] No audio bytes returned")


if __name__ == "__main__":
    main()
