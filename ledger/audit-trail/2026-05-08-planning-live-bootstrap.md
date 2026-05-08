---
date: 2026-05-08
type: audit-trail
related: [ADR-053, MOC-Planning-Live]
---

# 2026-05-08 — Planning Live Bootstrap (PR-1)

## What

PR-1 du système Planning Live mergée :
- ADR-053 créé en `status: proposed` + `planning_live_state: observing`
- 4 schemas canoniques sous `.spec/00-canon/planning/` (priority, itemtype, blocked-reason, status)
- MOC-Planning-Live.md avec seed manuel (items P0..P5 du roadmap session 2026-05-08)
- Scaffolding `ledger/snapshots/planning/` (vide pour l'instant, README explique format)
- check-moc-integrity étendu via mises à jour `updated:` cohérentes (MOC-Decisions, MOC-AuditTrail, MOC-Governance)

**Deferred to PR-1.x follow-up** :
- Création GitHub Project v2 + 9 champs custom (Annexe A §ADR-053). Bloqué par token gh CLI
  manquant scope `read:project,project` — refresh interactif requis. Voir suivi PR-1.x.
- En attendant, MOC-Planning-Live.md + git history = SoT canonique (I1). Le board est une
  projection UI best-effort, son absence ne bloque ni PR-2 (sync engine) ni PR-3 (alerts).

## Why

Roadmap manuel à 7 niveaux ingérable (cf. ADR-053 Context). 7 reviews architecturales
itératives ont consolidé les invariants I1..I5, le runtime VPS DEV cron (vs GHA write-blocked
canon vault), et les schemas canoniques.

## Runtime upgrade

- `gh CLI` upgradé 2.4.0 → 2.92.0 sur VPS DEV (ajout source officiel `cli.github.com`)
  — nécessaire pour `gh project` natif (was 2022-era version, manquait subcommand `project`).

## Next

PR-2 : sync engine (Python orchestrator + cron VPS DEV + tests + snapshots auto).
PR-1.x follow-up : refresh `gh auth refresh -s read:project,project` interactif puis
exécuter Task 1.12 du plan (création board + 9 champs custom + remplir Annexe A ADR-053).

## Verification

- ✅ `python3 _scripts/check-moc-integrity.py /opt/automecanik/governance-vault --strict` exit 0
- ⏸ `gh project view` → différé (auth scope manquant, voir PR-1.x)
- ⏸ Items seed P0/P1 dans le board → différé (idem)
- ✅ vault-weekly-lint reste vert
