---
id: INC-2026-006
type: incident
title: 503 systémique /constructeurs/*/type.html — allowlist RPC + image preprod obsolète
date: 2026-04-21
date_detected: 2026-04-21T13:15:00Z
date_resolved: 2026-04-21T13:57:00Z
severity: high
status: closed-with-structural-fix
impact_duration: "67 minutes (13:15 → 13:57 UTC)"
affected_systems:
  - route-frontend: /constructeurs/{brand}/{model}/{type}.html (R8)
  - backend-endpoint: /api/vehicles/types/*/page-data-rpc
  - rpc-gate: allowlist
  - ci/cd: deploy-prod.yml (promote preprod image)
root_cause: "Double bug — (1) ADR-016 Phase 2 a renommé get_vehicle_page_data_optimized → get_vehicle_page_data_cached sans MAJ allowlist RPC Gate. (2) deploy-prod.yml a promu l'image preprod flottante sans vérifier que son SHA correspond au tag git — le premier hotfix a donc promu une vieille image sans fix."
related_rules:
  - rpc-governance
related_adrs:
  - ADR-016-vehicle-page-matview-persistence
reviewed_by: "Claude Opus 4.7"
tags:
  - incident/high
  - domain/seo
  - tech/ci-cd
  - tech/docker
  - tech/rpc-gate
  - post-mortem
  - resolved
  - structural-fix
---

# INC-2026-006 : 503 systémique véhicule — allowlist RPC + image preprod obsolète

> [!warning] Résumé
> À 12:50 UTC, tag `v2026.04.21-adr-017-rpc-cleanup` déclenche `deploy-prod.yml` qui promeut l'image `:preprod` vers `:production`. Cette image (commit `0540d3b7`) contenait le code ADR-016 Phase 2 qui appelle `get_vehicle_page_data_cached`, mais son allowlist RPC Gate n'avait **pas** été mise à jour. Toutes les pages `/constructeurs/*` retournent **503 systématique** pendant 67 min. Deux PR de hotfix nécessaires : la première (v1) a promu une **autre image obsolète** car `deploy-prod.yml` ne vérifie pas la cohérence SHA. Résolu par tag v2 après build preprod terminé.

## Timeline

| Heure UTC | Évènement |
|-----------|-----------|
| 12:50 | Tag `v2026.04.21-adr-017-rpc-cleanup` pushé → `deploy-prod.yml` promeut image `:preprod` (commit `0540d3b7`) vers `:production` |
| 12:59 | Deploy PROD v1 = success, health check OK (`/health` 200) |
| 13:15 | **503 détecté** via tests smoke : `/constructeurs/bmw-33/x2-f39-33104/18-d-sdrive-62290.html` = HTTP 503 en 90 ms |
| 13:17 | Root cause #1 : backend appelle `get_vehicle_page_data_cached`, allowlist n'a que l'ancien nom → `RpcBlockedError` → `ServiceUnavailableException` |
| 13:19 | PR #93 — ajout 4 RPC ADR-016 à `rpc_allowlist.json` (2 copies : backend/ + root) |
| 13:21 | PR #93 merged main (commit `7646b472`) → build preprod queued |
| 13:22 | Tag `v2026.04.21-hotfix-rpc-allowlist` pushé |
| 13:25 | **Deploy PROD hotfix v1 = success — mais 503 PERSISTE** |
| 13:30 | Root cause #2 trouvé : le tag a promu l'image `:preprod` qui datait de `0540d3b7`, pas de `7646b472` (build pas encore terminé) |
| 13:40 | Build preprod sur `7646b472` = success (E2E Smoke flaky, non bloquant) |
| 13:45 | Tag `v2026.04.21-hotfix-rpc-allowlist-v2` pushé sur `7646b472` |
| **13:57** | **Deploy PROD v2 = success, `/constructeurs/*` = HTTP 200** (245-345 ms) |
| 14:05 | DB alias temporaire `get_vehicle_page_data_optimized → _cached` dropped |
| 14:15 | PR #fix/deploy-safety : 3 mesures structurelles (ce document) |

## Impact

- **URLs affectées** : 100% des pages véhicule R8 (`/constructeurs/*/type.html`) + `/api/vehicles/types/*/page-data-rpc`
- **Durée** : **67 min** 503 systémique
- **Trafic e-commerce** : **non impacté** (`/pieces/*` et cart fonctionnaient — autres RPC)
- **SEO Googlebot** : 67 min de 5xx sur pages véhicule — à surveiller sur GSC 24-48h
- **Utilisateurs** : page-not-available pendant 1h sur toute la branche R8

## Root Cause — double bug

### Bug #1 — Allowlist RPC Gate non mise à jour (Phase 2 ADR-016)

La PR fc9b94af (ADR-016 Phase 2) a :
- Réécrit `vehicle-rpc.service.ts` pour appeler `get_vehicle_page_data_cached` au lieu de `get_vehicle_page_data_optimized`
- Mis à jour le `r8-vehicle-enricher.service.ts`
- **Oublié** de mettre à jour `governance/rpc/rpc_allowlist.json`

Au runtime, `callRpc('get_vehicle_page_data_cached', …, { source: 'api' })` → gate évalue → non présent dans allowlist → source=api + prod → `UNKNOWN_BLOCKED_PROD` → `RpcBlockedError` → catch controller → `ServiceUnavailableException(503)`.

Pourquoi DEV preprod n'a pas détecté :
- Le deploy preprod charge le **même fichier allowlist depuis l'image** (statique)
- Mais E2E Smoke Tests en CI couvrait `/pieces/*`, pas `/constructeurs/*` — le bug s'est glissé sans test échoué
- Le `prod-smoke-tests.yml` scheduled ne tapait pas sur `/constructeurs/*` non plus

### Bug #2 — `deploy-prod.yml` promeut une image dont le SHA ne correspond pas au tag

Le workflow actuel :
```yaml
docker pull massdoc/nestjs-remix-monorepo:preprod
docker tag preprod production
docker push production
```

**Aucune vérification** que le tag `:preprod` correspond bien au commit du tag git. Conséquence :
- Tag `v2026.04.21-hotfix-rpc-allowlist` a été pushé à 13:22
- Build preprod du merge commit `7646b472` était encore **queued** (runner self-hosted saturé)
- Le `:preprod` actif pointait toujours sur l'image `0540d3b7` (qui n'a PAS le fix)
- Promotion → production sans fix → **503 persiste**

## Résolution

### Immédiat (incident fermé 13:57)

1. Attente fin du build preprod (commit `7646b472`) → 13:40 success
2. Nouveau tag `v2026.04.21-hotfix-rpc-allowlist-v2` sur même commit → promote la nouvelle image
3. Deploy PROD v2 = success → /constructeurs/* = HTTP 200

### Structurel (PR en cours, évite récidive)

Trois mesures dans `.github/workflows/` + script dédié :

**1. Labels OCI sur l'image Docker** (`build.yml`) :
```yaml
tags:
  - massdoc/nestjs-remix-monorepo:preprod
  - massdoc/nestjs-remix-monorepo:sha-${{ github.sha }}   # ← nouveau, pinning
labels:
  - org.opencontainers.image.revision=${{ github.sha }}    # ← introspection
```

**2. SHA consistency gate** (`deploy-prod.yml`) :
```yaml
IMAGE_SHA=$(docker inspect :preprod --format='{{ .Config.Labels "org.opencontainers.image.revision" }}')
if [ "$IMAGE_SHA" != "$GITHUB_SHA" ]; then
  echo "FATAL: :preprod ne correspond pas au commit du tag"
  exit 1
fi
```

**3. RPC allowlist coverage gate** (`scripts/ci/check-rpc-allowlist-coverage.sh`) :
- Grep `callRpc(..., { source: 'api' })` en multiline dans `backend/src/`
- Compare chaque nom RPC extrait avec `backend/governance/rpc/rpc_allowlist.json`
- Fail CI si un nom manque

Wired dans `ci.yml` job `rpc-gate-check`.

## Lessons Learned

1. **Les tags logiques flottants (`:preprod`, `:production`) sont des pièges**. Dès qu'un autre build écrase `:preprod`, promote → mauvaise image. Pinning par SHA obligatoire pour les déploiements.

2. **Renommer une RPC sans grep global est dangereux**. Au-delà du call site, il y a :
   - L'allowlist RPC Gate (backend + root)
   - Les test mocks éventuels
   - Les types générés `database.types.ts`
   - Les callers tiers (r8-vehicle-enricher, admin endpoints)

3. **CI preprod-deploy + CI E2E = succès partiel n'est pas succès.** Le job E2E Smoke a failed pendant que Deploy PREPROD a success. Le run global était marqué "failure" mais l'image était bien publiée. Ambiguïté à éviter : soit chaque job a une conséquence claire, soit le global status est impérieux.

4. **Rollback DB via alias = pansement sans valeur** pour ce cas précis. Le backend appelait `get_vehicle_page_data_cached` directement ; recréer `get_vehicle_page_data_optimized` n'a rien changé côté flow. **Toujours vérifier le call path complet avant rollback.**

5. **`/api/rm/alternatives` a continué de fonctionner** → la zone d'impact était limitée à R8. **Chance** : l'incident n'a pas cassé l'e-commerce. Si un jour un RPC critique de commande subit la même classe de bug, SEV1 immédiat.

## Actions Correctives

- [x] **[DONE]** Hotfix allowlist merged (PR #93) — 13:21
- [x] **[DONE]** Re-tag v2 + deploy prod success — 13:57
- [x] **[DONE]** DB alias temporaire nettoyé — 14:05
- [ ] **[THIS PR]** SHA consistency gate + OCI labels + RPC coverage CI gate — 14:15 (en cours)
- [ ] **[FOLLOW-UP]** Ajouter une ligne de smoke test `/constructeurs/*` au scheduled `prod-smoke-tests.yml` (blindspot actuel)
- [ ] **[FOLLOW-UP]** Documenter dans le runbook de migration : "toute nouvelle RPC DOIT passer par le gate coverage CI avant merge"
- [ ] **[FOLLOW-UP]** Nettoyer `check_piece_vehicle_compatibility` (référencée par le code mais n'existe pas en DB — dette pré-existante révélée par le gate)

## Preuves

- Commits : `fc9b94af` (ADR-016 Phase 2, cause #1), `f9c8c838` (hotfix allowlist), `7646b472` (merge PR #93), tag `v2026.04.21-hotfix-rpc-allowlist-v2`
- Runs CI : 24724745223 (Deploy PREPROD success, E2E flaky)
- DB evidence : `get_vehicle_page_data_cached(62290)` = 2 ms pendant que backend retournait 503 (DB OK, gate = le problème)
- __error_logs 13:24:31-13:24:52 UTC : 9+ entrées `err_subject=ERROR_ServiceUnavailableException` sur `/api/vehicles/types/*/page-data-rpc`
- Smoke test 13:57 post-v2 : 4/4 pages `/constructeurs/*` = HTTP 200, 245-345 ms

## Communication

- [x] Équipe (solo) notifiée en live pendant l'incident
- [x] Trigger J+1 auto-check (`trig_01XGve2U3fZfit4B3BV2igRG`) couvrira ADR-017 demain matin — confirmer que rien ne régresse
- [ ] PR structurelle mergée et taguée pour couvrir la classe entière de bug

## Liens

- Related : [[ADR-016-vehicle-page-matview-persistence]] (cause du renommage)
- Related : [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc]] (incident parent)
- Related knowledge : [[mcp-vs-python-direct-pg]]
- Related memory : `deployment-workflow.md` (clarification push main = DEV preprod)

---

*Créé le : 2026-04-21T14:15:00Z*
*Dernière mise à jour : 2026-04-21T14:15:00Z*
