The fix is a layout redesign of the blue box, not just new arrows.
Here's what the layout should look like conceptually:


┌─── OCP CLUSTER — GCC ──────────────────────────────┐
│                                                      │
│  [MCP Server Pod] ──tool call──► [Email Service Pod] │
│        │                               │             │
│   reads│                          writes│            │
│        ▼                               ▼             │
│    [PVC Storage] ◄──copies to── [Embedding Sync Pod] │
│                                  (background job)    │
│                                                      │
│         ┌ ─ ─ [SCC Mirror DC] ─ ─ ┐                 │
│              GTM routes both DCs                     │
│         └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘                 │
└──────────────────────────────────────────────────────┘


PVC sits bottom-left — central to both MCP Server above it and Embedding Sync beside it. SCC Mirror moves to the bottom as a footnote box since it's a passive mirror, not an active component in the flow.

Layout Redesign of Blue Box

IMPORTANT — Output valid draw.io XML only.
Use literal Unicode characters only. No HTML entities.
Import via: Extras → Edit Diagram → paste XML

Do not change any component names, labels, table content,
or anything outside the blue OCP Cluster GCC box.

---

REDESIGN: OCP CLUSTER GCC BOX LAYOUT

The blue box needs a complete internal layout redesign.
The goal is for the spatial arrangement of boxes to tell 
the story of how the three services connect, so arrows 
are short, direct, and never cross another box.

STEP 1 — INCREASE BLUE BOX SIZE
Make the OCP Cluster GCC box significantly larger:
- Wider: enough for a 2x2 grid of components
- Taller: enough for two rows plus the SCC Mirror footnote
- Maintain its position relative to the other two zones

STEP 2 — REPOSITION COMPONENTS IN A 2x2 GRID

Top-left:     MCP Server [Pod]
Top-right:    Email Service (Auth) [Pod]
Bottom-left:  PVC [Storage]
Bottom-right: Embedding Sync [Pod]

SCC Mirror [Mirror DC]:
  Move to bottom of blue box, full width, 
  short height (footnote style)
  Dashed border, label: "Mirror DC — GTM routes both DCs"

STEP 3 — INTERNAL CONNECTORS
Draw these five connectors using the new positions.
All connectors must be orthogonal (no diagonals).
No connector may cross another box.

A. MCP Client → MCP Server
   Enters blue box from left
   Label: "via RBC Assist UI harness"
   Line: solid, grey

B. MCP Server → Email Service
   Top-left to top-right (horizontal)
   Label: "tool call"
   Line: solid, grey, right arrow

C. Email Service → S3 Storage (exits blue box rightward)
   From Email Service top-right to Internal Corporate
   Label: "writes encrypted"
   Line: solid, grey, right arrow

D. Embedding Sync → PVC
   Bottom-right to bottom-left (horizontal)
   Label: "copies to PVC"
   Line: solid, grey, left arrow
   Note: Embedding Sync is a background job
   Add small label below box: "(background job)"

E. PVC → MCP Server
   Bottom-left to top-left (vertical)
   Label: "reads on demand"
   Line: dashed, grey, up arrow

STEP 4 — CONNECTOR STYLE
All connectors:
  Routing: orthogonal only
  Source end: no arrowhead
  Destination end: small open arrow
  Label font: 9px, colour #616161
  No connector may pass through or behind any box

STEP 5 — VERIFY BEFORE OUTPUT
Check these before generating XML:
1. No connector crosses the SCC Mirror box
2. PVC is adjacent to both MCP Server and Embedding Sync
3. The Email Service → S3 arrow exits the blue box 
   cleanly on the right edge
4. SCC Mirror is at the bottom, not interfering 
   with any connector path
5. All five connectors have labels


This layout change will cut the arrow crossing problem entirely because PVC is now physically between the two components that use it — MCP Server above and Embedding Sync beside it. The geometry does the work instead of fighting against it.

======================================


IMPORTANT — Output valid draw.io XML only.
Do NOT use HTML entities. Use literal Unicode only.
Import via: Extras → Edit Diagram → paste XML

Fix these five issues only. Do not change anything else.

---

FIX 1 — ROGUE ARROW
Delete the stray dashed connector attached to 
SCC Mirror [Mirror DC] pointing downward.
No connectors should exist outside the blue OCP box.

---

FIX 2 — EM DASH ENCODING
Rows 1, 2, 3, 4, 7, 8, 10 in the At Rest column 
show &#x2014; as visible text.
Replace every instance with the literal character: —

---

FIX 3 — S3 STORAGE LABEL
Replace current value containing visible <br> tag.
New value: S3 Storage [MinIO/Ceph]
Single line, no HTML tags.

---

FIX 4 — BLAST RADIUS ICONS
△ → ⚠️
■ → ✅
If emoji do not render in draw.io, use:
⚠️ → [R] in amber text #F57F17
✅ → [A] in green text #2E7D32

---

FIX 5 — OCP CLUSTER BLUE BOX INTERNAL FLOW

Before making any changes, read the production code 
to confirm the following relationships.
Do not assume. Do not hallucinate.
If the code is ambiguous on any point, note it 
and do not draw that connection.

Once confirmed by code, add internal connectors 
INSIDE the blue OCP Cluster GCC box only showing:

CONNECTION A — Client to MCP Server
  From: MCP Client [RBC Assist UI] 
        (in RBC Network Zone, entering blue box)
  To: MCP Server [Pod]
  Line: solid, dark grey
  Label: "via RBC Assist UI harness"

CONNECTION B — MCP Server to Email Service
  From: MCP Server [Pod]
  To: Email Service (Auth) [Pod]
  Line: solid, dark grey
  Label: "tool call"

CONNECTION C — Email Service writes to S3
  From: Email Service (Auth) [Pod]
  To: S3 Storage [MinIO/Ceph] (Internal Corporate zone)
  Line: solid, dark grey
  Label: "writes encrypted"

CONNECTION D — Embedding Sync copies S3 to PVC
  From: Embedding Sync [Pod]
  To: PVC [Storage]
  Line: solid, dark grey
  Label: "copies to PVC"
  Note: Sync is a background job — 
        show it below the main flow, 
        not inline with A→B→C

CONNECTION E — MCP Server reads from PVC
  From: PVC [Storage]
  To: MCP Server [Pod]
  Line: dashed, dark grey
  Label: "reads on demand"

LAYOUT RULE:
Arrange the three pods vertically inside the blue box 
to support a readable top-to-bottom flow:
  MCP Server [Pod]        ← top
  Email Service [Pod]     ← middle  
  Embedding Sync [Pod]    ← bottom (background job)
PVC sits to the right, shared between Sync and MCP Server.

Do not add any connectors outside the blue box 
except CONNECTION C which crosses to Internal Corporate.

CONNECTOR STYLE for all five:
  Orthogonal routing (no diagonals)
  No arrowheads on source end
  Small open arrow on destination end
  Font size 9px for labels
  Label colour: #616161




============================

Mapping your corrections to this reference:
Reference diagramYour actual componentPersonal Data IngestorEmail Service (Auth) [Pod]Personal Embedding StorageS3 Storage [MinIO/Ceph]Data Sources (EWS/Slack/etc)Exchange [EWS]Embedding Sync ServiceEmbedding Sync [Pod]Openshift PVC / Personal embeddingsPVC [Storage]Embedding Last Used Cache❌ Remove entirelyOn prem Embedding serviceGenAI Gateway [Cohere]

 Blue Box Redesign Using Reference Layout

 IMPORTANT — Output valid draw.io XML only.
Use literal Unicode only. No HTML entities.
Import via: Extras → Edit Diagram → paste XML

Only modify the interior of the OCP Cluster GCC blue box.
Do not change anything outside the blue box.
Do not change any table, footer, or other zone.

---

REFERENCE LAYOUT
Model the interior of the blue box on this flow:

  [Exchange EWS]  ←── outside box, top, existing component
        │
        │  Service Principal / NTLM Authentication
        ▼
  [Email Service (Auth) Pod]
        │
        │  Access Key & Secret (S3 key)
        ▼
  [S3 Storage MinIO/Ceph]  ←── exits right to Internal Corporate
        │
        │  Server to Server OAuth (through Apigee/GTM)
        ▼
  [Embedding Sync Pod]
    (background job)
        │
        │  writes to PVC
        ▼
  [PVC Storage]
        │
        │  reads on demand
        ▼
  [MCP Server Pod]  ←── receives from RBC Assist UI (left entry)
        │
        │  EntraID / OIDC OAuth
        ▼
  [RBC Assist / MCP Client]  ←── outside box, existing component

---

LAYOUT RULES

1. VERTICAL FLOW — arrange components top to bottom 
   in this exact order inside the blue box:
   
   Top:    Email Service (Auth) [Pod]
   Middle: S3 Storage [MinIO/Ceph]  
           — this exits RIGHT to Internal Corporate zone
           — keep it visually connected to that zone
   Below:  Embedding Sync [Pod]
           Label below box: "(background job)"
   Below:  PVC [Storage]
           — dashed border, it is shared storage
   Bottom: MCP Server [Pod]

2. CONNECTORS — vertical, orthogonal, no diagonals
   Each connector needs an auth/protocol label:
   
   Exchange EWS → Email Service:
     Label: "NTLM Authentication"
     Enters blue box from top
   
   Email Service → S3 Storage:
     Label: "S3 key + AES-256-GCM"
   
   S3 Storage → Embedding Sync:
     Label: "Server to Server OAuth"
     Note: show this going through GTM 
     (small annotation, not a separate box)
   
   Embedding Sync → PVC:
     Label: "writes encrypted DB"
   
   PVC → MCP Server:
     Label: "reads on demand"
     Line: dashed (read-only relationship)
   
   MCP Client → MCP Server:
     Label: "EntraID / OIDC OAuth"
     Enters blue box from left

3. REMOVE — do not include:
   - Embedding Last Used Cache
   - Any reference to Slack or other data sources
   - On prem Embedding service 
     (Cohere/GenAI stays in Internal Corporate as-is)

4. SCC MIRROR
   Keep at bottom of blue box as a dashed footnote box.
   Label: "Mirror DC — GTM routes both DCs"
   Must not interfere with the vertical flow above it.

5. CONNECTOR STYLE
   All connectors:
     Routing: orthogonal
     Source end: no arrowhead
     Destination end: open arrow
     Label fontSize: 10px
     Label fontColor: #212121
     Label background: #FFFFFF
     (labelBackgroundColor=#FFFFFF)

6. BOX SIZING
   Increase blue box height to comfortably fit 
   5 components vertically with 24px gaps between them
   plus the SCC Mirror footnote at the bottom.
   Minimum blue box height: 600px

7. VERIFY BEFORE OUTPUT
   - Flow reads top to bottom without any crossing arrows
   - Every connector has a label
   - S3 Storage is spatially close to the right edge 
     of the blue box so its connection to Internal 
     Corporate is short and clean
   - PVC has a dashed border
   - No connector passes through any box

The key insight from your reference image that was missing before is the auth label on every arrow. That's what makes the flow readable to a security team — they can trace not just what connects to what but how each connection is authenticated without looking at the connection key table. The diagram becomes self-explanatory. 

Make this change in a new file called v3.


===========
FInal fix


What's Missing / Wrong
1. MCP Client is not connected to GTM
The RBC Network Zone shows MCP Client, GTM Load Balancer, and User Browser as isolated boxes — none of them have connectors going into the blue OCP box. The flow starts abruptly at Email Service with no entry point shown from the left zone.
2. Exchange [EWS] has no connector to Email Service
The NTLM Authentication arrow is pointing the wrong way — it's coming FROM Internal Corporate TO Email Service, but EWS should be the source that Email Service pulls from. Also it looks like it's floating rather than anchored to Exchange.
3. S3 Storage is inside the blue box
It should be in Internal Corporate zone on the right, with an arrow exiting the blue box rightward. Currently it's sitting inside OCP which misrepresents where S3 lives.
4. Internal Corporate zone looks empty/sparse
With S3 potentially moved inside the blue box, the right zone has lost a component and looks unbalanced.
5. Blast Radius icons still showing △ and ■
You've confirmed you don't want emojis at all — replace with plain text labels.


IMPORTANT — Output valid draw.io XML only.
Use literal Unicode only. No HTML entities.
Import via: Extras → Edit Diagram → paste XML

---

FIX 1 — RBC NETWORK ZONE CONNECTORS
Add connectors from the RBC Network Zone 
into the OCP Cluster blue box:

MCP Client [RBC Assist UI] → MCP Server [Pod]
  Label: "EntraID / OIDC OAuth"
  Enters blue box from left side
  Line: solid, dark grey, open arrow

GTM Load Balancer [RBC Network] → MCP Server [Pod]
  Label: "TLS 1.3"
  Enters blue box from left side
  Line: solid, dark grey, open arrow

User Browser [RBC Intranet] → GTM Load Balancer
  Label: "LDAP creds"
  Line: solid, dark grey, open arrow

---

FIX 2 — EXCHANGE EWS CONNECTOR
Exchange [EWS] lives in Internal Corporate zone.
Email Service (Auth) [Pod] pulls from it.

Draw connector:
  From: Exchange [EWS] (Internal Corporate)
  To: Email Service (Auth) [Pod] (OCP blue box)
  Label: "NTLM Authentication"
  Direction: right to left 
  (Exchange is the source, Email Service pulls from it)
  Line: solid, dark grey, open arrow pointing 
  at Email Service

---

FIX 3 — S3 STORAGE LOCATION
S3 Storage [MinIO/Ceph] must live in 
Internal Corporate zone, NOT inside the blue box.

If it is currently inside the blue box:
  Move it to Internal Corporate zone
  Position it top-left of that zone

The connector from Email Service → S3 Storage
must cross from the blue box rightward 
into Internal Corporate.
  Label: "S3 key + AES-256-GCM"
  Line: solid, exits right edge of blue box

The connector from S3 → Embedding Sync
must re-enter the blue box from the right.
  Label: "Server to Server OAuth (via GTM)"

---

FIX 4 — BLAST RADIUS TABLE
Remove all emoji and icon characters entirely.
Replace with plain text + colour only:

  Per-user AES keys          → no icon, plain text
  TTL cache + secure erase   → no icon, plain text
  VPC endpoint + bucket policy → no icon, plain text
  Per-user volume isolation  → no icon, plain text
  JWKS + short token expiry  → no icon, plain text

For the Containment column:
  Active controls: text colour #2E7D32 (green)
  Recommended controls: text colour #E65100 (amber)

Add a small legend below the Blast Radius table:
  Green text = Active control
  Amber text = Recommended control

No emoji, no symbols, no icon characters anywhere 
in the Blast Radius table.

---

FIX 5 — OCP CLUSTER LABEL
The blue box label currently shows a warning icon 
next to "OCP CLUSTER — GCC".
Remove any icon or symbol from the zone label.
Plain text only: OCP CLUSTER — GCC

---

VERIFY BEFORE OUTPUT
1. S3 Storage is in Internal Corporate, not blue box
2. Every zone has at least one inbound connector
3. Exchange → Email Service arrow points left to right
   with arrowhead at Email Service end
4. No emoji or symbols in Blast Radius table
5. MCP Client has a connector reaching MCP Server
6. No connector crosses another box
