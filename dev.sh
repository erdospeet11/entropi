#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

#Create a virtual environment if it doesn't exist
if [[ ! -d .venv ]]; then
  python -m venv .venv
  .venv/bin/pip install -r backend/requirements.txt
fi

#Install the frontend dependencies if they don't exist
if [[ ! -d frontend/node_modules ]]; then
  npm install --prefix frontend
fi

#Run the backend in dev mode
.venv/bin/uvicorn app:app --reload --app-dir backend --host 127.0.0.1 --port 8000 &
api_pid=$!
#Run the frontend in dev mode
npm run dev --prefix frontend &
web_pid=$!

#Kill the processes when the script exits
trap 'kill $api_pid $web_pid 2>/dev/null' EXIT
#Wait for the processes to exit
wait