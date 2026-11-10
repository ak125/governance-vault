---
type: rules-document
status: canon
scope: deployment
updated: 2026-11-10
related_adrs: [ADR-028, ADR-075, ADR-101, ADR-102, ADR-121, ADR-123, ADR-124]
related_incidents: [INC-2026-007]
---

# Rules — Deployment Workflow (PREPROD par `main`, PROD par tag)

> **Version** : 2.0.0 | **Status** : CANON (règle du vault, normative au sens de G1)
> **État décrit** : `main` du monorepo au 2026-11-10 (`6eda5d6dd6c023ba4401186e99a27a098ae169b5`)
> **Incident racine** : [[2026-04-21-false-prod-claim-on-main-merge|INC-2026-007]], une fusion sur
> `main` annoncée comme un déploiement PROD.
> **2.0.0** : la 1.0.0 plaçait le déploiement de `main` sur la machine DEV et prescrivait
> `gh pr merge --admin`, un rollback par push direct sur `main` et un rollback PROD par SSH. Elle
> contredisait T6 ([[rules-technical]], corrigée par [[ADR-101-vault-decides-canon-authority|ADR-101]]) :
> `main` est protégée. Le vocabulaire suit [[ADR-075-deployment-topology-clarification|ADR-075]]
> (proposé).

---

## D1 — Déclencheurs

Deux déclencheurs, distincts et non substituables.

| Déclencheur | Workflow du monorepo | Image | Environnement | Validation |
|---|---|---|---|---|
| Fusion d'une PR sur `main` (push `main`) | `ci.yml` : `🐳 build` (via `build.yml`), puis `🧪 Deploy PREPROD`, `🎭 E2E Smoke Tests`, `🔦 Lighthouse Performance Audit` | `build.yml` publie `:sha-<commit>` et déplace l'alias `:preprod` | **PREPROD** : pile de CI sur l'hôte PROD (cinq conteneurs, ADR-075) ; application en `READ_ONLY=true`, sans accès direct à la base ; port 3200 de la boucle locale, publié par le proxy de la pile | automatique, sans humain |
| Push d'un tag `v*`, ou `workflow_dispatch` de `Deploy PROD (via tag)` sur ce tag | `deploy-prod.yml` | promotion de `:sha-<commit du tag>` vers `:production` | **PROD** : conteneur live derrière Caddy | décision de l'owner : le tag |

- Aucun workflow ne déploie sur la machine DEV. Son runtime de développement suit `main` par
  resynchronisation (`scripts/ops/sync-dev-runtime.sh`, lancé par un cron).
- `ci.yml` se déclenche aussi sur un push `dev`, mais `build.yml` et `🧪 Deploy PREPROD` ne
  publient et ne déploient que depuis `main`. Au 2026-11-10, la branche `dev` n'existe pas sur le
  dépôt distant.
- `ci.yml` ne filtre pas les chemins : toute fusion sur `main` lance le cycle PREPROD complet, y
  compris celle d'une PR de documentation et celle qu'exécute une porte de fusion automatique
  ([[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]] D7).
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
- **Ne pas déployer PROD hors de `deploy-prod.yml`** : sur `main`, son chemin vérifie la preuve
  PREPROD et capture le point de rollback ; le workflow d'un ancien tag a ses propres limites (D5).
- **Ne lancer `Deploy PROD (via tag)` que sur un tag `v*`.** Le formulaire du `workflow_dispatch`
  propose `main` par défaut, et le run exécute le `deploy-prod.yml` de la ref choisie. Lancé sur
  `main` dont PREPROD a validé la tête, le workflow déploierait ce commit sans tag `v*` et
  publierait l'image sous `:main` : la décision de l'owner n'aurait pas de preuve (D6). Il ne le
  bloque pas (constat d'ADR-075). Sur une branche dont la tête est un commit de `main` qui contient
  #1696 et que PREPROD a validé, il ferait de même sous le nom de la branche si ce nom est un tag
  Docker valide (au plus 128 caractères parmi lettres ASCII, chiffres, `_`, `.` et `-`, sans `.` ni
  `-` en tête : donc ni `/` ni `+`) ; sinon il refuse au contrôle de ce nom, mais après avoir
  remplacé `:production-previous` (D5, #1288). Sur une autre ref, le résultat suit le workflow de
  cette ref, comme pour un tag (D5) : au 2026-11-10, 25 branches distantes en portent un sans garde
  de label ni preuve PREPROD. Sur 24 d'entre elles (nom avec `/`), le run s'arrête avant tout push,
  mais après avoir fait pointer le tag local `:production` de l'hôte du runner sur l'image
  `:preprod` ; sur la 25e, il promeut l'alias `:preprod` courant vers PROD.
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
5. `deploy-prod.yml` refuse d'abord, sans rien modifier, un commit sans ces trois jobs verts
   (`scripts/ci/prod-preprod-evidence.mjs`). Il capture ensuite l'image en service comme point de
   rollback : son identifiant, épinglé pour le run, et l'alias `:production-previous`, poussé au
   registre (un échec de ce push n'arrête pas le run). Il vérifie que `:sha-<commit>` porte le bon
   label `revision` et la publie sous le nom du tag. Passé le point de non-retour, il déplace
   `:production`, charge le Caddyfile du commit (`scripts/ci/prod-caddy-config.sh` : fichier validé
   dans le Caddy en service avant d'être écrit, Caddy recréé seulement si le fichier a changé),
   remplace le conteneur PROD et contrôle `/health` (`revision` égal au commit du tag).
6. Si le conteneur PROD est absent de l'hôte, il n'y a pas d'image à capturer : le workflow refuse
   avant toute mutation. Le mode `break_glass_no_rollback_point` (entrée du `workflow_dispatch`, ou
   variable de dépôt `PROD_BREAK_GLASS_NO_ROLLBACK_POINT` pour un push de tag) lève ce refus : le
   run déploie alors **sans point de rollback** (D5). C'est une décision de l'owner, prévue pour un
   premier déploiement ou un hôte reconstruit.

## D5 — Rollback

| Environnement | Procédure |
|---|---|
| **PREPROD** | PR de revert du commit fautif, fusionnée selon D4.1. Le push `main` qui en résulte relance le cycle D1. Jamais de push direct ni de force-push sur `main`. |
| **PROD, pendant un déploiement** | Automatique : après le point de non-retour, tout échec déclenche `⏪ Rollback PROD` (`scripts/ci/prod-rollback.sh`), qui remet `:production` sur l'image capturée avant la mutation et la redémarre. Il ne restaure que l'image : un Caddyfile chargé par ce déploiement reste en place. En mode break-glass (D4.6), aucune image n'a été capturée : l'étape échoue et renvoie à l'intervention manuelle (dernière ligne). |
| **PROD, après un déploiement réussi** | L'owner relance `Deploy PROD (via tag)` (`workflow_dispatch`) sur le tag `v*` de la version à restaurer, dans les limites ci-dessous. |
| **PROD, workflow indisponible, tag refusé ou tag sans garde** | Intervention manuelle de l'owner sur l'hôte PROD, par la console de l'hébergeur. Aucun agent ne modifie PROD ; lire son `/health` (D6) n'est pas une modification. |

Le run relancé exécute le `deploy-prod.yml` **du tag choisi**, pas celui de `main`. Ses contrôles
dépendent donc des commits que contient le tag (303 tags `v*` au 2026-11-10 ; dates de fusion en
UTC) :

- tag qui contient les PR monorepo #1881, #1884 et #1887 (2026-10-24 et 2026-10-25 ; au 2026-11-10,
  deux tags : ceux du 2026-10-30 et du 2026-11-05) : contrôles de D4.5, dont `/health` `revision`,
  sauf le chargement du Caddyfile par `prod-caddy-config.sh` (#1961, 2026-11-05), qu'aucun tag ne
  contient encore. Le workflow de ces deux tags arrête et supprime Caddy avec le conteneur PROD,
  puis les recrée ensemble : le site ne répond pas pendant le remplacement ;
- tag qui contient #1696 (2026-10-02) mais pas #1881 (13 tags) : preuve PREPROD et provenance de
  `:sha-<commit>` vérifiées ; ni contrôle de version servie, ni champ `revision` dans `/health`, donc
  pas de preuve D6 de la version servie ;
- tag qui contient le commit monorepo `ed10ec6e5` (2026-04-21) mais pas #1696 (94 tags) : son
  workflow s'arrête si le label `revision` de l'alias `:preprod` diffère du commit du tag, avant de
  toucher `:production` et le conteneur PROD. L'alias suit `main` : le refus est la règle dès qu'un
  commit plus récent a été construit. Ligne « tag refusé » ;
- tag qui ne contient pas `ed10ec6e5` (194 tags) : **aucune garde de provenance** ; après le
  déploiement, seuls des contrôles d'exécution (conteneur démarré, réponses HTTP dont `/health`)
  vérifient l'état de PROD, jamais la version servie. Son workflow promeut l'alias `:preprod`
  courant vers `:production`, le pousse sous le nom du tag (ce qui écrase le tag Docker de la
  version d'origine) et redémarre PROD, quel que soit le commit de l'alias. Le rollback automatique
  de 39 d'entre eux revient à `:production-previous`, copié de `:production` après la promotion : il
  redémarre l'image promue. Ne jamais le relancer : ligne « tag sans garde ».

Un tag qui contient #1288 (2026-07-18 ; 41 tags : les 15 qui contiennent #1696 et 26 de la classe
`ed10ec6e5`) réétiquette `:production-previous` sur l'image en service et le pousse avant de
vérifier la provenance de l'image : un run refusé à ce stade remplace le point de retour précédent.
Les 15, et 5 des 26 qui contiennent aussi #1598 (2026-09-29), vérifient d'abord la preuve PREPROD du
commit (`scripts/ci/prod-preprod-evidence.mjs`) : si le run `ci.yml` manque ou n'est pas lisible,
ils refusent avant toute mutation. Les 26 refusent ensuite sur le label de `:preprod`, selon leur
classe. Les 15 supposent aussi que `:sha-<commit>` est encore dans le registre : sans l'image, ils
refusent avant de toucher `:production` et le conteneur PROD, mais après la capture. Après un tel
refus, l'intervention manuelle ne s'appuie pas sur `:production-previous` ; elle désigne l'image à
restaurer par le tag Docker poussé à son déploiement (nom du tag `v*`), ou par `:sha-<commit>` si
cette image est encore dans le registre.

Un revert sur `main` ne change pas PROD : il redéploie PREPROD. PROD ne change que par D4 ou par une
ligne de ce tableau.

## D6 — Six objets, six preuves

| Objet | Preuve | Ne prouve pas |
|---|---|---|
| Commit sur `main` | SHA de 40 caractères, commit de fusion de la PR | qu'une image existe ou qu'elle soit déployée |
| Tag `v*` | `git tag --points-at <sha>` | que le déploiement PROD ait réussi |
| Image | identifiant d'image et label `org.opencontainers.image.revision` de `:sha-<commit>` | qu'elle tourne ; un alias ne désigne pas une version |
| Environnement | son rôle (ADR-075 D2) | la version qu'il sert |
| Preuve CI | jobs en `success` sur le run `ci.yml` du commit, run `deploy-prod.yml` en `success` | que la version soit encore servie |
| Version servie | `/health` de l'environnement, `revision` égal au SHA attendu, lu et daté | quoi que ce soit sur un autre environnement |

Sources : `.github/workflows/ci.yml`, `.github/workflows/build.yml`,
`.github/workflows/deploy-prod.yml`, `.github/workflows/deploy-monitoring-scripts.yml`,
`docker-compose.preprod.yml`, `scripts/ci/prod-preprod-evidence.mjs`,
`scripts/ci/prod-caddy-config.sh` et `scripts/ci/prod-rollback.sh` du monorepo, ainsi que le
`deploy-prod.yml` de chaque tag `v*`. `.claude/rules/deployment.md` transmet cette
règle aux agents du monorepo ; un écart entre les deux est un constat (ADR-101 D3).

## Mapping historique

| Date | Événement |
|------|-----------|
| 2026-04-21 | Fusion de la PR #86 annoncée comme un déploiement PROD ; l'owner corrige ; création de cette règle (1.0.0) |
| 2026-04-21 | PR monorepo #91 : `.claude/rules/deployment.md` aligné sur la 1.0.0 |
| 2026-05-18 | PR monorepo #590 : vocabulaire DEV / PREPROD / PROD et lint (ADR-075) |
| 2026-11-01 | 2.0.0 : PREPROD sur l'hôte PROD, sans `--admin` ni push direct, rollback PROD par le workflow ou par l'owner, six preuves |
| 2026-11-10 | 2.0.0 révisée avant sa fusion : fusion selon T6 amendée (ADR-121, ADR-123, ADR-124), pile PREPROD de cinq conteneurs, Caddyfile et mode break-glass du déploiement PROD, tags et branches recomptés |

## Références

- [[ADR-075-deployment-topology-clarification]] (proposé) — vocabulaire et topologie
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
