---
id: ADR-130
title: "Amendement d'ADR-128 : constats corrigés (runner hetzner-prod sur l'hôte PROD), pilote-file déterministe avant toute session agent, sécurité des runners auto-hébergés d'un dépôt public"
status: proposed
date: "2026-11-15"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-128"]
extends: []
related_adr: ["ADR-012", "ADR-034", "ADR-121", "ADR-124", "ADR-128", "ADR-129"]
related_rules: ["AI1", "AI2", "AI9", "G1", "G4"]
related_incidents: []
reviewed_by: ""
version: "0.1.0"
---

# ADR-130 : amendement d'ADR-128 (runner PROD, pilote déterministe, sécurité des runners)

- **Statut** : Proposed (2026-11-15). Rédigé par un agent (Claude Code CLI, machine DEV) sur mandat de
  l'owner (« Mandat O »). La ratification est un acte de l'owner, décideur humain : Marwane
  ([[rules-vault|G1]] ; [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7).
- **Amende** [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] sur trois points et
  rien d'autre : le tableau des constats (D1), l'activation du pilote à l'étape 1 (D2), les règles de
  sécurité des runners auto-hébergés (D3). Le reste d'ADR-128 est inchangé. Le commit de ratification
  posera `amended_by: ["ADR-130"]` sur ADR-128 ; la PR de proposition ne touche pas ADR-128.
- **N'active rien et ne règle rien.** Aucun runner, workflow, label, secret, variable ni réglage
  GitHub n'est créé ou modifié par cet ADR. La PROD et le runner `hetzner-prod` ne sont pas touchés.

## Contexte

ADR-128 est accepté (PR #411, fusionnée le 2026-11-14 à 23:07:36 UTC ; `main` du vault à
`54faaa265a408d772357f838b201346f3b4463ce`). Trois écarts sont apparus depuis.

1. **Le runner existe.** Le rapport du mandat N (PR #2071 du monorepo, tête
   `7dd88ec37b3d1dff66d928e6293be25603e73770`) établit que le runner qui sert les cinq workflows
   `[self-hosted, Linux, X64]` est `hetzner-prod`, installé sur l'hôte PROD. Le constat d'ADR-128
   (« ils attendent un runner absent ») est faux.
2. **D2 et D8 se contredisent.** D2 bloque la routine agent d'un rôle sans producteur de KPI ; D8
   active `pilote-file` (rôle 23, producteur absent) dès l'étape 1.
3. **La garde de `ci.yml` n'est pas une barrière.** `ci.yml` se déclenche sur `pull_request` (et sur
   `push` vers `main` et `dev`) ; ses trois jobs auto-hébergés (`deploy` « Deploy PREPROD »,
   `e2e-smoke`, `lighthouse`) sont gardés par
   `github.ref == 'refs/heads/main' && github.event_name == 'push'`. Sur un événement de PR ou de
   push de branche, GitHub exécute la version du workflow présente dans la branche : une PR peut
   retirer la garde du workflow qu'elle exécute.

### Faits vérifiés par l'owner le 2026-11-15 vers 08:10 UTC

Depuis le PC, compte `ak125`, lecture seule (fournis dans le mandat ; l'agent ne peut pas les
vérifier, son jeton reçoit HTTP 403 sur l'API des runners) :

- politique d'approbation des PR de fork : `all_external_contributors` ;
- runner `hetzner-prod` enregistré sur le dépôt `ak125/nestjs-remix-monorepo`, `online`, labels
  `self-hosted`, `Linux`, `X64`, `production` ;
- `ak125` est un compte utilisateur : pas d'organisation, donc pas de groupe de runners.

### Faits relevés par l'agent le 2026-11-15 (lecture seule, `origin/main` du monorepo)

| Workflow | Déclencheurs | Jobs auto-hébergés |
|---|---|---|
| `ci.yml` (« 🚀 Deploy ») | `push` (`main`, `dev`), `pull_request` | `deploy` (PREPROD), `e2e-smoke`, `lighthouse`, gardés `main` + `push` |
| `deploy-monitoring-scripts.yml` | `push` `main` (filtre `scripts/monitoring/*.sh`), `workflow_dispatch` | 1 |
| `prod-smoke-tests.yml` | `schedule` `0 */6 * * *`, `workflow_dispatch` | 2 |
| `release-prod.yml` | `push` de tag `v*`, `workflow_dispatch` | 1 |
| `visual-gate.yml` | `workflow_dispatch` | 1 |

La PR #2071 a avancé depuis le rapport : sa tête est `5a1e6d9472519fadc52cb44c4e8bd258d92854b7`
(commit de plan, 2026-11-14 23:56 UTC). Elle est hors périmètre ; cet ADR cite le rapport à
`7dd88ec`.

## Décision

### D1 — Constats d'ADR-128 corrigés

Le tableau « Constats relevés le 2026-11-14 » d'ADR-128 se lit avec les corrections suivantes. Les
lignes non citées restent valables.

| Constat d'ADR-128 | Correction | Preuve |
|---|---|---|
| « Aucun runner auto-hébergé ne tourne sur le DEV » | **Inchangé** pour le DEV. Un runner auto-hébergé existe, sur l'hôte PROD : `hetzner-prod` | rapport du mandat N (#2071 à `7dd88ec`) ; vérification de l'owner du 2026-11-15 |
| « L'API des runners est fermée au jeton agent » | **Inchangé** pour le jeton agent. L'enregistrement est vérifié par l'owner avec son compte : `online`, labels `self-hosted`, `Linux`, `X64`, `production` | vérification de l'owner du 2026-11-15 |
| « 5 workflows ciblent `[self-hosted, Linux, X64]` … ils attendent un runner absent » | **Corrigé** : ils sont servis par `hetzner-prod`, donc exécutés sur l'hôte PROD | idem |
| « 254 exécutions en file … cause non établie » | **Précisé** : les exécutions en file du 2026-11-11 coïncident en partie avec deux incidents GitHub (Webhooks 20:22–20:26 UTC, Actions 20:48–21:21 UTC). La cause reste non établie pour le reste ; le critère de sortie de l'étape 1 « cause établie ou traitée à part » demeure | rapport du mandat N |

Dans « Inconnues » d'ADR-128, la ligne « Enregistrement réel du runner : non vérifiable par le jeton
agent » est levée pour `hetzner-prod` ; elle reste vraie pour le futur runner agents tant qu'il
n'est pas vu par l'owner (critère de l'étape 1, inchangé).

**Ce que cela change pour la séparation DEV/PROD d'[[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]] D1.**
ADR-129 D1 garde deux machines et la contrainte d'ADR-012 : « PROD n'est atteinte que par
`git push`, GitHub Actions et Docker ». Le runner sur PROD respecte la lettre de cette contrainte,
mais en déplace la garantie.

1. **Le canal « GitHub Actions » vers PROD est un runner installé sur l'hôte PROD.** Tout job qui
   cible `[self-hosted, Linux, X64]` s'exécute sur cet hôte, avec les droits du compte système du
   runner. Ces droits (compte, accès Docker, secrets lisibles sur l'hôte) ne sont pas vérifiés par
   cet ADR.
2. **La PREPROD et ses tests tournent sur l'hôte PROD.** Le job `deploy` de `ci.yml` (« Deploy
   PREPROD »), puis `e2e-smoke` et `lighthouse`, s'exécutent sur `hetzner-prod` à chaque push sur
   `main`. La PREPROD n'est pas une machine distincte de PROD.
3. **La séparation repose sur le droit d'écriture au monorepo, pas sur la revue.** Un événement de
   PR ou de push de branche exécute la version du workflow présente dans la branche. Toute identité
   qui peut pousser une branche contenant un workflow modifié peut donc faire exécuter du code sur
   l'hôte PROD sans passer par la revue ni par la fusion sur `main`. D3 fixe les règles qui ferment
   ce chemin.
4. **Le runner « DEV auto-hébergé » d'ADR-128 D3 n'est pas `hetzner-prod`.** Dans le tableau D3
   d'ADR-128, « DEV auto-hébergé » se lit « runner agents du DEV (label `agents` seul, D3.5) » ; dans
   « Charge sur le DEV », « distinct de celui de la CI » se lit « distinct de `hetzner-prod`, runner
   de la CI et des déploiements, installé sur l'hôte PROD ». Aucune routine d'ADR-128 ne cible
   `hetzner-prod`.

### D2 — Tension D2/D8 levée : `pilote-file` déterministe d'abord

1. **Étape 1.** `pilote-file` s'active comme **routine déterministe** : `gh issue list`,
   `gh pr list`, filtres `jq`, publication des constats selon ADR-128 D6 (mandats sans département,
   `statut:bloqué`, sans mouvement, expirés, PR sans issue). Aucune session Claude n'est ouverte.
   Comme les routines déterministes de 02 et 21 (ADR-128 D2), elle n'est pas un agent.
2. **Session agent.** La partie session de `pilote-file` (`claude -p` quand l'empreinte de la file
   change) reste soumise à ADR-128 D2 : elle ne s'active pas tant que le producteur de
   `useful_capabilities_not_complexity` n'est pas présent dans
   `backend/src/modules/admin/services/command-center-kpi.service.ts` (L1, définition d'ADR-128 D2).
   La détection des doublons, qui demande un jugement, arrive avec la session.
3. **Critère de sortie.** Le producteur du KPI du rôle 23 devient un critère de sortie de l'étape 1.
4. **Activation de la session (étape 1b).** Après la sortie de l'étape 1, l'owner active la session
   par un acte distinct. Critères de sortie de 1b : 10 exécutions de journée consécutives vertes avec
   session ; coût réel d'une journée mesuré. L'étape 2 ne dépend pas de 1b : ses sessions sont
   bornées par les approbations de l'owner (ADR-128 D3, D4).

**Tableau D8 d'ADR-128, lignes amendées :**

| Étape | Contenu | Critère de sortie |
|---|---|---|
| 1 (mandat N) | runner DEV agents enregistré (D3.5) ; labels D1 créés ; routine `pilote-file` en mode déterministe | runner `online` vu par l'API avec un jeton de l'owner, labels `agents` seul ; 10 exécutions de journée consécutives vertes sans session ; issue de pilotage à jour ; producteur de `useful_capabilities_not_complexity` présent (L1) ; cause des exécutions en file établie ou traitée à part ; D3.4 constaté par l'owner |
| 1b | session agent de `pilote-file` | 10 exécutions de journée consécutives vertes avec session ; coût réel d'une journée mesuré |

Le critère « coût réel d'une journée mesuré » quitte l'étape 1 pour 1b : sans session, la routine ne
consomme aucun jeton et ses minutes `ubuntu-latest` ne sont pas facturées (dépôt public, ADR-128 D3).
Les étapes 0, 2 et 3 sont inchangées.

### D3 — Sécurité des runners auto-hébergés sur un dépôt public

Ces règles valent pour `hetzner-prod` et pour le futur runner agents du DEV.

1. **Forks : approbation de tous les contributeurs externes.** La politique `all_external_contributors`
   (en place au 2026-11-15) est maintenue ; l'abaisser est une décision qui passe par un ADR.
   L'owner n'approuve jamais l'exécution d'une PR de fork qui modifie `.github/**` ou un fichier
   exécuté par un job auto-hébergé : une fois approuvée, la PR exécute sa propre version du workflow.
2. **Aucun runner auto-hébergé accessible à un workflow de PR.** Dans la version de `main`, aucun job
   d'un workflow déclenché par `pull_request`, `pull_request_target`, `pull_request_review`,
   `pull_request_review_comment`, `issue_comment` ou `workflow_run` issu d'une PR ne s'exécute sur un
   runner auto-hébergé, sauf garde explicite sur `github.event_name` et `github.ref` comme dans
   `ci.yml`. Cette règle contraint `main` ; elle n'arrête pas une branche qui réécrit le workflow
   (D1, point 3). Les barrières contre ce cas sont D3.1 (forks) et D3.4 (identités du dépôt).
3. **Pas de groupe de runners.** Sur un compte utilisateur, un runner ne peut pas être restreint à
   des workflows ou à des branches choisis. Les labels routent les jobs ; ils ne sont pas une
   barrière de sécurité. Tout runner enregistré sur le monorepo est accessible à toute identité qui
   peut y modifier un workflow.
4. **Droit de modifier les workflows réservé à l'owner.** Aucune identité d'agent ne détient le droit
   de créer ou de modifier un fichier de `.github/workflows/` : ni l'application
   `automecanik-agents[bot]` (permission « Workflows »), ni un jeton personnel (portée `workflow` ou
   permission « Workflows »), ni le `GITHUB_TOKEN`, qui ne peut pas recevoir ce droit. Un agent peut
   proposer un changement de workflow dans une issue ou un fichier hors `.github/workflows/` ; l'owner
   le porte. L'état actuel de ces permissions n'est pas vérifié par cet ADR : l'owner le constate en
   lecture (critère de l'étape 1) et en retire l'excès s'il existe (acte de l'owner, hors de cet ADR).
5. **Runner agents du DEV.** Il est enregistré avec `--no-default-labels --labels agents` : il ne porte
   ni `self-hosted`, ni `Linux`, ni `X64`, et ne prend donc aucun job des cinq workflows destinés à
   `hetzner-prod` (déploiements PREPROD et PROD compris). Il ne sert que des workflows déclenchés par
   `schedule`, `workflow_dispatch` ou `issues: labeled` filtré sur l'expéditeur (ADR-128 D4) ; jamais
   un événement de PR. Son compte système ne détient aucune clé ni aucun secret qui donne accès à
   l'hôte PROD.
6. **`hetzner-prod`.** Il reste réservé à la CI de `main`, aux déploiements et aux tests de PROD
   (les cinq workflows). Aucune routine d'agent ne le cible. Le risque résiduel est acté : toute
   identité qui peut modifier un workflow peut exécuter du code sur l'hôte PROD (D3.3) ; D3.4 limite
   ces identités à l'owner. Une évolution de ce runner (label `production` exigé par les jobs,
   déploiement depuis un runner hébergé par GitHub, etc.) relève d'un mandat et d'un ADR distincts.

## Options considérées

### Pour D2

- **Option A (retenue)** : `pilote-file` déterministe à l'étape 1 ; session soumise à D2 ; producteur
  du KPI du rôle 23 en critère de sortie de l'étape 1.
- **Option B, inverse (écartée)** : activer la session agent de `pilote-file` dès l'étape 1, par
  exception à D2 pour le rôle pilote, le producteur étant attendu plus tard. Écartée pour quatre
  raisons :
  1. [[rules-ai-cos|AI1]] (conservée par ADR-129 D5) : la session tournerait sans mesure, sur le rôle
     même dont le KPI juge l'utilité des capacités (« des capacités utiles, pas de complexité ») ;
  2. ce serait la première exception à D2, un précédent pour les cinq autres rôles sans producteur ;
  3. le coût s'engage avant d'être mesurable : jusqu'à environ un million de jetons d'entrée par jour
     au premier appel seul (ADR-128 D3), pour un gain qu'aucune mesure ne montre ;
  4. la partie déterministe couvre déjà les fonctions d'ADR-128 D6 sauf la détection des doublons.
- **Option C (écartée)** : reporter `pilote-file` en entier jusqu'au producteur. La file D1 resterait
  sans pilote pendant l'étape 1 ; les mandats bloqués ou expirés ne seraient pas signalés. Une
  routine déterministe ne relève pas d'AI1.

### Pour D3

- **Garde `if:` seule (écartée)** : elle est contenue dans le fichier que la PR peut modifier.
- **Groupe de runners restreint (impossible)** : réservé aux organisations ; `ak125` est un compte
  utilisateur.
- **Règles D3.1 à D3.6 (retenues)** : natives, sans réglage nouveau à l'adoption, et le risque
  résiduel est écrit.

## Conséquences

### Positives

- Le tableau des constats d'ADR-128 décrit l'état réel : un runner existe, sur PROD.
- L'étape 1 peut sortir sans exception à D2 ; le pilote rend service sans session.
- Le lien entre droit d'écriture et exécution sur l'hôte PROD est écrit, avec la règle qui le borne.

### Négatives

- La détection des doublons attend le producteur du KPI du rôle 23.
- Le risque résiduel sur `hetzner-prod` demeure tant que le runner reste sur l'hôte PROD (D3.6).
- D3.4 peut retirer à l'application des agents un droit dont un travail en cours dépend ; un
  changement de workflow passe alors par l'owner.

### Neutres

- Les étapes 0, 2 et 3 d'ADR-128 et ses décisions D1, D4 à D7 restent inchangées, hors les lectures
  de D1 point 4 et la règle D3 qui remplace ADR-128 D4.4 (« aucun déclencheur `pull_request` venant
  d'un fork ») par une règle plus large (aucun événement de PR, quelle que soit l'origine).

## Ce que cet ADR ne fait pas

- Il n'active rien et ne modifie aucun réglage GitHub (politique d'approbation, permissions de
  l'application, runners, labels, secrets, variables).
- Il ne touche ni la PR #2071, ni le runner `hetzner-prod`, ni la PROD, ni le monorepo.
- Il ne modifie pas le texte d'ADR-128 : le commit de ratification posera `amended_by`.

## Inconnues

- Compte système, accès Docker et secrets lisibles du runner `hetzner-prod` sur l'hôte PROD.
- Permissions actuelles de l'application `automecanik-agents[bot]` et des jetons d'agents sur
  `.github/workflows/` (D3.4).
- Cause des exécutions en file du 2026-11-11 hors des fenêtres d'incident GitHub.

## Retour arrière

Avant fusion : fermer la PR. Après : un ADR qui remplace celui-ci ; ADR-128 se relit alors sans ses
amendements.

## Revue planifiée

À la sortie de l'étape 1 d'ADR-128, et au plus tard le 2027-02-14 (revue d'ADR-128).

## Références

- [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]],
  [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]],
  [[ADR-012-aicos-vps-architecture|ADR-012]], [[ADR-034-aicos-operating-contract|ADR-034]]
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]],
  [[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]]
- [[rules-ai-cos]], [[rules-vault]]
- [[MOC-Decisions]], [[MOC-Agents]]

---

*Proposé le : 2026-11-15*
*Dernière revue : 2026-11-15*
