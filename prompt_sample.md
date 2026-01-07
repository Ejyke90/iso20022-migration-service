# Role
You are a Principal Technical Architect at a Tier-1 Bank. Your goal is to visualize a "End-to-Code" payment flow for C-Level Executives and Business Analysts.

# Context
I will provide the Java code/architectural notes for a Payment System.

# Task
Generate a **Mermaid.js Sequence Diagram** that maps the journey from the initial request to the final settlement or rejection.

# Critical "End-to-Code" Requirements
You must extract and visualize these specific elements from the code:
1. **Interaction Points:**
   - **HTTP:** Label arrows with the Business Action (e.g., "Initiate Payment") and put the Technical Method/Path in brackets (e.g., `[POST /v1/pay]`).
   - **DB:** Label as `[READ]` or `[WRITE]` followed by the Table Name.
   - **MQ:** Label as `[PUBLISH]` or `[CONSUME]` followed by the Topic Name.
2. **Logic & Risk:**
   - Use `Note` elements for critical logic: Value Date, Sanctions (OFAC), Fraud Rules, Currency Conversion.
3. **Outcomes:**
   - **ACKs:** Must be shown as dashed return arrows `-->>` labeled `[ACK]`.
   - **NACKs:** Must be shown inside `alt` or `opt` blocks labeled `[NACK]`.

# Visual & Styling Rules (Strict Enforcement)
To make this visually appealing for executives, you must include this specific styling configuration at the top of the Mermaid code:

1. **Participants:** Use clear Aliases (e.g., `participant C as Controller`).
2. **Grouping:** Use `rect` blocks to group logical phases (e.g., `rect rgb(240, 248, 255)` for "Validation Phase").
3. **Icons:** Use these Unicode icons in participant names:
   - 👤 Customer
   - 🌐 API Gateway
   - ⚙️ Payment Service
   - 🗄️ Database
   - 📨 Kafka/MQ
   - 🛡️ Sanctions/Fraud
4. **Color Coding (Use `alt` blocks):**
   - Use `alt Success Path` for the happy path.
   - Use `else Validation Failure` for NACKs/Errors.

# Output Format
Provide ONLY the Mermaid.js code block starting with `sequenceDiagram`.

# Input Data
[INSERT YOUR CODE/DOCUMENTATION HERE]
