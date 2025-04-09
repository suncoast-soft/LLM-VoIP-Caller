import os
import numpy as np
import torch
import torchaudio
import tempfile
from scipy.io.wavfile import write as write_wav
from TTS.api import TTS

# Load TTS model once
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
print(f"[DEBUG] Available speakers: {tts.speakers}")


def synthesize_full_response_audio(text: str, output_path: str) -> bool:
    if not text.strip():
        print("[TTS] Empty text, skipping synthesis.")
        return False

    try:
        # Generate audio from TTS
        audio = tts.tts(text, speaker="p313")
        sample_rate = tts.synthesizer.output_sample_rate

        # Add silence padding
        silence = np.zeros(int(0.1 * sample_rate), dtype=np.float32)
        padded_audio = np.concatenate([audio, silence])

        # Resample to 8000 Hz for Asterisk
        waveform = torch.tensor(padded_audio).unsqueeze(0)
        resampled = torchaudio.functional.resample(
            waveform, orig_freq=sample_rate, new_freq=8000)
        audio_int16 = np.int16(resampled.squeeze().numpy() * 32767)

        # Write to /tmp first
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir="/tmp") as tmp:
            tmp_path = tmp.name
        write_wav(tmp_path, 8000, audio_int16)

        # Move into final destination (Asterisk sounds dir)
        os.system(f"sudo mv {tmp_path} {output_path}")
        os.chmod(output_path, 0o644)

        return True

    except Exception as e:
        print(f"[TTS Error] {e}")
        return False
