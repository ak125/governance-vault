---
type: rules-document
status: canon
scope: deployment
updated: 2026-11-13
related_adrs: [ADR-028, ADR-075, ADR-101, ADR-102, ADR-121, ADR-123, ADR-124]
related_incidents: [INC-2026-007]
---

# Rules — Deployment Workflow (PREPROD par `main`, PROD par tag)

> **Version** : 2.1.0 | **Status** : CANON (règle du vault, normative au sens de G1)
> **État décrit** : `main` du monorepo après la fusion de la PR #2046 (2.0.0 : `main` au 2026-11-10,
> `6eda5d6dd6c023ba4401186e99a27a098ae169b5`)
> **Incident racine** : [[2026-04-21-false-prod-claim-on-main-merge|INC-2026-007]], une fusion sur
> `main` annoncée comme un déploiement PROD.
> **2.0.0** : la 1.0.0 plaçait le déploiement de `main` sur la machine DEV et prescrivait
> `gh pr merge --admin`, un rollback par push direct sur `main` et un rollback PROD par SSH. Elle
> contredisait T6 ([[rules-technical]], corrigée par [[ADR-101-vault-decides-canon-authority|ADR-101]]) :
> `main` est protégée. Le vocabulaire suit [[ADR-075-deployment-topology-clarification|ADR-075]].
> **2.1.0** : le workflow PROD refuse toute ref autre qu'un tag `v*` (PR monorepo #2010) et devient
> `release-prod.yml` ; l'ancien chemin `deploy-prod.yml` est désactivé (#2046). La classification
> des anciens tags (D5) est retirée : aucun ne doit être relancé (D3).

---

## D1 — Déclencheurs

Deux déclencheurs, distincts et non substituables.

| Déclencheur | Workflow du monorepo | Image | Environnement | Validation |
|---|---|---|---|---|
| Fusion d'une PR sur `main` (push `main`) | `ci.yml` : `🐳 build` (via `build.yml`), puis `🧪 Deploy PREPROD`, `🎭 E2E Smoke Tests`, `🔦 Lighthouse Performance Audit` | `build.yml` publie `:sha-<commit>` et déplace l'alias `:preprod` | **PREPROD** : pile de CI sur l'hôte PROD (cinq conteneurs, ADR-075) ; application en `READ_ONLY=true`, sans accès direct à la base ; port 3200 de la boucle locale, publié par le proxy de la pile | automatique, sans humain |
| Push d'un tag `v*`, ou `workflow_dispatch` de `Release PROD (tag v*)` sur ce tag | `release-prod.yml` | promotion de `:sha-<commit du tag>` vers `:production` | **PROD** : conteneur live derrière Caddy | décision de l'owner : le tag |

- Aucun workflow ne déploie sur la machine DEV. Son runtime de développement suit `main` par
  resynchronisation (`scripts/ops/sync-dev-runtime.sh`, lancé par un cron).
- `ci.yml` se déclenche aussi sur un push `dev`, mais `build.yml` et `🧪 Deploy PREPROD` ne
  publient et ne déploient que depuis `main`. Au 2026-11-10, la branche `dev` n'existe pas sur le
  dépôt distant.
- `ci.yml` ne filtre pas les chemins : toute fusion sur `main` lance le cycle PREPROD, y compris
  celle d'une PR de documentation et celle qu'exécute une porte de fusion automatique
  ([[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]] D7). Un run encore en attente
  est remplacé par celui de la fusion suivante (D4.3).
- Un push `main` qui modifie `scripts/monitoring/*.sh` lance aussi `deploy-monitoring-scripts.yml`,
  qui installe ces scripts dans `/usr/local/bin` de l'hôte PROD, hors des conteneurs. Ce workflow se
  lance aussi à la main (`workflow_dispatch`). Ce n'est pas un déploiement d'environnement, mais la
  fusion d'une telle PR modifie l'hôte PROD.

## D2 — Règle mnémonique

> **`main` = PREPROD. `v*` = PROD.**

En cas de doute, lire le workflow, pas la documentation.

## D3 — Interdictions

- **Ne pas annoncer « déployé en PROD »** après une fusion sur `main` : la fusion déploie PREPROD.
- **Ne pas écrire « déployé » sans la version servie** de l'environnement (D6).
- **Ne pas pousser directement sur `main`** : la branche est protégée, tout passe par une PR (T6).
- **Ne pas contourner la protection de `main`** : une PR passe ses checks requis et ses règles de
  fusion. Elle est fusionnée selon T6 : par l'owner, sur une tête épinglée, ou automatiquement dans
  un périmètre adopté puis activé selon
  [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]]. Hors d'un tel périmètre,
  un agent ne lance jamais de fusion et n'active jamais d'auto-fusion
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4). Cette règle ne prescrit
  plus `gh pr merge --admin`, qui passe outre les exigences de la protection, ni la désactivation
  d'un check.
- **Ne pas déployer PROD hors de `release-prod.yml`** : son chemin vérifie la ref, la preuve
  PREPROD et capture le point de rollback (D4.5).
- **Ne lancer `Release PROD (tag v*)` que sur un tag `v*` qui contient `release-prod.yml`.** Le
  formulaire du `workflow_dispatch` propose `main` par défaut, et le run exécute le workflow de la
  ref choisie. Sa première étape, `🔖 Release ref gate` (PR monorepo #2010), refuse avant le
  checkout et avant toute action sur l'hôte toute ref autre qu'un tag `v*` (`refs/tags/v…`, sans `/`
  après le `v`, comme le déclencheur `push`). Une ref dont le commit ne contient pas
  `release-prod.yml` ne peut pas lancer ce workflow.
- **Ne lancer aucun run de l'ancien workflow `deploy-prod.yml`, ne pas le réactiver, ne pas
  réintroduire ce chemin, ne pas pousser de tag `v*` sur un commit qui ne contient pas
  `release-prod.yml`.** GitHub identifie un workflow par son chemin et un run exécute la copie de
  sa ref : les tags et branches antérieurs au renommage (PR monorepo #2046) portent un
  `deploy-prod.yml`. Au 2026-11-13, les 305 tags `v*` le portent ; un seul contient la garde de
  ref, et 194 n'ont aucune garde de provenance (leur run promeut l'alias `:preprod` courant vers
  PROD). L'owner désactive ce workflow après la fusion du
  renommage ; son état, lu par l'API des workflows (`.state`), doit être `disabled_manually`. La
  documentation de GitHub ne précise pas l'effet d'une désactivation sur le run d'une ref
  antérieure : l'interdiction vaut désactivé ou non.
- **Ne pas utiliser le tag `latest`.** Un alias (`:preprod`, `:production`) ne sert pas de référence
  de version : citer le commit, le tag `v*` ou `:sha-<commit>`.

## D4 — Promotion PREPROD → PROD

1. La PR est fusionnée sous la protection de `main`, selon T6 : par l'owner sur une tête épinglée,
   ou automatiquement dans un périmètre activé selon ADR-123 (au 2026-11-10, le seul périmètre actif
   est celui d'ADR-124 : documentation Markdown du monorepo). Dans les deux cas la fusion est un push
   `main` et lance le cycle de l'étape 2.
2. `ci.yml` construit `:sha-<commit>`, déploie PREPROD et vérifie que le conteneur sert ce commit
   (`/health`, champ `revision`), puis lance E2E Smoke et Lighthouse.
3. L'owner choisit un commit dont les trois jobs `🧪 Deploy PREPROD`, `🎭 E2E Smoke Tests` et
   `🔦 Lighthouse Performance Audit` sont en `success`. Un run annulé par une fusion suivante ne
   valide pas son commit : prendre le dernier commit vert. Il note aussi le tag `v*` de la version
   en service, qui sert de point de retour (D5).
4. L'owner pose le tag `v*` sur ce commit et le pousse. Le tag est une décision de l'owner, jamais
   celle d'un agent.
5. `release-prod.yml` vérifie d'abord la ref (D3), puis refuse, sans rien modifier, un commit sans
   ces trois jobs verts
   (`scripts/ci/prod-preprod-evidence.mjs`). Il capture ensuite l'image en service comme point de
   rollback : son identifiant, épinglé pour le run, et l'alias `:production-previous`, poussé au
   registre (un échec de ce push n'arrête pas le run). Il vérifie que `:sha-<commit>` porte le bon
   label `revision` et la publie sous le nom du tag. Avant le point de non-retour, il a aussi copié
   les fichiers compose et mis à jour le `.env` de l'hôte. Passé ce point, il déplace `:production`,
   charge le Caddyfile du commit (`scripts/ci/prod-caddy-config.sh` : fichier validé dans le Caddy
   en service, s'il tourne, avant d'être écrit ; Caddy recréé si le fichier a changé, n'a pas encore
   été chargé, ou si sa définition compose a changé), remplace le conteneur PROD et contrôle
   `/health` (`revision` égal au commit du tag).
6. Si le conteneur PROD est absent de l'hôte, il n'y a pas d'image à capturer : le workflow refuse
   avant toute mutation. Le mode `break_glass_no_rollback_point` (entrée du `workflow_dispatch`, ou
   variable de dépôt `PROD_BREAK_GLASS_NO_ROLLBACK_POINT`) lève ce refus : le run déploie alors
   **sans point de rollback** (D5). C'est une décision de l'owner, prévue pour un premier
   déploiement ou un hôte reconstruit. La variable de dépôt vaut pour tout run, `workflow_dispatch`
   compris : tant qu'elle reste à `true`, l'absence du conteneur PROD ne fait refuser aucun run.
   Si le conteneur PROD existe, le mode ne change rien : l'image est capturée.

## D5 — Rollback

| Environnement | Procédure |
|---|---|
| **PREPROD** | PR de revert du commit fautif, fusionnée selon D4.1. Le push `main` qui en résulte relance le cycle D1. Jamais de push direct ni de force-push sur `main`. |
| **PROD, pendant un déploiement** | Automatique : après le point de non-retour, tout échec déclenche `⏪ Rollback PROD` (`scripts/ci/prod-rollback.sh`), qui remet `:production` sur l'image capturée avant la mutation et la redémarre. Il ne restaure que l'image : le Caddyfile, les fichiers compose et le `.env` posés par ce déploiement restent en place, et ses vérifications (`/health`, SSR) se font dans le conteneur, sans passer par Caddy. Un run annulé ou interrompu après le point de non-retour (annulation manuelle, perte du runner) ne déclenche pas ce rollback : dernière ligne. Ne jamais annuler un run en cours de déploiement. En mode break-glass (D4.6), si le conteneur PROD était absent, aucune image n'a été capturée : l'étape échoue et renvoie à l'intervention manuelle (dernière ligne). |
| **PROD, après un déploiement réussi** | L'owner relance `Release PROD (tag v*)` (`workflow_dispatch`) sur le tag `v*` de la version à restaurer, si ce tag contient `release-prod.yml`. |
| **PROD, workflow indisponible, run annulé ou interrompu après le point de non-retour, ou version à restaurer antérieure au renommage** | Intervention manuelle de l'owner sur l'hôte PROD, par la console de l'hébergeur. Aucun agent ne modifie PROD ; lire son `/health` (D6) n'est pas une modification. |

Le run relancé exécute le `release-prod.yml` **du tag choisi**, pas celui de `main`. Un tag qui le
contient contient aussi la garde de ref (#2010), le contrôle de la version servie (#1881, #1884,
#1887) et le traitement du Caddyfile (#1961) : ce sont les contrôles de D4.5. Un contrôle ajouté
plus tard ne vaut que pour les tags qui le contiennent.

Pour une version antérieure au renommage, l'intervention manuelle ne s'appuie pas sur
`:production-previous`, qu'un ancien run a pu remplacer (#1288) ; elle désigne l'image à restaurer
par `:sha-<commit>` si cette image est encore dans le registre, sinon par le tag Docker poussé à son
déploiement (nom du tag `v*`). Un ancien workflow a pu réécrire ce tag Docker avec une autre image :
vérifier son label `org.opencontainers.image.revision` avant de l'utiliser.

Un revert sur `main` ne change pas PROD : il redéploie PREPROD. PROD ne change que par D4 ou par une
ligne de ce tableau.

## D6 — Six objets, six preuves

| Objet | Preuve | Ne prouve pas |
|---|---|---|
| Commit sur `main` | SHA de 40 caractères, commit de fusion de la PR | qu'une image existe ou qu'elle soit déployée |
| Tag `v*` | `git tag --points-at <sha>` | que le déploiement PROD ait réussi |
| Image | identifiant d'image et label `org.opencontainers.image.revision` de `:sha-<commit>` | qu'elle tourne ; un alias ne désigne pas une version |
| Environnement | son rôle (ADR-075 D2) | la version qu'il sert |
| Preuve CI | jobs en `success` sur le run `ci.yml` du commit, run `release-prod.yml` en `success` (`deploy-prod.yml` avant le renommage) | que la version soit encore servie |
| Version servie | `/health` de l'environnement, `revision` égal au SHA attendu, lu et daté | quoi que ce soit sur un autre environnement |

Sources : `.github/workflows/ci.yml`, `.github/workflows/build.yml`,
`.github/workflows/release-prod.yml`, `.github/workflows/deploy-monitoring-scripts.yml`,
`docker-compose.preprod.yml`, `scripts/ci/prod-preprod-evidence.mjs`,
`scripts/ci/prod-caddy-config.sh`, `scripts/ci/prod-rollback.sh` et `scripts/ci/prod-ssr-probe.sh`
du monorepo, ainsi que les PR monorepo #2010 et #2046. `.claude/rules/deployment.md` transmet cette
règle aux agents du monorepo ; un écart entre les deux est un constat (ADR-101 D3).

## Mapping historique

| Date | Événement |
|------|-----------|
| 2026-04-21 | Fusion de la PR #86 annoncée comme un déploiement PROD ; l'owner corrige ; création de cette règle (1.0.0) |
| 2026-04-21 | PR monorepo #91 : `.claude/rules/deployment.md` aligné sur la 1.0.0 |
| 2026-05-18 | PR monorepo #590 : vocabulaire DEV / PREPROD / PROD et lint (ADR-075) |
| 2026-11-01 | 2.0.0 : PREPROD sur l'hôte PROD, sans `--admin` ni push direct, rollback PROD par le workflow ou par l'owner, six preuves |
| 2026-11-10 | 2.0.0 révisée avant sa fusion : fusion selon T6 amendée (ADR-121, ADR-123, ADR-124), pile PREPROD de cinq conteneurs, Caddyfile et mode break-glass du déploiement PROD, tags et branches recomptés |
| 2026-11-13 | 2.1.0 : garde de ref du workflow PROD (PR monorepo #2010), workflow renommé `release-prod.yml` et ancien chemin désactivé (#2046) ; D5 sans classification des anciens tags |

## Références

- [[ADR-075-deployment-topology-clarification]] — vocabulaire et topologie
- [[ADR-028-preprod-supabase-isolation]] — PREPROD en lecture seule
- [[ADR-101-vault-decides-canon-authority]] — le vault décide, le monorepo exécute
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] — G4 : écriture par PR
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts]] — D4 : la fusion appartient à l'owner
- [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte]] — fusion automatique dans un
  périmètre adopté puis activé
- [[ADR-124-premier-perimetre-fusion-automatique-monorepo]] — premier périmètre ; D7 : chaque fusion
  lance la chaîne PREPROD
- [[rules-technical]] (T6)
- [[rules-engineering-definition-of-done]] — DoD7 nomme le watcher du déploiement
