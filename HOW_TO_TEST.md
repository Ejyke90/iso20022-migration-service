# 🧪 How to Test the ISO 20022 Migration Service

## ⚡ Quick Start (3 Steps)

### 1. Start the Server
```bash
cd /Users/ejikeudeze/JourneyBegins/iso20022-migration-service
python -m uvicorn app.main:app --reload
```

### 2. Open Your Browser
Go to: **http://localhost:8000/docs**

### 3. Test It!
- Click **POST /convert**
- Click **"Try it out"**
- Copy one of the sample MT103 messages below
- Click **"Execute"**
- See your XML output! ✨

---

## 📄 Sample MT103 Messages (Copy & Paste These)

### Sample 1: Basic US Transfer (USD 10,000)
```
:20:TRF123456789
:32A:231005USD10000,
:50K:/1234567890
JOHN DOE
123 MAIN ST
NEW YORK, NY
:59:/0987654321
JANE SMITH
456 HIGH ST
LONDON, UK
:71A:OUR
```

### Sample 2: European Transfer (EUR 50,000)
```
:20:WIRE20231215001
:32A:231215EUR50000,00
:50K:/DE89370400440532013000
MUELLER GMBH
HAUPTSTRASSE 123
10115 BERLIN
GERMANY
:59:/GB29NWBK60161331926819
SMITH TRADING LTD
456 OXFORD STREET
LONDON W1D 1BS
UNITED KINGDOM
:71A:SHA
```

### Sample 3: UK to US Transfer (GBP 25,000)
```
:20:PAY2023120812345
:32A:231208GBP25000,50
:50K:/GB82WEST12345698765432
ACME CORPORATION
SUITE 500 BUSINESS PARK
MANCHESTER M1 1AE
:59:/US64SVBKUS6S3300958879
TECH INNOVATIONS INC
789 SILICON VALLEY BLVD
SAN FRANCISCO CA 94105
:71A:BEN
```

### Sample 4: Asia Transfer (JPY 1,000,000)
```
:20:INT2023Q4567890
:32A:240101JPY1000000,
:50K:/JP1234567890123456
TOKYO ELECTRONICS CO LTD
1-1-1 SHIBUYA
TOKYO 150-0002
JAPAN
:59:/SG9876543210987654
SINGAPORE IMPORTS PTE LTD
10 RAFFLES PLACE
SINGAPORE 048622
:71A:OUR
```

---

## 🎯 Alternative Testing Methods

### Method 1: Using Sample Files (Already Created!)

I've created 4 sample files for you in `samples/`:
- `sample_mt103_basic.txt`
- `sample_mt103_europe.txt`
- `sample_mt103_uk_to_us.txt`
- `sample_mt103_asia.txt`

**Test with a sample file:**
```bash
# Convert a sample file
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d "{\"mt103_message\": \"$(cat samples/sample_mt103_basic.txt)\"}" \
  | python3 -m json.tool > result.json

# Extract just the XML
cat result.json | python3 -c "import sys, json; print(json.load(sys.stdin)['pacs008_xml'])" > output.xml

# View the XML
cat output.xml
```

### Method 2: Interactive Python Script
```bash
python interactive_test.py
```
This will:
- Test all sample files automatically
- Save XML outputs
- Show you statistics
- Display results

### Method 3: Run the Demo Script
```bash
chmod +x demo.sh
./demo.sh
```

### Method 4: Using curl Directly
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": ":20:TRF123456789\n:32A:231005USD10000,\n:50K:/1234567890\nJOHN DOE\n123 MAIN ST\n:59:/0987654321\nJANE SMITH\n:71A:OUR"
  }' | python3 -m json.tool
```

---

## 🔍 Understanding MT103 Fields

| Field | Description | Example |
|-------|-------------|---------|
| `:20:` | Transaction Reference | `TRF123456789` |
| `:32A:` | Date, Currency, Amount | `231005USD10000,` (Oct 5, 2023, USD 10,000) |
| `:50K:` | Ordering Customer | Account + Name + Address |
| `:59:` | Beneficiary | Account + Name + Address |
| `:71A:` | Charge Bearer | `OUR`/`BEN`/`SHA` |

**Charge Bearer Codes:**
- `OUR` = Sender pays all charges (→ DEBT in ISO 20022)
- `BEN` = Beneficiary pays all charges (→ CRED in ISO 20022)
- `SHA` = Charges shared (→ SHAR in ISO 20022)

---

## 📊 Check Your Results

### View Statistics
```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

### View Recent Conversions
```bash
curl http://localhost:8000/logs?limit=10 | python3 -m json.tool
```

### Check Log File
```bash
cat data/conversion_logs.jsonl
```

---

## ✅ What to Expect

When you convert successfully, you'll get:

```json
{
  "success": true,
  "pacs008_xml": "<?xml version=\"1.0\"...>",
  "errors": null,
  "warnings": null,
  "input_hash": "95522fce...",
  "timestamp": "2025-12-31T23:30:00"
}
```

The `pacs008_xml` field contains your ISO 20022 XML!

---

## 🐛 Testing Error Handling

### Try a message missing the amount field:
```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": ":20:TEST123\n:50K:/123\nJOHN DOE\n:59:/456\nJANE SMITH"
  }'
```

Expected: Error about missing `:32A:` and `:71A:`

---

## 📚 More Information

- **Full Testing Guide:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Setup Guide:** See [SETUP_COMPLETE.md](SETUP_COMPLETE.md)

---

## 🎉 You're All Set!

**Easiest way:** Just go to http://localhost:8000/docs and use the interactive interface!
