---
id: INC-2026-005
type: incident
title: GSC 30,5k pages 5xx — cold RPC vehicle-page (pieces_relation_type 47GB)
date: 2026-04-20
date_detected: 2026-04-15
date_resolved: 2026-04-13
severity: high
status: closed-with-followup
impact_duration: "~48h observables (2026-04-13 → 2026-04-15), stock SEO résiduel 30,5k URLs"
affected_systems:
  - route-frontend: /constructeurs/{brand}/{model}/{type}.html (R8)
  - route-frontend: /pieces/{gamme}/{marque}/{modele}/{type}.html (R2)
  - rpc: get_vehicle_page_data_optimized
  - table: pieces_relation_type (47GB, 368M rows)
  - cache: Redis (stale-while-revalidate)
  - cdn: Caddy reverse proxy
root_cause: "Cold RPC p99 ≈ 4s sur pieces_relation_type 47GB/368M rows dépassait le timeout backend 1500ms. Cold hits (post-deploy, éviction Redis, type_id rare) renvoyaient 503 systématiquement à Googlebot."
related_rules:
  - performance-budget-ttfb
  - seo-http-status-contract
related_adrs:
  - ADR-016-vehicle-page-matview-persistence
owner: "@automecanik.seo"
reviewed_by: "Claude Opus 4.7"
tags:
  - incident/high
  - domain/seo
  - domain/catalog
  - tech/supabase
  - tech/postgres
  - tech/redis
  - tech/caddy
  - post-mortem
  - resolved
  - followup-adr-016
---

# INC-2026-005 : GSC 30,5k pages 5xx — cold RPC vehicle-page

> [!warning] Résumé
> Du **2026-03 (fenêtre estimée)** au **2026-04-13 22:30 UTC**, un cold hit sur `get_vehicle_page_data_optimized` (p99 ≈ 4s) dépassait le timeout backend 1500ms et renvoyait **503** à Googlebot. Google Search Console a agrégé **30,5k URLs** en statut "Erreur serveur (5xx)". Validation GSC lancée le 15/04, marquée **échec le 18/04** parce que le recrawl Googlebot est étalé sur plusieurs jours. Correctif palliatif déployé le 13/04 (`eff30b7f`). Live checks 20/04 : **10/10 URLs passent** (200/301). Cause structurelle non corrigée (voir ADR-016).

## Timeline

| Heure UTC | Événement |
|-----------|-----------|
| ~2026-03-15 (estimé) | Incident latent — cold RPC sous-dimensionné (1500ms < p99 4s) |
| 2026-04-13 22:43 | **Commit `eff30b7f`** — timeout adaptatif 3s/9s + R8 500ms + Caddy retry |
| 2026-04-15 | GSC ouvre la fenêtre de validation "Erreur serveur (5xx)" |
| 2026-04-18 | GSC marque validation **échouée** (recrawl incomplet, ≠ bug toujours actif) |
| 2026-04-20 14:00 | Re-check 10 URLs flagged → 100% 200/301 |
| 2026-04-20 14:15 | `__error_logs` depuis buffer activé (`8f0b7b91`) = 0 entrée 5xx |
| 2026-04-20 15:30 | 🏁 **Incident clos** — cause racine structurelle escaladée vers ADR-016 |

## Impact

- **URLs affectées** : 30,5k (agrégation GSC)
- **Utilisateurs finaux** : impact minoritaire (recrawl Googlebot, pas trafic humain direct)
- **SEO** : aucun desindex permanent attendu — 503 = "retry later" pour Google
- **Indicateurs** :
  - p99 cold path `get_vehicle_page_data_optimized` = 4064ms (vs timeout 1500ms → 503 garanti)
  - p99 warm path = 42-48ms via Redis
  - `pieces_relation_type` : 47GB / 368M rows / 20GB d'index dont 1 "popular" hardcodé top-10 type_ids

## Root Cause

> [!bug] Cause racine — RPC sur-dimensionnée pour une table de 368M rows
> `get_vehicle_page_data_optimized(p_type_id integer)` agrège 7 sections incluant une jointure sur `pieces_relation_type` (47GB, 368M lignes). Le plan Postgres utilisait un nested loop avec ~18K random I/O pour les type_ids hors du top-10 (qui bénéficient d'un index partiel hardcodé `idx_pieces_relation_type_popular`). Sur un cold path (Redis absent), cela donnait p99 ≈ 4s, dépassant le timeout backend 1500ms. Résultat : 503 systématique à Googlebot pour les 53k types hors top-10, à chaque fois que Redis ne cachait pas encore la ligne.

**Facteurs aggravants :**

1. **Index partiel hardcodé top-10** (`idx_pieces_relation_type_popular WHERE rtp_type_id IN (17173, 17458, ...)`) : symptôme d'un précédent bricolage, masquait le problème pour 10 types sur ~54k.
2. **Absence de cache pré-chauffé** : chaque éviction Redis = rafale de 503 sur le long tail.
3. **Pas de circuit breaker** : Googlebot crawlait de façon parallèle → 30k requêtes cold en quelques heures.
4. **Timeout backend plus strict que p99 RPC** : inversion du contrat (le timeout doit toujours être > p99 cible, pas le contraire).

## Résolution — palliatif immédiat (commit eff30b7f, 13/04)

```diff
- private readonly RPC_TIMEOUT_MS = 1500;
+ private readonly RPC_TIMEOUT_MS       = 3000;  // stale présent
+ private readonly RPC_COLD_TIMEOUT_MS  = 9000;  // stale absent (cold first hit)
+ private readonly R8_TIMEOUT_MS        =  500;  // overlay SEO non-critique
```

- Timeout adaptatif : **3s** quand stale Redis dispo (protège LCP via SWR), **9s** quand stale absent (cold doit aboutir, 1s marge avant timeout frontend 10s).
- R8 overlay plafonné à 500ms (SEO bonus, non-bloquant).
- Caddy `lb_try_duration=2s / lb_try_interval=250ms` — retry uniquement sur erreurs transport (dial refused, conn reset), pas sur 5xx.

> [!warning] Status du palliatif
> Le fix **tolère** la RPC lente au lieu de la **corriger**. Les cold hits longs (mesurés 5,4s sur `opel-astra-h-18301` le 20/04) restent dans la fenêtre 9s mais exposent le p99 à un risque de régression si :
> - la table `pieces_relation_type` continue de grossir (TecDoc sync augmente régulièrement)
> - Redis subit une éviction de masse (ex. post-deploy, OOM)
> - Googlebot parallélise davantage son crawl

## Lessons Learned

1. **Un timeout n'est jamais une solution, c'est une tolérance** — le vrai contrat est `p99 RPC < budget SLA utilisateur`, pas `timeout = budget`.
2. **Les index partiels hardcodés sur un top-N sont un code smell** — ils masquent le problème structurel et introduisent une dette (le top-10 de 2023 n'est plus le top-10 de 2026).
3. **GSC "validation échouée" ≠ bug encore actif** — le recrawl étale 30k URLs sur plusieurs jours; vérifier d'abord par checks directs avant de redéployer.
4. **368M rows × 7 jointures dans une RPC SSR n'est pas un pattern durable** — il faut précalculer.
5. **Absence de buffer error_logs = cécité historique** : impossible de savoir après-coup ce qu'il s'est passé entre 15/04 et 18/04 car `__error_logs` n'a été activé que le 20/04 (commit `8f0b7b91`).

## Actions Correctives

- [x] **[DONE] Palliatif déployé** — timeout adaptatif + Caddy retry (commit `eff30b7f`) — 13/04
- [x] **[DONE] Buffer error_logs** activé pour observer les récidives (commit `8f0b7b91`) — 20/04
- [ ] **[CRITICAL] ADR-016** — décider et implémenter la solution structurelle (matview persistante ou index covering + query rewrite). Owner: @automecanik.seo — Deadline: 2026-05-04
- [ ] **[HIGH] Supprimer `idx_pieces_relation_type_popular`** après mise en place ADR-016 (dette bricolage) — Owner: @automecanik.seo — Deadline: 2026-05-11
- [ ] **[MEDIUM] Alerting** : seuil `COUNT(*) WHERE err_status >= 500` > 10/h sur `__error_logs` → PREV-1 Gmail — Owner: @automecanik.seo — Deadline: 2026-04-27
- [ ] **[MEDIUM] Dashboard Supabase** : p50/p95/p99 `get_vehicle_page_data_optimized` par tranche de type_id (top-100 vs long tail) — Owner: @automecanik.seo — Deadline: 2026-05-04
- [ ] **[LOW] Relancer validation GSC** une fois ADR-016 en prod (≥ 7 jours d'observation propre) — Owner: @automecanik.seo

## Preuves

- Commit palliatif : [`eff30b7f`](https://github.com/ak125/nestjs-remix-monorepo/commit/eff30b7f) (13/04, backend + Caddy)
- Commit buffer error_logs : [`8f0b7b91`](https://github.com/ak125/nestjs-remix-monorepo/commit/8f0b7b91)
- Rapport GSC : capture d'écran 20/04, 30,5k URLs, période 15-18/04
- Vérification live 20/04 : `curl` 10/10 URLs flagged → 200/301 (extrait transcript `/opt/automecanik/app/.spec/reports/gsc-5xx-verify-20260420.log` à créer)
- Stats DB 20/04 :
  ```
  pieces_relation_type : 47 GB total (27 GB heap, 20 GB indexes), 368,304,448 rows
  idx_pieces_relation_type_popular WHERE rtp_type_id IN (17173, 17458, 18071, 18360,
    29994, 19614, 17484, 17971, 8801, 18358)  ← hardcoded top-10 smell
  ```
- RPC cold p99 mesurée : **4064ms** (test skoda-rapid type_id=52395, documenté dans `eff30b7f`)

## Communication

- [x] Équipe (solo-owner) notifiée via session interactive 20/04
- [x] ADR-016 créé comme followup structurel
- [ ] Post-mortem partagé sur canal gouvernance (vault → GitHub, flow DEV→Obsidian Windows)
- [ ] Validation GSC relancée une fois ADR-016 en prod

## Liens

- Related : [[ADR-016-vehicle-page-matview-persistence]]
- Related : [[INC-2026-002-paybox-tunnel-sev1-ipn-blocked]] (pattern similaire : bricolages empilés avant correction structurelle)
- Related rules : [[rules-governance]] G1/G2
- Code affecté :
  - `backend/src/modules/vehicles/services/vehicle-rpc.service.ts`
  - `frontend/app/routes/constructeurs.$brand.$model.$type.tsx:454-594`
  - `frontend/app/utils/pieces-vehicle.loader.server.ts:266-284, 434-449`

---

*Créé le : 2026-04-20*
*Dernière mise à jour : 2026-04-20*
