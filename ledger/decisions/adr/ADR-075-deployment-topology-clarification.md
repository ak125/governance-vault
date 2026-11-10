---
id: ADR-075
title: "Topologie et vocabulaire de déploiement (DEV / PREPROD / PROD) ; commit, tag, image, environnement, preuve CI et version servie — amende ADR-001"
status: accepted
date: "2026-05-18"
decision_date: "2026-11-10"
decision_makers: ["Architecture Team", "@fafa"]
version: "1.1.0"
supersedes: []
superseded_by: []
amends: ["ADR-001"]
extends: []
related_adr: ["ADR-028", "ADR-101", "ADR-102", "ADR-120", "ADR-121", "ADR-123", "ADR-124"]
related_rules: ["rules-deployment-workflow", "T6", "G1", "G4"]
related_incidents: ["INC-2026-007"]
reviewed_by: "Relecteur indépendant (agent distinct de l'auteur) — enregistrement de revue de la PR #294"
---

# ADR-075 : topologie et vocabulaire de déploiement

- **Statut** : Accepted (2026-11-10). Décision de l'owner, décideur humain : Marwane, sur le candidat
  de la PR #294 (`d58f01cf49a94112c1022f0d748fc10c5f1559bb`). Version 1.0.0 rédigée le 2026-05-18,
  révisée le 2026-11-01 (1.1.0), constats revérifiés le 2026-11-10. Le commit de ratification est
  préparé par un agent : son auteur et sa clé de signature sont techniques. Canon applicable à la
  fusion par l'owner de la tête qui porte cette décision, sous les contrôles requis
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7) ; avant cette fusion,
  ce statut décrit le candidat ratifié et ne modifie pas le canon de `main`.
- **Amende** [[ADR-001-environment-separation|ADR-001]] : il précise la topologie que ce dernier ne
  décrit pas et relève deux écarts entre ADR-001 et l'état réel, ainsi qu'un écart avec
  [[ADR-028-preprod-supabase-isolation|ADR-028]] (D2).
- **Révision 1.1.0** : réconciliation avec ADR-101 (le vault décide, le monorepo exécute), retrait
  des adresses IP et des noms d'hôte au profit des rôles, ajout de la promotion, du rollback et de la
  distinction entre commit, tag, image, environnement, preuve CI et version servie.
- **Méthode** : constats vérifiés le 2026-11-01 sur `main` du monorepo
  (`6ab7854c2adf15e3e588f8a73e4f9085ecaeee5d`) et sur `main` du vault, puis revérifiés le 2026-11-10
  sur `main` du monorepo (`6eda5d6dd6c023ba4401186e99a27a098ae169b5`) : pile PREPROD, workflows du
  runner auto-hébergé, tags, branches et règle d'agent. L'observation sur le runner unique date du
  2026-11-01.

## Contexte

L'audit du 2026-05-18 a compté 419 occurrences du mot « preprod » sous ses diverses graphies
(monorepo 118, vault 242, mémoires d'agents 59). Le mot désignait trois choses sans définition
commune :

1. le tag Docker `:preprod`, un artefact de CI ;
2. le conteneur éphémère que la CI démarre à partir de ce tag ;
3. un environnement intermédiaire imaginaire entre DEV et PROD, lu dans le préfixe « pré- ».

ADR-001 pose trois environnements logiques sans décrire la topologie : machines, ports, images,
déclencheurs. Ce silence a produit des erreurs répétées : un nom d'hôte PREPROD public qui n'a
jamais existé, une « PREPROD miroir de PROD », l'amalgame de la machine DEV et du conteneur PREPROD,
une mémoire d'agent qui plaçait le tag `:preprod` sur la machine DEV. L'owner a corrigé la même
confusion lors d'au moins trois sessions (2026-05-16, 17 et 18).

Deux confusions de même nature s'y ajoutent : une fusion sur `main` annoncée comme un déploiement
PROD ([[2026-04-21-false-prod-claim-on-main-merge|INC-2026-007]]), et une CI verte présentée comme la
preuve qu'une version est servie.

### Topologie réelle (2026-11-10)

Sources : `.sops.yaml`, `docker-compose.preprod.yml`, `scripts/ci/preprod-readonly-gateway.cjs` et,
sous `.github/workflows/`, `ci.yml`, `build.yml`, `deploy-prod.yml` et
`deploy-monitoring-scripts.yml` du monorepo.

| Rôle | Machine | Ce qui y tourne | Accès |
|---|---|---|---|
| **DEV** | machine opérateur | code, worktrees, runtime de développement (`npm run dev`, port 3000) resynchronisé depuis `main` par un cron | opérateur et agents ; aucun conteneur de déploiement |
| **PREPROD** | hôte PROD, distinct de la machine DEV | pile de cinq conteneurs démarrée par le job `🧪 Deploy PREPROD` de `ci.yml` : l'application (image du commit `:sha-<commit>`, réétiquetée `:preprod` en local, `READ_ONLY=true`), une passerelle en lecture seule vers la base, un proxy Caddy propre à PREPROD, imgproxy et Redis | port 3200 de la boucle locale, publié par le proxy PREPROD ; aucune URL publique ; lu par la CI, ou en local sur l'hôte |
| **PROD** | même hôte | conteneur promu par `deploy-prod.yml`, derrière Caddy (80/443) | trafic réel des utilisateurs |

L'hôte PROD porte aussi le runner GitHub Actions auto-hébergé (`runs-on: [self-hosted, Linux, X64]`) :
`deploy-prod.yml` y inspecte le conteneur PROD local. Sur `main`, cinq workflows (huit jobs) y
tournent : `deploy-prod.yml`, les jobs `🧪 Deploy PREPROD`, `🎭 E2E Smoke Tests` et
`🔦 Lighthouse Performance Audit` de `ci.yml`, `prod-smoke-tests.yml` (deux jobs), `visual-gate.yml`
et `deploy-monitoring-scripts.yml`, qui installe des scripts de surveillance sur l'hôte lui-même.
Les métadonnées des jobs exécutés nomment un seul runner pour ces cinq workflows ; l'inventaire des
runners n'est pas lisible (403), donc un second runner inactif aux mêmes labels n'est pas exclu.
`build.yml` tourne sur un runner hébergé par GitHub.

L'application PREPROD n'a aucun accès direct à la base : `DATABASE_URL` et la clé de service sont
vides, la clé anon est une valeur sentinelle inutilisable, et son seul réseau est interne, sans
sortie. Elle lit la base par la passerelle `readonly_preprod`, seul processus à détenir la clé amont
(fichier provisionné à part sur l'hôte, jamais copié de PROD par la CI). La passerelle ne transmet
que des requêtes GET et HEAD ; elle convertit en GET les appels RPC de lecture qu'elle reconnaît et
refuse toute autre méthode. Cet état date des PR monorepo #1963 et #1964 (2026-11-06).

## Décision

### D1 — Le vocabulaire se décide ici ; le monorepo l'exécute

Ce vocabulaire est fixé par cet ADR et par [[rules-deployment-workflow]] (ADR-101 D1). Dans le
monorepo, `.claude/rules/deployment.md` le transmet aux agents et
`scripts/lint/check-preprod-vocabulary.sh` (pre-commit, workflow `preprod-vocabulary-guard.yml`) en
est la garde mécanique. Ces fichiers exécutent la décision et ne la fondent pas. Un écart entre eux
et cet ADR est un constat, résolu par une PR du monorepo ou par un ADR d'amendement (ADR-101 D3).

La version 1.0.0 faisait de `.claude/rules/deployment.md` la « source de vérité terminologique ».
Cette formule est retirée : elle inversait le sens fixé par ADR-101.

### D2 — Trois environnements, définis par leur rôle

1. **DEV** : la machine opérateur. On y code et on y teste. Aucun conteneur de déploiement n'y
   tourne. Une fusion sur `main` n'y déploie rien ; le runtime de développement suit `main` par
   resynchronisation.
2. **PREPROD** : la pile de CI de l'hôte PROD, soit l'application et ses quatre services d'appui.
   Le run `ci.yml` d'un push sur `main` la redémarre sur l'image de ce commit, une fois les jobs
   requis en `success` ; un run en attente est remplacé par celui du push suivant. L'application lit
   la base partagée avec PROD, en lecture seule (ADR-028 Option D ; écart ci-dessous). Elle sert à la
   validation automatique du commit : santé du conteneur, E2E Smoke, Lighthouse. Elle n'a pas d'URL
   publique, et le cycle ne comporte aucune validation humaine.
3. **PROD** : le conteneur live du même hôte, derrière Caddy, qui sert le trafic réel.

**Écarts avec ADR-001 et ADR-028.** Le présent ADR consigne l'état réel ; il ne tranche aucun des
trois.

- Le tableau d'ADR-001 annonce en PREPROD des « données anonymisées ». PREPROD lit en réalité la base
  de PROD, en lecture seule (ADR-028). Cet ADR ne décide ni d'une anonymisation ni d'une base séparée.
- La règle 3 d'ADR-001 place PREPROD en mode `observe` avec métriques. `docker-compose.preprod.yml`
  démarre PREPROD avec `RPC_GATE_MODE=enforce` et `RPC_GATE_ENFORCE_LEVEL=P1`.
- La couche 2 d'ADR-028 (« Anon key only ») donne à l'application PREPROD la clé anon. Depuis les PR
  monorepo #1963 et #1964, l'application n'a plus de clé utilisable et passe par la passerelle en
  lecture seule décrite plus haut. L'isolation est plus stricte que celle qu'ADR-028 décrit, mais
  ADR-028 n'a pas été amendé.

### D3 — Six objets, six preuves

Chacun de ces objets a sa propre preuve. Aucun ne prouve l'objet suivant.

| Objet | Ce que c'est | Ce qui le prouve | Ce que cela ne prouve pas |
|---|---|---|---|
| **Commit** | un SHA de 40 caractères sur `main` | `git rev-parse`, le commit de fusion de la PR | qu'une image en soit construite, ni qu'il soit déployé |
| **Tag** | un tag git `v*` posé sur un commit | `git tag --points-at <sha>`, `git rev-parse <tag>^{commit}` | que le déploiement PROD ait réussi |
| **Image** | `:sha-<commit>` (une par commit, label `org.opencontainers.image.revision`) ; `:preprod`, `:production` et `:production-previous` sont des alias mobiles | l'identifiant d'image et son label `revision` | qu'elle tourne quelque part ; un alias ne désigne pas une version stable |
| **Environnement** | DEV, PREPROD ou PROD (D2) | le rôle de la machine ou du conteneur | la version qu'il sert |
| **Preuve CI** | un run `ci.yml` (push `main`) dont `🧪 Deploy PREPROD`, `🎭 E2E Smoke Tests` et `🔦 Lighthouse Performance Audit` sont en `success` ; un run `deploy-prod.yml` en `success` | le statut des jobs pour ce commit | que cette version soit encore servie : un déploiement ou un rollback ultérieur a pu la remplacer |
| **Version servie** | le commit que l'environnement exécute au moment de la lecture | `/health` de l'environnement, champ `revision`, égal au SHA attendu | rien sur un autre environnement |

« Déployé en PREPROD » ou « déployé en PROD » ne s'écrit qu'avec la version servie de cet
environnement, lue et datée. Une fusion, un tag ou une CI verte se nomment comme tels.

### D4 — Règles de vocabulaire

- « DEV pré-prod » et « DEV preprod » sont interdits : ils amalgament deux machines.
- PREPROD n'a pas de nom d'hôte public. Aucun document n'en invente un.
- « PREPROD miroir » et « miroir de PROD » sont interdits : PREPROD est en lecture seule, ce n'est
  pas une réplique.
- Le terme « staging » n'est pas employé : on dit PREPROD ou PROD.
- `:preprod` désigne l'alias Docker, déplacé par `build.yml` à chaque image construite depuis
  `main`. Il ne désigne ni un environnement ni une version.
- Les documents nomment les machines par leur rôle (« machine DEV », « hôte PROD »), sans adresse IP
  ni nom d'hôte. Le rôle est stable quand l'adresse change, et le vault est public.

## Options considérées

### Option A : vocabulaire décidé au vault, exécuté et vérifié au monorepo (retenue)

Un ADR et une règle du vault, une règle d'agent et un lint dans le monorepo. Aucun renommage
physique : tag, fichier compose et noms de jobs restent. Ce renommage est l'option C, différée.

- **Avantages** : cohérence vérifiée mécaniquement ; aucun changement runtime ni CI ; rollback par
  revert d'une PR.
- **Inconvénients** : le mot « preprod » reste dans des artefacts (tag, compose, nom de job) ; la
  liste d'exceptions du lint s'entretient.

### Option B : corriger seulement les pires occurrences

Errata sur une dizaine de fichiers, sans définition centrale ni lint. **Rejetée** : la confusion est
revenue sur trois sessions, et sans garde la documentation dérive de nouveau.

### Option C : renommages physiques complets

Renommer `:preprod`, `docker-compose.preprod.yml` et le job `🧪 Deploy PREPROD`. **Différée** :
les protections de branche, la gate PROD (`prod-preprod-evidence.mjs` cherche ce job par son nom),
les badges et les runbooks en dépendent. Un renommage demanderait une migration par alias, sur
plusieurs cycles, et un ADR distinct.

## Conséquences

### Positives

- Un vocabulaire unique, décidé au vault et vérifié dans le monorepo.
- Une fusion, un tag, une CI verte et une version servie ne se confondent plus dans un rapport.

### Négatives

- Le mot « preprod » demeure dans des noms techniques jusqu'à une éventuelle option C.
- La liste d'exceptions du lint reste à entretenir.

### Neutres

- ADR-001 reste en vigueur pour la séparation logique des trois environnements.

## Ce que cet ADR ne fait pas

- Il ne modifie ni workflow, ni image, ni conteneur, ni configuration d'environnement.
- Il ne modifie pas le monorepo. Sur `main` (`6eda5d6dd`), `.claude/rules/deployment.md` contient
  encore des adresses IP, un rollback PREPROD par push direct sur `main` (branche protégée), un
  rollback PROD par SSH et l'affirmation que la branche `dev` déploie comme `main` (le job
  `🧪 Deploy PREPROD` ne part que de `main`). `scripts/lint/check-preprod-vocabulary.sh` y désigne
  encore ce fichier comme le canon du vocabulaire. Ce sont des constats au sens de D1, à corriger
  par une PR du monorepo.
- Il n'ajoute aucune garde à `deploy-prod.yml`. Ce workflow accepte un `workflow_dispatch` sur toute
  ref et exécute le `deploy-prod.yml` de la ref choisie. Lancé sur `main` dont PREPROD a validé la
  tête, il déploierait ce commit sans tag `v*` et publierait l'image sous `:main`. Sur une branche
  dont la tête est un commit de `main` qui contient #1696 et que PREPROD a validé, il ferait de même
  sous le nom de la branche si ce nom est un tag Docker valide ; sinon il refuse au contrôle de ce
  nom, après avoir remplacé `:production-previous`. Sur une autre ref, le résultat suit le workflow
  de cette ref : au 2026-11-10, 25 branches distantes en portent un sans garde de label ni preuve
  PREPROD. Relancé sur un tag qui ne contient pas le commit `ed10ec6e5` (2026-04-21 ; 194 tags sur
  303), il exécute le workflow de ce tag, sans garde de provenance : il promeut l'alias `:preprod`
  courant vers PROD et le publie sous le nom du tag, ce qui écrase le tag Docker de la version
  d'origine. [[rules-deployment-workflow]] interdit ces lancements (D3, D5). Une garde mécanique
  relève d'une PR du monorepo ; le workflow d'un ancien tag reste figé dans ce tag.
- Il ne décide pas d'anonymiser les données PREPROD ni de changer le mode du RPC gate (D2).
- Il ne réécrit pas les documents historiques qui emploient l'ancien vocabulaire.

## Mise en œuvre

| Élément | État au 2026-11-10 |
|---|---|
| PR monorepo #590 (règle d'agent, lint, hook, workflow) | fusionnée le 2026-05-18 (`345b96809d59fe675a6bb4fa8d97a7d27dd0b1c4`) |
| `scripts/lint/check-preprod-vocabulary.sh`, `.husky/pre-commit`, `preprod-vocabulary-guard.yml` | présents sur `main` du monorepo |
| [[rules-deployment-workflow]] 2.0.0 | réécrite dans cette PR : déclencheurs, promotion, rollback, six preuves |
| `.claude/rules/deployment.md` du monorepo | PR monorepo #1949 (brouillon) l'aligne sur cette révision ; elle suivra toute correction de celle-ci |
| `ops/moc/MOC-Knowledge.md` | les mentions de `gh pr merge --admin` et d'auto-fusion des notes historiques sont signalées comme une pratique de l'époque |
| `ops/moc/MOC-Decisions.md` | index régénéré (`sync_moc_decisions.py --write`) |

## Ratification

[[rules-deployment-workflow]] 2.0.0 s'appuie sur cet ADR : les deux entrent en vigueur ensemble, à
la fusion de la PR #294.

L'owner a ratifié cet ADR le 2026-11-10, sur le candidat `d58f01cf49a94112c1022f0d748fc10c5f1559bb`.
Le commit de ratification, préparé par un agent sur cette décision :

- passe `status` à `accepted`, renseigne `decision_date` et `reviewed_by`, et réécrit la ligne
  Statut, dont la phrase qui suspendait l'entrée en vigueur ;
- date la ligne « Accepté le » du pied de page et passe la présente section de la prescription au
  constat ;
- ajoute `amended_by: ["ADR-075"]` au frontmatter d'[[ADR-001-environment-separation|ADR-001]] ;
- retire « (proposé) » des mentions de cet ADR dans [[rules-deployment-workflow]] ;
- régénère l'index de [[MOC-Decisions]] (`_scripts/sync_moc_decisions.py --write`).

Il ne modifie aucune décision : D1 à D4 et la règle sont celles du candidat. `reviewed_by` renvoie à
la revue indépendante consignée sur la PR ; il ne vaut pas approbation de l'owner. La décision de
l'owner est consignée par le commit de ratification (ADR-121 D7) ; son accord nominatif de niveau C
l'est sur la PR ([[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]] D3) ; la fusion de la tête
ratifiée est tracée selon ADR-121 D4. Tout commit ajouté après le candidat change la tête : son diff
est revu à son niveau avant la fusion (ADR-120 D4).

## Critères de succès

- [x] PR monorepo #590 fusionnée.
- [ ] `bash scripts/lint/check-preprod-vocabulary.sh` sur `main` du monorepo : 0 violation.
- [ ] `.claude/rules/deployment.md` aligné sur D2 à D4 par une PR du monorepo.
- [ ] Une session neuve à qui l'on demande « sur quelle machine tourne PREPROD ? » répond « dans une
  pile de conteneurs de CI sur l'hôte PROD, pas sur la machine DEV ».

## Liens

- [[ADR-001-environment-separation]] (amendé)
- [[ADR-028-preprod-supabase-isolation]] (PREPROD en lecture seule, Option D)
- [[ADR-101-vault-decides-canon-authority]] (le vault décide, le monorepo exécute)
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] (G4 : écriture par PR)
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts]] (D4 : la fusion appartient à l'owner)
- [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte]] et
  [[ADR-124-premier-perimetre-fusion-automatique-monorepo]] (fusion automatique dans un périmètre
  activé ; chaque fusion sur `main` du monorepo lance la chaîne PREPROD)
- [[rules-deployment-workflow]], [[rules-technical]] (T6)
- Monorepo : PR #590 ; `.claude/rules/deployment.md` ; `scripts/lint/check-preprod-vocabulary.sh`

---
_Dernière mise à jour : 2026-11-10_

*Accepté le : 2026-11-10 (décision de l'owner ; canon à la fusion de la tête ratifiée, ADR-121 D7)*
