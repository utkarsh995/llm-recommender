#!/bin/bash
# Install vllm if not already installed (optional check, better to just run command)
# pip install vllm

# Run VLLM server
# Serving Qwen/Qwen3-0.6B on port 8000
python3 -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3-0.6B \
    --trust-remote-code \
    --port 8000
