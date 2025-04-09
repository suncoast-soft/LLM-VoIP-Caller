import requests
import json

VLLM_STREAM_ENDPOINT = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "deepseek-ai/deepseek-llm-7b-chat"


def stream_llm_tokens(prompt: str):
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly, helpful person talking on a phone call. "
                    "Your goal is to sound natural, casual, and human at all times.\n\n"
                    "Guidelines:\n"
                    "- Keep responses short and conversational.\n"
                    "- Default to 1–2 sentences unless the user asks for more detail (then go up to 5).\n"
                    "- Speak in a relaxed, friendly tone — like you're chatting with someone you know.\n"
                    "- Use simple, natural phrases.\n"
                    "- If you're unsure of something, just say so casually (e.g., 'I'm not totally sure, you might want to check online.')\n\n"
                    "Avoid:\n"
                    "- Never say you are an AI, language model, or assistant.\n"
                    "- Never say things like 'as a language model' or 'I don’t have real-time data.'\n"
                    "- Never use placeholder phrases like [insert ...] or [e.g., ...].\n"
                    "- Do not list websites or links.\n"
                    "- Do not give overly formal or robotic-sounding answers."
                )
            },
            {
                "role": "user",
                "content": "Answer like a real person would: " + prompt
            }
        ]
    }

    response = requests.post(VLLM_STREAM_ENDPOINT,
                             headers=headers, json=payload, stream=True)

    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.strip() == "data: [DONE]":
                break
            if decoded.startswith("data: "):
                try:
                    data = json.loads(decoded[6:])
                    token = data["choices"][0]["delta"].get("content")
                    if token:
                        yield token
                except Exception as e:
                    print(f"[LLM Stream Error] {e}")
