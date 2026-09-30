#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# Open the browser (wait a sec for server to start)
(sleep 2 && open "http://localhost:8000") &

# Run the server using the virtual environment python
echo "Starting Finder..."
./venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload
