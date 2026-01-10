# TASK: Initialize AI Agent System

Please configure this repository with a "Multi-Agent" file structure by creating the following directories and files.

## Step 1: Create Directory Structure
Create a folder named `.ai` in the root.
Inside `.ai`, create a subfolder named `capabilities`.

## Step 2: Create Capability Files
Create the following markdown files inside `.ai/capabilities/`:

### File A: `.ai/capabilities/git_ops.md`
(Content: A "Release Manager" persona that enforces Conventional Commits, checks for 'feat/fix' branches, and requires tests before push.)
*Please write the full "Release Manager" content into this file.*

### File B: `.ai/capabilities/java_circuit.md`
(Content: A "Principal Java Architect" persona that enforces Resilience4j, specific @CircuitBreaker annotations, and fallback methods.)
*Please write the full "Java Architect" content into this file.*

## Step 3: Configure Router
Create (or append to) the `.windsurfrules` file in the root directory.
Add a section titled "## Dynamic Agent Routing".
Add rules that state:
- If the user mentions "git", "commit", or "release", load `.ai/capabilities/git_ops.md`.
- If the user mentions "circuit breaker", "resilience", or "fault tolerance", load `.ai/capabilities/java_circuit.md`.

## Step 4: Verification
List the files created and verify they exist.