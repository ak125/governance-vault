---
id: ADR-053
title: Planning Live System (cross-repo PR/ADR aggregation)
status: accepted
date: 2026-05-08
deciders: [Fafa]
decision_makers: [Fafa]
related: [MOC-Roadmap-2026, MOC-Planning-Live, ADR-034]
# --- état spécifique Planning Live (NOT a canon ADR field) ---
planning_live_state: live
live_since: 2026-05-08
observability_required_days: 7
override_observability_gate: true
override_rationale: "User signoff explicite 2026-05-08 17:30 UTC — empirical proof early : 1er real run end-to-end success (commit 4fa3784, 81 items, MOC + snapshot écrits sans incident, 2 bugs empiriques captés et fixés en PR #224 + #225). Le système est validé empiriquement plutôt que par observation passive de 7 jours."
---

# ADR-053: Planning Live System

## Context

Session 2026-05-08 a montré qu'un roadmap manuel à 7 niveaux couvrant ~50 PRs/ADRs sur 2 repos
(vault + monorepo) avec 4 chantiers concurrents devient ingérable sans tooling. Trello a été
écarté (SoT parallèle au MOC vault, viole governance no-duplication). GitHub Projects v2 est
natif au workflow GitHub déjà en place mais l'API GraphQL est fragile (IDs opaques, rate limits,
syntaxe instable).

## Decision

Construire un système où :
1. **MOC-Planning-Live.md + git history + ledger/snapshots/planning/run-*.json** = SoT canonique
2. **GitHub Projects v2** = projection UI best-effort (panne ⇒ système continue)
3. **GitHub Issues alertes P0** = projection notification best-effort (label `planning-p0-stagnant`,
   close=ack ; panne ⇒ fallback email SMTP)
4. **Sync** : VPS DEV cron daily 08:00 UTC, entry shell `_scripts/planning/run-cron.sh` →
   orchestrator Python `_scripts/planning/sync_planning.py`. Aligné canon vault read-only-on-GHA
   (cf. `feedback_cron_vps_canon_pour_mono_vps_setup.md`).

## Invariants

- **I1** : MOC + git + snapshots = SoT canonique. GH Project + GH Issues + email = best-effort.
- **I2** : `sync_planning.py` = unique writer auto. Exception humaine : bloc YAML `ack` uniquement.
- **I3** : Commit MOC "business update" ssi `semantic_hash` change. Updates techniques (ack)
  = commits séparés (`chore(planning): ack update [no-hash-change]`).
- **I4** : Priority/ItemType/BlockedReason/Status = 4 schemas YAML versionnés sous
  `.spec/00-canon/planning/`. `schema_version: planning.v1` dans chaque snapshot.
- **I5** : Alertes GitHub Issues rate-limited + ackables (close=ack) + best-effort, fallback
  email SMTP. Cooldown : pas de duplicate issue si une issue ouverte avec même `canonical_id`
  existe (dedup natif). Ack : `gh issue close` → prochain run lit
  `--state closed --label planning-p0-stagnant` et persiste `acked_at` dans MOC.
  Échec `gh issue create` (rate limit, scope) = fallback email, exit 0 sauf `--strict-alerts`.

### `semantic_hash` blacklist exhaustive

EXCLUS : `last_alert_at`, `acked_at`, `mute_until`, `stagnation_days`, `generated_at`,
`schema_version`, `source_status`, ordre non-canonique.

INCLUS : `canonical_id`, `priority`, `item_type`, `status`, `blocked_reason`, `owner`,
`depends_on[]`, `adr_link`, `title`.

## Lifecycle (3 phases)

1. **PR-1 mergée** : ADR existe en `status: proposed`, système `planning_live_state: observing`
2. **PR-3 mergée** : ADR promu `status: proposed → accepted` (canon LIVE règle générale).
   `planning_live_state` reste `observing`, `live_since: null` — système accepté mais en obs.
3. **+7j obs green + signoff Fafa** : audit-trail dédié promote
   `planning_live_state: observing → live`, set `live_since: <ISO date>`.
   Système LIVE canon ET LIVE opérationnel.

## Schemas canoniques

Voir `.spec/00-canon/planning/` :
- `planning-priority.yml` (P0..P8 + SLA)
- `planning-itemtype.yml` (PR/ADR/ROADMAP/INCIDENT/EPIC)
- `planning-blocked-reason.yml`
- `planning-status.yml`

## §6 Mécanisme d'alerte

**Décision PR-3 : (a) GitHub Issues primary + (b) email SMTP fallback.**

### Options évaluées

- ❌ **Paperclip HTTP POST** : Paperclip est en mode observation chez l'opérateur (pas d'auto-action). Ack structuré gaspillé sans interaction active sur le dashboard. Token + URL à gérer comme nouveau secret.
- ❌ **Webhook Slack/Discord seul** : pas d'ack structuré natif. Devrait recréer ack côté MOC manuellement.
- ❌ **Email seul** : universel mais pas d'ack structuré, pollution inbox.
- ✅ **GitHub Issues + email fallback** : retenu (cf. rationale).

### Mécanisme retenu

**Primary** : `gh issue create --repo ak125/governance-vault --title "[P0 stagnant Nd] <canonical_id>" --label "planning-p0-stagnant" --body "<details>"`.

**Dedup** : avant create, lookup `gh issue list --repo ak125/governance-vault --label planning-p0-stagnant --state open --json number,title --search "<canonical_id> in:title"`. Si existe ⇒ skip (pas de re-create, pas de spam).

**Ack** : opérateur ferme l'issue (UI ou `gh issue close N`). Prochain run cron lit `gh issue list --label planning-p0-stagnant --state closed --json number,title,closedAt,closedBy --limit 100`, extrait `canonical_id` du titre, persiste `acked_at: <closedAt>` + `acked_by: <closedBy.login>` dans bloc `ack` du MOC (commit technique `ack update [no-hash-change]`).

**Fallback email SMTP** : si `gh issue create` échoue (rate limit, scope manquant, network), `send_alert_email()` envoie un email à `EMAIL_ALERT_TO` via `smtplib.SMTP(SMTP_HOST, SMTP_PORT)` (env vars de `/etc/automecanik/planning.env`). Best-effort : si SMTP fail aussi, log warning, exit 0 sauf `--strict-alerts`.

### Rationale

- **Cohérence SoT** : items du Planning Live = PRs/ADRs sur GitHub. Alertes = issues GitHub. Tout dans le même outil.
- **Notification native gratuite** : créer une issue déclenche déjà une notification email + mobile push à l'opérateur (s'il watch le repo) — donc l'email "fallback" est une seconde garantie, pas le canal primaire.
- **Ack natif** : `gh issue close` (CLI) ou bouton "Close" (mobile) — UX standard. Pas de UI custom à apprendre.
- **Pas de nouveau secret** : `gh` CLI déjà auth sur VPS DEV (scope `repo` couvre `issues:write`). Aucun PAT supplémentaire.
- **Dedup natif** : une issue ouverte avec `canonical_id` dans le titre suffit comme verrou. Pas besoin de cooldown 24h en mémoire — l'issue elle-même EST le rate-limiter.

### Variables d'environnement

| Variable | Source | Obligatoire | Notes |
|----------|--------|-------------|-------|
| `GH_TOKEN` | déjà auth via `gh auth login` (gh config) | oui (pour create issue) | Scope `repo` requis (couvre `issues:write`) |
| `SMTP_HOST` | `/etc/automecanik/planning.env` | non (fallback) | ex `smtp.gmail.com` ou relay local `localhost:25` |
| `SMTP_PORT` | idem | non | défaut 587 si absent |
| `SMTP_USER` / `SMTP_PASSWORD` | idem | non | App password si Gmail |
| `SMTP_FROM` | idem | non | `automecanik-bot@<domain>` |
| `EMAIL_ALERT_TO` | idem | non (sinon skip email) | `automecanik.seo@gmail.com` |

Provisioning VPS DEV : voir Annexe C (file `/etc/automecanik/planning.env`,
permissions 0640, owner deploy). Kit one-shot manuel hors-repo.

## Annexe A : Project IDs GitHub

À remplir après setup one-shot Task 1.12. **Format machine-readable obligatoire** (bloc YAML
parsable par `_read_project_number_from_adr` — éviter regex fragile).

Distinguer **deux** identifiants :

- `project_number` (entier) → **utilisé par `gh project` CLI**
  (ex. `gh project view 42 --owner ak125`)
- `project_id` (`PV2_xxx`) → **utilisé par GraphQL API**
  (ex. `gh api graphql -f query='query { node(id: "PV2_xxx") { … } }'`)

Champs custom (9 au total) — `PVTSSF_xxx` pour single-select, `PVTF_xxx` pour text/number :

```yaml
github_project:
  project_number: 2
  project_id: "PVT_kwHOAslOC84BXISt"
  field_ids:
    # Custom fields (9 — créés via setup-github-project.sh 2026-05-08)
    priority: "PVTSSF_lAHOAslOC84BXIStzhSXWvE"
    itemtype: "PVTSSF_lAHOAslOC84BXIStzhSXWv8"
    plan_status: "PVTSSF_lAHOAslOC84BXIStzhSXWw0"   # renamed from "status" — collision avec default GH Status field
    blocked_reason: "PVTSSF_lAHOAslOC84BXIStzhSXWw4"
    owner: "PVTF_lAHOAslOC84BXIStzhSXWw8"
    stagnation_days: "PVTF_lAHOAslOC84BXIStzhSXWxA"
    depends_on: "PVTF_lAHOAslOC84BXIStzhSXWxE"
    adr_link: "PVTF_lAHOAslOC84BXIStzhSXWx8"
    canonical_id: "PVTF_lAHOAslOC84BXIStzhSXWzM"
    # Default GH fields (référence, non-écrits par sync_planning) :
    # title, assignees, status (default — distinct de plan_status), labels, etc.
```

URL : https://github.com/users/ak125/projects/2

Note : `ak125` est un User account, pas une Organization → la requête GraphQL utilise
`user(login: $login)`, pas `organization(login: $login)`. Le setup script
`setup-github-project.sh` a été corrigé en conséquence (cf. PR #229).

Récupérer via : `gh project field-list 2 --owner ak125 --format json --jq '.fields[] | {name, id}'`.

## Annexe B : Procédure GraphQL fallback

Si `gh project field-create` casse (CLI version drift, parsing options enum etc.),
utiliser GraphQL directement.

**1. Récupérer le `project_id` (PV2_xxx)** :

```bash
gh api graphql -f query='
  query($login: String!, $number: Int!) {
    organization(login: $login) {
      projectV2(number: $number) { id }
    }
  }' -f login=ak125 -F number=$PROJECT_NUM \
  --jq '.data.organization.projectV2.id'
```

**2. Créer un champ single-select** (ex: `Priority`) :

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
    createProjectV2Field(input: {
      projectId: $projectId,
      dataType: SINGLE_SELECT,
      name: $name,
      singleSelectOptions: $options
    }) {
      projectV2Field {
        ... on ProjectV2SingleSelectField { id name }
      }
    }
  }' \
  -f projectId="$PROJECT_ID" \
  -f name="Priority" \
  -F options='[
    {"name":"P0","color":"RED","description":"page-someone tier"},
    {"name":"P1","color":"ORANGE","description":"current sprint"},
    {"name":"P2","color":"YELLOW","description":"sprint backlog"},
    {"name":"P3","color":"GREEN","description":"cycle backlog"},
    {"name":"P4","color":"BLUE","description":"quarter backlog"},
    {"name":"P5","color":"PURPLE","description":"triage"},
    {"name":"P6","color":"PINK","description":"idea"},
    {"name":"P7","color":"GRAY","description":"deferred"},
    {"name":"P8","color":"GRAY","description":"archive"}
  ]'
```

**3. Créer un champ texte** (ex: `Owner`, `CanonicalId`, `AdrLink`) :

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $name: String!) {
    createProjectV2Field(input: {
      projectId: $projectId,
      dataType: TEXT,
      name: $name
    }) {
      projectV2Field {
        ... on ProjectV2Field { id name }
      }
    }
  }' \
  -f projectId="$PROJECT_ID" \
  -f name="CanonicalId"
```

**4. Créer un champ nombre** (ex: `StagnationDays`) :

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $name: String!) {
    createProjectV2Field(input: {
      projectId: $projectId,
      dataType: NUMBER,
      name: $name
    }) {
      projectV2Field {
        ... on ProjectV2Field { id name }
      }
    }
  }' \
  -f projectId="$PROJECT_ID" \
  -f name="StagnationDays"
```

Itérer pour les 9 champs : 4 single-select (Priority, ItemType, Status, BlockedReason),
4 text (Owner, DependsOn, AdrLink, CanonicalId), 1 number (StagnationDays).

## Hors scope (volontaire)

- HealthScore 0-100 (besoin baseline 30j snapshots)
- Execution intelligence (planning-intelligence.py daily digest)
- DependsOn graph viz cycle/topo
- Multicanal Slack/Discord policy
- Promotion en lot des 11 ADRs proposed (chantier séparé)
- GH Projects v2 automation rules (viole I2)
- GH Projects v2 custom field population (Priority/ItemType/Status/CanonicalId/...) :
  PR-2 = `item-add` only. Vues Kanban par Priority non-fonctionnelles avant follow-up PR-2.x.
- stagnation_days pour ADRs : MVP utilise `updated_at` des PRs uniquement. Follow-up PR-2.x
  ajoutera tracking via `git log -1 --format=%ct -- ledger/decisions/adr/ADR-NNN-*.md`.

## Consequences

**Positives** :
- Visibilité quotidienne automatique
- Audit-trail complet via snapshots immuables
- Découplage SoT canonique vs projections UI
- Aligné canon vault (VPS DEV cron, pas write-on-GHA)

**Négatives / risques** :
- Coût initial ~10h
- API GH Projects v2 fragile (mitigé par I1)
- Maintenance schemas YAML (mitigé par versioning)

## References

- MOC-Roadmap-2026 (chantier complémentaire stratégique)
- ADR-034 AI-COS Operating Contract (alertes)
- feedback_canon_rule_live_iff_adr_accepted.md (préservé, pas modifié)
- feedback_cron_vps_canon_pour_mono_vps_setup.md (runtime VPS DEV justifié)
