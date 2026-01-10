# AI Context - ISO20022 Migration Service

## Project Overview
This is a comprehensive Python-based REST API that converts legacy SWIFT MT messages to ISO 20022 MX XML messages, supporting critical message types used by banks during the global SWIFT ISO 20022 migration.

## Core Architecture

### Technology Stack
- **Language:** Python 3.11+
- **Web Framework:** FastAPI (main REST API)
- **Alternative Framework:** Flask (legacy API in `/api/` directory)
- **Data Validation:** Pydantic (strictly typed models) + XML libraries
- **Agent Framework:** LangChain (for intelligent field mapping)
- **Package Management:** Poetry (pyproject.toml)
- **Deployment:** Railway.app or Docker-based platforms

### Project Structure
```
iso20022-migration-service/
├── app/                          # FastAPI application (primary)
│   ├── main.py                   # FastAPI app entry point
│   ├── models/                   # Pydantic models by message type
│   │   ├── pacs008.py           # pacs.008 model (MT103 target)
│   │   ├── pacs009.py           # pacs.009 model (MT202 target)
│   │   └── pain001.py           # pain.001 model (MT101 target)
│   └── services/                 # Business logic
│       ├── converter.py         # Main conversion service
│       ├── mt102_converter.py   # MT102 conversion
│       ├── mt202_converter.py   # MT202 conversion
│       └── mt101_converter.py   # MT101 conversion
├── api/                          # Flask API (legacy)
│   ├── server.py                # Flask server
│   └── converter.py             # Flask converter
├── samples/                      # Test data and examples
├── data/                         # Runtime data (logs, etc.)
├── static/                       # Web UI assets
├── docs/                         # Documentation
└── tests/                        # Test files
```

## Key Entry Points

### 1. FastAPI Application (Primary)
- **File:** `app/main.py`
- **Purpose:** Main REST API with modern async support
- **Port:** 8000 (default)
- **Start:** `uvicorn app.main:app --reload`

### 2. Flask Application (Legacy)
- **File:** `api/server.py`
- **Purpose:** Backup/sync API with CORS support
- **Port:** 5000 (default)
- **Start:** `python api/server.py`

### 3. Streamlit Web App
- **File:** `app.py`
- **Purpose:** User-friendly web interface for testing
- **Port:** 8501 (default)
- **Start:** `streamlit run app.py`

### 4. CLI Interface
- **File:** `main.py`
- **Purpose:** Command-line conversion tool
- **Command:** `python main.py convert-doc <input> <output>`

## Supported Message Conversions

### Currently Implemented
1. **MT103 → pacs.008.001.08** (Customer Credit Transfer) ✅
2. **MT102 → pacs.008.001.08** (Multiple Customer Credit Transfer) ✅
3. **MT202 → pacs.009.001.08** (Financial Institution Credit Transfer) ✅

### Planned Implementation
4. **MT101 → pain.001.001.09** (Customer Payment Initiation)
5. **MT940 → camt.053.001.08** (Bank to Customer Statement)
6. **MT950 → camt.053.001.08** (Statement Message)
7. **MT900 → camt.054.001.08** (Confirmation of Debit)
8. **MT910 → camt.054.001.08** (Confirmation of Credit)

## API Endpoints (FastAPI)

### Main Conversion Endpoints
- `POST /convert/mt103` - Convert MT103 to pacs.008
- `POST /convert/mt102` - Convert MT102 to pacs.008
- `POST /convert/mt202` - Convert MT202 to pacs.009
- `POST /convert` - Auto-detect MT message type and convert

### Utility Endpoints
- `GET /` - Web UI redirect
- `GET /health` - Health check
- `GET /stats` - Conversion statistics
- `GET /logs` - Recent conversion logs
- `GET /supported-messages` - List all supported conversions

## Build System

### Dependencies
- **Poetry:** Primary package manager (pyproject.toml)
- **Requirements.txt:** Fallback for pip installs
- **Key Dependencies:**
  - fastapi, uvicorn (API server)
  - pydantic (data validation)
  - xmltodict (XML processing)
  - langchain (AI framework)
  - streamlit (web UI)

### Running the Application
1. **Install dependencies:** `poetry install` or `pip install -r requirements.txt`
2. **Start FastAPI:** `uvicorn app.main:app --reload`
3. **Start Flask:** `python api/server.py`
4. **Start Web UI:** `streamlit run app.py`

### Testing
- **Unit tests:** Located in `/tests/` directory
- **Integration tests:** `test_*.py` files in root
- **Demo script:** `demo.sh` for comprehensive testing

## Core Logic Components

### 1. Message Parsing
- **Location:** `app/services/` converters
- **Purpose:** Parse SWIFT MT field tags using regex
- **Features:** Auto-detection, field extraction, validation

### 2. Field Mapping
- **Location:** Individual converter files
- **Purpose:** Map MT fields to ISO 20022 XML elements
- **Intelligence:** LangChain-powered smart mapping

### 3. XML Generation
- **Location:** Model classes in `app/models/`
- **Purpose:** Generate valid ISO 20022 XML
- **Features:** Schema compliance, pretty formatting

### 4. Logging & Monitoring
- **File:** `data/conversion_logs.jsonl`
- **Content:** Timestamps, message types, success/failure, processing time
- **Analytics:** Conversion statistics by type

## Configuration Files
- **pyproject.toml:** Poetry configuration and dependencies
- **Dockerfile:** Production container configuration
- **.github/workflows/:** CI/CD pipelines
- **AGENTS.md:** Agent behavior rules and landing procedures

## Important Notes
- The README.md describing "Word to PDF" conversion is outdated
- This project is specifically for SWIFT MT → ISO 20022 MX conversion
- Multiple API frameworks are supported (FastAPI primary, Flask fallback)
- Comprehensive logging and error handling implemented
- Modern web UI available via Streamlit
- Docker-ready for production deployment
