---
type: meta
status: canon
updated: 2026-05-10
---

# Governance Runtime Map

Snapshot du système governance vault au moment de l'ouverture de la série PR-1..6
(« Vault Documentaire → Vault Exécutable »). Document vivant — mettre à jour à
chaque ajout de script governance ou modification de write/read path.

Sans ce snapshot, PR-3 (sync-moc-decisions) et PR-4 (ci-vault-gate strict)
deviendront opaques dans 2 mois. Ce map est la précondition documentaire.

## Composants par couche

### Couche A — Canonical sources

- `_scripts/schemas/{adr,rule,moc,incident,...}.schema.json` : authority de
  validation frontmatter (8 fichiers actuellement, 4 avec `status.enum`)
- `ledger/decisions/adr/ADR-*.md` : SoT décisions (frontmatter = state machine)
- `ledger/rules/rules-*.md` : SoT règles canon
- `.spec/00-canon/planning/*.yml` : SoT planning

### Couche B — Runtime mirrors / projections

- `_scripts/governance_constants.py` : runtime mirror des schemas (PR-2,
  parity-tested)
- `ops/moc/MOC-Decisions.md` : projection ADR frontmatter (PR-3, marker
  `<!-- AUTO-GENERATED:* -->`)
- `ops/moc/MOC-AuditTrail.md` : à projetter en follow-up (hors scope PR-1..6)

### Couche C — Validators & generators (scripts)

| Script | Type | Lit | Écrit | Invoqué par |
|--------|------|-----|-------|-------------|
| `check-frontmatter-schema.py` | validator | `schemas/*` + frontmatters | findings | weekly-lint |
| `check-moc-integrity.py` | validator | MOCs + ADR frontmatters | findings | weekly-lint |
| `check-adr-supersedes.py` | validator | ADR frontmatters | findings | weekly-lint |
| `check-obsolete-rules.py` | validator | rule frontmatters | findings | weekly-lint |
| `check_no_direct_schema_enum_access.py` | validator (PR-2b) | `_scripts/*.py` AST | findings | weekly-lint |
| `sync-moc-decisions.py` | generator (PR-3) | ADR frontmatters | `MOC-Decisions.md` (entre markers) | cron VPS DEV |
| `weekly-lint.sh` | **🔧 Governance Runtime Entrypoint** | tous les checks | `findings.json` + `report.md` | GHA cron + ci-vault-gate |
| `ci-vault-gate.sh` | gate (PR-4) | weekly-lint output | exit 0/1 + GH issue `infra-fail` | `vault-governance.yml` + `vault-weekly-lint.yml` |

> **⚠️ Reframing important** : `weekly-lint.sh` n'est plus « juste du lint ».
> Il est devenu progressivement l'entrypoint runtime du governance kernel :
> scheduler logique, agrégateur, reporting engine, gate engine, dispatcher.
> Le nom historique reste pour la rétrocompat ; le mental model doit changer.
> Renommage explicite (`governance-runtime.sh`) en follow-up quand un signal
> le justifie (ex: nouveau contributeur confus).

### Couche D — Automation (CI + cron)

GHA workflows actifs (5 fichiers `.github/workflows/`) :

| Workflow | Déclenchement | Rôle |
|----------|---------------|------|
| `vault-governance.yml` | sur PR | gates G2/G3, broken-links, v1-paths, canon-write-block. PR-4 ajoute `ci-vault-gate.sh pr` |
| `vault-weekly-lint.yml` | Monday 02:00 UTC | weekly-lint complet + artifact diffing. PR-4 ajoute `ci-vault-gate.sh weekly` |
| `vault-self-review-marker.yml` | sur PR | enforce `Self-review verdict: APPROVE` body marker |
| `vault-supabase-cost-check.yml` | scheduled | DB cost monitoring (ADR-035) |
| `canon-publish.yml` | sur push tag/main | publish canon hashes vers consommateurs (monorepo, AEC) |

Cron VPS DEV (Monday 01:30 UTC, ajouté par PR-3) : `sync-moc-decisions.py
--write` + auto-PR signée G3. Documenté dans `99-meta/cron-setup.md` (section
« Cron actifs sur VPS DEV », ajoutée par PR-3).

Branch protection main : signed commits G3 obligatoires, required status checks.
**Gap connu** : `enforce_admins=false` aujourd'hui sur le vault — admin peut
bypass. À combler par PR séparée hors scope PR-1..6 (cf. modèle 3-couches §
ci-dessous).

## Modèle 3 couches de protection

État actuel de la protection effective du vault :

| Couche | Mécanisme | État vault 2026-05-10 | Couvert par |
|--------|-----------|------------------------|-------------|
| **L1 — Canonique (logique)** | ADRs / SoT / canonical routes / role canon / URL ownership / write-path | ✅ Actif | ADR-015, R-SEO-09, frontmatter schemas, série PR-1..3 |
| **L2 — CI (structurel)** | weekly-lint + ci-vault-gate.sh PR mode + parity test enums + AST no-direct-schema | 🟡 Partiel (weekly-lint OK, strict gate pas encore actif) | PR-2 / PR-2b / PR-4 |
| **L3 — GitHub branch (runtime)** | `enforce_admins=true` + signed commits G3 + required reviews | 🔴 Gap : `enforce_admins=false` sur main | PR séparée hors scope PR-1..6 |

Annoncer « système verrouillé » suppose les 3 couches ✅. Aujourd'hui un admin
peut techniquement bypass L1+L2 par push direct. Ce gap est traité par une PR
dédiée hors série, pour ne pas mélanger gouvernance logique + sécurité GitHub.

## Write paths

| Path | Write authority | Method |
|------|-----------------|--------|
| `ledger/decisions/adr/ADR-*.md` | humains | PR signée G3 |
| `ledger/rules/rules-*.md` | humains | PR signée G3 |
| `ops/moc/MOC-Decisions.md` (contenu entre markers AUTO-GENERATED) | cron VPS DEV (PR-3) | auto-PR signée G3 |
| `ops/moc/MOC-Decisions.md` (colonne Notes inside markers) | humains | PR signée G3, préservée par cron |
| `_scripts/*.py` | humains | PR signée G3 |
| `_scripts/schemas/*.schema.json` | humains (rare, ADR requise) | PR signée G3 |
| `99-meta/cron-setup.md` | humains | PR signée G3 |
| GH Issues label `infra-fail` | `ci-vault-gate.sh` | GHA token, debounced 6h |

## Read paths

| Read source | Read by |
|-------------|---------|
| `schemas/*.schema.json` (full schema) | `check-frontmatter-schema.py` (validation conformité) |
| `schemas/*.schema.json` (enum extraction) | `test_governance_constants.py` UNIQUEMENT (parity test) |
| `governance_constants.py` | tous les autres scripts (impérativement, pas de parse direct enum) |
| ADR frontmatters | `sync-moc-decisions.py`, `check-moc-integrity.py`, `check-adr-supersedes.py` |

## Forbidden patterns (governance-runtime-boundaries)

1. ❌ Aucun script ne parse `*.schema.json` pour **extraire des enums** (sauf
   `test_governance_constants.py`) — enforced par PR-2b walker AST. Validation
   complète du schema (`check-frontmatter-schema.py`) reste légitime.
2. ❌ `governance_constants.py` ne contient AUCUNE fonction calculée, AUCUN
   import hors `__future__` — enforced par TestPurity (PR-2)
3. ❌ Aucun cron / CI ne push direct main — toujours auto-PR signée G3
4. ❌ Aucune édition manuelle entre markers `<!-- AUTO-GENERATED:* -->` (sauf
   colonne Notes) — détecté par `sync-moc-decisions.py --check`
5. ❌ Aucun script governance ne fait orchestration cross-repo, runtime state
   mutation, ou decision-making (= entreraient dans le Governance Engine —
   out-of-scope vault)
6. 🔒 **AUCUN script, workflow, ou agent ne lit le contenu de la colonne Notes
   pour en dériver une décision.** Notes = humain-only, jamais machine-read.
   Enforced par review (rejet de toute PR introduisant `parse_notes_for_X()`).

## Trigger to revisit this map

- Ajout d'un nouveau script `_scripts/*.py` non listé Couche C → mettre à jour
  le tableau
- Ajout d'un nouveau write path → mettre à jour write paths
- Modification du flow cron VPS DEV → mettre à jour Automation
- Activation de `enforce_admins=true` sur main → passer L3 à ✅ dans le tableau
  3-couches
- ADR canon-doc `governance-runtime-boundaries.md` créée → linker depuis ce map
