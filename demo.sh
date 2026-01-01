#!/bin/bash

echo "================================================================================"
echo "🚀 ISO 20022 Migration Service - Quick Demo"
echo "================================================================================"
echo ""
echo "This script will:"
echo "  1. Start the server"
echo "  2. Test all sample MT103 files"
echo "  3. Show you the XML outputs"
echo ""
echo "Press Ctrl+C when done to stop the server"
echo ""
read -p "Press Enter to start..."

# Start server in background
echo ""
echo "Starting server..."
/Users/ejikeudeze/JourneyBegins/iso20022-migration-service/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /dev/null 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
sleep 5

echo ""
echo "================================================================================"
echo "✅ Server is running at http://localhost:8000"
echo "================================================================================"
echo ""
echo "You can now:"
echo "  • Open http://localhost:8000/docs in your browser for interactive testing"
echo "  • Run the commands below in another terminal"
echo ""
echo "================================================================================"
echo ""

# Test each sample
for sample in samples/*.txt; do
    echo "================================================================================
"                                                                                   filename=$(basename "$sample")
    echo "📄 Testing: $filename"
    echo "================================================================================
"                                                                                   echo ""
    echo "Input MT103:"
    cat "$sample"
    echo ""
    echo "--------------------------------------------------------------------------------
"                                                                                   echo "Converting..."
    
    # Convert and save output
    output_file="output_${filename%.txt}.xml"
    
    curl -s -X POST http://127.0.0.1:8000/convert \
      -H "Content-Type: application/json" \
      -d "{\"mt103_message\": \"$(cat $sample)\"}" \
      | python3 -c "
import sys, json
try:
    result = json.load(sys.stdin)
    if result['success']:
        print('✅ SUCCESS!')
        print()
        with open('$output_file', 'w') as f:
            f.write(result['pacs008_xml'])
        print('📄 XML saved to: $output_file')
        print()
        print('XML Preview (first 25 lines):')
        print('-' * 80)
        lines = result['pacs008_xml'].split('\n')
        for line in lines[:25]:
            print(line)
        if len(lines) > 25:
            print(f'... ({len(lines) - 25} more lines)')
    else:
        print('❌ FAILED!')
        print('Errors:', result.get('errors'))
except Exception as e:
    print(f'Error: {e}')
"
    
    echo ""
    echo ""
    read -p "Press Enter to test next sample (or Ctrl+C to exit)..."
    echo ""
done

echo "================================================================================"
echo "📊 Statistics"
echo "================================================================================"
curl -s http://127.0.0.1:8000/stats | python3 -m json.tool
echo ""

echo "================================================================================"
echo "📝 Generated Files"
echo "================================================================================"
ls -lh output_*.xml 2>/dev/null || echo "No files generated"
echo ""

echo "================================================================================"
echo "Server is still running on PID $SERVER_PID"
echo "Press Ctrl+C to stop it"
echo "================================================================================"

# Wait for user interrupt
wait $SERVER_PID
