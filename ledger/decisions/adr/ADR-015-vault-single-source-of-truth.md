---
id: ADR-015
title: "Governance Vault — Single Source of Truth sur DEV VPS"
status: accepted
date: 2026-04-18
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1, G2, G3, G4]
related_incidents: [2026-04-14-paybox-tunnel-sev1-ipn-blocked]
reviewed_by: ""
---

# ADR-015: Governance Vault — Single Source of Truth sur DEV VPS

## Contexte

Pendant la gestion de [[2026-04-14-paybox-tunnel-sev1-ipn-blocked|INC-2026-002]] (2026-04-14 → 2026-04-18), Claude Code tournant sur le DEV VPS (`/opt/automecanik/app`) a écrit le post-mortem complet dans le chemin `/opt/automecanik/app/.local/governance-vault/01-incidents/`.

Or ce chemin est :

1. **Gitignoré** dans le monorepo (pattern `.local/` dans `.gitignore`) → jamais versionné
2. **Local au DEV VPS** uniquement → pas de sync vers GitHub
3. **Divergent** du vrai vault `/opt/automecanik/governance-vault/` (clone de `ak125/governance-vault`) → ADRs différents, structure différente, incidents absents

Découverte 4 jours après la résolution de l'incident : **INC-2026-002 n'était visible nulle part** hors du filesystem local du DEV VPS. Aucun audit trail GitHub, aucun G1-G4 CI, aucune traçabilité pour AI-COS.

Ce n'est pas un bug isolé — c'est un gouffre structurel entre "travail produit sur DEV" et "source of truth GitHub". Il allait se reproduire à chaque incident, chaque ADR, chaque règle.

Le problème a été aggravé par le fait que le clone DEV VPS local était **16 commits en retard** sur `origin/main` lorsque la migration a été tentée (PR #7 initiale construite sur une ancêtre v1 obsolète, conflict avec la structure v2 en place).

## Décision

**Le repository `/opt/automecanik/governance-vault/` (cloné depuis `git@github.com:ak125/governance-vault.git`) est la seule source of truth pour tout document de gouvernance produit sur DEV VPS.**

Concrètement :

1. **Deprecation `.local/governance-vault/`** — le chemin `/opt/automecanik/app/.local/governance-vault/` est DEPRECATED à compter du 2026-04-18. Il sera supprimé du monorepo via PR séparée (Suivi #1) avec pre-commit hook anti-régression.
2. **Structure canonique v2** — `ledger/` (historique immuable : incidents, ADRs, audits, evidence-packs) + `ops/` (opérationnel : MOCs, rules, policies actives) + `_templates/` + `_scripts/`. Toute migration préserve cette structure.
3. **Guardrails agents** — un fichier `AGENTS.md` à la racine du vault documente le workflow obligatoire pour tout agent IA (Claude Code, Cowork, Codex). Un helper `_scripts/new-incident.sh` scaffold les nouveaux incidents dans le bon chemin.
4. **CLAUDE.md monorepo = pointer** — le `CLAUDE.md` du monorepo `nestjs-remix-monorepo` devient un pointer unique vers ce vault (Suivi #3), ne contient aucune règle dupliquée.
5. **Canon architectural inchangé** — [[rules-vault|G1]] reste applicable : le canon technique (`.spec/00-canon/` du monorepo) fait foi en cas de conflit avec le vault. Le vault reste un miroir enrichi opérationnel, non normatif.

## Options Considérées

### Option A: Direct push DEV → main

**Description**: Claude commit et push au fur et à mesure vers le vault `ak125/governance-vault` main, sans PR.

**Avantages**:
- Zéro latence entre production et SoT
- Pas de workflow supplémentaire

**Inconvénients**:
- Contourne la review humaine (violation [[rules-vault|G3]])
- Risque majeur si les clés SSH de l'agent sont compromises
- Pas de CI G1-G4 (orphans, broken-links, signatures) avant merge

### Option B: Cron sync `.local/` → PR auto

**Description**: Bot planifié (cron 1× par jour) qui batch-sync `/opt/automecanik/app/.local/governance-vault/` vers des PRs automatiques sur le vrai vault.

**Avantages**:
- Conserve le chemin `.local/` existant
- Crée des PRs reviewables

**Inconvénients**:
- Masque le problème structurel au lieu de le résoudre
- Ajoute une brique à maintenir (cron, retry, gestion erreurs)
- Conflict resolution cauchemardesque quand deux agents modifient la même MOC
- Deux structures divergentes continuent à coexister → confusion permanente

### Option C: Un seul vault, `.local/` deprecated

**Description**: `/opt/automecanik/governance-vault/` devient le seul vault. `.local/governance-vault/` est supprimé du monorepo avec hook anti-régression. Agents écrivent directement dans le canonical vault via workflow git standard (branch + PR + review + merge).

**Avantages**:
- Élimine le gap structurel au lieu de le bridger
- Un seul workflow pour humains et agents
- Commit history propre sur GitHub
- CI G1-G4 s'applique naturellement

**Inconvénients**:
- Migration one-shot nécessaire (INC-2026-002 + tout document oublié dans `.local/`)
- Formation requise : chaque session Claude Code doit lire `AGENTS.md`

### Option D: Symlink `.local/` → vrai vault

**Description**: Créer un symlink `/opt/automecanik/app/.local/governance-vault/` → `/opt/automecanik/governance-vault/`.

**Avantages**:
- Compatible avec scripts existants qui référencent `.local/`
- Changement minimal côté code

**Inconvénients**:
- `.gitignore` du monorepo s'applique au path réel du symlink → confusion sur ce qui est versionné
- Fragile sur Windows / conteneurs Docker
- Maintient l'ambiguïté "deux chemins pour la même chose"

## Justification

**Option C retenue** pour trois raisons :

1. **Simplicité structurelle** — ce qui marche pour un développeur humain (git clone, branch, PR, merge) marche pour un agent IA. Aucune brique technique à inventer.
2. **Audit trail natif GitHub** — chaque document de gouvernance hérite automatiquement de la signature commit (G3), des checks CI (G1, G2, G4), et du workflow PR review.
3. **Alignement AI-COS** — [[ADR-012-aicos-vps-architecture|ADR-012]] prévoit qu'AI-COS VPS lit l'état de gouvernance via `git clone` read-only. Avec Option C, le vault canonique est immédiatement consultable depuis n'importe quel VPS via HTTPS GitHub.

Les options A et B sont rejetées car elles ajoutent de la complexité (brique technique ou contournement de review) sans résoudre le problème de fond. Option D est rejetée car elle maintient l'ambiguïté "deux chemins, un contenu" qui est précisément la cause racine de INC-2026-002.

## Conséquences

### Positives

- Un seul chemin pour tout agent IA ou humain → zéro ambiguïté, zéro divergence
- Audit trail GitHub de toute décision (PR review, signatures ed25519, CI G1-G4)
- AI-COS VPS peut consulter l'état de gouvernance via `git clone` read-only sans accès write
- Simplicité cognitive : workflow git standard, pas de brique sync à documenter
- Détection automatique des régressions (orphelins [[rules-vault|G2]], wikilinks cassés, canon modifié sans ADR [[rules-vault|G1]])

### Négatives

- Migration one-shot nécessaire (INC-2026-002 + autres documents résiduels dans `.local/`)
- Formation agents : toute session Claude Code doit lire `AGENTS.md` avant de produire un document
- Impossibilité d'écrire hors-ligne dans le vault (requiert accès réseau pour push)
- Les 2 commits préexistants sur le DEV VPS local (`30ca884` + `e40db12`, 13 020 lignes au total) nécessitent review humaine avant portage v2 → suivi séparé (Suivi #2)

### Neutres

- Les autres chemins `.local/*` (scripts dev, configs temporaires, caches) restent gitignorés et locaux — seul `.local/governance-vault/` est concerné par cet ADR
- Le vault Obsidian côté Windows PC synchronise via `git pull --rebase` standard — pas de changement d'outil

## Critères de Succès

- [ ] **C1 — Zéro `.local/governance-vault/`** — le dossier est absent du monorepo après merge du Suivi #1
- [ ] **C2 — Hook anti-régression** — toute tentative d'ajout sous `app/.local/governance-vault/` est bloquée par `.githooks/pre-commit` du monorepo
- [ ] **C3 — INC-2026-002 visible sur GitHub** — le post-mortem est listé dans [[MOC-Incidents]] et accessible via `ledger/incidents/2026/`
- [ ] **C4 — CLAUDE.md monorepo = pointer** — le fichier ne contient aucune règle, seulement un pointer vers le vault (Suivi #3)
- [ ] **C5 — AGENTS.md présent** — fichier racine du vault, documentation workflow agents
- [ ] **C6 — Helper `new-incident.sh` fonctionnel** — exécution `_scripts/new-incident.sh critical test-slug` crée un fichier valide dans `ledger/incidents/2026/`
- [ ] **C7 — CI G1-G4 verte** — check-orphans, check-broken-links, audit-signatures, branch-protection tous en vert sur main après merge

## Implémentation

Fichiers créés par cette ADR (branche `docs/adr-015-vault-sot-migrate-inc-2026-002`) :

- `ledger/decisions/adr/ADR-015-vault-single-source-of-truth.md` (ce fichier)
- `ledger/incidents/2026/2026-04-14-paybox-tunnel-sev1-ipn-blocked.md` (migration INC-2026-002)
- `AGENTS.md` (racine vault — guardrails agents)
- `_scripts/new-incident.sh` (helper scaffold incident)
- `_templates/ci-gate-template.md`, `health-check-template.md`, `verification-template.md` (templates audit)
- Mise à jour `ops/moc/MOC-Incidents.md` (ajout ligne INC-2026-002)
- Mise à jour `ops/moc/MOC-Decisions.md` (ajout ligne ADR-015)
- Ajout frontmatter YAML à [[2026-02-03-paybox-orderid-format|INC-2026-01-30]] (alignement format v2)

Actions correctives suivant cet ADR :

- **Suivi #1** — PR monorepo `chore/remove-local-governance-vault` : `git rm -r app/.local/governance-vault/` + pre-commit hook — **Owner** : Fafa — **Deadline** : 2026-04-25 — **Status** : PR #81 ouverte
- **Suivi #2** — Review + port v2 des 2 commits préexistants DEV VPS (13 020 lignes, branche `rescue/pre-v2-content`) — **Owner** : Fafa — **Deadline** : 2026-04-30
- **Suivi #3** — Mise à jour `CLAUDE.md` monorepo : pointer unique vers `/opt/automecanik/governance-vault/` — **Owner** : Fafa — **Deadline** : 2026-04-25 — **Status** : PR #80 ouverte (à amender ADR-013 → ADR-015)
- **Suivi #4** — ADR processus Incident (template renforcé + obligations review) — **Owner** : Fafa — **Deadline** : 2026-05-15

## Revue Planifiée

**Date**: 2026-07-18 (T+3 mois)
**Critères de revue**: 
- Aucun nouveau document gouvernance écrit hors du canonical vault depuis le merge
- Hook anti-régression `.local/governance-vault/` n'a rien bloqué (preuve que tous les agents respectent le workflow) ou a bloqué uniquement des tentatives rares et documentées
- Workflow `new-incident.sh` utilisé pour au moins 1 incident réel
- AI-COS consomme effectivement le vault via `git clone` HTTPS (documenter dans audit trail)

---

*Proposé le: 2026-04-18*
*Accepté le: 2026-04-18*
*Dernière revue: 2026-04-18*
