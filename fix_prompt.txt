You are fixing a token truncation bug in an MCP email tool.

Follow these steps IN ORDER. After each step, 
stop and confirm the output before proceeding.

STEP 1 — Read these files and report current line counts 
and function signatures only:
- email_tool_service.py (find format_email_to_markdown)
- app/router/email_mcp.py (find get_emails)

STEP 2 — Add triage mode to format_email_to_markdown.
Target: <150 chars per email. Show me the diff only.

STEP 3 — Add truncation warning to get_emails router.
Inject warning key into response dict when 
tokens_est > 5000. Show diff only.

STEP 4 — Add intent detection to route triage vs full mode.
Keyword signals: "urgent", "needs action", "any...soon".
Show diff only.

STEP 5 — Run the original failing query and report 
estimated token count from logs.

Do not write code until you have confirmed 
the file contents in Step 1.


You are a Principal Software Engineer. Do not write 
any code until Step 3.

CONTEXT:
The get_assist tool returns well-formatted markdown.
But the MCP client prepends the model's spoken text 
directly to the tool result string with no separator,
producing: "I'll get you a summary.## Catch-Up Summary"

The desired output is ONLY the tool result — no model 
preamble, no concatenation artifact.

STEP 1 — DIAGNOSE (read only, no edits)
Find and read these three things:
a) The system prompt or tool description for get_assist
   in email_mcp.py or wherever tools are registered
b) The exact return statement in get_assist / 
   catchup_service.py that builds the final string
c) How the MCP client assembles the final response
   (look for where tool result + model text join)
Report what you find. Stop.

STEP 2 — PROPOSE (no edits yet)
Based on Step 1, propose the minimal fix.
The correct fix is ONE of:
- Tool description instructs model to return 
  tool result only, no spoken preamble
- System prompt sets direct=True or equivalent
  to suppress model wrapping
- Response assembly changed to tool-result-only mode
Tell me which applies and show the exact line 
you will change. Stop.

STEP 3 — IMPLEMENT
Make only the change agreed in Step 2.
Show the diff. No other files touched.

STEP 4 — VERIFY
Rerun: "Hi catch me up last week and today"
Confirm the output starts directly with 
"# Catch Me Up" or the first section heading.
No introductory sentence. Report token count 
from logs.



So here's the step-by-step prompt template you can use, designed to always ground the diagram in production code first:

🔐 Security Cloud Architecture — Prompt Template
Phase 1: Ingestion Pipeline
Read the production code for the ingestion service.
Identify:
1. The exact Cohere Embed v4 API call — input format, batch size, model string
2. How embeddings are stored in SQLite — schema, table names, column types
3. The AES encryption implementation — which library, key size, IV handling, 
   whether encryption is per-file or per-chunk
4. The S3 upload flow — SDK used, bucket structure, metadata attached, 
   whether the encrypted file or raw file is uploaded
5. Any IAM roles, KMS keys, or S3 bucket policies involved

Then draw a diagram showing:
[User/File Source] → [AES Encrypt] → [Cohere Embed v4] → [SQLite] → [S3]
Label each arrow with the protocol, auth method, and data format in transit.

===========
Phase 2: Sync Service
Read the production code for the sync service.
Identify:
1. The trigger mechanism — cron, event-driven, webhook?
2. How it authenticates to S3 — IAM role, access key, IRSA?
3. The exact path it writes to on the OCP PersistentVolume
4. Whether it decrypts the file before writing, or writes encrypted
5. Any checksum/integrity verification after download
6. How the PV is mounted — StorageClass, access mode (RWO/RWX?)

Then draw a diagram showing:
[S3] → [Sync Service] → [OCP PV]
Label the OCP namespace, the PVC name if visible, and the mount path.

===========
Phase 3: RAG + MCP Pipeline

Read the production code for the RAG pipeline and MCP server.
Identify each of the 6 stages explicitly — do not infer, read the code:
Stage 1: Query intake — format, auth, rate limiting?
Stage 2: [identify from code]
Stage 3: [identify from code] — where does hydration occur?
Stage 4: DNS reranking — which reranker, what's the scoring mechanism?
Stage 5: [identify from code]
Stage 6: Response assembly — how is context injected into the LLM prompt?

Also identify:
- How the MCP server reads the SQLite db file from the OCP PV
- The MCP protocol version and transport (stdio, SSE, HTTP?)
- Any vector similarity search — library, distance metric, top-k value
- Authentication between the MCP client and server

Then draw a diagram showing all 6 stages with data flowing left to right,
with the OCP PV as the shared storage dependency.

============

Phase 4: Unified Diagram

Combine all three diagrams into one unified architecture diagram.
The three subsystems share these components:
- S3 (ingestion writes, sync reads)
- OCP PV (sync writes, RAG/MCP reads)
- SQLite db file (embedded at ingestion, queried at RAG time)

Draw boundaries showing:
- Trust zones (internet-facing vs. internal vs. OCP cluster)
- Encryption boundaries (what is encrypted at rest, in transit)
- Auth boundaries (where IAM, mTLS, or API keys are verified)

Use the actual component names from the codebase, not generic labels.

Ground Rules (add these to every prompt)
Rules:
- Read production code files, not README or docs
- If a detail is ambiguous in the code, say so — don't assume
- Flag any security gaps you observe (e.g., unencrypted path, 
  missing auth, hardcoded secrets)
- Use actual variable names, function names, and config keys 
  where they clarify the architecture



=============
For any service, run this AFTER the first draft:




You have just produced a first draft diagram of [SERVICE NAME].

Before I accept it, I need you to do two things:

---

PART 1 — AUDIENCE FILTER

Re-examine every element in this diagram through the eyes of 
an AI Security Team reviewing this for the first time.

They are NOT asking:
- What are the table column names?
- What is the method signature?
- What is the cache TTL?
- What does each function do internally?

They ARE asking:
- What components exist in this system?
- What are the trust boundaries? 
  (Where does data cross a network, a service, or an auth boundary?)
- Where is data stored, and is it encrypted at rest?
- Where is data in transit, and is it encrypted in transit?
- Who or what authenticates to what? 
  (IAM role, API key, mTLS, service account?)
- What are the external dependencies? 
  (S3, Cohere API, OCP cluster, etc.)
- Where could an attacker move laterally if one component is compromised?
- What secrets or credentials are involved and where do they live?

Remove any element that answers the first list but not the second.
Keep any element that helps a security reviewer assess risk or trust.

---

PART 2 — FLOW DIAGRAM vs ARCHITECTURE DIAGRAM

Your current output reads as a flow diagram. 
Convert it to an architecture diagram using these rules:

REMOVE:
- Step-by-step sequence numbering (1→2→3)
- Method names and function calls
- Internal implementation details (table schemas, cache keys, batch sizes)
- Anything that requires reading the code to understand

KEEP AND EMPHASISE:
- Named components (services, databases, storage, external APIs)
- The environment each component lives in 
  (OCP cluster, AWS, external SaaS, local process)
- Data classification on connections 
  (encrypted / unencrypted, what type of data flows: embeddings, 
  raw email, metadata, query, response)
- Auth mechanisms on connections 
  (IAM, API key, service account, none — "none" must be flagged)
- Trust zone boundaries drawn as visual groupings:
  → Internet-facing zone
  → Internal cluster zone  
  → Persistent storage zone
  → External services zone

ADD:
- A legend explaining:
  → Solid line = authenticated connection
  → Dashed line = unauthenticated or internal-only connection
  → Lock icon or label = encrypted at rest
  → Shield icon or label = encrypted in transit
- A one-line data sensitivity label per component 
  (e.g. "contains PII", "embeddings only — no raw content", 
  "ephemeral — no persistence")

---

PART 3 — FINAL CHECK

Before outputting the revised diagram, answer these 5 questions 
as the security reviewer would:

1. Can I identify every place raw email content is stored or transmitted?
2. Can I identify every external service this system calls?
3. Can I identify every authentication boundary?
4. Are there any connections with no auth or no encryption shown?
5. If one component were compromised, what's the blast radius?

If any answer reveals a gap in the diagram, add what's missing.
Then produce the revised architecture diagram.

Quick Reference — What to Strip vs Keep
Strip from flow diagramKeep for security architectureMethod namesComponent namesTable column namesDatabase type + encryption statusCache TTL valuesWhere credentials are storedBatch sizesTrust zone boundariesStep numbersAuth mechanism per connectionInternal logicData classification per flow
