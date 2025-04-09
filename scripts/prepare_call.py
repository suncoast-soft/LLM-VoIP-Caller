import requests
import sys
import uuid
import os

CALL_FILE = "/tmp/callfile.call"
ORCHESTRATOR_URL = "http://localhost:8100/call"
TARGET_NUMBER = sys.argv[1] if len(sys.argv) > 1 else None
CALLER_ID = "+13254840339"

if not TARGET_NUMBER:
    print("❌ Phone number is required")
    sys.exit(1)


# ✅ 1. Generate call ID
call_id = uuid.uuid4().hex[:8]


# ✅ 2. Define the intro agenda prompt
intro_agenda = (
    "Please greet the recipient as a friendly AI assistant and explain that this is "
    "a brief test call to demonstrate our intelligent voice system. Limit it to less than 2 sentences."
)


# ✅ 3. Trigger orchestrator to pre-generate intro
print("📡 Sending orchestrator API request...")
response = requests.post(ORCHESTRATOR_URL, json={
    "call_id": call_id,
    "intro_text": intro_agenda
})

if response.status_code != 200:
    print("❌ Orchestrator failed:", response.text)
    sys.exit(1)

print("✅ Orchestrator response:", response.json())


# ✅ 4. Create call file for Asterisk (pass call_id into channel variable)
callfile_content = f"""Channel: PJSIP/{TARGET_NUMBER}@twilio
Context: from-trunk
Extension: s
Priority: 1
CallerID: {CALLER_ID}
Set: CALL_ID={call_id}
"""

with open(CALL_FILE, "w") as f:
    f.write(callfile_content)


# ✅ 5. Queue the call
print("📞 Launching call with call ID:", call_id)
os.system(f"sudo mv {CALL_FILE} /var/spool/asterisk/outgoing/")
print("✅ Call queued for delivery.")
