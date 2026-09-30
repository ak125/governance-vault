---
type: meta
status: canon
updated: 2026-10-01
---

# Governance Runtime Map

Carte du système governance vault, ouverte avec la série PR-1..6 (« Vault
Documentaire → Vault Exécutable », 2026-05-10). Document vivant — mettre à jour à
chaque ajout de script governance ou modification de write/read path.

> **État vérifié le 2026-09-30** sur `_scripts/`, `.github/workflows/`, l'API de
> protection de branche, la crontab et `/etc/cron.d` de la machine DEV. De la
> série PR-1..6 : le générateur `sync_moc_decisions.py` (PR-3) est livré, mais son
> cron n'a jamais été installé ; `ci-vault-gate.sh` (PR-4) est livré en mode `pr`
> par la PR #360 (mise à jour du 2026-10-01). `enforce_admins` est actif sur `main`.

## Composants par couche

### Couche A — Canonical sources

- `_scripts/schemas/*.schema.json` : autorité de validation frontmatter
  (8 fichiers, 4 avec `status.enum` : adr, incident, moc, rule)
- `ledger/decisions/adr/ADR-*.md` : SoT décisions (frontmatter = state machine)
- `ledger/rules/rules-*.md` : SoT règles canon
- `.spec/00-canon/planning/*.yml` (dans ce vault) : SoT planning (ADR-053)

### Couche B — Runtime mirrors / projections

- `_scripts/governance_constants.py` : runtime mirror des schemas (PR-2,
  parity-tested)
- `ops/moc/MOC-Decisions.md` : projection des frontmatters ADR entre markers
  `<!-- AUTO-GENERATED:* -->`. Régénérée **à la main** par
  `sync_moc_decisions.py --write` dans la PR qui modifie un ADR (ex. #330, #353) :
  le cron prévu n'est pas installé. `--check` ignore la ligne « Dernier sync »
  (#356) et tourne sur chaque PR via `ci-vault-gate.sh pr` (#360) : une PR qui
  modifie un ADR sans régénérer l'index a un job rouge.
- `ops/moc/MOC-Planning-Live.md` + `ledger/snapshots/planning/` : projection
  planning (ADR-053), écrite par le cron planning — à l'arrêt, voir Couche D.
- `ops/moc/MOC-AuditTrail.md` : à projeter en follow-up (hors scope PR-1..6)

### Couche C — Validators & generators (scripts)

| Script | Rôle | Invoqué par |
|--------|------|-------------|
| `check-orphans.sh` | G2 (zéro orphelin) | hooks pre-commit + pre-push, check requis `G2: Zero Orphelin`, weekly-lint, `gov`, `preflight-write.sh`, `new-incident.sh` |
| `check-broken-links.sh` | wikilinks cassés | hooks pre-commit + pre-push, check requis `Broken Wikilinks`, weekly-lint, `preflight-write.sh`, `new-incident.sh` |
| `check-v1-paths.sh` | chemins v1 (ADR-015) | check requis `No V1 Paths (ADR-015)`, weekly-lint, `preflight-write.sh` |
| `check-signatures.sh` | G3 (signatures) | check requis `G3: Commits signes`, hook pre-push |
| `check-vault-pollution.sh` | sections opérationnelles (ADR-060 §1A inv. 5) | check **non requis** `No Operational Sections`, weekly-lint |
| `check-self-review-marker.sh` | marqueur `Self-review verdict` | check **non requis** `Self-Review Marker` |
| `check-frontmatter-schema.py`, `check-adr-supersedes.py`, `check-obsolete-rules.py`, `check-moc-integrity.py` | frontmatter, chaînes supersedes, rules obsolètes, invariants MOC | weekly-lint |
| `check-no-direct-schema-enum-access.sh` (→ `check_no_direct_schema_enum_access.py`), `test_governance_constants.py` | frontière schemas ↔ constants (PR-2 / PR-2b) | weekly-lint |
| `check-canon-backlinks.py`, `check-canon-freshness.py`, `check-canon-cross-repo.py` | cohérence vault ↔ monorepo | weekly-lint, seulement si le monorepo est présent : marqués `skipped` en GHA |
| `audit-signatures.sh` | rapport de signatures | manuel (cité dans l'en-tête de `weekly-lint.sh`, pas exécuté par lui) |
| `sync_moc_decisions.py` | générateur MOC-Decisions (PR-3) | manuel (`--write` dans les PR ADR) ; `--check` par `ci-vault-gate.sh pr` |
| `cron-sync-moc-decisions.sh`, `cron-sync-canon-mirrors.sh` (→ `sync_canon_mirrors.py`) | wrappers cron auto-PR | **aucun cron installé** |
| `compute-canon-hashes.py` | hashes des rules publiées | `canon-publish.yml`, `sync_canon_mirrors.py`, `test_canon_hashes.py` |
| `build-opa-bundles.sh` | bundles OPA | `opa-policy-build.yml` |
| `sync-canon.sh`, `evidence-pack.sh` | — | `gov` (manuel) |
| `preflight-write.sh`, `new-incident.sh` | — | manuel |
| `setup-branch-protection.sh` | protection de `main` versionnée ([[branch-protection]]) | manuel ; `--check` = comparaison en lecture seule avec la protection en vigueur |
| `planning/run-cron.sh` (→ `planning/sync_planning.py`) | writer planning (ADR-053) | `/etc/cron.d/planning-live` |
| `weekly-lint.sh` | **🔧 Governance Runtime Entrypoint** (agrégateur) | `vault-weekly-lint.yml` ; `ci-vault-gate.sh pr` (`--no-monorepo`) |
| `ci-vault-gate.sh` | gate de PR (PR-4) : weekly-lint sans les checks cross-repo + `sync_moc_decisions.py --check` ; mode `pr` seul (mode `weekly` et issue `infra-fail` non implémentés) | check `Vault Lint Gate (ADR-020)` |
| `test_*.py` (`_scripts/`, `_scripts/planning/tests/`) | tests des validateurs et générateurs | check `Vault Scripts Tests` (`pytest _scripts`) |

> **Reframing** : `weekly-lint.sh` n'est plus « juste du lint » : il agrège tous
> les checks et produit `findings.json` + `report.md`. Il tourne en entier chaque
> lundi (`vault-weekly-lint.yml`, non bloquant : issue quand de nouveaux findings
> apparaissent) et, sans les 3 checks cross-repo, sur chaque PR via
> `ci-vault-gate.sh pr` (rouge sur toute erreur). Les gates bloquants sont les
> checks requis de `vault-governance.yml` ([[branch-protection]]) ; le job du gate
> en fait partie une fois la protection mise à jour
> (`setup-branch-protection.sh --check` dit si c'est fait).

### Couche D — Automation (CI + cron)

GHA workflows (6 fichiers `.github/workflows/`) :

| Workflow | Déclenchement | Rôle |
|----------|---------------|------|
| `vault-governance.yml` | PR vers `main` ; push sur `main` et `refactor/**` | checks requis G2, Broken Wikilinks, G3, G4, No V1 Paths ; `Vault Scripts Tests` et `Vault Lint Gate (ADR-020)` (ajoutés par #360, requis une fois la protection mise à jour) ; `No Operational Sections` (non requis) |
| `vault-self-review-marker.yml` | PR vers `main` (opened, edited, synchronize, reopened) | `Self-Review Marker` (non requis) |
| `vault-weekly-lint.yml` | lundi 02:00 UTC + manuel | weekly-lint complet, diff avec le run précédent, issue (`governance`, `weekly-lint`) si nouveaux findings ; non bloquant |
| `vault-supabase-cost-check.yml` | lundi 08:00 UTC + manuel | dérive de la surface de coût DB (ADR-028, ADR-034) |
| `canon-publish.yml` | push `main` et PR touchant les rules publiées, `99-meta/canon-hashes.json` ou `compute-canon-hashes.py` ; manuel | contrôle des hashes ; sur push `main`, `repository_dispatch canon-updated` vers automecanik-wiki, automecanik-raw et nestjs-remix-monorepo |
| `opa-policy-build.yml` | PR et push `main` touchant `policies/**`, `dist/policies/**` ou `build-opa-bundles.sh` | tests + build des bundles OPA |

Cron machine DEV :

| Cron | Installé | Effet |
|------|----------|-------|
| `vault-sync.sh` (crontab `deploy`, toutes les 5 min, hors dépôt) | oui | HEAD sur une autre branche : met à jour la seule ref `main` (fast-forward), sans toucher HEAD ni l'arbre ; HEAD sur `main` et arbre propre : fast-forward |
| `_scripts/planning/run-cron.sh` (`/etc/cron.d/planning-live`) | oui, **à l'arrêt** | voir ci-dessous |
| `cron-sync-moc-decisions.sh` (prévu lundi 01:30 UTC) | non | — |
| `cron-sync-canon-mirrors.sh` | non | — |
| sync-canon dry-run, audit-signatures, check-orphans ([[cron-setup]]) | non | — |

Les deux wrappers auto-PR non installés commencent par
`git checkout main && git reset --hard origin/main` dans le checkout où ils
tournent : le checkout runtime du vault pour l'un, le checkout principal du
monorepo pour l'autre. Ne les installer que sur un clone dédié.

#### Writer planning (ADR-053) — à l'arrêt

- **Horaire** : `0 8 * * *` dans `/etc/cron.d/planning-live`, interprété dans le
  fuseau de la machine (Europe/Paris) : 06:00 UTC en été, 07:00 UTC en hiver. Le
  commentaire du fichier et ADR-053 disent « 08:00 UTC ».
- **Mécanique** : dans le checkout runtime partagé, `git reset --hard origin/main`
  sur la branche qui y est extraite, puis commit signé et `git push origin main`.
- **Rien sur `main` depuis le 2026-08-14** (dernier commit planning : `4c94c7d`).
  Du 2026-08-15 au 2026-09-14, les 31 exécutions ont commité sur la branche
  extraite à ce moment, pas sur `main` ; `git push origin main` répondait
  `Everything up-to-date` et le log écrivait `OK`. Chaque exécution a aussi
  ramené cette branche à `origin/main` : ses commits locaux non poussés ne
  restent accessibles que par le reflog.
- **Aucune exécution journalisée depuis le 2026-09-14.** Depuis le redémarrage du
  2026-09-17, le répertoire du verrou (`/var/lock/automecanik/`, sur tmpfs)
  n'existe plus : l'ouverture du verrou échoue et le script sort en 1 avant
  d'écrire son log ou son état. Le fichier cron n'a pas de `MAILTO` et aucun MTA
  n'est actif ; le dernier état enregistré reste `ok` (2026-09-14), sans
  `max_age_s`, donc le silence n'est pas détecté. Les 2026-09-15 et 09-16 ne
  sont pas vérifiables (journal système non lisible par `deploy`).
- **Ne pas « réparer » en recréant le répertoire du verrou** : le script
  reprendrait ses `reset --hard` sur le checkout partagé, et son push direct sur
  `main` est de toute façon refusé (`enforce_admins`). Le correctif (clone dédié
  + auto-PR, ou retrait) amende ADR-053 : décision owner.

Branch protection main : checks requis, `enforce_admins: true`, PR requise
(0 review), historique linéaire — liste et détail dans [[branch-protection]] ;
`_scripts/setup-branch-protection.sh --check` compare la protection en vigueur
à la configuration versionnée.

## Modèle 3 couches de protection

État de la protection effective du vault (vérifié le 2026-09-30 ; ligne L2 mise à jour le 2026-10-01 pour la PR #360) :

| Couche | Mécanisme | État vault | Couvert par |
|--------|-----------|------------------------|-------------|
| **L1 — Canonique (logique)** | ADRs / SoT / canonical routes / role canon / URL ownership / write-path | ✅ Actif | ADR-015, R-SEO-09, frontmatter schemas, série PR-1..3 |
| **L2 — CI (structurel)** | checks requis sur chaque PR, dont le gate `ci-vault-gate.sh pr` (weekly-lint sans cross-repo + `sync_moc_decisions.py --check`) et `pytest _scripts` + weekly-lint hebdomadaire complet (non bloquant) + parity test enums + AST no-direct-schema | 🟡 Partiel : gate livré par #360, bloquant une fois la protection mise à jour ; mode `weekly` et issue `infra-fail` non implémentés ; checks cross-repo seulement sur la machine DEV ; projection planning non vérifiée | `vault-governance.yml`, PR-2 / PR-2b, #360 |
| **L3 — GitHub branch (runtime)** | `enforce_admins=true` + check requis G3 + PR requise | ✅ Actif (constaté le 2026-09-30 ; `required_signatures` false, 0 review requise) | [[branch-protection]] |

Le push direct sur `main` est refusé à tous, admins compris. Ce qui reste ouvert
est en L2 : la projection planning n'est vérifiée par aucun check, les checks
cross-repo ne tournent que sur la machine DEV, et le gate de PR ne bloque le
merge qu'une fois ajouté aux checks requis.

## Write paths

| Path | Write authority | Method |
|------|-----------------|--------|
| `ledger/decisions/adr/ADR-*.md` | humains | PR signée G3 |
| `ledger/rules/rules-*.md` | humains | PR signée G3 |
| `ops/moc/MOC-Decisions.md` (contenu entre markers AUTO-GENERATED) | humains, via `sync_moc_decisions.py --write` | PR signée G3 (auto-PR cron prévue, non installée) |
| `ops/moc/MOC-Decisions.md` (colonne Notes) | humains | prévue, pas encore introduite |
| `ops/moc/MOC-Planning-Live.md`, `ledger/snapshots/planning/` | cron planning | push direct `main`, refusé depuis `enforce_admins` (writer à l'arrêt) |
| `_scripts/*.py` | humains | PR signée G3 |
| `_scripts/schemas/*.schema.json` | humains (rare, ADR requise) | PR signée G3 |
| `99-meta/cron-setup.md` | humains | PR signée G3 |
| GH Issues labels `governance` + `weekly-lint` | `vault-weekly-lint.yml` | `GITHUB_TOKEN` (`issues: write`), seulement si nouveaux findings |
| `repository_dispatch canon-updated` (3 dépôts consommateurs) | `canon-publish.yml` | token du workflow, sur push `main` |

## Read paths

| Read source | Read by |
|-------------|---------|
| `schemas/*.schema.json` (full schema) | `check-frontmatter-schema.py` (validation conformité) |
| `schemas/*.schema.json` (enum extraction) | `test_governance_constants.py` UNIQUEMENT (parity test) |
| `governance_constants.py` | tous les autres scripts (impérativement, pas de parse direct enum) |
| ADR frontmatters | `sync_moc_decisions.py`, `check-moc-integrity.py`, `check-adr-supersedes.py` |

## Forbidden patterns (governance-runtime-boundaries)

1. ❌ Aucun script ne parse `*.schema.json` pour **extraire des enums** (sauf
   `test_governance_constants.py`) — enforced par PR-2b walker AST. Validation
   complète du schema (`check-frontmatter-schema.py`) reste légitime.
2. ❌ `governance_constants.py` ne contient AUCUNE fonction calculée, AUCUN
   import hors `__future__` — enforced par TestPurity (PR-2)
3. ❌ Aucun cron / CI ne push direct main — toujours auto-PR signée G3.
   Exception de fait : le writer planning (ADR-053) est conçu pour pousser
   directement sur `main` ; la protection le refuse depuis `enforce_admins`
   (voir Couche D).
4. ❌ Aucune édition manuelle entre markers `<!-- AUTO-GENERATED:* -->` (sauf
   colonne Notes) — détectable par `sync_moc_decisions.py --check` (non branché
   en CI)
5. ❌ Aucun script governance ne fait orchestration cross-repo, runtime state
   mutation, ou decision-making (= entreraient dans le Governance Engine —
   out-of-scope vault)
6. 🔒 **AUCUN script, workflow, ou agent ne lit le contenu de la colonne Notes
   pour en dériver une décision.** Notes = humain-only, jamais machine-read.
   Enforced par review (rejet de toute PR introduisant `parse_notes_for_X()`).

## Trigger to revisit this map

- Ajout d'un nouveau script `_scripts/*` non listé Couche C → mettre à jour
  le tableau
- Ajout d'un nouveau write path → mettre à jour write paths
- Installation, retrait ou panne d'un cron (planning, sync-moc, canon-mirrors)
  → mettre à jour Couche D
- Ajout ou retrait d'un check requis, mode `weekly` ou issue `infra-fail` de
  `ci-vault-gate.sh` → revoir L2 dans le tableau 3-couches
- ADR canon-doc `governance-runtime-boundaries.md` créée → linker depuis ce map
