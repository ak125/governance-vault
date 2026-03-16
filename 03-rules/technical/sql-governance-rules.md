# SQL Governance Rules

> **Version** : 1.0.0 | **Date** : 2026-03-14
> **Statut** : ACTIVE
> **Contexte** : Post-Phase 1 remediation (-24 GB, -35% indexes) + Phase 2A optimization (x21 sur RPC principale)

---

## 4 regles anti-regression

### R1 — EXPLAIN de reference pour toute RPC critique

Toute nouvelle RPC sur le hot path (listing, SEO, vehicle, homepage) doit avoir un EXPLAIN ANALYZE de reference **avant merge**.

**Application** :
- Documenter dans `.spec/00-canon/db-governance/` avec params reels
- Seuil d'alerte : >200ms sur cold cache, >100ms sur warm cache
- Pattern interdit : `IN (SELECT ...)` sur table >100K rows → utiliser `LEFT JOIN LATERAL ... LIMIT 1`

**Justification** : La RPC `rm_get_page_complete_v2` a eu un bottleneck 907ms invisible sans EXPLAIN.

### R2 — Justification pour tout nouvel index

Tout nouvel index doit avoir un commentaire dans la migration SQL :

```sql
-- INDEX: idx_xxx
-- Table: xxx (N rows, X GB)
-- Pattern: JOIN/WHERE sur colonne Y avec cast Z
-- Gain attendu: Seq Scan N rows → Index Scan ~M rows
-- RPC concernees: rpc_name_1, rpc_name_2
CREATE INDEX CONCURRENTLY idx_xxx ON table (...);
```

**Justification** : 27 indexes supprimes en Phase 1 car crees sans justification ni suivi d'usage.

### R3 — Verification doublons d'index avant migration

Avant toute migration SQL creant un index :
1. Verifier `M2` (top indexes par taille) et `M6` (indexes 0-scan)
2. Comparer avec les indexes existants sur la meme table : `SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'xxx'`
3. Si un index similaire existe : justifier pourquoi les deux sont necessaires

**Justification** : Phase 1 a identifie 5+ paires d'indexes doublons (meme table, meme colonne, variantes inutiles).

### R4 — Fiche de suivi pour alertes persistantes

Toute alerte M2-M6 qui persiste >1 semaine apres detection doit :
1. Etre documentee avec une decision (action, report, acceptation)
2. Si action : ouvrir une issue GitHub avec le label `db-governance`
3. Si acceptation : documenter la raison (table attendue en croissance, index de securite, etc.)

**Justification** : Les alertes sans suivi perdent leur valeur. Le monitoring M1-M6 est inutile si les alertes sont ignorees.

---

## Patterns interdits (detectes en Phase 2A)

| Pattern | Risque | Alternative |
|---------|--------|-------------|
| `column_text::INTEGER IN (SELECT id FROM large_table)` | Merge Join scan full index | `LEFT JOIN LATERAL ... LIMIT 1` |
| `column_text::INTEGER = param::INTEGER` quand column est TEXT | Invalide les indexes btree TEXT | `column_text = param::TEXT` |
| Index partiel avec filtre non utilise par la RPC | Index cree mais jamais utilise par le planner | Verifier que les WHERE de l'index matchent ceux de la RPC |
| `DISTINCT ON` sur CTE avec `IN (subquery)` | Force materialisation + scan complet | LATERAL avec LIMIT 1 |

---

## Outils disponibles

| Outil | Usage |
|-------|-------|
| `GET /api/admin/db-governance/metrics` | M1-M6 live |
| `POST /api/admin/db-governance/snapshot` | Sauvegarder un snapshot |
| `GET /api/admin/db-governance/trend/:id` | Comparer N vs N-1 |
| `GET /api/admin/db-governance/quarterly-review` | Checklist trimestrielle |
