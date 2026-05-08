---
type: moc
status: proposed
updated: 2026-05-08
schema_version: planning.v1
semantic_hash: seed-pr1-2026-05-08
adr_link: ADR-053
---

# MOC-Planning-Live

## Contexte

Mirror humain-readable du système Planning Live (ADR-053). Source canonique = ce fichier
+ git history + `ledger/snapshots/planning/run-*.json`.

GitHub Project v2 + Paperclip alerts = projections best-effort, pas authoritative.

## Sources agrégées

- `gh pr list ak125/governance-vault --state open`
- `gh pr list ak125/nestjs-remix-monorepo --state open`
- `MOC-Decisions.md` table → ADRs status=proposed
- (futurs : incidents, roadmap items, epics)

## Items actifs (PR-1 seed)

| canonical_id | priority | item_type | status | title |
|--------------|----------|-----------|--------|-------|
| github:ak125/governance-vault:pr:149 | P1 | PR | review | Worktree script fix (G3 unblocker) |
| vault:adr:ADR-024 | P1 | ADR | review | R1 cache deployé — promote proposed→accepted |
| vault:adr:ADR-029 | P1 | ADR | review | RAG v2.1 P1 LIVE — promote |
| vault:adr:ADR-031 | P1 | ADR | review | Four-layer architecture wiki/raw shipped — promote |
| vault:adr:ADR-033 | P1 | ADR | review | Wiki gamme diagnostic relations wave 2 closed — promote |
| vault:adr:ADR-034 | P1 | ADR | review | AI-COS operating contract LIVE — promote |
| vault:adr:ADR-045 | P1 | ADR | review | SEO Monitoring Cron V0/V0.A shipped — promote |
| github:ak125/nestjs-remix-monorepo:pr:385 | P3 | PR | review | R6 PR-A+PR-C squashed (cascade) |
| github:ak125/nestjs-remix-monorepo:pr:386 | P3 | PR | review | R6 PR-B skill split |

(Liste complète sera générée auto par PR-2.)

## Ack block (édition humaine — exception I2)

```yaml
ack: {}
```

Format pour acks individuels :

```yaml
ack:
  "github:ak125/governance-vault:pr:149":
    acked_at: 2026-05-08T14:00:00Z
    acked_by: fafa
    mute_until: 2026-05-15T00:00:00Z
    reason: "Owner offline this week"
    last_alert_at: 2026-05-08T08:00:00Z   # auto-set by alerts.py
```

## Méthodologie

- Sync quotidien 08:00 UTC via VPS DEV cron `/etc/cron.d/planning-live` → `_scripts/planning/run-cron.sh`
- Commit MOC ssi `semantic_hash` change ("business update")
- Updates techniques (ack) = commits séparés `chore(planning): ack update [no-hash-change]`
- Snapshots immuables : `ledger/snapshots/planning/{date}/run-{HHMMSS}Z.json`
- `latest.json` = pointer non-canonique réécrivable (convenance)

## Hors scope

- HealthScore (besoin 30j baseline)
- DependsOn graph viz
- Promotion en lot des 11 ADRs proposed
- GH Projects v2 automation rules (viole I2)
- GH Project v2 custom field population (PR-2 = item-add only, vues Kanban non-fonctionnelles)
- stagnation_days pour ADRs (PR-2 MVP = PRs uniquement)

## Versionnage

- v0.1.0 (2026-05-08) — PR-1 seed manuel
- v0.2.0 — PR-2 sync engine (auto-updated)
- v1.0.0 — PR-3 alerts (post +7j obs green ⇒ `planning_live_state: live`)

## See also

- [[ADR-053-planning-live-system]]
- [[MOC-Roadmap-2026]]
- [[MOC-Decisions]]
