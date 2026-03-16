# DB Monitoring Runbook

> **Version** : 1.0.0
> **Date** : 2026-03-14
> **Statut** : ACTIVE
> **Baseline T0** : 2026-03-14 (cf. final-exec-summary.md V1.4.2)
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`

---

## Calendrier

| Frequence | Action | Outil |
|-----------|--------|-------|
| Mensuel | Snapshot M1-M6 complet | `POST /api/admin/db-governance/snapshot` ou SQL direct |
| Mensuel | Comparer avec snapshot precedent | `GET /api/admin/db-governance/trend/:id` |
| Trimestriel | ANALYZE tables catalog (A1) | SQL : `ANALYZE public.<table>` |
| Trimestriel | VACUUM tables dead tuples >10% (A2) | SQL : `VACUUM (ANALYZE) public.<table>` |
| Trimestriel | Reevaluer indexes 0-scan `___xtr_msg` (A3) | M6 + grep backend |
| Trimestriel | Revue RPC orphelines SEO (R5) | grep backend + `pg_proc` |
| Trimestriel | Monitor tables design-intent D8/D9 (C2) | M1 filtre `rm_*`, `import_*` |

---

## Seuils d'alerte et actions

### M1 — Croissance tables

| Seuil | Action |
|-------|--------|
| Table non-catalogue >10% croissance/mois | Investiguer la source (imports, logs, RPC) |
| `___xtr_msg` depasse 15 GB | Evaluer purge messages >12 mois |

### M2 — Nouveaux indexes suspects

| Seuil | Action |
|-------|--------|
| Nouvel index >500 MB avec 0 scan | Verifier si cree par migration recente |
| Index doublon detecte (meme table, colonnes similaires) | Ouvrir issue `db-governance`, appliquer R3 |

### M3 — Stats planner stale

| Seuil | Action |
|-------|--------|
| Table >100 MB sans autoanalyze >3 mois | `ANALYZE public.<table>` immediat |
| Table catalog (pieces_*) sans autoanalyze >1 mois | Surveiller, ANALYZE si F4-like regresse |

> Baseline T0 : 5 tables catalog ANALYZE le 2026-03-14 (toutes <1h).

### M4 — Dead tuples

| Seuil | Action |
|-------|--------|
| dead_pct >20% | `VACUUM (ANALYZE) public.<table>` |
| dead_tup >1M sur table >1 GB | Evaluer VACUUM, verifier autovacuum settings |

> Baseline T0 : `__sitemap_p_link` a 19.3% dead tuples — surveiller tendance.

### M5 — Seq scans anormaux

| Seuil | Action |
|-------|--------|
| avg_rows_per_scan > n_live_tup | Full scan systematique — investiguer la RPC source |
| Nouvelle table dans le top 5 seq_tup_read | Verifier si jointure RPC interne |

> Note : compteurs cumulatifs. Comparer le delta entre snapshots, pas la valeur absolue.

### M6 — Indexes 0-scan

| Seuil | Action |
|-------|--------|
| Index >100 MB avec 0 scan depuis >3 mois | Candidat audit : grep backend + RPC/vues/contraintes |
| PK structurelle 0-scan (ex: `___xtr_msg_pkey`) | Signal d'usage seulement, **pas candidate au DROP** |

> Baseline T0 : 5 indexes 0-scan restants (1.1 GB total), dont PK 714 MB.

---

## Points de surveillance specifiques

### `___xtr_msg` (11 GB, 15M rows)

- **Taille** : snapshot trimestriel, alerte si >15 GB
- **Indexes 0-scan** : `idx_msg_parent_id` (168 MB), `idx_msg_ord_id` (168 MB), PK (714 MB)
- **Decision** : conserves car utilises par contact.service.ts et order-actions.service.ts
- **Purge** : evaluer si >12 mois de messages sans activite recente
- **Prochaine reevaluation** : 2026-06-14

### `__sitemap_p_link` (dead tuples)

- **Baseline T0** : 19.3% dead tuples
- **Action** : VACUUM si tendance ne baisse pas au prochain snapshot
- **Cause probable** : regeneration sitemap periodique

### RPC orphelines SEO

- `log_seo_quality_check` : 0 consumers
- `get_seo_quality_daily_stats` : 0 consumers
- **Action** : DROP si toujours 0 consumers apres 2 trimestres (echéance : 2026-09-14)

---

## Outils

| Outil | Endpoint | Usage |
|-------|----------|-------|
| Metrics live | `GET /api/admin/db-governance/metrics` | M1-M6 en temps reel |
| Snapshot | `POST /api/admin/db-governance/snapshot` | Sauvegarder un point de comparaison |
| Trend | `GET /api/admin/db-governance/trend/:id` | Delta entre 2 snapshots |
| Review trimestrielle | `GET /api/admin/db-governance/quarterly-review` | Checklist complete |
| SQL direct | Requetes M1-M6 dans `phase-2-monitoring-rpc.md` | Quand l'endpoint admin n'est pas disponible |

---

## Refs croisees

| Document | Role |
|----------|------|
| `final-exec-summary.md` V1.4.2 | Baseline T0, gains, risques |
| `phase-2-monitoring-rpc.md` V1.0.0 | Requetes SQL M1-M6 completes |
| `sql-governance-rules.md` V1.0.0 | 4 regles anti-regression (R1-R4) |
| `sql-governance-policy.md` V1.0.0 | Politique durable 6 regles |
| `change-control-plan.md` V1.3.0 | Resultats Phase 1 (gele) |
