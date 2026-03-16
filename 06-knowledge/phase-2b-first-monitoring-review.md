# Phase 2B — First Monitoring Review

> **Version** : 1.1.0
> **Date T1** : 2026-03-14 15:50 UTC
> **Baseline T0** : 2026-03-14 14:54 UTC
> **Delta T0→T1** : ~1 heure (meme journee — ce cycle valide l'outillage, pas encore une derive temporelle)
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`
> **Snapshot DB** : `__db_governance_snapshots` (12 rows : 6 T0 + 6 T1)

---

## Tableau comparatif par metrique

### M1 — Top tables (taille)

| Table | T0 | T1 | Delta | Statut |
|-------|----|----|-------|--------|
| pieces_relation_criteria | 33 GB | 33 GB | 0 | stable |
| pieces_ref_search | 16 GB | 16 GB | 0 | stable |
| ___xtr_msg | 11 GB | 11 GB | 0 | stable |
| pieces_relation_type | 9.7 GB | 9.7 GB | 0 | stable |
| pieces_criteria | 5.4 GB | 5.4 GB | 0 | stable |

**Verdict** : aucune croissance detectee. `___xtr_msg` stable a 11 GB.

### M2 — Top indexes (taille)

| Index | T0 | T1 | idx_scan T1 | Statut |
|-------|----|----|-------------|--------|
| pk_pieces_relation_criteria | 14 GB | 14 GB | 32.8M | stable |
| pieces_ref_search_pkey | 4978 MB | 4978 MB | 42.5M | stable |
| idx_prs_prb_id_covering | 2278 MB | 2278 MB | 432K | stable |
| ___xtr_msg_pkey | 714 MB | 714 MB | **0** | PK structurelle |

**Verdict** : pas de nouvel index >500 MB. Espace indexes stable.

### M3a — Fraicheur effective des stats planner

> Mesure via `GREATEST(last_analyze, last_autoanalyze)` — ce qui compte pour le planner, c'est la date du dernier ANALYZE quel qu'il soit.

| Table | last_analyze (manuel) | last_autoanalyze (daemon) | Stats effectives | Statut |
|-------|----------------------|--------------------------|-----------------|--------|
| pieces_criteria | 2026-03-14 | 2025-06-19 | **<1h** | OK |
| pieces_media_img | 2026-03-14 | 2025-06-19 | **<1h** | OK |
| pieces_list | 2026-03-14 | 2025-06-19 | **<1h** | OK |
| pieces_ref_ean | 2026-03-14 | 2025-06-24 | **<1h** | OK |
| pieces_price | 2026-03-14 | 2025-07-02 | **<1h** | OK |
| pieces | 2026-03-14 | 2025-07-05 | **<1h** | OK |
| pieces_relation_type | 2026-03-14 | 2025-09-18 | **<1h** | OK |
| pieces_relation_criteria | 2026-03-14 | 2025-09-18 | **<1h** | OK |
| pieces_ref_search | 2025-11-12 | 2025-09-06 | **4 mois** | **ATTENTION** |

**Verdict M3a** : stats fraiches sur 8/9 tables grace aux ANALYZE manuels Phase 1. `pieces_ref_search` (4.9 GB) n'a pas ete ANALYZE depuis 4 mois — candidat au prochain ANALYZE.

### M3b — Sante du daemon autoanalyze

| Constat | Detail |
|---------|--------|
| Dernier autoanalyze | 2025-09-18 (`pieces_relation_criteria`) |
| Tables >100 MB sans autoanalyze >3 mois | **9/9** |
| Autoanalyze effectif sur grosses tables catalog | **NON** — non observe depuis 6 mois |

**Verdict M3b** : **ALERTE** — le daemon autovacuum/autoanalyze ne traite plus les grosses tables catalog. Les ANALYZE manuels compensent ponctuellement, mais sans automatisation la derive est garantie a terme.

**Action recommandee** :
1. Verifier la configuration autovacuum sur Supabase (parametres `autovacuum_analyze_threshold`, `autovacuum_analyze_scale_factor`)
2. Considerer un ANALYZE periodique via cron ou endpoint admin en attendant
3. ANALYZE immediat sur `pieces_ref_search` (4 mois de retard)

### M4 — Dead tuples

| Table | T0 dead_tup | T1 dead_tup | T0 dead_pct | T1 dead_pct | Statut |
|-------|-------------|-------------|-------------|-------------|--------|
| pieces_relation_type | 2.1M | 2.1M | 1.5% | 1.5% | stable |
| pieces_ref_search | 802K | 802K | 1.1% | 1.1% | stable |
| __sitemap_p_link | 91K | 91K | 19.3% | **16.2%** | ameliore (-3.1 pts) |

**Verdict** : `__sitemap_p_link` passe de 19.3% a 16.2% dead tuples (-3.1 pts). Amelioration confirmee, mais reste au-dessus du seuil de confort (10%). A surveiller.

### M5 — Seq scans (compteurs cumulatifs)

| Table | seq_tup_read | avg_per_scan | n_live_tup | Full scan ? | Statut |
|-------|-------------|--------------|------------|-------------|--------|
| pieces_relation_type | 463B | 23.7M | 146M | non (16%) | RPC interne |
| pieces_price | 289B | 440K | 442K | **oui (~100%)** | RPC interne |
| auto_type_number_code | 287B | 165K | 165K | **oui (~100%)** | RPC interne |
| pieces_media_img | 267B | 4.3M | 4.6M | quasi (93%) | RPC interne |

> Compteurs cumulatifs — pas de delta significatif sur 1h. A comparer au prochain snapshot mensuel.

**Verdict** : memes patterns qu'en Phase 1. Les full scans proviennent des RPC internes (deja documente dans Lessons Learned). Pas de nouveau signal.

### M6 — Indexes 0-scan

| Index | Taille | T0 idx_scan | T1 idx_scan | Statut |
|-------|--------|-------------|-------------|--------|
| ___xtr_msg_pkey | 714 MB | 0 | 0 | PK structurelle, non candidate |
| idx____xtr_msg_msg_parent_id | 168 MB | 0 | 0 | sous surveillance (contact.service) |
| idx____xtr_msg_msg_ord_id | 168 MB | 0 | 0 | sous surveillance (order-actions) |
| idx_pieces_list_component | 25 MB | 0 | 0 | petit, stable |
| idx_pli_piece_id | 21 MB | 0 | 0 | petit, stable |
| idx_pieces_price_pri_ean | 19 MB | 0 | 0 | petit, stable |

> 20 indexes 0-scan au total (vs 5 dans le top T0). Les 14 supplementaires sont tous <20 MB (pieces_price, pieces_list, cross_gamme, blog, seo). Pas de nouveau gros index 0-scan.

**Verdict** : stable. Les 3 indexes `___xtr_msg` (1050 MB total) restent sous surveillance. Aucun nouveau candidat critique.

---

## Checklist risques R1-R5

| # | Risque | T0 | T1 | Statut |
|---|--------|----|----|--------|
| R1 | `___xtr_msg` croissance | 11 GB | 11 GB | **stable** |
| R3 | Stats planner stale | ANALYZE fait | daemon OK, tables statiques — comportement normal | **resolu** |
| R4 | Indexes doublons post-migration | 0 | 0 | **stable** |
| R5 | RPC orphelines SEO | 0 consumers | 0 consumers confirme — candidats DROP T3 | **confirme** |

---

## Alertes declenchees

| # | Metrique | Niveau | Detail | Action |
|---|----------|--------|--------|--------|
| A1 | M3b | ~~WARNING~~ → **resolu** | Daemon OK, tables statiques (seuil non atteint) | Aucune action — ANALYZE manuels periodiques suffisent |
| — | M1 | — | Pas d'alerte | — |
| — | M2 | — | Pas d'alerte | — |
| — | M4 | — | Pas d'alerte (amelioration sitemap_p_link) | — |
| — | M5 | — | Pas de nouveau signal (cumulatif) | — |
| — | M6 | — | Pas de nouveau gros index 0-scan | — |

---

## Verdict global

**STABLE — aucune alerte active. Deux candidats DROP differes a T3.**

- Tailles stables, pas de derive (M1/M2)
- Stats planner fraiches grace aux ANALYZE manuels (M3a OK, 9/9 tables apres ANALYZE `pieces_ref_search`)
- Dead tuples en amelioration (M4 : `__sitemap_p_link` 19.3% → 16.2%)
- Indexes 0-scan stables, pas de nouveaux gros (M6)
- Seq scans : memes patterns RPC internes (M5, attendu)
- **M3b resolu** : daemon autovacuum actif, absence d'autoanalyze = comportement normal (tables statiques, seuil non atteint)
- **R5 confirme** : 2 RPC orphelines SEO → candidats DROP a T3 (2026-06-14)

---

## Actions post-review (2026-03-14)

### M3b — Investigation autovacuum

| Parametre | Valeur |
|-----------|--------|
| `autovacuum` | **on** |
| `autovacuum_analyze_scale_factor` (global) | 0.1 (10%) |
| `autovacuum_analyze_threshold` (global) | 50 |
| `autovacuum_naptime` | 60s |
| `autovacuum_max_workers` | 3 |

**Overrides par table** (4 tables avec config agressive) :

| Table | analyze_scale_factor | vacuum_scale_factor |
|-------|---------------------|---------------------|
| pieces_relation_criteria | 0.01 (1%) | 0.02 |
| pieces_relation_type | 0.01 (1%) | 0.02 |
| pieces_ref_search | 0.01 (1%) | 0.02 |
| pieces | 0.02 (2%) | 0.05 |

**Diagnostic** : le daemon est actif et correctement configure. L'absence d'autoanalyze s'explique par la nature statique des tables catalog : aucun DML significatif depuis septembre 2025. Le seuil de declenchement (ex: `pieces_relation_criteria` = 50 + 1% * 157M = **1.58M modifications necessaires**) n'est jamais atteint car ces tables ne recoivent pas d'INSERT/UPDATE/DELETE.

**Conclusion M3b** : **pas un bug, comportement attendu**. Le daemon fonctionne mais les tables n'ont pas assez de modifications pour declencher un autoanalyze. Les ANALYZE manuels periodiques (Phase 1 + runbook) compensent adequatement. Alerte M3b → **resolue** (comportement normal, pas d'action corrective necessaire).

### R5 — RPC orphelines SEO

| RPC | Consumers backend | Consumers frontend | Statut |
|-----|-------------------|-------------------|--------|
| `log_seo_quality_check` | 0 (reference uniquement dans `rpc_allowlist.json`) | 0 | **confirme orpheline** |
| `get_seo_quality_daily_stats` | 0 (reference uniquement dans `rpc_allowlist.json`) | 0 | **confirme orpheline** |

**Decision R5** : 2 RPCs confirmees orphelines. Candidats DROP au prochain checkpoint trimestriel T3 (2026-06-14). Pas de DROP immediat — laisser une fenetre de 3 mois au cas ou un consumer serait ajoute.

### ANALYZE pieces_ref_search

```sql
ANALYZE public.pieces_ref_search;  -- execute 2026-03-14
```

Seule table avec `last_analyze` > 3 mois (4 mois, 2025-11-12). Stats planner rafraichies.

### Bilan post-review

| Point | Avant | Apres | Statut |
|-------|-------|-------|--------|
| M3b (daemon) | ALERTE | comportement normal documente | **resolu** |
| R5 (RPC orphelines) | open | 2 RPCs confirmees orphelines | **confirme** (DROP T3) |
| pieces_ref_search stats | 4 mois | <1h | **resolu** |

---

## Prochaine review

| Checkpoint | Date | Scope |
|------------|------|-------|
| T2 | 2026-04-14 | Snapshot M1-M6 mensuel, comparer avec T1 |
| T3 (trimestriel) | 2026-06-14 | Review complete : ANALYZE/VACUUM + reevaluation indexes ___xtr_msg + RPC orphelines |

---

## Refs croisees

| Document | Role |
|----------|------|
| final-exec-summary.md V1.4.2 | Baseline T0 |
| db-monitoring-runbook.md V1.0.0 | Seuils et procedures |
| sql-governance-rules.md V1.0.0 | Regles anti-regression |
