# CLAUDE.md — Instructions pour les agents IA travaillant sur ce vault

Ce fichier guide les agents Claude (Code, Desktop, Cowork, Agent SDK) quand ils editent le governance vault.

---

## Regle Maitresse

> **Le vault decide, le monorepo execute** (G1, [[ADR-101-vault-decides-canon-authority|ADR-101]]). Les ADR `accepted` et les regles de `ledger/rules/` sont normatifs. Dans `.spec/00-canon/` du monorepo, seuls les contrats consommes par du code, un generateur ou un check CI font foi, dans leur domaine ; le reste est de la prose de reference sans autorite. Une divergence entre une decision et le code est un constat a signaler, jamais a trancher en silence.
>
> Le mot `canon` est polysemique. Pour les acceptions distinctes (canon architectural / document canonique / canonical path / registry / source), voir le glossaire dans [[MOC-Governance]] section "Glossaire `canon`". L'autorite de chaque acception reste dans son document canonique (regle G1, ADR-015, etc.) — jamais dupliquee ici.

Avant toute modification:

1. Identifier si le changement est operationnel (documentation, runbook, MOC) ou une decision (ADR obligatoire, G1)
2. Lire les MOCs concernees (`ops/moc/MOC-*.md`) pour comprendre le contexte
3. Respecter la taxonomie T/G/AI/V (voir README)

---

## Regles Vault (a respecter imperativement)

### G1: Le Vault Decide

NE JAMAIS prendre ou modifier une decision sans ADR (voir `_templates/adr-template.md`).
Un document `status: canon` se modifie par PR signee ; si le changement modifie une
decision, il passe par un ADR. Une divergence constatee entre une regle et le code se
signale et se resout par une PR de code ou un ADR d'amendement.

### G2: Zero Orphelin

Chaque nouveau document CREE DOIT etre lie:

- Soit depuis un MOC existant (`ops/moc/MOC-*.md`)
- Soit depuis un INDEX-* local (`ledger/agents/*/INDEX-agents-*.md`, `ledger/compliance/.../INDEX-EP-*.md`, ...)

Avant de committer, executer:

```bash
_scripts/check-orphans.sh .
```

Si FAIL, lier ou archiver dans `ledger/_archive/` (G8).

### G3: Commits Signes

Ne jamais proposer un commit non signe a l'utilisateur. Si la config signing manque, guider l'utilisateur vers `99-meta/signing-policy.md`.

### G4: CI Read-Only

NE JAMAIS modifier depuis un workflow GitHub Actions. Le kill-switch `AI_VAULT_WRITE=false` doit rester respecte. Toute tentative de write depuis CI est une violation critique.

---

## Conventions de Nommage

### Wikilinks

- Prefere les wikilinks courts: `[[ADR-001-environment-separation]]`, `[[rules-technical]]`
- Pour les fichiers a nom identique (ex: `01-context.md` dans 4 evidence-packs): utilise un **stem unique** (`INDEX-EP-xxx.md`) plutot qu'un wikilink path-based
- Dans les **tableaux markdown**, evite `[[path|alias]]` — le `|` doit etre escape en `\|` ce qui casse le parsing Obsidian. Utilise une liste a la place, ou renomme le fichier cible pour avoir un stem unique

### Frontmatter YAML

Tout document canonique doit avoir:

```yaml
---
type: adr | rule | plan | checklist | retrospective | audit-report | evidence-pack | moc | index | policy | spec | knowledge | template
status: <valeur du schema de son type>
updated: YYYY-MM-DD
---
```

Les valeurs autorisees de `status` sont celles des schemas `_scripts/schemas/<type>.schema.json`
(adr, rule, moc, incident), en minuscules : ils font foi. Ne pas recopier leurs enums ici.

Pour les ADR specifiquement (champs requis par `adr.schema.json` : id, title, status, date, decision_makers):

```yaml
---
id: ADR-XXX
title: "..."
status: proposed   # enum : _scripts/schemas/adr.schema.json
date: YYYY-MM-DD
decision_makers: [...]
supersedes: []
superseded_by: []
related_rules: [...]
---
```

### Nouvelles ADR

Utiliser `_templates/adr-template.md`. Numero = dernier ADR + 1 (voir `MOC-Decisions`).

### Nouveaux Incidents

Utiliser `_templates/incident-template.md`. Lier depuis `MOC-Incidents`.

### Nouvelles Regles

Utiliser `_templates/rule-template.md`. L'ajouter au fichier de regles approprie (T/G/AI/V) et l'indexer dans `MOC-Rules`.

---

## Workflow Typique

Quand l'utilisateur demande une modification:

1. **Lire les MOCs pertinents** pour comprendre le contexte (pas juste le fichier cible)
2. **Verifier** si le changement modifie une decision (auquel cas : ADR, G1)
3. **Appliquer** le changement + lier depuis un MOC/INDEX si creation
4. **Executer** `_scripts/preflight-write.sh` avant d'ecrire (obligatoire, voir `AGENTS.md`), puis
   `_scripts/check-orphans.sh .` et `_scripts/check-broken-links.sh .` avant de committer
5. **Proposer** un commit message clair + rappeler qu'il doit etre signe (G3)

---

## Ce qu'il ne faut PAS faire

- Creer un fichier sans le lier (G2 violation)
- Modifier une regle `status: canon` sans ADR
- Utiliser le format legacy `DEC-00X` (reclasse en Phase 4 vers ADR-014 + plan/audit-trail)
- Utiliser les anciens chemins `../05-agents/...`, `../02-decisions/...` (structure v1, remplacee par `ledger/`)
- Committer sans signature
- Creer des fichiers `INDEX.md` supplementaires (utiliser `INDEX-<scope>.md` pour stems uniques)

---

## Scripts Utiles

| Script | Role |
|--------|------|
| `_scripts/check-orphans.sh` | G2 enforcement (exit 1 si orphelins) |
| `_scripts/check-broken-links.sh` | Detection wikilinks casses (exit 1 si casses) |
| `_scripts/preflight-write.sh` | Preflight obligatoire avant ecriture (clone a jour, arbre propre, pas de chemin v1) |
| `_scripts/audit-signatures.sh` | Audit retro des signatures git |
| `_scripts/evidence-pack.sh` | Generateur Airlock, encore sur chemins v1 : ne pas utiliser (voir `AGENTS.md`) |

---

## Contact

- Owner: Fafa (automecanik.seo@gmail.com)
- Monorepo (execute): https://github.com/ak125/nestjs-remix-monorepo
- Ce vault: https://github.com/ak125/governance-vault

---

_Dernière mise a jour: 2026-09-30_
