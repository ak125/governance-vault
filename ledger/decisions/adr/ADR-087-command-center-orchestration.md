---
id: ADR-087
title: "Command Center — observatoire advisory vers orchestration gouvernée (lift ciblé de la pause new-control-plane)"
status: accepted
date: "2026-06-16"
decision_date: "2026-11-10"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: ["ADR-058", "ADR-085"]
related_rules: []
related_incidents: []
version: "1.0.0"
---

# ADR-087 — Command Center : observatoire advisory → orchestration gouvernée

## Statut et réconciliation (2026-11-10)

- **Statut** : Accepted (2026-11-10), borné aux phases 0 à 2. Le frontmatter portait
  `decision_date: 2026-06-16` alors que le statut restait `proposed` : aucun commit de ratification
  n'avait consigné cette décision. La date retenue est celle de la présente ratification. Statut
  arrêté sur délégation de l'owner (message du 2026-11-10 : appliquer la meilleure approche aux
  points ouverts de l'analyse du vault), dans une PR préparée par un agent (Claude CLI). La décision
  est consignée par la fusion, par l'owner, de la tête qui porte ce commit
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7). Avant cette fusion,
  ce statut décrit un candidat et ne modifie pas le canon de `main`.
- **Décision acceptée** : le Command Center passe d'observatoire consultatif à une orchestration
  gouvernée, par phases : 0 (consultatif), 1 (shadow, aucune écriture), 2 (exécution approuvée
  action par action par l'owner). La pause `new-control-plane` de la doctrine est levée pour ce seul
  périmètre ; tout autre control plane reste en pause.
- **Ce que l'acceptation n'active pas** : rien. Le mode se lit dans `COMMAND_CENTER_ORCHESTRATION`,
  vaut `off` par défaut et toujours `off` en production ; `auto` n'est pas implémenté. Chaque
  activation de phase reste un GO distinct de l'owner. La Phase 3 (exécution sans humain) demande un
  ADR séparé.
- **Livré** (présent dans le monorepo) :
  `backend/src/modules/admin/services/command-center-orchestrator/` (contrat, service, journal
  d'exécution, planificateurs, exécuteur), le test
  `backend/tests/unit/command-center-orchestrator.service.test.ts`, et
  `frontend/app/components/command-center/OrchestrationPanel.tsx`.
- **Corrections de ce texte** : le bandeau « DRAFT » est retiré et « Décision (proposée) » devient
  « Décision ». `amends` est vidé : cet ADR ne modifie aucun passage
  d'[[ADR-058-repository-control-plane|ADR-058]], il ajuste une entrée de doctrine ; ADR-058 reste
  dans `related_adr`. Les « Questions ouvertes » et la « Procédure si approuvé » sont gardées comme
  historique et annotées en place.
- **Non vérifié** : la valeur du flag en PREPROD et en PROD ; tout usage réel des phases 1 et 2.
- **Preuves** : monorepo `ak125/nestjs-remix-monorepo` à `fd80dd33e7b37a41d4400ce22ec218c14e4d69e3`
  (`origin/main` au 2026-11-10). Elles établissent la présence du code, pas ce qui est servi : ni la
  base, ni PREPROD, ni PROD n'ont été interrogées.

## Contexte

Le Command Center (`/admin/command-center`, plan `23-tait-groundable-et-giggly-fog.md`,
livré 2026-06-04) est **par conception un observatoire read-only** :

- Plan, verbatim : *« Read-only visualization of already-governed surfaces… **decides
  nothing, no new SoT, additive, warn-only** »*.
- Canon : *« AI Operating Map… **pas orchestrateur** »*.
- Il n'a pu être livré **que parce qu'il ne décide rien** — c'est ainsi qu'il **passe**
  la contrainte doctrine **`new-control-plane` : DO NOT start** (`top-priorities.md`).
- Sa sortie = une **OwnerActionQueue** qui **affiche** des actions (repair / wire /
  business / certification) que l'owner traite **à la main**. Zéro exécution.

**Intention owner (2026-06-16)** : le plan **doit diriger vers l'orchestration** —
c.-à-d. que le Command Center **exécute / coordonne**, au lieu de seulement conseiller.

## Problème (le conflit à trancher)

Orchestrer = **décider + exécuter** = **un control plane**. Or :

1. C'est l'inverse exact du principe fondateur du plan (« decides nothing »).
2. `new-control-plane` est **explicitement en pause** (doctrine).

Donc « faire diriger le plan vers l'orchestration » **n'est pas une suite du plan** :
c'est un **pivot stratégique** qui doit (a) lever la pause de façon ciblée, et (b) être
gardé pour rester safe. D'où cet ADR.

### Vérité inconfortable à acter (anti-bricolage)

**La file d'actions actuelle est advisory PARCE QUE ses actions sont, par nature, du
jugement / de la gouvernance — pas des mutations mécaniques :**

| Type d'action queue | Nature réelle | Auto-exécutable ? |
|---|---|---|
| `repair:*` / `wire:*` / `certification` | « certifier une source », « câbler un contrat », « définir un verdict de fiabilité » = **travail humain / ADR** | **Non** (jugement) |
| `seo:opportunity:*` (business) | « améliorer title/meta + maillage » = édition de contenu **sous invariants SEO** (no-touch-meta-if-optimized, R* canon) | **Non** (gouverné SEO) |
| `pricing:*` | touche la **marge** = economic governance, owner-gated | **Non** (gouverné pricing) |

⇒ **« Orchestrer » ne veut PAS dire « exécuter cette file telle quelle ».** Un vrai
orchestrateur a besoin d'une **nouvelle classe d'actions mécaniquement sûres et
réversibles** (ex. *régénérer un snapshot*, *déclencher un cron gouverné*, *poser un flag
gouverné*, *ouvrir une PR de proposition*), distinctes des actions de jugement actuelles.
Cet ADR pose le cadre ; l'énumération de ces actions exécutables est un livrable de Phase 1.

## Décision

**Lever la pause `new-control-plane` UNIQUEMENT pour le Command Center**, conditionnée à un
design **phasé, gated, shadow-first, réversible**, où **le canon décide toujours**
(l'orchestrateur coordonne des actions déjà gouvernées ; il n'invente aucune SoT).

### Conception phasée (chaque phase = un GO owner distinct ; flag `COMMAND_CENTER_ORCHESTRATION`)

| Phase | Flag | Ce qui se passe | Écriture ? |
|---|---|---|---|
| **0 — Advisory** *(actuel, livré)* | `off` (défaut) | la file s'affiche, l'owner agit à la main | **0** |
| **1 — Shadow-execute (dry-run)** | `shadow` | pour chaque action dotée d'un **contrat exécutable**, calcule + **simule** la mutation exacte qu'elle ferait, journalise dans un **execution-ledger** append-only ; l'owner revoit les effets *would-be* | **0** (dry-run) |
| **2 — Owner-approved execute (HITL)** | `approved` | une action n'est exécutée **que sur approbation explicite par-action** (clic owner), **seulement** pour des types **whitelistés + réversibles**, **via les modules/RPC gouvernés** (jamais de DML direct), guards en vigueur, rollback-handle stocké au ledger | mutation **gouvernée + réversible**, jamais autonome |
| **3 — Autonome-gardé** *(ADR séparé, plus tard)* | `auto` (défaut OFF) | seuls des types **bas risque, pleinement réversibles, observables** s'auto-exécutent sous SLO + kill-switch ; tout le reste reste HITL | borné + kill-switch |

### Garde-fous (invariants non négociables — repris du plan + doctrine)

- **Le canon décide** : l'orchestrateur ne coordonne que des actions déjà gouvernées ;
  aucune nouvelle SoT, aucune action hors du moteur `command-center-action-rules`.
- **Pessimisme préservé** : une action sur source **UNCERTIFIED / cassée** ne peut
  **jamais** être exécutée (le floor `finalizeAction` < 40 → certification reste). Pas de
  vert sur donnée cassée.
- **Réutiliser les guards existants** (jamais de nouveau control plane d'enforcement) :
  RPC Safety Gate (`callRpc`), `supabase-guard` G6 (pas de DML direct
  `pieces`/`pieces_price`/`__seo_*`), `payments/` intouchable, **jamais de mutation PROD
  sans tag `v*`**, `COMMAND_CENTER_MODE=disabled` en PROD par défaut.
- **No-silent-fallback** : toute tentative d'exécution (succès / échec / skip) journalisée
  au **execution-ledger** ; un échec **remonte**, jamais avalé.
- **Réversibilité obligatoire** : seuls les types d'action ayant un **inverse défini**
  sont exécutables ; le ledger stocke le rollback-handle. Idempotence + dédup (pas de
  double-exécution).
- **Kill-switch** : `COMMAND_CENTER_ORCHESTRATION=off` stoppe **instantanément** toute
  exécution ; **défaut OFF**. DEV/PREPROD d'abord ; PROD = décision owner séparée.

## Conséquences

- **+** Le cockpit ferme la boucle (observe → propose → **agit**), **dans** la gouvernance.
- **−/risque** : exécuter = vraies mutations. **Atténué** par shadow-first + HITL +
  réutilisation de **tous** les guards existants + kill-switch + réversibilité-only.
- **Doctrine** : `new-control-plane` est **amendée, pas supprimée** — levée **uniquement**
  pour ce Command Center scopé et gardé ; tout autre control plane reste en pause.

## Rollback

Flag → `off` (arrêt immédiat) ; revert des PRs du module orchestration ; le cockpit
advisory (Phase 0) **reste intact** dessous. Aucun état non réversible introduit par design.

## Questions ouvertes (à trancher par l'owner avant Phase 1)

> Note du 2026-11-10 : section gardée comme historique. La question 1 a sa réponse en
> Annexe A. Le numéro demandé par la question 2 est attribué (ADR-087) ; sa seconde moitié,
> la mise à jour du plan du monorepo, n'a pas été traitée. La phase shadow de la question 3
> est codée (flag `shadow`).

1. **Quels types d'actions** sont in-scope pour l'exécution en premier ? (cf. tableau :
   la plupart sont HITL par nature → la liste des actions *mécaniquement* exécutables est à
   définir, probablement courte : régen snapshot, déclenchement cron gouverné, pose de flag
   gouverné, ouverture de PR-proposition).
2. **Numéro d'ADR** (vault) + faut-il **aussi** mettre à jour le plan monorepo
   `23-tait-groundable-et-giggly-fog.md` (Phase 3 = orchestration) ?
3. Confirmer que **Phase 1 (shadow, 0 écriture)** est le bon premier pas (recommandé :
   oui — prouve la mécanique sans aucun risque, avant tout HITL).

---

## Annexe A — Énumération concrète des actions exécutables (réponse vérifiée à la Q1)

> Audit read-only du moteur `command-center-action-rules/*` + des surfaces gouvernées
> (2026-06-16). **Fait dur : les 4 types émis aujourd'hui sont 100 % du jugement.**

**A.1 — La file ACTUELLE n'a aucune action mécaniquement auto-exécutable :**

| Action émise | `action_type` | Pourquoi NON auto-exécutable |
|---|---|---|
| `repair:*`, `wire:*`, `seo:gsc-data-gap`, `pricing:wire-margin-thresholds` | `certification` / `repair` | « certifier / câbler / définir un verdict » = travail humain + ADR |
| `seo:opportunity:{product,content,other}` | `business` | édition title/meta + maillage **sous invariants SEO** (no-touch-meta, R* canon) |
| `pricing:sell-at-loss`, `pricing:missing-purchase` | `risk` | touche la **marge** = economic governance, owner-gated |

⇒ **Phase 1 ne « branche » pas la file existante** : elle introduit une **nouvelle petite
classe d'actions mécaniques**, distincte, à côté.

**A.2 — Candidats Phase 1 (shadow), classés par sûreté (vérifiés présents dans le repo) :**

| # | Action mécanique | Réversibilité | Blast radius | Verdict Phase 1 |
|---|---|---|---|---|
| 1 | **Régénérer un artefact généré** (ex. `build-command-center-snapshot.js`, idempotent `--check`) | **totale** (regen déterministe) | nul (projection) | ✅ **candidat shadow idéal** |
| 2 | **Ouvrir une PR-proposition** pour les `owner_action` déjà émis (ex. enum AJV `DROPPED_CAPABILITY`, 2 départements YAML de #1003) | totale (fermer la PR) | nul (0 mutation directe) | ✅ **candidat sûr** (HITL au merge) |
| 3 | **Déclencher un job observabilité gouverné** (ex. `quality-history-snapshot.service`, `seo-daily-fetch`) | partielle (écrit de l'observabilité, ignorable) | faible | 🟡 medium — shadow d'abord |
| 4 | **Flip de flag** (`SEO_CHAIN_R*_MODE`, `SUPPLIER_TRUTH_SYNC_ENABLED`) | totale (re-flip) | **ÉLEVÉ** (active des chaînes en pause) | ❌ **jamais auto** — reste owner-only |

**A.3 — Recommandation** : démarrer Phase 1 (shadow) sur **#1 et #2 uniquement** (régen
d'artefact + PR-proposition) — réversibilité totale, blast radius nul, et ça **prouve la
mécanique d'orchestration sans aucun risque**. Les jobs (#3) viennent en Phase 2 HITL ; les
flips de flag (#4) restent **exclus de l'orchestration automatique à vie** (décision owner
nominative, doctrine controlled-acceleration).

---

### Procédure si approuvé (rappel governance-vault-ops — l'owner exécute, pas l'assistant)

> Note du 2026-11-10 : procédure gardée comme historique, parce que
> [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] y renvoie. Elle n'est plus à
> suivre : `gov` est retiré, rien ne s'écrit dans le clone runtime, et un changement du vault
> passe par une PR signée préparée dans un worktree (ADR-102, G4 de [[rules-vault]]).

1. Assigner le numéro ADR, déplacer ce draft vers le vault (`/opt/automecanik/governance-vault`).
2. PR signée G3 dans `ak125/governance-vault` (commit `Good "git" signature`, single write point = Deploy VPS).
3. `./scripts/check-orphans.sh .` → 0 orphan ; lier dans le MOC ADR.
4. Après merge vault : `gov` (sync canon→vault) si un mirror `.spec/00-canon` est concerné.
5. **Seulement ensuite** : ouvrir le chantier code Phase 1 (shadow) en worktree, flag défaut OFF.
