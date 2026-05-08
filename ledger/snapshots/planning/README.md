# Planning Snapshots

Snapshots immuables par run du système Planning Live (ADR-053).

## Format

### Canonique (immutable, append-only)

`{YYYY-MM-DD}/run-{HHMMSS}Z.json` — un fichier par run cron, jamais réécrit.

```json
{
  "schema_version": "planning.v1",
  "generated_at": "2026-05-08T08:00:12Z",
  "semantic_hash": "abc123...",
  "items": []
}
```

### Pointer (non-canonique, réécrivable)

`{YYYY-MM-DD}/latest.json` — copie du dernier `run-*.json` du jour, **PAS authoritative**.
Utilité ergonomique uniquement (requêtes "dernier état du jour"). Toute requête historique
doit cibler `run-*.json` directement.

## Garanties

- Append-only : un `run-*.json` n'est jamais modifié post-écriture
- `schema_version` versionné : permet migrations futures
- Snapshot toujours committé, MÊME si MOC inchangé (semantic_hash stable)

## Consumed by

- `_scripts/check-moc-integrity.py` (validation cohérence avec MOC)
- `_scripts/planning/sync_planning.py` (lecture pour comparaison hash)
- (futur) `_scripts/planning/intelligence.py` (analytics sur 30j+ snapshots)

## See also

- [ADR-053](../../decisions/adr/ADR-053-planning-live-system.md)
- [MOC-Planning-Live](../../../ops/moc/MOC-Planning-Live.md)
