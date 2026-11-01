---
id: ADR-118
title: "Retrait des méthodes BMAD, Superpowers et Spec Kit : agents BMAD désactivés, amende ADR-008, ADR-009 et ADR-011"
status: accepted
date: "2026-10-27"
decision_date: "2026-10-26"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-008", "ADR-009", "ADR-011"]
extends: []
related_adr: ["ADR-013", "ADR-101", "ADR-102"]
related_rules: ["G5"]
related_incidents: []
version: "1.0.0"
---

# ADR-118 : Retrait des méthodes BMAD, Superpowers et Spec Kit

- **Statut** : Accepted (2026-10-27). La fusion par l'owner vaut ratification.
- **Amende** [[ADR-008-agent-placement-rules|ADR-008]], [[ADR-009-agents-phase1-activation|ADR-009]]
  et [[ADR-011-openclaw-claude-api-replacement|ADR-011]], sur les seuls passages listés en D3.
  Le reste de ces ADR reste en vigueur et leur corps n'est pas modifié.
- **Modifie** la règle G5 de [[rules-governance-process]] (v3.1.0) et le registre
  [[REG-001-agents]] (v2.4.0).
- **Méthode** : chaque constat ci-dessous a été vérifié le 2026-10-27 sur `main` du vault
  (`684e734`) et sur `main` du monorepo (`ab7a505f2`).

## Contexte

Le 2026-10-26, l'owner a demandé le retrait des méthodes de travail génériques BMAD,
Superpowers et Spec Kit. Elles ajoutent aux agents des rituels et des gabarits qui gonflent
leur contexte et doublent les instructions propres au dépôt.

Côté monorepo, la PR ak125/nestjs-remix-monorepo#1900 (squash `f406f2bee`, fusionnée le
2026-10-26) a :

- supprimé les artefacts BMAD `_bmad-output/` ;
- retiré le kit de maintenance Spec Kit de `.spec/` ;
- renommé `docs/superpowers/specs` et `docs/superpowers/plans` en `docs/specs` et `docs/plans`,
  en mettant à jour les références ;
- retiré des plans les directives d'exécution `superpowers:*`, et des réglages Claude Code les
  entrées de plugins qui n'étaient plus installés.

Le vault, lui, déclare encore BMAD actif :

| Passage | État au 2026-10-27 |
|---|---|
| ADR-008, tableau « Règles de Placement par Type d'Agent » | Catégorie « BMAD Agents » placée en zone External |
| ADR-009 §2.2 « Zones autorisees par type d'agent » | « BMAD Agents » au statut ACTIF |
| ADR-011 §3.1 « REG-001 — Agent Registry » | Fiche « dev (BMAD) » à mettre à jour |
| [[REG-001-agents]] | 10 agents du domaine `bmad` au statut `active` |
| `ledger/agents/bmad/` | 10 fiches `status: active` |
| G5 de [[rules-governance-process]] (v3.0.0) | `_bmad-output/*` listé comme source ; checklist « Avant tout workflow BMAD » |
| [[MOC-Agents]] | Zone `local` illustrée par « BMAD » |

Superpowers et Spec Kit n'ont pas de texte normatif dans le vault. Leurs mentions sont des
chemins de fichiers ou des récits datés (D5).

[[ADR-101-vault-decides-canon-authority|ADR-101]] D3 traite une divergence entre une décision
et l'état du dépôt par une PR de code ou par un ADR d'amendement. Le code a déjà changé ; cet
ADR aligne le vault.

## Décision

### D1 — Les méthodes sont retirées

BMAD, Superpowers et Spec Kit ne sont plus des méthodes de travail du projet. Après cet ADR,
le vault ne contient plus de texte normatif qui les prescrit. Leur réintroduction demande un
nouvel ADR.

### D2 — Les 10 agents BMAD passent `disabled`

- Dans [[REG-001-agents]], les agents `bmad-master`, `analyst`, `architect`, `dev`, `pm`,
  `quick-flow-solo-dev`, `sm`, `tea`, `tech-writer` et `ux-designer` passent de `active` à
  `disabled`.
- Leurs fiches de `ledger/agents/bmad/` sont conservées comme historique, avec
  `status: disabled`. Le précédent est celui des fiches backend `AGENT-cache-processor` et
  `AGENT-email-processor`.
- Les verdicts de l'audit d'origine (`APPROVED`, `APPROVED_WITH_CONDITIONS`) ne sont pas
  réécrits. Ils datent cet audit ; avec le statut `disabled`, ils n'autorisent plus d'exécution.
- Ce retrait est une modification du catalogue : niveau G1 de
  [[ADR-013-agent-lifecycle-governance|ADR-013]] (PR, revue humaine, fusion), que cette PR
  remplit. Une réactivation suivrait le niveau G2 d'ADR-013, tel qu'amendé par
  [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]], et demanderait un ADR qui
  révoque D1.

### D3 — Passages amendés

| ADR | Passage | Lecture après ADR-118 |
|---|---|---|
| ADR-008 | Tableau « Règles de Placement par Type d'Agent », ligne « BMAD Agents » | Sans objet : la catégorie n'a plus d'agent actif. |
| ADR-009 | §2.2 « Zones autorisees par type d'agent », ligne « BMAD Agents » | Statut « RETIRÉ (ADR-118) » au lieu de « ACTIF ». |
| ADR-011 | §3.1 « REG-001 — Agent Registry », ligne « dev (BMAD) » | Plus de mise à jour à faire : la fiche est `disabled`. |

Comme pour ADR-102, seul le frontmatter de ces trois ADR change : `amended_by` reçoit
`ADR-118`. Leur corps reste tel qu'il a été accepté.

### D4 — Règle G5

Dans [[rules-governance-process]] :

- la ligne `_bmad-output/*` du tableau des sources est retirée : le dossier n'existe plus sur
  `main` du monorepo depuis #1900 ;
- la checklist « Avant tout workflow BMAD » devient « Avant tout deliverable », en écho à
  « Apres chaque deliverable » qui la suit ; ses items ne changent pas ;
- la version passe de 3.0.0 à 3.1.0.

### D5 — Références historiques conservées

Les mentions restantes sont des chemins ou des récits datés. Elles ne sont pas réécrites :

- ADR-035, ADR-076, ADR-080 et le runbook `soft-404-telemetry` citent des chemins
  `docs/superpowers/specs/...` ou `docs/superpowers/plans/...`. Sur `main` du monorepo, les
  mêmes fichiers se trouvent sous `docs/specs/` et `docs/plans/`, et l'ancien chemin reste
  lisible dans l'historique git ;
- ADR-025 raconte une étape de travail menée en 2026 avec un skill Superpowers ;
- les documents de `ledger/knowledge/` et `ledger/audit-trail/` qui citent ces méthodes sont
  datés et non normatifs au sens de G5.

## Options considérées

- **A — Amender (retenue).** Le canon rejoint l'état du monorepo, l'historique d'audit reste
  lisible et le diff reste limité aux passages normatifs.
- **B — Supprimer les fiches et réécrire les ADR.** Efface l'historique de l'audit des agents
  et réécrit des ADR acceptés, à l'inverse de la pratique d'ADR-102 (frontmatter seul).
- **C — Ne rien faire.** ADR-009 continuerait de déclarer BMAD actif et la divergence resterait
  ouverte, contrairement à ADR-101 D3.

## Ce que cet ADR NE fait PAS

- Il ne réécrit pas le corps d'ADR-008, ADR-009 et ADR-011.
- Il ne supprime ni les fiches BMAD ni les verdicts d'audit.
- Il ne réécrit pas les références historiques listées en D5.
- Il ne règle pas l'installation de plugins dans les outils des postes de travail : elle relève
  du titulaire de chaque outil, hors du vault.
- Il ne prescrit pas de méthode de remplacement.

## Conséquences

### Positives

- Un agent qui lit le vault ne trouve plus d'instruction BMAD active.
- Le registre et les fiches décrivent l'état réel du projet.

### Négatives

- La colonne « Total » de la couverture par domaine de REG-001 compte désormais des agents
  `disabled` : une note l'explique sous le tableau.
- Une règle normative change de libellé (G5 v3.1.0).

### Neutres

- `total_agents: 144` et les compteurs par verdict de REG-001 ne changent pas.

## Critères de succès

- `git grep -n -E '^status: active' -- ledger/agents/bmad/` ne renvoie rien.
- Dans `ledger/agents/registry/REG-001-agents.md`, aucune ligne du domaine `bmad` ne porte le
  statut `active`.
- `git grep -n -E '_bmad-output|workflow BMAD' -- ledger/rules/` ne renvoie rien.
- `_scripts/check-adr-supersedes.py` ne signale pas d'asymétrie entre `amends` et
  `amended_by`, et `_scripts/ci-vault-gate.sh pr` est vert.

## Mise en œuvre (cette PR)

| Fichier | Changement |
|---|---|
| `ledger/decisions/adr/ADR-118-retrait-methodes-bmad-superpowers-spec-kit.md` | Cet ADR |
| ADR-008, ADR-009, ADR-011 | `amended_by: ["ADR-102", "ADR-118"]` (frontmatter seul) |
| `ledger/agents/registry/REG-001-agents.md` | 10 agents `disabled`, couverture BMAD, note, ADR liés, v2.4.0 |
| `ledger/agents/bmad/AGENT-*.md` (10 fiches) | `status: disabled`, renvoi à cet ADR |
| `ledger/agents/bmad/INDEX-agents-bmad.md` | Bannière de retrait |
| `ledger/rules/rules-governance-process.md` | D4, v3.1.0 |
| `ops/moc/MOC-Agents.md` | Catégorie BMAD marquée retirée, exemple de zone `local` corrigé |
| `ops/moc/MOC-Decisions.md` | Index régénéré par `_scripts/sync_moc_decisions.py --write` |

## Références

- [[ADR-101-vault-decides-canon-authority|ADR-101]] D3 : traitement d'une divergence.
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] : précédent d'amendement par le
  seul frontmatter.
- [[ADR-013-agent-lifecycle-governance|ADR-013]] : niveaux G1 et G2 du cycle de vie des agents.
- PR ak125/nestjs-remix-monorepo#1900 : retrait côté monorepo.
