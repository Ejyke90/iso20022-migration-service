I have an Excalidraw security architecture diagram that is the 
SOURCE OF TRUTH for all component names, zone names, connections, 
and security classifications.

Do NOT read any code. Do NOT make assumptions.
Extract only what is in the Excalidraw file.

Your job is to convert it into a clean draw.io XML diagram 
in the style of a simplified Lucid Chart — like a consultant 
would present to a boardroom.

---

## VISUAL STYLE RULES

Think: large boxes, lots of whitespace, minimal text, 
clean straight connectors, one colour per zone.

1. BOXES
   - Large, rounded rectangles
   - One colour fill per zone (pastel, not bright)
   - Component name only — NOTHING ELSE inside the box
   - Font: 14px bold for component names
   - No annotations, no icons, no bullet points inside boxes

2. ZONE BOUNDARIES
   - Drawn as large rounded rectangles behind the components
   - Labelled in the top-left corner in CAPS, 12px
   - Use these zone colours:
     RBC Network Zone:     light orange  (#FFF3E0)
     OCP Cluster GCC:      light blue    (#E3F2FD)
     OCP Cluster SCC:      light blue, dashed border
     Internal Corporate:   light green   (#E8F5E9)
     Secrets + Blast:      below diagram, no zone border

3. CONNECTORS
   - Straight orthogonal lines only (no curves, no diagonals)
   - No arrowheads — use line ends only (target dot or nothing)
   - No labels ON the lines
   - Line colour: dark grey (#424242)
   - One line per zone-to-zone relationship only
     (not component-to-component)

4. WHITESPACE
   - Minimum 40px padding inside every zone
   - Minimum 60px between zones
   - Components arranged in a single column per zone
     unless there are more than 3, then two columns max

---

## CONTENT MIGRATION RULES

Migrate from Excalidraw in THREE layers only:

LAYER 1 — ON THE CANVAS (visual)
Extract these and place them as boxes:
- Zone names and boundaries
- Component names only (Pod, Service, Storage labels in brackets)
- The SCC Mirror box with its one-line label

LAYER 2 — BELOW THE CANVAS (tables)
Place these as clean tables beneath the diagram:

Table A: CONNECTION KEY
Columns: # | From | To | Protocol | In Transit | At Rest
Extract each numbered connection from the Excalidraw.
One row per connection. No paragraph format.

Table B: SECRETS
Columns: Secret | Accessed By
Use the security classification names, NOT env var names:
  File Encryption Key, Service Client Credentials,
  Internal Service Token, Object Storage Credentials

Table C: BLAST RADIUS
Columns: If Breached | Containment
Extract each row from the Excalidraw blast radius box.
Mark each mitigation: ✅ Active or ⚠️ Recommended

LAYER 3 — FOOTER (single line)
The DATA FLOW summary sentence only.
Exactly as written in the Excalidraw. No changes.

---

## WHAT TO LEAVE BEHIND

Do NOT migrate any of the following:
- Individual security annotations from inside boxes
  (encryption types, auth mechanisms, PII warnings)
  These live in the connection key table, not on the canvas
- The legend box — draw.io has its own legend system
- Any text smaller than 10px in the Excalidraw
- Vault secret variable names (use classification names instead)
- Any implementation detail (key sizes, TTL values, method names)

---

## OUTPUT FORMAT

Produce valid draw.io XML that can be imported directly 
via File → Import → From XML in draw.io or Lucidchart.

Before outputting, confirm:
1. Every component name matches the Excalidraw exactly
2. No box contains more than 2 lines of text
3. The connection key is a proper table, not a paragraph
4. Zone colours match the spec above
5. No diagonal connectors exist in the output

=======================

The draw.io diagram canvas is correct. Do not touch it.
Fix only the three supporting sections below the canvas.

---

FIX 1 — CONNECTION KEY
Currently rendering as a paragraph. Convert to a proper table.

Create an HTML-style table inside a draw.io table shape with these 
exact columns:
  # | From | To | Protocol | In Transit | At Rest

Rules:
- One row per numbered connection
- Alternate row shading: white and #F5F5F5
- Header row: bold, #1565C0 text, #E3F2FD background
- Column widths — fixed, not auto:
  #=30px, From=120px, To=140px, 
  Protocol=80px, In Transit=90px, At Rest=100px
- For internal pod connections: 
  Protocol = Internal, In Transit = Internal only
- No cell may wrap to a second line — abbreviate if needed

---

FIX 2 — SECRETS TABLE
Convert to a two-column table:

Header: SECRETS (Vault)
Columns: Secret | Accessed By

Rows (use exactly these names, no env vars):
  File Encryption Key      | MCP, Email Svc, Sync
  Service Client Creds     | MCP, Auth, Sync
  Internal Service Token   | Internal proxy
  Object Storage Creds     | Email Svc, Sync

Table style: same alternating shading as connection key.

---

FIX 3 — BLAST RADIUS TABLE
Convert to a two-column table:

Header: BLAST RADIUS (red #B71C1C text, #FFEBEE background)
Columns: If Breached | Containment

Rows:
  MCP Pod          | ⚠️ Per-user AES keys
  Email Svc (Auth) | ✅ TTL cache + secure erase
  S3 Bucket        | ✅ VPC endpoint + bucket policy
  PVC              | ⚠️ Per-user volume isolation
  Entra ID         | ✅ JWKS validation + short expiry

✅ = active control (green text)
⚠️ = recommended, not confirmed (amber text)

---

FIX 4 — S3 STORAGE LABEL
Current label reads [MinIO/CephA] — this is wrong.
Correct it to: S3 Storage [MinIO/Ceph]
Match exactly what the Excalidraw source shows.

---

FIX 5 — FOOTER LAYOUT
Remove all empty space between the three tables.
Stack them in this order with 16px gap between each:
  1. CONNECTION KEY (full width)
  2. SECRETS + BLAST RADIUS (side by side, 50/50 split)
  3. DATA FLOW sentence (centred, 11px, grey #616161)

Output as valid draw.io XML only.
Do not change anything on the canvas above the footer.


================

The canvas is correct. Do not change it.

The CONNECTION KEY, SECRETS, and BLAST RADIUS sections 
are rendering as paragraph text boxes.
This is wrong. They must be actual draw.io table shapes.

Use this exact XML pattern for each table:

<mxCell id="table1" value="CONNECTION KEY" 
  style="shape=table;startSize=30;container=1;
         collapsible=0;childLayout=tableLayout;
         fillColor=#E3F2FD;strokeColor=#1565C0;
         fontStyle=1;fontSize=12;" 
  vertex="1" parent="1">
  <mxGeometry x="40" y="520" width="760" height="30" as="geometry"/>
</mxCell>

<mxCell id="row1" value="" 
  style="shape=tableRow;horizontal=0;
         startSize=0;swimlaneHead=0;
         fillColor=#F5F5F5;" 
  vertex="1" parent="table1">
  <mxGeometry y="30" width="760" height="30" as="geometry"/>
</mxCell>

<mxCell id="cell1" value="#" 
  style="shape=partialRectangle;top=0;left=0;
         bottom=0;right=0;fontStyle=1;" 
  vertex="1" parent="row1">
  <mxGeometry width="30" height="30" as="geometry"/>
</mxCell>

Repeat this pattern for every row and every cell.

---

CONNECTION KEY TABLE
Columns: # | From | To | Protocol | In Transit | At Rest
Column widths: 30 | 120 | 140 | 80 | 90 | 100
Header fill: #E3F2FD, text: #1565C0, bold
Odd rows: #FFFFFF, Even rows: #F5F5F5
Use the 11 numbered connections from the Excalidraw source.

---

SECRETS TABLE
Position: bottom-left, width 360px
Header: SECRETS (Vault)
Header fill: #F3E5F5, text: #6A1B9A, bold
Columns: Secret (180px) | Accessed By (180px)
Rows:
  File Encryption Key      | MCP, Email Svc, Sync
  Service Client Creds     | MCP, Auth, Sync
  Internal Service Token   | Internal proxy
  Object Storage Creds     | Email Svc, Sync

---

BLAST RADIUS TABLE
Position: bottom-right, width 360px
Header: BLAST RADIUS
Header fill: #FFEBEE, text: #B71C1C, bold
Columns: If Breached (150px) | Containment (210px)
Rows:
  MCP Pod          | ⚠️ Per-user AES keys
  Email Svc (Auth) | ✅ TTL cache + secure erase
  S3 Bucket        | ✅ VPC endpoint + bucket policy
  PVC              | ⚠️ Per-user volume isolation
  Entra ID         | ✅ JWKS + short token expiry

---

DATA FLOW
Single text cell below both tables.
Style: fontSize=11, fontColor=#616161, align=center
Value: DATA FLOW: User → FE (LDAP) → Email (Auth) → 
EWS (NTLM, PII) → Enc. → S3 → Sync → PVC → 
MCP (dec.) → GenAI (rerank) → Client

---

Output valid draw.io XML only.
No paragraph text boxes anywhere in the footer.
Every section must use shape=table with shape=tableRow children.



======================

Fix the following five issues only. Do not change anything else.

---

FIX 1 — CHARACTER ENCODING
All special characters are rendering as raw HTML entities.
Replace every HTML entity with the literal Unicode character:

  &#246x; or circled numbers → use plain text: 1, 2, 3, 4...
  &#2014; or &mdash; → use literal: —
  &#x2705; → use literal: ✅
  &#x26A0; → use literal: ⚠️
  <br> tags in cell values → use a real line break 
  or replace with a space

Do this across all three tables and every cell.

---

FIX 2 — S3 STORAGE LABEL
Current value: Storage<br>[MinIO/Ceph]
Replace with two lines using Lucidchart line break syntax
OR simplify to single line: S3 Storage [MinIO/Ceph]
Do not show any HTML tags as visible text.

---

FIX 3 — CONNECTION KEY ROW NUMBERS
Replace the # column values with plain integers:
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
Do not use circled Unicode numbers — they are not 
rendering correctly in Lucidchart CSV import.

---

FIX 4 — BLAST RADIUS ICONS
Replace all encoded emoji with literal characters:
✅ for active controls (green)
⚠️ for recommended controls (amber)
If Lucidchart does not render emoji, replace with:
✅ → [Active]
⚠️ → [Recommended]

---

FIX 5 — ZONE CONNECTORS
Add connection lines between zones using these 
zone-to-zone relationships only (not component level):

  RBC Network Zone → OCP Cluster GCC
  OCP Cluster GCC → Internal Corporate
  OCP Cluster GCC → PVC (already internal, dashed line)
  OCP Cluster GCC ↔ SCC Mirror (dashed, double-ended)

Line style: straight, no arrowheads, dark grey
One line per zone relationship — not per component.

Output updated Lucidchart CSV only.
