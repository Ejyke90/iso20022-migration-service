# 🚀 Quick Start Guide

## Start the Server

```bash
python -m uvicorn app.main:app --reload
```

**The server will run at: http://localhost:8000**

## Test the API

### 1. Check Server Health
```bash
curl http://localhost:8000/
```

### 2. Convert MT103 to pacs.008

Using the sample from PROJECT_SPEC.md:

```bash
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": ":20:TRF123456789\n:32A:231005USD10000,\n:50K:/1234567890\nJOHN DOE\n123 MAIN ST\nNEW YORK, NY\n:59:/0987654321\nJANE SMITH\n456 HIGH ST\nLONDON, UK\n:71A:OUR"
  }'
```

### 3. View API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Run Tests

```bash
# Test converter logic only
python test_converter.py

# Test all API endpoints
./final_test.sh
```

## View Logs

```bash
cat data/conversion_logs.jsonl
```

## View Statistics

```bash
curl http://localhost:8000/stats
```

---

**That's it! Your ISO 20022 Migration Service is ready.** 🎉
