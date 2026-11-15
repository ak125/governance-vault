---
id: ADR-133
title: "Niveau B de la fusion automatique : identité de revue distincte (GitHub App en lecture et revue seules), approbation sur la tête exacte, classe « faible risque » d'ADR-128 D5"
status: proposed
date: "2026-11-15"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-124"]
extends: ["ADR-128"]
related_adr: ["ADR-102", "ADR-120", "ADR-121", "ADR-123", "ADR-124", "ADR-128", "ADR-130", "ADR-131"]
related_rules: ["DoD2", "G1", "G3", "G4"]
related_incidents: []
reviewed_by: ""
version: "0.1.0"
---

# ADR-133 : niveau B de la fusion automatique et identité de revue distincte

- **Statut** : Proposed (2026-11-15). Rédigé par un agent (Claude Code CLI, machine DEV, session
  `d12e0713-ad11-4209-bc5c-0ff6ac13dc7c`) sur mandat de l'owner (« Mandat X »). Aucune ratification
  sans instruction explicite de l'owner ([[rules-vault|G1]] ;
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D7).
- **Amende** [[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]] sur D1 (le niveau B
  peut s'ouvrir), D3 (une revue déclarée de niveau B n'exclut plus une PR de la classe, quand le
  niveau B est actif) et D5 (cas de refus du niveau B ajoutés). Le reste d'ADR-124 est inchangé.
- **Prolonge** [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] D5 : la classe
  candidate « faible risque » est reprise telle qu'écrite et son prérequis bloquant (l'identité de
  revue) reçoit une réponse. ADR-128 n'est pas modifié.
- **Précise** [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]] D5 : l'approbation de l'identité
  de revue est une condition de fusion vérifiable par la porte ; elle ne remplace ni l'enregistrement
  DoD2, ni la revue indépendante qu'il consigne (D4 ci-dessous).
- **N'active rien.** Le bloc `level_b` de la politique est écrit à l'état `inactive`. Aucune identité,
  clé, application, secret, variable ou réglage GitHub n'est créé par cet ADR ni par la session qui
  l'a rédigé. L'activation est un acte séparé de l'owner (D8).

## Contexte

[[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]] a ouvert un premier périmètre de
fusion automatique sur le monorepo : niveau DoD2 A, documentation Markdown seule. Il a laissé le
niveau B fermé : « la porte ne saurait pas prouver la revue indépendante qu'il exige. L'ouvrir suppose
une revue attestée par une identité distincte de l'auteur, puis une modification de la politique par
PR du vault. » [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] D5 a ensuite défini
une classe « faible risque » pour ce niveau et noté son prérequis bloquant : l'identité de revue
distincte n'existe pas, et `automecanik-agents[bot]` ne peut pas approuver ses propres PR.

### État relevé par l'agent le 2026-11-15 entre 12:55 et 13:05 UTC (lecture seule)

- **Politique** `ledger/policies/merge-perimeter.v1.json` sur `main` du vault : `status: active`,
  `schema_version: 1`, `authorized_review_levels: ["A"]`, inchangée depuis le commit
  `dc821d5872001b5b6bcf89c6c0127ddcc2cbe950` (PR #394, 2026-11-09).
- **Fusions faites par la porte depuis le 2026-11-09** : aucune. Sur 90 PR du monorepo fusionnées
  entre 2026-11-09T06:38:12Z et 2026-11-15T12:50:01Z, 87 ont `merged_by` = `app/automecanik-agents`
  et 3 `ak125` (#2071, #1997, #1973). Aucune ne porte le commentaire « Fusion automatique (ADR-124) »
  que la porte pose avant de fusionner (`scripts/ci/merge-perimeter-gate.mjs`, fonction `merge`).
  Les 87 fusions sous le compte de l'application relèvent donc d'un autre chemin que la porte ; ce
  relevé n'établit pas leur décideur (voir Constats hors périmètre).
- **Pause** : `/home/deploy/resync/merge-perimeter.pause` est **absent** ; le verrou
  `merge-perimeter.lock` aussi.

## Décision

### D1 — Identité de revue : une seconde GitHub App, `automecanik-reviewer`

Le niveau B repose sur une identité native de GitHub, distincte de l'auteur et reconnue par GitHub
comme un approbateur : une **seconde GitHub App**, nommée `automecanik-reviewer` (son compte bot est
`automecanik-reviewer[bot]`). Aucun mécanisme maison : l'approbation est une revue GitHub
(`POST /repos/{repo}/pulls/{n}/reviews`, `event: APPROVE`, `commit_id` = tête), lue par la porte
existante (`GET /repos/{repo}/pulls/{n}/reviews`).

- **Permissions minimales** (dépôt) : Metadata en lecture (obligatoire), Pull requests en lecture et
  écriture (pour déposer une revue), Contents en lecture, Checks en lecture, Commit statuses en
  lecture. Aucune autre : ni Contents en écriture, ni Workflows, ni Administration, ni Actions, ni
  Secrets. Webhook désactivé. Installable sur ce compte seulement.
- **Installation** : le seul dépôt `ak125/nestjs-remix-monorepo`. Jamais le vault, qui reste hors de
  toute fusion automatique ([[rules-vault|G4]]).
- **Qui la crée** : l'owner, depuis les réglages développeur de son compte. Un agent ne crée ni
  l'application, ni sa clé.
- **Où vit la clé** : sur la machine DEV, selon le modèle du kit d'identité existant
  (`/home/deploy/automecanik-identite-github-20261025/`, helper `automecanik-gh-app-token`), avec des
  éléments distincts de ceux de `automecanik-agents` : un compte système dédié (proposé :
  `automecanik-ghreview`), un dossier `/etc/automecanik/github-reviewer-app/` lisible par ce seul
  compte, un helper `/usr/local/libexec/automecanik-gh-reviewer-token` et une règle sudoers qui
  n'autorise que ce helper. Pas de minuterie et pas d'écriture dans `~/.config/gh/hosts.yml` : le
  jeton d'installation (valable une heure) est émis à la demande pour l'appel de revue, passé en
  `GH_TOKEN` à cette seule commande, et restreint à la demande au dépôt et aux permissions ci-dessus.

**Pourquoi pas `automecanik-agents[bot]`** : c'est l'auteur des PR des agents. GitHub refuse
l'approbation de sa propre PR, et une approbation par l'auteur ne prouverait aucune indépendance.

**Pourquoi pas le compte de l'owner** : son approbation est une revue humaine par PR, ce que le niveau
B automatise justement (ADR-120 D3) ; un agent n'agit pas sous le compte de l'owner pour produire une
trace de décision (ADR-121 D4 et ADR-120 D5) ; l'owner ne peut pas approuver les PR qu'il ouvre
lui-même.

### D2 — Revue : une session distincte, sur une tête figée, consignée dans l'approbation

L'approbation est déposée par une **session de revue distincte de la session auteur** :

1. **Qui** : une session lancée hors de la conversation de l'auteur, qui ne reçoit ni son contexte ni
   ses conclusions, et n'écrit pas sur la branche (ADR-120, « Revue indépendante »). Elle est de
   préférence d'une **autre famille de modèle** que l'auteur (par exemple Codex CLI pour une PR écrite
   par Claude). Ce choix reprend le principe de contestation par une autre famille proposé par
   ADR-131 (PR #413 du vault, `proposed`) pour le WIKI, sans le présupposer accepté ni l'étendre :
   ADR-133 ne dépend pas de son adoption. La famille et le modèle sont déclarés dans le corps de
   l'approbation.
2. **Sur quelles preuves** : la tête (SHA de 40 caractères) est figée avant la revue. La session lit
   le diff `base...tête` dans un arbre extrait à cette tête, hors du worktree de l'auteur ; vérifie que
   les contrôles requis sont verts sur cette tête (`gh pr checks`) ; vérifie chaque fichier contre la
   liste fermée de D3 ; lit chaque test modifié pour y chercher un test neutralisé sans motif interdit
   que la porte ne détecte pas (assertion retirée ou affaiblie, sortie anticipée sous condition, test
   déclaré par un alias ; Limites).
3. **Trace** : le corps de l'approbation donne la tête, la base, la procédure, le modèle et sa
   famille, l'identifiant de session, les constats et leur issue. L'enregistrement DoD2 du corps de
   la PR (`- [x] Revue niveau B — tête …, base …` puis `procédure : revue indépendante, par …`) reste
   exigé par la porte, comme au niveau A.
4. **Dépôt** : `gh api repos/ak125/nestjs-remix-monorepo/pulls/<N>/reviews -f commit_id=<tête>
   -f event=APPROVE -f body=<trace>`, sous `GH_TOKEN` émis par le helper de D1. Un constat bloquant
   donne `event=REQUEST_CHANGES` sur la même tête, que la porte lit comme un retrait (D5).

### D3 — Ouverture du niveau B : la classe « faible risque » d'ADR-128 D5, telle qu'écrite

Le niveau B est ouvert pour la seule classe d'ADR-128 D5, reprise sans élargissement :

- **Condition** : CI requise verte sur la tête **et** revue de niveau B, c'est-à-dire une approbation
  sur ce SHA par une identité distincte de l'auteur, vérifiable par la porte.
- **Liste fermée de chemins** :
  1. Markdown hors chemins refusés de la politique (déjà couvert au niveau A par ADR-124) ;
  2. `audit/**/*.md` (rapports d'audit) ;
  3. `backend/tests/unit/**` et `frontend/tests/unit/**`, en ajout ou modification de tests
     seulement (aucun fichier source, aucune suppression de test ; motifs refusés `\.skip\(` et
     `\.only\(`).
- **Exclus dans tous les cas** : les `deny_paths` de la politique, `.github/**`,
  `.spec/00-canon/**`, les projections générées, `packages/seo-role-contracts/**`, toutes les zones
  STOP, et tout le dépôt du vault.

Toutes les autres conditions d'ADR-124 restent appliquées au niveau B : classification de
`ownership.yaml` lue à la base, `deny_diff_patterns`, assignee humain, tête à jour, contrôles requis,
une seule fusion à la fois, même porte, même compte exécutant, même fichier de pause. Le niveau C
reste toujours refusé.

### D4 — Articulation avec ADR-120 D5

ADR-120 D5 interdit de satisfaire DoD2 par une nouvelle identité ou une approbation. Ce n'est pas le
cas ici : DoD2 est satisfait par l'enregistrement de revue indépendante sur la tête (ADR-120 D2), que
la porte continue d'exiger. L'approbation de `automecanik-reviewer[bot]` est une **condition de
fusion supplémentaire**, liée par GitHub au SHA (`commit_id`) et vérifiable par la porte ; elle prouve
que la revue consignée a été déposée par une identité distincte de l'auteur sur cette tête. Sans
enregistrement, l'approbation ne suffit pas ; sans approbation, l'enregistrement ne suffit pas.

### D5 — Cas de refus

Les cas d'ADR-124 D5 (repris d'ADR-123 D4) restent tous applicables. S'y ajoutent ceux du niveau B ;
le code est celui qu'écrit la porte.

| Cas | Code de la porte | Effet |
|---|---|---|
| Revue déclarée de niveau B, bloc `level_b` absent ou `inactive` | `LEVEL_B_NOT_ACTIVE` | pas de fusion |
| Revue de niveau C sur la tête | `REVIEW_LEVEL_REFUSED` | pas de fusion |
| Enregistrement de niveau B sans procédure « revue indépendante, par … » | `REVIEW_NOT_INDEPENDENT` | pas de fusion |
| Aucune approbation | `APPROVAL_MISSING` | pas de fusion |
| Approbation de l'identité listée sur une autre tête | `APPROVAL_OTHER_HEAD` | pas de fusion ; nouvelle revue sur la nouvelle tête |
| Auteur de la PR listé, ou approbation par l'auteur | `APPROVAL_BY_AUTHOR` | pas de fusion |
| Approbation par une identité non listée (owner compris) | `APPROVAL_UNLISTED_IDENTITY` | pas de fusion |
| Dernière revue décisive de l'identité listée : changements demandés ou revue rejetée | `APPROVAL_WITHDRAWN` | pas de fusion |
| Chemin exclu dans tous les cas | `LEVEL_B_DENY_PATH` | pas de fusion |
| Chemin hors liste fermée | `LEVEL_B_PATH_REFUSED` | pas de fusion |
| Fichier non test sous `tests/unit/` | `LEVEL_B_NOT_TEST_FILE` | pas de fusion |
| Chemin de test qui nomme une zone STOP | `LEVEL_B_STOP_ZONE` | pas de fusion |
| Fichier de test supprimé, renommé ou copié ; déclaration de test retirée, mise en commentaire, placée sous condition ou dans un nouvel appel englobant ; test de la base vidé, sans appel ou ouvert par un `return` sans appel ; nom `it`, `test` ou `describe` redéfini ; fichier de test non analysable | `TEST_REMOVED` | pas de fusion |
| `.skip(` ou `.only(` ajouté, ou modificateur `skip`, `only`, `todo`, `skipIf`, `runIf` ajouté sous toute écriture | `LEVEL_B_DIFF_PATTERN` | pas de fusion |
| Patch d'un test absent (binaire, trop gros), ou fichier illisible à la base de fusion ou à la tête | `PATCH_UNAVAILABLE` | pas de fusion |

Les déclarations de test sont lues par l'analyseur TypeScript (dépendance `typescript` déjà présente
à la racine du monorepo) sur le fichier entier, à la base de fusion et à la tête, tous deux lus par
l'API contents de GitHub. Commentaires et chaînes, même sur plusieurs lignes, ne peuvent donc ni cacher
ni simuler un test. Chaque appel dont la chaîne d'appel nomme `it`, `test` ou `describe` (`it(`,
`suite.test(`, `test.each(t)(` compris) présent à la base se retrouve à la tête avec le même appel et
le même premier argument et la même position syntaxique, modificateurs mis à part. La position va
du fichier à l'appel : chaque appel de test englobant y figure par son appel et son titre, chaque autre
nœud par sa nature. Un titre changé, un test placé sous un `if`, un `&&`, un `?:` ou une boucle, ou
dans un nouvel appel englobant (`describe`, `registry.test`, `describe.each([])`) compte comme un
retrait, et un test retiré ne se compense pas par un autre ajouté. Un test de la base est refusé si,
à la tête, il n'a plus de rappel littéral, si son rappel ne contient aucun appel (`() => undefined`,
`() => void 0`, corps vide) ou s'il s'ouvre par un `return` sans appel (`return;`,
`return undefined;`). Un nom `it`, `test` ou `describe` lié ou réassigné à la tête (déclaration,
paramètre, import hors de `vitest`, `@jest/globals` et `node:test`, affectation directe ou sur un objet
global) est refusé : un `describe` redéfini en fonction vide ferait disparaître ses tests sans changer
leur clé.

### D6 — Politique

`ledger/policies/merge-perimeter.v1.json` reçoit un bloc `level_b` à l'état `inactive` :
`review_identities` (`automecanik-reviewer[bot]`), `allowed_paths`, `test_paths`, `test_file_globs`,
`allowed_test_file_statuses`, `deny_paths`, `stop_zone_fragments`, `deny_added_line_patterns` et la
description de l'évaluation. `authorized_review_levels` reste `["A"]` : le niveau B ne s'ouvre que par
`level_b`, et la porte refuse toute autre valeur dans ce champ. Le `status` général reste celui
d'ADR-124 (`active`) : seul `level_b.status` gouverne le niveau B. Si GitHub attribue à l'application
un autre identifiant que `automecanik-reviewer[bot]`, la valeur est corrigée dans le commit
d'activation (D8).

### D7 — Porte

La porte existante `scripts/ci/merge-perimeter-gate.mjs` du monorepo est étendue, sans nouveau
mécanisme (PR [#2079](https://github.com/ak125/nestjs-remix-monorepo/pull/2079)). Quand
l'enregistrement de la tête est de niveau B et que `level_b` est `active`, elle applique la classe de
D3 à chaque chemin, ancien et nouveau, puis lit les revues GitHub de la PR et exige l'approbation de
D5. Pour chaque fichier de test, elle lit le fichier à la base de fusion et à la tête par l'API
contents (`readTestContents`), avec le compte qui l'exécute ; une lecture en échec vaut refus. Chaque
cas de refus de D5 a un test dans `scripts/ci/merge-perimeter-gate.test.mjs`, exécuté par le contrôle
`audit.yml`. Le niveau A est inchangé.

### D8 — Activation séparée (ADR-124 D8)

L'adoption de cet ADR n'active pas le niveau B. L'activation passe `level_b.status` à `active` par un
commit signé sur une PR du vault fusionnée par l'owner ; ce commit cite la **recette** : chaque cas de
D5 démontré par un refus réel de la porte en `--dry-run`, avec une copie locale `active` de la
politique, sur des PR de recette réelles approuvées ou non par l'identité créée. Un cas que GitHub
rend impossible à construire (par exemple un patch absent) est démontré par son test unitaire, et la
recette le dit. La pause (`merge-perimeter.pause`) et l'arrêt (`level_b.status: inactive` ou revert)
d'ADR-124 D8 s'appliquent au niveau B.

### Composants, outil natif et responsable

| Composant | Outil natif | Responsable |
|---|---|---|
| Identité de revue | GitHub App `automecanik-reviewer` | owner : création, installation, clé |
| Clé privée | fichier `.pem` sous `/etc/automecanik/github-reviewer-app/`, compte système dédié | owner : pose sur la machine DEV |
| Jeton | jeton d'installation GitHub App émis par un helper sous sudoers | owner : pose du helper ; session de revue : usage |
| Revue | session distincte, de préférence d'une autre famille de modèle (Codex CLI) | session de revue lancée hors de la session auteur |
| Approbation | revue GitHub `APPROVE` épinglée par `commit_id` | session de revue, sous l'identité de revue |
| Contrôles requis | protection de branche et contrôles GitHub de la tête | owner (réglages) ; GitHub (exécution) |
| Vérification | `scripts/ci/merge-perimeter-gate.mjs` (API reviews) | monorepo ; fusion de la PR par l'owner |
| Politique | `merge-perimeter.v1.json`, bloc `level_b` | vault ; PR fusionnée par l'owner |
| Activation, pause, arrêt | commit signé (D8) ; fichier `merge-perimeter.pause` | owner |
| Fusion | `gh pr merge --squash --match-head-commit` par la porte | compte exécutant d'ADR-124 |

## Étapes de l'owner (écrites, non exécutées)

1. **Créer l'identité** : réglages du compte, « Developer settings », « GitHub Apps », « New GitHub
   App » ; nom `automecanik-reviewer` ; webhook décoché ; permissions de D1, toutes les autres à
   « No access » ; « Only on this account ». Générer une clé privée.
2. **L'installer** sur `ak125/nestjs-remix-monorepo` seulement (« Only select repositories »).
   Preuve par l'API, avec le compte de l'owner :
   `gh api user/installations --jq '.installations[] | select(.app_slug=="automecanik-reviewer") | {id, repository_selection, permissions}'`
   puis `gh api user/installations/<id>/repositories --jq '.repositories[].full_name'` (un seul dépôt
   attendu) et `gh api 'users/automecanik-reviewer%5Bbot%5D' --jq '.login'`.
3. **Poser la clé** sur la machine DEV selon D1 (compte système dédié, dossier lisible par lui seul,
   helper, règle sudoers limitée au helper), sur le modèle du kit
   `/home/deploy/automecanik-identite-github-20261025/`.
4. **Ratifier** cet ADR par instruction explicite en session (ADR-121 D7), puis fusionner la PR du
   vault et la PR #2079 du monorepo, chacune sur sa tête :
   `gh pr merge <N> --squash --match-head-commit <sha40>`.
5. **Recette** (D8) : PR de recette ouvertes par les agents, titrées « NE PAS FUSIONNER — recette
   ADR-133 », assignées à l'owner, puis fermées. Pour chaque cas de D5,
   `node scripts/ci/merge-perimeter-gate.mjs <N> --dry-run --policy-file <copie locale active>`
   doit écrire le refus attendu. Exemples de construction : aucune approbation (`APPROVAL_MISSING`) ;
   approbation puis nouveau commit (`APPROVAL_OTHER_HEAD`) ; approbation par l'owner
   (`APPROVAL_UNLISTED_IDENTITY`) ; approbation puis `REQUEST_CHANGES` (`APPROVAL_WITHDRAWN`) ; PR
   ouverte sous l'identité de revue depuis une branche existante (`APPROVAL_BY_AUTHOR`) ; fichiers
   hors classe, test retiré, `.skip(` ajouté, chemin de test nommant une zone STOP.
6. **Activer** : commit signé sur une PR du vault qui passe `level_b.status` à `active` (et corrige
   l'identifiant si besoin), cite la recette, et est fusionné par l'owner.

## Options considérées

- **Retenue : seconde GitHub App en revue seule.** Identité native, distincte, sans droit d'écriture
  sur le code, approbation liée au SHA par GitHub, lisible par la porte.
- **Compte machine GitHub (utilisateur dédié)** : identité distincte, mais un siège et un jeton
  personnel à longue durée, des droits plus larges que nécessaire et un compte de plus à protéger.
  Écartée.
- **Approbation par l'owner** : retour à la revue humaine par PR que le niveau B vise à éviter.
  Écartée (D1).
- **Statut de commit ou check run posé par la session de revue** : natif, mais exigerait une
  permission d'écriture de statut et un nom de contexte que la porte devrait croire sur parole ; une
  revue GitHub porte nativement son auteur et son `commit_id`. Écartée.
- **Revue exécutée dans un workflow GitHub Actions** : demanderait une clé de modèle et la clé de
  l'application en secrets du dépôt, et un workflow écrit par l'owner (ADR-130 D3.4). Possible plus
  tard pour renforcer l'indépendance (Limites) ; hors de ce mandat.

## Conséquences

### Positives

- Les PR de tests unitaires et de rapports d'audit des agents peuvent être fusionnées sans acte de
  l'owner par PR, avec une revue indépendante prouvée sur la tête exacte.
- La preuve de la revue n'est plus déclarative : la porte la lit dans GitHub.

### Négatives

- Une identité et une clé de plus à garder et à faire tourner.
- La classe est plus stricte que sa lettre sur trois points : un test dont le titre change est
  refusé, un tableau `.each` modifié aussi, et un audit en sous-dossier classé D15 reste refusé
  (Limites).

### Neutres

- Le niveau A, le vault et les zones STOP sont inchangés.

## Limites

- **Séparation procédurale sur la machine DEV.** Tout processus du compte `deploy` peut appeler le
  helper de revue : la séparation entre session auteur et session de revue tient à la procédure et à
  sa trace, pas à Unix. Un renforcement (compte Unix distinct qui lance seul les sessions de revue,
  ou revue dans un workflow écrit par l'owner) relève d'un mandat distinct.
- **La porte vérifie la forme, pas la qualité.** Elle prouve qui a approuvé et sur quel SHA, pas que
  la revue a bien lu le diff. La qualité tient à D2.
- **Déclarations de test reconnues par leur nom d'appel.** L'analyse est syntaxique : un test
  déclaré par un alias (`const t = test; t("…")`) n'est pas reconnu comme tel, et son retrait échappe
  à `TEST_REMOVED` ; la session de revue le cherche (D2.2). À l'inverse, tout appel nommé `test`
  (`re.test(s)` compris) est compté : son retrait est refusé, le doute valant refus.
- **Tests affaiblis dans leur corps.** La porte refuse un test placé sous condition ou enveloppé,
  sans appel ou ouvert par un `return` sans appel, pas une assertion retirée ou affaiblie, ni une
  sortie anticipée après une première instruction (`if (x) return;`), ni un rappel dont les appels ne
  s'exécutent pas (`() => { const f = () => check(); }`). La session de revue doit les chercher (D2.2).
- **Déplacer un test dans un `describe` est refusé.** La position inclut les appels englobants : un
  regroupement de tests existants sous un nouveau `describe`, ou le renommage d'un `describe`, compte
  comme un retrait. Ce faux refus est voulu ; la PR passe par la revue humaine.
- **Tableau `.each` modifié.** Le premier argument d'un appel non littéral (tableau de `test.each`)
  est comparé tel quel : ajouter une ligne au tableau compte comme un retrait et est refusé.
- **Zones STOP par fragments de nom.** `stop_zone_fragments` reconnaît une zone STOP au nom du
  chemin d'un test ; c'est une heuristique, le doute valant refus. Le contenu reste filtré par
  `deny_diff_patterns`.
- **`audit/**/*.md` en sous-dossier.** La classification d'`ownership.yaml` (lue au niveau A et B)
  classe plusieurs sous-dossiers d'`audit/` en D15 (gouvernance), refusé : ces rapports restent
  fusionnés par l'owner tant que la classification ou la politique ne changent pas.
- **Pull requests en écriture.** Cette permission permet aussi à l'identité de revue de modifier ou
  fermer une PR et d'en ouvrir une depuis une branche existante ; la porte refuse alors l'approbation
  par l'auteur. Elle ne permet ni de pousser du code ni de fusionner (Contents en lecture).

## Constats hors périmètre (signalés, non corrigés)

- 87 PR du monorepo fusionnées depuis le 2026-11-09 sous le compte `app/automecanik-agents`, hors
  de la porte (aucun commentaire « Fusion automatique »). Leur décideur et leur chemin de fusion
  (`merge-pr.sh`, train de fusion) ne sont pas établis par ce relevé ; à rapprocher d'ADR-121 D4.
- La permission « Workflows » de `automecanik-agents` (ADR-130 D3.4) : son retrait est un acte de
  l'owner, non vérifié ici.
- `classification_exempt_paths` exempte `backend/tests/**` et `frontend/tests/**` de la
  classification ; au niveau A ces fichiers sont refusés par la règle « Markdown seul », au niveau B
  par la liste fermée de D3.

## Retour arrière

`level_b.status: inactive`, ou retrait du bloc `level_b`, par une PR du vault fusionnée par l'owner ;
pause immédiate par `merge-perimeter.pause`. Désinstallation de l'application par l'owner. Une fusion
déjà faite se corrige par une PR de revert.

## Revue planifiée

Après la recette et l'activation, puis après les dix premières fusions de niveau B : vérifier dans
GitHub l'auteur et le `commit_id` de chaque approbation, et le commentaire de la porte.

## Références

- [[ADR-120-dod2-preuve-de-revue-liee-au-sha]] (niveaux, revue indépendante, D5)
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts]] (D4, D7)
- [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte]] (D4, D7)
- [[ADR-124-premier-perimetre-fusion-automatique-monorepo]] (D1, D3, D5, D8)
- [[ADR-128-departements-autonomes-coordonnes-file-github]] (D5)
- [[ADR-130-amendement-adr-128-runner-prod-pilote-deterministe-securite-runners]] (D3.4)
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] (CI en lecture seule sur le vault)
- ADR-131 (PR #413 du vault, `proposed`) : principe de contestation par une autre famille, cité sans
  le présupposer accepté.
- Politique : `ledger/policies/merge-perimeter.v1.json` ; porte : PR monorepo
  [#2079](https://github.com/ak125/nestjs-remix-monorepo/pull/2079).

---

_Proposé le 2026-11-15. Accepté le : —_
