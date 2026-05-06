#!/bin/bash
echo "Starting Gmail API Server..."
python api_server.py &
API_PID=$!

echo "Starting Gmail Frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Services started:"
echo "  API:      http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both services."

trap "kill $API_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
