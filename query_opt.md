OpenSpec: Personal Grounding Service (Refined)
## Why
Current RAG performance shows that both verbose and optimized prompts dilute search precision by adding irrelevant terms. We need a deterministic approach that extracts the "Project ID" and "User Identity" as hard filters before applying the E5 semantic search.

## GoalsPrecision Recovery: Restore quality to $1/1$ top-result accuracy by stopping "keyword stuffing".Deterministic Filtering: Use extracted entities (e.g., "Konek ID") as mandatory metadata filters in the vector database.Identity Isolation: Ensure the employee_id is a primary partition key for all email RAG operations.Traceability: Every result must display the source (e.g., "Kevin Sivaperumal, Sept 12, 2025").

## The Refined LLM Gateway Prompt
Agent Persona: Entity_Extraction_Specialist

Model: meta-llama/Llama-3.1-8B-Instruct

This prompt is designed to be extractive, not expansive, to prevent the "Quality Issue" where extra terms hurt relevance.

<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a High-Precision Entity Extractor for an Enterprise RAG Gateway.
Your goal: Transform a raw query into a minimal, high-signal JSON object.
Rules:
1. Identify the PRIMARY PROJECT ENTITY (e.g., "Konek ID").
2. Identify the SENDER if mentioned (e.g., "Kevin").
3. DO NOT expand with generic terms like "status," "updates," or "results" unless they are unique to the intent.
4. Output ONLY valid JSON.

### Examples
Input: "How is the Konek ID E2E testing progressing?"
Output: {"project": "Konek ID", "keywords": "E2E testing cycle execution", "intent": "status"}

Input: "What did Kevin say about Konek?"
Output: {"project": "Konek ID", "sender": "Kevin", "keywords": "updates", "intent": "person_query"}
<|eot_id|><|start_header_id|>user<|end_header_id|>
{user_query}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>

## Technical Architecture: The "Full Flow"Input: User Query $\rightarrow$ "What's the status of Konek ID?"LLM Gateway: Extracts {"project": "Konek ID", "keywords": "execution cycle"}.Signal Builder: Python service constructs the E5 string: query: Konek ID execution cycle.Vector DB (Hybrid Search):Filter 1: employee_id == <USER_ID>Filter 2: project_tag == "Konek ID" (Deterministic match).Semantic: Match E5 vector within the "Konek ID" subset.Contextual Result: "Cycle 2 execution completed" (Source: Kevin Sivaperumal, Sept 12).

## Implementation Task for the AI Agent
Task: "Implement the QueryEnricher class in Python.

Integrate with the Llama-3.1-8B TGI endpoint using the provided Extraction Prompt.

Ensure the output is a Pydantic model: EnrichedQuery(project: str, keywords: str, sender: Optional[str]).

Implement a 'Strict Mode' where if a project is found, the downstream search must include a metadata filter for that project, fixing the expansion dilution issue seen in previous tests."
