# phase-2-monitoring-rpc.md

> **Version** : 1.0.0
> **Date** : 2026-03-14
> **Phase** : MONITORING + RPC AUDIT
> **Pre-requis** : Phase 1 close (change-control-plan.md V1.3.0)
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`

---

## 1. Monitoring post-remediation

6 requetes SQL a executer periodiquement (hebdomadaire recommande les 2 premieres semaines, puis mensuel).

### M1 — Top tables par taille

```sql
SELECT
  schemaname,
  relname AS table_name,
  pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
  pg_size_pretty(pg_relation_size(relid)) AS data_size,
  pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size,
  n_live_tup
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;
```

**Baseline post-Phase 1** : `___xtr_msg` ~25 GB, `pieces_relation_criteria` ~36 GB.
**Alerte** : croissance > 10% en 1 mois sur une table non-catalogue.

### M2 — Top indexes par taille

```sql
SELECT
  schemaname,
  relname AS table_name,
  indexrelname AS index_name,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
  idx_scan
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;
```

**Baseline** : total indexes ~45 GB post-Phase 1.
**Alerte** : nouvel index > 500 MB avec 0 scans.

### M3 — Tables avec stats stale (autoanalyze > 3 mois)

```sql
SELECT
  schemaname,
  relname,
  last_autoanalyze,
  last_autovacuum,
  n_live_tup,
  pg_size_pretty(pg_relation_size(relid)) AS size
FROM pg_stat_user_tables
WHERE last_autoanalyze < now() - interval '3 months'
   OR last_autoanalyze IS NULL
ORDER BY pg_relation_size(relid) DESC
LIMIT 20;
```

**Alerte** : toute table > 100 MB sans autoanalyze depuis 3 mois.
**Action** : `ANALYZE public.<table>` immediat.

### M4 — Tables avec dead tuples eleves

```sql
SELECT
  schemaname,
  relname,
  n_dead_tup,
  n_live_tup,
  CASE WHEN n_live_tup > 0
    THEN round(100.0 * n_dead_tup / n_live_tup, 1)
    ELSE 0
  END AS dead_pct,
  last_autovacuum,
  pg_size_pretty(pg_relation_size(relid)) AS size
FROM pg_stat_user_tables
WHERE n_dead_tup > 100000
ORDER BY n_dead_tup DESC
LIMIT 20;
```

**Alerte** : dead_pct > 20% ou dead_tup > 1M.
**Action** : evaluer `VACUUM (ANALYZE)`.

### M5 — Top objets seq_tup_read anormal

```sql
SELECT
  schemaname,
  relname,
  seq_scan,
  seq_tup_read,
  idx_scan,
  CASE WHEN seq_scan > 0
    THEN round(seq_tup_read::numeric / seq_scan, 0)
    ELSE 0
  END AS avg_rows_per_scan,
  n_live_tup
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_tup_read DESC
LIMIT 20;
```

**Alerte** : avg_rows_per_scan > n_live_tup (= full table scan a chaque appel).
**Note** : les compteurs sont cumulatifs. Comparer avec la baseline Phase 1 pour detecter une croissance.

### M6 — Indexes avec idx_scan = 0

```sql
SELECT
  schemaname,
  relname AS table_name,
  indexrelname AS index_name,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
  idx_scan,
  idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND pg_relation_size(indexrelid) > 1048576  -- > 1 MB
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;
```

**Alerte** : nouvel index 0-scan > 100 MB.
**Action** : verifier si cree par migration recente. Si > 3 mois sans scan → candidat audit.

---

## 2. Audit RPC hot path — Phase 2A

### Contexte

Phase 1 V2 a demontre que les seq_scans massifs (288B pieces_price, 287B auto_type_number_code, 267B pieces_media_img) proviennent des **jointures internes des RPC functions**, pas des queries directes SDK.

Les queries directes sont toutes indexees (< 4ms). Le prochain levier de performance est l'optimisation interne des RPC.

### Cibles prioritaires

| RPC | Hot path | Tables jointes | Impact estime |
|-----|----------|---------------|---------------|
| `rm_get_page_complete_v2` | U1 listing, U3 vehicle | pieces_price, pieces_media_img, auto_type_number_code, pieces_gamme, pieces_criteria | ELEVE — RPC la plus complexe, probablement >10 jointures internes |
| `get_pieces_for_type_gamme_v1/v2/v3/v4` | U1 listing | pieces_price, pieces_relation_type, pieces_relation_criteria | ELEVE — variantes du listing |
| `get_listing_products_*` | U1 listing | pieces_price | MOYEN |
| `get_gamme_price_preview` | U1 listing | pieces_price | MOYEN |
| `get_vehicle_page_data_optimized` | U3 vehicle | auto_type_number_code | MOYEN |

### Methode d'audit

**Etape 1** — Lire le code source SQL de chaque RPC :
```sql
SELECT proname, prosrc
FROM pg_proc
WHERE proname = 'rm_get_page_complete_v2';
```

**Etape 2** — Decomposer en sous-requetes et profiler individuellement :
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
<sous-requete extraite>;
```

**Etape 3** — Identifier les jointures internes couteuses :
- Jointures sans index sur la colonne de jointure
- Jointures avec estimation de cardinalite incorrecte
- Sous-requetes materialisees inutilement

### Format de sortie par RPC

| Champ | Valeur |
|-------|--------|
| RPC | nom |
| Nombre de sous-requetes | — |
| Sous-requete la plus couteuse | `SELECT ...` |
| Plan observe | — |
| Tables jointes | — |
| Index manquant(s) | — |
| Optimisation proposee | simplifier / ajouter index / pre-calculer / decouper |
| Risque | R0-R3 |
| Gain attendu | — |

### Gate Phase 2A

- Ne pas modifier une RPC sans avoir profile toutes ses sous-requetes
- Ne pas ajouter d'index sans avoir confirme l'impact sur la sous-requete
- Toute modification de RPC doit etre testee avec la requete baseline avant deploy

---

## 3. Calendrier recommande

| Semaine | Action |
|---------|--------|
| S1 (post-Phase 1) | Executer M1-M6, verifier baseline |
| S2 | Re-executer M1-M6, comparer avec S1 |
| S3-S4 | Phase 2A : audit RPC (rm_get_page_complete_v2 en premier) |
| Mensuel | M1-M6 en routine |
| Trimestriel | Revue complete : indexes 0-scan, vues/RPC orphelines, tables design-intent |

---

## Refs croisees

| Document | Version | Role |
|----------|---------|------|
| change-control-plan.md | V1.3.0 (gele) | Resultats Phase 1 |
| final-exec-summary.md | V1.1.0 | Bilan + risques + prochaine phase |
| sql-governance-policy.md | V1.0.0 | Politique durable |
| execution-map.md | V1.2.0 | 5 flux critiques U1-U5 |
