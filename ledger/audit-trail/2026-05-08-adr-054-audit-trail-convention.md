---
title: "ADR-054 audit-trail convention shipped 2026-05-08 (auto-application méta)"
date: 2026-05-08
type: session-trail
related_chantier: governance
related_adr: ["ADR-054"]
related_moc: ["MOC-Decisions", "MOC-AuditTrail"]
related_prs:
  - "ak125/governance-vault#TBD"  # vault PR feat/adr-054-audit-trail-convention
status: shipped
session_closed_at: 2026-05-08
---

# ADR-054 — Convention governance standard audit-trail vault par défaut sur ADR

> **Statut** : shipped 2026-05-08 — vault PR ouverte, ADR-054 status `accepted` directement.
> **Méta** : cet audit-trail applique la convention qu'il documente. Première application empirique d'ADR-054.

## Synthèse

Formalisation de la convention « tout ADR vault destiné au merge → audit-trail vault par défaut dans la même session ». Inversion d'opt-in (demande explicite utilisateur) en opt-out (par défaut + dérogation documentée). Pattern de facto déjà observé sur 16+ sessions 2026-05-08 — l'ADR codifie l'existant, ne crée pas une nouvelle exigence.

## Drivers empiriques

1. **Risque d'oubli structurel** observé : ADRs livrés sans audit-trail si l'utilisateur oublie de demander. Mémoire institutionnelle (drivers, itérations critique, drift) perdue.
2. **Couplage logique ADR ↔ audit-trail inséparable** : la décision canon et la trace de session sont 2 artefacts complémentaires d'une même action.
3. **Pattern de facto déjà universel** : 16+ entrées audit-trail créées pour 2026-05-08 seul (cf MOC-AuditTrail.md chronologie). Manque uniquement la formalisation canonique.
4. **Inversion conceptuelle** : convention par défaut + dérogation documentée = aligné philosophie observatory (ADR-030), anti-bureaucratique.

## Itérations plan (5 cycles utilisateur critique)

| Version | Critique utilisateur | Correction |
|---|---|---|
| v1 | Trigger trop restrictif "ADR + PR monorepo" | Trigger = ADR seul, indépendamment des artefacts annexes (PR monorepo, PR vault, issue, follow-up) |
| v1 | "obligatoire" trop fort dans système sans enforcement runtime | "Convention governance standard" + "deviation requires explicit opt-out rationale" — aligné ADR-030 observatory philosophy |
| v1 | Memory feedback risque devenir 2nde SoT | Frontmatter explicite "Source of truth: ADR-054. This memory operationalizes but does not redefine." |
| v1 | Invariant MOC-AuditTrail non vérifié | Ajout invariant explicite + distinction enforcement réel (G2 zero-orphan strict) vs convention déclarative (MOC-AuditTrail link) |
| v1 | "Convention LIVE" imprécis | Séparé en (a) Canon LIVE = merge ADR-054 accepted, (b) Operational effectiveness = 3-4 sessions consécutives sans rappel |
| v2 | "pre-commit blocked" overclaim sans vérif G2 | Vérification empirique `_scripts/check-orphans.sh` : G2 = zero-orphan check générique, pas MOC-AuditTrail-specific. Reformulation rigoureuse. |
| v2 | "ADR éditorial sans session significative" trop vague | Remplacé par "ADR metadata/editorial maintenance only — non-decision-bearing editorial amendment (typo, wording, frontmatter, link, compliance refs)" |

## Livrables

### Vault canon
- `ledger/decisions/adr/ADR-054-audit-trail-on-adr-convention.md` — ADR status `accepted` directement (pas de phase observatoire pour la règle, pattern de facto observé).
- `ops/moc/MOC-Decisions.md` — entrée ADR-054 ajoutée après ADR-053.
- `ledger/audit-trail/2026-05-08-adr-054-audit-trail-convention.md` — cet audit-trail (auto-application méta de la convention).

### Memory DEV (PR follow-up commit)
- `home/deploy/.claude/projects/-opt-automecanik-app/memory/feedback_auto_vault_audit_trail_on_adr.md` — operationalization Claude DEV.
- `home/deploy/.claude/projects/-opt-automecanik-app/memory/MEMORY.md` — index pointer.

## Distinction enforcement réel vs convention déclarative

Vérification empirique `_scripts/check-orphans.sh` :
- **Gate G2 effectif** = zero-orphan check générique. Bloque tout `.md` orphelin strict (zéro référent wikilink depuis n'importe quel autre `.md` du vault, hors exclusions MOC/_assets/_templates/_scripts/etc.).
- **Convention MOC-AuditTrail link** = discoverability discipline déclarative dans cet ADR. **Pas un gate distinct aujourd'hui**.
- **Conséquence pratique** : un audit-trail référencé seulement depuis l'ADR (sans MOC-AuditTrail link) passera G2 actuel mais violera la convention. Extension G2 → "audit-trail must reference MOC-AuditTrail spécifiquement" reste follow-up potentiel si signal empirique justifie.

## Opt-out terms précis (vs vague "session significative")

Dérogations valides avec rationale documentée :
- **revert** : commit qui annule un précédent
- **exploratoire abandonné** : branche jamais mergée
- **draft non destiné au vault** : work-in-progress
- **ADR metadata/editorial maintenance only** : *non-decision-bearing editorial amendment* — typo, wording, frontmatter, link update, compliance refs. Pas de nouvelle décision substantive.

## Verdict empirique CI local

- Pre-commit G2 : **PASS** (0 orphan, 0 broken wikilink). ADR-054 référencée MOC-Decisions, audit-trail référencé MOC-AuditTrail (à ajouter dans le commit suivant).

## Hors scope (volontaire — documenté ADR-054)

- **Skill `vault-audit-trail-writer` dédié** : direction architecture future alignée AI-COS observatory. Reporté post-validation 3-4 sessions sous convention manuelle + memory feedback.
- **Extension G2 → MOC-AuditTrail-specific** : possible mais pas nécessaire aujourd'hui. Convention déclarative + memory feedback suffisent.
- **Hook pre-commit vault** détectant commit ADR sans audit-trail dans la même branche : possible mais ajoute friction CI. Préférer discipline canon + memory + gate G2 indirect.

## Forward-compat

Cette convention canonique est universelle (humains + agents). Operationalization Claude DEV via memory feedback. Pour les autres contributeurs (humains, autres agents), l'ADR-054 sert de référence déclarative + le pattern de facto déjà observé continue.

## Suite (post-merge)

1. Memory feedback DEV créé dans le commit suivant (même branche).
2. Canon LIVE dès merge ADR-054 vault accepted dans `main`.
3. Operational effectiveness validée empiriquement après 3-4 sessions consécutives sans rappel explicite utilisateur.
4. Si memory feedback inactif sur 2+ sessions consécutives, debug : memory file présent ? auto-loadé via MEMORY.md ? frontmatter OK ?
