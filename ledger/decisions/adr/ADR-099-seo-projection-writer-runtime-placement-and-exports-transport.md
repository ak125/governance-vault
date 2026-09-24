---
id: ADR-099
title: "SEO Projection — lieu d'exécution du forward writer (conteneur PROD), transport des exports par le pin du sous-module, object-store sur l'hôte PROD, immuabilité write-once, rollout par drapeaux d'environnement : amende ADR-059 et ADR-090"
status: proposed
date: "2026-09-24"
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-059", "ADR-090"]
extends: []
related_adr: ["ADR-027", "ADR-028", "ADR-031", "ADR-032", "ADR-039", "ADR-055", "ADR-059", "ADR-090"]
related_rules: ["G1", "G2", "G3", "AP-10"]
related_incidents: []
version: "1.0.0"
---

# ADR-099 : SEO Projection — exécution du writer, transport des exports, object-store, immuabilité, rollout

- **Statut** : Proposed. La signature G3 et l'acceptation reviennent à l'owner.
- **Amende** :
  - **ADR-059** : §Snapshots immutables (lieu, backup, `chattr`) et §Rollout via GrowthBook ;
  - **ADR-090** : §A (localisation du writer) et §G (« Snapshot immutability »).
- **N'abroge rien.** Les contrats de payload, de 2-gate, de `wouldRegress` et de read-RPC (ADR-090
  §B à §F) restent inchangés. Les §Interdictions formelles d'ADR-059 aussi.
- **Méthode** : chaque écart ci-dessous a été constaté sur `main` du monorepo le 2026-09-24. Quand un
  ADR contredit l'état réel du dépôt, c'est le dépôt qui prime (CLAUDE.md, invariant 1).

## Contexte

La boucle `SCRAPING → RAW → WIKI → exports/seo → forward writer → DB versionnée → RPC → pages R*` est
codée jusqu'au writer. Le module NestJS `backend/src/modules/seo-projection/` est sur `main` : #1031,
#1033, #1282, #1299. Mais ADR-059 et ADR-090 laissent sans réponse, ou décrivent faussement, cinq
points qui empêchent de faire tourner ce writer sans bricolage :

| # | Ce que disent ADR-059 / ADR-090 | État réel sur `main` (2026-09-24) |
|---|---|---|
| 1 | Lieu d'exécution du writer : non spécifié (ADR-059 parle d'un « Backup VPS DEV », donc implicitement DEV) | `.github/workflows/wiki-exports-seo-generate.yml` (#1174) : le writer « DOIT s'exécuter sur un process TOUJOURS allumé = le conteneur PROD, JAMAIS sur DEV (`npm run dev`, intermittent) ». Le feeder documente sa vérification « SSH en PROD ». |
| 2 | Transport de `exports/seo` jusqu'au writer : non spécifié | Le writer lit `content/automecanik-wiki/exports/seo`, c'est-à-dire le sous-module `backend/content/automecanik-wiki` (`.gitmodules`). Rien ne faisait avancer son pin : `800a9d2`, qui ne porte que `.gitkeep`, contre `3cdd6ba` sur WIKI `main`, qui porte 3 exports gamme. Le `Dockerfile` ne copie aucun `content/`, et aucun checkout de `ci.yml` ne récupère les sous-modules. **L'image PROD ne contient aucun export.** |
| 3 | Object-store `/opt/automecanik/object-store/exports-snapshots/` | Défaut `OBJECT_STORE_ROOT_DEFAULT = '/opt/automecanik/object-store'` (`seo-projection.types.ts`). Aucun volume ne le monte dans `monorepo_prod` (`docker-compose.prod.yml`). Le répertoire n'existe pas sur la machine DEV. |
| 4 | « `chattr +i` post-write » | Le conteneur tourne en non-root (`USER remix-api`) et ne peut pas poser `chattr`. `atomicWrite` publie par `rename` sur `<sha256>.tar.zst` **à chaque run**, sans garde d'existence. Sur une archive déjà scellée, ce `rename` échoue en `EPERM` : un second run d'exports identiques échouerait. |
| 5 | Rollout via GrowthBook `seo_projection_read_v1` en % | GrowthBook n'est pas déployé. Mécanisme implémenté (`backend/src/config/feature-flags.service.ts`) : `SEO_PROJECTION_READ_V1` (maître, défaut `false`) et `SEO_PROJECTION_READ_CANARY` (jetons `<ROLE>@<entity_id>`, vide = fail-closed), clés présentes dans `ALLOWED_KEYS`. |
| 6 | ADR-090 §A : writer « frère de `replay_projection.py` sous `scripts/seo-projection/` » | Le writer est le module NestJS (writer, processors BullMQ write/refresh, feeder, producteur de snapshot TypeScript). Seuls les constantes et le layout sont partagés avec `replay_projection.py` (`SNAPSHOTS_SUBDIR = "exports-snapshots"`). |

**Erratum** : le corps d'ADR-090 porte encore la bannière « PROPOSÉ — numéro à confirmer au vault » et
« DRAFT vault — préparé en /tmp, NON appliqué », alors que son frontmatter dit `status: accepted`.
Le frontmatter fait foi, et le MOC le lit. La bannière est un vestige de préparation : cet ADR
l'enregistre sans réécrire le corps historique.

## Cohérence avec le canon existant

- **ADR-039** (accepted), « Décisions ouvertes » n° 1 : le mode d'intégration monorepo ↔ wiki
  (sous-module, sync explicite ou contrôle de hash) restait à trancher.
  - **D2 le tranche pour le seul flux `exports/seo` → forward writer** : c'est le sous-module.
  - La question du CI de validation des proposals, qui relève d'ADR-039 Phase 2, reste ouverte.
- **ADR-032** D5 (proposed, donc non normatif) décrit le même schéma pour le contenu diagnostic :
  sous-module, image construite avec son contenu au moment du build. D2 converge avec ce précédent
  sans le rendre normatif.
- Aucun ADR accepté ne place le writer sur DEV, n'exige GrowthBook pour ce flux ni ne fixe
  l'object-store ailleurs qu'ADR-059. Recherche faite dans `ledger/decisions/adr/` et `ops/rules/`
  sur « object-store », « seo_projection_read_v1 », « exports-snapshots », « forward writer » et
  « submodule ».

## Décision

### D1. Le forward writer s'exécute uniquement dans le conteneur PROD

- Seul le conteneur PROD (`monorepo_prod`) planifie le feeder et exécute le
  writer contre la DB partagée. Trois raisons :
  - le process doit être toujours allumé ;
  - la DB est partagée entre les environnements ;
  - il ne peut y avoir qu'un seul écrivain de `__seo_projection_runs` et du registre de snapshots.
- **DEV** : `SEO_PROJECTION_R1_FEED_ENABLED` reste absent ou `false`, et personne n'y appelle
  `POST /api/admin/seo-projection/feed/trigger*`. Même doctrine que la collecte GSC/GA4, qui a PROD
  pour unique collecteur (#1534).
- **PREPROD** (`READ_ONLY=true`, ADR-028) : le writer et le feeder y sont déjà un *skip* observable.
  Rien ne change.
- **Activation** : `SEO_PROJECTION_R1_FEED_ENABLED=true` dans l'environnement du conteneur PROD. C'est
  un acte owner, pris hors de cet ADR, après provisionnement de D3.

### D2. La version d'exports consommée est fixée par le pin du sous-module et livrée dans l'image

- **Autorité de version** : le gitlink `backend/content/automecanik-wiki` du commit monorepo déployé.
  Pas de montage d'un clone vivant du wiki, pas de `git pull` au runtime, pas de fetch réseau par le
  backend.
- **Avance du pin** : une PR Dependabot (écosystème `gitsubmodule`) **revue par un humain, jamais
  auto-fusionnée**. Son diff est le contenu qui sera projeté. La revue automatique Claude exclut ces
  branches (`dependabot/submodules/`).
- **Livraison** :
  - le build CI de l'image récupère le sous-module ;
  - le dépôt wiki est public, donc aucun secret n'est requis ;
  - le `Dockerfile` copie `exports/seo`, et **seulement** `exports/seo`, à l'emplacement que lit le
    writer ;
  - si la source manque, la copie échoue et le build avec elle (fail-closed, jamais d'image sans
    exports).
- **Conséquence** : la version d'exports en PROD est une fonction du tag `v*`. Rollback des exports =
  rollback du tag. `wiki_commit_sha` reste une métadonnée d'audit, et le replay continue de passer par
  le seul tar.zst (ADR-059 §Audit metadata vs replay authority, inchangé).
- **Côté DEV** : `scripts/ops/sync-dev-runtime.sh` aligne le sous-module sur le pin après chaque
  fast-forward. Contenu local, commit non publié ou dépôt injoignable : alerte, jamais d'écrasement.

### D3. L'object-store vit sur l'hôte PROD

- `/opt/automecanik/object-store` (hôte PROD) est monté en lecture-écriture dans `monorepo_prod`, **au
  même chemin**. Le défaut `OBJECT_STORE_ROOT_DEFAULT` ne change pas, et aucune variable n'est à
  poser.
- Le propriétaire est l'uid/gid du conteneur (`remix-api`). Le provisionnement (création, propriétaire,
  permissions) est un acte owner.
- **Le backup hors site part de l'hôte PROD.** Cela remplace « Backup VPS DEV → cron rsync »
  d'ADR-059. La cible (Storage Box) et la vérification des checksums restent celles d'ADR-059.
- **Aucun snapshot éphémère** : un run dont l'object-store n'est pas le volume persistant ne doit pas
  réussir. Le writer fait un `mkdir -p` avant d'écrire. La PR de packaging doit donc prouver qu'un
  conteneur sans ce volume fait échouer le run, observable dans `__seo_projection_runs`, au lieu
  d'écrire dans sa couche éphémère.

### D4. Immuabilité : write-once dans le writer, puis `chattr +i` côté hôte

- **Write-once (writer)** : aucun fichier publié sous `exports-snapshots/` n'est réécrit.
  - **Archive `<sha256>.tar.zst` déjà présente** : ses octets sont relus et hachés. S'ils
    correspondent, l'écriture est sautée : c'est la déduplication voulue par l'adressage par contenu.
    Sinon, le run échoue (fail-closed, marqué `failed`) : un fichier nommé par son hash qui ne porte
    pas ce hash est une corruption, jamais un cas à écraser.
  - **Manifest par run `<sha256>.<runId>.manifest.json`** : même règle. Un manifest existant n'est
    jamais réécrit.
- **Scellement (hôte)** : `chattr +i` est posé par l'hôte PROD, avec un privilège que le conteneur n'a
  pas (`CAP_LINUX_IMMUTABLE`). Il porte sur les fichiers publiés, jamais sur le répertoire, que le
  writer doit pouvoir continuer à remplir. Le mécanisme (tâche périodique ou job de backup) est un
  acte owner.
- **Ordre imposé** : le write-once est livré **avant** tout scellement. Sinon le premier run d'exports
  déjà snapshotés échoue en `EPERM`.

### D5. Le rollout de lecture passe par des drapeaux d'environnement et un canary par rôle

- Mécanisme réel, qui remplace le « % rollout GrowthBook » d'ADR-059 :
  - `SEO_PROJECTION_READ_V1` : maître, défaut `false`. S'il est OFF, aucune RPC n'est lue et le legacy
    est servi ;
  - `SEO_PROJECTION_READ_CANARY` : allowlist de paires `<ROLE>@<entity_id>`. Vide = fail-closed.
    L'identité est la **paire** : un GO R3 sur une gamme n'active jamais R4/R6 de la même gamme.
- **La progression est nominative et déterministe** (liste revue), pas un pourcentage tiré au hasard :
  chaque entité servie depuis la projection est nommée.
- **Les §GrowthBook d'ADR-059 sont sans objet tant que GrowthBook n'est pas déployé.** Leur invariant
  (« les pages ne bloquent jamais sur un lookup de flag ») est satisfait par construction : les flags
  sont lus dans l'environnement du process. Réintroduire GrowthBook sur ce flux exigerait un ADR.

### D6. Le writer est le module NestJS ; le contrat de run reste partagé avec le replay (erratum ADR-090 §A)

- Le forward writer est `backend/src/modules/seo-projection/`, et non un script frère sous
  `scripts/seo-projection/`.
- La contrainte d'ADR-090 §A demeure : le writer et `replay_projection.py` partagent le **même contrat
  de run**. Concrètement :
  - `__seo_projection_runs` ;
  - layout `exports-snapshots/` et manifest ;
  - ce que le writer écrit, le replay doit pouvoir le reconstruire depuis le tar.zst.
- La règle « no-refactor-libre » (revue @fafa, et ADR si le comportement change) s'applique au
  **producteur de snapshot TypeScript** (`seo-projection-snapshot.ts`) comme à `replay_projection.py`.

## Ce que cet ADR NE fait PAS

- **Il ne change rien** au payload R1, aux 2-gate, à `wouldRegress`, à l'outbox ni au GRANT anon du
  read-path (ADR-090 §B à §F).
- **Il ne crée** aucune table, aucune queue, aucun drapeau. Il ne fait que décrire ceux qui existent.
- **Il n'active rien.** L'activation du feeder, l'ajout d'entrées au canary et le tag PROD restent des
  actes owner séparés.
- **Il ne traite pas le diagnostic.** `diagnostic-content.service.ts` lit `wiki/` hors `exports/`, et
  ce contenu n'est pas embarqué dans l'image. R5 est en pause (ADR-027 et priorités) : hors périmètre.
- **Il ne touche** aucune URL, canonical, meta ni H1.
- **Il ne modifie pas le corps** d'ADR-059 ni celui d'ADR-090 (historique). Les amendements vivent ici.

## Conséquences

- **Positif** :
  - la version d'exports servie en PROD est déterministe, revue par un humain et rattachée au tag ;
  - un seul écrivain ;
  - les snapshots survivent aux redéploiements et restent compatibles avec le scellement ;
  - plus aucune dépendance à une machine intermittente (DEV).
- **Coût et latence** : un export validé au wiki n'atteint le writer PROD qu'après PR de bump, merge
  puis tag `v*`. C'est voulu, puisque l'humain reste dans la boucle.
- **Actes owner requis** avant la première écriture PROD :
  1. provisionner l'object-store sur l'hôte PROD ;
  2. mettre en place le backup hors site depuis l'hôte PROD, puis le scellement ;
  3. fusionner les PR monorepo (transport, packaging, write-once) ;
  4. poser le tag `v*` ;
  5. activer `SEO_PROJECTION_R1_FEED_ENABLED`.
- **Risque résiduel** : la taille de l'image croît avec `exports/seo`. C'est aujourd'hui de l'ordre du
  kilo-octet (3 exports gamme) : à surveiller à mesure que les gammes se multiplient.

## Mise en œuvre (monorepo, hors vault)

| Décision | Implémentation | État au 2026-09-24 |
|---|---|---|
| D2 (avance du pin, sync DEV) | Dependabot `gitsubmodule`, exclusion de la revue Claude, `sync_submodules()` | PR monorepo #1564 ouverte |
| D2 (livraison) et D3 (volume) | `ci.yml` récupère le sous-module, `Dockerfile` copie `exports/seo`, volume object-store dans `docker-compose.prod.yml` | à ouvrir |
| D4 (write-once) | garde d'existence et vérification sha256 dans `buildAndPublishSnapshot`, avec tests | à ouvrir |
| D1, D3 (hôte), D4 (scellement), D5 | actes owner | non commencés |

## Références

- [ADR-059 SEO Runtime Projection](ADR-059-seo-runtime-projection.md) (accepted, **amendé**)
- [ADR-090 SEO Projection Forward Writer Canon](ADR-090-seo-projection-forward-writer-canon.md) (accepted, **amendé**)
- [ADR-039 Wiki Frontmatter Zod Canon](ADR-039-wiki-frontmatter-zod-canon.md) (décision ouverte n° 1, tranchée pour `exports/seo`) · [ADR-032 Diagnostic/Maintenance unification](ADR-032-diagnostic-maintenance-unification.md) (D5, précédent proposé)
- [ADR-028 PREPROD Supabase isolation](ADR-028-preprod-supabase-isolation.md) (READ_ONLY Option D) · [ADR-055 SEO shadow mode](ADR-055-seo-shadow-mode-architecture.md) · [ADR-027 R5 → R3 S2_DIAG](ADR-027-r5-consolidation-into-r3-s2-diag.md) · [ADR-031 Four-Layer](ADR-031-four-layer-content-architecture.md)
- Monorepo `main` :
  - `backend/src/modules/seo-projection/` (writer, feeder, `seo-projection-snapshot.ts`) ;
  - `backend/src/config/feature-flags.service.ts` ;
  - `.github/workflows/wiki-exports-seo-generate.yml` (#1174) ;
  - `docker-compose.prod.yml` ; `Dockerfile` ; `.gitmodules` ;
  - `scripts/seo-projection/replay_projection.py`.
