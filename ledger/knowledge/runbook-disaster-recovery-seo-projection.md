---
name: runbook-disaster-recovery-seo-projection
description: Disaster Recovery Procedure (DRP) pour SEO Runtime Projection (ADR-059). Replay deterministic depuis snapshots tar.zst immutables, validation sha256 + versions complètes, --dry-run/--apply strict. Classification G1/G2 critical governance infrastructure.
type: runbook
status: active
date: 2026-05-13
related_adr: ["ADR-059", "ADR-031", "ADR-021"]
related_rules: ["G1", "G2", "G3"]
---

# Runbook — Disaster Recovery SEO Runtime Projection (ADR-059)

> **Classification** : `critical governance infrastructure G1/G2` per ADR-059 §"Replay infrastructure".
>
> **Replay SoT non-négociable** : `tar.zst` immutable du object-store. **`git checkout` INTERDIT** comme source replay (force-push / mirror sync / submodule changes peuvent casser l'alignement historique).

## Quand utiliser ce runbook

Au moins UN des scénarios suivants déclenche une procédure DRP :

1. **Corruption DB** : intégrité de `__seo_entity_facts` / `__seo_entity_fact_versions` compromise (sha256 mismatch sur `content_hash`, ou conflits massifs `__seo_projection_conflicts` non auto-applicables).
2. **Migration cassée** : nouvelle migration applique mal le pattern kg_v3 ; rollback nécessaire vers état avant migration.
3. **Refactor projection runner** : besoin de re-projeter les exports historiques avec une nouvelle version du runner (test A/B ancien vs nouveau contrat sur même snapshot).
4. **Bump `projection_contract_version`** : passage `v1.x.x → v2.0.0` ; replay forward complet pour vérifier compatibilité.
5. **Audit légal** : reconstruction de l'état DB à une date donnée pour un audit (export-réel + golden).
6. **Replay staging** : reproduire un état prod sur staging (avec anonymisation découplée).

## Pré-requis

- Accès SSH VPS DEV / PROD avec rôle `deploy` (sudo non requis pour le replay)
- Variables d'environnement Supabase :
  - `SUPABASE_URL=https://<project>.supabase.co`
  - `SUPABASE_SERVICE_ROLE_KEY=<service_role>`
- Python 3.11+ avec deps : `click pyyaml hypothesis pytest supabase`
- Accès lecture à `/opt/automecanik/object-store/exports-snapshots/`
- Accès écriture à `/opt/automecanik/object-store/replay-queue/`
- `ADR-059.status == "accepted"` (vérification automatique par `assertCompatibleProjectionContract`)

## Procédure pas-à-pas

### Étape 1 — Identifier la fenêtre temporelle à replayer

```bash
# Lister les runs récents
psql "$DATABASE_URL" -c "
  SELECT id, started_at, status, exports_snapshot_hash, projection_contract_version
  FROM __seo_projection_runs
  ORDER BY started_at DESC
  LIMIT 20;
"
```

Identifier `--from-run` (UTC ISO 8601) et `--to-run` (UTC ISO 8601) selon le scénario (point dans le temps avant corruption, ou avant migration, etc.).

### Étape 2 — Dry-run (validation intégrité sans écriture)

```bash
cd /opt/automecanik/app
python3 scripts/seo-projection/replay_projection.py \
  --from-run 2026-05-13T10:00:00Z \
  --to-run   2026-05-13T11:00:00Z \
  --object-store /opt/automecanik/object-store
```

**Sortie attendue** :

```
=== replay_projection validation report ===
object_store: /opt/automecanik/object-store
target_projection_contract: 1.0.0
mode: DRY-RUN (default)
total runs: N
valid:   N (idéal)
invalid: 0 (idéal)
=== DRY-RUN complete (no writes). Pass --apply to materialize. ===
```

**Si `invalid > 0`** :

- `integrity:sha256_mismatch` → snapshot tar.zst corrompu ou tampered. **Investigation requise** : restaurer depuis backup offsite Hetzner (`/opt/automecanik/object-store-backup/`).
- `integrity:snapshot_missing` → snapshot supprimé manuellement (anti-pattern : `chattr +i` devrait empêcher). **Restaurer depuis backup offsite**.
- `version_missing:<field>` → run historique antérieur à la stricte fields-required policy. **Décision humaine** : exclure ce run de la fenêtre, ou patch manuel des versions.
- `manifest:manifest_sidecar_missing` → manifest JSON absent. **Re-générer via** `snapshot_exports_seo.py` si le tar.zst est intact.

### Étape 3 — Apply (génère manifest replay)

**ATTENTION** : `--apply` requiert `--manifest-out` explicite. Aucun défaut.

```bash
python3 scripts/seo-projection/replay_projection.py \
  --from-run 2026-05-13T10:00:00Z \
  --to-run   2026-05-13T11:00:00Z \
  --apply \
  --manifest-out /opt/automecanik/object-store/replay-queue/replay-$(date +%Y%m%d-%H%M%S).yaml
```

Le manifest YAML est écrit sous `<object-store>/replay-queue/`. Path enforcement strict : le script refuse toute autre destination.

### Étape 4 — Backend integration (manifest picker)

> Hors scope PR-6c-a. À implémenter en PR followup (PR-6c-followup ou PR-7).

Le backend NestJS picker (à venir) :

1. Watch `<object-store>/replay-queue/*.yaml`
2. Pour chaque manifest :
   - Validate via Zod (RefreshJobData-like schema)
   - Pour chaque `runs_to_replay[i]` : enqueue `WriteJob` BullMQ avec `trigger_kind='replay'` + `replayed_from_run_id`
3. Move manifest vers `<object-store>/replay-queue/.done/` après enqueue

Pour Phase B initiale (avant backend integration) : enqueue manuel via le backend admin endpoint OU script Node helper one-shot.

### Étape 5 — Audit trail post-replay

Un replay réussi crée une nouvelle ligne `__seo_projection_runs` avec :

- `status='success'`
- `trigger_kind='replay'`
- `replayed_from_run_id=<original_run_id>`

Vérifier :

```sql
SELECT id, started_at, ended_at, status, trigger_kind, replayed_from_run_id
FROM __seo_projection_runs
WHERE trigger_kind = 'replay'
ORDER BY started_at DESC
LIMIT 10;
```

Créer une entrée `ledger/audit-trail/YYYY-MM-DD-replay-<context>.md` pour documenter la motivation, fenêtre, runs replayés, résultat (cf. convention ADR-054 audit trail).

## Rollback strategy (si replay introduit régression)

**JAMAIS DELETE / TRUNCATE / DROP** sur `__seo_projection_*` ou `__seo_entity_*` (ADR-059 §Rollback).

Rollback canonique :

```sql
-- Pour chaque fact / block où active_version_id a flipé vers la version replay :
UPDATE __seo_entity_facts
SET active_version_id = <previous_active_version_id>
WHERE entity_id = '<entity>' AND fact_key = '<key>';

UPDATE __seo_content_blocks
SET active_version_id = <previous_active_version_id>
WHERE entity_id = '<entity>' AND role = '<role>' AND COALESCE(section, '') = COALESCE('<section>', '');
```

Audit trail préservé : les versions historiques restent dans `__seo_entity_fact_versions` / `__seo_content_block_versions` ; seul le pointer `active_version_id` change.

## Vérification post-recovery

Checklist obligatoire avant clôture incident :

- [ ] `replay_projection.py` dry-run sur fenêtre complète retourne `invalid: 0`
- [ ] Sample 5 entités random : `mv_seo_entity_facts_current` reflète l'état attendu
- [ ] `__seo_projection_conflicts.resolution = 'pending'` : aucun conflit non-acquitté > 24h
- [ ] Sentry alert `projection_contract_mismatch` : 0 sur 24h
- [ ] Audit-trail entry créée dans `ledger/audit-trail/YYYY-MM-DD-*.md` + linkée depuis MOC-AuditTrail

## Backup offsite (préventif)

Cron quotidien `0 5 * * *` (PR-5b followup) :

```bash
rsync -av --delete \
  /opt/automecanik/object-store/exports-snapshots/ \
  hetzner:/storage-box/automecanik/exports-snapshots-mirror/
```

En cas de corruption du object-store local :

```bash
rsync -av \
  hetzner:/storage-box/automecanik/exports-snapshots-mirror/ \
  /opt/automecanik/object-store/exports-snapshots/

# Re-apply chattr +i après restore
find /opt/automecanik/object-store/exports-snapshots/ -name "*.tar.zst" -exec chattr +i {} \;
```

## Garde-fous testés (CI replay-projection-regression.yml)

| Garde-fou | Test |
|---|---|
| Replay SoT = tar.zst | `test_sha256_property_*` (Hypothesis) |
| sha256 STRICT bit-exact | `test_sha256_strict_match`, `test_sha256_mismatch_rejected` |
| `git checkout` INTERDIT | `test_git_checkout_forbidden` (6 patterns) |
| `--dry-run` par défaut | `test_dry_run_default_in_cli_option` |
| `--apply` requires `--manifest-out` | `test_apply_requires_manifest_out` |
| 5 versions complètes | `test_missing_any_version_rejects` (parametrize) |
| 0 LLM / 0 DELETE / 0 wiki canon | `test_no_*_in_replay` (static scans) |
| Manifest path enforcement | `test_manifest_writer_refuses_*` (3 négatifs) |

36 tests CI sur chaque PR touchant `scripts/seo-projection/` ou `backend/src/modules/seo/projection/`.

## Références

- [[ADR-059-seo-runtime-projection]] (accepted 2026-05-13)
- [[ADR-031-four-layer-content-architecture]] (proposed — supplemented by ADR-059)
- [[ADR-021-database-rls-hardening-zero-trust]] (RLS canon pour `__seo_*`)
- Monorepo PR-6c-a : `scripts/seo-projection/replay_projection.py`
- Monorepo PR-5b : `scripts/cron/snapshot_exports_seo.py` (générateur tar.zst immutable)
- Monorepo PR-6a : `backend/supabase/migrations/*_seo_projection_*.sql` (7 tables + 2 MVs)
- Monorepo PR-6b : `backend/src/modules/seo/projection/` (workers BullMQ + assertCompatibleProjectionContract)
