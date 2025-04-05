# ai_call_center/orchestrator/tts.py

from TTS.api import TTS
import time

tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC",
                progress_bar=False, gpu=False)


def synthesize_audio(text: str, output_path: str):
    tts_model.tts_to_file(text=text, file_path=output_path)


def synthesize_audio_streaming(generator, base_output_path: str) -> list:
    """
    Accepts a generator of tokens and produces audio segments as WAV files
    Returns list of paths to audio segment files
    """
    buffer = ""
    segment_files = []
    counter = 0

    for token in generator:
        buffer += token
        if token.endswith((".", "!", "?")) and len(buffer.strip().split()) >= 3:
            out_path = f"{base_output_path}_segment_{counter}.wav"
            tts_model.tts_to_file(text=buffer.strip(), file_path=out_path)
            segment_files.append(out_path)
            counter += 1
            buffer = ""

    # Final leftover buffer
    if buffer.strip():
        out_path = f"{base_output_path}_segment_{counter}.wav"
        tts_model.tts_to_file(text=buffer.strip(), file_path=out_path)
        segment_files.append(out_path)

    return segment_files
