#!/bin/bash
# Start cron daemon
service cron start

# Get PORT from environment or default to 8000
PORT=${PORT:-8000}

# Run uvicorn in background
uvicorn app.main:app --host 0.0.0.0 --port $PORT &

# Keep container running
wait

