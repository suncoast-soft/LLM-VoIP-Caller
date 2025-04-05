import requests
import json

VLLM_URL = "http://localhost:8000/v1/chat/completions"


def generate_response(prompt: str) -> str:
    """Non-streaming fallback"""
    payload = {
        "model": "deepseek-ai/deepseek-llm-7b-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful AI phone agent."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 256,
        "stream": False
    }
    response = requests.post(VLLM_URL, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def stream_response(prompt: str):
    payload = {
        "model": "deepseek-ai/deepseek-llm-7b-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful AI phone agent."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 256,
        "stream": True
    }

    with requests.post(VLLM_URL, json=payload, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            try:
                if line.startswith(b"data: "):
                    json_str = line[len(b"data: "):].decode("utf-8").strip()
                    if json_str == "[DONE]":
                        break
                    data = json.loads(json_str)
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
            except Exception as e:
                print("[stream_response] Skipped malformed line:", line)
                continue
