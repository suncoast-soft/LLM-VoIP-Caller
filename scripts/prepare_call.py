import requests
import sys
import os
from TTS.api import TTS


# ✅ CONFIG
VLLM_URL = "http://localhost:8000/v1/chat/completions"
SOUND_FILE = "/var/lib/asterisk/sounds/intro.wav"
TEMP_FILE = "/tmp/intro.wav"
CALL_FILE = "/tmp/callfile.call"
TARGET_NUMBER = sys.argv[1] if len(sys.argv) > 1 else "+18599512822"
CALLER_ID = "+13254840339"  # your Twilio number


# ✅ 1. Define the intro agenda prompt
intro_agenda = "Please greet the recipient as a friendly AI assistant and explain that this is a brief test call to demonstrate our intelligent voice system."


# ✅ 2. Query the LLM
print("🧠 Prompting LLM...")
response = requests.post(VLLM_URL, json={
    "model": "deepseek-ai/deepseek-llm-7b-chat",
    "messages": [
        {"role": "system", "content": "You are a friendly voice assistant making a call."},
        {"role": "user", "content": intro_agenda}
    ],
    "temperature": 0.7,
    "max_tokens": 200,
    "stream": False
})
print(response)
intro_text = response.json()["choices"][0]["message"]["content"]
print("✅ LLM Response:", intro_text)

intro_text = "I am an AI caller center"


# ✅ 3. Convert to speech with Coqui TTS
print("🗣️ Generating speech...")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC",
          progress_bar=False, gpu=False)
tts.tts_to_file(text=intro_text, file_path=TEMP_FILE)


# ✅ 4. Convert to ulaw in temp, then sudo move to Asterisk
print("🎙️ Converting to 8000Hz mono 8-bit ulaw for Asterisk...")
converted = f"{TEMP_FILE}.ulaw"
conversion_result = os.system(
    f"sox {TEMP_FILE} -r 8000 -c 1 -e u-law -t raw {converted}"
)

if conversion_result != 0:
    print("❌ sox ulaw conversion failed")
    sys.exit(1)

SOUND_FILE = "/var/lib/asterisk/sounds/intro.ulaw"
os.system(f"sudo mv {converted} {SOUND_FILE}")
os.system(f"sudo chown asterisk:asterisk {SOUND_FILE}")
os.system(f"sudo chmod 644 {SOUND_FILE}")


# ✅ 5. Create call file
callfile_content = f"""Channel: PJSIP/{TARGET_NUMBER}@twilio
Context: from-trunk
Extension: s
Priority: 1
CallerID: {CALLER_ID}
"""

with open(CALL_FILE, "w") as f:
    f.write(callfile_content)


# ✅ 6. Move call file into Asterisk queue
print("📞 Triggering call...")
os.system(f"sudo mv {CALL_FILE} /var/spool/asterisk/outgoing/")

print("✅ Call launched.")
