---
id: ADR-075
title: "Topologie et vocabulaire de déploiement (DEV / PREPROD / PROD) ; commit, tag, image, environnement, preuve CI et version servie — amende ADR-001"
status: proposed
date: "2026-05-18"
decision_makers: ["Architecture Team", "@fafa"]
version: "1.1.0"
supersedes: []
superseded_by: []
amends: ["ADR-001"]
extends: []
related_adr: ["ADR-028", "ADR-101", "ADR-102", "ADR-120"]
related_rules: ["rules-deployment-workflow", "T6", "G1", "G4"]
related_incidents: ["INC-2026-007-false-prod-claim-on-main-merge"]
reviewed_by: ""
---

# ADR-075 : topologie et vocabulaire de déploiement

- **Statut** : Proposed. Version 1.0.0 rédigée le 2026-05-18, révisée le 2026-11-01 (1.1.0). Rien
  n'est normatif avant la ratification (section « Ratification ») et la fusion
  ([[ADR-101-vault-decides-canon-authority|ADR-101]] D1).
- **Amende** [[ADR-001-environment-separation|ADR-001]] : il précise la topologie que ce dernier ne
  décrit pas et relève un écart entre son tableau et l'état réel (D2).
- **Révision 1.1.0** : réconciliation avec ADR-101 (le vault décide, le monorepo exécute), retrait
  des adresses IP et des noms d'hôte au profit des rôles, ajout de la promotion, du rollback et de la
  distinction entre commit, tag, image, environnement, preuve CI et version servie.
- **Méthode** : constats vérifiés le 2026-11-01 sur `main` du monorepo
  (`6ab7854c2adf15e3e588f8a73e4f9085ecaeee5d`) et sur `main` du vault.

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

### Topologie réelle (2026-11-01)

Sources : `.sops.yaml`, `docker-compose.preprod.yml`, `.github/workflows/ci.yml`,
`.github/workflows/deploy-prod.yml` du monorepo.

| Rôle | Machine | Ce qui y tourne | Accès |
|---|---|---|---|
| **DEV** | machine opérateur | code, worktrees, runtime de développement (`npm run dev`, port 3000) resynchronisé depuis `main` par un cron | opérateur et agents ; aucun conteneur de déploiement |
| **PREPROD** | hôte PROD, distinct de la machine DEV | conteneur démarré par le job `🧪 Deploy PREPROD` de `ci.yml` : image du commit (`:sha-<commit>`), réétiquetée `:preprod` en local ; `READ_ONLY=true` et clé anon seule (ADR-028 Option D) | port 3200 lié à la boucle locale ; aucune URL publique ; lu par la CI, ou en local sur l'hôte |
| **PROD** | même hôte | conteneur promu par `deploy-prod.yml`, derrière Caddy (80/443) | trafic réel des utilisateurs |

L'hôte PROD porte aussi le runner GitHub Actions auto-hébergé. Il exécute `deploy-prod.yml` et, dans
`ci.yml`, les jobs `🧪 Deploy PREPROD`, `🎭 E2E Smoke Tests` et `🔦 Lighthouse Performance Audit` ;
`build.yml` et les autres jobs tournent sur des runners hébergés par GitHub.

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
2. **PREPROD** : le conteneur de CI de l'hôte PROD. Le run `ci.yml` d'un push sur `main` le
   redémarre sur l'image de ce commit, une fois les jobs requis en `success` ; un run en attente est
   remplacé par celui du push suivant. Il tourne en lecture seule sur la base partagée avec PROD
   (ADR-028 Option D). Il sert à la validation automatique du
   commit : santé du conteneur, E2E Smoke, Lighthouse. Il n'a pas d'URL publique, et le cycle ne
   comporte aucune validation humaine.
3. **PROD** : le conteneur live du même hôte, derrière Caddy, qui sert le trafic réel.

**Écarts avec ADR-001.** Le présent ADR consigne l'état réel ; il ne tranche aucun des deux.

- Le tableau d'ADR-001 annonce en PREPROD des « données anonymisées ». PREPROD lit en réalité la base
  de PROD, en lecture seule (ADR-028). Cet ADR ne décide ni d'une anonymisation ni d'une base séparée.
- La règle 3 d'ADR-001 place PREPROD en mode `observe` avec métriques. `docker-compose.preprod.yml`
  démarre PREPROD avec `RPC_GATE_MODE=enforce` et `RPC_GATE_ENFORCE_LEVEL=P1`.

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
- Il ne modifie pas le monorepo. Sur `main` (`6ab7854c2`), `.claude/rules/deployment.md` contient
  encore des adresses IP, un rollback PREPROD par push direct sur `main` (branche protégée), un
  rollback PROD par SSH et l'affirmation que la branche `dev` déploie comme `main` (le job
  `🧪 Deploy PREPROD` ne part que de `main`). Ce sont des constats au sens de D1, à corriger par une
  PR du monorepo.
- Il n'ajoute aucune garde à `deploy-prod.yml`. Ce workflow accepte un `workflow_dispatch` sur une
  branche et ne contrôle que la forme du nom de la ref : il déploierait alors le commit de tête de la
  branche sans tag `v*`. [[rules-deployment-workflow]] l'interdit (D3) ; une garde mécanique relève
  d'une PR du monorepo.
- Il ne décide pas d'anonymiser les données PREPROD ni de changer le mode du RPC gate (D2).
- Il ne réécrit pas les documents historiques qui emploient l'ancien vocabulaire.

## Mise en œuvre

| Élément | État au 2026-11-01 |
|---|---|
| PR monorepo #590 (règle d'agent, lint, hook, workflow) | fusionnée le 2026-05-18 (`345b96809d59fe675a6bb4fa8d97a7d27dd0b1c4`) |
| `scripts/lint/check-preprod-vocabulary.sh`, `.husky/pre-commit`, `preprod-vocabulary-guard.yml` | présents sur `main` du monorepo |
| [[rules-deployment-workflow]] 2.0.0 | réécrite dans cette PR : déclencheurs, promotion, rollback, six preuves |
| `ops/moc/MOC-Knowledge.md` | les mentions de `gh pr merge --admin` et d'auto-fusion des notes historiques sont signalées comme une pratique de l'époque |
| `ops/moc/MOC-Decisions.md` | index régénéré (`sync_moc_decisions.py --write`) |

## Ratification

[[rules-deployment-workflow]] 2.0.0 s'appuie sur cet ADR ; elle ne se fusionne pas tant qu'il est
`proposed`. À la décision de l'owner, avant la fusion, un commit de cette PR :

- passe `status` à `accepted`, renseigne `decision_date` et `reviewed_by`, et réécrit la ligne
  Statut, dont la phrase qui suspend l'entrée en vigueur ;
- ajoute `amended_by: ["ADR-075"]` au frontmatter d'[[ADR-001-environment-separation|ADR-001]] ;
- retire « (proposé) » des mentions de cet ADR dans [[rules-deployment-workflow]] ;
- régénère l'index de [[MOC-Decisions]] (`_scripts/sync_moc_decisions.py --write`).

Ce commit change la tête : son diff est revu à son niveau avant la fusion
([[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]] D4).

## Critères de succès

- [x] PR monorepo #590 fusionnée.
- [ ] `bash scripts/lint/check-preprod-vocabulary.sh` sur `main` du monorepo : 0 violation.
- [ ] `.claude/rules/deployment.md` aligné sur D2 à D4 par une PR du monorepo.
- [ ] Une session neuve à qui l'on demande « sur quelle machine tourne PREPROD ? » répond « dans un
  conteneur de CI sur l'hôte PROD, pas sur la machine DEV ».

## Liens

- [[ADR-001-environment-separation]] (amendé)
- [[ADR-028-preprod-supabase-isolation]] (PREPROD en lecture seule, Option D)
- [[ADR-101-vault-decides-canon-authority]] (le vault décide, le monorepo exécute)
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] (G4 : écriture par PR, fusion humaine)
- [[rules-deployment-workflow]], [[rules-technical]] (T6)
- Monorepo : PR #590 ; `.claude/rules/deployment.md` ; `scripts/lint/check-preprod-vocabulary.sh`

---
_Dernière mise à jour : 2026-11-01_
