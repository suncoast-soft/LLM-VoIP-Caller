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

# Play the static intro message
echo "STREAM FILE intro \"\""
read

counter=1

while true; do
  USER_AUDIO="/home/ubuntu/ai-call-center/audio/inputs/user_${counter}.wav"
  AI_AUDIO_BASE="/home/ubuntu/ai-call-center/audio/outputs/response_${counter}"
  AST_AUDIO_BASE="/var/lib/asterisk/sounds/response_${counter}"

  # 1. Record user voice input
  echo "RECORD FILE ${USER_AUDIO%.*} wav \"#\" 30000 0 s=5"
  read

  # 2. Send to orchestrator for STT → LLM → streaming TTS
  curl -s -X POST http://localhost:8010/process_audio \
    -F "audio=@$USER_AUDIO" \
    --output "${AI_AUDIO_BASE}_segment_0.wav"

  # 3. Convert all generated segments to Asterisk format
  for f in ${AI_AUDIO_BASE}_segment_*.wav; do
    base_name=$(basename "${f%.*}")
    sox "$f" -r 8000 -c 1 -e signed-integer -b 16 "${AST_AUDIO_BASE}_${base_name##*_}.wav"
  done

  # 4. Stream back all response segments
  for seg in ${AST_AUDIO_BASE}_segment_*.wav; do
    seg_name=$(basename "${seg%.*}")
    echo "STREAM FILE $seg_name \"\""
    read
  done

  # Optional: break on silence/keyword (not yet implemented)

  counter=$((counter + 1))
done

# Cleanup (not reachable without break)
echo "HANGUP"
read
