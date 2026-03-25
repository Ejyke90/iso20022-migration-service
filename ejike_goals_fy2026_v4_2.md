# FY2026 Goals — Ejike Udeze
**RBC Borealis · Personal Grounding AI · Lead Cloud AI Engineer**
**Vertical → Principal Engineer | Horizontal → AI Product Owner**

---

## Legend
| | |
|---|---|
| ✅ | Done |
| 🔄 | In Progress |
| 🎯 | Committed |
| 📅 | Planned |

---

# Technical

---

## 1. Ship Personal Grounding AI — MVP

**Stack:** Python · FastMCP · FastAPI · SQLite-vec · Cohere · OCP · S3 · Postgres · EWS

**Done:**
- ✅ Grounding Service MCP designed and built
- ✅ Personal Data Ingestor (email + calendar ingestion)
- ✅ Embedding storage pipeline (S3 + sqlite-vec)
- ✅ PVC provisioned for active user embeddings
- ✅ DB encrypted at ingestion

**Shipping (Q2):**
- 🔄 Embedding model deployed to pre-production and production
- 🔄 Auth integration (EntraID OIDC OAuth)
- 🔄 Calendar data retrieval via MCP tool
- 🔄 EWS calendar sync configured
- 🔄 OCP Route Session Affinity — pins each user to one MCP pod, preventing concurrent SQLite access conflicts on the shared PVC

**Production target: May 2026**

**Measure:**
- MVP live on OCP by May 31
- Email + Calendar tools functional at launch
- Zero P0s from infra at go-live

---

## 2. Personal Grounding RAG Pipeline

> The core intelligence layer — Data Sources → Ingestor → On-Prem Embedding → S3 Storage → Embedding Sync → OCP PVC → MCP Semantic Search → RBC Assist

**Done:**
- ✅ End-to-end pipeline designed
- ✅ Semantic search via sqlite-vec on PVC
- ✅ Embedding Sync Service loads active user files into PVC

**Shipping (Q2):**
- 🔄 On-Prem Embedding Service via LLM Gateway (replace local container model)
- 🔄 Embedding Last Used Cache — track active users, manage PVC load

**Extend (H2):**
- 📅 Calendar data embedded and retrievable via MCP
- 📅 Additional data sources integrated as team provisions connectors

**ADR:** OCP Route Session Affinity design · Embedding Sync strategy

**Measure:**
- Embedding freshness measurable (daily refresh cycle validated)
- Retrieval latency benchmarked at MVP launch

---

## 3. AI Observability — Personal Grounding Components

> Scoped to components we own: Ingestor · Grounding MCP · Embedding Sync Service · PVC · Last Used Cache
> Approach: extend existing Dynatrace setup with OpenLLMetry instrumentation — no new tooling to provision

- 📅 Instrument FastAPI + FastMCP services with OpenLLMetry (OpenTelemetry for GenAI)
- 📅 Retrieval latency tracking on MCP semantic search
- 📅 Embedding freshness monitoring (sync lag, daily refresh cycle)
- 📅 RAG response quality signals (token cost per query, retrieval hit rate)
- 📅 PVC load and cache hit/miss rate
- 📅 Ingestor failure and retry visibility
- 📅 Define AI app standards for Personal Grounding — prompt injection defence, RAG data privacy guardrails for personal email/calendar data, model governance

**Measure:** OpenLLMetry instrumentation live by Q3 · Dynatrace AI dashboard by Q4 · AI app standards documented and adopted on PG team

---

## 4. Spikes & PoCs

> Each spike produces a written outcome — even "not yet" is a decision.

- 🎯 Calendar embedding retrieval strategy (Q2)
- 🎯 Journal Assistant PoC — AI-powered personal journal for tech and non-tech users (Q3) *(see goal 5)*
- 📅 Knowledge Assistant — retrieval design + UX (Q3–Q4)
- 📅 Proactive email agent — security, permissions, prompt injection (Q4)

**Measure:** 1 spike per quarter · written outcome for each

---

## 5. Journal Assistant — PoC & Exec Approval

> First proposed extension of Personal Grounding. An AI-powered journal tool — captures thoughts, reflections, and notes for both technical and non-technical users. Proactive by design.

- 📅 Define use case and user value clearly in a brief (Q2)
- 🎯 Run PoC — prove retrieval, journaling UX, and grounding value (Q3)
- 📅 Present findings to senior leadership for approval (Q3)
- 📅 Build only after approval is secured

**Measure:** PoC completed and presented by end of Q3 · Go/no-go decision from exec before any build begins

---

## 6. Architecture Decision Records (ADRs)

- ✅ 2 ADRs authored (Q1)
- 🎯 2 more by Q2 — OCP Session Affinity · Embedding Sync design
- 📅 1 ADR per significant feature trade-off going forward

> Feature-triggered, not calendar-driven. Target: 6–8 by year end.

---

## 7. Champion Spec-Driven Development (SDD)

> Introducing OpenAPI-first engineering to the team — define the contract before writing implementation code.

- 🎯 Propose SDD as a team standard — get buy-in from team and manager (Q2)
- 🎯 Author first OpenAPI spec for a FastAPI service (Data Ingestor or Embedding Sync) as the reference example (Q2)
- 📅 Define MCP tool schemas upfront before each new tool is implemented
- 📅 SDD adopted on at least 1 H2 feature from day one

**Measure:** First spec authored and peer-reviewed by Q2 · SDD used on at least 1 H2 feature from inception

---

# Non-Technical

---

## 8. Onboarding

> Team is growing — this is immediate, not a Q4 activity.

- 🎯 Document ramp-up gaps and onboarding friction points — Q1/Q2
- 🎯 Produce onboarding guide: Personal Grounding architecture, local setup, RAG pipeline walkthrough
- 🎯 Ready to buddy the next hire when they join

**Measure:** Guide completed by end of Q2 · Used by first new joiner

---

## 9. Mentorship

- 🎯 2 mentees named by Q2 — focus: RAG pipeline + OCP deployment
- 🎯 Go-to person on team for MCP architecture
- 📅 Pair on every major feature sprint

**Measure:** 2 named mentees · 4 pairing sessions by year end

---

## 10. Sponsorship

- 🎯 1 high-potential engineer identified by Q2
- 🎯 2 visible advocacy moments — design review, demo, or tech talk

**Measure:** 1 sponsee · 2 advocacy moments by year end

---

## 11. Internal Knowledge Sharing

- 🎯 First talk by May — Personal Grounding RAG pipeline design
- 📅 Q3 talk tied to Journal Assistant PoC outcome
- 📅 Post-launch demo to Borealis leadership (June)
- 📅 1 talk per quarter

**Measure:** 4 talks by year end

---

## 12. Product Ownership

- 🎯 Drive Journal Assistant from idea → PoC → exec brief
- 🎯 Contribute to H2 roadmap — Knowledge Assistant + Proactive Agent
- 📅 1 prod usage insight → roadmap input per half

**Measure:** 1 exec brief by Q3 · named roadmap contribution per half

---

# Milestone Tracker

| Quarter | Technical | Non-Technical |
|---|---|---|
| **Q1** *(done)* | MCP built · Ingestor built · DB encrypted · PVC live · 2 ADRs | Joined Borealis |
| **Q2** | MVP to prod · Session Affinity · Calendar tool · LLM Gateway embedding · 2 ADRs · First OpenAPI spec (SDD) | First talk · 2 mentees · Sponsee · Onboarding guide |
| **Q3** | Journal PoC + exec brief · Knowledge Assistant spike · Observability proposal | Talk · Sponsorship moment · Roadmap contribution |
| **Q4** | Proactive Agent spike · Observability dashboard · Knowledge Assistant build (if approved) | Talk · Year-end retro · New hire onboarded |

---

# Measures of Success

## Vertical — Growing into Principal Engineer

| What | Done when |
|---|---|
| AI observability | Dynatrace AI dashboard live · team uses it for all new AI services |
| Session Affinity | Zero SQLite lock errors under load before May go-live |
| AI app standards | Standards doc adopted by team · applied to Journal Assistant build |
| ADR influence | At least 1 ADR cited by an engineer outside the PG team |

---

## Horizontal — Growing into AI Product Owner

| What | Done when |
|---|---|
| Roadmap ownership | Manager presents your H2 roadmap to leadership without restructuring it |
| PoC → exec approval | Journal Assistant PoC presented · go/no-go received from senior leadership |
| Product metrics | 1 roadmap or feature decision backed by prod usage data |
| Exec presence | You lead 2 exec-facing presentations · 1 senior stakeholder knows you by name |

---

## The Dual-Track Signal

> You have arrived when you are the person the team calls to decide *what to build* **and** *how to build it*.

---

*Personal Grounding AI — your context, your assistant, your data.*
*RBC Borealis · FY2026*
