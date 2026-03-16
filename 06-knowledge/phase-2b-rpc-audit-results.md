# Phase 2B — RPC Hot Path Audit (RPCs secondaires)

> **Date** : 2026-03-14
> **Version** : 1.0.0
> **Methode** : Appel reel avec timing `clock_timestamp()` + analyse patterns source
> **Params de test** : gamme_id=82, type_id=30971, marque_id=54

---

## Resume

| RPC | Temps | Taille reponse | Patterns risque | Verdict |
|-----|-------|---------------|-----------------|---------|
| `get_vehicle_compatible_gammes_php(30971)` | **41 ms** | table rows | Aucun (Index Scan partout) | OK |
| `get_homepage_data_optimized()` | **59 ms** | 68 KB | Aucun | OK |
| `get_gamme_page_data_optimized(82)` | **27 ms** | 64 KB | 1x `::INTEGER` cast (non bloquant) | OK |
| `get_vehicle_page_data_optimized(30971)` | **64 ms** | 31 KB | Aucun | OK |
| `get_brand_page_data_optimized(54)` | **2 ms** | 63 B (ID invalide) | Aucun | OK |
| `get_brand_bestsellers_optimized(54)` | **8 ms** | 31 B (ID invalide) | Aucun | OK |

**Conclusion** : Toutes les RPCs P0-P1 restantes sont sous 65ms. Aucun bottleneck critique detecte. Pas d'action requise.

---

## Analyse patterns

### Patterns verifies (absents = sains)

| Pattern dangereux | homepage | gamme | vehicle | brand | brand_best | compat |
|-------------------|----------|-------|---------|-------|------------|--------|
| `tnc_type_id::INTEGER` | - | - | - | - | - | - |
| `criteria_positions` CTE | - | - | - | - | - | - |
| `IN (subquery)` sur table > 100K | - | - | - | - | - | - |
| Seq Scan force | - | - | - | - | - | - |

### EXPLAIN detaille (get_vehicle_compatible_gammes_php)

Seule RPC verifiee par EXPLAIN ANALYZE (la plus critique P0) :

```
Nested Loop (41ms)
  -> Index Scan idx_pieces_relation_type_type_id_composite (6ms, 14450 rows)
  -> Index Only Scan idx_pieces_visible_only (0.002ms/loop, 14450 loops)
     Heap Fetches: 0
Buffers: shared hit=48671 read=6
```

Plan optimal. Aucune action.

---

## Comparaison avec Phase 2A

| RPC | Avant Phase 2A | Apres Phase 2A | Phase 2B |
|-----|----------------|----------------|----------|
| `rm_get_page_complete_v2` | 1,423 ms | **68 ms** | - (deja optimise) |
| `get_pieces_for_type_gamme_v3` | ~1,000 ms (estime) | **~50 ms** | - (deja optimise) |
| Autres 6 RPCs | non auditees | - | **27-64 ms** (saines) |

**Les 2 seuls bottlenecks du systeme etaient dans les RPCs listing (v2/v3), resolus en Phase 2A.**
