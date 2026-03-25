# Ejike Udeze

**Principal Software Engineer | Framework: GROW + SMART | Updated: March 2026**

---

## Status Key
| Symbol | Meaning |
|---|---|
| ✅ | Delivered |
| 🔄 | In Progress |
| 🎯 | Committed |
| 📅 | Planned |

---

# 🔧 Technical Goals

---

## 1. Ship & Scale the Personal Grounding AI Tool

> You own the core product — an MCP-powered chat agent that grounds users in their own context (email, Slack, and beyond). This is the ship that matters this fiscal year.

**What's done:**
- ✅ MCP tool architecture designed and in active development
- ✅ RAG pipeline built with SQLite-backed ingestion
- ✅ DB encrypted at ingestion phase
- ✅ PVC provisioned for S3 file downloads; MCP tool reads from PVC

**Q2 targets:**
- 🔄 Ship MVP to production — all **4 features** (MCP core, Sticky Sessions, email integration, Slack integration) live by **May 31**

**H2 targets:**
- 📅 Complete the product's target state — extended integrations (Confluence, Jira), Knowledge Assistant, Journal Assistant, and Proactive Agent — each with a **documented ADR** and captured in the **product catalogue**

**Measures:**
- MCP tool live in prod by **May 31**
- Email + Slack fully functional at launch
- 1 PoC per quarter (Q2: Knowledge, Q3: Journal, Q4: Proactive Agent)
- Each PoC produces a written outcome note
- Proactive agent spike documented by Q4

---

## 2. Architecture Decision Records (ADRs)

> Every meaningful design trade-off on this team gets documented. Not bureaucracy — institutional memory that compounds.

**What's done:**
- ✅ 2 ADRs authored in Q1

**Targets:**
- 🎯 2 more ADRs by end of Q2 (PVC design + MCP tool architecture)
- 📅 1 ADR per major integration — Confluence, Jira, Proactive Agent

**Measures:**
- No feature with a significant design trade-off ships without an ADR
- **6–8 ADRs total** by FY end — feature-driven, not calendar-driven

---

## 3. Spec-Driven Development (SDD)

> Spec before code. Every major feature on this team starts with a written spec — not a ticket, not a verbal agreement. You set this bar and hold the team to it.

**Targets:**
- 🎯 Author spec for MCP tool core architecture — within 45 days
- 📅 Spec for each major integration (Confluence, Jira, Proactive Agent)
- 📅 Spec for agent orchestration layer as the tool count grows

**Measures:**
- No major feature starts without a written, reviewed spec
- Minimum **1 spec per quarter**; 4 by FY end

---

## 4. AI Systems & Cloud-Native Engineering

> You own how this product runs, not just what it does. Infrastructure decisions made here have a long tail.

**What's done:**
- ✅ OpenShift/Kubernetes deployment — 5+ years of production experience
- ✅ PVC provisioned and integrated into MCP pipeline
- ✅ 99.99% uptime track record on mission-critical systems

**Targets:**
- 🎯 Sticky Sessions implemented and load-tested before prod launch
- 📅 Define scaling strategy for Personal Grounding tool as user base grows
- 📅 Propose AI observability framework (latency, retrieval quality, hallucination rate) — **Q3**
- 📅 AI observability dashboard live — **Q4**

**Measures:**
- Zero P0 incidents at launch attributable to infrastructure decisions
- Observability framework proposal delivered to team by end of Q3
- Metrics dashboard live in Q4

---

# 🤝 Non-Technical Goals

---

## 5. Team Mentorship

> You've mentored 5+ engineers before. At Borealis, you're the AI systems specialist — be deliberate about sharing that edge.

**Targets:**
- 🎯 Mentor **2+ engineers** on RAG pipeline design and cloud-native AI this fiscal year
- 🎯 Be the team's go-to on MCP architecture — own the room when that question comes up
- 📅 Pair with at least 1 engineer on each major integration sprint

**Measures:**
- **2 named mentees by Q2**
- At least **4 documented pairing sessions** by year end

---

## 6. Sponsorship

> Mentorship opens minds. Sponsorship opens doors. Your village got you here — pay it forward.

**Targets:**
- 🎯 Identify **1 high-potential junior or mid-level engineer** by Q2
- 🎯 Create at least **2 visible moments** for them — design review co-lead, stakeholder demo, or tech talk
- 📅 Advocate for them in rooms they are not in

**Measures:**
- **1 named sponsee** by end of Q2
- **2+ advocacy moments** logged by year end

---

## 7. Internal Knowledge Sharing & Demos

> You spoke at BFUTR 2025 to thousands. Bring that energy inside — this team and organisation need it.

**Targets:**
- 🎯 First internal tech talk by **end of May** — topic: MCP architecture or RAG pipeline design for Personal Grounding
- 📅 Quarterly knowledge share — tied to PoC outcomes or product milestones
- 📅 Lead post-launch demo of Personal Grounding tool to Borealis leadership (May/June)
- 📅 Demo agent extension roadmap to team and leadership in Q3

**Measures:**
- **1 talk per quarter** = 4 by year end
- At least **2 demos** delivered to stakeholders by year end
- At least 1 talk directly tied to a PoC or product milestone

---

## 8. Product Roadmap Contribution

> You don't just execute on the roadmap — you shape it. Think like the founder of this product, not just an engineer on it.

**Targets:**
- 🎯 Champion Knowledge + Journal Assistant extensions in H2 roadmap discussions
- 🎯 Write a **product brief** on the proactive email-sending agent use case before the spike begins
- 📅 Bring at least **1 user insight or usage pattern** from prod to inform a roadmap decision

**Measures:**
- **1 product brief** authored by Q3
- **Named contribution** to at least 1 roadmap decision per half

---

## 9. Onboarding Contribution

> You're still in ramp-up mode — that's a superpower. You see what insiders have stopped seeing.

**Targets:**
- 🎯 Document your own ramp-up gaps and missing context by end of Q2
- 🎯 Produce **1 onboarding artefact** (guide or checklist) for the next AI engineer who joins this team
- 📅 Co-onboard or buddy the next hire when they join

**Measures:**
- Onboarding artefact submitted to team by **end of Q2**

---

# 📊 Milestone Tracker

| Quarter | Technical | Non-Technical |
|---|---|---|
| **Q1 ✅** | MCP in dev · 2 ADRs · DB encrypted · PVC live | Joined team |
| **Q2** | MCP to prod · Sticky Sessions · 2 ADRs · First spec · PoC: Knowledge Assistant | First internal talk · 2 mentees named · Sponsee identified · Onboarding artefact |
| **Q3** | PoC: Journal Assistant · Confluence + Jira integrations · AI observability proposal · 2 specs | Quarterly talk · Sponsorship advocacy · Roadmap product brief |
| **Q4** | Proactive Agent spike · AI observability dashboard · ADRs for new integrations | Quarterly talk · Year-end retro with manager · Next hire co-onboarding |

---


