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




========================

🐛 Prompt Template — RAG/MCP Debug & Fix

You are a senior RAG pipeline engineer and MCP integration specialist.
You debug with precision — you read the production code first, 
form a hypothesis second, and only then propose a fix.
You do not guess. You trace.

---

## THE BUG

My RAG and MCP pipeline has a scope bug:

When a user asks about their emails, the pipeline appears to be 
scoping its retrieval to the inbox only — or to recently received emails only.

This means:
- Emails in non-default folders (Sent, Drafts, Deleted, custom folders) 
  are not being surfaced even if they were ingested
- Emails that are not recent are being silently dropped rather than 
  returned with a recency disclaimer
- The pipeline is interpreting "no recent inbox emails" as 
  "user has no emails" — which is incorrect

The correct behaviour should be:

RULE 1 — SCOPE: If a DB file exists on the PV, ALL ingested emails 
are searchable regardless of folder, direction (sent/received), 
or age. The DB is the source of truth, not the folder label.

RULE 2 — RECENCY: If the user's query implies recency 
(e.g. "did I get any emails today", "recent emails") and no 
recent emails are found, the pipeline should still search the full DB 
and respond with something like:
"I didn't find any emails from [today / this week], but here's 
what I found that may be relevant — these are from [actual date range]."

RULE 3 — NO SILENT FAILURES: The pipeline must never return 
"no results" without first confirming it searched the full DB scope.
If results are empty after a full search, say so explicitly with the 
scope that was searched.

---

## YOUR DEBUGGING PROCESS

Follow these steps in order. Do not skip ahead.

### STEP 1 — Read the retrieval/query stage of the RAG pipeline
Identify:
- Where the query is constructed before hitting the vector store or SQLite DB
- Whether any folder filter, label filter, or date filter is being 
  applied at query time
- Whether "inbox" or "received" is hardcoded or inferred anywhere 
  in the query construction logic
- Whether the retrieval is scoped by a metadata field 
  (e.g. folder="INBOX") that wasn't intended to be a hard filter

### STEP 2 — Read the metadata schema in the DB
Identify:
- What metadata fields are stored per email chunk 
  (folder, date, direction, sender, recipient, subject, etc.)
- Whether folder is stored as a filterable field
- Whether there is a default filter being applied that excludes 
  non-inbox folders

### STEP 3 — Read the MCP tool definition for email search
Identify:
- What parameters the MCP tool exposes to the LLM
- Whether the tool description or parameter schema implies 
  inbox-only or received-only scope
- Whether the LLM is inferring a filter from the tool's 
  name or description (e.g. a tool named "search_inbox" 
  will always be called with inbox intent)

### STEP 4 — Trace a failing query end to end
Take this example query: "Show me emails I sent last month"
Trace it through every stage of the pipeline:
1. MCP tool selection — which tool is called, with what parameters?
2. Query construction — what goes into the vector search or SQL query?
3. Retrieval — what filter is applied? What scope is searched?
4. Reranking — is any folder or recency filter applied here?
5. Response assembly — is the LLM given the full result set 
   or a pre-filtered one?

At each stage, identify whether a scope narrowing occurs 
that shouldn't be there.

### STEP 5 — Identify the root cause
State clearly:
- Which stage introduces the incorrect scope constraint
- Whether it is a hardcoded filter, an inferred filter, 
  a metadata schema issue, or an MCP tool description problem
- Whether the bug affects retrieval, reranking, or response generation

---

## YOUR FIX

Once root cause is confirmed, propose a fix for each layer affected:

### FIX A — Retrieval layer
If a folder or recency filter is being applied incorrectly:
- Show the exact code change to remove or conditionalize the filter
- The default retrieval scope must be ALL ingested emails in the DB
- Folder and date filters should only be applied when the user 
  explicitly requests them

### FIX B — MCP tool definition
If the tool name, description, or parameter schema is causing 
the LLM to infer inbox-only scope:
- Rewrite the tool description to make clear it searches 
  ALL ingested email folders
- Add an explicit parameter: folder (optional, default: all)
- Add an explicit parameter: date_range (optional, default: all time)

### FIX C — Response generation
Add a recency disclaimer pattern to the response assembly stage:
- If query implies recency AND no results match the recency window:
  → Do not return empty
  → Search full DB without date filter
  → Return results with disclaimer: 
    "No emails found from [requested period]. 
     Here are the closest matches from your ingested emails, 
     dated [actual date range]."
- If full DB search also returns empty:
  → Return: "I searched all your ingested emails and found 
     nothing matching [query]. If you expected results, 
     confirm the relevant folders were ingested."

### FIX D — Regression test cases
Write test cases to confirm the fix holds:

Test 1: Query against a Sent folder email → must return result
Test 2: Query against a Deleted folder email → must return result  
Test 3: Query for "emails from today" when all emails are 6 months old 
        → must return closest results with recency disclaimer
Test 4: Query for "recent emails" with no DB file on PV 
        → must return "no ingested emails found", not "no emails"
Test 5: Query using a custom folder name the user created 
        → must return result if that folder was ingested

---

## RULES

- Read production code at every step. Do not assume any behaviour.
- If you cannot find where a filter is applied, say so and 
  suggest where to add instrumentation/logging to find it.
- Never propose a fix without first confirming the root cause in code.
- Flag any secondary bugs you find while tracing — do not ignore them.
- The DB file on the PV is the source of truth. 
  If it exists and contains emails, they must be searchable. Full stop.


=============================

🎨 Prompt Template — Diagram UX & Legibility Fix

You have produced a security architecture diagram that is 
structurally correct but visually broken.

Do NOT change any of the following:
- Component names
- Trust zone boundaries and their labels
- Security annotations (encryption, auth mechanisms, data classification)
- The legend content
- The data flow summary at the bottom
- The blast radius notes

Your job is to fix ONLY the visual presentation layer.

---

## ARROW RULES

Current problem: arrows are crossing, overlapping, and creating visual noise.

Fix using these rules:

1. DIRECTIONALITY — all arrows must flow in one primary direction:
   Left to right for the main data flow.
   Top to bottom for hierarchical relationships within a zone.
   Never diagonal unless absolutely unavoidable.

2. NO CROSSING ARROWS — if two arrows must cross, 
   use a bridge (a small arc over the other line).
   Reroute arrows around component boxes rather than through them.

3. ARROW GROUPING — if multiple components send to the same destination,
   consolidate into one arrow with a label like "3 services" 
   rather than drawing 3 separate arrows.

4. ARROW LABELS — every arrow must have exactly one label:
   - The protocol or auth mechanism (TLS, mTLS, IAM, Bearer Token)
   - If the connection carries sensitive data, add a second 
     line in smaller text: "carries: [data type]"
   - Labels must sit ON the arrow, centred, never overlapping a box

5. ARROW WEIGHT — use line thickness to convey trust level:
   Thick solid line = authenticated + encrypted
   Thin solid line = authenticated only
   Dashed line = internal only / read-only
   Red dashed line = flagged — needs review

---

## TEXT & LEGIBILITY RULES

Current problem: text is too small, too dense, and inconsistently sized.

Fix using these rules:

1. HIERARCHY — use exactly 3 text sizes:
   LARGE: Zone labels (INTERNET ZONE, OCP CLUSTER, etc.)
   MEDIUM: Component names (MCP Server Pod, Auth Service Pod, etc.)
   SMALL: Annotations only (encryption type, secret names, data labels)
   Nothing smaller than SMALL. If it doesn't fit at SMALL, remove it.

2. ANNOTATIONS — move all bullet-point lists OUT of the component boxes.
   Replace with icons + one-line labels:
   🔒 AES-256-GCM   (encrypted at rest)
   🔐 TLS 1.3       (encrypted in transit)
   🔑 Vault          (secrets managed by)
   ⚠️ Contains PII   (data classification)
   👤 Bearer Token   (auth mechanism)

3. COMPONENT BOXES — each box should contain only:
   Line 1: Component name (MEDIUM, bold)
   Line 2: Environment tag in brackets [Pod / Service / Storage]
   Line 3-4: Max 2 icon+label annotations from the list above
   Nothing else. All other detail moves to the legend.

4. LEGEND — expand the legend to absorb the detail removed from boxes:
   Group into 4 sections:
   - Connection Types (your existing content, keep it)
   - Auth Mechanisms (one line per mechanism: icon + name + what uses it)
   - Data Classification (one line per type: icon + label + which components)
   - Secrets Management (one line per secret: name + where stored + who accesses)

5. WHITESPACE — add padding inside every box (text must not touch the border).
   Add spacing between zones (zones must not share a border).
   Every arrow must have clearance from the nearest box edge.

---

## COLOUR RULES

Current problem: colours are being used inconsistently 
and some zones are hard to distinguish.

Fix using this system:

   Internet Zone:        Red border,   light red fill    (#FFF0F0)
   OCP Cluster GCC:      Blue border,  light blue fill   (#F0F4FF)
   OCP Cluster SCC:      Blue border,  light blue fill,  dashed border
   Internal Corporate:   Green border, light green fill  (#F0FFF4)
   Secrets Management:   Purple border, light purple fill (#F8F0FF)
   Legend box:           Grey border,  white fill

   Component boxes INSIDE zones:
   Use white fill with the zone's border colour.
   Never use a different colour family inside a zone.

   Arrows:
   Default: dark grey (#333333)
   Auth boundary crossing: blue (#0055CC)
   Flagged/unencrypted: red (#CC0000)

---

## OUTPUT FORMAT

Produce the revised diagram in Excalidraw JSON format
so it can be imported directly and edited further.

Before outputting, confirm:
1. No arrows cross without a bridge
2. No box contains more than 2 annotation lines
3. Every arrow has exactly one label
4. All three text sizes are used consistently
5. The legend accounts for all detail removed from boxes

Use Excalidraw's elbow connector style for all arrows 
(not curved, not straight — elbow/orthogonal only).
This prevents diagonal crossing and keeps the diagram grid-aligned.
Set all arrow endpoints to use named anchor points 
(top, bottom, left, right) not free-floating points.



==============

The current diagram has arrow routing problems that are 
reducing legibility. 

Replace all directional arrows with the following approach:

1. Draw thin lines (no arrowheads) between connected components.
   Use line colour only to indicate trust level:
   Blue line = crosses an auth boundary
   Grey line = internal only
   Red line = flagged / unencrypted segment

2. Label each line with a circled number only: ①②③ etc.
   No text on the lines themselves.

3. Add a CONNECTION KEY table below the diagram with columns:
   # | From | To | Auth | Protocol | Data Carried | Encrypted?

4. Remove the existing arrow colour legend — 
   replace with the connection key table.

5. The data flow summary sentence at the bottom stays as-is.
   It provides the narrative. The connection key provides the detail.
   The diagram itself provides the spatial layout.
   These three layers together replace what arrows were trying to do alone.

============

Targeted Cleanup & Label Corrections

Make the following specific corrections to the diagram.
Do not change anything else.

---

CORRECTION 1 — MCP Server Pod
Current annotations are incomplete. Replace with:

  MCP Server [Pod]
  🔑 OAuth2 + JWT + HMAC
  🔓 Decrypts AES-256-GCM on read
  ⚠️ Contains PII

---

CORRECTION 2 — Auth Service Pod
Add the EWS protocol explicitly:

  Auth Service [Pod]
  🔑 LDAP auth
  🔑 NTLM → EWS
  ⚠️ Contains PII

---

CORRECTION 3 — Embedding Sync Pod
Clarify the write destination:

  Embedding Sync [Pod]
  🔑 S3 key
  → Copies encrypted DB to PVC

---

GLOBAL TEXT RULE — apply across entire diagram
Shorten all labels using these substitutions:

  "Encrypted at rest" → "Enc. at rest"
  "Authentication" → "Auth"
  "Persistent Volume Claim" → "PVC"
  "Internal only" → "Internal"
  "Contains" → "Has"
  "Encrypted PII" → "Enc. PII"
  "At rest: AES-256-GCM" → "Rest: AES-256-GCM"
  "In transit: TLS 1.3" → "Transit: TLS 1.3"
  "If compromised" → "If breached"
  "All connections TLS unless noted" → "All conns. TLS"
  "Identical Deployment" → "Mirror DC"

Maximum label length: 25 characters per line.
If a label exceeds this, split across two lines or abbreviate further.


============


Entra ID Classification Fix

CORRECTION — Entra ID label is wrong.

Current label says: Entra ID [EXTERNAL]
This is incorrect and must be changed.

Context:
RBC operates its own internal Microsoft tenant.
Entra ID is external to the MCP app but internal to RBC corporate network.
It is NOT a public external service. It sits inside RBC's trust boundary.

Fix as follows:

1. Move Entra ID out of any EXTERNAL classification.
   It belongs in the INTERNAL CORPORATE zone, not the internet zone.

2. Relabel the component:
   Entra ID [RBC Internal]
   🔑 JWKS only
   🏢 RBC Microsoft Tenant

3. Add a clarification note in the legend under AUTH MECHANISMS:
   "Entra ID = RBC-managed Microsoft tenant.
    External to MCP app. Internal to RBC. Not public."

4. If any arrow or connection line treats Entra ID as 
   crossing an internet boundary, reclassify it as 
   an internal corporate boundary crossing instead.
   Change line colour from red/external to blue/auth boundary.

Do not change anything else.


===============

Mitigation strategies

Add a MITIGATION column to the existing Blast Radius box.

For each breached component already listed, add one mitigation control.

Rules:
- Mitigations must be design-level controls, not code details
  (e.g. "per-user AES keys" not "see encrypt_file() method")
- If a mitigation is not yet implemented, mark it: ⚠️ Recommended
- If a mitigation is confirmed in place, mark it: ✅ Active
- Maximum one line per mitigation
- Do not remove the existing impact statements

Also add one row for:
  PVC breached → all synced DBs readable
  And one row for:
  Entra ID breached → token forgery risk

Keep the box compact. Two columns: Impact | Mitigation.



==============

Remove all connection lines and numbered circle labels 
from the diagram canvas entirely.

The CONNECTION KEY table already communicates every relationship.
Lines on the canvas are now redundant and creating visual noise.

After removing lines:
- Reposition component boxes to use the freed whitespace
- Ensure each zone box has even internal padding
- The numbered circles (①②③) should only appear 
  in the CONNECTION KEY table, not on the canvas

Do not change any text, zone boundaries, 
component labels, or the connection key table.


Also — fix the Entra ID label while you're at it. Still says [EXTERNAL] in this version. Add this line to the same prompt:
Also correct: Entra ID label must read [RBC Internal] not [EXTERNAL].
Move it visually inside the INTERNAL CORPORATE zone border if it is not already.
