---
type: knowledge
status: active
date: 2026-05-01
related_adr: ["ADR-033", "ADR-031", "ADR-032", "ADR-039"]
related_rules: ["G1", "G2", "G3", "Q1", "Q3"]
audience: ["@fafa", "claude-code", "cowork", "future-sessions"]
---

# ADR-033 Phase 2/3 wave closure — verdict READY atteint (2026-04-30 → 2026-05-01)

> Wave de propagation du contrat ADR-033 wiki gamme `diagnostic_relations[]` à travers le monorepo, après livraison Phase 1 wiki/raw scaffold. **Le critère go Partie 3 a été atteint pour la 1ère fois 2026-05-01 10:55 UTC** : `wiki-readiness-check.py` retourne `READY` avec 6/6 critères C1-C6 PASS simultanément. Branchement consommateurs (DB / RAG / SEO / blog / diagnostic / chatbot) débloqué pour Partie 3.

## Contexte

ADR-033 (vault PR #108 commit `77085ef`, status `accepted` 2026-04-29) a défini le contrat `diagnostic_relations[]` top-level pour les fiches gamme wiki, retiré le bloc anti-pattern `entity_data.symptoms[]` (§D2), et figé 3 anti-patterns §D3 (pas `wiki/systemes/`, pas fichier-par-symptôme, pas réécriture moteur diagnostic).

Phase 1 ADR-033 (PR wiki #8 + #9 + raw #6 mergées 2026-04-30) a livré côté repos applicatifs : schema v2.0.0, 9 quality gates Python, 5 pilotes G6, dette P0 sources stub + symptom slugs DB convention. Ce dépôt **monorepo** était resté en gap : aucun outil propagé pour producteurs aval (skill, agents, validateur CI, cron export DB).

Cette wave (Phase 2 propagation + Phase 3 cron + readiness check) est livrée dans le plan rev 3 `mvp-et-raw-et-wobbly-brooks.md` (renommé rev 4 « Chantier C : Knowledge / Raw / Wiki / Diagnostic Canon » dans la roadmap globale 2026).

## PRs livrées (10 PRs en 1 session)

| # | Repo | PR | Commit | Scope |
|---|---|---|---|---|
| 1 | `automecanik-rag` | #7 PR-A.rag | `224e4c63` | `GammeContentContract.v1` → `v2.0` (canon §D6 published) |
| 2 | `automecanik-wiki` | #10 sub-PR | `451ab939` | retire orphan `diagnostic_relations[]` filtre-a-air.md (sibling P0(b) pattern) |
| 3 | `nestjs-remix-monorepo` | #249 PR-B | `7d77be6d` | workspace `workspaces/wiki/` + skill `wiki-proposal-writer` |
| 4 | `nestjs-remix-monorepo` | #250 PR-C | `d0b32a0b` | validateur Python `validate-gamme-diagnostic-relations.py` + workflow `wiki-validate.yml` |
| 5 | `nestjs-remix-monorepo` | #251 PR-D | `96837b95` | cron `export-diag-canon-slugs.py` + workflow nightly |
| 6 | `nestjs-remix-monorepo` | #252 ADR-039 sibling | `59cd0d8f` | TS Zod canon (parallèle, mergé par autre agent) |
| 7 | `nestjs-remix-monorepo` | #253 PR-F | `b6a73af8` | `wiki-readiness-check.py` 6 critères C1-C6 + workflow |
| 8 | `nestjs-remix-monorepo` | #256 fix#1 | `097d3558` | psycopg2 → PostgREST API (secret manquant `SUPABASE_DB_PASSWORD`) |
| 9 | `nestjs-remix-monorepo` | #257 fix#2 | `b70ca1e6` | `.strip()` env vars (newline secret) |
| 10 | `nestjs-remix-monorepo` | #258 closed | — | redondant avec #257 (fermé) |

PR-E migration script (Phase 4 ADR-033) **différée** : `wiki/gammes/` actuellement vide, 232 legacy `symptoms:` vivent dans `automecanik-rag/knowledge/gammes/`. Tool deviendra utile en Partie 3 quand sync-from-rag arrivera.

## Verdict READY atteint 2026-05-01

```json
{
  "verdict": "READY",
  "criteria": [
    {"code": "C1", "name": "schema v2.0.0 propagated", "passed": true,
     "evidence": "_meta/templates/gamme.md: schema_version: 2.0.0 ✓ | docs/GAMME_PAGE_CONTRACT.md: v2.0 mentioned ✓"},
    {"code": "C2", "name": "validateur CI bloquant actif", "passed": true,
     "evidence": ".github/workflows/wiki-validate.yml present and blocking ✓"},
    {"code": "C3", "name": "exports/diag-canon-slugs.json fresh", "passed": true,
     "evidence": "exports/diag-canon-slugs.json: 62 slugs, last commit 0d ago ✓"},
    {"code": "C4", "name": "fiches gamme migrées", "passed": true,
     "evidence": "wiki/gammes/ is empty (N/A — no legacy to migrate) ✓"},
    {"code": "C5", "name": "quality gates green", "passed": true,
     "evidence": "quality-gates: 18/18 PASS — 0 FAIL — 1 WARN ✓"},
    {"code": "C6", "name": "skill wiki-proposal-writer operational", "passed": true,
     "evidence": "workspaces/wiki/.claude/skills/wiki-proposal-writer/SKILL.md ✓"}
  ]
}
```

Workflow run référence : `wiki-readiness-check.yml` run #25211876381.

## 6 découvertes empiriques à conserver

### 1. Pattern « PR-A.app collapsed » — vérifier l'existant avant de propager

Plan rev 3 PR-A.app supposait l'existence de `nestjs-remix-monorepo/backend/content/automecanik-wiki/_templates/new-gamme.md` à bumper en v2.0.0. **Ce fichier n'existe pas sur main** : le dossier `backend/content/automecanik-wiki/` est vide. La propagation canon vers monorepo se fait via pointers ADR-031/032/033 dans `workspaces/wiki/CLAUDE.md` + `wiki-batch.md` de PR-B.

**Règle émergente** :

> Avant de planifier un bump version sur un fichier supposé exister, faire `find <path> -type f` pour confirmer. Plan fait sur supposition = bricolage potentiel. ADR-033 §"Critères de succès" #3 mentionnait `template/new-gamme.md` en générique — l'instanciation concrète a varié selon les repos.

### 2. Pattern « Python > TypeScript » pour outillage CI side-canon

Plan rev 3 PR-C/D/F prévoyaient TypeScript pour aligner avec `scripts/validate-gamme-schema.ts` existant. À l'inspection :

- Root `package.json` n'a **pas** `js-yaml` ni `ajv` (ils vivent dans `backend/` workspace)
- Wiki repo `_scripts/quality-gates.py` est **Python** (pyyaml + jsonschema)
- Adopter Python évite : (a) ajouter deps au root (side-effect lock file), (b) divergence de pattern entre wiki et monorepo

**Règle émergente** :

> Le choix du langage d'outillage CI side-canon doit s'aligner avec le repo qui contient déjà le canon (ici `automecanik-wiki/_scripts/`). Le sibling PR ADR-039 #252 (par autre agent) a couvert le besoin TS de manière complémentaire — il est OK d'avoir Python ET TypeScript en parallèle quand les besoins sont distincts.

### 3. Pattern « secret manquant inventé » — grep avant secret

PR-D #251 shippé avec workflow référençant `secrets.SUPABASE_DB_PASSWORD`. Découvert post-merge : ce secret **n'existe pas** dans monorepo Actions secrets (probablement convention de `apply-migration-marketing-phase1.py` qui run en local seulement, pas CI). Inventaire `gh secret list` montre `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` disponibles.

Fix : PR #256 switch psycopg2 → PostgREST API stdlib (réutilise secrets existants, no new dep).

**Règle émergente** :

> Avant de référencer `secrets.<NAME>` dans un workflow, faire `gh secret list --repo <repo>` pour vérifier que le secret existe. Si absent, vérifier d'abord les alternatives : autre secret avec accès équivalent (ex `SUPABASE_SERVICE_ROLE_KEY` au lieu de `SUPABASE_DB_PASSWORD`), API REST stdlib au lieu de driver natif, etc.

### 4. Pattern « newline trailing dans secret pasté » — `.strip()` défensif systématique

Run #25211659750 fail avec `urllib.InvalidURL: URL can't contain control characters. 'cxpojprgwgubzjyqzmoq.supabase.co\n' (found at least '\n')`. Le secret `SUPABASE_URL` provisionné via GitHub UI contient un `\n` final (artefact copy-paste).

Fix double :
- **Côté script** (PR #257) : `.strip()` défensif sur les env vars avant usage
- **Côté secret** : re-set propre via `printf '%s' '<value>' | gh secret set <NAME>` (sans newline)

**Règle émergente** :

> Tout script CI qui consomme un secret texte (URL, token, JWT) doit faire `os.environ.get(NAME, "").strip()` avant usage. Les secrets pastés via GitHub UI ont une probabilité non-nulle de carry trailing whitespace. Defense-in-depth client-side + canon-set provisioning.

### 5. Pattern « PR-E déférée » — outil pour contenu inexistant = bricolage

Plan rev 3 PR-E prévoyait `migrate-symptoms-to-relations.py` pour migrer fiches gamme legacy `entity_data.symptoms[]` → `diagnostic_relations[]`. Vérification : `wiki/gammes/` actuellement vide. 232 legacy `symptoms:` vivent dans `automecanik-rag/knowledge/gammes/` (autre repo, pas migrable directement par ce script).

**Règle émergente** (alignée garde-fou utilisateur #12 « pas de bricolage hybride transitoire ») :

> Un outil livré sans contenu à migrer = bricolage. Le tool deviendra utile en Partie 3 quand `sync-from-rag` (branche `feat/phase-f0c-sync-from-wiki`, WIP) peuplera `wiki/gammes/` avec les 232 legacy. PR-E sera alors créée à ce moment, avec contenu testable end-to-end.

### 6. Pattern « scope-disjoint firewall » — parallélisation propre via worktrees

Pendant la livraison ADR-033, l'utilisateur travaillait en parallèle sur ADR-036 (marketing Phase 2) + ADR-038 (marketing-agent-naming-canon) sur le main worktree. Discipline mécanique :

1. **Worktrees dédiés** sous `.worktrees/adr-033-pr-<x>/` pour chaque PR ADR-033
2. **Pre-commit grep guard** : `git diff --cached --name-only | grep -E "(workspaces/marketing|backend/src/modules/marketing|__marketing_|cst_marketing_consent|adr-036|adr-038)"` retourne 0 → ✅ scope clean
3. **Header commit `adr-033-scope: <zone>`** : `wiki|raw|rag|workspaces-wiki|scripts-wiki|workflows-wiki`

Vérifié à chaque commit. Aucune collision avec les chantiers parallèles user. ADR-036 PR #257 (par user/autre agent) qui a touché `scripts/wiki/export-diag-canon-slugs.py` en parallèle a généré le merge conflict de mon PR #258 — résolu en fermant PR #258 comme redondant (PR #257 a livré le même fix `.strip()`).

**Règle émergente** :

> Pour multi-chantiers parallèles, worktrees dédiés sont la défense de premier ordre. Les conflits de fichier signalent une duplication de scope (bonne nouvelle) ou un vrai overlap (à investiguer). Fermer la PR redondante en référençant celle qui a mergé en premier — pas de re-livraison.

## Workflows live (5 cron actifs post-wave)

| Workflow | Schedule | Repo | Rôle |
|---|---|---|---|
| `diag-canon-slugs-export.yml` | quotidien 02:00 UTC | monorepo | export DB → wiki/exports/diag-canon-slugs.json (idempotent diff-then-commit) |
| `wiki-validate.yml` | lundi 03:00 UTC + PR | monorepo | validateur Python 7 gates (drift detection wiki) |
| `wiki-readiness-check.yml` | lundi 04:00 UTC + PR + dispatch | monorepo | verdict 6 critères C1-C6 (informational schedule, fail PR/dispatch) |
| `vault-supabase-cost-check.yml` | lundi 08:00 UTC | vault | Management API monitoring (PR vault #124) |
| `vault-weekly-lint.yml` | lundi 02:00 UTC | vault | drift check rules canon |

Plus 2 routines Paperclip cron-like : `trig_01Tq3Z8ohU29suDmnezZhWnG` (J+2 INC ADR-034 DB freeze) + `trig_01LKqhkSKddud3ywGM9Yjb6z` (J+30 audit ADR-033).

## Prochaines étapes (Partie 3 unlocked)

Le verdict `READY` débloque la **Partie 3 Annexe A** (consommateurs différés du plan rev 6) :

1. **Sync-from-rag** (branche `feat/phase-f0c-sync-from-wiki` WIP 2026-04-28) : sync `automecanik-rag/knowledge/gammes/*.md` → `automecanik-wiki/wiki/gammes/*.md`. Active 232 legacy fiches.
2. **PR-E activation** : `migrate-symptoms-to-relations.py` peut maintenant être créé et testé end-to-end sur les 232 fiches légacy fraîchement importées.
3. **DB / RAG / SEO / blog / diagnostic / chatbot consumers branchement** : tous étaient gates sur `wiki-readiness-check.py = READY`. Prêts à déclencher.
4. **Maturité G9-B** (J+17 → J+30) : `migrate-template.py`, `wiki-quality-audit.yml` cron weekly full sweep, rollback drill C4. Routine vault J+30 audit ADR-033 fera tomber le déclic.

## Références

- ADR-033 vault PR #108 commit `77085ef` (status `accepted` 2026-04-29)
- ADR-031 (4-layer architecture) + ADR-032 (cohabitation maintenance{}) + ADR-039 (TS Zod canon)
- Plan rev 3/4 : `/home/deploy/.claude/plans/mvp-et-raw-et-wobbly-brooks.md`
- Mémoire personnelle Claude Code : `adr-033-wave-2-closed.md`
- Sibling knowledge file : `adr-032-session-empirics-20260429.md` (pattern « 3 faux problèmes »)
- Sibling knowledge file : `adr-026-p0-handoff-completion-20260427.md` (pattern handoff completion)
- Workflow CI vivants (production) :
  - `.github/workflows/wiki-validate.yml` (monorepo)
  - `.github/workflows/diag-canon-slugs-export.yml` (monorepo)
  - `.github/workflows/wiki-readiness-check.yml` (monorepo)
- Verdict READY artifact : workflow run #25211876381 (download via `gh run download` → `readiness-report.json`)
