# 🧪 Testing Guide - ISO 20022 Migration Service

## Quick Start

### 1. Start the Server

```bash
cd /Users/ejikeudeze/JourneyBegins/iso20022-migration-service
python -m uvicorn app.main:app --reload
```

The server will start at: **http://localhost:8000**

---

## Testing Methods

### Method 1: Using Web Browser (Interactive API Docs)

**Easiest method - No command line needed!**

1. Start the server (see above)
2. Open your browser to: **http://localhost:8000/docs**
3. Click on **POST /convert**
4. Click **"Try it out"**
5. Paste a sample MT103 message (see samples below)
6. Click **"Execute"**
7. See the XML output in the response!

---

### Method 2: Using curl (Command Line)

#### Test with Basic Sample:
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "mt103_message": ":20:TRF123456789
:32A:231005USD10000,
:50K:/1234567890
JOHN DOE
123 MAIN ST
NEW YORK, NY
:59:/0987654321
JANE SMITH
456 HIGH ST
LONDON, UK
:71A:OUR"
}
EOF
```

#### Test with File:
```bash
# Read MT103 from file
MT103_CONTENT=$(cat samples/sample_mt103_basic.txt)

curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d "{\"mt103_message\": \"$MT103_CONTENT\"}"
```

#### Save XML Output to File:
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d @- << 'EOF' | python3 -c "import sys, json; print(json.load(sys.stdin)['pacs008_xml'])" > output.xml
{
  "mt103_message": ":20:TRF123456789
:32A:231005USD10000,
:50K:/1234567890
JOHN DOE
:59:/0987654321
JANE SMITH
:71A:OUR"
}
EOF

cat output.xml
```

---

### Method 3: Using Python Script

Create a file `my_test.py`:

```python
import requests
import json

# Read MT103 from file
with open('samples/sample_mt103_basic.txt', 'r') as f:
    mt103_message = f.read()

# Send request
response = requests.post(
    'http://localhost:8000/convert',
    json={'mt103_message': mt103_message}
)

# Parse response
result = response.json()

if result['success']:
    print("✅ Conversion Successful!")
    print("\nGenerated XML:")
    print(result['pacs008_xml'])
    
    # Save to file
    with open('output_pacs008.xml', 'w') as f:
        f.write(result['pacs008_xml'])
    print("\n📄 XML saved to output_pacs008.xml")
else:
    print("❌ Conversion Failed!")
    print("Errors:", result['errors'])
```

Run it:
```bash
python my_test.py
```

---

### Method 4: Using httpx (Async Python)

```python
import httpx
import asyncio

async def test_conversion():
    with open('samples/sample_mt103_europe.txt', 'r') as f:
        mt103_message = f.read()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8000/convert',
            json={'mt103_message': mt103_message},
            timeout=10.0
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ Success!")
            print(result['pacs008_xml'])
        else:
            print("❌ Failed:", result['errors'])

asyncio.run(test_conversion())
```

---

## Sample MT103 Files

I've created 4 sample files in the `samples/` directory:

### 1. Basic US Transfer
**File:** `samples/sample_mt103_basic.txt`
- Amount: USD 10,000
- From: John Doe (USA)
- To: Jane Smith (UK)
- Charges: OUR (sender pays)

### 2. European Transfer
**File:** `samples/sample_mt103_europe.txt`
- Amount: EUR 50,000
- From: Mueller GmbH (Germany)
- To: Smith Trading Ltd (UK)
- Charges: SHA (shared)

### 3. UK to US Transfer
**File:** `samples/sample_mt103_uk_to_us.txt`
- Amount: GBP 25,000.50
- From: Acme Corporation (UK)
- To: Tech Innovations Inc (USA)
- Charges: BEN (beneficiary pays)

### 4. Asia Transfer
**File:** `samples/sample_mt103_asia.txt`
- Amount: JPY 1,000,000
- From: Tokyo Electronics (Japan)
- To: Singapore Imports (Singapore)
- Charges: OUR (sender pays)

---

## Quick Tests

### 1. Health Check
```bash
curl http://localhost:8000/
```

Expected:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-31T...",
  "version": "0.1.0"
}
```

### 2. Convert Sample File
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d "{\"mt103_message\": \"$(cat samples/sample_mt103_basic.txt)\"}" \
  | python3 -m json.tool
```

### 3. View Statistics
```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

### 4. View Logs
```bash
curl http://localhost:8000/logs?limit=5 | python3 -m json.tool
```

---

## Testing Error Handling

### Missing Mandatory Field
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": ":20:TEST123\n:50K:/123456\nJOHN DOE\n:59:/654321\nJANE SMITH"
  }'
```

Expected: Error about missing :32A: (amount) and :71A: (charges)

### Invalid Charge Code
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": ":20:TEST123\n:32A:231005USD1000,\n:50K:/123\nJOHN\n:59:/456\nJANE\n:71A:XXX"
  }'
```

Expected: Error about invalid charge bearer code

---

## Recommended Testing Flow

1. **Start the server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Open browser to http://localhost:8000/docs**

3. **Test each sample file using the interactive API**
   - Click POST /convert
   - Click "Try it out"
   - Copy/paste content from each sample file
   - Click "Execute"
   - Review the XML output

4. **Check statistics:**
   ```bash
   curl http://localhost:8000/stats | python3 -m json.tool
   ```

5. **Review logs:**
   ```bash
   cat data/conversion_logs.jsonl
   ```

---

## Output Files

After conversion, you can save the XML:

```bash
# Using Python
python3 -c "
import requests
with open('samples/sample_mt103_basic.txt') as f:
    mt103 = f.read()
response = requests.post('http://localhost:8000/convert', json={'mt103_message': mt103})
with open('output.xml', 'w') as f:
    f.write(response.json()['pacs008_xml'])
print('Saved to output.xml')
"
```

---

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Try: `python -m uvicorn app.main:app --port 8001`

### Import errors
- Make sure you're in the virtual environment
- Run: `source .venv/bin/activate` (or use the full path)

### Connection refused
- Ensure the server is running
- Check the server logs for errors

---

## Need Help?

- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Check server logs** in the terminal where uvicorn is running
- **Check conversion logs:** `cat data/conversion_logs.jsonl`

---

**Happy Testing! 🚀**
