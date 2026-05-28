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
