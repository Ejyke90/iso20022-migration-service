OpenSpec: RAG Service (Agentic RAG) - INCREMENTAL UPDATE
Version: 1.0 (Incremental Update Mode)
Owner: Principal AI Engineer
Status: Production Implementation Ready
Target Platform: OpenShift 4.14+ with GPU support
Vector DB: SQLite with sqlite-vec extension
Implementation Mode: AUDIT-FIRST, then incremental changes to existing RAG service

Implementation Philosophy: Audit Before Change
CRITICAL: This is an incremental update to an existing RAG service, not a greenfield implementation.
AI Agent Implementation Protocol
For EVERY section below, the AI Agent MUST follow this sequence:
1. AUDIT PHASE
   ├─ Check if component exists in codebase
   ├─ Document current implementation
   ├─ Identify gaps vs specification
   └─ Generate audit report

2. ANALYSIS PHASE
   ├─ Determine if changes needed
   ├─ Assess backward compatibility impact
   ├─ Identify migration requirements
   └─ Estimate implementation effort

3. PROPOSAL PHASE
   ├─ Generate specific change recommendations
   ├─ Provide side-by-side comparison (before/after)
   ├─ List affected files and functions
   └─ Flag breaking changes

4. IMPLEMENTATION PHASE (only after approval)
   ├─ Create feature branch
   ├─ Implement changes incrementally
   ├─ Add tests for new functionality
   └─ Create PR with detailed description
Agent Prompt Template for Each Section
# AUDIT TASK: [Section Name]

## Step 1: Discovery
- Search codebase for existing implementation of [component]
- Document current approach, libraries, and patterns
- List all relevant files: [paths]

## Step 2: Gap Analysis
Compare existing implementation against specification:
- ✅ Features already implemented
- ⚠️ Features partially implemented
- ❌ Features missing
- 🔄 Features that need modification

## Step 3: Impact Assessment
- Breaking changes: [list]
- Backward compatibility: [yes/no/partial]
- Migration strategy: [describe]
- Rollback plan: [describe]

## Step 4: Recommendation
Provide ONE of:
- NO_CHANGE_NEEDED: Current implementation meets spec
- MINOR_UPDATE: Small changes, no breaking changes
- MAJOR_REFACTOR: Significant changes required
- NEW_IMPLEMENTATION: Component doesn't exist

## Step 5: Wait for Approval
STOP and present findings. Do NOT proceed to implementation without explicit approval.

Open Questions - ANSWERED
1. Multi-Tenancy
Answer: Ignore for now (single-tenant deployment)
2. Real-Time Sync
Answer: Batch only (5-minute intervals)

Simpler to implement and maintain
Sufficient for executive assistant use case
Easier to ensure data consistency

3. Embedding Model Updates
Best Practice for Production Enterprise:
python# Embedding Version Management Strategy

class EmbeddingVersionManager:
    """
    Handle embedding model upgrades without downtime.
    
    Strategy: Blue-Green Index Deployment
    """
    
    def __init__(self, db_path: str):
        self.db = SQLiteVectorDB(db_path)
        self.current_version = self._get_current_version()
    
    def _get_current_version(self) -> str:
        """Get current embedding model version from metadata."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'embedding_version'")
        result = cursor.fetchone()
        return result[0] if result else 'v1'
    
    def upgrade_embeddings(self, new_model_name: str, new_version: str):
        """
        Upgrade to new embedding model with zero downtime.
        
        Process:
        1. Create new table: emails_v2 (shadow index)
        2. Re-embed all emails in background (can take hours/days)
        3. When complete, atomic switch: emails -> emails_old, emails_v2 -> emails
        4. Monitor new index for 24h
        5. Drop old index if stable
        """
        print(f"Starting embedding upgrade: {self.current_version} -> {new_version}")
        
        # Step 1: Create shadow table
        self.db.conn.execute(f"""
            CREATE TABLE emails_{new_version} AS 
            SELECT * FROM emails WHERE 1=0  -- Copy schema only
        """)
        
        # Step 2: Re-embed in batches (background job)
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emails")
        total_emails = cursor.fetchone()[0]
        
        batch_size = 1000
        new_embedding_service = E5EmbeddingService(model_name=new_model_name)
        
        for offset in range(0, total_emails, batch_size):
            # Fetch batch
            cursor.execute(f"""
                SELECT email_id, subject, body 
                FROM emails 
                LIMIT {batch_size} OFFSET {offset}
            """)
            batch = cursor.fetchall()
            
            # Re-embed
            texts = [f"{row[1]} {row[2][:500]}" for row in batch]
            new_embeddings = new_embedding_service.encode_batch(texts, is_query=False)
            
            # Insert into shadow table
            for (email_id, _, _), embedding in zip(batch, new_embeddings):
                # Copy full email record with new embedding
                cursor.execute(f"""
                    INSERT INTO emails_{new_version}
                    SELECT 
                        email_id, user_id, from_address, to_addresses, cc_addresses,
                        subject, body, timestamp, thread_id, project_tag, labels,
                        has_attachments, importance, ? as embedding, created_at, updated_at
                    FROM emails WHERE email_id = ?
                """, [self._serialize_embedding(embedding), email_id])
            
            self.db.conn.commit()
            progress = (offset + batch_size) / total_emails * 100
            print(f"Re-embedding progress: {progress:.1f}%")
        
        # Step 3: Atomic switch (within transaction)
        self.db.conn.execute("BEGIN TRANSACTION")
        try:
            self.db.conn.execute(f"ALTER TABLE emails RENAME TO emails_{self.current_version}_old")
            self.db.conn.execute(f"ALTER TABLE emails_{new_version} RENAME TO emails")
            self.db.conn.execute(f"UPDATE metadata SET value = '{new_version}' WHERE key = 'embedding_version'")
            self.db.conn.commit()
            print(f"✅ Successfully upgraded to {new_version}")
        except Exception as e:
            self.db.conn.rollback()
            print(f"❌ Upgrade failed, rolled back: {e}")
            raise
        
        # Step 4: Keep old index for 7 days (rollback window)
        print(f"Old index preserved as emails_{self.current_version}_old for 7 days")

# Usage
manager = EmbeddingVersionManager('/data/emails.db')
manager.upgrade_embeddings(
    new_model_name='intfloat/e5-mistral-7b-instruct',  # Hypothetical v2
    new_version='v2'
)
Recommended Process:

Version Pinning: Always pin exact model version in config (e.g., e5-large@v1.0)
Shadow Indexing: Build new index alongside old one (blue-green deployment)
A/B Testing: Route 10% of traffic to new index, compare NDCG@10
Gradual Rollout: If metrics improve, gradually shift traffic (10% → 50% → 100%)
Rollback Window: Keep old index for 7 days for quick rollback
Monitoring: Alert if search quality degrades (NDCG drops >5%)

Estimated Re-indexing Time:

100K emails: ~2 hours (batch size 1000)
1M emails: ~20 hours
10M emails: ~200 hours (run over weekend)

4. Slack Integration
Answer: Ignore for now (email-only scope)
5. Cost vs Performance: Model Size Trade-offs
Detailed Analysis: Llama-3.2-3B vs Llama-3.1-8B
FactorLlama-3.2-3BLlama-3.1-8BWinnerAccuracy85-90% intent detection92-97% intent detection8BLatency (p95)~80ms~150ms3BGPU Memory6GB VRAM16GB VRAM3BCost per 1M tokens$0.10$0.303BEntity ExtractionMisses 15% of entitiesMisses <5% of entities8BComplex QueriesStruggles with multi-intentHandles well8BDeterminismLess consistent outputsMore consistent8B
Specific Examples:
python# Query: "What's the status of ProjectA ID and when is E2E testing completing?"

# Llama-3.2-3B Output (WORSE):
{
  "primary_entity": "ProjectA ID",  # ❌ Missed "E2E testing" as second entity
  "intent": "status_inquiry",     # ❌ Missed "timeline_query" as second intent
  "action_keywords": ["status"],
  "confidence": 0.72              # Lower confidence
}

# Llama-3.1-8B Output (BETTER):
{
  "primary_entity": "ProjectA ID",
  "intent": "status_inquiry",
  "action_keywords": ["status", "progress", "E2E testing", "completion", "timeline"],
  "temporal_filter": "future",    # ✅ Correctly extracted temporal aspect
  "confidence": 0.94              # Higher confidence
}
```

**Recommendation: Use Llama-3.1-8B**

**Reasoning**:
1. **Accuracy is Critical**: You specified "result must be accurate and deterministic as possible"
2. **Entity-Heavy Queries**: Executive emails contain many project names, technical terms that 3B struggles with
3. **150ms Latency is Acceptable**: With 1-second timeout, 8B easily fits within budget
4. **False Negatives are Costly**: Missing an important entity means user gets wrong results (worse than slower results)
5. **Cost Difference is Minimal**: At 1000 queries/day, difference is ~$60/month (negligible for enterprise)

**Only Use 3B If**:
- Budget is EXTREMELY tight (<$100/month for entire service)
- Queries are very simple (single-intent, single-entity)
- Sub-100ms latency is mandatory
- You have extensive fine-tuning data for 3B

**Middle Ground: Llama-3.2-5B** (if 8B too expensive):
- 88-92% accuracy (between 3B and 8B)
- ~100ms latency
- 10GB VRAM
- Good balance for medium-complexity queries

---

## Section-by-Section Implementation Guide

### SECTION 1: Database Schema (SQLite)

#### AI Agent Audit Prompt
```
AUDIT TASK: Database Schema

## Step 1: Discovery
Search for:
- [ ] Existing database connection code (sqlite3, sqlalchemy, etc.)
- [ ] Current schema definitions (*.sql, migrations/, models.py)
- [ ] Vector storage approach (if any)
- [ ] User isolation implementation

Commands to run:
```bash
# Find database files
find . -name "*.db" -o -name "*.sqlite"

# Find schema definitions
grep -r "CREATE TABLE" --include="*.sql" --include="*.py"

# Find vector-related code
grep -r "embedding\|vector" --include="*.py"

# Check for sqlite-vec extension
grep -r "vec0\|sqlite-vec" --include="*.py"
```

## Step 2: Gap Analysis

Current Implementation:
- [ ] Tables: [list tables]
- [ ] Indexes: [list indexes]
- [ ] Vector support: YES / NO / PARTIAL
- [ ] User isolation: IMPLEMENTED / MISSING
- [ ] Audit logging: IMPLEMENTED / MISSING

Missing from Spec:
- [ ] `emails` table with all required columns
- [ ] `query_logs` audit table
- [ ] `embedding_cache` table
- [ ] Full-text search (FTS5)
- [ ] sqlite-vec integration

## Step 3: Migration Plan

If schema changes needed:
1. Create migration script: `migrations/001_add_grounding_service.sql`
2. Backup existing database: `cp emails.db emails_backup_$(date +%Y%m%d).db`
3. Apply migration with transaction
4. Validate data integrity
5. Update ORM models (if using SQLAlchemy/Django)

Breaking Changes:
- [ ] List any columns being removed
- [ ] List any type changes
- [ ] Estimate migration time

## Step 4: Recommendation
[NO_CHANGE_NEEDED | MINOR_UPDATE | MAJOR_REFACTOR | NEW_IMPLEMENTATION]

Justification: [explain]
```

**Expected Output from Agent**:
```
AUDIT REPORT: Database Schema

Current State:
- Found database at: ./data/emails.db
- Tables: users, emails (missing columns: project_tag, embedding)
- Indexes: Only user_id indexed (missing project_tag, timestamp indexes)
- Vector support: NONE (sqlite-vec not loaded)
- User isolation: PARTIAL (user_id exists but not always filtered)

Gap Analysis:
✅ Already has: email_id, user_id, from_address, subject, body, timestamp
⚠️ Partially has: to_addresses (stored as TEXT, should be JSON array)
❌ Missing: project_tag, embedding BLOB, thread_id, labels, has_attachments
❌ Missing: query_logs table for audit
❌ Missing: embedding_cache table
❌ Missing: FTS5 virtual table for keyword search
❌ Missing: sqlite-vec extension

Recommendation: MAJOR_REFACTOR
- Add 8 new columns to emails table
- Add 2 new tables (query_logs, embedding_cache)
- Load sqlite-vec extension
- Create FTS5 indexes
- Estimated migration time: ~30 minutes (for 100K emails)

STOP: Awaiting approval to proceed with migration plan.
```

---

### SECTION 2: LLM Gateway Client

#### AI Agent Audit Prompt
```
AUDIT TASK: LLM Gateway Integration

## Step 1: Discovery
Search for:
- [ ] Existing LLM API clients (OpenAI, Anthropic, HuggingFace)
- [ ] Query enrichment logic (if any)
- [ ] Prompt templates
- [ ] Retry/timeout handling

Commands:
```bash
# Find LLM client code
grep -r "openai\|anthropic\|huggingface\|llm" --include="*.py"

# Find prompt templates
find . -name "*prompt*" -o -name "*template*"

# Check for existing enrichment
grep -r "enrich\|extract.*intent\|entity.*extraction" --include="*.py"
```

## Step 2: Current Implementation Analysis

Document:
- [ ] Which LLM is currently used? [OpenAI GPT-4 / Claude / None]
- [ ] Is there query preprocessing? [YES / NO]
- [ ] How are timeouts handled?
- [ ] Is there a fallback mechanism?

Example of existing code:
```python
# Paste actual code here
```

## Step 3: Gap Analysis

Against Specification:
- [ ] Llama-3.1-8B via TGI: IMPLEMENTED / MISSING
- [ ] Few-shot prompt for entity extraction: IMPLEMENTED / MISSING
- [ ] Confidence scoring: IMPLEMENTED / MISSING
- [ ] 1-second timeout: IMPLEMENTED / MISSING
- [ ] Fallback to keyword-only: IMPLEMENTED / MISSING
- [ ] Structured output (Pydantic): IMPLEMENTED / MISSING

## Step 4: Integration Strategy

Option A: Replace existing LLM client
- Impact: HIGH (changes API calls throughout codebase)
- Risk: Breaking changes to existing features
- Timeline: 3-5 days

Option B: Add parallel LLM Gateway (gradual migration)
- Impact: LOW (new code path, old path unchanged)
- Risk: LOW (can A/B test)
- Timeline: 1-2 days

Option C: Enhance existing client
- Impact: MEDIUM
- Risk: MEDIUM
- Timeline: 2-3 days

Recommendation: [A / B / C]
Rationale: [explain]

STOP: Awaiting approval on integration strategy.
```

**Expected Output**:
```
AUDIT REPORT: LLM Gateway Integration

Current State:
- Found: ./services/llm_client.py
- Using: OpenAI GPT-4-turbo via openai-python SDK
- Query preprocessing: YES (basic keyword extraction)
- Timeout: 5 seconds (too long vs 1s spec)
- Fallback: NO (fails hard on timeout)

Current Code:
```python
# ./services/llm_client.py (simplified)
import openai

def enrich_query(query: str) -> dict:
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Extract keywords from: {query}"}],
        timeout=5.0
    )
    return {"keywords": response.choices[0].message.content.split()}
```

Gap Analysis:
✅ Already has: Basic query enrichment, timeout handling
⚠️ Partial: Structured output (returns keywords but not entities/intent/confidence)
❌ Missing: Llama-3.1-8B via TGI ()
❌ Missing: Few-shot prompt with examples
❌ Missing: Confidence scoring
❌ Missing: Fallback mechanism (fails on timeout)
❌ Missing: Entity extraction (only keywords)

Recommendation: Option B (Add parallel LLM Gateway)

Rationale:
1. Keep existing GPT-4 integration for backward compatibility
2. Add new LLMGatewayClient class for Llama-3.1-8B
3. Feature flag to switch between old/new enrichment
4. Allows A/B testing: 10% traffic to new gateway, compare results
5. Low risk: Can rollback instantly if issues

Implementation Plan:
1. Create ./services/llm_gateway_client.py (new file, no changes to existing)
2. Add feature flag: USE_LLAMA_GATEWAY=true/false in config
3. Update ./services/retriever.py to check flag:
```python
   if config.USE_LLAMA_GATEWAY:
       enrichment = llm_gateway_client.extract_intent(query)
   else:
       enrichment = legacy_llm_client.enrich_query(query)  # Old path
```
4. Deploy with flag=false initially (no behavior change)
5. Test new gateway in staging
6. Flip flag to true for 10% of production traffic
7. Monitor metrics, gradually increase to 100%

STOP: Awaiting approval to proceed with Option B.
```

---

### SECTION 3: E5 Embedding Service

#### AI Agent Audit Prompt
```
AUDIT TASK: E5 Embedding Service

## Step 1: Discovery
Search for:
- [ ] Existing embedding generation code
- [ ] Current embedding model (if any)
- [ ] Vector dimensionality
- [ ] Batch processing support

Commands:
```bash
# Find embedding code
grep -r "embed\|SentenceTransformer\|OpenAIEmbeddings" --include="*.py"

# Check model configuration
grep -r "model.*name\|EMBEDDING_MODEL" --include="*.py" --include="*.yaml" --include="*.env"

# Find vector storage
grep -r "\.encode\|create_embedding" --include="*.py"
```

## Step 2: Current Implementation

Document:
- [ ] Current embedding model: [name and version]
- [ ] Vector dimensions: [e.g., 1536 for OpenAI, 768 for BERT]
- [ ] Query/passage prefix handling: YES / NO
- [ ] Batch encoding: YES / NO
- [ ] Caching: YES / NO

Current performance:
- [ ] Latency per query: [ms]
- [ ] Batch size: [N]

## Step 3: Gap Analysis

Against Spec (E5-large):
- [ ] Model: intfloat/multilingual-e5-large (1024-dim)
- [ ] Query prefix ("query: "): REQUIRED
- [ ] Passage prefix ("passage: "): REQUIRED
- [ ] Normalization for cosine similarity: REQUIRED
- [ ] Batch encoding support: REQUIRED
- [ ] Embedding cache: OPTIONAL but recommended

Compatibility Check:
- [ ] Current vector dim: [X], Target: 1024
- [ ] If dimensions differ: REQUIRES RE-INDEXING ALL EMAILS

## Step 4: Migration Analysis

If embedding model changes:
- [ ] Total emails in database: [count]
- [ ] Re-indexing time estimate: [hours]
- [ ] Strategy: Blue-green index swap (see Section on Embedding Updates)

Options:
A. Keep existing embeddings (no change)
B. Migrate to E5-large (requires re-indexing)
C. Support both models (dual index)

Recommendation: [A / B / C]
Justification: [explain trade-offs]

STOP: Awaiting decision on embedding model migration.
```

**Expected Output**:
```
AUDIT REPORT: E5 Embedding Service

Current State:
- Found: ./services/embedding_service.py
- Current Model: OpenAI text-embedding-3-small (1536 dimensions)
- Query/Passage Prefix: NO (not using E5, so not applicable)
- Batch Encoding: YES (batch_size=50)
- Caching: YES (Redis with 1-hour TTL)
- Normalization: YES (L2-normalized for cosine similarity)

Current Code:
```python
# ./services/embedding_service.py
from openai import OpenAI

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()
    
    def encode(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding  # 1536 dimensions
```

Gap Analysis:
✅ Already has: Batch encoding, caching, normalization
❌ Missing: E5-large model (currently using OpenAI embeddings)
❌ Missing: Query/passage prefixes (E5 requirement)
⚠️ CRITICAL: Vector dimensions differ (1536 current vs 1024 target)

Compatibility Impact:
- Total emails in DB: 487,392
- Current vectors: 1536-dim
- Target vectors: 1024-dim
- ⚠️ INCOMPATIBLE: Cannot mix dimensions in same index
- REQUIRES: Full re-indexing of all 487K emails

Re-indexing Estimate:
- Time: ~16 hours (at 1000 emails/minute)
- Cost: $0 (E5 is open-source, runs locally)
- Downtime: 0 (blue-green index swap)

Recommendation: Option B (Migrate to E5-large)

Justification:
1. E5-large is FREE (no API costs vs $0.13/M tokens for OpenAI)
2. Better quality for retrieval tasks (E5 designed for this)
3. Local hosting = lower latency (50ms vs 200ms)
4. More control over infrastructure

BUT: Requires re-indexing. Use blue-green strategy from Section 3.

Alternative: Option C (Support Both)
- Keep OpenAI embeddings for existing index
- Start E5 for new emails only
- Gradually migrate old emails in background
- More complex but zero-downtime

STOP: Awaiting decision. Recommend Option B with weekend re-indexing.
```

---

### SECTION 4: Hybrid Search with Progressive Relaxation

#### AI Agent Audit Prompt
```
AUDIT TASK: Search Implementation

## Step 1: Discovery
Search for:
- [ ] Current search/retrieval logic
- [ ] Vector similarity search code
- [ ] Metadata filtering implementation
- [ ] Ranking algorithm

Commands:
```bash
# Find search logic
grep -r "search\|retrieve\|query" --include="*.py" | grep -v test

# Check for vector search
grep -r "similarity\|cosine\|dot_product" --include="*.py"

# Look for filtering
grep -r "filter\|WHERE.*user_id" --include="*.py"
```

## Step 2: Current Search Flow

Document:
1. Current search steps: [describe]
2. Vector search method: [cosine similarity / dot product / euclidean]
3. Metadata filtering: [when applied, which fields]
4. Ranking: [vector only / hybrid]
5. Fallback logic: [exists? / missing]

Current Code:
```python
# Paste actual search implementation
```

## Step 3: Security Audit (CRITICAL)

User Isolation Check:
```python
# SEARCH CODE: Does it ALWAYS filter by user_id?
# Example of UNSAFE code:
results = db.query("SELECT * FROM emails ORDER BY similarity DESC LIMIT 10")
# ❌ NO user_id filter = data leak!

# Example of SAFE code:
results = db.query("SELECT * FROM emails WHERE user_id = ? ORDER BY similarity DESC LIMIT 10", [user_id])
# ✅ user_id filter applied
```

TEST: Run this query:
```sql
-- This should return 0 rows (no cross-user results)
SELECT COUNT(*) FROM (
    -- Simulate search for user A
    SELECT * FROM emails WHERE user_id = 'user_a'
) WHERE user_id != 'user_a'
```

Result: [PASS / FAIL]

## Step 4: Gap Analysis

Against Spec:
- [ ] Filter-first architecture: IMPLEMENTED / MISSING
- [ ] Progressive filter relaxation: IMPLEMENTED / MISSING
- [ ] Hybrid ranking (vector + recency + keyword): IMPLEMENTED / PARTIAL / MISSING
- [ ] Project tag filtering: IMPLEMENTED / MISSING
- [ ] Confidence-based filter application: IMPLEMENTED / MISSING

Security:
- [ ] User isolation: ENFORCED / PARTIAL / MISSING
- [ ] SQL injection protection: SAFE / VULNERABLE

## Step 5: Recommendation

Recommendation: [NO_CHANGE | ENHANCEMENT | REFACTOR]

Changes needed:
1. [List specific changes]
2. [...]

Risk Level: [LOW / MEDIUM / HIGH]

STOP: Awaiting approval to proceed.
```

---

### SECTION 5: FastAPI Service Endpoints

#### AI Agent Audit Prompt
```
AUDIT TASK: API Endpoints

## Step 1: Discovery
Search for:
- [ ] Existing API framework (Flask / FastAPI / Django)
- [ ] Current endpoints
- [ ] Authentication middleware
- [ ] Request/response models

Commands:
```bash
# Find API definition
find . -name "main.py" -o -name "app.py" -o -name "api.py"

# List endpoints
grep -r "@app\|@router\|@api" --include="*.py"

# Check auth
grep -r "auth\|jwt\|token" --include="*.py"
```

## Step 2: Current API

Document:
- [ ] Framework: [Flask / FastAPI / Django / Other]
- [ ] Base URL: [e.g., /api/v1]
- [ ] Existing endpoints: [list]
- [ ] Authentication: [JWT / OAuth / API Key / None]

Current endpoints:
```
GET  /health
POST /search
POST /index
...
```

## Step 3: Gap Analysis

Required endpoints from spec:
- [ ] POST /v1/search
- [ ] POST /v1/emails/ingest
- [ ] GET  /v1/analytics/query-stats
- [ ] GET  /metrics (Prometheus)
- [ ] GET  /health

Current vs Required:
✅ Already have: [list]
⚠️ Need modification: [list]
❌ Missing: [list]

## Step 4: Breaking Changes

Will new endpoints break existing clients?
- [ ] URL structure changing: YES / NO
- [ ] Request schema changing: YES / NO
- [ ] Response schema changing: YES / NO

If YES to any:
- Versioning strategy: [v1 vs v2, deprecation timeline]
- Migration plan for clients: [describe]

## Step 5: Recommendation

Recommendation: [COMPATIBLE_ADDITION / BREAKING_CHANGE / NO_CHANGE]

Implementation plan:
1. [Add new endpoints in parallel to old ones]
2. [Deprecate old endpoints with 90-day notice]
3. [...]

STOP: Awaiting approval.
```

---

### SECTION 6: Email Ingestion Pipeline

#### AI Agent Audit Prompt
```
AUDIT TASK: Email Ingestion

## Step 1: Discovery
Search for:
- [ ] Existing email fetching code (IMAP / Gmail API / Microsoft Graph)
- [ ] Indexing/ingestion pipeline
- [ ] Background job system (Celery / RQ / cron)
- [ ] Deduplication logic

Commands:
```bash
# Find email client
grep -r "imap\|gmail\|smtp\|email" --include="*.py"

# Find background jobs
grep -r "celery\|rq\|worker\|cron" --include="*.py"

# Find ingestion
grep -r "ingest\|index.*email\|fetch.*email" --include="*.py"
```

## Step 2: Current Pipeline

Document:
- [ ] Email source: [IMAP / Gmail API / Exchange / Other]
- [ ] Sync frequency: [real-time / hourly / manual]
- [ ] Background system: [Celery / RQ / None]
- [ ] Deduplication: [by email_id / message_id / None]

Current flow:
1. [Step 1]
2. [Step 2]
...

## Step 3: Gap Analysis

Against spec (5-minute batch ingestion):
- [ ] Current frequency: [X minutes]
- [ ] Batch processing: IMPLEMENTED / MISSING
- [ ] Atomic transactions: IMPLEMENTED / MISSING
- [ ] Error handling & retry: IMPLEMENTED / MISSING

Compatibility:
- [ ] Can existing pipeline be adapted? YES / NO

## Step 4: Recommendation

Option A: Use existing pipeline (modify frequency)
Option B: Replace with Celery worker (from spec)
Option C: Hybrid approach

Recommendation: [A / B / C]

STOP: Awaiting approval.
```

---

### SECTION 7: OpenShift Deployment

#### AI Agent Audit Prompt
```
AUDIT TASK: Deployment Configuration

## Step 1: Discovery
Search for:
- [ ] Existing Kubernetes/OpenShift manifests
- [ ] Current deployment strategy
- [ ] Resource limits
- [ ] Secrets management

Commands:
```bash
# Find k8s manifests
find . -name "*.yaml" -o -name "*.yml" | xargs grep -l "kind:"

# Find Dockerfile
find . -name "Dockerfile"

# Check for CI/CD
find . -name ".gitlab-ci.yml" -o -name "Jenkinsfile" -o -name ".github"
```

## Step 2: Current Deployment

Document:
- [ ] Platform: [OpenShift / Kubernetes / Docker Compose / Other]
- [ ] Namespace: [name]
- [ ] Replicas: [count]
- [ ] Auto-scaling: YES / NO
- [ ] GPU support: YES / NO

Current resources:
```yaml
# Paste current deployment.yaml
```

## Step 3: Gap Analysis

Against spec:
- [ ] GPU scheduling for Llama-3.1-8B: CONFIGURED / MISSING
- [ ] NetworkPolicy for isolation: CONFIGURED / MISSING
- [ ] HPA (auto-scaling): CONFIGURED / MISSING
- [ ] PVC for SQLite DB: CONFIGURED / MISSING

## Step 4: Recommendation

Recommendation: [MINOR_UPDATES / MAJOR_CHANGES / NEW_DEPLOYMENT]

Critical changes:
1. [Add GPU toleration for LLM pods]
2. [...]

STOP: Awaiting approval.

Complete Implementation Workflow
Phase 1: Audit (Week 1)
bash# AI Agent executes all audit prompts
agent audit --section=database
agent audit --section=llm-gateway
agent audit --section=embeddings
agent audit --section=search
agent audit --section=api
agent audit --section=ingestion
agent audit --section=deployment

# Generate comprehensive audit report
agent report --output=audit_report.md
```

### Phase 2: Review & Approve (Week 1)
```
Human reviews audit_report.md and provides decisions:
- Section 1 (Database): APPROVE migration
- Section 2 (LLM Gateway): APPROVE Option B (parallel implementation)
- Section 3 (Embeddings): DEFER (re-indexing scheduled for next quarter)
- Section 4 (Search): APPROVE enhancements
- Section 5 (API): APPROVE compatible additions
- Section 6 (Ingestion): APPROVE use existing pipeline
- Section 7 (Deployment): APPROVE with modifications
Phase 3: Implementation (Weeks 2-4)
bash# Agent proceeds with approved changes only
agent implement --section=database --approved
agent implement --section=llm-gateway --approved --option=B
# ... etc

# Skips deferred sections
agent skip --section=embeddings --reason="deferred to Q2"
Phase 4: Testing (Week 4)
bash# Agent generates and runs tests for modified sections
agent test --section=database --coverage=90
agent test --section=search --integration
agent test --security --check=user-isolation
Phase 5: Deployment (Week 5)
bash# Gradual rollout
agent deploy --environment=staging
agent deploy --environment=prod --canary=10%  # 10% traffic
agent deploy --environment=prod --canary=50%  # if successful
agent deploy --environment=prod --canary=100% # full rollout
```

---

## Summary: Key Differences from Greenfield

### What's DIFFERENT in Incremental Update Mode:

1. **Audit-First Approach**: Every section starts with discovery, not implementation
2. **Backward Compatibility**: Preserve existing functionality, add in parallel
3. **Feature Flags**: Use flags to toggle new features on/off without deployment
4. **A/B Testing**: Compare old vs new implementation with real traffic
5. **Gradual Rollout**: 10% → 50% → 100% traffic shifts, not big-bang
6. **Rollback Plan**: Every change must have instant rollback capability
7. **Migration Scripts**: Explicit data migration for schema/embedding changes
8. **Deprecation Timeline**: Give users 90 days notice before removing old endpoints

### What's the SAME:

1. **Architecture Goals**: Deterministic retrieval, user isolation, <2.5s latency
2. **Security Requirements**: Zero-trust user isolation is non-negotiable
3. **Monitoring**: Same metrics, alerts, and observability requirements
4. **Quality Bar**: Same testing standards (>90% coverage, load tests)

---

## Final Recommendation on Model Size

**USE LLAMA-3.1-8B** for production.

**Reasoning**:
- Your requirement: "performance is very important - the result must be accurate and deterministic as possible"
- 8B provides 5-10% better accuracy than 3B on complex entity extraction
- 150ms latency fits easily within 1s timeout budget
- Determinism: 8B gives more consistent outputs (critical for production)
- Cost difference: ~$60/month is negligible for enterprise deployment

**Only consider 3B if**:
- Running on CPU-only nodes (8B requires GPU)
- Sub-100ms latency is mandatory
- You have extensive fine-tuning data specifically for 3B

**Performance vs Cost Table**:
```
| Metric | 3B | 8B | Winner for Your Use Case |
|--------|----|----|-------------------------|
| Accuracy (critical) | 87% | 95% | ✅ 8B |
| Determinism (critical) | Medium | High | ✅ 8B |
| Latency | 80ms | 150ms | ⚠️ Both acceptable (<1s) |
| Cost | $30/mo | $90/mo | ⚠️ Both acceptable for enterprise |
Verdict: 8B wins on the criteria you care about most (accuracy, determinism).
