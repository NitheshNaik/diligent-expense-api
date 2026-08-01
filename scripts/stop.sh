#!/bin/bash

PID_FILE=".server.pid"

if [ -f "$PID_FILE" ]; then
    SERVER_PID=$(cat "$PID_FILE")
    if [ -n "$SERVER_PID" ]; then
        echo "Stopping server process with PID $SERVER_PID..."
        
        # Kill the process
        if kill -0 "$SERVER_PID" 2>/dev/null; then
            kill "$SERVER_PID" 2>/dev/null || kill -9 "$SERVER_PID" 2>/dev/null
            echo "Process $SERVER_PID terminated."
        else
            echo "Process $SERVER_PID is not running."
        fi
    else
        echo "No PID found in $PID_FILE."
    fi
    rm -f "$PID_FILE"
else
    echo "No $PID_FILE file found. Is the server running?"
fi

# Deactivate virtual environment if function exists in parent shell (when sourced)
# To deactivate the parent shell's virtual environment, the user MUST run:
# source scripts/stop.sh
if declare -f deactivate >/dev/null; then
    deactivate
    echo "Virtual environment deactivated."
else
    echo "Note: If you run this script directly (e.g. ./scripts/stop.sh), the virtual environment"
    echo "in your calling shell remains active. To deactivate it, run: source scripts/stop.sh"
fi
