# GOVERNANCE-HUMAN.md  
## Human Authority & Zero-Trust Agents Doctrine

**System:** AutoMecanik  
**Status:** ACTIVE – SOURCE OF TRUTH  
**Author:** Human (Owner / Operator)  
**Scope:** Global – applies to ALL systems, agents, repositories, and environments  
**Last update:** 2026-11-07 (RULE-H5 and H6 completed by ADR-123: conditional automatic merge execution)  

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

"Reviewed by a human" means the owner's decision to adopt the change (ADR-121
D2). For a change carried by an ADR, its proof is the ratification commit on the
pull request head that the owner then merges (ADR-121 D7); for any other change,
it is the owner's merge of the pinned head, recorded per ADR-121 D4. The merge
remains a separate act, even where it serves as that proof (ADR-121 D4). The
review of the diff is the DoD2 review record bound to the head SHA (ADR-120): it
is a condition of that decision, not a substitute for it. (Clarified by ADR-121.)

Within a perimeter explicitly adopted and then activated under ADR-123, the merge
may be executed automatically, on the conditions of ADR-123 D2 to D6. The
decision stays human and no longer rests on the merge: a prior category
authorization in an approved policy for an ordinary change, or the human adoption
of the content, traced before the merge, for a governance decision (for an ADR,
its ratification commit, ADR-121 D7; for any other change, in the form the
activated perimeter sets). The record keeps the authorization, the merged head,
the executing account and the result. Until a perimeter is adopted and then
activated, the two paragraphs above apply without exception; within it, the
manual commit required above is that traced human adoption, not the merge.

---

## 6. Agent Proposal Channel

### RULE-H6 — Agent Proposals Go Through a Pull Request

Any modification proposed by an agent MUST pass through:

1. A branch and a pull request on the target repository, with signed commits
   where that repository requires them
2. The required checks of that repository
3. The DoD2 review record of the head, then the owner's decision and merge
   (RULE-H5; ADR-121), or, within a perimeter explicitly adopted and then
   activated under ADR-123, the automatic execution of the authorized decision

An agent never merges, including its own pull request. Within a perimeter
explicitly adopted and then activated under ADR-123, the merge is executed by the
activated mechanism on an authorized decision, never on an agent's own decision.

Self-review, independent review, a ticked box, green checks, a label or a
general "go" are conditions of a merge; none of them authorizes it. An agent
never runs a merge command and never enables auto-merge, under any account,
the owner's included: it hands the owner the pull request number, the head SHA
(40 characters) and the merge command pinned to that SHA. A merge record
distinguishes the human who decides, the merged SHA and the technical account
that executes; the account alone does not prove the human. (ADR-121 D3-D4.)
Within a perimeter adopted and then activated under ADR-123, the mechanism, the
executing account and the act that arms it are those fixed by the activated
perimeter (ADR-123 D2 to D6). Until a perimeter is adopted and then activated,
this paragraph applies without exception.

"Airlock" now designates the RPC gate only (ADR-003). The bundle channel
(bundle → agent-submissions → Airlock) is retired.

> This rule was truncated mid-sentence from the creation of this file
> (commit `607ac42`). It was completed by ADR-102.
