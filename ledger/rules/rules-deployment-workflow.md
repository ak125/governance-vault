---
type: rules-document
status: canon
scope: deployment
updated: 2026-11-01
related_adrs: [ADR-028, ADR-075, ADR-101, ADR-102]
related_incidents: [INC-2026-007]
---

# Rules — Deployment Workflow (PREPROD par `main`, PROD par tag)

> **Version** : 2.0.0 | **Status** : CANON (règle du vault, normative au sens de G1)
> **État décrit** : `main` du monorepo au 2026-11-01 (`6ab7854c2adf15e3e588f8a73e4f9085ecaeee5d`)
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
| Fusion d'une PR sur `main` (push `main`) | `ci.yml` : `🐳 build` (via `build.yml`), puis `🧪 Deploy PREPROD`, `🎭 E2E Smoke Tests`, `🔦 Lighthouse Performance Audit` | `build.yml` publie `:sha-<commit>` et déplace l'alias `:preprod` | **PREPROD** : conteneur de CI sur l'hôte PROD, port 3200 sur la boucle locale, `READ_ONLY=true` | automatique, sans humain |
| Push d'un tag `v*`, ou `workflow_dispatch` de `Deploy PROD (via tag)` sur ce tag | `deploy-prod.yml` | promotion de `:sha-<commit du tag>` vers `:production` | **PROD** : conteneur live derrière Caddy | décision de l'owner : le tag |

- Aucun workflow ne déploie sur la machine DEV. Son runtime de développement suit `main` par
  resynchronisation (`scripts/ops/sync-dev-runtime.sh`, lancé par un cron).
- `ci.yml` se déclenche aussi sur un push `dev`, mais `build.yml` et `🧪 Deploy PREPROD` ne
  publient et ne déploient que depuis `main`. Au 2026-11-01, la branche `dev` n'existe pas sur le
  dépôt distant.
- Un push `main` qui modifie `scripts/monitoring/*.sh` lance aussi `deploy-monitoring-scripts.yml`,
  qui installe ces scripts dans `/usr/local/bin` de l'hôte PROD, hors des conteneurs. Ce n'est pas un
  déploiement d'environnement, mais la fusion d'une telle PR modifie l'hôte PROD.

## D2 — Règle mnémonique

> **`main` = PREPROD. `v*` = PROD.**

En cas de doute, lire le workflow, pas la documentation.

## D3 — Interdictions

- **Ne pas annoncer « déployé en PROD »** après une fusion sur `main` : la fusion déploie PREPROD.
- **Ne pas écrire « déployé » sans la version servie** de l'environnement (D6).
- **Ne pas pousser directement sur `main`** : la branche est protégée, tout passe par une PR (T6).
- **Ne pas contourner la protection de `main`** : une PR passe ses checks requis et ses règles de
  fusion, et un agent ne la fusionne jamais
  ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] D2). La fusion suit une validation
  manuelle explicite (T6). Cette règle ne prescrit plus `gh pr merge --admin`, qui passe outre les
  exigences de la protection, ni la désactivation d'un check.
- **Ne pas déployer PROD hors de `deploy-prod.yml`** : sur `main`, son chemin vérifie la preuve
  PREPROD et capture le point de rollback ; le workflow d'un ancien tag a ses propres limites (D5).
- **Ne lancer `Deploy PROD (via tag)` que sur un tag `v*`.** Le formulaire du `workflow_dispatch`
  propose `main` par défaut, et le run exécute le `deploy-prod.yml` de la ref choisie. Lancé sur
  `main` dont PREPROD a validé la tête, le workflow déploierait ce commit sans tag `v*` et
  publierait l'image sous `:main` : la décision de l'owner n'aurait pas de preuve (D6). Il ne le
  bloque pas (constat d'ADR-075). Sur une branche dont la tête est un commit de `main` qui contient
  #1696 et que PREPROD a validé, il ferait de même sous le nom de la branche si ce nom est un tag
  Docker valide (au plus 128 caractères parmi lettres, chiffres, `_`, `.` et `-`, sans `.` ni `-` en
  tête : donc ni `/` ni `+`) ; sinon il refuse au contrôle de ce nom, mais après avoir remplacé
  `:production-previous` (D5, #1288). Sur une autre ref, le résultat suit le workflow de cette ref,
  comme pour un tag (D5) : au 2026-11-01, 25 branches distantes en portent un sans garde de label ni
  preuve PREPROD. Sur 24 d'entre elles (nom avec `/`), le run s'arrête avant tout push, mais après
  avoir fait pointer le tag local `:production` de l'hôte du runner sur l'image `:preprod` ; sur la
  25e, il promeut l'alias `:preprod` courant vers PROD.
- **Ne pas utiliser le tag `latest`.** Un alias (`:preprod`, `:production`) ne sert pas de référence
  de version : citer le commit, le tag `v*` ou `:sha-<commit>`.

## D4 — Promotion PREPROD → PROD

1. Un humain fusionne la PR sous la protection de `main`, après validation manuelle explicite (T6) ;
   un agent ne fusionne jamais (ADR-102 D2).
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
   rollback (alias `:production-previous`, poussé au registre), vérifie que `:sha-<commit>` porte le
   bon label `revision` et la publie sous le nom du tag. Il déplace enfin `:production`, redémarre
   PROD et contrôle `/health` (`revision` égal au commit du tag).

## D5 — Rollback

| Environnement | Procédure |
|---|---|
| **PREPROD** | PR de revert du commit fautif, fusionnée selon D4.1. Le push `main` qui en résulte relance le cycle D1. Jamais de push direct ni de force-push sur `main`. |
| **PROD, pendant un déploiement** | Automatique : après le point de non-retour, tout échec déclenche `⏪ Rollback PROD`, qui redémarre l'image capturée avant la mutation. |
| **PROD, après un déploiement réussi** | L'owner relance `Deploy PROD (via tag)` (`workflow_dispatch`) sur le tag `v*` de la version à restaurer, dans les limites ci-dessous. |
| **PROD, workflow indisponible, tag refusé ou tag sans garde** | Intervention manuelle de l'owner sur l'hôte PROD, par la console de l'hébergeur. Aucun agent ne modifie PROD ; lire son `/health` (D6) n'est pas une modification. |

Le run relancé exécute le `deploy-prod.yml` **du tag choisi**, pas celui de `main`. Ses contrôles
dépendent donc des commits que contient le tag (302 tags `v*` au 2026-11-01 ; dates de fusion en
UTC) :

- tag qui contient les PR monorepo #1881, #1884 et #1887 (2026-10-24 et 2026-10-25 ; au 2026-11-01,
  seul le tag du 2026-10-30) : contrôles complets de D4.5, dont `/health` `revision` ;
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

Un tag qui contient #1288 (2026-07-18 ; 40 tags : les 14 qui contiennent #1696 et 26 de la classe
`ed10ec6e5`) réétiquette `:production-previous` sur l'image en service et le pousse avant de
vérifier la provenance de l'image : un run refusé à ce stade remplace le point de retour précédent.
Les 14, et 5 des 26 qui contiennent aussi #1598 (2026-09-29), vérifient d'abord la preuve PREPROD du
commit (`scripts/ci/prod-preprod-evidence.mjs`) : si le run `ci.yml` manque ou n'est pas lisible,
ils refusent avant toute mutation. Les 26 refusent ensuite sur le label de `:preprod`, selon leur
classe. Les 14 supposent aussi que `:sha-<commit>` est encore dans le registre : sans l'image, ils
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
`docker-compose.preprod.yml` et `scripts/ci/prod-preprod-evidence.mjs` du monorepo, ainsi que le
`deploy-prod.yml` de chaque tag `v*`. `.claude/rules/deployment.md` transmet cette
règle aux agents du monorepo ; un écart entre les deux est un constat (ADR-101 D3).

## Mapping historique

| Date | Événement |
|------|-----------|
| 2026-04-21 | Fusion de la PR #86 annoncée comme un déploiement PROD ; l'owner corrige ; création de cette règle (1.0.0) |
| 2026-04-21 | PR monorepo #91 : `.claude/rules/deployment.md` aligné sur la 1.0.0 |
| 2026-05-18 | PR monorepo #590 : vocabulaire DEV / PREPROD / PROD et lint (ADR-075) |
| 2026-11-01 | 2.0.0 : PREPROD sur l'hôte PROD, sans `--admin` ni push direct, rollback PROD par le workflow ou par l'owner, six preuves |

## Références

- [[ADR-075-deployment-topology-clarification]] (proposé) — vocabulaire et topologie
- [[ADR-028-preprod-supabase-isolation]] — PREPROD en lecture seule
- [[ADR-101-vault-decides-canon-authority]] — le vault décide, le monorepo exécute
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] — D2 : un agent ne fusionne jamais
- [[rules-technical]] (T6)
- [[rules-engineering-definition-of-done]] — DoD7 nomme le watcher du déploiement
