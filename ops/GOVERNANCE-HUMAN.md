# GOVERNANCE-HUMAN.md  
## Human Authority & Zero-Trust Agents Doctrine

**System:** AutoMecanik  
**Status:** ACTIVE – SOURCE OF TRUTH  
**Author:** Human (Owner / Operator)  
**Scope:** Global – applies to ALL systems, agents, repositories, and environments  
**Last update:** 2026-03-07  

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
| **External** | Claude API, local machines, external VPS | Read-only + bundle generation |
| **Principal VPS** | Governance & Airlock authority | Validation only |
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
- ✅ may ONLY submit **candidates**

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

---

## 6. Airlock Principle

### RULE-H6 — Airlock Is Mandatory

Any modification proposed by an agent MUST pass through:

