# Planning Canonical Schemas

Schemas YAML versionnés gouvernant le système Planning Live (ADR-053).

## Files

- `planning-priority.yml` — taxonomie P0..P8 + SLA
- `planning-itemtype.yml` — types items (PR/ADR/ROADMAP/INCIDENT/EPIC) + canonical_id pattern
- `planning-blocked-reason.yml` — reasons valides quand status=blocked
- `planning-status.yml` — lifecycle items

## Versioning

Tout changement passe par PR vault avec ADR-link. `version` (semver) reflète le schema lui-même.
`schema_version: planning.v1` est la version du contrat global utilisée par les snapshots.

## Usage

Consommé par `_scripts/planning/schemas.py` (loader + validator).

## References

- ADR-053 Planning Live System (décision canon)
- MOC-Planning-Live (mirror humain)
