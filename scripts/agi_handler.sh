#!/bin/bash

CALL_ID="$1"
LOG_FILE="/var/log/asterisk/agi/agi_log_${CALL_ID}.log"
echo "📎 CALL_ID passed to AGI: $CALL_ID" >> "$LOG_FILE"

# --- AGI handshake ---
while read line; do
  [ "$line" = "" ] && break
done

echo "ANSWER"
read
echo "WAIT FOR DIGIT 1000"
read
sleep 1

# --- Play pre-generated intro if it exists ---
INTRO_PATH="/var/lib/asterisk/sounds/intro_${CALL_ID}.wav"
if [ -f "$INTRO_PATH" ]; then
  echo "[AGI] Playing intro_${CALL_ID}.wav" >> "$LOG_FILE"
  echo "STREAM FILE intro_${CALL_ID} \"\""
  read
  echo "WAIT FOR DIGIT 500"
  read
fi

# --- Conversation Loop ---
while true; do
  RECORD_PATH="/tmp/user_input_${CALL_ID}.wav"
  RESPONSE_PATH="/var/lib/asterisk/sounds/response_${CALL_ID}.wav"

  echo "[AGI] Recording caller..." >> "$LOG_FILE"
  echo "RECORD FILE ${RECORD_PATH%.*} wav \"#\" 15000 1 s=2"
  read

  if [ ! -f "$RECORD_PATH" ]; then
    echo "[AGI] No user input recorded. Ending call." >> "$LOG_FILE"
    break
  fi

  echo "[AGI] Sending to orchestrator..." >> "$LOG_FILE"
  curl -s -X POST http://localhost:8100/call \
    -H "Content-Type: application/json" \
    -d "{\"call_id\": \"$CALL_ID\"}" >> "$LOG_FILE" 2>&1

  if [ -f "$RESPONSE_PATH" ]; then
    echo "[AGI] Playing response_${CALL_ID}.wav" >> "$LOG_FILE"
    echo "STREAM FILE response_${CALL_ID} \"\""
    read
    echo "WAIT FOR DIGIT 500"
    read
  else
    echo "[AGI] No response audio found. Ending call." >> "$LOG_FILE"
    break
  fi

  # Optional: clean up audio files to avoid overwrite conflict
  rm -f "$RECORD_PATH"
  rm -f "$RESPONSE_PATH"
done

echo "HANGUP"
