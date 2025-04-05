#!/bin/bash

cd ~/ai-call-center/orchestrator/
uvicorn main:app --host 0.0.0.0 --port 8010
