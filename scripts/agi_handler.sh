#!/bin/bash

# 1. Tell Asterisk to answer the call
echo "ANSWER"
read

# 2. Play static intro
echo "STREAM FILE intro \"\""
read

# # 3. Record the user's input (max 30s)
# echo "RECORD FILE /home/ubuntu/ai-call-center/audio/inputs/user wav \"#\" 30000 0 s=5"
# read

# # 4. Call the Python orchestrator
# curl -s -X POST http://localhost:8010/process_audio \
#   -F "audio=@/home/ubuntu/ai-call-center/audio/inputs/user.wav" \
#   --output /home/ubuntu/ai-call-center/audio/outputs/response.wav

# # 5. Play the AI response
# echo "STREAM FILE /home/ubuntu/ai-call-center/audio/outputs/response \"\""
# read

# echo "WAIT FOR DIGIT 1000"
# read

# echo "SAY DIGITS 1 \"\""
# read

# 6. Hang up
echo "HANGUP"
read
