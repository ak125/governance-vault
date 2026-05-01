---
title: "Session 2026-05-01 — verifier-en-profondeure rev 1→10 + P0/P3 execution"
date: 2026-05-01
type: session-trail
related_adrs: ["ADR-031", "ADR-033"]
related_prs:
  - "ak125/automecanik-raw#10"
  - "ak125/automecanik-wiki#14"
  - "ak125/nestjs-remix-monorepo#260"
  - "ak125/nestjs-remix-monorepo#261"
status: closed
session_closed_at: 2026-05-01
final_status: SCOPE_SCANNED
---

# Session 2026-05-01 — verifier-en-profondeure-ces-async-pie + P0/P3 execution

## Résumé

Audit factuel des claims utilisateur sur l'état des 4 repos canon
(`automecanik-raw`, `automecanik-wiki`, `nestjs-remix-monorepo`,
`governance-vault`), suivi de l'exécution disciplinée des priorités P0/P3
identifiées. Plan local rédigé en 10 révisions itératives sous correction
utilisateur stricte « pas de bricolage ».

**4 PRs mergées, 0 fail CI au moment du merge**, ~520 LOC modifiés au total. Deploy DEV main post-merge PR #261 encore en cours au moment de cette consignation (cf. `remaining_unknowns` du coverage manifest).

## Audit initial — corrections apportées aux claims user

| Claim user | Verdict | Preuve |
|---|---|---|
| « PR #7 raw introduit `regen-manifests.py` mais n'est pas encore sur main » | ❌ FAUX | `gh pr list --state all` ⇒ PR #7 **MERGED** ; `regen-manifests.py` déjà sur main, `raw-checksum-verify.yml:42` l'appelle déjà en bloquant |
| « PR #8 raw ajoute `gates.py` runner AEC unifié » | ⚠️ CORRECTION | PR #8 **CLOSED** (pas en attente) ; remplacée par PR #9 mergée avec `gates.py` Gates A/B/D/E |
| Wiki `quality-gates.py` 11 checks bloquants | ✅ VERIFIED | Lignes 437-450, 1 warning (pollution), 11 failures |
| Monorepo `SupabaseBaseService` READ_ONLY + circuit breaker + sémaphore + RpcGate | ✅ VERIFIED | `backend/src/database/services/supabase-base.service.ts:87,114-120,15-75,25-60,162-216,447-507` |
| Vault `vault-weekly-lint.yml` cron Mon 02:00 UTC + diff artefacts | ✅ VERIFIED | `.github/workflows/vault-weekly-lint.yml:4` |

## Itérations du plan (rev 1 → rev 10)

| Rev | Modification clé | Trigger |
|---|---|---|
| 1 | Audit initial, 4 verdicts par repo | Demande user |
| 2 | Feuille de route P0-P3 corrigée (PR #7 mergée, pas open) | Découverte audit |
| 3 | 3 ajustements user : Gate C quarantine ≠ tombstones, Gate D cross-repo, P3 split Phase 1/1bis | Correction user |
| 4 | Section technique anti-bricolage (7 principes + patterns par gate) | Demande user « meilleure approche pas de bricolage » |
| 5 | 2 corrections : Gate A versionné v1/v2, séparation P0 Gate D vs P1 enforcement | Correction user |
| 6 | 6 corrections additionnelles : Gate D côté wiki, exemptions repo path, JSON Schema canon, signed commits enforcement, by_symptom unique, branch naming + tests | Mes propres améliorations validées |
| 7 | Découverte bloquante : raw privé sur GitHub free → branch protection 403 | Vérification Étape 0 |
| 8 | Option D retenue : différer enforcement signed commits | Choix user |
| 9 | Découverte PR #9 raw mergée → P0a réduit ~150 LOC (extension, pas runner from scratch) | Vérification post-plan |
| 10 | Découverte PR #13 wiki mergée → P0b réduit ~80 LOC (workflow uniquement, pas validateur) | Vérification post-plan |

## PRs livrées

### P0a — `automecanik-raw#10` — `229ace3`

`feat(raw): add inventory_complete gate (Gate C) + externalize exemptions to manifests/exemptions.yaml`

- Ajout `gate_inventory_complete()` dans `_scripts/gates.py` (existant via PR #9)
- `manifests/exemptions.yaml` + `_schemas/exemptions.schema.json` (JSON Schema 2020-12)
- 9 tests unittest stdlib (pas de pytest dep)
- Pre-commit hook trigger pattern étendu
- +394 / -33, 6 fichiers
- CI : 2/2 PASS Python 3.11+3.12

### P0b — `automecanik-wiki#14` — `443a8fd`

`feat(ci): add cross-repo-source-catalog-gate workflow (CI wire-up for P2 gate)`

- Workflow `.github/workflows/cross-repo-source-catalog-gate.yml`
- Détection conditionnelle PAT (`steps.pat_check`) — skip+warn si secret absent, exit 0
- Délègue à `quality-gates.py --all` canon (gate métier déjà mergé via wiki PR #13)
- +80 / 0, 1 fichier
- CI : 4/4 PASS

### P3 Phase 1 — `nestjs-remix-monorepo#260` — `82ddf001`

`chore(dep-cruiser): promote 5 zero-violation rules from warn to error (Phase 1 partial)`

- 5 règles promotes après audit confirmant 0 violation chacune :
  `not-to-deprecated`, `frontend-not-to-backend-src`, `backend-not-to-frontend`,
  `not-to-test`, `not-to-spec`
- Pas d'allowlist (0 violation à exclure)
- +24 / -13, 1 fichier
- CI : 16/16 PASS dont `🛡️ Deterministic gates` 2m33s

### P3 Phase 1 bis — `nestjs-remix-monorepo#261` — `3e7a0bf`

`chore(deps): declare 3 phantom deps + promote no-non-package-json to error (Phase 1 bis)`

- Audit a révélé que les 3 violations `no-non-package-json` étaient des **vrais bugs phantom deps** (transitive accidents), pas des exceptions légitimes
- Fix root cause : déclaré `file-type@^20.4.1` dans `backend/package.json`, `@radix-ui/react-collapsible@^1.1.12` + `cookie@^0.7.2` dans `frontend/package.json`
- `npm install --package-lock-only` pour update lockfile (3 lignes ajoutées)
- Règle promue à error sans allowlist
- +15 / -4, 4 fichiers
- CI post-merge : Audit gates Phase 0 PASS

## Découvertes structurelles anti-bricolage

### 1. PR #9 raw + PR #13 wiki déjà mergées

L'audit Explore initial avait listé uniquement les 8 premières PRs. PR #9 raw
(`gates.py` AEC-unified runner) et PR #13 wiki (`gate_source_catalog_raw_refs`)
étaient mergées et livraient l'essentiel de la logique métier P0a et P0b.

**Impact scope** :
- P0a passé de ~500 LOC (runner from scratch) à ~150 LOC (extension Gate C + exemptions YAML)
- P0b passé de ~300 LOC (validateur pydantic v2 + dual checkout + script Python) à ~80 LOC (workflow YAML uniquement)

**Leçon canonisée** dans la mémoire personnelle de l'agent (espace
`~/.claude/projects/-opt-automecanik-app/memory/feedback_check_merged_prs_before_planning.md`,
non versionnée vault) — `gh pr list --state merged --limit 20 --repo <repo>`
AVANT de scoper toute PR sur un repo canon.

### 2. Étape 0 P0a bloquée — raw privé sur GitHub free

`automecanik-raw` est le seul repo canon en privé. Sur compte GitHub free,
branch protection API renvoie HTTP 403 → `required_signatures: true`
non-enforce côté serveur.

**Décision retenue (Option D)** : différer l'enforcement signed commits, démarrer
P0a sans bloquer. G3 sur `tombstones.json` reste demandée (convention) mais
non enforce serveur. Dette tracée en section "Follow-up différés" du plan rev 8.

**4 options évaluées** :
- A — Rendre raw public (audit `recycled/` 312M préalable nécessaire)
- B — Upgrade GitHub Pro (~4 €/mois)
- C — Enforcement alternatif (hook pre-commit + CI verify-commit, fragile)
- D — Différer (retenu)

### 3. Phantom deps P3 Phase 1 bis = vrais bugs

Les 3 violations `no-non-package-json` (file-type, @radix-ui/react-collapsible,
cookie) auraient pu être allowlistées comme « exceptions légitimes ». Audit a
révélé qu'elles n'étaient déclarées dans aucun `package.json` (root, backend,
frontend) — elles marchaient uniquement par transitive accident.

**Anti-bricolage discipline** : rejeter le pattern « ajouter `forbidden.exceptions[]` »
qui aurait masqué la dette. Fix root cause = déclarer les 3 packages dans les
`package.json` corrects. Plus aucune violation à exclure → règle promotée
proprement.

## Setup user offline restant

Pour activer P0b en mode enforce (au lieu de skip+warn actuel) :

1. Créer fine-grained PAT sous https://github.com/settings/personal-access-tokens
   - Resource owner : `ak125`
   - Repository access : Only select repositories → `ak125/automecanik-raw`
   - Permissions → Contents: Read-only
   - Expiration : ≤ 90 jours
2. Stocker le token dans https://github.com/ak125/automecanik-wiki/settings/secrets/actions
   - Name: `RAW_READONLY_PAT`
   - Value: \[le PAT\]

## Items différés (avec raisons)

| Item | Raison du différé |
|---|---|
| **P1** wiki business rules (`exportable.* + status: to_capture` block) | 0 fiche wiki actuellement `approved` → construire en avance pour cas non-actuel = sur-ingénierie. **Anti-bricolage = ne pas construire en anticipation.** Ré-évaluer dès la 1ère fiche en review. |
| **P3 Phase 2** `no-circular` (41) / `no-orphans` (48) / `no-deep-module-access` (77) | Refactor lourd — 166 violations sur 3 règles. Chantier dédié multi-sessions, prérequis : visualisation cycles via `madge` ou `dpdm` avant attaque. |
| **P2** export DB diag `by_symptom` typé | Autre chantier (ADR-033 PR-D, plan `mvp-et-raw-et-wobbly-brooks`). Scope-discipline = ne pas mélanger les chantiers. |

## Coverage manifest (AEC v1.0.0)

```yaml
scope_requested: |
  Vérification factuelle de claims utilisateur sur 4 repos canon, puis
  exécution disciplinée des priorités P0/P3 identifiées (P0a raw, P0b wiki,
  P3 Phase 1 + Phase 1 bis dep-cruiser monorepo).

scope_actually_scanned:
  - automecanik-raw: workflows/scripts/manifests/schemas (read), 1 PR livré
  - automecanik-wiki: workflows/scripts/schemas (read), 1 PR livré
  - nestjs-remix-monorepo: .dependency-cruiser.cjs (modifié), 2 PRs livrés
  - governance-vault: structure ledger/audit-trail (read pour ce trail)

files_read_count: ~40 fichiers via 3 agents Explore parallèles + lectures directes

excluded_paths:
  - .worktrees/ et /tmp/ workspaces concurrents (out of scope)
  - DB Supabase schemas (out of scope, P2 reportée)
  - workspaces/marketing/ (chantier ADR-036/038 parallèle, scope-disjoint)

unscanned_zones:
  - P3 Phase 2 deep refactor cycles (166 violations) — chantier dédié futur
  - P1 wiki business rules — différé jusqu'à 1ère fiche `approved`
  - P0b runtime enforce — bloqué sur PAT user offline

corrections_proposed: 0 hors scope des 4 PRs livrés
corrections_applied: 4 PRs MERGED (#10 raw, #14 wiki, #260 + #261 monorepo)
validation_executed:
  - depcruise audit pre/post chaque promotion (0 errors confirmé)
  - quality-gates.py --all sur 18 fiches wiki (18/18 PASS)
  - gates.py --all sur raw repo (8862 files SCOPE_SCANNED, 4 gates PASS)
  - 9 tests unittest pour gate_inventory_complete (9/9 PASS)
  - CI runs : 16/16 PR #260, 4/4 PR #14, 2/2 PR #10, partial PR #261

remaining_unknowns:
  - Deploy DEV main post-merge PR #261 — en cours au moment de cette consignation
  - Statut futur des items différés (P1, P3 Phase 2, P2)
  - Setup PAT côté wiki (action user offline)

final_status: SCOPE_SCANNED
generated_at: 2026-05-01T22:00:00Z
```

## Références

- Plan source (DEV scratch local agent) : `/home/deploy/.claude/plans/verifier-en-profondeure-ces-async-pie.md` rev 10
- Mémoires perso agent (espace `~/.claude/projects/-opt-automecanik-app/memory/`, non versionnées vault) :
  - `roadmap-p0-p3-canon-repos-20260501.md`
  - `feedback_check_merged_prs_before_planning.md`
- ADR-031 — Raw / Wiki / RAG / SEO Separation
- ADR-033 — Wiki Gamme Diagnostic Relations (référence indirecte via P0b gate)
- AEC v1.0.0 (`ledger/rules/rules-agent-exit-contract.md` ce vault)
- Session précédente complémentaire : [[2026-05-01-roadmap-canonization-and-chantier-c-ready]]
