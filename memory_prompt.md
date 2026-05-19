# Agent prompt: implement PG memory layer (MongoDB + SQLite)

---

## Your role

You are a senior Python engineer implementing a memory layer for a Personal Grounding (PG) AI tool. PG is an MCP-based RAG system that ingests personal data (emails via EWS, calendar events, documents), encrypts and uploads to S3, and retrieves via a 6-stage search pipeline. Your task is to implement the memory layer end-to-end: schema, storage, retrieval integration, ingestion hooks, and consolidation agents.

**Accuracy is the north star.** Every architectural decision must be justified against retrieval quality first, then latency, then operational simplicity.

---

## System context — read this before touching any code

### Existing 6-stage retrieval pipeline (do not break these)
1. **Embedding stage** — query embedded with Cohere embed v4
2. **Dense search stage** — ANN lookup on SQLite vec tables (sqlite-vec or similar)
3. **Metadata/lexical search stage** — SQL scoring on metadata tables (body excluded)
4. **RRF fusion stage** — Reciprocal Rank Fusion at k=60 merging stages 2 and 3
5. **Hydration stage** — full document bodies fetched for top-N candidates
6. **Reranking stage** — final relevance reranking of hydrated results

### Existing ingestion pipeline
- Source: EWS (Exchange Web Services) for emails and calendar events
- Preprocessing: sanitize body, filter secrets, classify external domains
- Embedding: Cohere embed v4 (1024-dim, must remain consistent across all memory)
- Storage: encrypt → upload to S3; local SQLite for vec and metadata tables

### Storage available (on-prem, no cloud exposure)
- **SQLite** — local, already used for vec tables and metadata. Fast ANN index.
- **MongoDB** (on-prem Enterprise Server) — document store. New for memory layer.

### Embedding constraint
**All embeddings — documents, emails, and memory chunks — must use Cohere embed v4.**
Never introduce a second embedding model. Mixed embedding spaces silently destroy RRF fusion accuracy.

---

## What you are building

### 1. Memory layer architecture

**Design principle:** MongoDB is the canonical source of truth. SQLite is a rebuildable shadow index.

- MongoDB stores full memory documents (episodic logs, identity profile)
- SQLite stores Cohere embeddings of memory chunks with a `mongo_id` foreign key
- On read: SQLite ANN → get `mongo_id` refs → hydrate from MongoDB (same pattern as existing hydration stage)
- On rebuild: re-embed all MongoDB docs, repopulate SQLite vec table. No data loss possible.

**Memory channel integration point:** Inject memory as a **3rd retrieval channel into RRF fusion (stage 4)**. Do not inject after reranking — memory must compete fairly with dense and metadata results so the highest-accuracy signal wins regardless of source. The merged+reranked list then goes through the existing reranker with full context.

**Phase 1 scope (this task):** Episodic memory + Identity/profile memory only.
**Phase 2 scope (future task, do not implement now):** Semantic memory + Procedural memory.

---

### 2. MongoDB schema

#### Collection: `memory_episodic`
One document per discrete interaction or event. Raw record — never summarize or destructively transform.

```python
{
    "_id": ObjectId,
    "user_id": str,                    # scopes all queries — mandatory on every doc
    "session_id": str,                 # groups related interactions
    "timestamp": datetime,             # UTC, when the event occurred
    "ingested_at": datetime,           # UTC, when PG processed it
    "source": str,                     # "email" | "calendar" | "query" | "manual"
    "source_ref": str | None,          # e.g. EWS item_id, S3 key — links back to raw doc
    "content": str,                    # the raw text of the interaction/event
    "summary": str | None,             # short agent-written summary (populated async)
    "entities": list[str],             # extracted names, projects, orgs
    "importance_score": float,         # 0.0–1.0, set at write time by importance classifier
    "tags": list[str],                 # e.g. ["project:x", "person:john", "decision"]
    "expires_at": datetime | None,     # None = permanent; set for short-lived episodic logs
    "sqlite_synced": bool,             # True once embedding written to SQLite vec table
    "chunk_ids": list[str]             # SQLite rowids for ANN lookup
}
```

#### Collection: `memory_identity`
One document per user. Single living document, updated in place. This is the always-loaded "core memory" — user preferences, communication style, relationship graph.

```python
{
    "_id": ObjectId,
    "user_id": str,                    # unique index — one doc per user
    "updated_at": datetime,
    "display_name": str,
    "communication_style": str,        # e.g. "direct, prefers bullet summaries"
    "writing_style": str | None,
    "preferences": dict,               # {"meeting_type": "async", "summary_format": "bullets", ...}
    "active_projects": list[{
        "project_id": str,
        "name": str,
        "role": str,
        "status": str                  # "active" | "paused" | "completed"
    }],
    "relationships": list[{
        "name": str,
        "email": str | None,
        "context": str,                # "direct report", "client", "exec sponsor"
        "last_interaction": datetime | None
    }],
    "known_facts": list[str],          # freeform distilled facts: ["prefers morning meetings", ...]
    "sqlite_synced": bool
}
```

#### MongoDB indexes to create
```python
# memory_episodic
db.memory_episodic.create_index([("user_id", 1), ("timestamp", -1)])
db.memory_episodic.create_index([("user_id", 1), ("source", 1)])
db.memory_episodic.create_index([("user_id", 1), ("tags", 1)])
db.memory_episodic.create_index([("sqlite_synced", 1)])   # for sync worker
db.memory_episodic.create_index([("expires_at", 1)], expireAfterSeconds=0)  # TTL

# memory_identity
db.memory_identity.create_index([("user_id", 1)], unique=True)
```

---

### 3. SQLite schema additions

Add these tables to the existing SQLite database. Do not modify existing vec or metadata tables.

```sql
-- Memory chunk embeddings (ANN index for memory retrieval)
CREATE TABLE IF NOT EXISTS memory_vec (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    mongo_id    TEXT NOT NULL,          -- references MongoDB _id as string
    mongo_coll  TEXT NOT NULL,          -- "memory_episodic" | "memory_identity"
    user_id     TEXT NOT NULL,
    chunk_text  TEXT NOT NULL,          -- the text that was embedded (for debugging)
    chunk_index INTEGER NOT NULL DEFAULT 0,  -- if doc split into chunks
    embedding   BLOB NOT NULL,          -- Cohere embed v4, 1024-dim float32, stored as bytes
    created_at  TEXT NOT NULL           -- ISO8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_memory_vec_user ON memory_vec(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_vec_mongo ON memory_vec(mongo_id);
```

> Use the same ANN method already in use for existing vec tables (sqlite-vec, or manual cosine if no extension). Do not introduce a new vector library.

---

### 4. Memory service — `memory_service.py`

Create `memory_service.py` as a standalone Python module. It must be importable by the MCP server and the ingestion pipeline independently.

```python
"""
PG Memory Service
Owns all reads and writes to the memory layer (MongoDB + SQLite vec).
Called by: MCP retrieval pipeline, ingestion pipeline, consolidation agent.
"""
```

#### Required public interface

```python
class MemoryService:

    def __init__(self, mongo_client, sqlite_conn, cohere_client, user_id: str):
        ...

    # --- Write path ---

    def write_episodic(self, content: str, source: str, source_ref: str | None = None,
                       session_id: str | None = None, tags: list[str] = [],
                       importance_score: float | None = None) -> str:
        """
        Write a raw episodic memory. Steps:
        1. Compute importance_score if not provided (simple heuristic: len/keywords ok for now)
        2. Insert document into memory_episodic (sqlite_synced=False)
        3. Embed content with Cohere embed v4
        4. Insert embedding into SQLite memory_vec with mongo_id reference
        5. Update memory_episodic: sqlite_synced=True, chunk_ids=[rowid]
        Returns: mongo_id as string
        """

    def update_identity(self, patch: dict) -> None:
        """
        Upsert the identity document for this user.
        patch is a partial dict — merge into existing doc, do not replace.
        Re-embed the serialized identity text and update SQLite memory_vec.
        Identity is treated as a single chunk (no splitting).
        """

    # --- Read path ---

    def retrieve(self, query_embedding: list[float], top_k: int = 10,
                 source_filter: str | None = None) -> list[dict]:
        """
        ANN lookup in SQLite memory_vec for this user_id.
        Returns top_k candidates: [{"mongo_id": str, "mongo_coll": str, "score": float, "chunk_text": str}]
        Scoped strictly to user_id — never return another user's memory.
        """

    def hydrate(self, candidates: list[dict]) -> list[dict]:
        """
        Fetch full documents from MongoDB for a list of candidates.
        Returns candidates with "document" key added.
        Candidates referencing non-existent mongo_ids are silently dropped.
        """

    def get_identity(self) -> dict | None:
        """Return the identity document for this user, or None if not yet created."""

    # --- Maintenance ---

    def rebuild_sqlite_index(self) -> int:
        """
        Re-embed all MongoDB memory docs for this user and repopulate memory_vec.
        Called when SQLite is rebuilt from scratch. Returns count of records written.
        """
```

#### Implementation notes
- All MongoDB queries **must** include `user_id` as a filter. No exceptions. Memory is strictly user-scoped.
- Use `pymongo` for MongoDB. Use the same SQLite connection pattern as the rest of the codebase.
- Cohere embed v4 call: `input_type="search_document"` for writes, `input_type="search_query"` for reads. This matters for retrieval accuracy.
- Store embeddings as `bytes` in SQLite: `numpy.array(embedding, dtype=numpy.float32).tobytes()`. Deserialize with `numpy.frombuffer(blob, dtype=numpy.float32)`.
- Cosine similarity for ANN: `score = dot(q, d) / (norm(q) * norm(d))`. Return top_k by score descending.
- Do not chunk episodic documents for Phase 1. One doc = one embedding. Add chunking in Phase 2 when semantic memory requires it.

---

### 5. RRF fusion — modify stage 4

Find the existing RRF fusion function in the retrieval pipeline. Extend it to accept a third channel.

**Current signature (approximate):**
```python
def rrf_fuse(dense_results: list[dict], metadata_results: list[dict], k: int = 60) -> list[dict]:
```

**New signature:**
```python
def rrf_fuse(
    dense_results: list[dict],
    metadata_results: list[dict],
    memory_results: list[dict] | None = None,
    k: int = 60
) -> list[dict]:
```

**Rules:**
- `memory_results=None` must be backward-compatible — existing calls without memory must work unchanged.
- Each result list must have a unique `id` field. Memory results use `mongo_id` as id; map it to a namespaced key (`"mem::{mongo_id}"`) so it never collides with document ids from the other channels.
- RRF formula is unchanged: `score(d) = sum(1 / (k + rank(d, channel)))` across all channels where `d` appears.
- A result appearing in only one channel still gets a valid RRF score — do not filter out single-channel results.
- After fusion, the hydration stage (step 5) must handle both document hydration (existing) and memory hydration (new `MemoryService.hydrate()`). Detect by id prefix: `"mem::"` → memory hydration path.

---

### 6. Email ingestion service — modifications

Locate the existing EWS ingestion pipeline. Add the following **after** the existing preprocessing step and **before** the encrypt+upload step. Do not modify the existing S3 upload or existing SQLite write logic.

#### Hook to add: `_write_episodic_memory(item, preprocessed_body)`

```python
def _write_episodic_memory(item, preprocessed_body: str, memory_service: MemoryService):
    """
    Called for every successfully preprocessed email/calendar item.
    Writes a lightweight episodic memory — NOT the full body.
    Content written to memory is the preprocessed_body (already sanitized,
    secrets filtered). Do not embed or store the raw EWS body.
    """
    source = "email" if is_email(item) else "calendar"
    source_ref = item.id  # EWS item id — links back to full doc in S3

    # Extract lightweight tags from item metadata (not body)
    tags = []
    if hasattr(item, 'sender') and item.sender:
        tags.append(f"person:{item.sender.email_address}")
    if hasattr(item, 'subject'):
        tags.append(f"subject:{item.subject[:40]}")

    memory_service.write_episodic(
        content=preprocessed_body,
        source=source,
        source_ref=source_ref,
        tags=tags
    )
```

**Important:** `MemoryService` must be instantiated once per ingestion run (not per item) and passed through. Do not instantiate inside the per-item loop — that would create a new MongoDB connection per email.

#### Identity update hook

After processing a batch of emails, call:
```python
memory_service.update_identity({
    "relationships": extract_senders(processed_items)  # list of {name, email, last_interaction}
})
```

Implement `extract_senders()` to deduplicate senders from the batch and return relationship patches. Merge strategy: if email already exists in identity.relationships, update `last_interaction` only.

---

### 7. Configuration

Add to the existing config file (wherever env vars or config dict is defined):

```python
# MongoDB memory layer
MONGODB_URI = os.getenv("MONGODB_URI")          # e.g. "mongodb://localhost:27017"
MONGODB_DB  = os.getenv("MONGODB_DB", "pg_memory")

# Memory retrieval
MEMORY_TOP_K        = int(os.getenv("MEMORY_TOP_K", "10"))
MEMORY_RRF_WEIGHT   = float(os.getenv("MEMORY_RRF_WEIGHT", "1.0"))  # future: tune channel weight
MEMORY_ENABLED      = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
```

---

### 8. Consolidation agent (stub — wire up, don't fully implement)

Create `memory_consolidation_agent.py` as a schedulable script. For Phase 1, implement only the scaffolding and the `flag_for_consolidation` logic. Full consolidation (episodic → semantic distillation) is Phase 2.

```python
"""
Memory Consolidation Agent
Scheduled nightly. Phase 1: marks stale episodic docs. Phase 2 will distill to semantic.
Run as: python memory_consolidation_agent.py --user-id <uid>
"""

def run(user_id: str, memory_service: MemoryService, dry_run: bool = False):
    """
    Phase 1 behaviour:
    1. Find episodic docs older than 30 days with importance_score < 0.3
    2. Set expires_at = now + 7 days (TTL index will clean them up)
    3. Log count of docs flagged
    4. Log count of docs with sqlite_synced=False (sync anomaly alert)
    Phase 2 hook (do not implement, leave TODO):
    # TODO: distill high-importance episodic clusters into semantic memory docs
    """
```

---

### 9. Validation checklist — verify before marking complete

#### Correctness
- [ ] `memory_vec` records are always created after MongoDB insert, never before
- [ ] Every MongoDB query includes `user_id` filter — grep the codebase to confirm
- [ ] RRF fusion with `memory_results=None` produces identical output to the original function (write a unit test)
- [ ] Cohere embed v4 is called with `input_type="search_document"` on write and `input_type="search_query"` on read
- [ ] Identity upsert uses `$set` (merge), never full document replace

#### Resilience
- [ ] If MongoDB is unreachable at ingestion time, the email ingestion pipeline continues (memory write failure is non-fatal — log and skip, do not raise)
- [ ] If memory_vec SQLite write fails after MongoDB write, `sqlite_synced` remains False — the rebuild script will recover it
- [ ] `retrieve()` returns empty list (not exception) if memory_vec has no rows for user

#### Security
- [ ] No raw EWS body is stored in MongoDB — only preprocessed_body (already sanitized upstream)
- [ ] `user_id` is always sourced from the authenticated session, never from request payload
- [ ] No PII logged at DEBUG level in memory_service.py

#### Backward compatibility
- [ ] Existing retrieval pipeline with `MEMORY_ENABLED=false` runs unchanged
- [ ] Existing ingestion pipeline with no MongoDB URI configured skips memory hooks gracefully
- [ ] All existing SQLite tables and indexes are untouched

---

### 10. Files to create or modify

| File | Action | Notes |
|------|--------|-------|
| `memory_service.py` | Create | Core memory read/write service |
| `memory_consolidation_agent.py` | Create | Phase 1 stub only |
| `retrieval/pipeline.py` (or equivalent) | Modify | Add memory channel to RRF stage 4 + memory hydration in stage 5 |
| `ingestion/ews_ingestion.py` (or equivalent) | Modify | Add `_write_episodic_memory` and `extract_senders` hooks |
| `config.py` (or equivalent) | Modify | Add MongoDB and memory config vars |
| `schema/sqlite_migrations.sql` (or create) | Create | `memory_vec` table DDL |
| `tests/test_memory_service.py` | Create | Unit tests for RRF backward compat + user_id scoping |

---

## What NOT to do

- Do not implement semantic or procedural memory (Phase 2)
- Do not introduce chunking — one episodic doc = one embedding
- Do not introduce a second embedding model or a dedicated vector database
- Do not modify existing SQLite vec or metadata tables
- Do not make memory write failures fatal to the ingestion pipeline
- Do not store raw email bodies in MongoDB — only preprocessed content
- Do not hardcode user_id anywhere — always pass it through from the calling context



You are improving an existing MCP tool implementation for a RAG service (PG MCP).

## Goal
Fix four specific failure modes observed when smaller models (Haiku, Sonnet, 
Cohere) use these tools:
1. Date range confusion with relative phrases ("this past week", "last week")
2. Incorrect tool/parameter selection on complex queries  
3. Timezone resolution failure
4. Arithmetic/logic errors on aggregate queries (e.g. "busiest day")

## Constraints — read these first
- DO NOT add new tools. Improve existing tool and parameter descriptions only.
- DO NOT change function signatures or return shapes.
- DO NOT refactor working logic. Touch only docstrings, descriptions, enum 
  values, and server-side computation where explicitly noted below.
- Each change must be independently reversible.
- If a fix requires a new parameter, it must be optional with a sensible default.

## Specific fixes — do exactly these, nothing more
1. **Date params**: Add inline examples for relative date phrases 
   (e.g. `"this past week" means the 7 days ending yesterday`). 
   Include an explicit note that "past week ≠ last calendar week".

2. **Parameter descriptions**: Expand descriptions and add enum hints where 
   selection is ambiguous. Mirror the pattern already used in the clearest 
   existing tool.

3. **Timezone param**: Add an optional `timezone` parameter (default: "UTC") 
   with a one-line description. Do not infer timezone from context.

4. **Busiest-day / aggregate logic**: Move computation server-side. 
   Return the computed result, not raw data for the model to calculate.

## Acceptance bar
- A smaller model (non-Sonnet) calling these tools should now pick the right 
  tool and parameters on the first try for the above scenarios.
- No change to response contracts that would break existing callers.
- No new dependencies.

## Output format
For each fix: show the before/after diff and a one-line rationale. 
Flag anything that feels outside scope rather than implementing it.
