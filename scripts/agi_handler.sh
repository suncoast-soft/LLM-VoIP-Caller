#!/bin/bash

# AGI handshake: wait for empty line
while read line; do
  [ "$line" = "" ] && break
done

echo "ANSWER"
read
echo "WAIT FOR DIGIT 1000"
read
sleep 1

# Play static intro
echo "STREAM FILE intro \"\""
read

counter=1

while true; do
  USER_AUDIO="/home/ubuntu/ai-call-center/audio/inputs/user_${counter}.wav"
  AI_AUDIO_BASE="/home/ubuntu/ai-call-center/audio/outputs/response_${counter}"

  # 1. Record user voice input
  echo "RECORD FILE ${USER_AUDIO%.*} wav \"#\" 30000 0 s=7"
  read

  # 2. Call orchestrator and block until all segments are ready
  curl -s -X POST http://localhost:8010/process_audio \
    -F "audio=@$USER_AUDIO"

  # 3. Wait until all segments are written (watch files appear)
  timeout=10
  elapsed=0
  while [ ! -f "${AI_AUDIO_BASE}_segment_1.wav" ] && [ $elapsed -lt $timeout ]; do
    sleep 1
    elapsed=$((elapsed + 1))
  done

  # 4. Convert all generated segments to Asterisk-compatible format
  for f in ${AI_AUDIO_BASE}_segment_*.wav; do
    if [ -f "$f" ]; then
      base_name=$(basename "${f%.*}")
      sox "$f" -r 8000 -c 1 -e signed-integer -b 16 "/var/lib/asterisk/sounds/$base_name.wav"
    fi
  done

  # 5. Wait to ensure conversion is complete and files flushed
  sleep 1

  # 6. Stream all segments back to the user
  for seg in /var/lib/asterisk/sounds/response_${counter}_segment_*.wav; do
    seg_name=$(basename "${seg%.*}")
    echo "[AGI] Playing $seg_name" >&2
    echo "STREAM FILE $seg_name \"\""
    read
    echo "WAIT FOR DIGIT 500"
    read
  done

  counter=$((counter + 1))
done

# Final hangup (if you add break later)
echo "HANGUP"
read
