#!/bin/bash

# Test error handling with invalid MT103 (missing :32A: field)

echo "Starting FastAPI server..."
/Users/ejikeudeze/JourneyBegins/iso20022-migration-service/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
sleep 5

echo ""
echo "========================================="
echo "Test 1: Valid MT103 Message"
echo "========================================="
curl -s -X POST http://127.0.0.1:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": "\n:20:TRF123456789\n:32A:231005USD10000,\n:50K:/1234567890\nJOHN DOE\n123 MAIN ST\nNEW YORK, NY\n:59:/0987654321\nJANE SMITH\n456 HIGH ST\nLONDON, UK\n:71A:OUR\n"
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Success:', data['success'])"

echo ""
echo "========================================="
echo "Test 2: Missing :32A: Field (should fail)"
echo "========================================="
curl -s -X POST http://127.0.0.1:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": "\n:20:TRF123456789\n:50K:/1234567890\nJOHN DOE\n:59:/0987654321\nJANE SMITH\n:71A:OUR\n"
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Success:', data['success']); print('Errors:', data.get('errors'))"

echo ""
echo "========================================="
echo "Test 3: Invalid Charge Code"
echo "========================================="
curl -s -X POST http://127.0.0.1:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": "\n:20:TRF123456789\n:32A:231005USD10000,\n:50K:/1234567890\nJOHN DOE\n:59:/0987654321\nJANE SMITH\n:71A:XXX\n"
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Success:', data['success']); print('Errors:', data.get('errors'))"

echo ""
echo "========================================="
echo "Final Stats"
echo "========================================="
curl -s http://127.0.0.1:8000/stats | python3 -m json.tool

echo ""
echo "Shutting down server..."
kill $SERVER_PID
echo "Done!"
