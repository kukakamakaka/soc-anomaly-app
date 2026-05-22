#!/bin/bash
# Sentinel.AI — one-command startup
set -e
cd "$(dirname "$0")"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       SENTINEL.AI  —  STARTING       ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Kill any old instances
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "next dev"             2>/dev/null || true
sleep 1

# 1. Backend (FastAPI + SQLite — no external DB needed)
echo "  [1/2] Starting backend..."
/Library/Frameworks/Python.framework/Versions/3.12/bin/uvicorn \
  app.main:app --host 0.0.0.0 --port 8000 \
  > /tmp/sentinel_backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend
until curl -s http://localhost:8000/ > /dev/null 2>&1; do sleep 1; done
echo "        Backend ready  →  http://localhost:8000"

# 2. Frontend (Next.js with webpack)
echo "  [2/2] Starting frontend..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
nvm use 20 2>/dev/null || true

cd frontend
npm run dev > /tmp/sentinel_frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend
until grep -q "Ready" /tmp/sentinel_frontend.log 2>/dev/null; do sleep 2; done
echo "        Frontend ready →  http://localhost:3000"

echo ""
echo "  ✅  All systems online"
echo "  ✅  Backend  PID: $BACKEND_PID"
echo "  ✅  Frontend PID: $FRONTEND_PID"
echo ""
echo "  Open: http://localhost:3000"
echo ""
echo "  To stop: pkill -f 'uvicorn|next dev'"
echo ""

wait
