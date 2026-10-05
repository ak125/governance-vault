---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: SEO Monitor — RPC manquante silencieusement masquée par OBSERVE + catch-and-return-empty
slug: seo-monitor-random-sample-silent-fail
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-01"
updated_by: "@fafa"
related_adr:
  - "ADR-017"
related_prs: []
status: proposed
---

# SEO Monitor — RPC `get_random_vehicle_gamme_combinations` jamais créée, cron silencieux pendant des mois

> Découvert 2026-05-01 sur logs DEV. Cron BullMQ `check-random-sample` toutes les 6h
> appelait une RPC inexistante en DB. Personne ne l'avait vu : combinaison de 3 couches
> de "soft fail" qui ont rendu l'incident invisible jusqu'à inspection manuelle des logs.

## 1. Symptôme

Logs DEV récurrents toutes les 6h (`0 */6 * * *`) :

```
[ERROR] RPC ERROR: get_random_vehicle_gamme_combinations
  context: "RpcGateService"
  decision: "OBSERVE"
  reason: "UNKNOWN_FUNCTION"
  source: "cron"
  error: "Could not find the function public.get_random_vehicle_gamme_combinations(sample_size) in the schema cache"
[WARN]  ⚠️ Impossible de récupérer échantillon aléatoire
  context: "SeoMonitorProcessor"
[INFO]  ✅ [Job #...] Monitoring terminé en 121ms - 0 OK, 0 warnings, 0 erreurs
```

La ligne `INFO` finale ressemble à un succès trivial. Aucune alerte, aucun crash, aucun
incident ouvert depuis le shipping initial du processor (commit `2ad0ace7` —
`feat(gamme): rpc v2 endpoints + seo monitor + video processor updates`).

## 2. Cause profonde

### 2.1 La RPC n'a jamais été créée

`grep -rn "get_random_vehicle_gamme_combinations" backend/supabase/migrations/` → 0
résultat. Le processor a été mergé sans sa migration SQL accompagnatrice. Le DDL côté
DB n'a jamais existé.

### 2.2 Trois couches de "soft fail" empilées qui masquent l'incident

| Couche | Comportement | Effet |
|---|---|---|
| RpcGate (P0 OBSERVE) | log WARN, ne lève pas | Erreur loggée mais job continue |
| `getRandomUrlSample()` catch | `return []` sur error | Le caller reçoit 0 URL au lieu d'une exception |
| `handleMonitoring()` analyse | 0 résultat → `0 OK / 0 warning / 0 error` | Reporte un succès "vide" comme un succès |

→ Le job se termine `processedOn` correct, `failedReason` null, `returnvalue` valide
(juste vide). Bull queue stats : `completed++`. Aucun signal d'erreur remonte au
`AdminJobHealthService` (`recordSuccess('seo-monitor', duration)` est appelé même quand
0 URL n'a été checkée).

### 2.3 Pourquoi personne n'a tiré la sonnette

- Path parallèle `check-critical-urls` (toutes les 30min, 8 URLs hardcodées) marche
  bien et produit du signal réel — le monitoring "global" semblait sain.
- Les logs WARN/ERROR du `SeoMonitorProcessor` se noient dans le volume DEV.
- Aucune métrique "couverture sample aléatoire" n'est exposée — seul le compteur "jobs
  completed" est visible côté admin, et il s'incrémente normalement.

## 3. Pattern réutilisable — checklist de détection

Quand tu inspectes un cron BullMQ qui semble "tourner sans bruit", vérifier :

```
[ ] Le job catch les erreurs de ses dépendances DB/RPC ? Si oui, que retourne-t-il ?
    → Si fallback "vide" (return []), suspecter un trou silencieux.
[ ] Le summary final différencie-t-il "0 résultat parce que rien à faire"
    de "0 résultat parce que la dépendance est cassée" ?
    → Sinon, le job ne peut pas signaler son propre échec.
[ ] Le job appelle-t-il `jobHealth.recordSuccess()` inconditionnellement ?
    → Si oui, l'admin job-health dashboard ne révèle rien.
[ ] Existe-t-il une métrique métier ("URLs checkées dans les 7 derniers jours")
    pour révéler un floor à zéro ?
    → Sinon, ajouter une assertion côté planner ou retirer le path.
```

## 4. Options évaluées et recommandation

Deux options évaluées sur 2026-05-01 :

| Option | Coût | Bénéfice | Risque |
|---|---|---|---|
| **A. Créer la RPC manquante** | Migration SQL avec JOIN sur `pieces_relation_type` (368M rows) + `auto_type/modele/marque/pieces_gamme` + `ORDER BY random()` ou `TABLESAMPLE` | Reprise de la couverture aléatoire des combos | Perf coûteuse sur grosse table, **dette DB en plein cleanup ADR-017** (8 RPC à supprimer en cours), valeur d'alerte non démontrée empiriquement (jamais vue depuis le shipping) |
| **B. Retirer le path mort** | Suppression `getRandomUrlSample`, `setupRandomSampleMonitoring`, `buildUrl`, branche `else if` dans `handleMonitoring`, types narrowed à `'check-critical-urls'` uniquement | Code mort retiré, plus de bruit log, plus de RPC fantôme, scope `RpcGateService` réduit | Perte théorique de la couverture aléatoire — mitigée par le path `check-critical-urls` (8 URLs critiques toutes les 30min, qui fonctionne) |

→ **Recommandation : Option B** (cohérente avec ADR-017 RPC cleanup et le principe
"delete dead code, don't resurrect" dans CLAUDE.md monorepo).

**Statut application** : recommandation consignée, application monorepo en attente
de décision (PR non ouverte au 2026-05-01). Repasser ce document à `status: current`
+ ajouter le PR monorepo dans `related_prs` une fois l'option appliquée.

**Cleanup Redis quand l'option sera appliquée** : pas d'action manuelle. La méthode
`cleanOldRepeatableJobs()` du scheduler purge **tous** les repeatable jobs de la queue
`seo-monitor` au démarrage, puis ne rajoute que `critical-urls-monitoring`. La clé
orpheline `random-sample-monitoring` disparaîtra au prochain déploiement DEV
post-merge.

## 5. Lien anti-pattern AP-12 (ADR-034)

Cet incident illustre une variante du pattern visé par AP-12 (anti-bricolage
orchestrateur maison) : un fragment d'observabilité shippé sans son composant DB,
maintenu en vie par un fail-soft. Solution structurelle = compléter ou retirer, pas
laisser tourner en `OBSERVE` indéfiniment.

## 6. Références

- Logs source : DEV VPS, 2026-05-01 ~00:00 UTC
- Caller unique : `backend/src/workers/processors/seo-monitor.processor.ts` (avant
  cleanup, ligne 297)
- Scheduler : `backend/src/workers/services/seo-monitor-scheduler.service.ts`
- Commit d'origine : `2ad0ace7` (sans migration SQL accompagnatrice)
- ADR-017 — RPC cleanup en cours (8 RPC restantes à supprimer)
- CLAUDE.md monorepo § "Vérifier l'existant AVANT d'inventer" — règle qui aurait
  bloqué l'ajout d'une nouvelle RPC sans grep préalable
