---
id: ADR-020
title: "Weekly Governance Vault Lint"
status: accepted
date: 2026-04-23
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1, G2, G3, G4]
related_incidents: []
reviewed_by: ""
---

# ADR-020: Weekly Governance Vault Lint

## Contexte

La CI actuelle du vault (`.github/workflows/vault-governance.yml`) s'exécute **on-push / on-PR** uniquement, avec 4 checks basiques (orphans, broken-links, signed-commits, v1-paths). Trois angles morts restent :

1. **Pas de lint périodique.** Une dérive introduite entre deux PRs (status `deprecated` laissé sans `superseded_by`, wikilink vers un fichier renommé par un refactor adjacent, schéma YAML modifié sans validation) reste invisible tant qu'aucun auteur ne retouche la zone concernée.
2. **Checks structurels manquants.** Le vault compte 19 ADRs + ~290 documents, avec 4 types de frontmatter distincts (adr / rule / moc / incident). Rien ne valide la conformité YAML (champs requis, types, enums) ni la cohérence des chaînes `supersedes` / `superseded_by`.
3. **Pas d'alerte cross-canon.** [[rules-vault|G1]] stipule que le canon technique vit dans `.spec/00-canon/` (monorepo) et que le vault ne peut pas contredire. Rien ne détecte actuellement si un nouveau fichier canon apparaît sans backlink depuis le vault (dérive G1 latente).

Un smoke-test local (2026-04-23) révèle déjà :
- 18 erreurs de frontmatter (ADR-002 et ADR-009 sans `date`, INC-2026-01-11 avec id non-standard, MOC-Knowledge sans frontmatter)
- 3 erreurs de chaînes supersedes (ADR-002, ADR-009, ADR-010 réfèrent des cibles non existantes)
- 30 fichiers `.spec/00-canon/*` jamais backlinkés depuis le vault

Ces findings existent silencieusement depuis des semaines sans jamais déclencher la CI on-push (aucun de ces fichiers n'a été touché par une PR récente).

## Décision

**Ajouter un workflow GitHub Actions hebdomadaire (`vault-weekly-lint.yml`) qui exécute les 4 checks existants + 4 nouveaux checks avancés, et remonte les findings via une issue GitHub tagguée `governance`, `weekly-lint`.**

Concrètement :

1. **Nouveau workflow** `.github/workflows/vault-weekly-lint.yml` — cron `0 2 * * 1` (lundi 02:00 UTC), runner `ubuntu-latest`, `permissions: contents: read + issues: write`.
2. **Orchestrateur** `_scripts/weekly-lint.sh` — chaîne les 8 checks (4 legacy bash + 4 modernes Python) et produit `findings.json` + `report.md`.
3. **4 nouveaux scripts Python** dans `_scripts/` :
   - `check-frontmatter-schema.py` — valide le frontmatter YAML par type contre un JSON schema (adr / rule / moc / incident)
   - `check-adr-supersedes.py` — détecte cycles, cibles manquantes, asymétries dans les chaînes `supersedes` / `superseded_by`
   - `check-obsolete-rules.py` — flague `status: deprecated|superseded` sans `superseded_by` ni wikilink de replacement
   - `check-canon-backlinks.py` — alerte si un fichier `.spec/00-canon/*` du monorepo n'est pas référencé depuis le vault
4. **4 JSON schemas** dans `_scripts/schemas/` — un par type de document (source de vérité pour la validation frontmatter).
5. **Output** — artifact GitHub (`weekly-lint-<run_id>`, rétention 90 j) + issue auto si findings présents. Aucune écriture dans le vault (respect G4).
6. **ADR-020 (ce document)** formalise la décision et entre dans [[MOC-Decisions]].

## Options Considérées

### Option A: NestJS `@Cron` côté monorepo

**Description**: Ajouter un cron NestJS (`@Cron('0 2 * * 1')`) dans le backend monorepo qui SSH vers le DEV VPS et exécute les scripts du vault.

**Avantages**:
- Centralisation avec les autres jobs récurrents (ex : `order-cleanup`, `vehicle-filtered-catalog-v4-hybrid`)
- Pas de secret GitHub Actions à gérer

**Inconvénients**:
- `ScheduleModule` NestJS actuellement désactivé sur le projet (conflit version `@nestjs/common v10`) — fragile
- Viole l'esprit de [[ADR-015-vault-single-source-of-truth|ADR-015]] : le vault devient dépendant d'un scheduler externe côté monorepo
- Logs dispersés (pas de trace GitHub natif)

### Option B: Cron système sur DEV VPS

**Description**: `crontab` système sur 46.224.118.55 qui exécute `_scripts/weekly-lint.sh` et push les résultats manuellement.

**Avantages**:
- Contrôle total, zéro dépendance GitHub
- Accès direct au monorepo `/opt/automecanik/app/` → check `canon-backlinks` complet

**Inconvénients**:
- Infrastructure cron manuelle à documenter et maintenir (régression typique si le VPS redémarre mal)
- Pas de trace GitHub native (logs locaux uniquement)
- Nécessite des credentials GitHub write pour ouvrir les issues (augmente la surface d'attaque)

### Option C: GitHub Action scheduled workflow

**Description**: Nouveau workflow GH Actions `vault-weekly-lint.yml` qui tourne sur `ubuntu-latest`, clone le vault, exécute les checks, upload artifact + ouvre issue si findings.

**Avantages**:
- Pattern déjà établi dans le vault (`vault-governance.yml` est un workflow GH Actions existant)
- Pattern déjà établi dans le monorepo (`prod-smoke-tests.yml` tourne en `schedule: cron` `0 */6 * * *`)
- Zéro infrastructure à maintenir (GitHub gère retry, notifications, logs, rétention)
- Audit trail natif (GitHub Actions run history + artifact 90 jours)
- `contents: read` permission only → respect strict G4 (CI read-only sur canon)
- Issue auto = notification Fafa + tracking
- Intégration native avec future review humaine (label `weekly-lint` filtrable)

**Inconvénients**:
- Pas d'accès direct à `/opt/automecanik/app/.spec/00-canon/` (monorepo privé séparé) — le check `canon-backlinks` reste skipped en CI. Exécution locale reste possible sur DEV VPS pour un audit ponctuel cross-canon.

## Justification

**Option C retenue** pour trois raisons :

1. **Cohérence avec l'existant** — le vault a déjà `vault-governance.yml`, le monorepo a déjà des workflows scheduled. Aucun nouveau concept ni infrastructure à introduire.
2. **Respect strict G3 + G4** — permissions `contents: read` uniquement, aucun commit auto, aucune modification du canon. Les findings remontent via issue (humain-éligible, signable, révertable).
3. **Zéro coût de maintenance** — GitHub gère intégralement le scheduling, la rétention, le retry, les logs. Pas de régression possible par redémarrage VPS ou upgrade NestJS.

La limite sur `canon-backlinks` (pas d'accès monorepo en CI) est acceptable : ce check peut être lancé manuellement sur DEV VPS via `_scripts/weekly-lint.sh --monorepo /opt/automecanik/app` pour un audit cross-canon complet, typiquement trimestriel.

## Conséquences

### Positives

- Détection précoce des dérives silencieuses entre PRs (status orphelin, chaîne supersedes cassée, frontmatter invalide, canon non backlinké)
- Issue GitHub taguée `governance,weekly-lint` = tracking naturel + label filtrable
- Artifact 90 jours = comparaison historique possible (évolution du nombre de findings)
- Aucune écriture auto dans le vault → G3 (signatures) et G4 (read-only) intacts
- Les 4 nouveaux scripts Python sont aussi utilisables en local (`_scripts/check-*.py .`) pour audit ponctuel humain

### Négatives

- Une issue est créée **à chaque run** où il y a des findings (même si inchangés depuis la semaine précédente). Mitigation future : ajouter un step de diff vs artifact précédent pour `new_findings` only (hors scope ADR-020, amélioration incrémentale)
- `check-canon-backlinks` reste skipped en CI (monorepo privé non clonable sans secret) → audit cross-canon manuel trimestriel
- Les 18 erreurs + 7 warnings déjà présents dans le vault deviendront **visibles immédiatement** à la première run. C'est volontaire (c'était le but) mais peut surprendre

### Neutres

- Les schemas JSON dans `_scripts/schemas/` sont tolérants sur les formats historiques (ex : `status: accepted-revised`, `status: deferred`) pour ne pas flaguer des ADRs légitimes anciens
- Les rules sans frontmatter (`rules-vault.md`, `rules-technical.md`, etc.) sont en `warning` plutôt qu'`error` (compatibilité historique)

## Critères de Succès

- [ ] **C1 — Workflow actif** : `vault-weekly-lint.yml` apparaît dans `gh workflow list --repo ak125/governance-vault` après merge
- [ ] **C2 — First run green** : le trigger manuel `gh workflow run vault-weekly-lint.yml` produit un artifact `weekly-lint-<run_id>` téléchargeable contenant `findings.json` + `report.md`
- [ ] **C3 — Issue auto** : la première run crée une issue taguée `governance,weekly-lint` listant les 18 errors + 7 warnings actuels du vault
- [ ] **C4 — Cron auto** : lundi 2026-04-27 02:00 UTC, le workflow se déclenche sans intervention humaine
- [ ] **C5 — Compatibilité G1-G4** : la CI `vault-governance.yml` (g2-orphans, broken-links, g3-signed-commits, v1-paths, g4-canon-write-block) reste verte après merge
- [ ] **C6 — Dépendances isolées** : `pip install pyyaml` dans le workflow n'introduit pas d'autre dépendance non documentée

## Implémentation

Fichiers créés par cette ADR (branche `feature/weekly-vault-lint`) :

- `_scripts/weekly-lint.sh` — orchestrateur bash
- `_scripts/check-frontmatter-schema.py` — validation YAML par type
- `_scripts/check-adr-supersedes.py` — chaînes supersedes
- `_scripts/check-obsolete-rules.py` — status deprecated sans replacement
- `_scripts/check-canon-backlinks.py` — drift G1 cross-canon
- `_scripts/schemas/adr.schema.json` — schema ADR
- `_scripts/schemas/rule.schema.json` — schema rule (optionnel)
- `_scripts/schemas/moc.schema.json` — schema MOC
- `_scripts/schemas/incident.schema.json` — schema incident
- `.github/workflows/vault-weekly-lint.yml` — workflow GH Actions scheduled
- `ops/moc/MOC-Decisions.md` — update : ajout ligne ADR-020

Actions de suivi :

- **Suivi #1** — Régler les 18 errors réelles détectées par la première run (ADR-002 et ADR-009 sans `date`, ADR-010 `supersedes` avec suffixe descriptif, MOC-Knowledge sans frontmatter) — **Owner** : Fafa — **Deadline** : 2026-05-15
- **Suivi #2** — Décider pour les 30 fichiers canon non-backlinkés (`ledger/knowledge/` ou `ops/moc/MOC-Knowledge` à enrichir) — **Owner** : Fafa — **Deadline** : 2026-05-31
- **Suivi #3** — Amélioration future : step diff vs artifact précédent pour ne remonter issue que sur NEW findings (hors scope ADR-020)

## Revue Planifiée

**Date**: 2026-07-23 (T+3 mois)

**Critères de revue**:
- Au moins 10 runs hebdo exécutées sans régression
- Au moins 1 dérive détectée et corrigée grâce au lint (preuve de valeur)
- Nombre d'issues ouvertes-puis-fermées avec le label `weekly-lint`
- Décider si activer un mode "new-findings-only" pour réduire le bruit sur findings persistants

---

*Proposé le: 2026-04-23*
*Accepté le: 2026-04-23*
*Dernière revue: 2026-04-23*
