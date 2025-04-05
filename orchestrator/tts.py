# ai_call_center/orchestrator/tts.py

from TTS.api import TTS
import time

tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC",
                progress_bar=False, gpu=False)


def synthesize_audio(text: str, output_path: str):
    tts_model.tts_to_file(text=text, file_path=output_path)


def synthesize_audio_streaming(generator, base_output_path: str) -> list:
    buffer = ""
    segment_files = []
    counter = 0

    for token in generator:
        buffer += token
        if token.endswith((".", "!", "?")) or len(buffer.strip().split()) >= 8:
            out_path = f"{base_output_path}_segment_{counter}.wav"
            if len(buffer.strip()) < 5:
                print(f"[TTS] Skipping short buffer: '{buffer.strip()}'")
                buffer = ""
                continue
            try:
                print(f"[TTS] Synthesizing: {buffer.strip()} -> {out_path}")
                tts_model.tts_to_file(text=buffer.strip(), file_path=out_path)
                segment_files.append(out_path)
            except Exception as e:
                print(
                    f"[TTS ERROR] Failed to synthesize '{buffer.strip()}': {e}")
            buffer = ""
            counter += 1

    if buffer.strip():
        out_path = f"{base_output_path}_segment_{counter}.wav"
        try:
            tts_model.tts_to_file(text=buffer.strip(), file_path=out_path)
            segment_files.append(out_path)
        except Exception as e:
            print(f"[TTS ERROR] Failed final segment: {e}")

    print(f"[TTS] Total segments: {len(segment_files)}")
    return segment_files
