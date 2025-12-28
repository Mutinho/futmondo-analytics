#!/bin/bash
# Start cron daemon
service cron start

# Run uvicorn in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Keep container running
wait

