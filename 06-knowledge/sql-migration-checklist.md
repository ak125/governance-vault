# SQL Migration Checklist

> Template a utiliser avant chaque migration SQL touchant schema/indexes/RPCs.

---

## Pre-merge

- [ ] **Index existants** : `SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'TABLE'` — pas de doublon
- [ ] **M6 unused** : verifier que les indexes 0-scan sur la meme table ne sont pas redondants avec le nouveau
- [ ] **CONCURRENTLY** : tout `CREATE INDEX` utilise `CONCURRENTLY` (pas de lock table en prod)
- [ ] **Commentaire** : chaque index a un commentaire justificatif (table, pattern, gain attendu, RPCs)
- [ ] **IF NOT EXISTS** : toute creation de table/index utilise `IF NOT EXISTS`

## RPCs

- [ ] **Pas de cast invalide** : pas de `text_column::INTEGER = param` quand un index btree(text) existe
- [ ] **Pas de IN (subquery)** sur table >100K rows : utiliser `LEFT JOIN LATERAL ... LIMIT 1`
- [ ] **EXPLAIN reference** : si RPC critique, EXPLAIN ANALYZE documente dans `.spec/`
- [ ] **SECURITY DEFINER** : toute RPC admin a `SECURITY DEFINER` + `SET search_path = public`

## Post-merge

- [ ] **ANALYZE** : executer `ANALYZE table_name` apres creation d'index
- [ ] **Snapshot** : `POST /api/admin/db-governance/snapshot` pour baseline post-migration
- [ ] **Verification M2** : verifier que le nouvel index apparait dans M2 avec un idx_scan > 0 apres quelques heures
