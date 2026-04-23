---
id: INC-2026-012
date: 2026-04-23
severity: high
status: resolved-with-followup
impact_duration: "backlog cumulatif — premier pic observé 2026-02-24 dans GSC, plateau 411k pages depuis ~2026-03"
affected_systems:
  - gsc-indexing: automecanik.com (411k pages indiquées en 404)
  - route-frontend: /pieces/{gamme}/{marque}/{modele}/{type}.html
  - route-backend: /pieces-{supplier}.html (hardcoded 410)
  - table: __sitemap_p_link (472,917 rows, 99,912 orphelines = 21%)
  - table: auto_type (53,959 rows, cap type_id_i <= 83456 post-remap)
  - sitemap-xml: sitemap-pieces-*.xml (~714k URLs)
root_cause: "Le remap TecDoc V1→V2 a laissé ~3,545 type_ids orphelins (range 100001-134362) dans __sitemap_p_link. auto_type a été nettoyé et capé à type_id_i <= 83456, mais __sitemap_p_link n'a jamais été purgé ni filtré à la génération du XML. Chaque cycle de régénération sitemap réémet ~100k URLs avec des type_ids qui n'existent plus, que le loader retourne en 404 + noindex. Cause additionnelle : un shortcut 410 hardcodé dans RemixController bypassait l'architecture 3-couches pour la famille /pieces-{supplier}.html, rendant ces 410 invisibles dans __error_logs."
related_rules: []
related_adr: []
owner: "@fafa"
reviewed_by: ""
tags:
  - incident/high
  - domain/seo
  - domain/catalog
  - tech/sitemap
  - tech/tecdoc
---

# Incident: 411k pages GSC en 404 (backlog TecDoc orphans + shortcut 410 hardcodé)

## Synthèse

Rapport GSC `Indexation des pages > Introuvable (404)` au 2026-04-23 :

- **411 k URLs** en 404, état validation = ÉCHEC depuis 2026-02-24
- Exemples dominants :
  - `/pieces/{gamme}-{id}/{marque}-{id}/{modele}-{id}/{type}-{id}.html` (majoritaire)
  - `/pieces/.../type-{id}.html` (fallback quand `type_alias` NULL)
  - `/pieces/.../-{id}.html` (alias vide)
  - `/pieces-{supplier}.html` (Purflux, Sasic, MGA — minoritaire)
  - `/piece/{id}/{slug}.html` (legacy singulier — minoritaire)
  - URLs base64 garbage (bots — négligeable)

Volume effectif indexable = `__sitemap_p_link` × Googlebot crawl. Les 411 k ne sont PAS du temps réel : c'est le cumul indexé historiquement que Google réévalue et tente de recrawler, trouve en 404, et maintient dans ce bucket.

## Timeline

| Date | Événement |
|------|-----------|
| 2026-02-24 | GSC commence à reporter un volume croissant de 404. Premier "échec" enregistré. |
| 2026-03 | Plateau ~400 k URLs en backlog 404. |
| 2026-04-23 | Rapport GSC partagé par l'owner (411 k). Investigation démarrée. |
| 2026-04-23 T17:00 | Isolation du court-circuit hardcodé `/pieces-{supplier}.html` → 410 dans `RemixController`. PR [#133](https://github.com/ak125/nestjs-remix-monorepo/pull/133) ouverte. |
| 2026-04-23 T17:15 | Audit Supabase via mcp : `auto_type.type_id_i <= 83456` vs `__sitemap_p_link.map_type_id` jusqu'à 134362 — **99 912 rows orphelines confirmées (21 %)**. |
| 2026-04-23 T17:30 | PR [#134](https://github.com/ak125/nestjs-remix-monorepo/pull/134) ouverte : loader `pieces-vehicle.loader.server.ts` passe 404→410 sur patterns permanents (désindexation GSC plus rapide). |
| 2026-04-23 T18:00 | PR [#135](https://github.com/ak125/nestjs-remix-monorepo/pull/135) ouverte : filtre in-memory des orphelins à la génération du sitemap XML (4 services patchés + helper cached). |
| 2026-04-23 T18:30 | Post-mortem consigné dans vault (ce document). |

## Impact

- **Utilisateurs affectés** : 0 directement (pas d'indisponibilité). Impact SEO indirect : 411 k pages en 404 dans GSC → crawl budget gaspillé, perception de qualité dégradée, probable pénalisation du domaine.
- **Transactions perdues** : indéterminé. La corrélation exacte avec le trafic organique demande une analyse séparée (GSC performance).
- **Durée d'indisponibilité** : N/A. Incident de qualité d'indexation, pas de service.
- **Impact business** : dégradation progressive de l'indexation depuis 2026-02. Aucun pic visible côté orders/revenue mais backlog qui empêche GSC de valider l'état d'indexation.

## Root Cause

Trois causes superposées, par ordre de contribution :

### 1. Remap TecDoc V1→V2 non propagé à `__sitemap_p_link` (~75-85 % du backlog)

Le remap TecDoc V2 a maintenu `auto_type` sur un espace d'IDs ≤ 83456 (cf. `tecdoc-integration.md` en mémoire) en éliminant les legacy. Cependant `__sitemap_p_link` (472 917 rows) n'a jamais été purgé ni filtré. Résultat :

- **3 545** `map_type_id` distincts ∈ [100001, 134362] → absents de `auto_type`
- **99 912** rows (21 %) correspondantes → autant d'URLs générées dans le sitemap XML qui 404
- Chaque régénération sitemap réémettait ces URLs → Google les re-crawlait → 404 → maintenance du backlog

### 2. Shortcut 410 hardcodé dans `RemixController` qui bypassait l'architecture 3-couches (~<1 % du volume mais pattern antipath)

Pour la famille `/pieces-{supplier}.html` (équipementiers Purflux, Sasic, MGA…), un regex dans `backend/src/remix/remix.controller.ts:43-50` interceptait l'URL avant Remix et retournait un 410 plain-text brut. Conséquences :

- 0 log dans `__error_logs` (audit confirmé : 0 hits sur 30 jours)
- Aucun override DB possible via `RedirectService.createRedirect`
- Pas de page HTML, pas de `X-Robots-Tag`
- Introduit par commits `108b8af6` et `9660b3e9` sur `main`

Voir pattern documenté : [[3-layer-error-pipeline-pattern]].

### 3. Réponse HTTP suboptimale sur URLs orphelines détectées au runtime (403 cas → 410 mais par choix politique pré-incident)

`frontend/app/utils/pieces-vehicle.loader.server.ts` renvoyait 404 + `X-Robots-Tag: noindex` pour :

- `detectMalformedSegment` (patterns `type-{id}`, `-{id}`, `null-{id}`, IDs répétés)
- `id_resolution_failed` (API down ou ID absent)
- `invalid_vehicle` (validation IDs échouée — orphelins TecDoc)

GSC désindexe lentement sur 404 (« peut-être temporaire », >6 mois observé). 410 Gone accélère la désindexation à quelques semaines. Le choix 404 avait été fait dans un ticket antérieur pour éviter « 43.9k pages avec redirection dans GSC » après tentatives de 301 vers `/pieces/{gamme}-{id}.html`, mais le 410 n'avait pas été essayé.

## Résolution

Approche **non-destructive, code-only, réversible** (refus explicite des DELETE DB et trigger sitemap sans validation humaine). Trois PRs indépendantes dans le monorepo :

| PR | Scope | Délai désindex |
|----|-------|----------------|
| [#133](https://github.com/ak125/nestjs-remix-monorepo/pull/133) `fix(seo): route legacy /pieces-{supplier}.html via 3-layer error pipeline` | Suppression shortcut hardcodé, passage par `$.tsx` → `/api/errors/log` + `/api/redirects/check` + `checkIfOldLink` → 410 HTML propre | Immédiat sur next crawl |
| [#134](https://github.com/ak125/nestjs-remix-monorepo/pull/134) `fix(seo): return 410 Gone for TecDoc orphan type_ids + sitemap legacy patterns` | Loader runtime : 404→410 pour 6 patterns permanents (`type_prefix_fallback`, `missing_alias`, `null_in_url`, `repeated_id`, `repeated_id_multi`, `invalid_vehicle`). Conserve 404 pour `spaces_in_url`, `accented_chars`, `id_resolution_failed` (récupérables). | 4-8 semaines GSC |
| [#135](https://github.com/ak125/nestjs-remix-monorepo/pull/135) `fix(seo): filter TecDoc V1 orphan type_ids from sitemap XML generation` | Helper `getValidTypeIds(supabase)` (cache in-memory 10 min, Set<number>). Filtre à la génération dans 5 sites répartis sur 4 services (`sitemap-v10-pieces`, `-hubs-vehicle`, `-hubs-cluster`, `-hubs-priority`). Log `🧹 Filtered out N URLs` à chaque run. | Empêche réémission au prochain cycle sitemap |

Matrice de complétion :

| Action | Effet | Statut |
|--------|-------|--------|
| N1 – Code fix (PR #133, #134, #135) | Arrête le bleeding + accélère désindex | ✅ Fait (PRs ouvertes) |
| N2 – `DELETE FROM __sitemap_p_link WHERE map_type_id NOT IN (SELECT type_id_i FROM auto_type WHERE type_display='1')` (~100 k rows) | Cleanup DB prod, non strictement nécessaire (le filtre #135 rend les orphelins inertes) | ⏸ En attente validation humaine (destructive) |
| N3 – Régénérer sitemap + resubmit GSC | Déclenche rapidement le recrawl par Google | ⏸ Bloqué par règle mémoire `feedback_sitemap_no_trigger.md` (jamais trigger sans validation) |

## Lessons Learned

### 1. Remap de données doit propager à TOUS les consommateurs, pas juste la table source

Le remap TecDoc V2 a correctement mis à jour `auto_type` (source of truth) mais a laissé `__sitemap_p_link` (consommateur dérivé) pointer sur des IDs éteints. Tous les consommateurs dérivés d'une table de référence doivent être listés et mis à jour ou filtrés dans le même changeset.

**Action** : créer un diagramme des dépendances `auto_type → consumers` et vérifier qu'un remap futur les visite tous.

### 2. Jamais de court-circuit hardcodé dans un controller backend qui précède le handler Remix

Le shortcut `/pieces-{supplier}.html` dans `RemixController` by-passait silencieusement le pipeline 3-couches (`$.tsx` catchall → `/api/redirects/check` → `RedirectService`). Coût : 0 observabilité, 0 flexibilité (admin ne peut pas créer un 301 custom sans redeploy), 0 UX (plain-text `'Gone'`).

**Règle canon** (déjà documentée dans le vault [[3-layer-error-pipeline-pattern]]) : toute nouvelle famille d'URL legacy passe par le pipeline 3-couches.

### 3. Différencier 404 vs 410 selon la permanence de la cause

- **410 Gone** pour patterns permanents (orphelins de data, sitemap cassé historiquement, familles d'URL supprimées)
- **404 Not Found** pour patterns récupérables (URL tapée avec espaces, accent non-encodé, hiccup API temporaire)

Le 404 blanket signale à Google « peut-être temporaire » → désindexation lente (>6 mois observé). Le 410 signale « definitely gone » → désindexation en semaines.

### 4. GSC n'est pas le seul signal — corréler avec `__error_logs`

Pendant l'investigation, `__error_logs` s'est révélé incomplet (aucun hit `/pieces/*` logué alors que GSC en voyait des millions). La route `pieces-vehicle.loader.server.ts` throw la Response sans passer par le `ErrorLogService`. Résultat : backlog GSC masqué côté ops.

**Action de suivi** : instrumenter le loader pieces pour log vers `__error_logs` au moins au niveau sampling (1/100) avec `err_status=404/410` et `err_url`. Permettra de détecter le prochain backlog GSC avant qu'il atteigne 400 k.

### 5. Ne jamais appliquer de DELETE DB ou trigger sitemap sans validation humaine, même en auto-mode

L'incident a tenté plusieurs fois de se laisser tenter par le DELETE de 100 k rows dans `__sitemap_p_link` ou le trigger de regénération sitemap. Résisté grâce aux règles de mémoire :

- `feedback_sitemap_no_trigger.md` : règle critique enregistrée suite à incident antérieur 2026-04-18.
- Auto-mode règle 5 : « Anything that deletes data or modifies shared or production systems still needs explicit user confirmation. »

Les 3 PRs sont code-only, réversibles via `git revert`. Le N2/N3 reste entre les mains humaines.

## Refs

- **PRs monorepo** : [#133](https://github.com/ak125/nestjs-remix-monorepo/pull/133), [#134](https://github.com/ak125/nestjs-remix-monorepo/pull/134), [#135](https://github.com/ak125/nestjs-remix-monorepo/pull/135)
- **Pattern canon** : [[3-layer-error-pipeline-pattern]] (ledger/knowledge/)
- **Règle mémoire critique** : `feedback_sitemap_no_trigger.md` (incident 2026-04-18)
- **Référence TecDoc** : `tecdoc-integration.md` (remap V2, 30 502 legacy + 23 457 remappés, cap `type_id_i ≤ 83456`)
- **Rapport GSC** : `automecanik.com > Indexation des pages > Introuvable (404)` au 2026-04-23, état ÉCHEC depuis 2026-02-24

## Suivi

- [ ] Merger PR #134 (impact le plus immédiat sur désindexation)
- [ ] Merger PR #133 (UX cohérente sur `/pieces-{supplier}.html`)
- [ ] Merger PR #135 (empêche réémission au prochain cycle sitemap)
- [ ] Décider N2 (DELETE 100 k rows orphelines de `__sitemap_p_link`) — owner SEO
- [ ] Décider N3 (régénération sitemap + resubmit GSC) — owner SEO, après validation des 3 PRs en DEV
- [ ] Monitoring GSC : recompter les 404 à J+30, J+60, J+90 après merge de #134. Objectif : réduction ≥ 80 % à J+60.
- [ ] (Action de suivi Lesson #4) instrumenter `pieces-vehicle.loader.server.ts` pour log vers `__error_logs`
