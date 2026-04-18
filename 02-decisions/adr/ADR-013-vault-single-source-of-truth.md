---
id: ADR-013
title: Governance Vault — Single Source of Truth sur DEV VPS
status: accepted
date: 2026-04-18
version: 1.0.0
decision_makers: [owner]
supersedes: []
superseded_by: []
related_adr: [ADR-007, ADR-012]
related_rules: [R-Vault-01, R-Vault-02]
---

# ADR-013 : Governance Vault — Single Source of Truth sur DEV VPS

## Status

**ACCEPTED** — 2026-04-18

## Contexte

Pendant la gestion de **[[2026-04-14-paybox-tunnel-sev1-ipn-blocked|INC-2026-002]]** (2026-04-14 → 2026-04-18), Claude Code tournant sur DEV VPS (`/opt/automecanik/app`) a écrit le post-mortem complet dans le chemin `/opt/automecanik/app/.local/governance-vault/01-incidents/`.

Or ce chemin est :
1. **Gitignoré** dans le monorepo (pattern `.local/` dans `.gitignore`) → jamais versionné
2. **Local au DEV VPS** uniquement → pas de sync vers GitHub
3. **Divergent** du vrai vault `/opt/automecanik/governance-vault/` (repo cloné depuis `ak125/governance-vault`) → ADR différents, structure différente, incidents absents

Découverte 4 jours après la résolution de l'incident : **INC-2026-002 n'était visible nulle part** hors du filesystem local du DEV VPS. Aucun audit trail, aucun G1-G4 CI, aucune traçabilité pour AI-COS.

**Ce n'est pas un bug isolé** — c'est un gouffre structurel entre "travail produit sur DEV" et "source of truth GitHub". Il allait se reproduire à chaque incident, chaque ADR, chaque règle.

### Options étudiées

| Option | Principe | Verdict |
|---|---|---|
| **A — Direct push DEV→main** | Claude commit/push au fur et à mesure vers le vault | ❌ Contourne PR review, risque si clés SSH compromises |
| **B — Cron sync `.local/`→PR auto** | Bot batched sync depuis `.local/` | ❌ Masque le problème, ajoute une brique à maintenir, conflict resolution cauchemar |
| **C — Un seul vault, `.local/` deprecated** | `/opt/automecanik/governance-vault/` = le vrai repo cloné, agents écrivent dedans | ✅ **RETENU** — enlève le gap au lieu de le bridger |
| **D — Symlink `.local/` → vrai vault** | Lien symbolique | ❌ Fragile (gitignore s'applique au path réel, confusion permanente) |

## Décision

### 1. Source of truth unique

Le repo **`/opt/automecanik/governance-vault/`** (cloné depuis `git@github.com:ak125/governance-vault.git`) est **la seule** source of truth pour tout document de gouvernance produit sur DEV VPS.

### 2. Deprecation `.local/governance-vault/`

Le chemin `/opt/automecanik/app/.local/governance-vault/` est **DEPRECATED** à compter du **2026-04-18**. Il sera :
- **Migré** : les documents présents (incidents, MOC) sont copiés dans le canonical vault sur une branche de migration
- **Archivé** : snapshot pris dans `04-audit-trail/_archive/dev-local-vault-snapshot-20260418/`
- **Supprimé** du monorepo dans une PR séparée (`chore/remove-local-governance-vault`)

### 3. Guardrails

- Un fichier `AGENTS.md` à la racine du vault canonique documente le workflow obligatoire pour tout agent
- Un helper `scripts/new-incident.sh` scaffold les nouveaux incidents dans le bon chemin
- Un pre-commit hook côté monorepo (follow-up, voir Actions Correctives) bloquera toute modif dans `app/.local/governance-vault/*`

### 4. Canon architectural — inchangé

R-Vault-01 reste applicable : le **canon technique** (`/opt/automecanik/app/.spec/00-canon/`) fait foi en cas de conflit avec le vault. Le vault reste un miroir enrichi **opérationnel**, non normatif.

## Conséquences

### Positives

- **Un seul chemin** pour tout agent → zéro ambiguïté, zéro perte
- **Audit trail GitHub** de toute décision (PR review, signatures, CI)
- **AI-COS VPS** (voir [ADR-012](ADR-012-aicos-vps-architecture.md)) peut lire l'état de gouvernance via `git clone` du vault
- **Simplicité** : ce qui marche pour un dev (workflow git standard) marche pour un agent

### Négatives / Risques

- **Migration one-shot** nécessaire : 3 documents dans `.local/` à recréer dans le canonical vault (INC-2026-002, snapshot MOC, archives éventuelles)
- **2 commits non-pushés** préexistants sur la branche `main` du canonical vault (10 790 lignes) à pousser après review humaine séparée — non couverts par cet ADR
- **Formation agents** : toute session Claude Code doit lire `AGENTS.md` avant de produire un document de gouvernance

### Neutres

- Les autres chemins `.local/*` (scripts dev, configs temporaires) restent gitignorés — seul `.local/governance-vault/` est concerné par cet ADR

## Actions Correctives

- [x] Migrer INC-2026-002 vers canonical vault — **Owner** : @automecanik.seo — **Deadline** : 2026-04-18 — **Status** : ✅ FAIT (cette PR)
- [x] Mettre à jour `00-index/MOC-Incidents.md` canonical — **Owner** : @automecanik.seo — **Deadline** : 2026-04-18 — **Status** : ✅ FAIT (cette PR)
- [x] Créer `AGENTS.md` — **Owner** : @automecanik.seo — **Deadline** : 2026-04-18 — **Status** : ✅ FAIT (cette PR)
- [x] Créer helper `scripts/new-incident.sh` — **Owner** : @automecanik.seo — **Deadline** : 2026-04-18 — **Status** : ✅ FAIT (cette PR)
- [ ] **Suivi #1** — PR séparée monorepo `chore/remove-local-governance-vault` : `git rm -r app/.local/governance-vault/` + pre-commit hook — **Owner** : @automecanik.seo — **Deadline** : 2026-04-25
- [ ] **Suivi #2** — Review + push des 2 commits préexistants (`30ca884` + `e40db12`) sur `ak125/governance-vault` main — **Owner** : @automecanik.seo — **Deadline** : 2026-04-25
- [ ] **Suivi #3** — Mise à jour `CLAUDE.md` monorepo : section Governance Vault → pointer uniquement vers `/opt/automecanik/governance-vault/` — **Owner** : @automecanik.seo — **Deadline** : 2026-04-25
- [ ] **Suivi #4** — ADR-014 sur processus Incident (template + helper + obligations review) — **Owner** : @automecanik.seo — **Deadline** : 2026-05-15

## Références

- Incident déclencheur : [[../../01-incidents/2026/2026-04-14-paybox-tunnel-sev1-ipn-blocked|INC-2026-002]]
- [ADR-007 : Location Independence](ADR-007-location-independence.md)
- [ADR-012 : AI-COS VPS Architecture](ADR-012-aicos-vps-architecture.md)
- R-Vault-01 : Canon fait foi (voir `README.md`)
- R-Vault-02 : Zéro orphelin (voir `README.md`)

---

*Créé le : 2026-04-18*
*Owner : @automecanik.seo*
