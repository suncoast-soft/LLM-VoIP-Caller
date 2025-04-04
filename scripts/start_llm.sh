#!/bin/bash

python3 -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/deepseek-llm-7b-chat \
  --dtype float16 \
  --max-model-len 1024 \
  --host 0.0.0.0 \
  --port 8000
