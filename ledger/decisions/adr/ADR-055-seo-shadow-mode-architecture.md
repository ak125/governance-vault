---
id: ADR-055
title: SEO Shadow Mode Architecture (observability avant flip mode=on)
status: accepted
date: 2026-05-09
deciders: [Fafa]
related: [ADR-031, ADR-037, ADR-039, ADR-047, ADR-048, MOC-Roadmap-2026, R-SEO-09]
---

# ADR-055: SEO Shadow Mode Architecture

## Context

Le plan stratégique seo-v9 (cf. `ledger/knowledge/seo-v9-cascade-state-20260508.md`) a livré
sur main un module observability **SeoShadowObservatoryModule** + premier usage R7 (hub marque)
et R8 (fiche véhicule) en mode shadow strictement non-bloquant (cf. cascade PRs #398, #399,
#404, #406, #407 mergées 2026-05-09).

L'objectif est de **comparer la sortie SEO legacy** (RPC `get_brand_page_data_optimized` /
`get_vehicle_page_data_cached`) à la **sortie chain** (`SeoChainOrchestratorService`, ADR-047)
sans muter la réponse servie, afin de décider empiriquement si la chaîne SEO peut remplacer
le legacy en production.

Cette ADR formalise les invariants du shadow mode et le pré-requis canon pour tout futur
flip `mode=on` sur les surfaces SEO.

Sans ADR formalisée, le code shadow shippé sur main n'est **pas LIVE** au sens canon
(cf. mémoire `feedback_canon_rule_live_iff_adr_accepted.md` : "Chantier `LIVE` ssi
ADR.status=accepted. Code shippé ≠ canon LIVE").

## Decision

### D1. Shadow mode = lecture passive uniquement, jamais mutation

Le `SeoShadowObservatoryModule` est l'**unique** chemin canon pour observer une divergence
legacy↔chain. L'API publique `observatory.observe(input)` est **synchrone** (return immédiat),
le travail réel court via `setImmediate` (vraie fire-and-forget). Aucun `await` sur le chemin
réponse HTTP du caller.

Il est **interdit** d'introduire du shadow inline dans un service métier (pattern PR-3
rm-builder, à retrofit) — toute observation passe par le module dédié.

### D2. Trois modes de feature flag, mais le code n'expose que deux

Convention `SEO_CHAIN_<surface>_MODE` (cf. ADR-047) avec valeurs `off | shadow | on`. Mais
**le code livré ne contient pas la branche `mode === 'on'`** dans les modules d'observation —
un flip ENV ne peut pas activer la chaîne en prod sans modification de code.

### D3. Defense-in-depth contre flip `mode=on` accidentel (4 couches indépendantes)

| Couche | Mécanisme |
|---|---|
| Zod env | `SEO_CHAIN_R*_MODE=tru` (typo) → boot fail. |
| Boot guard | `mode=on` détecté → `throw` au démarrage NestJS, container ne boot pas. |
| CI guard | `.github/workflows/seo-shadow-flag-guard.yml` refuse `=on` dans `.env*`/`docker-compose*`/workflows/secrets. |
| Lint ast-grep | `.ast-grep/rules/seo-shadow-no-await.yml` interdit `await observatory.observe()`. |
| ADR | Cette ADR + sign-off explicite pour le flip. |

Trois modifications coordonnées (code + ADR + ENV) sont nécessaires pour activer `on`.

### D4. Persistance via `__seo_event_log` réutilisé (pas de migration DB dédiée)

Le sink shadow utilise l'`event_type='anomaly_detected'` existant + `payload.subtype LIKE
'seo.shadow.<surface>.divergence'` (cf. cascade PR-6 §2bis Adjusted). Aucune migration DB
n'est requise. La sémantique "divergence shadow = anomalie observée" est cohérente.

`severity` mapping : `info` quand pas de policy_divergence, `medium` quand canonical ou
robots divergent.

### D5. Sampler déterministe + cron purge TTL 30j livrés dans la même PR

`sha1(${surface}:${entityId})` % 2^32 / 2^32 < rate. La même paire (surface, entityId) est
**toujours** ou **jamais** échantillonnée pour un taux fixe. Reproductibilité tests +
diff stable + couverture homogène.

Default conservateur **0.01 (1%)** au merge — volume `__seo_event_log` inconnu sur cette
nouvelle source. Augmenter à 0.05/0.1 en preprod après validation J+1.

Cron purge `payload->>'subtype' LIKE 'seo.shadow.%.divergence' AND created_at < now() -
interval '30 days'` co-livré pour borner volume DB.

### D6. R8 canonical comparison désactivée à J0 (limite connue)

Le frontend Remix R8 applique un redirect 301 `marque_alias-marque_id` mismatch
([constructeurs.$brand.$model.$type.tsx:317-330](https://github.com/ak125/nestjs-remix-monorepo/blob/main/frontend/app/routes/constructeurs.%24brand.%24model.%24type.tsx#L317-L330))
que le backend ne reproduit pas. Comparer les canonicals R8 backend produirait une avalanche
de faux positifs.

Skip explicite dans `SeoShadowDiffEngine` quand `surface === 'R8_VEHICLE'` :
`canonical_eq=null` + `skip_reason='r8_frontend_redirect_logic_not_reproduced'`. R8
`policy_divergence` reste piloté par `robots_eq` uniquement.

**Issue follow-up** : reproduire la logique de redirect backend-side (lever le skip).

## Invariants

- **I1** : `SeoShadowObservatoryModule` = unique chemin canon pour shadow SEO. Pas de shadow
  inline dans un service métier (R-SEO-canon).
- **I2** : `observatory.observe()` est **sync**. Lint ast-grep `seo-shadow-no-await.yml` actif
  pre-commit + CI.
- **I3** : Aucune branche `mode === 'on'` dans le code des callers shadow. Ajout futur =
  PR séparée + référence à cette ADR.
- **I4** : Persistance `__seo_event_log` via `event_type='anomaly_detected'` +
  `payload.subtype` figé par PR. Aucune URL canonical brute persistée — uniquement hashes
  sha256 12 hex (cardinalité maîtrisée).
- **I5** : Sampler **déterministe** (sha1 hash). `Math.random()` interdit (anti-pattern
  reproductibilité).
- **I6** : Cron purge TTL 30j co-livré avec tout sink shadow. WHERE clause stricte
  (`payload->>'subtype' LIKE 'seo.shadow.%.divergence'`) — ne touche aucun autre consommateur.
- **I7** : `READ_ONLY=true` env var → cron purge no-op (gate au processor, pas au scheduler).

## Pré-requis canon pour flip `mode=on`

Les 5 conditions doivent toutes être satisfaites pour ouvrir une PR de flip :

1. **Shadow observation 7j minimum** sur preprod DEV (`46.224.118.55`) avec sample_rate ≥ 0.01.
2. **Bilan SQL `policy_divergence` count** :
   ```sql
   SELECT payload->>'surface' AS surface,
          count(*) FILTER (WHERE payload->>'policy_divergence' = 'true') AS policy_div,
          count(*) AS total
   FROM __seo_event_log
   WHERE event_type = 'anomaly_detected'
     AND payload->>'subtype' LIKE 'seo.shadow.%.divergence'
     AND created_at > now() - interval '7 days'
   GROUP BY 1;
   ```
   Si `policy_div > 0` sur une surface : **STOP**, remontée utilisateur, alignement
   chaîne→legacy ou legacy→chaîne avant tout flip.
3. **Sentry warn count** sur événements `[SEO_SHADOW][<surface>] policy_divergence` <
   threshold (0 idéalement, ≤ 1% total observations).
4. **ADR amendement** : cette ADR référencée dans la PR de flip + checkpoint dans le PR body
   (`Self-review verdict: APPROVE` cf. mémoire `vault-pr-self-review-marker-format.md`).
5. **Sign-off explicite** de Fafa (decider) — pas d'auto-merge sur la PR de flip.

## Surfaces actuellement câblées (état 2026-05-09)

| Surface | Service caller | Mode default | Status |
|---|---|---|---|
| R7_BRAND_HUB | `BrandRpcService.getBrandPageDataOptimized` | `off` | Câblé |
| R8_VEHICLE | `VehicleRpcService.getVehiclePageDataOptimized` | `off` | Câblé (canonical skip) |

## Surfaces planifiées (à wirer dans futurs PRs)

| Surface | Caller futur | ADR follow-up |
|---|---|---|
| R0_HOME | `HomeService` (PR-8 plan seo-v9) | À ouvrir |
| R3_ADVICE / BLOG_* | Routes blog (PR-12 différé) | À ouvrir |
| R1_GAMME_ROUTER (rm-builder) | `rm-builder` (retrofit PR-3) | Retrofit, pas nouvelle ADR |
| R1_GAMME_VEHICLE_ROUTER (gamme-rest) | `GammeResponseBuilder` (retrofit PR-5) | Retrofit |

## Conséquences

- **Code shadow seo-v9 atterri sur main 2026-05-09** = officiellement LIVE (ADR.status=accepted).
- **Activation preprod possible immédiatement** : `SEO_CHAIN_R7_MODE=shadow` +
  `SEO_CHAIN_R8_MODE=shadow` + `SEO_CHAIN_SHADOW_SAMPLE_RATE=0.01` sur DEV.
- **Retrofit PR-3 rm-builder + PR-5 gamme-rest** sur le module shadow = mandatory pour
  cohérence I1 (issue follow-up monorepo).
- **R8 redirect logic backend-side** = mandatory pour lever skip canonical R8 (issue
  follow-up monorepo).

## Références

- Plan PR-6 : `home/.claude/plans/pr-6-r7-brand-rpc-fancy-blum.md`
- Mémoire cascade : `feedback_seo_shadow_mode_hygiene.md` (7 règles transverses)
- Mémoire état : `seo-v9-cascade-state-20260508.md`
- ADR-031 : Canonical 4-layer framework (raw/wiki/exports/consumers)
- ADR-037 : RoleId enum canon
- ADR-047 : SeoChainOrchestratorService canon
- R-SEO-09 : URL Immutability rule (canonical never modified without explicit user signoff)
