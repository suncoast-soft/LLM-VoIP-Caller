# ai_call_center/orchestrator/tts.py

from TTS.api import TTS

tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC",
                progress_bar=False, gpu=True)


def synthesize_audio(text: str, output_path: str):
    tts_model.tts_to_file(text=text, file_path=output_path)
