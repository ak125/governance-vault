---
date: 2026-05-08
type: audit-trail
related: [ADR-053-planning-live-system, MOC-Planning-Live]
---

# 2026-05-08 — Planning Live promotion observing → live (override 7d gate)

## What

Promotion ADR-053 phase 3 (lifecycle) avec **override explicite** du gate 7j observabilité :

- `planning_live_state: observing → live`
- `live_since: null → 2026-05-08`
- `override_observability_gate: true`
- `override_rationale` : "User signoff explicite — empirical proof early"

## Why override the 7d gate

Le gate `observability_required_days: 7` était défini dans ADR-053 phase 2 (PR-3 mergée avec
`status: accepted` + `planning_live_state: observing`) comme garde-fou contre une promotion
prématurée. La logique : laisser tourner 7 jours, vérifier les logs, puis promouvoir si OK.

L'override est justifié par **preuve empirique acquise plus tôt que prévu** :

1. **1er real run end-to-end SUCCESS** (2026-05-08 17:20 UTC, commit `4fa3784`)
   - 81 items aggregés (30 vault PRs + 51 monorepo PRs + 0 ADRs proposed)
   - MOC réécrit, snapshot immutable créé (`run-172010Z.json`)
   - Push signé G3 vers main accepté
   - exit code 0

2. **2 bugs empiriques captés et fixés** durant le force-run :
   - Fix #224 : `cron_report` function name (lib-supabase-report.sh contract mismatch)
   - Fix #225 : writer wikilink slug (`[[ADR-053]]` → `[[ADR-053-planning-live-system]]`)
   - Ces bugs auraient été silencieux/différés sans le force-run — le gate 7j ne les aurait
     pas captés mieux

3. **Self-Review §4 lint shipped** (PR #226) : ruff + mypy clean, 0 issue.

4. **37 tests pytest passing** + 1 skip (real_gh GH_TOKEN-gated) — couverture cohérente.

L'ensemble valide empiriquement le système. L'attente passive de 7 jours n'apporterait
aucune information supplémentaire (le système ne "découvre" rien de nouveau en restant
idle ; les vrais signaux sont déjà acquis).

User signoff explicite : "faite le" 2026-05-08 17:30 UTC.

## Constraint preserved

L'override est **documenté** dans le frontmatter ADR-053 (`override_observability_gate: true`
+ `override_rationale`). Toute future audit / récupération de gouvernance peut tracer la
décision et la justifier.

Le pattern reste valide pour de futurs ADR avec `observability_required_days` : par défaut,
attendre. L'override est une exception explicite, pas une norme.

## Cross-references

- ADR-053 frontmatter : `planning_live_state: live`, `live_since: 2026-05-08`
- Commit empirique : 4fa3784
- 6 PRs mergées : #221 (foundation) + #222 (sync) + #223 (alerts) + #224 (cron_report fix) + #225 (wikilink fix) + #226 (lint)
- Memory : `feedback_force_run_catches_empirical_bugs.md` (2 bugs trouvés via real-run)

## Next

- Cron daily 08:00 UTC continue de tourner (LIVE en production canon)
- Monitoring : `tail /var/log/governance-vault/planning-sync.log`
- Tout incident futur peut déclencher rollback `live → observing` via PR de gouvernance
