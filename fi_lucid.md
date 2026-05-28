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
