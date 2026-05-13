# ISO 20022 Migration Service

FastAPI service for converting SWIFT MT messages into ISO 20022 XML.

## What this service does

This service converts:

- **MT103 → pacs.008.001.08** (`POST /convert`)
- **MT101 → pain.001.001.09** (`POST /convert/mt101`)
- **MT102 → pacs.008.001.08** (`POST /convert/mt102`)
- **MT202 → pacs.009.001.08** (`POST /convert/mt202`)

It also exposes:

- `GET /health` for health status
- `GET /logs?limit=10` for recent conversion logs
- `GET /stats` for conversion statistics

The root route `GET /` serves `static/index.html` when present, otherwise a small JSON message.

---

## Tech stack

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic
- xmltodict

Core app entrypoint: `app/main.py`

---

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Request payloads

### MT103 (`POST /convert`)

```json
{
  "mt103_message": ":20:TRF123456789\n:32A:231005USD10000,\n:50K:/1234567890\nJOHN DOE\n:59:/0987654321\nJANE SMITH\n:71A:OUR"
}
```

### MT101 (`POST /convert/mt101`)

```json
{
  "mt101_message": ":20:PAY20231201001\n:32B:EUR75000,00\n:50K:/GB82WEST12345698765432\nCORPORATE PAYMENTS LTD\n:59:/DE89370400440532013000\nSUPPLIER ONE GMBH"
}
```

### MT102 (`POST /convert/mt102`)

> Note: this endpoint currently expects the field name `mt103_message` in the request body.

```json
{
  "mt103_message": ":20:MULTI20231205001\n:32A:231205USD95000,00\n:50K:/GB82WEST12345698765432\nCORPORATE PAYMENTS LTD\n:21:001\n:32B:USD45000,00\n:59:/US64SVBKUS6S3300958879\nTECH SOLUTIONS INC\n:71A:SHA"
}
```

### MT202 (`POST /convert/mt202`)

```json
{
  "mt202_message": ":20:COV20231210001\n:32A:231210USD250000,00\n:52A:CHASUS33XXX\n:58A:BNPAFRPPXXX"
}
```

---

## Example curl

```bash
curl -X POST http://127.0.0.1:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "mt103_message": ":20:TRF123456789\n:32A:231005USD10000,\n:50K:/1234567890\nJOHN DOE\n:59:/0987654321\nJANE SMITH\n:71A:OUR"
  }'
```

---

## Testing

These scripts are used in CI and can be run locally:

```bash
python test_converter.py
python test_mt102_direct.py
python test_all_endpoints.py
```

`test_all_endpoints.py` expects the API server to already be running on `127.0.0.1:8000`.

---

## Docker

Build:

```bash
docker build -t iso20022-migration-service .
```

Run:

```bash
docker run --rm -p 8000:8000 iso20022-migration-service
```

---

## Data and logging

- Conversion attempts are stored in `data/conversion_logs.jsonl`
- Each entry includes timestamp, input hash, success/failure, errors, and processing time
