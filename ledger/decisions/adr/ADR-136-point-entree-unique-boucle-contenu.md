---
id: ADR-136
title: "Circuit du contenu : un point d'entrée unique par demande (issue de la file ADR-128 exécutée par mandat-remise), étapes déterministes versionnées, qualification ADR-131 dans la boucle"
status: proposed
date: "2026-11-15"
decision_date: ""
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-128"]
related_adr: ["ADR-031", "ADR-034", "ADR-046", "ADR-083", "ADR-102", "ADR-114", "ADR-119", "ADR-121", "ADR-128", "ADR-130"]
related_rules: ["AI1", "AP-12", "G1", "G4"]
related_incidents: []
reviewed_by: ""
version: "0.1.0"
---

# ADR-136 : un point d'entrée unique pour la boucle contenu

- **Statut** : Proposed (2026-11-15). Rédigé par un agent (Claude Code CLI, machine DEV) sur le
  mandat AD de l'owner (« Circuit du contenu : carte unique, preuves d'usage et retrait de
  l'obsolète », départements 09 et 06, 02 pour la carte et l'orchestration). La ratification
  (`accepted`) et la fusion sont réservées à l'owner
  ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]],
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]]).
- **Étend** [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] (D1, D3, D4) pour un
  seul circuit, celui du contenu, sans en réécrire le texte ni la séquence de bascule
  ([[ADR-130-amendement-adr-128-runner-prod-pilote-deterministe-securite-runners|ADR-130]] D2).
- **N'active rien.** Aucun workflow, label, runner, timer, condition de promotion ni écriture en
  base n'est créé, modifié ou activé par cet ADR (§ « Ce que cet ADR ne fait pas »).

## Contexte

L'owner, le 2026-11-15 : « La confusion et que tout existe mais éparpillés et n'est pas coordonnées
et orchestre ». La carte du circuit établie le même jour (monorepo,
`audit/seo-content-circuit-2026-11-15.md` et section « Carte du circuit » du skill
`seo-content-loop`, PR monorepo #2084) donne une pièce canon par étape. Elle montre aussi
qu'aucune pièce ne fait démarrer la boucle :

| # | Étape | Pièce canon | Déclencheur constaté le 2026-11-15 |
|---|---|---|---|
| 1 | Besoin | file d'issues (ADR-128 D1), `pilote-file.yml` | cron horaire, mode déterministe (ADR-130 D2) |
| 2 | Capture RAW | `auto-capture-runner.py` | session humaine ou timer `knowledge-jobs` (collecte) |
| 3 | Contrôle RAW | `gates.py` I/J, `regen-manifests.py` | CI du dépôt RAW |
| 4 | Proposition WIKI | skill `wiki-proposal-writer` | session Claude ouverte à la main |
| 5 | Contrôle WIKI | `validate-frontmatter.py`, `quality-gates.py`, `_scripts/gates/` | CI WIKI et `knowledge-jobs` |
| 6 | Qualification du 11 | aucune pièce câblée (ADR-131 proposé, PR vault #413) | — |
| 7 | Promotion | `promotion_decision.py` (décideur unique, [[ADR-114-wiki-safety-auto-gate|ADR-114]] D2) via `promote.py --apply` | timer `knowledge-jobs`, 08:00 Europe/Paris |
| 8 | Export | `build_exports_seo.py` | workflow `wiki-exports-seo-generate.yml` |
| 9–10 | Projection, consommation | `backend/src/modules/seo-projection/` | drapeaux OFF : projeté ≠ servi |
| 11 | Chatbot | `sync-rag-from-wiki.sh` | consommateur RAG ([[ADR-046-r-stack-single-generator-and-layers|ADR-046]]) |
| 12 | Mesure | `v5-guardian`, `seo-gamme-audit`, `content-audit` | sessions à la main |

Faits relevés le 2026-11-15 (lecture seule) :

- Le timer `knowledge-jobs` (unités `knowledge-jobs.timer` et `.service` de l'utilisateur
  `deploy`, code sous `~/.local/lib/knowledge-jobs/`) n'est **versionné dans aucun dépôt**. Il
  enchaîne collecte, validation, tests du décideur et `promote.py --apply`. Run du 2026-11-15 07:00Z
  (`wiki-apply.stdout.json`) : 13 fiches évaluées, 0 promue.
- `pilote-file.yml` est sur `main` du monorepo (#2071). Son étape de session (`claude -p`) est
  présente mais suspendue : run du 2026-11-15 15:06Z, « session suspendue : producteur du KPI
  useful_capabilities_not_complexity absent ». Il tourne donc en mode déterministe (ADR-130 D2).
- La routine `mandat-remise` (ADR-128 D4, étape 2) est proposée dans la PR monorepo #2082
  (ouverte, non fusionnée).
- La PR monorepo #1718 (brouillon) rejoue chaque jour la décision de promotion en dry-run
  ([[ADR-083-tiered-wiki-promotion|ADR-083]]).
- La routine `editorial-sur-wiki` (ADR-128 D3, `repository_dispatch` du dépôt WIKI) n'existe pas.
- ADR-131 (proposé) ajoute une condition `technical_qualification_pass` lue par le décideur
  (D3) et une boucle de corroboration bornée (D9, D10) ; rien n'est câblé.

## Décision (proposée)

### D1 — Une demande de contenu entre par une issue, et seulement par elle

- Toute exécution de la boucle (capture → proposition → qualification) part d'une issue de la file
  ADR-128 D1, label de département `dept:09-wiki` (la boucle produit une fiche WIKI ; le
  demandeur, 06 ou 07, est cité dans le corps). Le corps donne la gamme ou le sujet, le rôle de
  page visé, le run `RUN_TARGETED_RAW_TO_WIKI <gamme>` du skill `seo-content-loop` et la
  profondeur ADR-131 D4 attendue.
- L'issue est exécutée par `mandat-remise` (ADR-128 D4) après le label `mandat-prêt` posé par
  l'owner. La session tourne dans un worktree isolé et rend sa preuve AEC dans l'issue.
- Une session ouverte à la main reste possible pour un mandat de l'owner ; elle cite alors son
  issue (`Refs #N`). Aucune autre entrée (cron, `repository_dispatch`, script) ne démarre une
  demande.

### D2 — Les étapes déterministes restent planifiées, mais versionnées

- Validation, décision de promotion et `promote.py --apply` restent un balayage quotidien
  déterministe : il ne démarre aucune demande, il applique le décideur unique à ce qui est prêt.
- Condition préalable à toute activation de D1 pour le circuit : le code du timer
  `knowledge-jobs` est versionné dans un dépôt, avec ses tests, par une PR. Les fichiers de
  connexion (`ssh_config`, `known_hosts`) restent hors dépôt. Le dépôt cible est un choix de
  l'owner (Inconnues).
- `PROMOTE_GATE_ENGINE` et les drapeaux de projection restent régis par leurs ADR ; cet ADR n'en
  change aucun.

### D3 — La qualification ADR-131 se place dans la session sous mandat

- Dans une session D1, après la proposition (étape 4), la qualification et la contestation
  (ADR-131 D1, D2) produisent leurs artefacts sous `_audit/technical-qualification/` dans la PR
  WIKI du mandat.
- Le décideur du balayage D2 lit `technical_qualification_pass` comme toute autre condition
  (ADR-131 D3), une fois cette condition câblée par la PR WIKI que prévoit ADR-131. Avant ce
  câblage, l'artefact est produit et non lu : la session le dit dans sa preuve AEC.

### D4 — La boucle de corroboration est bornée par le mandat

- Les reprises d'ADR-131 D10 (questions de reprise, `RUN_TARGETED_RAW_TO_WIKI`) s'exécutent dans
  la même session, jusqu'à la cible ou au maximum de reprises fixés par ADR-131.
- À l'arrêt sans cible atteinte, la session livre le lot `à revoir` et ouvre une issue fille,
  sans `mandat-prêt`, qui porte les questions restantes. Une nouvelle reprise exige un nouveau
  label de l'owner. Aucune reprise ne se relance seule.

### D5 — Rôle du pilote

`pilote-file` signale, dans son issue de pilotage, les demandes de contenu bloquées, expirées ou
livrées `à revoir` (ADR-128 D6). Il ne lance aucune exécution de la boucle.

## Options considérées

### Option A : la routine `pilote-file` comme point d'entrée

**Description** : le pilote horaire repère les besoins (issues, constats) et lance lui-même la
boucle.

- Avantages : déjà sur `main` ; une seule routine à surveiller.
- Inconvénients : contraire à ADR-130 D2 (pilote déterministe, aucune session avant le producteur
  du KPI du rôle 23) ; un pilote qui exécute cumule juger et faire ; il lancerait des sessions sans
  acte de l'owner, ce qu'ADR-128 D4 réserve au label `mandat-prêt`.
- **Retenue pour l'observation seule (D5), rejetée comme entrée.**

### Option B : un workflow `repository_dispatch` ou un cron dédié à la boucle

**Description** : un workflow (fusion WIKI → `editorial-sur-wiki`, ou cron quotidien sur le modèle
de #1718) déclenche la boucle.

- Avantages : natif GitHub ; aucune session à la main.
- Inconvénients : la fusion WIKI est l'aval de la boucle, pas son entrée ; un cron n'a pas de
  demande à exécuter et produirait du contenu sans besoin nommé (filler, CLAUDE.md invariant 5) ;
  une deuxième entrée parallèle à la file ADR-128 recrée l'éparpillement constaté ; une
  orchestration maison de plus heurte [[rules-ai-antipatterns#AP-12|AP-12]].
- **Rejetée comme entrée.** `editorial-sur-wiki` reste une routine aval d'ADR-128 D3 ; #1718 reste
  une mesure en dry-run.

### Option C : sessions sous mandat, issue par issue (`mandat-remise`) — retenue

**Description** : D1. La demande est une issue ; l'owner l'approuve ; `mandat-remise` l'exécute.

- Avantages : une seule file pour tout le projet (ADR-128 D1) ; acte humain avant chaque
  exécution ; preuve AEC dans l'issue ; isolement en worktree ; borne naturelle de la boucle de
  corroboration (D4) ; aucun composant nouveau.
- Inconvénients : dépend de l'étape 2 d'ADR-128 (#2082 non fusionnée) ; débit borné par les
  approbations de l'owner ; d'ici là, les sessions restent ouvertes à la main.

### Option D : le timer `knowledge-jobs`, versionné, comme point d'entrée

**Description** : étendre le timer quotidien pour qu'il lance aussi capture et proposition.

- Avantages : il tourne déjà chaque jour et porte la promotion.
- Inconvénients : non versionné à ce jour ; une étape de jugement (proposition, qualification)
  dans un timer sans demande ni acte de l'owner ; aucune trace dans la file ; mélange l'exécution
  déterministe et celle d'un modèle.
- **Retenue pour les seules étapes déterministes (D2), après versionnement ; rejetée comme
  entrée.**

## Justification

La boucle a déjà ses pièces ; ce qui manque est une entrée unique et visible. La file ADR-128 est
déjà ratifiée comme lieu unique des mandats ; y placer la boucle n'ajoute aucun composant. Séparer
l'entrée (issue + mandat) du balayage déterministe (timer versionné) garde un seul décideur
(ADR-114 D2) et ne donne au modèle aucune autorité de promotion. La boucle de corroboration
d'ADR-131 a besoin d'une borne : le mandat la fournit.

## Conséquences

### Positives

- Une demande de contenu = une issue, avec son état et sa preuve.
- Un lancement implicite (cron, session sans issue) n'est plus une entrée admise pour produire
  du contenu.
- Le code qui promeut chaque jour devient relisible et testé en CI.

### Négatives

- Tant que #2082 n'est pas fusionnée et l'étape 2 d'ADR-128 sortie, D1 s'applique par sessions
  ouvertes à la main citant leur issue.
- Versionner `knowledge-jobs` demande une PR et une installation par l'owner.

### Neutres

- Les routines aval d'ADR-128 D3 (`seo-sur-fusion`, `editorial-sur-wiki`) ne changent pas.

## Ce que cet ADR ne fait pas

- Il ne crée ni n'active aucun workflow, label, runner, timer ou condition ; il ne fusionne aucune
  PR et ne modifie pas `pilote-file.yml`.
- Il ne câble pas `technical_qualification_pass` et ne fixe ni cible ni maximum de reprises
  (ADR-131).
- Il n'écrit rien en base, ne touche ni la PROD, ni une page, ni une fiche WIKI.
- Il ne change ni `PROMOTE_GATE_ENGINE`, ni les drapeaux de projection, ni ADR-083.

## Inconnues

- Dépôt cible du code `knowledge-jobs` (WIKI, RAW ou monorepo) : choix de l'owner.
- Le label `dept:09-wiki` existe (relevé du 2026-11-15) ; un label propre à la demande de
  contenu n'est pas proposé ici : le gabarit d'issue (Mise en œuvre, 3) suffit, sauf avis de l'owner.
- Sort final d'ADR-131 : si elle est rejetée, D3 et D4 tombent sans affecter D1, D2 et D5.

## Critères de succès

- [ ] C1 — Code `knowledge-jobs` versionné, tests verts en CI, timer réinstallé depuis le dépôt.
- [ ] C2 — Trois demandes de contenu menées de l'issue à la PR WIKI avec preuve AEC dans l'issue.
- [ ] C3 — Aucune fiche promue pendant 30 jours sans issue d'origine retrouvable.

## Mise en œuvre (après ratification, chacune par PR et acte de l'owner)

1. PR de versionnement de `knowledge-jobs` (D2).
2. Sortie de l'étape 2 d'ADR-128 (`mandat-remise`, #2082).
3. Gabarit d'issue « demande de contenu » dans le monorepo (D1).
4. Après câblage d'ADR-131 D3 : vérification que le balayage lit la condition (D3).

## Revue planifiée

**Date** : 2027-02-15.
**Critères de revue** : C1 à C3 ; sort d'ADR-131.

---

*Proposé le : 2026-11-15*
