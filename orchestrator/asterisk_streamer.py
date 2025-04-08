import os
import pwd
import uuid
import subprocess

# Asterisk-compatible audio directory
AUDIO_STREAM_DIR = "/var/lib/asterisk/sounds/stream_audio"

# Ensure output directory exists
os.makedirs(AUDIO_STREAM_DIR, exist_ok=True)

# Get asterisk UID/GID
asterisk_uid = pwd.getpwnam("asterisk").pw_uid
asterisk_gid = pwd.getpwnam("asterisk").pw_gid


def convert_to_asterisk_wav(in_path, out_path):
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", in_path,
        "-ar", "8000",
        "-ac", "1",
        "-sample_fmt", "s16",
        out_path
    ], check=True)


def stream_to_asterisk(audio_bytes, final_path):
    temp_raw_path = final_path + ".raw"
    temp_fixed_path = final_path + ".tmp.wav"

    # Write raw TTS audio
    with open(temp_raw_path, "wb") as f:
        f.write(audio_bytes)

    # Convert to 8000Hz mono 16-bit PCM WAV
    convert_to_asterisk_wav(temp_raw_path, temp_fixed_path)
    os.remove(temp_raw_path)

    # Final move
    if os.path.exists(final_path):
        os.remove(final_path)
    os.rename(temp_fixed_path, final_path)

    # Correct permissions
    os.chown(final_path, asterisk_uid, asterisk_gid)
    os.chmod(final_path, 0o644)
