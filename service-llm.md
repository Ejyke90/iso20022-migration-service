OpenSpec: RAG Service - LLM Gateway MVP (Local Development)
Version: 1.0 MVP - LLM Gateway Only (Local)
Owner: Principal AI Engineer
Status: Ready for Local MVP Implementation
Target Platform: Local Development (Docker Compose)
Scope: LLM Gateway Integration ONLY
Implementation Mode: AUDIT-FIRST, then add LLM Gateway in parallel

MVP Scope: LLM Gateway Integration (Local Development Focus)
What's IN SCOPE for MVP:

✅ LLM Gateway (Llama-3.1-8B) for query enrichment
✅ TGI service running locally via Docker Compose
✅ Parallel implementation (feature flag enabled)
✅ Few-shot prompt engineering
✅ Confidence scoring and fallback mechanism
✅ Basic integration tests and monitoring
✅ Local development setup

What's OUT OF SCOPE (deferred):

❌ OpenShift/Kubernetes deployment (Phase 2)
❌ Database schema changes (use existing schema)
❌ E5 embedding model migration (keep current embeddings)
❌ Progressive filter relaxation (keep current search logic)
❌ New API endpoints (use existing endpoints)
❌ Email ingestion changes (keep current pipeline)
❌ Production-grade monitoring (Prometheus/Grafana)


AI Agent Implementation Protocol (MVP-Specific)
CRITICAL: Check for Existing TGI Service FIRST
# AUDIT TASK 0: Check for Existing TGI Service

## Step 1: Discovery - Search for TGI Service
Run these commands to check if TGI is already deployed:
```bash
# Check for TGI in docker
docker ps | grep -i "text-generation-inference\|tgi"

# Check for TGI in docker-compose files
find . -name "docker-compose*.yml" -o -name "docker-compose*.yaml" | xargs grep -l "text-generation-inference\|tgi" 2>/dev/null

# Check for running TGI process
ps aux | grep -i "text-generation-inference\|tgi"

# Check for TGI configuration in code
grep -r "text-generation-inference\|TGI\|llama.*8b" --include="*.py" --include="*.yaml" --include="*.env" 2>/dev/null

# Check for LLM service URLs in config
grep -r "8080\|tgi\|llm.*gateway" --include="*.env" --include="config.py" --include="settings.py" 2>/dev/null

# Check for existing HuggingFace integrations
grep -r "huggingface\|transformers.*pipeline\|AutoModel" --include="*.py" 2>/dev/null
```

## Step 2: Analyze Findings

**Case A: TGI Service Found**
Found: docker container "tgi-server" running on port 8080
Action:

Document existing TGI configuration
Verify model is Llama-3.1-8B (or compatible)
Test connectivity: curl http://localhost:8080/health
Recommendation: REUSE existing TGI service
Skip TGI deployment step


**Case B: Other LLM Service Found** (e.g., vLLM, OpenAI, Anthropic)
Found: OpenAI client in services/llm_client.py
Action:

Document existing LLM integration
Determine if it can be adapted for enrichment
Options:
A) Replace with TGI + Llama (full control, no API costs)
B) Keep existing LLM, adapt prompt (faster MVP)
Recommendation: Provide both options for approval


**Case C: No LLM Service Found**
Found: No existing LLM infrastructure
Action:

Proceed with new TGI deployment
Follow Section 1: TGI Setup for Local Development


## Step 3: Report Findings

Generate report:
AUDIT REPORT: TGI Service Discovery
Status: [FOUND_TGI | FOUND_OTHER_LLM | NOT_FOUND]
Details:

Service URL: [URL or N/A]
Model: [model name or N/A]
Integration point: [file path or N/A]
Current usage: [describe or N/A]

Recommendation: [REUSE | ADAPT | DEPLOY_NEW]
Justification: [explain]
STOP: Awaiting approval on recommendation before proceeding.


SECTION 1: TGI Setup for Local Development
Option A: Docker Compose (Recommended for Local)
yaml# docker-compose.tgi.yml (NEW FILE)
# Add this to your existing docker-compose setup

version: '3.8'

services:
  tgi:
    image: ghcr.io/huggingface/text-generation-inference:2.0.3
    container_name: tgi-llama-8b
    ports:
      - "8080:80"  # Expose TGI on localhost:8080
    environment:
      - MODEL_ID=meta-llama/Llama-3.1-8B-Instruct
      - HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}  # Set this in .env
      - MAX_BATCH_PREFILL_TOKENS=4096
      - MAX_TOTAL_TOKENS=8192
      - MAX_CONCURRENT_REQUESTS=128
    volumes:
      # Cache downloaded models to avoid re-downloading
      - ./data/huggingface_cache:/data
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 300s  # 5 minutes for model download on first run
    restart: unless-stopped

# Optional: Add to existing app service to link with TGI
  app:
    # ... your existing app config ...
    environment:
      # ... existing env vars ...
      - USE_LLAMA_GATEWAY=true
      - LLM_GATEWAY_URL=http://tgi:80
      - LLM_GATEWAY_TIMEOUT=1.0
    depends_on:
      tgi:
        condition: service_healthy
Environment Variables
bash# .env (ADD THESE LINES)

# HuggingFace token (get from https://huggingface.co/settings/tokens)
# Accept Llama license at https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
HF_TOKEN=hf_your_token_here

# LLM Gateway configuration
USE_LLAMA_GATEWAY=false  # Start with false, enable after testing
LLM_GATEWAY_URL=http://localhost:8080
LLM_GATEWAY_TIMEOUT=1.0
LLM_GATEWAY_MIN_CONFIDENCE=0.7
Starting TGI Locally
bash# 1. Set HuggingFace token
echo "HF_TOKEN=hf_your_token_here" >> .env

# 2. Start TGI (first run downloads ~8GB model, takes 5-10 minutes)
docker-compose -f docker-compose.tgi.yml up -d

# 3. Watch logs (model download progress)
docker-compose -f docker-compose.tgi.yml logs -f tgi

# Expected output:
# tgi  | Downloading model meta-llama/Llama-3.1-8B-Instruct
# tgi  | ████████████████████ 100% 8.5GB/8.5GB
# tgi  | Loading model into GPU memory...
# tgi  | Model loaded successfully
# tgi  | Server ready on port 80

# 4. Test TGI health (wait until model loaded)
curl http://localhost:8080/health
# Expected: {"status":"ready","model_id":"meta-llama/Llama-3.1-8B-Instruct"}

# 5. Test generation
curl http://localhost:8080/generate \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": "What is 2+2?",
    "parameters": {
      "max_new_tokens": 50,
      "temperature": 0.1
    }
  }'

# Expected response:
# {
#   "generated_text": "What is 2+2? 2+2 equals 4."
# }
Option B: Docker Run (Alternative)
bash# If you prefer docker run instead of docker-compose

# Pull image
docker pull ghcr.io/huggingface/text-generation-inference:2.0.3

# Run TGI
docker run -d \
  --name tgi-llama-8b \
  --gpus all \
  -p 8080:80 \
  -e MODEL_ID=meta-llama/Llama-3.1-8B-Instruct \
  -e HUGGING_FACE_HUB_TOKEN=$HF_TOKEN \
  -v $(pwd)/data/huggingface_cache:/data \
  ghcr.io/huggingface/text-generation-inference:2.0.3

# Check logs
docker logs -f tgi-llama-8b

# Test
curl http://localhost:8080/health
Option C: CPU-Only TGI (No GPU)
⚠️ WARNING: CPU mode is 10-20x slower. Only for testing without GPU.
yaml# docker-compose.tgi-cpu.yml
version: '3.8'

services:
  tgi-cpu:
    image: ghcr.io/huggingface/text-generation-inference:2.0.3
    container_name: tgi-llama-8b-cpu
    ports:
      - "8080:80"
    environment:
      - MODEL_ID=meta-llama/Llama-3.1-8B-Instruct
      - HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}
      - MAX_BATCH_PREFILL_TOKENS=2048
      - MAX_TOTAL_TOKENS=4096
      - MAX_CONCURRENT_REQUESTS=4
    volumes:
      - ./data/huggingface_cache:/data
    # No GPU configuration
    restart: unless-stopped
Update timeout for CPU:
bash# .env
LLM_GATEWAY_TIMEOUT=5.0  # Increase to 5 seconds for CPU
```

---

## SECTION 2: LLM Gateway Client Implementation

### AI Agent Audit Prompt
```
# AUDIT TASK 1: LLM Gateway Integration Point Discovery

## Step 1: Find Search Entry Point
Search for where user queries enter the search system:
```bash
# Find search/query functions
grep -r "def search\|def query\|def retrieve" --include="*.py" | grep -v test | grep -v __pycache__

# Find API endpoints that handle search
grep -r "@app.post.*search\|@router.post.*search" --include="*.py"

# Find where embeddings are generated
grep -r "\.encode\|encode_query\|embed.*query" --include="*.py" | head -20

# Find current query processing
grep -r "query.*processing\|preprocess.*query\|clean.*query" --include="*.py"
```

## Step 2: Document Current Flow

Create a flow diagram of current search:
```
User Query → [WHERE DOES IT ENTER?] → [WHAT HAPPENS?] → Search Results
```

Example findings:
```python
# Found in: app/api/search.py
@app.post("/search")
async def search(request: SearchRequest):
    query = request.query  # ← ENTRY POINT
    embedding = embedding_service.encode(query)  # ← BEFORE THIS
    results = vector_db.search(embedding)  # ← EXISTING SEARCH
    return results
```

## Step 3: Identify Integration Point

Mark where to inject LLM Gateway:
```python
@app.post("/search")
async def search(request: SearchRequest):
    query = request.query
    
    # 👈 INSERT LLM GATEWAY HERE (before embedding)
    # if config.USE_LLAMA_GATEWAY:
    #     enrichment = llm_gateway.extract_intent(query)
    #     query = enrichment.to_enhanced_query()
    
    embedding = embedding_service.encode(query)
    results = vector_db.search(embedding)
    return results
```

## Step 4: Report Findings

Report format:
```
AUDIT REPORT: Search Integration Point

Entry Point:
- File: app/api/search.py
- Function: search()
- Line: 45

Current Flow:
1. Receive query from user
2. Generate embedding (line 47)
3. Search vector DB (line 48)
4. Return results (line 49)

Proposed Integration Point:
- Location: Between step 1 and 2 (after line 45)
- Change type: ADDITION (no modifications to existing code)
- Risk: LOW (feature flag allows rollback)

Files to Create:
- services/llm_gateway_client.py (NEW)
- models/enrichment.py (NEW)

Files to Modify:
- app/api/search.py (add 5 lines)
- config.py (add 4 config variables)
- requirements.txt (add httpx, pydantic if missing)

STOP: Awaiting approval to proceed.
```

Configuration (Feature Flag)
python# config.py (ADD THESE LINES)

import os
from typing import Optional

class Config:
    # ... existing config ...
    
    # ===== LLM Gateway Configuration (MVP) =====
    USE_LLAMA_GATEWAY: bool = os.getenv('USE_LLAMA_GATEWAY', 'false').lower() == 'true'
    LLM_GATEWAY_URL: str = os.getenv('LLM_GATEWAY_URL', 'http://localhost:8080')
    LLM_GATEWAY_TIMEOUT: float = float(os.getenv('LLM_GATEWAY_TIMEOUT', '1.0'))
    LLM_GATEWAY_MIN_CONFIDENCE: float = float(os.getenv('LLM_GATEWAY_MIN_CONFIDENCE', '0.7'))
    
    @classmethod
    def validate(cls):
        """Validate configuration on startup."""
        if cls.USE_LLAMA_GATEWAY:
            print(f"✓ LLM Gateway ENABLED")
            print(f"  URL: {cls.LLM_GATEWAY_URL}")
            print(f"  Timeout: {cls.LLM_GATEWAY_TIMEOUT}s")
            print(f"  Min Confidence: {cls.LLM_GATEWAY_MIN_CONFIDENCE}")
        else:
            print(f"○ LLM Gateway DISABLED (using direct query)")

# Call validation on import
Config.validate()

Data Models
python# models/enrichment.py (NEW FILE)

from typing import List, Optional
from pydantic import BaseModel, Field, validator

class EnrichmentOutput(BaseModel):
    """
    Structured output from LLM Gateway after query enrichment.
    
    Example:
    {
        "primary_entity": "Konek ID",
        "intent": "status_inquiry",
        "action_keywords": ["status", "progress", "cycle", "testing"],
        "temporal_filter": "last_90_days",
        "confidence": 0.95,
        "fallback_mode": false
    }
    """
    
    primary_entity: Optional[str] = Field(
        None,
        description="Main entity extracted (e.g., 'Konek ID', 'Project Phoenix')",
        example="Konek ID"
    )
    
    intent: str = Field(
        ...,
        description="Query intent classification",
        example="status_inquiry"
    )
    
    action_keywords: List[str] = Field(
        ...,
        description="Relevant keywords for search (3-8 keywords)",
        min_items=1,
        max_items=10,
        example=["status", "progress", "update", "completion"]
    )
    
    temporal_filter: Optional[str] = Field(
        None,
        description="Time range if detected",
        example="last_90_days"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the enrichment (0.0-1.0)"
    )
    
    fallback_mode: bool = Field(
        False,
        description="True if LLM Gateway failed and we fell back to basic extraction"
    )
    
    @validator('intent')
    def validate_intent(cls, v):
        """Ensure intent is from allowed list."""
        allowed = [
            'status_inquiry',
            'timeline_query',
            'information_retrieval',
            'person_search',
            'unknown'
        ]
        if v not in allowed:
            return 'unknown'
        return v
    
    def to_enhanced_query(self) -> str:
        """
        Convert enrichment to enhanced query string.
        
        Strategy:
        - If high confidence entity: prioritize entity + keywords
        - If low confidence: just use keywords
        
        Returns:
            Enhanced query string for embedding
        """
        if self.primary_entity and self.confidence > 0.7:
            # High confidence: use entity + keywords
            return f"{self.primary_entity} {' '.join(self.action_keywords)}"
        else:
            # Low confidence: keywords only
            return ' '.join(self.action_keywords)
    
    class Config:
        schema_extra = {
            "example": {
                "primary_entity": "Konek ID",
                "intent": "status_inquiry",
                "action_keywords": ["status", "progress", "cycle", "testing"],
                "temporal_filter": "last_90_days",
                "confidence": 0.95,
                "fallback_mode": False
            }
        }

LLM Gateway Client
python# services/llm_gateway_client.py (NEW FILE)

import httpx
import json
import logging
from typing import Optional
import time

from models.enrichment import EnrichmentOutput
from config import Config

logger = logging.getLogger(__name__)

class LLMGatewayClient:
    """
    Client for LLM Gateway (Llama-3.1-8B via TGI).
    
    Responsibilities:
    - Query enrichment with few-shot prompting
    - Entity extraction and intent classification
    - Confidence scoring
    - Timeout handling and automatic fallback
    
    Usage:
        client = LLMGatewayClient()
        enrichment = await client.extract_intent("What's the status of Konek ID?")
        enhanced_query = enrichment.to_enhanced_query()
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        self.base_url = base_url or Config.LLM_GATEWAY_URL
        self.timeout = timeout or Config.LLM_GATEWAY_TIMEOUT
        
        # HTTP client with timeout
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10
            )
        )
        
        logger.info(
            f"LLM Gateway Client initialized: {self.base_url}, timeout={self.timeout}s"
        )
    
    async def extract_intent(
        self, 
        query: str, 
        user_context: Optional[dict] = None
    ) -> EnrichmentOutput:
        """
        Extract structured information from natural language query.
        
        Args:
            query: Raw user query (e.g., "What's the status of Konek ID?")
            user_context: Optional context like recent projects, user role
            
        Returns:
            EnrichmentOutput with extracted entities, intent, keywords, confidence
            
        Behavior:
            - On success: Returns enrichment with confidence score
            - On timeout: Returns fallback enrichment (confidence=0.0)
            - On error: Returns fallback enrichment (confidence=0.0)
            - Never raises exceptions (fail-safe design)
        
        Example:
            >>> enrichment = await client.extract_intent("Status of Konek ID?")
            >>> enrichment.primary_entity
            'Konek ID'
            >>> enrichment.confidence
            0.95
        """
        start_time = time.time()
        
        try:
            # Build few-shot prompt
            prompt = self._build_few_shot_prompt(query, user_context)
            
            # Call TGI /generate endpoint
            response = await self.client.post(
                f"{self.base_url}/generate",
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 256,
                        "temperature": 0.1,  # Low for deterministic output
                        "top_p": 0.9,
                        "do_sample": True,
                        "stop": ["\n\n", "Q:", "Query:"]  # Stop sequences
                    }
                }
            )
            
            response.raise_for_status()
            
            # Parse TGI response
            output_text = response.json()['generated_text']
            enrichment_json = self._extract_json(output_text)
            
            # Validate with Pydantic
            enrichment = EnrichmentOutput(**enrichment_json)
            
            latency = time.time() - start_time
            logger.info(
                f"Query enrichment successful (latency: {latency:.3f}s)",
                extra={
                    "confidence": enrichment.confidence,
                    "entity": enrichment.primary_entity,
                    "intent": enrichment.intent,
                    "query_length": len(query),
                    "latency_ms": int(latency * 1000)
                }
            )
            
            return enrichment
            
        except httpx.TimeoutException:
            latency = time.time() - start_time
            logger.warning(
                f"LLM Gateway timeout after {latency:.3f}s, using fallback enrichment"
            )
            return self._fallback_enrichment(query)
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Invalid LLM response format: {e}, using fallback")
            return self._fallback_enrichment(query)
        
        except Exception as e:
            logger.error(f"Unexpected error in LLM Gateway: {e}, using fallback")
            return self._fallback_enrichment(query)
    
    def _build_few_shot_prompt(
        self, 
        query: str, 
        user_context: Optional[dict]
    ) -> str:
        """
        Build few-shot prompt for Llama-3.1-8B.
        
        Structure: System instruction + Examples + User query
        """
        # Add user context if available
        context_str = ""
        if user_context and user_context.get('recent_projects'):
            projects = user_context['recent_projects'][:5]
            context_str = f"\nUser's recent projects: {', '.join(projects)}"
        
        prompt = f"""You are an AI assistant that extracts structured information from user queries about emails and projects.

Output ONLY valid JSON with these fields:
- primary_entity: The main project/topic name (null if none detected)
- intent: One of [status_inquiry, timeline_query, information_retrieval, person_search, unknown]
- action_keywords: List of relevant keywords for search (3-8 keywords)
- temporal_filter: Time range like "last_7_days", "last_90_days", "future", or null
- confidence: Float 0.0-1.0 indicating extraction confidence

Examples:

Query: "What's the status of Konek ID project?"
{{"primary_entity": "Konek ID", "intent": "status_inquiry", "action_keywords": ["status", "progress", "update", "completion"], "temporal_filter": "last_90_days", "confidence": 0.95}}

Query: "When is the E2E testing for Preauth completing?"
{{"primary_entity": "Preauth", "intent": "timeline_query", "action_keywords": ["E2E testing", "completion", "timeline", "schedule", "deadline"], "temporal_filter": "future", "confidence": 0.90}}

Query: "Tell me about recent updates"
{{"primary_entity": null, "intent": "information_retrieval", "action_keywords": ["recent", "updates", "news", "changes"], "temporal_filter": "last_30_days", "confidence": 0.60}}

Query: "Any emails from Kevin about the launch?"
{{"primary_entity": "launch", "intent": "person_search", "action_keywords": ["Kevin", "launch", "emails", "messages"], "temporal_filter": null, "confidence": 0.75}}

Query: "How is the Konek ID E2E testing progressing?"
{{"primary_entity": "Konek ID", "intent": "status_inquiry", "action_keywords": ["E2E testing", "progress", "status", "cycle"], "temporal_filter": "last_90_days", "confidence": 0.92}}

Query: "Project Phoenix timeline and deliverables"
{{"primary_entity": "Project Phoenix", "intent": "timeline_query", "action_keywords": ["timeline", "deliverables", "milestones", "schedule"], "temporal_filter": null, "confidence": 0.88}}
{context_str}

Now extract from this query:
Query: "{query}"
"""
        
        return prompt
    
    def _extract_json(self, text: str) -> dict:
        """
        Extract JSON from LLM response.
        
        LLM might return:
        - "Here's the extraction: {...}"
        - "```json\n{...}\n```"
        - Just "{...}"
        
        We extract the JSON object regardless of surrounding text.
        """
        # Remove markdown code blocks if present
        text = text.replace('```json', '').replace('```', '')
        
        # Find JSON object boundaries
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start == -1 or end == 0:
            raise ValueError(f"No JSON object found in response: {text[:100]}")
        
        json_str = text[start:end]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}\nJSON: {json_str[:200]}")
    
    def _fallback_enrichment(self, query: str) -> EnrichmentOutput:
        """
        Fallback enrichment when LLM Gateway fails.
        
        Strategy:
        - Extract basic keywords by splitting on spaces
        - Filter out common stop words
        - No entity extraction (primary_entity = None)
        - Confidence = 0.0 (indicates fallback mode)
        - fallback_mode = True
        """
        # Stop words to filter out
        stop_words = {
            'the', 'and', 'for', 'with', 'about', 'what', 'how', 'when',
            'is', 'are', 'was', 'were', 'a', 'an', 'in', 'on', 'at'
        }
        
        # Simple keyword extraction
        keywords = [
            word.strip().lower() 
            for word in query.split() 
            if len(word) > 2 and word.lower() not in stop_words
        ]
        
        # Limit to 8 keywords
        keywords = keywords[:8]
        
        logger.info(
            f"Fallback enrichment: extracted {len(keywords)} keywords from query"
        )
        
        return EnrichmentOutput(
            primary_entity=None,
            intent='unknown',
            action_keywords=keywords if keywords else ['search'],  # Default if empty
            temporal_filter=None,
            confidence=0.0,
            fallback_mode=True
        )
    
    async def close(self):
        """Close HTTP client. Call on application shutdown."""
        await self.client.aclose()
        logger.info("LLM Gateway Client closed")

Integration into Existing Search
python# app/api/search.py (MODIFY EXISTING FILE)
# Or wherever your search endpoint is located

from config import Config
from services.llm_gateway_client import LLMGatewayClient
from models.enrichment import EnrichmentOutput

# ===== INITIALIZATION (add to your app setup) =====

# Initialize LLM Gateway client (singleton)
llm_gateway_client = None

if Config.USE_LLAMA_GATEWAY:
    llm_gateway_client = LLMGatewayClient()
    logger.info("✓ LLM Gateway Client initialized")
else:
    logger.info("○ LLM Gateway disabled")


# ===== MODIFY YOUR SEARCH ENDPOINT =====

@app.post("/search")  # Or your actual search endpoint
async def search(request: SearchRequest):
    """
    Search endpoint with optional LLM Gateway enrichment.
    
    MVP CHANGE: Add query enrichment before embedding generation.
    """
    user_id = request.user_id
    query = request.query
    
    logger.info(f"Search request: user={user_id}, query='{query}'")
    
    # ===== MVP: LLM GATEWAY ENRICHMENT (NEW CODE) =====
    enhanced_query = query  # Default: use original query
    enrichment_metadata = None
    
    if llm_gateway_client:
        try:
            # Extract intent and entities
            enrichment = await llm_gateway_client.extract_intent(
                query=query,
                user_context={
                    'recent_projects': request.user_context.get('recent_projects', [])
                }
            )
            
            # Use enrichment if confidence is high enough
            if enrichment.confidence >= Config.LLM_GATEWAY_MIN_CONFIDENCE:
                enhanced_query = enrichment.to_enhanced_query()
                
                logger.info(
                    f"Query enriched: '{query}' → '{enhanced_query}'",
                    extra={
                        "confidence": enrichment.confidence,
                        "entity": enrichment.primary_entity,
                        "intent": enrichment.intent
                    }
                )
            else:
                logger.info(
                    f"Low confidence enrichment ({enrichment.confidence:.2f}), "
                    f"using original query"
                )
            
            # Store enrichment metadata for response
            enrichment_metadata = {
                'enriched': True,
                'confidence': enrichment.confidence,
                'entity': enrichment.primary_entity,
                'intent': enrichment.intent,
                'fallback_mode': enrichment.fallback_mode
            }
            
        except Exception as e:
            logger.error(f"LLM Gateway error: {e}, using original query")
            enhanced_query = query  # Fallback to original
    
    # ===== EXISTING CODE: No changes below this line =====
    
    # Generate embedding (now uses enhanced query if enrichment succeeded)
    embedding = embedding_service.encode(enhanced_query)
    
    # Vector search (existing code)
    results = vector_db.search(
        user_id=user_id,
        query_vector=embedding,
        limit=10
    )
    
    # Post-processing and ranking (existing code)
    # ... your existing result processing ...
    
    # Return results (optionally include enrichment metadata)
    return {
        'results': results,
        'query': query,
        'enhanced_query': enhanced_query if enhanced_query != query else None,
        'enrichment': enrichment_metadata  # Optional: for debugging/analytics
    }


# ===== CLEANUP ON SHUTDOWN (add to app shutdown) =====

@app.on_event("shutdown")
async def shutdown_event():
    """Close LLM Gateway client on shutdown."""
    if llm_gateway_client:
        await llm_gateway_client.close()

SECTION 3: Testing (Local Development)
Unit Tests
python# tests/test_llm_gateway_client.py (NEW FILE)

import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from services.llm_gateway_client import LLMGatewayClient
from models.enrichment import EnrichmentOutput

@pytest.fixture
def client():
    """Create LLM Gateway client for testing."""
    return LLMGatewayClient(
        base_url="http://test:8080",
        timeout=1.0
    )

@pytest.mark.asyncio
async def test_extract_intent_success(client):
    """Test successful entity extraction from LLM."""
    # Mock successful TGI response
    mock_response = Mock()
    mock_response.json.return_value = {
        'generated_text': '{"primary_entity": "Konek ID", "intent": "status_inquiry", "action_keywords": ["status", "progress"], "temporal_filter": "last_90_days", "confidence": 0.95}'
    }
    mock_response.raise_for_status = Mock()
    
    with patch.object(client.client, 'post', return_value=mock_response):
        result = await client.extract_intent("What's the status of Konek ID?")
    
    # Assertions
    assert isinstance(result, EnrichmentOutput)
    assert result.primary_entity == "Konek ID"
    assert result.intent == "status_inquiry"
    assert result.confidence == 0.95
    assert result.fallback_mode == False
    assert "status" in result.action_keywords

@pytest.mark.asyncio
async def test_extract_intent_timeout(client):
    """Test timeout handling with automatic fallback."""
    # Mock timeout
    with patch.object(
        client.client, 
        'post', 
        side_effect=httpx.TimeoutException("Request timeout")
    ):
        result = await client.extract_intent("What's the status?")
    
    # Should fallback gracefully
    assert isinstance(result, EnrichmentOutput)
    assert result.fallback_mode == True
    assert result.confidence == 0.0
    assert len(result.action_keywords) > 0  # Should extract basic keywords

@pytest.mark.asyncio
async def test_extract_intent_invalid_json(client):
    """Test handling of invalid JSON response."""
    # Mock invalid JSON
    mock_response = Mock()
    mock_response.json.return_value = {
        'generated_text': 'This is not valid JSON at all'
    }
    mock_response.raise_for_status = Mock()
    
    with patch.object(client.client, 'post', return_value=mock_response):
        result = await client.extract_intent("What's the status?")
    
    # Should fallback gracefully
    assert result.fallback_mode == True
    assert result.confidence == 0.0

def test_enrichment_to_enhanced_query_high_confidence():
    """Test conversion with high confidence entity."""
    enrichment = EnrichmentOutput(
        primary_entity="Konek ID",
        intent="status_inquiry",
        action_keywords=["status", "progress", "update"],
        confidence=0.95
    )
    
    enhanced = enrichment.to_enhanced_query()
    
    # Should include entity when confidence high
    assert "Konek ID" in enhanced
    assert "status" in enhanced

def test_enrichment_to_enhanced_query_low_confidence():
    """Test conversion with low confidence (skip entity)."""
    enrichment = EnrichmentOutput(
        primary_entity="Konek ID",
        intent="status_inquiry",
        action_keywords=["status", "progress"],
        confidence=0.5  # Low confidence
    )
    
    enhanced = enrichment.to_enhanced_query()
    
    # Should NOT include entity when confidence low
    assert "Konek ID" not in enhanced
    assert "status" in enhanced
    assert "progress" in enhanced

def test_fallback_enrichment():
    """Test fallback enrichment for failed LLM call."""
    client = LLMGatewayClient()
    
    result = client._fallback_enrichment(
        "What is the status of Project Phoenix and when will testing complete?"
    )
    
    # Verify fallback behavior
    assert result.primary_entity is None
    assert result.intent == 'unknown'
    assert result.confidence == 0.0
    assert result.fallback_mode == True
    assert len(result.action_keywords) > 0
    # Should extract: "status", "project", "phoenix", "testing", "complete"
    assert "status" in result.action_keywords
Integration Test (End-to-End)
python# tests/test_search_integration.py (NEW FILE)

import pytest
from fastapi.testclient import TestClient

from app.main import app  # Your FastAPI app
from config import Config

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_search_with_llm_gateway_disabled(client, monkeypatch):
    """Test search works with LLM Gateway disabled (baseline)."""
    # Disable feature flag
    monkeypatch.setattr(Config, 'USE_LLAMA_GATEWAY', False)
    
    response = client.post(
        "/search",
        json={
            "user_id": "test_user",
            "query": "What's the status of Konek ID?"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify search works (existing functionality)
    assert "results" in data
    assert data.get("enhanced_query") is None  # Not enriched

def test_search_with_llm_gateway_enabled(client, monkeypatch, mock_tgi):
    """Test search with LLM Gateway enabled."""
    # Enable feature flag
    monkeypatch.setattr(Config, 'USE_LLAMA_GATEWAY', True)
    
    # Mock TGI response (you'll need to implement mock_tgi fixture)
    # See below for mock implementation
    
    response = client.post(
        "/search",
        json={
            "user_id": "test_user",
            "query": "What's the status of Konek ID?"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify enrichment was applied
    assert "results" in data
    assert "enrichment" in data
    assert data["enrichment"]["enriched"] == True
    assert data["enrichment"]["entity"] == "Konek ID"

@pytest.fixture
def mock_tgi(monkeypatch):
    """Mock TGI service for testing."""
    async def mock_post(*args, **kwargs):
        mock_response = Mock()
        mock_response.json.return_value = {
            'generated_text': '{"primary_entity": "Konek ID", "intent": "status_inquiry", "action_keywords": ["status", "progress"], "confidence": 0.95}'
        }
        mock_response.raise_for_status = Mock()
        return mock_response
    
    # Patch httpx.AsyncClient.post
    monkeypatch.setattr(
        "httpx.AsyncClient.post",
        mock_post
    )

Manual Testing Script
python# scripts/test_llm_gateway.py (NEW FILE)
# Manual testing script for local development

import asyncio
import sys
sys.path.insert(0, '.')

from services.llm_gateway_client import LLMGatewayClient
from config import Config

async def test_queries():
    """Test various queries against LLM Gateway."""
    
    # Initialize client
    client = LLMGatewayClient()
    
    # Test queries
    test_cases = [
        "What's the status of Konek ID?",
        "When is E2E testing for Preauth completing?",
        "Tell me about recent updates",
        "Any emails from Kevin about the launch?",
        "Project Phoenix timeline and deliverables",
        "How is testing going?",
        "Status update please"
    ]
    
    print("=" * 80)
    print("LLM Gateway Manual Test")
    print(f"TGI URL: {Config.LLM_GATEWAY_URL}")
    print(f"Timeout: {Config.LLM_GATEWAY_TIMEOUT}s")
    print("=" * 80)
    print()
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_cases)}: {query}")
        print(f"{'='*80}")
        
        try:
            # Extract intent
            enrichment = await client.extract_intent(query)
            
            # Display results
            print(f"✓ Enrichment successful")
            print(f"  Primary Entity:   {enrichment.primary_entity or 'None'}")
            print(f"  Intent:           {enrichment.intent}")
            print(f"  Keywords:         {', '.join(enrichment.action_keywords)}")
            print(f"  Temporal Filter:  {enrichment.temporal_filter or 'None'}")
            print(f"  Confidence:       {enrichment.confidence:.2f}")
            print(f"  Fallback Mode:    {enrichment.fallback_mode}")
            print(f"  Enhanced Query:   '{enrichment.to_enhanced_query()}'")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Close client
    await client.close()
    
    print(f"\n{'='*80}")
    print("Test complete!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(test_queries())
Run manual tests:
bash# 1. Ensure TGI is running
docker ps | grep tgi

# 2. Enable LLM Gateway
export USE_LLAMA_GATEWAY=true

# 3. Run test script
python scripts/test_llm_gateway.py

# Expected output:
# ================================================================================
# Test 1/7: What's the status of Konek ID?
# ================================================================================
# ✓ Enrichment successful
#   Primary Entity:   Konek ID
#   Intent:           status_inquiry
#   Keywords:         status, progress, update, completion
#   Temporal Filter:  last_90_days
#   Confidence:       0.95
#   Fallback Mode:    False
#   Enhanced Query:   'Konek ID status progress update completion'
# ...

SECTION 4: Local Development Workflow
Step-by-Step Setup
bash# ===== STEP 1: Set up HuggingFace Token =====
# Get token from: https://huggingface.co/settings/tokens
# Accept Llama license: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct

echo "HF_TOKEN=hf_your_token_here" >> .env
echo "USE_LLAMA_GATEWAY=false" >> .env  # Start disabled

# ===== STEP 2: Start TGI Service =====
docker-compose -f docker-compose.tgi.yml up -d

# Wait for model download (5-10 minutes first time)
docker-compose -f docker-compose.tgi.yml logs -f tgi

# Test TGI
curl http://localhost:8080/health
# Expected: {"status":"ready"}

# ===== STEP 3: Install Dependencies =====
pip install httpx pydantic  # If not already installed

# ===== STEP 4: Create New Files =====
# Use AI agent to create:
# - models/enrichment.py
# - services/llm_gateway_client.py

# ===== STEP 5: Modify Existing Files =====
# Update config.py (add LLM Gateway config)
# Update app/api/search.py (add enrichment integration)

# ===== STEP 6: Run Unit Tests =====
pytest tests/test_llm_gateway_client.py -v

# ===== STEP 7: Manual Testing =====
python scripts/test_llm_gateway.py

# ===== STEP 8: Enable Feature Flag =====
# Edit .env
echo "USE_LLAMA_GATEWAY=true" >> .env

# ===== STEP 9: Test Search Endpoint =====
# Start your app
python -m uvicorn app.main:app --reload

# Test search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "What is the status of Konek ID?"
  }'

# ===== STEP 10: Compare Results =====
# A) With LLM Gateway enabled (USE_LLAMA_GATEWAY=true)
# B) With LLM Gateway disabled (USE_LLAMA_GATEWAY=false)
# Compare result quality, latency, relevance

SECTION 5: Troubleshooting Guide
Common Issues
Issue 1: TGI Container Won't Start
bash# Check logs
docker logs tgi-llama-8b

# Common causes:
# 1. Invalid HF token
#    Solution: Check token at https://huggingface.co/settings/tokens

# 2. Llama license not accepted
#    Solution: Visit https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct

# 3. No GPU available
#    Solution: Use CPU mode (slower) or add GPU support

# 4. Port 8080 already in use
#    Solution: Change port in docker-compose.tgi.yml
#    ports:
#      - "8081:80"  # Use 8081 instead
Issue 2: "Connection Refused" Error
bash# Check if TGI is actually running
curl http://localhost:8080/health

# If connection refused:
# 1. TGI not started
docker ps | grep tgi  # Should show running container

# 2. Wrong URL in config
# Check .env: LLM_GATEWAY_URL=http://localhost:8080

# 3. Inside Docker network
# If your app runs in Docker, use service name:
# LLM_GATEWAY_URL=http://tgi:80
Issue 3: Timeouts (>1 second latency)
bash# Cause: CPU mode or overloaded GPU
# Solution 1: Increase timeout
echo "LLM_GATEWAY_TIMEOUT=5.0" >> .env

# Solution 2: Check GPU usage
docker stats tgi-llama-8b

# Solution 3: Reduce concurrent requests
# Edit docker-compose.tgi.yml:
# MAX_CONCURRENT_REQUESTS=32  # Reduce from 128
Issue 4: Invalid JSON from LLM
python# Enable debug logging to see raw responses
import logging
logging.basicConfig(level=logging.DEBUG)

# Check logs for:
# "generated_text": "..."

# Common causes:
# 1. Temperature too high (more creative = less structured)
#    Solution: Ensure temperature=0.1 in client code

# 2. Prompt not clear enough
#    Solution: Review few-shot examples in _build_few_shot_prompt()

# 3. Model not following format
#    Solution: Add more examples or use stricter stop sequences

SECTION 6: Success Criteria (MVP)
Metrics to Track
python# Track these metrics during MVP testing

metrics = {
    # Performance
    "llm_gateway_latency_p50": "<150ms",  # Target
    "llm_gateway_latency_p95": "<500ms",  # Max acceptable
    "llm_gateway_latency_p99": "<1000ms",  # Timeout threshold
    
    # Quality
    "confidence_score_avg": ">0.75",  # Average confidence
    "fallback_rate": "<10%",  # Percentage of queries using fallback
    "entity_extraction_accuracy": ">85%",  # Manual evaluation
    
    # Reliability
    "llm_gateway_uptime": ">99%",  # TGI availability
    "error_rate": "<1%",  # HTTP errors, parsing errors
    
    # Business Impact
    "search_quality_improvement": "Manual evaluation",  # A/B test
    "user_satisfaction": "Collect feedback",  # Survey or thumbs up/down
}
Manual Evaluation Process
python# scripts/evaluate_enrichment.py (NEW FILE)
# Manual evaluation helper

import asyncio
from services.llm_gateway_client import LLMGatewayClient

# Golden dataset for evaluation
test_queries = [
    {
        "query": "What's the status of Konek ID?",
        "expected_entity": "Konek ID",
        "expected_intent": "status_inquiry"
    },
    {
        "query": "When is E2E testing completing?",
        "expected_entity": None,  # No specific project mentioned
        "expected_intent": "timeline_query"
    },
    # Add 20-30 more test cases...
]

async def evaluate():
    client = LLMGatewayClient()
    
    correct = 0
    total = len(test_queries)
    
    for test in test_queries:
        enrichment = await client.extract_intent(test["query"])
        
        # Check entity extraction
        entity_correct = (enrichment.primary_entity == test["expected_entity"])
        
        # Check intent classification
        intent_correct = (enrichment.intent == test["expected_intent"])
        
        if entity_correct and intent_correct:
            correct += 1
            print(f"✓ {test['query']}")
        else:
            print(f"✗ {test['query']}")
            print(f"  Expected: entity={test['expected_entity']}, intent={test['expected_intent']}")
            print(f"  Got:      entity={enrichment.primary_entity}, intent={enrichment.intent}")
    
    accuracy = correct / total
    print(f"\nAccuracy: {accuracy:.2%} ({correct}/{total})")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(evaluate())
```

---

## Summary: MVP Deliverables (Local)

### What You'll Have After MVP

✅ **Infrastructure:**
- TGI service running locally (Docker Compose)
- Llama-3.1-8B model loaded and ready

✅ **Code:**
- `services/llm_gateway_client.py` - LLM client with fallback
- `models/enrichment.py` - Pydantic models for structured output
- Modified search endpoint with enrichment integration
- Feature flag for easy enable/disable

✅ **Tests:**
- Unit tests for LLM Gateway client
- Integration tests for search flow
- Manual testing scripts

✅ **Documentation:**
- This OpenSpec document
- Inline code documentation
- Troubleshooting guide

### Next Steps After MVP

**Phase 2: Production Deployment (OpenShift)**
- Migrate TGI to OpenShift with GPU scheduling
- Add production monitoring (Prometheus/Grafana)
- Implement HPA for auto-scaling
- Set up CI/CD pipeline

**Phase 3: Advanced Features**
- Database schema updates (project_tag extraction)
- Progressive filter relaxation
- E5 embedding migration
- Audit logging and analytics

---

## Appendix: File Checklist

### New Files to Create
```
✓ docker-compose.tgi.yml           # TGI service definition
✓ models/enrichment.py              # Pydantic models
✓ services/llm_gateway_client.py   # LLM client
✓ tests/test_llm_gateway_client.py # Unit tests
✓ tests/test_search_integration.py # Integration tests
✓ scripts/test_llm_gateway.py      # Manual testing
✓ scripts/evaluate_enrichment.py   # Evaluation script
```

### Files to Modify
```
✓ .env                              # Add HF_TOKEN, feature flags
✓ config.py                         # Add LLM Gateway config
✓ app/api/search.py                 # Add enrichment integration
✓ requirements.txt                  # Add httpx, pydantic (if missing)
```

### Files to Review (No Changes)
```
○ Database schema files             # No changes in MVP
○ Embedding service                 # No changes in MVP
○ Vector DB code                    # No changes in MVP
○ Email ingestion pipeline          # No changes in MVP
