# 🤖 ISO20022 Migration Service - AI Agent Manual

This repository is equipped with a **Multi-Agent System** running on Windsurf (Cascade). We do not use generic AI prompts. We use specialized "Personas" to enforce our engineering standards.

## ⚡️ Quick Reference Table

| Agent Name | Primary Focus | Trigger Keywords | Capability File |
| :--- | :--- | :--- | :--- |
| **Release Manager** | Git Ops, Commits, Deployments | `git`, `commit`, `push`, `release` | `git_ops.md` |
| **The Architect** | Java Patterns, Resilience, Core Logic | `circuit breaker`, `design`, `structure`, `pattern` | `java_circuit.md` |
| **The SDET** | Testing, Coverage, TDD, Mocks | `test`, `unit test`, `coverage`, `verify`, `mock` | `test_standards.md` |
| **The Debugger** | Root Cause Analysis (RCA), Fixes | `fix`, `error`, `crash`, `stack trace`, `debug` | `debugger.md` |
| **Performance Eng** | Latency, Throughput, Memory | `performance`, `slow`, `optimize`, `bottleneck` | `performance_engineer.md` |
| **Security & Systems**| AppSec, Scaling, Caching, Auth | `security`, `auth`, `scale`, `cache`, `vulnerability` | `security_systems.md` |

---

## 📘 Detailed Usage Guides

### 1. Release Manager (`git_ops.md`)
**Role:** Enforces Conventional Commits and safe git practices.
**When to use:** You have finished coding and need to commit, or you need to manage branches.

**✅ How to Trigger:**
> "Release Manager, prepare the commit for these changes."
> "I need to start a new feature for ISO validation. Git agent, set up the branch."

**❌ Don't say:** "Commit this." (Might result in a generic `Update file` message).

---

### 2. The Architect (`java_circuit.md`)
**Role:** Principal Java Engineer. Enforces Spring Boot best practices and Resilience4j patterns.
**When to use:** When scaffolding new services, classes, or implementing complex logic.

**✅ How to Trigger:**
> "Acting as the Architect, scaffold a `PaymentValidationService` with a Circuit Breaker."
> "Design the class structure for the PACS.008 message parser."

**❌ Don't say:** "Write a Java class for payment validation." (Will produce junior-level code without resilience).

---

### 3. The SDET (`test_standards.md`)
**Role:** QA Automation Lead. Enforces JUnit 5, AssertJ, and edge-case coverage.
**When to use:** Writing tests for existing code or performing Test Driven Development (TDD).

**✅ How to Trigger:**
> "Acting as SDET, write the unit tests for this new class using AssertJ."
> "I want to do TDD for the XML parser. SDET, generate the failing test cases first."

**❌ Don't say:** "Add tests." (Will produce weak, happy-path-only tests).

---

### 4. The Debugger (`debugger.md`)
**Role:** L3 Support & Incident Response. Focuses on Root Cause Analysis (RCA) before fixing.
**When to use:** When a build fails, an exception is thrown, or the app crashes.

**✅ How to Trigger:**
> "@debugger.md Here is the stack trace. Perform an RCA and propose a fix."
> "The build is failing on GitHub Actions. Debugger, analyze the logs."

**❌ Don't say:** "Fix this." (The AI might guess blindly without finding the root cause).

---

### 5. Performance Engineer (`performance_engineer.md`)
**Role:** Optimization Specialist. Hunts for N+1 queries, memory bloat, and latency killers.
**When to use:** Before merging a PR, or when code feels slow.

**✅ How to Trigger:**
> "@performance_engineer.md Review this specific loop for bottlenecks."
> "I need to process 50k ISO messages. Performance agent, evaluate the trade-offs between batching and streaming."

**❌ Don't say:** "Make it fast." (Too vague; specific inputs yield specific benchmarks).

---

### 6. Security & Systems Architect (`security_systems.md`)
**Role:** Guardian of Security (AppSec) and Scale (System Design).
**When to use:** Designing APIs, implementing Auth, or reviewing code for vulnerabilities (OWASP).

**✅ How to Trigger:**
> "I am adding a new endpoint. Security Agent, review it for IDOR and Injection flaws."
> "We need to cache these exchange rates. Systems Agent, design a caching strategy that respects CAP theorem."

**❌ Don't say:** "Add a login." (Will likely skip necessary security headers and validation).

---

## 🛠 Troubleshooting
**The Agent isn't listening to the rules?**
1.  **Check Context:** Did you reference the file? Try typing `@git_ops.md` explicitly.
2.  **Check Rules:** Open `.windsurfrules` and ensure the trigger keywords match what you are typing.
3.  **Refresh:** Sometimes the context gets stale. Type `/clear` or start a new chat session.