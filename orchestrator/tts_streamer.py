import os
import numpy as np
import tempfile
from TTS.api import TTS
from scipy.io.wavfile import write as write_wav
import torchaudio
import torch

# Load TTS model
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
print(f"[DEBUG] Available speakers: {tts.speakers}")


def synthesize_audio_stream(text: str) -> bytes:
    if not text.strip():
        return None

    try:
        # Generate audio at native sample rate (usually 22050 Hz)
        audio = tts.tts(text, speaker="p225")
        sample_rate = tts.synthesizer.output_sample_rate

        # Add 100ms silence at native sample rate
        silence = np.zeros(int(0.1 * sample_rate), dtype=np.float32)
        padded_audio = np.concatenate([audio, silence])

        # Convert to torch tensor and resample to 8000 Hz
        waveform = torchaudio.functional.resample(
            torch.tensor(padded_audio).unsqueeze(0), orig_freq=sample_rate, new_freq=8000
        )
        audio_resampled = waveform.squeeze().numpy()

        # Convert to 16-bit PCM
        audio_int16 = np.int16(audio_resampled * 32767)

        # Write to temp wav file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        write_wav(tmp_path, 8000, audio_int16)

        # Return wav bytes
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.remove(tmp_path)

        return audio_bytes

    except Exception as e:
        print(f"[TTS Error] {e}")
        return None
