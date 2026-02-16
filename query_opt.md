OpenSpec: Personal Grounding Service (Agentic RAG)
## Why
Current LLM expansions are adding terms that dilute search relevance rather than improving it. We must move to a deterministic pipeline that prioritizes high-signal entities (like "Konek ID") and isolates data by user.

## Goals
Deterministic Precision: Resolve the "expanded query" dilution by prioritizing exact entity matches (e.g., "Konek ID").

Zero-Trust Identity Isolation: Prevent cross-pollination. Every search must be hard-scoped to the employee_id.

Performance with Quality: Maintain the 15.9x speed of optimized prompts while restoring the quality of the top search results.

Low-Latency Performance: Ensure P95 latency remains under 2.5s for the full "Gateway -> E5 -> Search" loop on OpenShift.

Source-Grounded Traceability: Ground all answers in specific email metadata (e.g., "From: Kevin Sivaperumal, Sept 12, 2025").

## What Changes
1. Refined LLM Gateway (Reasoning Layer)
Model: meta-llama/Llama-3.1-8B-Instruct

New Logic: Switch from "Query Expansion" to Structured Entity Extraction. The goal is a concise JSON object, not a verbose sentence.

Action: Extract primary_entity (e.g., "Konek ID"), sender, and intent. Stop the "over-expansion" that leads to query dilution.

2. E5 Embedding Optimization (Retrieval Layer)
Model: intfloat/multilingual-e5-large

Signal: Embed the high-signal string only after entity isolation.

Requirement: Mandatory query:  prefix for E5 retrieval.

3. Hybrid RAG Search (Data Isolation)
Strategy: Perform a Strict Metadata Pre-filter on the project entity (e.g., project == "Konek ID") before semantic ranking. This ensures the "Librarian" is looking in the right room before looking for the book.

## Design & ArchitectureThe New FlowUser Query $\rightarrow$ LLM Gateway (Extracts Konek ID as a key identifier).LLM Gateway $\rightarrow$ Structured JSON (Prevents the "overly expanded" query problem).JSON $\rightarrow$ E5 Model (Embeds target keywords with query:  prefix).Vector $\rightarrow$ Hybrid Search (Strictly filtered by employee_id and project_tag).Contextual Results $\rightarrow$ Final Synthesis (Grounded in specific emails like "Cycle 2 execution completed").

# Core logic to fix the "Expansion Dilution" problem
class DeterministicRetriever:
    def get_grounded_context(self, user_id, raw_query):
        # 1. Extraction (Not Expansion)
        enrichment = self.gateway.extract_entity(raw_query) # e.g. {"project": "Konek ID"}
        
        # 2. Strict Signal Construction
        # Avoids adding generic "status" terms that dilute the vector
        search_signal = f"query: {enrichment.project} {enrichment.specific_keywords}"
        
        # 3. Isolated Hybrid Search
        results = self.db.search(
            vector=self.e5.encode(search_signal),
            filter={
                "employee_id": user_id,
                "project_tag": enrichment.project  # HARD FILTER
            }
        )
        return results

## Implementation Tasks[Prompt Tuning] Refine the LLM Gateway prompt to stop "expanding" queries and start "extracting" entities to fix the precision issues.[API] Implement a POST /v1/enrich endpoint that returns Pydantic-validated JSON.[Search] Configure the Vector DB (OpenSearch) to enforce mandatory employee_id and project metadata filtering.[Validation] Re-run the E2E test scenarios (specifically looking to improve the $6/8$ failure rate).
