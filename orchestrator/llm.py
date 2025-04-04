import requests

VLLM_URL = "http://localhost:8000/v1/chat/completions"


def generate_response(prompt: str) -> str:
    payload = {
        "model": "deepseek-llm-7b-chat",
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


if __name__ == "__main__":
    print(generate_response("Hello, who are you?"))
