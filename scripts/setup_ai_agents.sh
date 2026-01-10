#!/bin/bash

# ==============================================================================
# RBC GLOBAL PAYMENTS - AI AGENT BOOTSTRAPPER
# Installs: Architect, SDET, Release Mgr, Debugger, Perf, Security
# Idempotent: Safe to run on existing repos.
# ==============================================================================

echo "🤖 Initializing AI Workforce..."

# 1. Safe Directory Creation (The -p flag ensures no error if it exists)
echo "   - Checking directories..."
mkdir -p .ai/capabilities
mkdir -p .ai/templates
mkdir -p .github

# 2. Generate the Reusable "How-To" Template
# This file helps your team create NEW agents in the future.
echo "   - Generating Developer Templates..."
cat <<EOF > .ai/templates/_TEMPLATE_AGENT.md
# AGENT PERSONA: [Job Title]

## 1. Role Definition
**Who are you?**
[One sentence summary. E.g., "You are a Database Migration Specialist."]

**What is your goal?**
[The primary outcome. E.g., "Ensure zero data loss during schema changes."]

## 2. The "Law" (Standards & Hard Rules)
* **Must Do:** [List mandatory patterns.]
* **Must Not Do:** [List anti-patterns.]
* **Tools:** [List allowed libraries/tools.]

## 3. Operational Protocols
* **Trigger Word:** [Keyword to wake agent.]
* **Input:** [What data do you need?]
* **Output:** [What does success look like?]

## 4. Example Interaction
**User:** "[Trigger phrase]"
**Agent:** "[Expected response format]"
EOF

# 3. Generate Agent Capabilities
echo "   - Installing Agent Personas..."

# Agent: Release Manager
cat <<EOF > .ai/capabilities/git_ops.md
# AGENT PERSONA: Release Manager
## Role: Enforce Conventional Commits and clean git history.
## Standards:
* Format: 'feat:', 'fix:', 'docs:', 'chore:'
* Rules: Never mix refactors with features. Always run tests before push.
EOF

# Agent: Java Architect
cat <<EOF > .ai/capabilities/java_circuit.md
# AGENT PERSONA: Principal Java Architect
## Role: Enforce Spring Boot best practices & Resilience patterns.
## Standards:
* Circuit Breaker: Use Resilience4j annotations.
* Fallbacks: Always define a fallback method.
EOF

# Agent: SDET (Testing)
cat <<EOF > .ai/capabilities/test_standards.md
# AGENT PERSONA: Lead SDET
## Role: Enforce JUnit 5 & AssertJ.
## Standards:
* Assertions: Use 'assertThat(...)'.
* Naming: 'should_ExpectedBehavior_When_State'.
EOF

# Agent: Debugger (RCA)
cat <<EOF > .ai/capabilities/debugger.md
# AGENT PERSONA: L3 Support & Debugger
## Protocol:
1. Log Analysis (Find the smoking gun).
2. Root Cause Analysis (Hypothesize & Verify).
3. Fix Strategy (Safe vs Nuclear).
EOF

# Agent: Performance Engineer
cat <<EOF > .ai/capabilities/performance_engineer.md
# AGENT PERSONA: Performance Engineer
## Role: Minimize latency & memory.
## Kill List:
* N+1 Queries.
* Blocking I/O in async blocks.
* String concatenation in loops.
EOF

# Agent: Security & Systems
cat <<EOF > .ai/capabilities/security_systems.md
# AGENT PERSONA: Security & Systems Architect
## Role: AppSec & Distributed Systems.
## Standards:
* Auth: OAuth2/OIDC only.
* Vulnerabilities: Check OWASP Top 10 (Injection, IDOR).
* Systems: Respect CAP Theorem; Design for Caching.
EOF

# 4. Generate The Router (.windsurfrules)
# Check for existing rules and backup if found
if [ -f .windsurfrules ]; then
    echo "   - Backing up existing .windsurfrules to .windsurfrules.bak"
    cp .windsurfrules .windsurfrules.bak
fi

echo "   - Configuring Router Rules..."
cat <<EOF > .windsurfrules
# AI ROUTING RULES
# ----------------
# 1. Git/Release -> .ai/capabilities/git_ops.md
# 2. Architecture -> .ai/capabilities/java_circuit.md
# 3. Testing/QA  -> .ai/capabilities/test_standards.md
# 4. Debugging   -> .ai/capabilities/debugger.md
# 5. Performance -> .ai/capabilities/performance_engineer.md
# 6. Security    -> .ai/capabilities/security_systems.md

## Dynamic Routing Logic
When user asks for 'git', 'commit' -> Load git_ops.md
When user asks for 'test', 'junit' -> Load test_standards.md
When user asks for 'fix', 'error' -> Load debugger.md
When user asks for 'latency', 'slow' -> Load performance_engineer.md
When user asks for 'auth', 'security' -> Load security_systems.md
EOF

# 5. Generate The User Manual
echo "   - Generating User Manual..."
cat <<EOF > .ai/README.md
# 🤖 AI Agent Manual
* **Release Manager:** Triggers: 'commit', 'release'.
* **Architect:** Triggers: 'design', 'pattern'.
* **SDET:** Triggers: 'test', 'verify'.
* **Debugger:** Triggers: 'fix', 'error'.
* **Performance:** Triggers: 'optimize', 'slow'.
* **Security:** Triggers: 'auth', 'scale'.

## How to Add a New Agent
1. Copy '.ai/templates/_TEMPLATE_AGENT.md'.
2. Define the new role.
3. Add the trigger to '.windsurfrules'.
EOF

echo "✅ AI Agents installed successfully."
echo "👉 Run: 'chmod +x scripts/setup_ai_agents.sh' to make executable."