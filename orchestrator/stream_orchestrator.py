import os
import uuid
from orchestrator.whisper_handler import transcribe_file
from orchestrator.llm_streamer import stream_llm_tokens
from orchestrator.tts_streamer import synthesize_audio_stream
from orchestrator.asterisk_streamer import stream_to_asterisk

AUDIO_FILE = "/tmp/user_input.wav"
AUDIO_STREAM_DIR = "/var/lib/asterisk/sounds/stream_audio"


def group_tokens(token_stream, max_words=5):
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


def main():
    if not os.path.exists(AUDIO_FILE):
        print(f"[ERROR] Audio file not found: {AUDIO_FILE}")
        return

    print("[STT] Transcribing...")
    transcript = transcribe_file(AUDIO_FILE)
    print(f"[STT] Transcript: {transcript}")

    print("[LLM] Streaming response...")
    token_stream = stream_llm_tokens(transcript)
    for phrase in group_tokens(token_stream, max_words=5):
        print(f"[LLM] {phrase}", flush=True)
        audio_bytes = synthesize_audio_stream(phrase)
        if audio_bytes:
            filename = f"stream_{uuid.uuid4().hex[:8]}.wav"
            filepath = os.path.join(AUDIO_STREAM_DIR, filename)
            stream_to_asterisk(audio_bytes, filepath)
            print(f"[TTS] Audio chunk written: {filename}")
        else:
            print("[TTS] No audio bytes returned")


if __name__ == "__main__":
    main()
