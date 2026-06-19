---
id: ADR-090
title: "SEO Projection Forward Writer Canon — ratifie les contrats §C1-C4 (outbox refresh-trigger, payload R1 block-taxonomy, 2-gate writer wouldRegress) dont dépend le writer exports/seo→DB : amende ADR-059"
status: accepted
date: "2026-06-19"
decision_date: "2026-06-19"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-059"]
extends: ["ADR-031", "ADR-033", "ADR-046", "ADR-086", "ADR-088", "ADR-089"]
related_adr: ["ADR-027", "ADR-028", "ADR-031", "ADR-033", "ADR-039", "ADR-046", "ADR-055", "ADR-059", "ADR-074", "ADR-086", "ADR-088", "ADR-089"]
related_rules: ["G1", "G2", "G3", "AI1", "AP-10", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-090 (PROPOSÉ — numéro à confirmer au vault) : SEO Projection Forward Writer Canon (ratifie §C1-C4)

> **DRAFT vault — préparé en /tmp, NON appliqué.** À porter dans `ak125/governance-vault`
> via PR signée G3 (single-write-point Deploy VPS). **Amende ADR-059** (SEO Runtime Projection
> Architecture, accepted) — ajoute le contrat du **forward writer** (exports/seo → DB versionnée),
> côté écriture, sans modifier le read-path projeté ni les §Interdictions déjà gravées. **N'abroge
> rien.** Référence **ADR-088/089** (gates substance / coverage-map, déjà au vault), **ADR-046**
> (single-generator), **ADR-028** (READ_ONLY Option D anon). Owner décide. Rien n'est écrit dans le
> vault par l'assistant.

- **Statut** : Proposed
- **Date** : 2026-06-19
- **Amende** : **ADR-059** (§Décision — ajoute le contrat du `SeoProjectionWriteWorker` côté payload + refresh-trigger + write-semantics + read-RPC grant) — **n'abroge pas**, **complète côté write**
- **Référence inchangée** : ADR-059 (7 tables + 2 MVs + 2 queues BullMQ + `replay_projection.py` ; flag `seo_projection_read_v1` défaut FALSE ; snapshots tar.zst immutables ; §Interdictions formelles ; §Projections never generate canon ; one-way SoT) · ADR-046 (R-stack single-generator) · ADR-028 Option D (backend READ_ONLY/PREPROD = anon)
- **Auteur du draft** : assistant (préparation) — **validation + signature = owner**
- **Preuves** : `audit/seo-wiki-to-content-db-wiring-design-20260610.md` §C1-C4 (salvage legacy, contre-vérifié adversarialement) · migration `backend/supabase/migrations/20260427_r1_related_blocks_cache_schema.sql` (LIVE, 238 G1/G2 matérialisées) · service `backend/src/modules/gamme-rest/services/r1-related-resources.service.ts` (consomme déjà le contrat §C2 cache-first, fallback `{ blocks: [] }` observable) · `scripts/seo-projection/replay_projection.py` + `__seo_projection_runs` (LIVE) · `audit/r1-related-blocks-golden-sample-20260611/` (golden 14/14)

---

## Contexte (problème mesuré — candidats non ratifiés bloquent le writer)

ADR-059 a gravé le **lecteur** projeté (RPC `get_active_seo_projection`, MVs, flag `seo_projection_read_v1`)
et la mécanique de **versioning / replay** (`__seo_projection_runs`, snapshots immutables). Mais ADR-059
§Plan d'implémentation décrit le `SeoProjectionWriteWorker` au niveau mécanique (« INSERT versions +
UPDATE active_version_id, transaction courte ») **sans graver le contrat du payload qu'il écrit**, ni
**ce qui déclenche un refresh ciblé**, ni **la sémantique anti-régression** de l'écriture.

Le pilote contenu (`audit/seo-wiki-to-content-db-wiring-design-20260610.md`) a vérifié que **tout le code
amont est prêt** (`build_exports_seo.py` approved-only ; `exports/seo/<entity>.json` contractuel) et que
**le seul maillon manquant côté DB est ce forward writer**. Le même audit a salvagé, depuis le legacy
« RAG = source de contenu » avant suppression, **4 designs de production** (§C1-C4), explicitement marqués
**« CANDIDATS, jamais canon »** :

- **C1** — Outbox de refresh (hérité de `rag-change-watcher.service.ts`, table `__rag_change_events`
  conservée en DB) : sait **quels R rafraîchir** quand une fiche wiki promue change.
- **C2** — Taxonomie des blocs maillage R1 = **contrat du payload** de `__seo_r1_related_blocks_cache`
  (table LIVE, déjà consommée cache-first par le SSR R1). Le writer en devient **producteur + rafraîchisseur**.
- **C3** — Familles de slots R1 (hérité de `r1-enricher.service.ts`) : forme des slots écrits par rôle R1.
- **C4** — Writer sync 2-gate (hérité de `conseil-enricher.service.ts`, refactor canon #348) :
  **CanonGate → QualityGate** + **`wouldRegress`** (anti-régression par section).

**Tension** : on ne peut pas construire le writer R1-feeder + `wouldRegress` au-dessus de contrats que la
gouvernance qualifie de « jamais canon ». Construire d'abord = soit figer un contrat de fait non revu
(dérive #1 agent : système parallèle), soit risquer une régression silencieuse de contenu. **Le writer a
besoin que §C1-C4 deviennent canon AVANT son implémentation.** C'est l'objet de cet amendement.

## Décision

Cet ADR **ratifie §C1-C4 comme contrats canon** du forward writer, **annexes au contrat ADR-059**. Il ne
crée aucune table, aucun flag, aucune queue nouvelle : il **étend** les artefacts ADR-059 déjà gravés et
les tables/services LIVE déjà cités. Le writer **réutilise** `__seo_projection_runs`,
`projection_contract_version`, les 2 queues BullMQ (`projection-write-queue` / `projection-refresh-queue`)
et l'object-store snapshots — il ne fork rien.

### A. Localisation du forward writer (sibling, zéro système parallèle)

Le forward writer est un **frère** de `replay_projection.py`, sous **`scripts/seo-projection/`** du
monorepo (NestJS-side `SeoProjectionWriteWorker` pour l'enqueue BullMQ tel que défini ADR-059). Il
**réutilise** `__seo_projection_runs` (1 row/run, `projection_contract_version` + `exports_snapshot_hash`
+ `exports_snapshot_uri`) comme audit-trail unique — **aucun nouveau registre de run**. Le replay
(`replay_projection.py`) et le forward writer partagent le **même contrat de run** : ce que le writer
écrit, le replay doit pouvoir reconstruire bit-exact depuis le snapshot tar.zst (round-trip Hypothesis,
ADR-059 §Replay infrastructure G1/G2). Toute évolution de signature du writer suit la même contrainte
**no-refactor-libre** que `replay_projection.py` (review @fafa + ADR amendment si comportement change).

### B. C1 — Outbox de refresh : sémantique du refresh-trigger (ratifiée)

L'outbox `__rag_change_events` (table conservée en DB) est l'**unique déclencheur** du refresh ciblé
post-write. Sémantique canon :

- **Événement** = `{ entity_id, hash old/new, diff_sections[], rce_impacted_roles[], rce_jobs_enqueued }`
  (traçabilité complète — quels R rafraîchis, quels jobs enqueués).
- **Refresh ciblé déclenché par l'outbox** : un write projection émet l'événement ; un changement de
  fiche wiki promue **n'invalide que les rôles impactés** (`rce_impacted_roles[]`), jamais un REFRESH MV
  global aveugle. Le refresh MV reste hors-transaction sur `projection-refresh-queue` (ADR-059), avec
  **coalescing/debounce 5s** déjà gravé.
- **Dédup fenêtre glissante** (60 min défaut) : même `entity_id × rôle` déjà en file → **skip** (pas de
  ré-enqueue, pas de tempête de refresh).
- **Double whitelist** (rôles autorisés × gammes autorisées) = surface de **rollout progressif** côté
  write, miroir du flag `seo_projection_read_v1` côté read. Hors whitelist → **pas de write projeté**
  (fail-closed, défaut sûr = ne rien projeter).
- **Re-filtrage du scope côté processor** (garde-fou hérité pipeline-chain) : **jamais confiance au
  payload seul** — le worker `projection-refresh-queue` re-vérifie le scope (rôle autorisé × gamme
  indexée) avant d'agir. Payload empoisonné ⇒ no-op observable.
- **Breaker 3 seuils** + table incidents (`__rag_pipeline_incidents`) + kill volatile + métriques
  **calculées côté serveur** via RPC `rag_watcher_breaker_metrics` (jamais côté client). Breaker open
  ⇒ arrêt du write projeté, **pas** de fallback silencieux : incident loggé + Sentry (ADR-059 obs stack).

### C. C2 — Taxonomie des blocs maillage R1 : contrat du payload (ratifié)

Le writer est le **producteur + rafraîchisseur canon** de `__seo_r1_related_blocks_cache` (table LIVE,
migration `20260427_r1_related_blocks_cache_schema.sql`). Le contrat du JSONB `payload` (`{ blocks: [] }`)
est **canon**, déjà consommé par `r1-related-resources.service.ts` (cache-first, fallback observable) :

- **3 kinds** : `avoid-confusion` (score 1.0) · `buying-guide` (guide-achat 0.95 / conseils 0.9) ·
  `compatible-parts` (0.6). Inputs depuis `exports/seo` : `confusion_with` / `related_parts` (provenance
  re-routée RAW, jamais RAG lu directement — ADR-031/046).
- **Bornes dures** : max **3 blocs × 3 liens** ; **blocs vides non retournés** ; **no-self-link**.
- **Cible de lien filtrée `pg_level='1'`** (gammes indexées uniquement) — cohérent ADR-074
  (indexability decision plane). Lien vers non-indexé interdit.
- **Existence-gating** : lien `buying-guide` **seulement si R6 publié non-draft** ; lien `conseils`
  **seulement si plan R3 `validated`**. Le writer ne fabrique jamais un lien vers un contenu inexistant.
- **Le frontend consomme, n'arbitre rien** : toute la décision de maillage vit côté writer ; le SSR
  rend ce que le cache contient, gamme hors-cache ⇒ `{ blocks: [] }` par design, observable via
  `GET /api/admin/r1-related-blocks-cache/stats`.
- **Source-hash & invalidation** : `source_hash = md5(rag_data + db_state)` pour détection no-op et
  invalidation ciblée (déjà gravé dans la migration). Un refresh qui produit le même hash = no-op
  (n'incrémente pas de version, ne déclenche pas de refresh MV inutile).

### D. C3 — Familles de slots R1 (ratifié, annexe du payload)

Le writer écrit les slots R1 selon les familles héritées (recette `r1-content-batch` successeure) :

- `hero_subtitle` ≤ 200 c (depuis `intro_role`) · `args` 1-4 (titre ≤ 100 c / contenu ≤ 300 c, depuis
  `buy_args`) · `FAQ` max 6.
- **Persistance du gatekeeper score** (`r1s_gatekeeper_score`) à **chaque écriture** — traçabilité de la
  qualité au moment du write, pas seulement au read.

### E. C4 — Writer 2-gate + `wouldRegress` : sémantique d'écriture (ratifiée)

Le forward writer applique **2 portes en séquence** avant tout INSERT de version, héritées du refactor
canon #348 (`conseil-enricher.service.ts`) :

1. **CanonGate** (pureté de rôle) — émise via `canon-observability.service.ts` (**point d'émission
   désigné, conservé** ; pas de nouvelle surface d'observabilité). Un bloc destiné à R1 ne porte que du
   contenu de rôle R1, etc. (cohérent ADR-046 single-generator : la projection est l'INPUT du générateur).
2. **QualityGate** (scoring) — réutilise les gates de substance ADR-088 (planchers 6-dim/100, coverage-map
   ADR-089 par claim) ; **pas de nouveau scoreur**. Sous-plancher ⇒ **bloqué** (fail-closed), pas écrit.

**Sémantique `wouldRegress` (canon)** — anti-régression **par section** :

- **INSERT-new-version-never-UPDATE** : conforme à l'interdiction ADR-059 « DB overwrite destructive
  (INSERT nouvelle version, jamais UPDATE row existante) ». Le writer **INSÈRE** toujours une nouvelle
  ligne dans `__seo_entity_fact_versions` / `__seo_content_block_versions`, puis bascule
  `active_version_id` — il ne modifie **jamais** une version existante en place.
- **`wouldRegress` = no-rétro-régression** : avant de basculer `active_version_id` vers la nouvelle
  version, le writer compare son score (QualityGate) au score de la version active courante **par
  section**. Si la nouvelle version est **moins bonne** (`wouldRegress = true`), la nouvelle version est
  **insérée en `status='draft'`** (audit-trail préservé, ADR-059 §Rollback) mais **`active_version_id`
  n'est PAS basculé** — le contenu meilleur reste servi. Un meilleur contenu n'est **jamais écrasé** par
  un moins bon. Décision **observable** (logguée + métrique), jamais un skip silencieux (CLAUDE.md
  « No silent fallback »).
- **Fallback S2_DIAG observable** : seul usage autorisé de la RPC `get_observable_symptoms_for_gamme`
  (aligné doctrine « Internal DB first »). Fallback **observable**, pas silencieux ; jamais une source
  de contenu inventée.

### F. Read-path RPC sous READ_ONLY/PREPROD anon (GRANT EXECUTE obligatoire)

Sous ADR-028 Option D, le backend en **READ_ONLY/PREPROD tourne en `anon`** (pas de service_role). Le
read-path projeté (`get_active_seo_projection`, et le getter R1 `get_r1_related_blocks_cached` déjà
`SECURITY DEFINER STABLE`) est appelé par le backend **en tant que anon**. **Conséquence canon de cet
amendement** : toute RPC du read-path projeté DOIT avoir `GRANT EXECUTE ... TO anon` dans sa migration,
**sinon le smoke E2E PREPROD casse** (REVOKE EXECUTE sur un DEFINER read-path = échec boot smoke,
incident documenté MEMORY `feedback_readonly_preprod_backend_runs_as_anon_needs_definer_execute`).
Cartographier le read-path **avant** tout durcissement EXECUTE. Le **write-path** reste service_role-only
(RLS `service_role` de la table R1 cache, cohérent ADR-021) — anon n'écrit jamais.

### G. Sûreté de déploiement (fail-closed, no blast-radius)

- **Flag `seo_projection_read_v1` défaut FALSE** (inchangé ADR-059) : le read projeté reste dark tant que
  l'owner ne promeut pas. Le forward writer peut écrire (shadow) **sans** que les pages lisent la
  projection — découplage write/read préservé (ADR-055 shadow mode).
- **Fail-closed partout** : hors whitelist ⇒ pas de write ; breaker open ⇒ stop + incident ; sous-plancher
  QualityGate ⇒ bloqué ; `wouldRegress` ⇒ pas de bascule active. **Aucun fail-open, aucun fallback
  implicite.**
- **NO URL / canonical change** : le writer ne touche **jamais** d'URL, de canonical, de meta_title/desc/H1
  (MEMORY `feedback_no_url_changes_ever`, `feedback_no_touch_meta_h1_if_optimized`). Il alimente du contenu
  de blocs/facts projetés, pas le routage SEO.
- **Snapshot immutability** : chaque run du writer scelle son snapshot exports tar.zst en object-store
  avec `chattr +i` post-write (ADR-059 §Snapshots immutables), seul SoT de replay. Replay via
  `git checkout` interdit.
- **One-way SoT préservé** : le writer est **write-only consumer** des exports — **jamais** de write-back
  wiki, jamais d'auto-fix projection→wiki (ADR-059 §Projections never generate canon). Pre-commit wiki
  refuse tout commit `Author: SeoProjectionWriter`.

## Observabilité (réutiliser l'existant, zéro canary externe)

- **Émission CanonGate** : `canon-observability.service.ts` (point désigné conservé).
- **Breaker / métriques** : RPC `rag_watcher_breaker_metrics` (serveur) + `__rag_pipeline_incidents` +
  Sentry (LIVE) + stack OpenTelemetry/Grafana ADR-059. **Pas** de nouveau canary externe (MEMORY
  `feedback_no_external_canary_when_internal_observability_exists`).
- **R1 cache** : `GET /api/admin/r1-related-blocks-cache/stats` (stats existantes) + golden sample
  `audit/r1-related-blocks-golden-sample-20260611/` comme non-régression.
- **Run audit** : `__seo_projection_runs` (1 row/run) = trace unique, partagée avec le replay.

## Ce que cet ADR NE fait PAS

- **Ne crée** aucune table, aucun flag, aucune queue, aucun registre nouveau. Il **ratifie** des contrats
  au-dessus d'artefacts ADR-059 + tables/services LIVE.
- **Ne promeut pas** `seo_projection_read_v1` (reste FALSE — décision owner séparée, ADR-059).
- **Ne modifie pas** le read-path projeté ni les §Interdictions ADR-059 (les renforce côté write).
- **Ne change aucune URL/canonical/meta**.
- **N'implémente pas** le writer (vault = décisions only). L'implémentation (sibling
  `scripts/seo-projection/`, migrations GRANT EXECUTE, tests Hypothesis round-trip) est owner-sponsorisée
  APRÈS acceptation.

## Invariant — AVANT / APRÈS

| Aspect | AVANT (ADR-059 seul) | APRÈS (ADR-090) |
|---|---|---|
| §C1-C4 | « CANDIDATS, jamais canon » | **canon, annexes ADR-059** |
| Payload R1 (`__seo_r1_related_blocks_cache`) | consommé LIVE, contrat non gravé | **contrat ratifié** (3 kinds, 3×3, no-self-link, existence-gating) |
| Refresh post-write | MV refresh hors-tx (générique) | **outbox `__rag_change_events` = trigger ciblé** (dédup, whitelist, breaker, re-filtre processor) |
| Write semantics | « INSERT version, jamais UPDATE » | + **`wouldRegress` no-rétro-régression par section** (draft si pire, pas de bascule active) |
| Forward writer location | non spécifié | **sibling `scripts/seo-projection/`, réutilise `__seo_projection_runs`** |
| Read RPC sous anon | implicite | **GRANT EXECUTE anon obligatoire** (sinon smoke E2E casse) |

## Conséquences

- **Positif** : le writer R1-feeder + `wouldRegress` peut être construit sur des contrats gravés ; zéro
  système parallèle ; round-trip replay garanti ; régression de contenu structurellement impossible
  (wouldRegress) ; smoke E2E préservé (GRANT anon).
- **Coût** : l'owner doit signer cet amendement avant l'implémentation du writer ; migrations futures
  doivent inclure le GRANT EXECUTE anon sur le read-path.
- **Risque résiduel** : si le scope whitelist est mal câblé, le writer ne projette rien (fail-closed —
  défaut sûr, observable, pas de dégât).

## Précisions issues de la revue adversariale (2026-06-19)

- **`wouldRegress` n'est pas un veto définitif** : la version « pire » est conservée en `draft`
  (audit-trail), pas jetée. Un humain/owner peut la promouvoir manuellement (ADR-059 §Rollback inverse).
- **Le re-filtrage processor (C1) est NON-négociable** : c'est lui qui empêche un payload outbox
  empoisonné de projeter hors-scope. La whitelist côté enqueue n'est pas suffisante seule.
- **C2 existence-gating dépend d'états R3/R6** : si ces états ne sont pas observables au moment du write,
  le lien n'est **pas** émis (fail-closed), jamais émis « optimistiquement ».
- **GRANT anon ≠ write anon** : seul le read-path DEFINER est GRANT anon ; le write reste service_role.

## Questions ouvertes (à trancher par l'owner en signant)

- **Q1 — `projection_contract_version` bump ?** L'ajout du contrat writer change-t-il le
  `projection_contract_version` (runner) gravé ADR-059, ou est-ce un `writer_contract_version` distinct
  (cohérent §Contract versioning extensible ADR-059) ? Proposition : **nouveau `writer_contract_version`**
  pour découpler writer/runner/pages.
- **Q2 — Granularité du score `wouldRegress`** : comparer le score QualityGate **par section** (proposé)
  ou par bloc entier ? Le legacy `conseil-enricher` opérait par section ; à confirmer pour R1 slots (C3).
- **Q3 — Whitelist C1 = nouvelle table ou réutilise la double-whitelist legacy ?** Si table, owner-gated
  (mutation schéma). Proposition : réutiliser la structure héritée, pas de nouvelle table.
- **Q4 — RPC `rag_watcher_breaker_metrics` / `get_observable_symptoms_for_gamme` : statut LIVE à
  re-vérifier** avant implémentation (présence + GRANT anon si lues sous READ_ONLY).

## Action owner (vault G3)

1. Relire ce draft + `audit/seo-wiki-to-content-db-wiring-design-20260610.md` §C1-C4.
2. Trancher Q1-Q4.
3. Confirmer le numéro ADR (090 supposé libre ; 089 = dernier proposé).
4. Porter dans `ak125/governance-vault` via PR signée G3 (frontmatter ci-dessus, aligné ADR-088/089).
5. APRÈS acceptation : sponsoriser l'implémentation du writer (sibling `scripts/seo-projection/`,
   migrations GRANT EXECUTE anon, tests Hypothesis round-trip vs `replay_projection.py`).

## Références

- [ADR-059 SEO Runtime Projection](ADR-059-seo-runtime-projection.md) (accepted — **amendé par cet ADR**)
- [ADR-088 Gate de promotion de substance](ADR-088-promotion-gate-substance-scoring.md) (QualityGate réutilisée)
- [ADR-089 Content Coverage-Map Canon](ADR-089-content-coverage-map-canon.md) (dim A par claim)
- [ADR-046 R-stack single-generator] · [ADR-028 READ_ONLY Option D anon] · [ADR-055 shadow mode] · [ADR-074 indexability decision plane]
- Audit candidats : `audit/seo-wiki-to-content-db-wiring-design-20260610.md` §C1-C4 (monorepo)
- Infra LIVE réutilisée : `scripts/seo-projection/replay_projection.py` · `__seo_projection_runs` + `projection_contract_version` · `backend/supabase/migrations/20260427_r1_related_blocks_cache_schema.sql` · `backend/src/modules/gamme-rest/services/r1-related-resources.service.ts` · `__rag_change_events` · golden `audit/r1-related-blocks-golden-sample-20260611/`
