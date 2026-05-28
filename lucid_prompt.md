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
