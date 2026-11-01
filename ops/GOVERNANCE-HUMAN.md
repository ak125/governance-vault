# GOVERNANCE-HUMAN.md  
## Human Authority & Zero-Trust Agents Doctrine

**System:** AutoMecanik  
**Status:** ACTIVE – SOURCE OF TRUTH  
**Author:** Human (Owner / Operator)  
**Scope:** Global – applies to ALL systems, agents, repositories, and environments  
**Last update:** 2026-10-01 (RULE-H3 to H6 aligned with ADR-102)  

---

## 0. Purpose (WHY THIS FILE EXISTS)

This document defines the **ultimate authority model** of the AutoMecanik system.

Its purpose is to:
- Prevent any ambiguity about **who decides**
- Enforce **Zero-Trust for all automated agents**
- Provide a **human-written constitutional layer** above ADRs, agents, tools, and CI
- Act as the **final arbitration reference** in case of conflict

> **This file overrides any other document, prompt, agent behavior, or automation.**

---

## 1. Supreme Authority Rule

### RULE-H0 — Human Supremacy (NON-NEGOTIABLE)

The **human operator** is the **only authority** empowered to:
- Define governance rules
- Approve or reject architectural decisions
- Activate or deactivate agents
- Authorize writes to critical systems
- Decide what is production-safe

No AI agent, automation, or tool may override, reinterpret, or weaken this authority.

---

## 2. Zero-Trust Agents Doctrine

### RULE-H1 — Agent ≠ Authority

All agents are considered **NON-TRUSTED by default**, regardless of:
- Their location (local, VPS, cloud, CI)
- Their purpose (analysis, code, governance, security)
- Their perceived intelligence or reliability
- Their access level or configuration

> **Trust is never granted to an agent.  
> Trust is granted only to a verifiable process.**

---

### RULE-H2 — Location Independence

An agent’s **physical or logical location** does NOT increase its trust level.

An agent running:
- on the principal VPS
- inside CI
- with repository access
- with secrets or tokens

…is still treated as **NON-TRUSTED** until its output passes governance gates.

(Location ≠ Authority)

---

## 3. Zones of Execution

### RULE-H3 — Execution Zones

The system is strictly divided into zones:

| Zone | Description | Agent Rights |
|----|----|----|
| **External** | Claude API, local machines, external VPS | Read-only + pull request preparation (RULE-H6) |
| **Principal VPS** | Governance authority, RPC gate ("Airlock", ADR-003) | Validation only |
| **Production** | Runtime execution | ❌ NO AGENTS ALLOWED |

> **No AI agent is allowed to execute in Production. Ever.**

---

## 4. Writing Rules (Critical)

### RULE-H4 — Single Point of Write Authority

Only the **principal VPS + human-approved workflows** may write to:

- Production monorepo
- Governance vault
- Canonical specifications

Agents:
- ❌ must NOT commit directly
- ❌ must NOT push to production repositories
- ❌ must NOT modify governance rules
- ✅ may ONLY submit **candidates**: a pull request (RULE-H6)

---

## 5. Canonical Truth

### RULE-H5 — Canon Is Sacred

The following are **read-only for agents**:

- `.spec/00-canon/**`
- `governance-vault/**`
- ADRs
- Rules
- Audit trails

Any change to canon or governance:
- MUST be proposed
- MUST be reviewed by a human
- MUST be committed manually

For an agent, *read-only* means it never writes to the default branch of these
repositories. It may prepare a pull request (RULE-H6), unless the target
repository reserves the path to the owner; the human merge is the manual commit.
(Clarified by ADR-102.)

---

## 6. Agent Proposal Channel

### RULE-H6 — Agent Proposals Go Through a Pull Request

Any modification proposed by an agent MUST pass through:

1. A branch and a pull request on the target repository, with signed commits
   where that repository requires them
2. The required checks of that repository
3. Review and merge by a human

An agent never merges, including its own pull request.

"Airlock" now designates the RPC gate only (ADR-003). The bundle channel
(bundle → agent-submissions → Airlock) is retired.

> This rule was truncated mid-sentence from the creation of this file
> (commit `607ac42`). It was completed by ADR-102.
