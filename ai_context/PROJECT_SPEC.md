# Project Specification: ISO 20022 Migration Service - Multi-Message Support

## 1. Project Goal
Build a comprehensive Python-based REST API that converts legacy SWIFT MT messages to ISO 20022 MX XML messages, supporting the most critical message types used by banks during the global SWIFT ISO 20022 migration.

## 2. Supported Message Conversions

### Priority 1 - Payment Messages (IMPLEMENTED & ENHANCED)
1. **MT103 → pacs.008.001.08** (Customer Credit Transfer)
   - Single customer credit transfer
   - Most commonly used payment message
   
2. **MT101 → pain.001.001.09** (Customer Payment Initiation)
   - Request for transfer by customer
   - Multiple transactions supported

3. **MT102 → pacs.008.001.08** (Multiple Customer Credit Transfer)
   - Batch payments
   - Multiple beneficiaries in one message

4. **MT202 → pacs.009.001.08** (Financial Institution Credit Transfer)
   - Bank-to-bank transfers
   - Cover payments

### Priority 2 - Account Reporting & Notifications
5. **MT940 → camt.053.001.08** (Bank to Customer Statement)
   - Account statement
   - Most critical for cash management

6. **MT950 → camt.053.001.08** (Statement Message)
   - Detailed statement message

7. **MT900 → camt.054.001.08** (Confirmation of Debit)
   - Debit notification

8. **MT910 → camt.054.001.08** (Confirmation of Credit)
   - Credit notification

### Priority 3 - Additional Messages
9. **MT199 → pain.002.001.10** (Payment Status Report)
   - Free format message for payment instructions

10. **MT192 → pain.002.001.10** (Request for Cancellation)
    - Payment cancellation request

## 3. Core Architecture
- **Language:** Python 3.11+
- **Web Framework:** FastAPI (for the REST API)
- **Data Validation:** Pydantic (strictly typed models) + XML libraries
- **Agent Framework:** LangChain (for intelligent field mapping)
- **Deployment:** Railway.app or Docker-based platforms
- **Web UI:** Modern HTML/CSS/JavaScript interface

## 4. API Endpoints

### Main Conversion Endpoints
- `POST /convert/mt103` - Convert MT103 to pacs.008
- `POST /convert/mt101` - Convert MT101 to pain.001
- `POST /convert/mt102` - Convert MT102 to pacs.008
- `POST /convert/mt202` - Convert MT202 to pacs.009
- `POST /convert/mt940` - Convert MT940 to camt.053
- `POST /convert/mt950` - Convert MT950 to camt.053
- `POST /convert/mt900` - Convert MT900 to camt.054
- `POST /convert/mt910` - Convert MT910 to camt.054
- `POST /convert` - Auto-detect MT message type and convert

### Utility Endpoints
- `GET /` - Web UI
- `GET /health` - Health check
- `GET /stats` - Conversion statistics
- `GET /logs` - Recent conversion logs
- `GET /supported-messages` - List all supported conversions

## 5. Key Features

### Parsing & Validation
1. **Smart MT Detection:** Auto-detect message type from MT header
2. **Field Extraction:** Regex-based parsing of all MT field tags
3. **Mandatory Field Validation:** Ensure all required fields are present
4. **Business Rule Validation:** 
   - Amounts must be positive
   - Dates must be valid
   - Currency codes must be ISO 4217 compliant
   - BIC codes must be valid (when present)

### Mapping Intelligence
1. **Field Mapping:** Comprehensive MT → MX field mappings per ISO 20022 standards
2. **Data Transformation:**
   - Date format conversion (YYMMDD → YYYY-MM-DD)
   - Charge bearer mapping (OUR/BEN/SHA → DEBT/CRED/SHAR)
   - Currency/amount formatting
3. **Address Parsing:** Extract structured address from unstructured MT fields
4. **Party Information:** Map ordering/beneficiary customer data

### XML Generation
1. **Valid XML Output:** Well-formed XML with proper namespaces
2. **Pretty Formatting:** Indented, readable XML
3. **Schema Compliance:** Adherence to ISO 20022 XSD schemas
4. **Namespace Management:** Correct xmlns declarations per message type

### Logging & Monitoring
1. **Comprehensive Logging:** Log to `conversion_logs.jsonl` with:
   - Timestamp
   - Message type (MT103, MT101, etc.)
   - Input hash (SHA256, anonymized)
   - Success/Failure status
   - Validation errors
   - Processing time
2. **Statistics Tracking:** Count conversions by message type
3. **Error Analytics:** Track common failure patterns

## 6. Technical Constraints
- **No Heavy Databases:** Use in-memory processing + file-based logging
- **Modular Architecture:**
  - `app/main.py` - FastAPI application
  - `app/models/` - Pydantic models by message type
  - `app/services/converters/` - Converter per MT message type
  - `app/services/parsers/` - MT parsers
  - `app/services/mappers/` - MT→MX mappers
  - `app/services/validators/` - Validation logic
- **Dockerfile:** Production-ready container
- **Dependencies:** Poetry for package management

## 7. Message Type Priorities

### Phase 1 (Current Implementation)
- ✅ MT103 → pacs.008 (COMPLETE)

### Phase 2 (Immediate)
- MT101 → pain.001
- MT102 → pacs.008
- MT202 → pacs.009

### Phase 3 (Account Reporting)
- MT940 → camt.053
- MT950 → camt.053
- MT900 → camt.054
- MT910 → camt.054

### Phase 4 (Enhanced)
- MT199 → pain.002
- MT192 → pain.002
- Additional message types based on demand

## 8. Sample Test Data

### MT103 Sample (IMPLEMENTED)
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

### MT101 Sample (TO BE IMPLEMENTED)
```
:20:PMT20231205001
:28D:1/1
:50A:BOFAUS3N
:50K:/1234567890
ABC CORPORATION
:30:231206
:21:TXN001
:32B:USD10000,00
:50K:/1234567890
ABC CORPORATION
:59:/0987654321
XYZ LIMITED
:71A:SHA
```

### MT202 Sample (TO BE IMPLEMENTED)
```
:20:COV123456789
:21:INSTREF001
:32A:231205EUR50000,
:52A:DEUTDEFF
:58A:CHASUS33
:72:/REC/Payment for invoice 12345
```

### MT940 Sample (TO BE IMPLEMENTED)
```
:20:STMT20231205
:25:DE89370400440532013000EUR
:28C:1/1
:60F:C231204EUR10000,00
:61:231205D5000,00NMSCNONREF//TRF001
:86:Payment to supplier
:62F:C231205EUR5000,00
```

## 9. Success Criteria
1. **Coverage:** Support top 8 MT→MX conversions used by banks
2. **Accuracy:** 99%+ field mapping accuracy
3. **Validation:** All mandatory fields validated per ISO 20022
4. **Performance:** < 100ms conversion time per message
5. **Reliability:** Comprehensive error handling and logging
6. **Usability:** Modern web UI for testing and production use

## 10. References
- ISO 20022 Message Definitions: https://www.iso20022.org/iso-20022-message-definitions
- SWIFT MT Standards: https://www.swift.com/standards/mt-standards
- ISO 20022 Migration Guide: https://www.swift.com/standards/iso-20022
- pacs.008 Documentation: ISO 20022 pacs (Payments Clearing and Settlement)
- pain.001 Documentation: ISO 20022 pain (Payments Initiation)
- camt.053 Documentation: ISO 20022 camt (Cash Management)