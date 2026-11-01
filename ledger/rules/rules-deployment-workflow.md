---
type: rules-document
status: canon
scope: deployment
updated: 2026-11-01
related_adrs: [ADR-028, ADR-075, ADR-101, ADR-102]
related_incidents: [INC-2026-007-false-prod-claim-on-main-merge]
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
- **Ne pas déployer PROD hors de `deploy-prod.yml`** : son chemin vérifie la preuve PREPROD et
  capture le point de rollback.
- **Ne pas lancer `Deploy PROD (via tag)` sur une branche.** Le `workflow_dispatch` l'accepte et
  déploierait le commit de tête de la branche, sans tag `v*` : la décision de l'owner n'aurait pas de
  preuve (D6). Le workflow ne le bloque pas (constat d'ADR-075).
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
5. `deploy-prod.yml`, avant toute mutation, refuse un commit sans ces trois jobs verts
   (`scripts/ci/prod-preprod-evidence.mjs`), capture l'image en service comme point de rollback et
   vérifie que `:sha-<commit>` porte le bon label `revision`. Il déplace ensuite `:production`,
   redémarre PROD et contrôle `/health` (`revision` égal au commit du tag).

## D5 — Rollback

| Environnement | Procédure |
|---|---|
| **PREPROD** | PR de revert du commit fautif, fusionnée selon D4.1. Le push `main` qui en résulte relance le cycle D1. Jamais de push direct ni de force-push sur `main`. |
| **PROD, pendant un déploiement** | Automatique : après le point de non-retour, tout échec déclenche `⏪ Rollback PROD`, qui redémarre l'image capturée avant la mutation. |
| **PROD, après un déploiement réussi** | Relancer `Deploy PROD (via tag)` (`workflow_dispatch`) sur le tag `v*` de la version à restaurer, dans les limites ci-dessous. |
| **PROD, workflow indisponible ou tag refusé** | Intervention manuelle de l'owner sur l'hôte PROD, par la console de l'hébergeur. Aucun agent ne modifie PROD ; lire son `/health` (D6) n'est pas une modification. |

Le run relancé exécute le `deploy-prod.yml` **du tag choisi**, pas celui de `main`. Ses contrôles
dépendent donc de l'âge du tag :

- tag qui contient les PR monorepo #1881 et #1884 (2026-10-24) : contrôles complets de D4.5, dont
  `/health` `revision` ;
- tag antérieur qui contient #1696 (2026-10-02) : preuve PREPROD et provenance de `:sha-<commit>`
  vérifiées ; ni contrôle de version servie, ni champ `revision` dans `/health`, donc pas de preuve
  D6 de la version servie ;
- tag antérieur à #1696 : son workflow promeut l'alias `:preprod` et s'arrête si son label
  `revision` diffère du commit du tag, avant de toucher `:production` et le conteneur PROD. Ligne
  « tag refusé ».

Ce chemin suppose aussi que `:sha-<commit>` est encore dans le registre et que le run `ci.yml` de ce
commit est lisible ; sinon le workflow refuse avant toute mutation.

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
`.github/workflows/deploy-prod.yml`, `docker-compose.preprod.yml` et
`scripts/ci/prod-preprod-evidence.mjs` du monorepo. `.claude/rules/deployment.md` transmet cette
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
