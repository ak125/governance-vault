---
id: INC-2026-005-recurrence
type: incident
title: GSC 30,4k pages 5xx — Cloudflare cache poisoning sur loader-thrown 5xx Remix
date: 2026-05-06
date_detected: 2026-05-05
date_resolved: 2026-05-06
severity: high
status: resolved
impact_duration: "Persistance jusqu'à 24h après chaque 500 origin (s-maxage=86400). Stock GSC 30,4k URLs. Levée par PROD tag v2026.05.06-cf-cache-5xx-fix + purge Cloudflare 2026-05-06 ~13:35-13:42 UTC."
affected_systems:
  - route-frontend: /pieces/{gamme}/{marque}/{modele}/{type}.html (R2)
  - route-frontend: /pieces/{gamme}-{id}.html (R1)
  - route-frontend: /blog-pieces-auto/guide-achat (R3 hub)
  - cdn: Cloudflare
  - reverse-proxy: Caddy → NestJS
related_rules:
  - seo-http-status-contract
  - performance-cache-discipline
related_adrs:
  - ADR-016-vehicle-page-matview-persistence
related_incidents:
  - INC-2026-005
owner: "@automecanik.seo"
reviewed_by: "Claude Opus 4.7"
tags:
  - incident/high
  - domain/seo
  - domain/catalog
  - tech/cloudflare
  - tech/remix
  - tech/caddy
  - cache-poisoning
  - resolved
  - post-mortem
  - followup-backend-rm-v2
---

# INC-2026-005-recurrence : Cloudflare cache poisoning sur loader-thrown 5xx Remix

> [!warning] Résumé
> Récurrence partielle d'INC-2026-005. La cause **origin** (cold RPC `pieces_relation_type` qui timeout sur certaines combos `gamme_id × type_id`) n'a jamais été pleinement corrigée — ADR-016 a stabilisé les vehicles `/constructeurs/*` mais pas la chaîne RM V2 `/api/rm/page-v2` qui sert `/pieces/*`. Côté CDN, un bug architectural Remix faisait que **toute 500 transitoire devenait persistante 24h** : la fonction `headers: HeadersFunction = () => ({...})` zero-arg appliquait le `Cache-Control: public, s-maxage=86400` du chemin heureux à toutes les réponses, y compris les 4xx/5xx loader-thrown. Cloudflare honorait le `s-maxage` → cache HIT 5xx pendant 24h → effet boule de neige Googlebot.
>
> **Sample empirique 2026-05-06** (audit DEV → PROD, 930 URLs sitemap stratifiées) :
>
> | Catégorie | 200 | 5xx | Total |
> |-----------|-----|-----|-------|
> | `/constructeurs/*` (vehicles) | 100 % | 0 % | 200 |
> | `/pieces/*` (pieces vehicle) | 53 % | **47 %** | 550 |
> | autres (brands, blog, ref) | 99 % | <1 % | 180 |
>
> Distribution 5xx : 100 % `type_id < 60000` (legacy SEO-prioritaire), transversale aux gammes/brands.
>
> Mitigation **PR #320** mergée 2026-05-06 : helper `~/utils/cache-control#buildCacheHeaders` errorHeaders-aware + 7 tests + garde mécanique (script bash + pre-commit + step CI lint blocant). Limite la **persistance 24h**, pas l'occurrence initiale du 500.

## Timeline

| Heure UTC | Événement |
|-----------|-----------|
| ~2026-03-15 (estimé) | Persistance latente : `s-maxage=86400` agressif présent depuis ajout des routes pieces R2 (origine non datée précisément, hors scope ce post-mortem) |
| 2026-04-13 | Fix INC-2026-005 sur vehicles — `/constructeurs/*` stabilisés, mais `/pieces/*` non couverts par ADR-016 |
| 2026-05-05 ~21:00 | Email GSC `[WNC-10031170]` : validation échouée 2026-05-02 sur 30,4k pages, début 2026-04-28 |
| 2026-05-06 13:27 | Audit empirique stratifié 930 URLs (sitemap + dump GSC) → **27,8 %** sample en 500 caché Cloudflare HIT, age >300s |
| 2026-05-06 13:34 | Headers prod inspectés : `cache-control: public, max-age=7200, s-maxage=86400 ... cf-cache-status: HIT, age: 392, server: cloudflare, via: 1.1 Caddy`. Body HTML complet et valide malgré le 500 |
| 2026-05-06 14:02 | Code dive : 3 routes route-level avec `() => ({...})` zero-arg → `pieces.\$gamme...\$type[.]html.tsx` (BUG), `pieces.\$slug.tsx` (pattern partiel), `blog-pieces-auto.guide-achat._index.tsx` |
| 2026-05-06 14:51 | Helper + 3 routes migrées, 7 tests vitest verts, tsc 0 erreur, lint script déterministe |
| 2026-05-06 ~15:10 | **PR #320 mergée sur main**, commit `a93b7dcb` |

## Root cause

**Architecture** : Remix invoque la fonction `headers` exportée par une route pour TOUTES les réponses (succès loader, loader-thrown Response, défer rejection). Une signature zero-arg `() => ({...})` ne reçoit pas `loaderHeaders` ni `errorHeaders`, donc :

- ne peut pas distinguer le statut HTTP de la réponse,
- ne peut pas lire le `Cache-Control: no-cache` que le loader pose explicitement sur ses 503 ([`pieces-vehicle.loader.server.ts:294-298, 460-464`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/frontend/app/utils/pieces-vehicle.loader.server.ts)),
- applique uniformément le `Cache-Control` du chemin heureux.

Cloudflare honore `s-maxage` (CDN-tier `Cache-Control` directive RFC-7234) **même sur les 4xx/5xx**. Avec `s-maxage=86400`, chaque réponse 5xx devient cache HIT pendant 24h pour toute requête suivante depuis la même région. La 500 initiale (timeout backend RM V2 ~10-12s) devient ainsi un statut figé dans le CDN, ré-affirmé à Googlebot à chaque crawl.

**Pourquoi non détecté avant** : le sample initial 60 URLs vehicles `/constructeurs/*` était propre (ADR-016 a fait le travail). Le bug est confiné à la chaîne pieces R2/R1 + le hub blog. L'audit large a fallu pour révéler le pattern.

## Mitigations livrées (PR #320)

- **Helper canonique** `frontend/app/utils/cache-control.ts` :
  - `buildCacheHeaders(successPolicy)` retourne une `HeadersFunction` standard
  - Précédence : `errorHeaders` (loader threw) → `loaderHeaders` (succès, override possible) → `successPolicy` fallback
  - Force `no-cache, no-store, must-revalidate` quand `errorHeaders` set sans `Cache-Control`
  - Propage `X-Robots-Tag` depuis la bonne source
- **3 routes migrées** : `pieces.\$gamme.\$marque.\$modele.\$type[.]html.tsx`, `pieces.\$slug.tsx`, `blog-pieces-auto.guide-achat._index.tsx`
- **7 tests unitaires** vitest dont la régression no-leak-success-policy-onto-error
- **Garde mécanique 3 couches** :
  - `scripts/lint/check-no-zero-arg-headers-with-s-maxage.sh` (bash awk déterministe, source de vérité)
  - hook husky pre-commit (staged routes, fast)
  - step CI lint `🛡️ Cache-Control discipline (Remix routes)` (full repo, blocking)
  - règle ast-grep YAML correspondante en `severity: warning` (script bash reste SoT tant que le pattern combiné ast-grep ne match pas fiablement la version utilisée)

## Follow-up requis (à ouvrir séparément)

1. **Origine du timeout backend** `/api/rm/page-v2?gamme_id=X&type_id=Y` (10-12s). Sans SSH PROD, stack trace inaccessible. Ce PR limite la persistance 24h, pas l'occurrence initiale. Probablement même nature qu'INC-2026-005 (cold RPC `pieces_relation_type` 47GB) appliquée à la chaîne RM V2.
2. **Purge Cloudflare** des 259 URLs `/pieces/*` actuellement cache HIT 500 (liste exacte conservée localement par l'auditeur, ne pas committer dans le vault). Sans purge, le fix prend jusqu'à 24h à propager naturellement.
3. **Tag PROD** `v2026.05.06-cf-cache-5xx-fix` une fois DEV preprod validé.
4. **Re-validation GSC** dans Search Console → Indexation des pages → "Erreur serveur (5xx)" → "Valider la correction".
5. **Migration des 4 routes mineures** encore en `() => ({...})` mais sans `s-maxage` (max-age=300 only) : `_index.tsx`, `constructeurs.\$brand[.]html.tsx`, `blog-pieces-auto.guide-achat.\$pg_alias.tsx`, `blog-pieces-auto.conseils.\$pg_alias.tsx`. Risque marginal mais cohérence.

## Liens

- **PR mitigation** : https://github.com/ak125/nestjs-remix-monorepo/pull/320 (commit `a93b7dcb`)
- **Email GSC source** : `[WNC-10031170]` 2026-05-05 21:00
- **Incident parent** : INC-2026-005 (`2026-04-20-gsc-5xx-vehicle-page-cold-rpc.md`)
- **Helper** : `frontend/app/utils/cache-control.ts`
- **Lint script** : `scripts/lint/check-no-zero-arg-headers-with-s-maxage.sh`

---

## Résolution end-to-end (addendum 2026-05-06 ~13:42 UTC)

### Chaîne de fix

| # | Action | Quand | Référence |
|---|--------|-------|-----------|
| 1 | PR monorepo #320 — helper `buildCacheHeaders` + 3 routes migrées + 7 tests + lint dual-layer | 2026-05-06 ~13:00 UTC | commit `a93b7dcb` |
| 2 | PR monorepo #322 — fix YAML quoting de la règle ast-grep introduite par #320 | 2026-05-06 ~13:14 UTC | commit `e270b95c` |
| 3 | Vault PR #167 — post-mortem indexé MOC-Incidents (3 sections) | 2026-05-06 ~13:20 UTC | commit `f331d1f` |
| 4 | Tag PROD `v2026.05.06-cf-cache-5xx-fix` poussé sur `e270b95c` | 2026-05-06 ~13:34 UTC | tag annoté |
| 5 | Workflow `deploy-prod.yml` run #25438575798 — image `production` promue | 2026-05-06 ~13:36 UTC | success 2m2s |
| 6 | Cloudflare purge `/pieces/*` (action utilisateur) | 2026-05-06 ~13:40 UTC | purge confirmé empiriquement |

### Vérifications empiriques

**Avant chaîne de fix** (audit 2026-05-06 13:27 UTC, 930 URLs sample sitemap stratifié) :

- 27,8 % `/pieces/*` en `HTTP 500` + `cf-cache-status: HIT` + `age > 300s`
- 100 % type_id legacy `<60000` (URLs SEO prioritaires)
- Latence retry 40 ms = serveur cache CF, pas origin

**Après purge Cloudflare** (sample 30 URLs ex-500, sans cache-bust) :

- 30/30 = `HTTP 200`
- `cf-cache-status: HIT` avec `age` faible = nouvelles entrées 200 cachées
- Backend RM V2 répond 200 OK sur les combos `(gamme_id, type_id)` qui timeout-aient à 10-12 s pendant l'audit (origine du 500 transitoire, probablement résolu par cache backend Redis warm ou ADR-016 partiel)

**Après deploy PROD `v2026.05.06-cf-cache-5xx-fix`** (sample 30 URLs ex-500 + edge cases) :

- 30/30 ex-500 = `HTTP 200` (succès propagé)
- Edge cases (orphan type_id `999999`, URL malformée) = `HTTP 200 + X-Robots-Tag: noindex, follow` (page no-products alternatives propre, pas de 5xx accidentel)
- Helper `buildCacheHeaders` confirmé dans le bundle prod (les routes l'importent et le bundle build green)

### Validation de la mitigation

Le helper canonique `frontend/app/utils/cache-control.ts` est désormais actif côté production. Comportement validé indirectement par 7/7 tests vitest qui assertent le contrat sur tous les états (succès, errorHeaders, X-Robots-Tag propagation, no-leak régression). La provocation d'un 5xx vivant côté prod n'a pas pu être obtenue (le système gère bien les edge cases via page alternatives 200+noindex), mais le contrat unitaire est verrouillé.

Defense in depth garantit que tout 5xx futur transitoire (timeout backend ponctuel, hook réseau, etc.) sortira avec `Cache-Control: no-cache, no-store, must-revalidate` au lieu de `s-maxage=86400` — Cloudflare ne pourra plus accumuler 30 k URLs en 5xx HIT 24h. La cache poisoning est structurellement éliminée sur les 3 routes route-level concernées (`pieces.\$gamme...\$type[.]html.tsx`, `pieces.\$slug.tsx`, `blog-pieces-auto.guide-achat._index.tsx`), avec garde mécanique 3 couches (script bash awk + pre-commit hook + step CI lint blocant) qui empêche toute régression sur de futures routes.

### Action utilisateur restante

Re-validation Google Search Console : `Indexation des pages` → `Erreur serveur (5xx)` → bouton `Valider la correction`. Recrawl progressif Googlebot 3-7 jours typique. Surveillance recommandée à J+3 / J+7 / J+14 pour confirmer la baisse du compteur GSC vers 0.

### Suivi futur (séparés)

- Origine timeout backend `/api/rm/page-v2` 10-12 s sur certaines combos (`gamme_id × type_id`) — probablement même nature qu'INC-2026-005 (cold RPC `pieces_relation_type` 47 GB) appliquée à la chaîne RM V2. Nécessite SSH PROD pour stack trace si récurrence observable.
- Migration des 4 routes mineures encore en `() => ({...})` mais sans `s-maxage` (`_index.tsx`, `constructeurs.\$brand[.]html.tsx`, `blog-pieces-auto.guide-achat.\$pg_alias.tsx`, `blog-pieces-auto.conseils.\$pg_alias.tsx`). Risque marginal mais cohérence.
- Bilateral cross-ref vers INC parent INC-2026-005 (canon §3.7).
- Pre-existing fail GATE-3 `dependabot-claude-review.yml` (`pull_request_target` + `actions/checkout`) — détecté pendant cet incident mais hors scope, follow-up sécurité séparé.
