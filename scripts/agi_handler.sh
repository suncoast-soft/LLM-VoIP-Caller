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

# --- Launch orchestrator call via API
echo "VERBOSE \"[AGI] Launching AI orchestrator...\" 1"
curl -X POST http://localhost:8100/call \
  -H "Content-Type: application/json" \
  -d "{\"audio_path\": \"/tmp/user_input.wav\"}" &

# --- Wait for the first segment to appear
AUDIO_DIR="/var/lib/asterisk/sounds/stream_audio"
MAX_WAIT=20
WAITED=0

while ! ls $AUDIO_DIR/stream_*.wav 1> /dev/null 2>&1; do
  echo "[AGI] Waiting for first .wav segment..." >&2
  sleep 0.25
  WAITED=$((WAITED + 1))
  if [ $WAITED -ge $MAX_WAIT ]; then
    echo "[AGI] Timeout waiting for response audio" >&2
    echo "HANGUP"
    exit 0
  fi
done

# --- Stream audio chunks as they are created ---
INDEX=0
IDLE_TICKS=0
while true; do
  filename=$(printf "stream_%08d.wav" $INDEX)
  filepath="$AUDIO_DIR/$filename"

  if [ -f "$filepath" ]; then
    seg_name="${filename%.*}"
    echo "[AGI] Playing $seg_name" >&2
    echo "STREAM FILE stream_audio/$seg_name \"\""
    read
    echo "WAIT FOR DIGIT 300"
    read
    rm -f "$filepath"
    INDEX=$((INDEX + 1))
    IDLE_TICKS=0
  else
    sleep 0.25
    IDLE_TICKS=$((IDLE_TICKS + 1))
    if [ $IDLE_TICKS -ge 20 ]; then
      break
    fi
  fi
done

echo "HANGUP"
