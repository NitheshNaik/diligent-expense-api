#!/bin/bash

# Determine venv activation path (works on POSIX and Git Bash/MSYS on Windows)
if [ -f ".venv/Scripts/activate" ]; then
    VENV_ACTIVATE=".venv/Scripts/activate"
elif [ -f "venv/Scripts/activate" ]; then
    VENV_ACTIVATE="venv/Scripts/activate"
elif [ -f ".venv/bin/activate" ]; then
    VENV_ACTIVATE=".venv/bin/activate"
elif [ -f "venv/bin/activate" ]; then
    VENV_ACTIVATE="venv/bin/activate"
else
    echo "Error: Virtual environment (.venv or venv) not found. Please build one first."
    exit 1
fi

echo "Activating virtual environment..."
source "$VENV_ACTIVATE"

# Start uvicorn in the background, redirecting output to uvicorn.log
echo "Starting uvicorn server in the background..."
nohup uvicorn src.main:app --reload > uvicorn.log 2>&1 &
SERVER_PID=$!

# Save PID to file
echo $SERVER_PID > .server.pid

echo "Server started successfully."
echo "PID: $SERVER_PID"
echo "API URL: http://127.0.0.1:8000"
echo "Docs URL: http://127.0.0.1:8000/docs"
