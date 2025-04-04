#!/usr/bin/env python3

import sys
import os
import requests
import subprocess

AUDIO_INPUT = "/home/ubuntu/ai_call_center/audio/inputs/user.wav"
AUDIO_OUTPUT = "/home/ubuntu/ai_call_center/audio/outputs/response.wav"
INTRO_AUDIO = "/home/ubuntu/ai_call_center/static/intro.wav"
ORCHESTRATOR_URL = "http://127.0.0.1:8000/process_audio"  # adjust if different


def agi_write(command):
    sys.stdout.write(command + '\n')
    sys.stdout.flush()


def agi_read():
    return sys.stdin.readline().strip()


def log(msg):
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()


def main():
    log("AGI Script Started")

    # 1. Answer the call
    agi_write("ANSWER")
    agi_read()

    # 2. Play static intro
    # Asterisk strips .wav extension
    agi_write(f"STREAM FILE {INTRO_AUDIO[:-4]} \"\"")
    agi_read()

    # 3. Record user's response
    # 30s max, silence detection
    agi_write(f"RECORD FILE {AUDIO_INPUT[:-4]} wav \"#\" 30000 0 s=5")
    agi_read()

    log("User audio recorded, sending to orchestrator...")

    # 4. Send to orchestrator
    try:
        with open(AUDIO_INPUT, 'rb') as f:
            files = {'audio': f}
            response = requests.post(ORCHESTRATOR_URL, files=files)
            if response.status_code == 200:
                with open(AUDIO_OUTPUT, 'wb') as out:
                    out.write(response.content)
                log("Received response audio from orchestrator.")
            else:
                log(f"Orchestrator error: {response.status_code}")
                return
    except Exception as e:
        log(f"Failed to call orchestrator: {e}")
        return

    # 5. Play response audio
    agi_write(f"STREAM FILE {AUDIO_OUTPUT[:-4]} \"\"")
    agi_read()

    # 6. Hang up
    agi_write("HANGUP")
    agi_read()


if __name__ == "__main__":
    main()
