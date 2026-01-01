"""
FastAPI application for ISO 20022 Migration Service.

This module provides REST API endpoints for converting MT103 SWIFT messages
to ISO 20022 pacs.008.001.08 XML format.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pathlib import Path

from app.services.converter import (
    convert_mt103_to_iso,
    compute_input_hash,
    MT103ParseError,
    MT103MissingFieldError,
    MT103ValidationError,
    ISO20022ConversionError,
)
from app.services.mt101_converter import (
    convert_mt101_to_pain001,
    MT101ParseError,
    MT101MissingFieldError,
    MT101ValidationError,
    Pain001ConversionError,
)
from app.services.mt102_converter import (
    convert_mt102_to_pacs008,
    MT102ParseError,
    MT102MissingFieldError,
    MT102ValidationError,
    Pacs008ConversionError,
)
from app.services.mt202_converter import (
    convert_mt202_to_pacs009,
    MT202ParseError,
    MT202MissingFieldError,
    MT202ValidationError,
    Pacs009ConversionError,
)
from app.models import ConversionResponse, ConversionLog, MT103Message
from app.models.pain001 import MT101Message, ConversionResponse as Pain001Response
from app.models.pacs009 import MT202Message, ConversionResponse as Pacs009Response


# ============================================================================
# Configuration
# ============================================================================

LOG_FILE_PATH = Path("data/conversion_logs.jsonl")
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Request/Response Models
# ============================================================================

class ConvertRequest(BaseModel):
    """Request model for MT103 conversion endpoint"""
    mt103_message: str = Field(
        ...,
        description="Raw MT103 SWIFT message text",
        min_length=10,
        example="""
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
"""
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="0.1.0")


# ============================================================================
# Logging Service
# ============================================================================

class LoggingService:
    """Service for logging conversion attempts to JSONL file"""
    
    @staticmethod
    def log_conversion(log_entry: ConversionLog) -> None:
        """
        Log conversion attempt to conversion_logs.jsonl file.
        
        Args:
            log_entry: ConversionLog Pydantic model
        """
        try:
            log_data = log_entry.model_dump()
            # Convert datetime to ISO format string
            log_data['timestamp'] = log_data['timestamp'].isoformat()
            
            with open(LOG_FILE_PATH, 'a') as f:
                f.write(json.dumps(log_data) + '\n')
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"Warning: Failed to write to log file: {e}")


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Ensures log file exists on startup.
    """
    # Startup
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()
        print(f"Created log file: {LOG_FILE_PATH}")
    
    print(f"ISO 20022 Migration Service started")
    print(f"Logging to: {LOG_FILE_PATH.absolute()}")
    
    yield
    
    # Shutdown
    print("ISO 20022 Migration Service shutting down")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="ISO 20022 Migration Service",
    description="REST API for converting SWIFT MT103 messages to ISO 20022 pacs.008.001.08 XML",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ============================================================================
# Middleware
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests.
    """
    start_time = time.time()
    
    response = await call_next(request)
    
    processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    print(f"{request.method} {request.url.path} - {response.status_code} - {processing_time:.2f}ms")
    
    return response


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """
    Serve the web UI.
    """
    static_file = Path(__file__).parent.parent / "static" / "index.html"
    if static_file.exists():
        return FileResponse(static_file)
    else:
        return {"message": "ISO 20022 Migration Service", "docs": "/docs"}


@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthCheckResponse with service status
    """
    return HealthCheckResponse(status="healthy")


@app.post("/convert", response_model=ConversionResponse, status_code=status.HTTP_200_OK)
async def convert_mt103(request: ConvertRequest) -> ConversionResponse:
    """
    Convert MT103 SWIFT message to ISO 20022 pacs.008.001.08 XML.
    
    This endpoint:
    1. Accepts a raw MT103 message
    2. Parses and validates the message
    3. Converts it to ISO 20022 pacs.008 XML format
    4. Logs the conversion attempt
    
    Args:
        request: ConvertRequest containing MT103 message
        
    Returns:
        ConversionResponse with XML output or error details
        
    Raises:
        HTTPException: If conversion fails with appropriate status code
    """
    start_time = time.time()
    mt103_text = request.mt103_message
    
    # Compute input hash for logging (anonymized)
    input_hash = compute_input_hash(mt103_text)
    
    try:
        # Perform conversion
        pacs008_xml = convert_mt103_to_iso(mt103_text)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Log successful conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=True,
            errors=None,
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return success response
        return ConversionResponse(
            success=True,
            pacs008_xml=pacs008_xml,
            errors=None,
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )
        
    except MT103MissingFieldError as e:
        # Handle missing mandatory fields
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return ConversionResponse(
            success=False,
            pacs008_xml=None,
            errors=[error_msg],
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )
        
    except MT103ValidationError as e:
        # Handle validation errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return ConversionResponse(
            success=False,
            pacs008_xml=None,
            errors=[error_msg],
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )
        
    except MT103ParseError as e:
        # Handle parsing errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return ConversionResponse(
            success=False,
            pacs008_xml=None,
            errors=[error_msg],
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )
        
    except ISO20022ConversionError as e:
        # Handle ISO 20022 conversion errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return ConversionResponse(
            success=False,
            pacs008_xml=None,
            errors=[error_msg],
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        # Handle unexpected errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = f"Unexpected error: {str(e)}"
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return ConversionResponse(
            success=False,
            pacs008_xml=None,
            errors=[error_msg],
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )


@app.post("/convert/mt101", response_model=Pain001Response, status_code=status.HTTP_200_OK)
async def convert_mt101_endpoint(request: MT101Message) -> Pain001Response:
    """
    Convert MT101 SWIFT message to ISO 20022 pain.001.001.09 XML.
    
    This endpoint:
    1. Accepts a raw MT101 message (Customer Transfer Initiation)
    2. Parses and validates the message
    3. Converts it to ISO 20022 pain.001 XML format
    4. Logs the conversion attempt
    
    Args:
        request: MT101Message containing MT101 message
        
    Returns:
        ConversionResponse with XML output or error details
    """
    start_time = time.time()
    mt101_text = request.mt101_message
    
    # Compute input hash for logging (anonymized)
    from app.services.mt101_converter import compute_input_hash as compute_mt101_hash
    input_hash = compute_mt101_hash(mt101_text)
    
    try:
        # Perform conversion
        pain001_xml, _ = convert_mt101_to_pain001(mt101_text)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Log successful conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=True,
            errors=None,
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return success response
        return Pain001Response(
            success=True,
            message="MT101 successfully converted to pain.001",
            pain001_xml=pain001_xml,
            errors=None,
            input_hash=input_hash
        )
        
    except MT101MissingFieldError as e:
        # Handle missing mandatory fields
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return Pain001Response(
            success=False,
            message="MT101 conversion failed",
            pain001_xml=None,
            errors=[error_msg],
            input_hash=input_hash
        )
        
    except (MT101ValidationError, MT101ParseError, Pain001ConversionError) as e:
        # Handle validation/parsing/conversion errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return Pain001Response(
            success=False,
            message="MT101 conversion failed",
            pain001_xml=None,
            errors=[error_msg],
            input_hash=input_hash
        )
        
    except Exception as e:
        # Handle unexpected errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = f"Unexpected error: {str(e)}"
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return Pain001Response(
            success=False,
            message="MT101 conversion failed",
            pain001_xml=None,
            errors=[error_msg],
            input_hash=input_hash
        )


@app.post("/convert/mt102", response_model=ConversionResponse, status_code=status.HTTP_200_OK)
async def convert_mt102_endpoint(request: ConvertRequest) -> ConversionResponse:
    """
    Convert MT102 SWIFT message to ISO 20022 pacs.008.001.08 XML.
    
    This endpoint:
    1. Accepts a raw MT102 message (Multiple Customer Credit Transfer)
    2. Parses and validates the message
    3. Converts it to ISO 20022 pacs.008 XML format (same output as MT103)
    4. Logs the conversion attempt
    
    Args:
        request: ConvertRequest containing MT102 message
        
    Returns:
        ConversionResponse with XML output or error details
    """
    start_time = time.time()
    mt102_text = request.mt103_message  # Reuses field name from MT103
    
    # Compute input hash for logging (anonymized)
    from app.services.mt102_converter import compute_input_hash as compute_mt102_hash
    input_hash = compute_mt102_hash(mt102_text)
    
    try:
        # Perform conversion
        pacs008_xml, _ = convert_mt102_to_pacs008(mt102_text)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Log successful conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=True,
            errors=None,
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return success response
        return ConversionResponse(
            success=True,
            pacs008_xml=pacs008_xml,
            errors=None,
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )
        
    except MT102MissingFieldError as e:
        # Handle missing mandatory fields
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return ConversionResponse(
            success=False,
            pacs008_xml=None,
            errors=[error_msg],
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )
        
    except (MT102ValidationError, MT102ParseError, Pacs008ConversionError) as e:
        # Handle validation/parsing/conversion errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return ConversionResponse(
            success=False,
            pacs008_xml=None,
            errors=[error_msg],
            warnings=None,
            input_hash=input_hash,
            timestamp=datetime.utcnow()
        )


@app.post("/convert/mt202", response_model=Pacs009Response, status_code=status.HTTP_200_OK)
async def convert_mt202_endpoint(request: MT202Message) -> Pacs009Response:
    """
    Convert MT202 SWIFT message to ISO 20022 pacs.009.001.08 XML.
    
    This endpoint:
    1. Accepts a raw MT202 message (Financial Institution Transfer)
    2. Parses and validates the message
    3. Converts it to ISO 20022 pacs.009 XML format
    4. Logs the conversion attempt
    
    Args:
        request: MT202Message containing MT202 message
        
    Returns:
        Pacs009Response with XML output or error details
    """
    start_time = time.time()
    mt202_text = request.mt202_message
    
    # Compute input hash for logging (anonymized)
    from app.services.mt202_converter import compute_input_hash as compute_mt202_hash
    input_hash = compute_mt202_hash(mt202_text)
    
    try:
        # Perform conversion
        pacs009_xml, _ = convert_mt202_to_pacs009(mt202_text)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Log successful conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=True,
            errors=None,
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return success response
        return Pacs009Response(
            success=True,
            message="MT202 successfully converted to pacs.009",
            pacs009_xml=pacs009_xml,
            errors=None,
            input_hash=input_hash
        )
        
    except MT202MissingFieldError as e:
        # Handle missing mandatory fields
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return Pacs009Response(
            success=False,
            message="MT202 conversion failed",
            pacs009_xml=None,
            errors=[error_msg],
            input_hash=input_hash
        )
        
    except (MT202ValidationError, MT202ParseError, Pacs009ConversionError) as e:
        # Handle validation/parsing/conversion errors
        processing_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log failed conversion
        log_entry = ConversionLog(
            input_hash=input_hash,
            success=False,
            errors=[error_msg],
            processing_time_ms=processing_time_ms
        )
        LoggingService.log_conversion(log_entry)
        
        # Return error response
        return Pacs009Response(
            success=False,
            message="MT202 conversion failed",
            pacs009_xml=None,
            errors=[error_msg],
            input_hash=input_hash
        )


@app.get("/logs")
async def get_logs(limit: int = 10) -> Dict:
    """
    Retrieve recent conversion logs.
    
    Args:
        limit: Maximum number of log entries to return (default: 10)
        
    Returns:
        Dictionary containing log entries
    """
    try:
        if not LOG_FILE_PATH.exists():
            return {"logs": [], "count": 0}
        
        logs = []
        with open(LOG_FILE_PATH, 'r') as f:
            lines = f.readlines()
            # Get last N lines
            for line in lines[-limit:]:
                if line.strip():
                    logs.append(json.loads(line))
        
        return {
            "logs": logs,
            "count": len(logs),
            "total_entries": len(lines)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read logs: {str(e)}"
        )


@app.get("/stats")
async def get_stats() -> Dict:
    """
    Get conversion statistics.
    
    Returns:
        Dictionary containing conversion statistics
    """
    try:
        if not LOG_FILE_PATH.exists():
            return {
                "total_conversions": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        
        total = 0
        successful = 0
        failed = 0
        
        with open(LOG_FILE_PATH, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    total += 1
                    if entry.get('success'):
                        successful += 1
                    else:
                        failed += 1
        
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        return {
            "total_conversions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(success_rate, 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate stats: {str(e)}"
        )


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
