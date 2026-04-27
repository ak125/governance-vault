# Runbook : Régénération sitemap + resubmit GSC après fix TecDoc orphans

**Domaine :** SEO, Sitemap V10, Google Search Console
**Date :** 2026-04-24 (canon, à jour à la création)
**Première exécution réelle :** 2026-04-23 (cf. section "Run history" en bas — résultats consignés pour référence future)
**Incident lié :** [[2026-04-23-gsc-411k-404-tecdoc-orphans|INC-2026-012]] — 411 k GSC 404 TecDoc orphans
**Évidence :** monorepo PRs #133, #134, #135, #136 + tag `v2026.04.23-gsc-404-tecdoc-fix`

---

## Quand utiliser ce runbook

Après que les **3 PRs code-only de l'incident INC-2026-012** soient mergées ET déployées en DEV ET smoke-testées. Le runbook guide l'action humaine pour :

1. Finaliser l'étape N2 (DELETE DB des 100 k rows orphelines — optionnel mais recommandé)
2. Exécuter l'étape N3 (régénération du sitemap XML + resubmit GSC)

**⚠️ Ce runbook est réservé à l'action humaine.** La règle mémoire `feedback_sitemap_no_trigger.md` interdit qu'un agent déclenche la régénération de sitemap sans validation humaine explicite (incident antérieur 2026-04-18). Ce document est une checklist d'exécution, pas un script auto.

## Prérequis (checklist obligatoire)

### Code

- [ ] monorepo PR #133 (`fix(seo): route legacy /pieces-{supplier}.html via 3-layer error pipeline`) mergée dans `main`
- [ ] monorepo PR #134 (`fix(seo): return 410 Gone for TecDoc orphan type_ids + sitemap legacy patterns`) mergée dans `main`
- [ ] monorepo PR #135 (`fix(seo): filter TecDoc V1 orphan type_ids from sitemap XML generation`) mergée dans `main`

### Déploiement DEV validé

- [ ] Les 3 PRs sont déployées sur DEV preprod (46.224.118.55) — image `massdoc/nestjs-remix-monorepo:preprod`
- [ ] `curl -sI https://dev.automecanik.com/pieces-purflux.html` → **HTTP 410** + `Content-Type: text/html` + `X-Robots-Tag: noindex`
- [ ] `curl -sI https://dev.automecanik.com/pieces/filtre-a-huile-7/audi-22/a3-i-22030/type-19354.html` → **HTTP 410** (type_prefix_fallback)
- [ ] `curl -sI https://dev.automecanik.com/pieces/filtre-a-huile-7/audi-22/a3-i-22030/-12345.html` → **HTTP 410** (missing_alias)
- [ ] Une URL canonique fonctionnelle (e.g. `/pieces/filtre-a-huile-7/peugeot-128/208-128021/1.2-vti-107419.html`) → **HTTP 200** (non-régression)

### DB backup

- [ ] Backup Supabase récent (<24 h) confirmé côté projet `cxpojprgwgubzjyqzmoq`
- [ ] Timestamp du backup noté dans la fiche incident INC-2026-012 (section Suivi)

## Étape N2 — Purge DB des orphelins (optionnel mais recommandé)

La monorepo PR #135 rend les orphelins inertes côté XML (ils ne sortent plus). La purge DB est **cosmétique** : économie ~20 MB + cohérence table.

### Exécution

La migration est versionnée dans : `backend/supabase/migrations/20260424_archive_purge_sitemap_orphan_types.sql`

Elle comporte **3 étapes distinctes** à exécuter dans l'ordre, avec validation manuelle entre chaque :

#### N2.1 — Archive (non-destructive)

```
mcp__supabase__apply_migration   # nom: 20260424_archive_purge_sitemap_orphan_types
```

Exécute `CREATE TABLE __sitemap_p_link_archive_20260423 AS SELECT orphans` + indexe. Idempotent, re-lançable sans risque.

**Résultat attendu :** ~99 912 rows dans la table d'archive.

#### N2.2 — Validation manuelle

Exécuter les 4 checks A, B, C, D listés dans le header du fichier SQL. Via :

```sql
-- Check A : count archive
SELECT COUNT(*) FROM public.__sitemap_p_link_archive_20260423;
-- Attendu : ~99,912 (±5%)

-- Check B : count total avant delete
SELECT COUNT(*) FROM public.__sitemap_p_link;
-- Attendu : ~472,917

-- Check C : aucun orphelin hors archive
-- (cf. SQL complet dans le fichier migration)
-- Attendu : 0

-- Check D : PR #135 active sur DEV
-- Trigger génération sitemap DEV + lire logs backend
-- Chercher : "🧹 Filtered out N URLs with orphan type_ids"
```

**Ne PAS procéder à N2.3 si un check échoue.** Investiguer avant.

#### N2.3 — DELETE (destructif)

Le bloc `DELETE` est commenté dans le fichier SQL pour forcer une édition manuelle explicite. Procédure :

1. Copier le bloc `DELETE FROM public.__sitemap_p_link ...` depuis le fichier (lignes ~78-88)
2. L'exécuter via `mcp__supabase__execute_sql` ou psql supervisé, encapsulé dans `BEGIN ... COMMIT`
3. Vérifier le count post-delete avant `COMMIT` :
   ```
   (472 917) − (~99 912) ≈ 373 005 rows restantes
   ```
4. Si divergence >5 %, `ROLLBACK` et investiguer.

### Rollback N2

Si N2.3 pose problème après COMMIT :

```sql
BEGIN;
INSERT INTO public.__sitemap_p_link
SELECT * FROM public.__sitemap_p_link_archive_20260423;
-- Vérifier COUNT rétabli à ~472,917
COMMIT;
```

L'archive reste disponible pendant ≥ 30 jours avant drop (cf. section CLEANUP du fichier SQL).

## Étape N3 — Régénération sitemap + resubmit GSC

### N3.1 — Trigger génération sitemap

**Pré-check :** PR #135 bien mergée sur main ET déployée en PROD (tag push requis, pas seulement DEV).

```bash
# PROD (49.12.233.2) uniquement — DEV est déjà couvert par le smoke test
curl -X POST https://www.automecanik.com/api/sitemap/v10/generate-all \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json"
```

Remplacer `${ADMIN_TOKEN}` par un token admin valide. Le job est async, réponse `{ jobId: "..." }` immédiate.

### N3.2 — Monitoring de la génération

```bash
# Status job
curl "https://www.automecanik.com/api/sitemap/v10/status/${JOB_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"

# Logs backend PROD
ssh 49.12.233.2 "docker compose logs -f backend | grep -E '(Filtered out|URLs pieces INDEX|Written sitemap)'"
```

**Critères de succès :**

- [ ] Le log `🧹 Filtered out N URLs with orphan type_ids` apparaît avec **N ≈ 99 912** (si N2 n'a pas été exécuté) OU **N = 0** (si N2 exécuté)
- [ ] Le count total `URLs pieces INDEX` est **≈ 614 k** (714 k − 100 k), cohérent avec le filtre
- [ ] Les fichiers `sitemap-pieces-*.xml` sont régénérés dans `/opt/automecanik/sitemaps/` avec timestamp récent
- [ ] Pas d'erreur backend dans les logs

### N3.3 — Vérification sitemaps publiés

```bash
# Index
curl -sI https://www.automecanik.com/sitemap.xml
# Attendu : 200 OK + Last-Modified récent

# Un shard
curl -s https://www.automecanik.com/sitemaps/stable/sitemap-pieces-1.xml | head -30
# Vérifier : pas d'URL avec type_id > 83456 dans les <loc>
```

Spot-check : 5 URLs prises dans un shard doivent toutes retourner 200 OK :

```bash
curl -s https://www.automecanik.com/sitemaps/stable/sitemap-pieces-1.xml \
  | grep -oP '<loc>\K[^<]+' | shuf -n 5 | xargs -I{} curl -sI -o /dev/null -w '%{http_code} {}\n' {}
# Attendu : toutes en 200
```

### N3.4 — Resubmit GSC

**Action humaine uniquement via interface Google Search Console** :

1. https://search.google.com/search-console
2. Propriété `automecanik.com`
3. Menu `Sitemaps` → supprimer l'ancien sitemap (s'il est en état `Erreur` ou `Avertissement`)
4. `Ajouter un sitemap` → `https://www.automecanik.com/sitemap.xml`
5. Vérifier statut `Réussi` sous 24 h

**Monitoring J+1, J+7, J+30, J+60, J+90** (cf. checklist de suivi dans [[2026-04-23-gsc-411k-404-tecdoc-orphans|INC-2026-012]]) :

- Rapport `Indexation des pages > Introuvable (404)` : tendance à la baisse
- Objectif : **≤ 50 k URLs en 404 à J+60** (réduction ≥ 87 % depuis les 411 k observés 2026-04-23)

## Rollback N3

Si la régénération sitemap produit un résultat inattendu (URLs manquantes légitimes, erreur massive) :

1. Récupérer la version précédente des sitemaps depuis backup disque `/opt/automecanik/sitemaps-backup/` (rotation quotidienne)
2. Remettre en place via `cp -r`
3. Vérifier `curl -sI https://www.automecanik.com/sitemap.xml` (200 OK)
4. Ouvrir un incident follow-up référencé à INC-2026-012
5. Décider de revert monorepo PR #135 si le bug vient du filtre (peu probable vu le helper testé, mais option disponible)

## Critères de clôture de l'incident INC-2026-012

L'incident passe de `resolved-with-followup` à `closed` quand :

- [ ] N1 (3 PRs code) mergées + déployées PROD — ✅ livrable Claude
- [ ] N2 (DELETE) exécuté + validé (ou décidé explicitement de skipper)
- [ ] N3 (régénération sitemap + resubmit GSC) exécuté
- [ ] J+60 : GSC `Introuvable (404)` en baisse de ≥ 80 %
- [ ] J+90 : backlog stabilisé à une valeur résiduelle acceptable (< 20 k)
- [ ] Post-mortem complété : [[2026-04-23-gsc-411k-404-tecdoc-orphans|INC-2026-012]] section Suivi toutes cases cochées

## Run history

### Run #1 — 2026-04-23 (première exécution, INC-2026-012 N3)

**Trigger** : `POST https://www.automecanik.com/api/sitemap/v10/generate-all` lancé par owner SEO depuis VPS PROD `49.12.233.2` à 19:42 UTC.

**Réponse API** (HTTP 201, durée 18 748 ms) :

```json
{
  "success": true,
  "totalUrls": 102395,
  "totalFiles": 11,
  "indexPath": "/var/www/sitemaps/sitemap.xml",
  "buckets": [
    {"bucket": "hot",    "urlCount": 0,      "filesGenerated": 0},
    {"bucket": "stable", "urlCount": 102395, "filesGenerated": 3},
    {"bucket": "cold",   "urlCount": 0,      "filesGenerated": 0}
  ],
  "hubResult": {"totalUrls": 250539, "totalFiles": 113}
}
```

**Vérifications post-trigger** :

| Check | Résultat |
|-------|----------|
| `sitemap-pieces-1.xml` taille | 50 000 URLs ✅ |
| `sitemap-pieces-2.xml` taille | 50 000 URLs ✅ |
| `sitemap-pieces-3.xml` taille | 2 395 URLs ✅ (somme = 102 395, match API) |
| Orphan check `type_id > 83456` dans XML | 0 trouvé ✅ (filtre PR #135 actif) |
| Spot-check 5 URLs random | 4×200 + 1×301 (URL normalisée vers slug canonique = comportement attendu) ✅ |
| `sitemap.xml` index public | HTTP 200, lastmod 2026-04-23 ✅ |

**Note** : `sitemap-pieces-4.xml` (50 000 URLs) reste sur le filesystem mais n'est pas référencé dans `sitemap.xml` (donc pas indexé par GSC). Leftover d'un ancien run avant le filtre orphans. Cleanup à programmer en opération séparée non-bloquante.

**Calibrage attendu pour les prochains runs** :
- Bucket stable ≈ 100 k URLs (avec threshold `min_items_threshold = 20`, cf. `crawl_budget_experiments`)
- Hubs ≈ 250 k URLs (113 files)
- Durée totale ≈ 20 s
- Filtre orphans : devrait être proche de 0 si la DB reste stable, sinon investiguer (nouveau remap TecDoc ?)

### Run #2+ — à compléter

À chaque exécution future de ce runbook, ajouter une section similaire avec : trigger source, réponse API, vérifications, anomalies éventuelles.

## Références

- Incident : [[2026-04-23-gsc-411k-404-tecdoc-orphans|INC-2026-012]] (`ledger/incidents/2026/2026-04-23-gsc-411k-404-tecdoc-orphans.md`)
- Pattern canon : [[3-layer-error-pipeline-pattern]] (`ledger/knowledge/`)
- Migration SQL : monorepo `backend/supabase/migrations/20260424_archive_purge_sitemap_orphan_types.sql`
- Règle mémoire bloquante : `feedback_sitemap_no_trigger.md` (incident 2026-04-18)
- Auto-mode règle 5 : toute opération destructive ou sur système partagé nécessite confirmation humaine explicite
- PRs monorepo : [#133](https://github.com/ak125/nestjs-remix-monorepo/pull/133), [#134](https://github.com/ak125/nestjs-remix-monorepo/pull/134), [#135](https://github.com/ak125/nestjs-remix-monorepo/pull/135), [#136](https://github.com/ak125/nestjs-remix-monorepo/pull/136)
- Tag PROD : `v2026.04.23-gsc-404-tecdoc-fix` (commit `5dd0be92`)
