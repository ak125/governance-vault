---
adr: 054
title: Convention governance standard — audit-trail vault par défaut pour toute session ADR
status: accepted
date: 2026-05-08
deciders: Fafa (owner)
tags:
  - governance
  - vault
  - audit-trail
  - convention
related:
  - ADR-030  # Observatory progressive enforcement philosophy
  - ADR-046  # Canon roles & contracts (L1.5 CONTRACTS extension)
  - ADR-053  # Planning Live System (audit-trail referencé MOC-AuditTrail pattern)
---

# ADR-054 — Convention governance standard : audit-trail vault par défaut sur ADR

## Status

**accepted** 2026-05-08 — convention de gouvernance, pas de phase observatoire pour la règle elle-même : pattern de facto déjà observé sur 16+ sessions 2026-05-08 (cf `MOC-AuditTrail.md` chronologie). Canon LIVE dès merge dans `main`.

## Context

### Pattern observé

Chaque session significative produit un ADR vault + un audit-trail vault qui documente la session ayant produit l'ADR. Parfois aussi PR monorepo, PR vault uniquement, issue GitHub, ou follow-up différé.

L'audit-trail dépend cependant d'une **demande explicite utilisateur** (« consigne dans vault », « ajoute audit-trail »). Cette dépendance crée :

- **Risque d'oubli structurel** : ADR existe sans trace de session si l'utilisateur oublie. Mémoire institutionnelle perdue (drivers empiriques, itérations critique, drift détecté = invisibles).
- **Couplage logique non formalisé** : ADR documente la décision canon, audit-trail documente la session. Les deux forment un couple inséparable. Sans audit-trail = décision orpheline de contexte.
- **Inversion d'opt-in vs opt-out** : convention de facto déjà universelle (16+ sessions 2026-05-08), mais opt-in (demande explicite) au lieu d'opt-out (par défaut + dérogation).

### Pourquoi pas couplage avec PR monorepo

Une définition restrictive « ADR + PR monorepo → audit-trail » crée des trous de gouvernance pour :
- ADR vault sans PR monorepo associée (pure governance)
- ADR + PR vault uniquement (refactor structure vault)
- ADR + issue GitHub (decision pending external action)
- ADR + follow-up différé (decision now, implementation later)
- ADR + commit isolé (hotfix)

Le trigger doit être l'**ADR seul**.

## Decision

Convention governance standard :

> Toute session produisant **un ADR vault destiné au merge** (status `proposed | accepted`) **livre par défaut** un audit-trail vault dans la même session, sauf **opt-out explicite avec rationale documenté**.

### Champs frontmatter audit-trail

```yaml
---
title: "..."
date: YYYY-MM-DD
type: session-trail
related_adr: ["ADR-NNN"]    # requis (1+ ADR)
related_prs: [...]            # optionnel
related_issues: [...]         # optionnel
related_commits: [...]        # optionnel
status: open | shipped | closed   # requis
---
```

### Invariant déclaratif (discoverability)

Every audit-trail entry **SHOULD** be referenced from `ops/moc/MOC-AuditTrail.md` using the same discoverability discipline as ADRs in MOC-Decisions.md.

### Distinction enforcement réel vs convention déclarative

| Mécanisme | Portée | Aujourd'hui |
|---|---|---|
| **Gate G2 effectif** (`_scripts/check-orphans.sh`) | Bloque tout `.md` orphelin strict (zéro référent wikilink depuis n'importe quel autre `.md` du vault) | LIVE |
| **Convention MOC-AuditTrail link** | Discoverability discipline alignée MOC-Decisions ↔ ADRs | Déclarative dans cet ADR-054, **pas un gate distinct aujourd'hui** |
| **Extension G2 → MOC-AuditTrail-specific** | Bloquer audit-trails non référencés depuis MOC-AuditTrail spécifiquement | Follow-up potentiel si signal empirique justifie |

Conséquence pratique : un audit-trail référencé seulement depuis l'ADR (sans MOC-AuditTrail link) **passera G2 actuel** mais violera la convention déclarative de cet ADR.

### Opt-out explicite

Dérogations valides avec rationale documentée dans le commit ou la PR :

- **revert** : commit qui annule un précédent
- **exploratoire abandonné** : branche jamais mergée
- **draft non destiné au vault** : work-in-progress
- **ADR metadata/editorial maintenance only** : *non-decision-bearing editorial amendment* — typo, wording, frontmatter, link update, compliance refs. Pas de nouvelle décision substantive.

Deviation requires explicit opt-out rationale. Opt-out silencieux = violation de convention.

## Rationale

- **Couplage logique** : ADR = décision canon, audit-trail = trace de session. Couple inséparable indépendamment des artefacts annexes (PR, issue, commit).
- **Discipline mécanique cohérente** : gate G2 force ADR ∈ MOC-Decisions ; audit-trail ∈ MOC-AuditTrail = même logique de découvrabilité.
- **Mémoire institutionnelle** : drivers empiriques, itérations critique, drift détecté ne se reconstruisent pas a posteriori. Consigner pendant que le contexte est frais = robustesse.
- **Alignement philosophie observatory** (ADR-030) : pas d'enforcement automatique runtime, convention par défaut + opt-out documenté = anti-bureaucratique.

## Consequences

### Positives

- Mémoire institutionnelle préservée systématiquement, indépendamment des artefacts annexes.
- Reviewer canon a toujours le contexte session disponible (drivers, itérations, drift).
- Pattern aligné `feedback_decision_must_be_signal_proven_not_intuited` (signaux session conservés pour pilotage empirique futur).

### Négatives / risques

- Charge marginale ~5 min/session pour rédiger l'audit-trail.
- Discipline déclarative sans enforcement runtime spécifique. Drift possible si convention oubliée. Mitigation triple :
  1. Memory feedback DEV (Claude sessions) — `feedback_auto_vault_audit_trail_on_adr.md` opérationnalise la règle dans mes sessions futures.
  2. Gate G2 effectif bloque audit-trail orphelin strict (zéro référent wikilink).
  3. Convention "référence depuis MOC-AuditTrail" reste discoverability discipline non-gateée — extension G2 follow-up potentiel.

## Compliance

- ADR-030 — philosophie observatory progressive enforcement.
- ADR-046 § L1.5 CONTRACTS — extension du canon governance.
- `feedback_canon_rule_live_iff_adr_accepted` — règle Canon LIVE dès merge `accepted`.

## Operationalization

Cette ADR documente la **règle canonique** (déclarative, universelle aux humains et agents). Son opérationnalisation côté Claude DEV passe par memory feedback :

- `home/deploy/.claude/projects/-opt-automecanik-app/memory/feedback_auto_vault_audit_trail_on_adr.md`
- Auto-loadé dans MEMORY.md → mes sessions futures appliquent la convention sans demande explicite.
- Memory **operationalizes** la convention mais ne la **redéfinit pas** : ADR-054 reste l'unique source of truth. En cas d'évolution, amender ADR-054 d'abord, memory mise à jour ensuite.

## Operational effectiveness validation

À distinguer du Canon LIVE (= règle vault appliquée immédiatement après merge accepted) :

- **Operational effectiveness** = memory feedback DEV fait son travail dans mes sessions sans rappel utilisateur.
- Critère : 3-4 sessions consécutives produisant un ADR vault avec audit-trail livré sans rappel explicite.
- Si memory feedback inactif sur 2+ sessions consécutives, debug : memory file présent ? auto-loadé via MEMORY.md ? frontmatter OK ?

## Follow-ups

- **Skill `vault-audit-trail-writer` dédié** : direction architecture future alignée AI-COS observatory (templates, extraction semi-auto PRs/ADR refs/issues/commits/evidence packs). Reporté post-validation 3-4 sessions sous convention manuelle + memory feedback. Si signal empirique justifie l'automatisation, PR dédiée.
- **Extension G2** → "audit-trail must reference MOC-AuditTrail spécifiquement" : possible mais pas nécessaire aujourd'hui (convention déclarative suffit + memory feedback opérationnalise).
- **Hook pre-commit vault** détectant commit ADR sans audit-trail dans la même branche : possible mais ajoute friction CI. Préférer discipline canon + memory + gate G2 indirect.

## Self-review verdict: APPROVE
