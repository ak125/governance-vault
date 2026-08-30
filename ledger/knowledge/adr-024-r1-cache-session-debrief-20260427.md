---
category: knowledge
doc_family: knowledge
source_type: session-debrief
title: "ADR-024 R1 Gamme Page Cache — Session debrief 2026-04-27 (Phases 1-6a livrees)"
slug: adr-024-r1-cache-session-debrief-20260427
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-27"
updated_by: "@fafa"
related_adr:
  - ADR-024-r1-gamme-page-matview-persistence
  - ADR-016-vehicle-page-matview-persistence
  - ADR-021-database-rls-hardening-zero-trust
related_prs:
  - "ak125/governance-vault#80"
  - "ak125/governance-vault#81"
  - "ak125/governance-vault#82"
  - "ak125/governance-vault#83"
  - "ak125/governance-vault#84"
  - "ak125/governance-vault#85"
  - "ak125/governance-vault#86"
  - "ak125/nestjs-remix-monorepo#194"
  - "ak125/nestjs-remix-monorepo#196"
  - "ak125/nestjs-remix-monorepo#197"
  - "ak125/nestjs-remix-monorepo#198"
status: current
---

# ADR-024 R1 Gamme Page Cache — Session debrief 2026-04-27

> Session unique 2026-04-27 (Claude Opus 4.7 1M ctx + @fafa). Du diagnostic E2E
> flake initial a la livraison Phases 1->6a + scheduling de la promotion ADR
> automatique a J+14.

## 1. Contexte d'origine

Run CI deploy 2026-04-27 a echoue sur PR monorepo #190 (TS path aliases) avec
2 / 8 timeouts E2E Playwright sur `/pieces/plaquettes-de-frein-1.html` + 6 / 8
flaky. Le run precedent (`695fb86d`) avait 7 / 8 flaky tous recuperes. Marge
contre le timeout 15s aleatoire entre runs.

Diagnostic (debut de session) : la page R1 (`pieces.$slug.tsx`) appelle un
controller backend qui fait :
1. RPC `get_gamme_page_data_optimized` (~75ms warm, plusieurs secondes cold)
2. **+ 4 requetes sequentielles** dans `gamme-response-builder.service.ts`
   (948 lignes), incluant un **filesystem RAG read** dans
   `r1-related-resources.service.ts`

Le warming au boot ne couvre que le data cache, pas le response cache. Cold
load systematique > 15s sur les 238 G1/G2 gammes.

## 2. Decision : ADR-024 par parite ADR-016

Adopter le pattern **ADR-016 vehicle_page_cache** pour R1 :
- Table `__gamme_page_cache` (PK pg_id, payload JSONB, source_hash, stale)
- Fonctions `build_gamme_page_payload` / `rebuild_gamme_page_cache` /
  `get_gamme_page_data_cached` / `refresh_stale_gamme_cache`
- Table compagnon `__seo_r1_related_blocks_cache` pour sortir le RAG fs read
  du chemin SSR

ADR-024 propose dans vault PR #86 mergee `4f7b1d21`.

## 3. Ce qui a ete livre

### 3.1 Vault (8 PRs canon)

| PR | Sujet | Commit |
|---|---|---|
| `governance-vault#80` | rules-engineering-quality Q1-Q4 (anti-bricolage canon) | `d8bf1a0f` |
| `#81` | vault `.gitignore` orphelins lint transients | `faf36e48` |
| `#82` | ADR-016 + ADR-017 promus `proposed -> accepted` (evidence-based) | `2e35b0a9` |
| `#83` | ADR-006 superseded par ADR-011 + ADR-025 (joint coverage) | `1df609a9` |
| `#84` | MOC-Decisions sync + section Status Semantics (6 statuts) | `cc25e874` |
| `#85` | ADR-006 superseded_by format short IDs (regression fix) | `25cf73a8` |
| `#86` | **ADR-024 propose : R1 Gamme Page matview (parite ADR-016)** | `4f7b1d21` |

Note : la session a aussi repare au passage 2 fichiers orphelins
(`ledger/knowledge/typescript-aliases-tsc-alias-gotcha-20260427.md` et
`codeql-volume-false-positive-20260427.md`) qui etaient pousses en
feature branch sans PR — pris en charge dans une autre branche, mergee sur
main avant la fin de la session.

### 3.2 Monorepo (4 PRs)

| PR | Phase | Commit | Effet |
|---|---|---|---|
| `nestjs-remix-monorepo#194` | Phase 1 | `e0119308` | Schema `__gamme_page_cache` + 4 fonctions SQL + admin endpoint `/api/admin/gamme-cache/*` |
| `#196` | Phase 2 | `d50445e4` | Schema `__seo_r1_related_blocks_cache` + admin endpoint `/api/admin/r1-related-blocks-cache/*` + `get_r1_related_blocks_cached` SQL |
| `#197` | **Phase 5a** | `77a30254` | SSR read path bascule sur `get_gamme_page_data_cached` + cache-first lookup dans `R1RelatedResourcesService.buildRelatedBlocks` (fallback legacy preserve) |
| `#198` | **Phase 6a** | `663987ea` | R1 perf gate CI top 5 G1 gammes (parite gate R2 existant) |

Allowlist RPC mise a jour : `total: 174 -> 175` avec 5 nouveaux RPC
(`get_gamme_page_data_cached`, `rebuild_gamme_page_cache`,
`refresh_stale_gamme_cache`, `build_gamme_page_payload`,
`get_r1_related_blocks_cached`).

### 3.3 DB Supabase massdoc (`cxpojprgwgubzjyqzmoq`)

3 migrations appliquees via `mcp__supabase__apply_migration` (le pipeline
de deploy ne pousse PAS automatiquement les migrations Supabase — point Q4
note ci-dessous) :

- `adr024_phase1_gamme_page_cache_schema`
- `adr024_phase1_gamme_page_cache_functions`
- `adr024_phase2_r1_related_blocks_cache`
- `adr024_phase4_invalidation_helpers_and_triggers`

**Etat live** :
- `__gamme_page_cache` : **238 / 238** G1/G2 cached, 7.51 MB total
  (avg 32.3 KB / gamme), `stale_count = 0`
- `__seo_r1_related_blocks_cache` : **0 / 238** (Phase 3 batch B reste a
  faire — voir section 5)
- 12 triggers d'invalidation actifs sur `__seo_gamme`, `__seo_r1_image_prompts`,
  `__seo_gamme_purchase_guide`, `__seo_gamme_links` (3 events x 4 tables)
- 1 cron pg_cron job (`refresh-stale-gamme-cache`, jobid 14, schedule
  `*/10 * * * *`)
- Round-trip valide : UPDATE source -> trigger fire -> stale=TRUE ->
  `refresh_stale_gamme_cache(50)` -> stale=FALSE

## 4. Q-rules ayant guide la session

L'utilisateur a invoque la regle `[[rules-engineering-quality]]` (canon
mergee dans vault PR #80) plusieurs fois pendant la session avec
"meilleure solution pas de bricolage". Application stricte sur chaque
decision :

| Moment | Q1 application |
|---|---|
| Initial : refresh baseline knip ? | **Rejete** = bricolage. Solution : tool-version-aware baseline + dependabot split (vault PR #80 / monorepo PR #191) |
| R1 perf : aggressive cache warming ? | **Rejete** = bricolage. Solution : matview pattern parite ADR-016 (ADR-024) |
| R1 perf : split critical/enrichment endpoint ? | **Rejete** = asymetrie ADR-016, garde RAG fs read. |
| Implementation : Phase 1 + draft PR ? | **Adopte** = invariant garanti, scope honnete |
| Phase 5 : full refactor 948->50 lignes ? | **Differe Phase 5b** = scope realiste pour cette session |
| Phase 6 : pause ou enchainer ? | **Phase 6a maintenant** = invariant ajoute par construction, 6b/6c via /schedule J+14 |

## 5. Ce qui reste a faire

### 5.1 Phase 3 batch B — `__seo_r1_related_blocks_cache` backfill

Status : **0 / 238 cached**. Le code applicatif gere transparemment via
fallback legacy (PR monorepo #197 Phase 5a) : si `get_r1_related_blocks_cached`
retourne NULL, le SSR appelle l'ancien chemin (RAG fs read + 3 sub-queries).

Pour finir le backfill :
- Quand DEV preprod sera disponible sur `localhost:3200` (deploy mergee depuis
  l'evenement de session), executer :
  ```bash
  curl -X POST http://localhost:3200/api/admin/r1-related-blocks-cache/rebuild-all \
    -H "Cookie: connect.sid=<admin-session>"
  ```
- Verifier ensuite via `mcp__supabase__execute_sql` :
  ```sql
  SELECT count(*), count(*) FILTER (WHERE stale=TRUE)
  FROM __seo_r1_related_blocks_cache;
  ```

### 5.2 Phase 5b — refactor full

Hors scope de cette session. A faire dans une PR dediee :
1. **Etendre `build_gamme_page_payload`** SQL pour inclure `image_prompts`,
   `buying_guide_contract`, `sg_content` via JSON aggregation. Cela rend le
   payload de `__gamme_page_cache` self-contained (le SSR n'a plus a faire
   les 4 queries enrichment du tout, meme cold-load).
2. **Reduire `gamme-response-builder.service.ts`** 948 -> ~50 lignes
   (transformation pure post-RPC).
3. **Retirer `RESPONSE_CACHE_PREFIX`** et la double couche cache de
   `gamme-rest-rpc-v2.controller.ts` (le DB cache rend Redis response cache
   redondant pour ce path).
4. **Reduire `r1-related-resources.service.ts`** a un service de seed offline
   (le SSR ne l'appelle plus, le cache table est la source).

Estimation : ~4-6h (refactor + test exhaustif des 4 queries enrichment
deplacees en SQL CTE).

### 5.3 Phase 6b + 6c — observation 14j + promotion ADR-024

Routine remote schedulee : `trig_01AN2TfMQ7587KFUqxqS4wXt`
- Run-once : **2026-05-11 08:00 UTC** (Lun J+14, 10:00 Europe/Paris)
- Modele : `claude-sonnet-4-6`
- URL : `https://claude.com/code/routines/trig_01AN2TfMQ7587KFUqxqS4wXt`

L'agent autonome :
1. Mesure p50/p95/max R1 perf gate sur 14 derniers runs CI ci.yml main
2. Query `__gamme_page_cache` + cron `cron.job_run_details` 7j success rate
3. Decision sur 4 criteres :
   - p95 < 3000ms sur 14 runs (warning OK, error count = 0)
   - 238 / 238 cached, still_stale = 0 (ou explicable)
   - cron `refresh-stale-gamme-cache` 0 fails / 7 jours
   - 0 incidents lies dans GitHub issues / log.md
4. Si vert : ouvre PR vault `chore/adr-024-promote-accepted` qui flip
   `status: proposed -> accepted` + ajoute `implementation_evidence:`
   block (pattern PR vault #82). Auto-merge si CI verte.
5. Si rouge : ouvre GitHub issue `ADR-024 promotion blocked at J+14`.

### 5.4 Q4 trigger note — pipeline de deploy ne pousse pas les migrations Supabase

Decouvert en Phase 3 : les CI gates verifient la safety des migrations mais
ne les appliquent pas. ADR-016 vehicle migration aussi a ete appliquee
manuellement (pas de pipeline). C'est un trou de gouvernance.

Soit :
- Etendre `.github/workflows/ci.yml` step `Deploy PREPROD` avec
  `npx supabase db push` (ou equivalent sous condition que les migrations
  soient idempotentes, ce que le Migration Safety gate enforce deja).
- Soit creer un workflow dedie `apply-migrations.yml` qui se declenche sur
  `workflow_dispatch` apres deploy mergee, avec confirmation manuelle.

Ne pas adresser ad-hoc — meriter ADR / discussion separee.

## 6. Notes incident / rollback locaux

Pendant la session, plusieurs system reminders ont indique des fichiers
modifies "intentionnellement" en local (worktree `/tmp/claude-cleanup-worktree`
qui occupait le checkout `main`, faisant alterner les states). Verification
finale 2026-04-27 fin de session :

- `origin/main` : 4 commits PR Phase 1-2-5a-6a presents (`e0119308`,
  `d50445e4`, `77a30254`, `663987ea`) — OK
- Local working tree : etait en etat pre-merge sur certains fichiers
  (`ci.yml` sans R1 perf gate, `gamme-rpc.service.ts` sans cache-first).
  Cela ne reflete PAS l'etat de `origin/main`.

→ A retenir : pour les sessions futures, eviter les worktrees secondaires
qui peuvent court-circuiter les checkouts main et creer une fausse
impression de regression. Le canon est `origin/main`.

## 7. Liens

- ADR : [[ADR-024-r1-gamme-page-matview-persistence]]
- Pattern parent : [[ADR-016-vehicle-page-matview-persistence]]
- Regle canon : [[rules-engineering-quality]]
- Routine remote : `trig_01AN2TfMQ7587KFUqxqS4wXt` (J+14 promotion)

## 8. Evidence chiffree (snapshot fin de session)

```
__gamme_page_cache:     238 / 238 cached, 0 stale, 7.51 MB
__seo_r1_related_blocks_cache: 0 / 238 (legacy fallback actif)
Triggers invalidation:  12 (3 events x 4 tables)
pg_cron:                jobid 14 active, */10 * * * *
RPC allowlist:          175 entries
Vault PRs mergees:      8 (PR #80 a #86 + un knowledge cleanup)
Monorepo PRs mergees:   4 (PR #194, #196, #197, #198)
Migrations Supabase:    4 (3 schema/fn + 1 triggers/helpers)
Branche feature locale: cleaned up (toutes squash-merged + branch deleted)
```

---

*Session date : 2026-04-27*
*Session duration : ~3h*
*Status : Phase 1->6a livrees, 6b/6c automatiques a J+14*
