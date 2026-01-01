#!/bin/bash

# Start server in background
echo "Starting FastAPI server..."
/Users/ejikeudeze/JourneyBegins/iso20022-migration-service/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
echo "Waiting for server to start..."
sleep 5

echo ""
echo "========================================="
echo "Testing Health Check Endpoint"
echo "========================================="
curl -s http://127.0.0.1:8000/ | python3 -m json.tool

echo ""
echo ""
echo "========================================="
echo "Testing /convert Endpoint"
echo "========================================="
curl -s -X POST http://127.0.0.1:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": "\n:20:TRF123456789\n:32A:231005USD10000,\n:50K:/1234567890\nJOHN DOE\n123 MAIN ST\nNEW YORK, NY\n:59:/0987654321\nJANE SMITH\n456 HIGH ST\nLONDON, UK\n:71A:OUR\n"
  }' | python3 -m json.tool | head -30

echo ""
echo ""
echo "========================================="
echo "Testing /stats Endpoint"
echo "========================================="
curl -s http://127.0.0.1:8000/stats | python3 -m json.tool

echo ""
echo ""
echo "========================================="
echo "Checking Logs"
echo "========================================="
cat data/conversion_logs.jsonl

echo ""
echo ""
echo "Shutting down server..."
kill $SERVER_PID
echo "Done!"
