# Contributing to ISO20022 Migration Service

Welcome to the team. This repository is **AI-Enabled**, meaning we use specialized AI Agents to enforce architectural standards, manage releases, and maintain code quality.

We use **Windsurf (Cascade)** as our primary editor. Please follow the workflows below to collaborate with our AI agents.

---

## 🤖 Meet the AI Team
We do not use generic AI prompts here. We have defined specific "Personas" that you must utilize for specific tasks.

| Agent Role | Responsibility | Trigger Keywords | Capability File |
| :--- | :--- | :--- | :--- |
| **The Architect** | Implements Java/Spring patterns, Resilience4j, and core logic. | `Architecture`, `Circuit Breaker`, `Pattern`, `Design` | `.ai/capabilities/java_circuit.md` |
| **The SDET** | Writes strict JUnit 5/AssertJ tests. Focuses on edge cases. | `Test`, `Coverage`, `TDD`, `Mock`, `Verify` | `.ai/capabilities/test_standards.md` |
| **Release Mgr** | Handles git commits, pushes, and changelogs. Enforces Conventional Commits. | `Git`, `Commit`, `Push`, `Release` | `.ai/capabilities/git_ops.md` |
| **The Debugger** | Root Cause Analysis (RCA) for build failures and bugs. | `Fix`, `Error`, `Crash`, `RCA`, `Debug` | `.ai/capabilities/debugger.md` |

---

## 🛠 Standard Workflows

### 1. Building New Features
**Do not** just ask "Write code for X."
**Do** ask the Architect to implement specific patterns.
> **Prompt:** *"Acting as the Architect, scaffold a new PaymentService class using our standard Circuit Breaker pattern."*

### 2. Testing (TDD)
We follow a strict "Verify First" approach.
> **Prompt:** *"I need to add a parser for field 72. Acting as SDET, write the failing unit tests first using AssertJ."*

### 3. Debugging & RCA
If a build fails, do not blindly apply the fix. Ask for the Root Cause.
> **Prompt:** *"@debugger.md Here is the stack trace. Perform an RCA and propose the safest fix."*

### 4. Committing Code
Never run `git commit -m` manually for complex changes. Let the Release Manager draft it to ensure it links to issues correctly.
> **Prompt:** *"I am done with the feature. Release Manager, please prepare the commit."*

---

## 🧠 Memory System (Beads)
This repo uses **Beads** to maintain context across sessions.

* **Start of Day:** Run `bd issues` to see open tasks.
* **New Task:** Run `bd create "Title of task"` to log your work.
* **Context Lost?** If the AI seems confused, tell it: *"Read @AI_CONTEXT.md to refresh your memory."*

---

## 🛡 Governance & Rules
* **AI Rules (`.windsurfrules`):** This file controls how the agents behave. It is **protected**.
* **Capabilities (`.ai/capabilities/`):** These define our engineering standards.
* **Changes:** If you want to update a standard (e.g., switch test libraries), you must submit a PR and get approval from the Tech Lead / Code Owners.

---

## 🚀 Quick Setup for New Joiners
1.  Install **Windsurf Editor**.
2.  Open this repository.
3.  Open Cascade Chat (`Cmd+L`).
4.  Type: *"@AI_CONTEXT.md Hello, please explain the current architecture of this application to me."*