#!/bin/bash

# --- AGI handshake ---
while read line; do
  [ "$line" = "" ] && break
done

# --- Answer call and stabilize RTP ---
echo "ANSWER"
read
echo "WAIT FOR DIGIT 1000"
read
sleep 1

# --- Play intro
echo "STREAM FILE intro \"\""
read
echo "WAIT FOR DIGIT 500"
read

# --- Record user response
echo "RECORD FILE /tmp/user_input wav \"#\" 5000"
read

# --- Run orchestrator to generate streamed response
echo "VERBOSE \"[AGI] Launching AI orchestrator...\" 1"
cd /home/ubuntu/ai-call-center
/home/ubuntu/ai-call-center/venv/bin/python3 -m orchestrator.stream_orchestrator >> /tmp/orchestrator.log 2>&1

# --- Wait until TTS starts writing files
AUDIO_DIR="/var/lib/asterisk/sounds/stream_audio"
MAX_WAIT=10  # 5s max (10 × 0.5s)
WAITED=0

while ! ls $AUDIO_DIR/stream_*.wav 1> /dev/null 2>&1; do
  echo "[AGI] Waiting for first .wav segment..." >&2
  sleep 0.5
  WAITED=$((WAITED + 1))
  if [ $WAITED -ge $MAX_WAIT ]; then
    echo "[AGI] Timeout waiting for response audio" >&2
    echo "HANGUP"
    exit 0
  fi
done

# --- Play each segment as it's created
for seg in $AUDIO_DIR/stream_*.wav; do
  seg_name=$(basename "${seg%.*}")

  # Wait until the file is fully flushed (optional: small delay)
  sleep 0.2

  echo "[AGI] Playing $seg_name" >&2
  echo "STREAM FILE stream_audio/$seg_name \"\""
  read
  echo "WAIT FOR DIGIT 300"
  read

  # --- DO NOT DELETE HERE ---
  # rm -f "$seg"
done

echo "HANGUP"
