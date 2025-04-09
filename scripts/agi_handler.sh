#!/bin/bash

CALL_ID="$1"
LOG_FILE="/var/log/asterisk/agi/agi_log_${CALL_ID}.log"
echo "📎 CALL_ID passed to AGI: $CALL_ID" >> "$LOG_FILE"

# --- AGI handshake ---
while read line; do
  [ "$line" = "" ] && break
done

echo "[AGI] Playing intro_${CALL_ID}.wav" >> "$LOG_FILE"

# --- Answer and stabilize RTP ---
echo "ANSWER"
read
echo "WAIT FOR DIGIT 1000"
read
sleep 1

# --- Play intro if available ---
INTRO_PATH="/var/lib/asterisk/sounds/intro_${CALL_ID}.wav"
if [ -f "$INTRO_PATH" ]; then
  echo "STREAM FILE intro_${CALL_ID} \"\""
  read
  echo "WAIT FOR DIGIT 500"
  read
else
  echo "[AGI] No intro file found for CALL_ID ${CALL_ID}" >> "$LOG_FILE"
fi

# --- Record caller response ---
RECORD_PATH="/tmp/user_input_${CALL_ID}.wav"
echo "RECORD FILE ${RECORD_PATH%.*} wav \"#\" 5000"
read
echo "[AGI] Recorded caller response to ${RECORD_PATH}" >> "$LOG_FILE"

# --- Send to orchestrator for response generation ---
echo "[AGI] Sending call_id to orchestrator..." >> "$LOG_FILE"
curl -X POST http://localhost:8100/call \
  -H "Content-Type: application/json" \
  -d "{\"call_id\": \"$CALL_ID\"}" >> "$LOG_FILE" 2>&1

# --- Play generated response ---
RESPONSE_PATH="/var/lib/asterisk/sounds/response_${CALL_ID}.wav"
if [ -f "$RESPONSE_PATH" ]; then
  echo "STREAM FILE response_${CALL_ID} \"\""
  read
else
  echo "[AGI] No response audio found at $RESPONSE_PATH" >> "$LOG_FILE"
fi

# --- Optional cleanup ---
rm -f "$RECORD_PATH"
rm -f "$INTRO_PATH"
rm -f "$RESPONSE_PATH"

echo "HANGUP"
