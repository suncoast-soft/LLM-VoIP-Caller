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
            {"role": "user", "content": prompt}
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
