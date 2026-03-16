# DB Governance — Executive Summary

> **Date** : 2026-03-14
> **Version** : 1.4.2
> **Statut** : COMPLETE
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`
> **Reference** : change-control-plan.md V1.3.0
> **Perimetre** : Ce resume couvre le perimetre effectivement traite et valide pendant la phase 1 de remediation. Il ne constitue pas un audit exhaustif de l'ensemble des 283 objets.

---

## Avant / Apres

| Metrique | Avant | Apres | Delta |
|----------|-------|-------|-------|
| Espace indexes total | 69 GB | 45 GB | **-24 GB (-35%)** |
| Query F4 (jointure critique) | 5,884 ms | 1.6 ms | **x3,600** |
| Indexes 0-scan audites (scope traite) | 25 (~23.5 GB) | 0 restant dans le scope | **-25 indexes** |
| Tables orphelines confirmees (scope traite) | 7 | 0 restant dans le scope | **-7 tables** |
| Vues phantom | 2 | 0 | **-2 vues** |
| Phantom idx_scan (seo_quality_log) | 104M | 0 | **elimines** |
| Dead code (password.service.ts) | 1 methode + 2 appels | 0 | **supprime** |

---

## Objets supprimes

### Tables (7)

| Table | Taille | Raison |
|-------|--------|--------|
| `products` | 24 KB | Vide, 0 refs (remplacee par `pieces`) |
| `categories` | 24 KB | Vide, 0 refs |
| `messages` | 64 KB | Vide, 0 refs (remplacee par `___xtr_msg`) |
| `sessions` | 48 KB | Vide, 1 dead code ref supprime (Redis = seul store) |
| `__blog_advice_old` | 280 KB | Vide, migree vers `__blog_advice` |
| `__rag_knowledge_backup_20260222` | 1.3 MB | Subset obsolete de `__rag_knowledge` (314 vs 367 rows) |
| `__cross_gamme_car_new2` | 30 MB | Subset ancien de `__cross_gamme_car_new` (164K vs 175K rows) |

### Vues (2)

| Vue | Raison |
|-----|--------|
| `v_seo_blocking_issues` | 0 consumers, table source vide (`__seo_quality_log`) |
| `v_seo_quality_stats` | 0 consumers, table source vide |

### Indexes supprimes (27)

> 25 issus du scope 0-scan audite + 2 complementaires (C4 phantom restants).

| Batch | Indexes | Taille | Tables |
|-------|---------|--------|--------|
| V3bis Batch 1 (doublons) | 5 | ~4 GB | pieces_relation_type, pieces_media_img |
| V3bis Batch 2 (supersedes) | 4 | ~4 GB | pieces_relation_criteria, pieces_ref_search |
| V3bis Batch 3 (petits 0-scan) | 10 | ~1 GB | pieces_ref_ean, pieces, pieces_criteria, pieces_media_img, pieces_list |
| V5 (___xtr_msg) | 3 | ~15 GB | ___xtr_msg (msg_content 14GB, msg_orl_equiv_id, msg_orl_id) |
| C4 (phantom) | 5 | ~40 KB | __seo_quality_log |

### Indexes crees (3)

| Index | Taille | Table | Raison |
|-------|--------|-------|--------|
| `idx_sitemap_p_link_map_pg_id` | ~15 MB | `__sitemap_p_link` | Optimisation jointure sitemap (Phase 1) |
| `idx_pieces_criteria_cri100_piece_int` | 27 MB | `pieces_criteria` | Expression index LATERAL hot path (Phase 2A) |
| `idx_pieces_price_piece_id_int_full` | 9.7 MB | `pieces_price` | Expression index cast TEXT→INT (Phase 2A) |

---

## Objets gardes avec justification

| Objet | Taille | idx_scan | Raison de conservation |
|-------|--------|----------|----------------------|
| `___xtr_msg` | 11 GB | — | 7 services actifs : contact (CRITICAL), review (HIGH), legal/RGPD (HIGH) |
| `idx____xtr_msg_msg_parent_id` | 168 MB | **0** | contact.service.ts — reply chains (a reevaluer) |
| `idx____xtr_msg_msg_ord_id` | 168 MB | **0** | order-actions.service.ts — filtre par commande (a reevaluer) |
| `__seo_quality_log` | 56 KB | — | Infrastructure QA SEO, pourrait etre activee |
| `__seo_gamme_car` | 1.2 MB | — | Lookup table hot path, 11 RPCs + 5 services |
| `__seo_keyword_type_mapping` | 11 MB | — | Active via 11 RPCs |

---

## Monitoring actif

| # | Action | Cible | Frequence | Statut |
|---|--------|-------|-----------|--------|
| M1-M6 | Snapshot governance complet | toutes tables/indexes | mensuel | `actif` (baseline T0 : 2026-03-14) |
| A1 | ANALYZE tables catalog stale | pieces_criteria, pieces_media_img, pieces_list, pieces_ref_ean, pieces_price | trimestriel | `fait` (2026-03-14) |
| A2 | VACUUM tables dead tuples >10% | pieces_ref_ean (0%), storage.objects (0%) | trimestriel | `fait` (2026-03-14) |
| A3 | Reevaluer indexes 0-scan ___xtr_msg | idx_msg_parent_id (168 MB), idx_msg_ord_id (168 MB) | trimestriel | `ongoing` |
| C2 | Monitor tables design-intent D8/D9 | rm_*, import_* | trimestriel | `ongoing` |

---

## Risques restants

| # | Risque | Impact | Mitigation |
|---|--------|--------|------------|
| R1 | `___xtr_msg` (11 GB, 15M rows) + 3 indexes 0-scan (1 GB) | Espace disque | Monitoring M6 trimestriel, evaluer purge > 12 mois |
| R3 | Stats planner — re-degradation si autovacuum tombe | Regression query | Monitoring M3 `last_autoanalyze` > 3 mois |
| R4 | Indexes re-crees par migration | Regression espace | Checklist migration (sql-migration-checklist.md) |
| R5 | 2 RPC orphelines (`log_seo_quality_check`, `get_seo_quality_daily_stats`) | Dette technique | Revue trimestrielle, DROP si 0 consumers |

---

## Prochaines actions recommandees

1. **Snapshot M1-M6 mensuel** — comparer avec baseline T0
2. **Reevaluer indexes 0-scan ___xtr_msg** — 3 indexes (1 GB), trimestriel
3. **Revue RPC orphelines SEO** — 2 RPCs, trimestriel

> ANALYZE (A1) et VACUUM (A2) completes le 2026-03-14. Detail dans `phase-2a-rpc-audit-results.md`, `sql-governance-rules.md`.

---

## Baseline T0 (2026-03-14)

Snapshot initial enregistre dans `__db_governance_snapshots` (6 rows, created_at=2026-03-14T14:54:07Z).
ANALYZE + VACUUM executes le 2026-03-14. M3/M4 ci-dessous = valeurs post-intervention.

### M1 — Top tables
| Table | Total | Data | Indexes | Rows |
|-------|-------|------|---------|------|
| pieces_relation_criteria | 33 GB | 11 GB | 22 GB | 157M |
| pieces_ref_search | 16 GB | 4.9 GB | 11 GB | 73M |
| ___xtr_msg | 11 GB | 7.6 GB | 3.3 GB | 15M |
| pieces_relation_type | 9.7 GB | 8.5 GB | 1.1 GB | 146M |
| pieces_criteria | 5.4 GB | 1.2 GB | 4.2 GB | 17.6M |

### M3 — Stats staleness (post-ANALYZE 2026-03-14)
| Table | Last analyze | Age |
|-------|-------------|-----|
| pieces_criteria | 2026-03-14 | **<1h** ✅ |
| pieces_media_img | 2026-03-14 | **<1h** ✅ |
| pieces_list | 2026-03-14 | **<1h** ✅ |
| pieces_ref_ean | 2026-03-14 | **<1h** ✅ |
| pieces_price | 2026-03-14 | **<1h** ✅ |

### M4 — Dead tuples (post-VACUUM 2026-03-14)
| Table | Dead tuples | Ratio |
|-------|-------------|-------|
| pieces_relation_type | 2.1M | 1.5% |
| pieces_ref_search | 802K | 1.1% |
| __sitemap_p_link | 91K | **19.3%** ⚠️ |
| pieces_criteria | 14K | 0.1% |

> pieces_ref_ean et storage.objects resolus (0% dead tuples post-VACUUM).
> `__sitemap_p_link` (19.3% dead tuples) : a surveiller au prochain snapshot M4. VACUUM si la tendance reste elevee.

### M6 — Unused indexes (top 5)
| Index | Taille | idx_scan |
|-------|--------|----------|
| ___xtr_msg_pkey | 714 MB | 0 |
| idx____xtr_msg_msg_parent_id | 168 MB | 0 |
| idx____xtr_msg_msg_ord_id | 168 MB | 0 |
| idx_pieces_list_component | 25 MB | 0 |
| idx_pli_piece_id | 21 MB | 0 |

### Indexes Phase 2A — Verification
| Index | idx_scan | Taille | Statut |
|-------|----------|--------|--------|
| idx_pieces_criteria_cri100_piece_int | 85,439 | 27 MB | ✅ actif |
| idx_pieces_price_piece_id_int_full | 86,369 | 9.7 MB | ✅ actif |

> `___xtr_msg_pkey` (714 MB, 0 scan) : PK structurelle, non candidate au DROP. Surveillee comme signal d'usage uniquement.

27 indexes Phase 1 confirmes absents (spot-check 14 noms = 0 resultats).

---

## Statut de cloture

| Bloc | Statut |
|------|--------|
| Phase 1 remediation | cloturee |
| Nettoyage schema (tables/vues) | cloture |
| Nettoyage indexes | cloture |
| Hot path F4 | stabilise |
| Legacy critique `___xtr_msg` | sous surveillance |
| Phase 2A hot path RPC | cloturee (x21 gain) |
| Phase 2B secondary RPCs | cloturee (6 RPCs <65ms) |
| Phase 3 regles anti-regression | documentees (R1-R4) |
| Phase 4 dashboard admin | deploye |
| Baseline T0 | capturee (2026-03-14) |

---

## Lessons Learned

1. **Toujours ANALYZE avant d'indexer** — 6 mois de stats obsoletes causaient un plan catastrophique (Seq Scan force, x3600 plus lent). Un simple ANALYZE a corrige le probleme sans aucun changement de code ou d'index.

2. **Ne pas deduire trop vite depuis seq_tup_read** — Les compteurs massifs (288B sur pieces_price) provenaient des jointures internes des RPC, pas de queries directes. Les queries SDK utilisaient toutes des Index Scans (<4ms).

3. **Un 0-scan n'autorise jamais seul un DROP** — Chaque index a ete croise avec les contraintes PK/UNIQUE, les RPC, les vues et le code backend avant decision. `idx____xtr_msg_msg_parent_id` (0-scan) a ete conserve car utilise par contact.service.ts.

4. **Les RPCs hot path concentraient l'essentiel des anomalies** — Phase 2A a resolu le bottleneck principal de `rm_get_page_complete_v2` (1423ms→68ms, x21) via LATERAL join + expression indexes. Les 6 RPCs secondaires (Phase 2B) etaient toutes <65ms.
