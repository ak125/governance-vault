---
id: ADR-101
title: "Le vault décide : autorité des ADR et des règles du vault, rang des fichiers `.spec/00-canon/` du monorepo, correction des copies de règles legacy, retrait de sync-canon.sh — amende ADR-015 §5"
status: accepted
date: "2026-10-01"
decision_date: "2026-10-01"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-015"]
extends: []
related_adr: ["ADR-048", "ADR-049", "ADR-058", "ADR-060", "ADR-061", "ADR-062", "ADR-099"]
related_rules: ["G1", "G2", "G3", "G5", "T2", "T5", "T6", "T7"]
related_incidents: []
version: "1.0.0"
---

# ADR-101 : Le vault décide — autorité des ADR et des règles, rang des fichiers `.spec/00-canon/`

- **Statut** : Accepted (2026-10-01). La fusion par l'owner vaut ratification.
- **Amende** [[ADR-015-vault-single-source-of-truth|ADR-015]], §5 (« Canon architectural inchangé ») uniquement.
  Les points 1 à 4 d'ADR-015 restent en vigueur.
- **N'abroge rien d'autre.** Le programme d'[[ADR-048-canon-enforcement-coverage|ADR-048]] et
  d'[[ADR-049-db-governance-canon-enforcement|ADR-049]] continue. Seule la phrase de contexte d'ADR-048
  qui désigne le canon « par G1 + ADR-015 §5 » se lit désormais à travers cet ADR.
- **Méthode** : chaque constat ci-dessous a été vérifié le 2026-10-01 sur `main` du vault et sur
  `main` du monorepo (`4cb25b2c8`).

## Contexte

Deux doctrines contradictoires coexistent, toutes deux portées par des ADR acceptés :

| Source | Énoncé |
|---|---|
| ADR-015 §5, [[rules-vault]] G1, [[rules-governance-process]] G5 | `.spec/00-canon/` du monorepo fait foi. Le vault est un « miroir enrichi opérationnel, non normatif ». |
| [[ADR-060-repository-roles-doctrine|ADR-060]] (accepted 2026-05-13) | « vault décide, wiki valide, raw collecte, monorepo exécute, rag indexe et consomme ». Le vault porte les ADR, les règles et les policies ; le monorepo n'écrit jamais dans le vault. |
| `CLAUDE.md` du monorepo (état du 2026-10-01) | La gouvernance canon (ADR, règles, policies) vit au vault. Les documents legacy `.spec/00-canon/{architecture,rules,governance-policy}.md` n'ont aucune autorité courante. |

La pratique suit ADR-060 : depuis mai 2026, toutes les décisions sont prises en ADR dans le vault, et
le monorepo les applique. La contradiction a pourtant des effets concrets.

1. **Appliquée à la lettre, G1 ferait prévaloir `.spec/00-canon/rules.md` sur un ADR accepté.** Ce
   fichier est recopié mot pour mot dans [[rules-technical]] (T1-T7), et quatre de ses énoncés sont
   contredits par le code :

   | Règle | Énoncé | État de `main` du monorepo |
   |---|---|---|
   | T2 | « Tables : Prefixe `__` (ex : `__products`, `__orders`, `__users`) » | Schéma généré (`packages/database-types/src/supabase-generated.types.ts`) : 695 tables, dont 157 sans préfixe `__` (ex. `pieces`). Aucun des trois exemples n'existe. |
   | T5 | Exemple : `return signature === expectedSignature` ; retour Paybox vérifié par HMAC | Les retours SystemPay sont comparés par `timingSafeEqual` sur des tampons de même longueur (`cyberplus.service.ts`, `payment-validation.service.ts`). Le retour Paybox est vérifié par signature RSA avec la clé publique Paybox (`paybox-callback-gate.service.ts`). HMAC-SHA512 ne signe que la requête sortante (`paybox.service.ts`). |
   | T6 | « `main` = production automatique » | Un merge sur `main` redéploie le container PREPROD de CI (`ci.yml`). La PROD part d'un tag `v*` (`deploy-prod.yml`). |
   | T7 | « INTERDIT : Jest, Vitest » | Les tests backend tournent sous Jest (`backend/package.json`), les tests frontend sous Vitest (`frontend/package.json`), et `ci.yml` exécute les deux. |

2. **G5 est la copie de la règle R8 de `.spec/00-canon/governance-policy.md`** : « Seuls les fichiers
   dans `.spec/00-canon/` font autorité ». À la lettre, elle retire toute autorité aux ADR du vault.
3. **`_scripts/sync-canon.sh` copie le monorepo vers le vault**, à rebours de l'invariant 3
   d'ADR-060. Seuls les miroirs d'[[ADR-061-workspace-governance|ADR-061]] (`sync_canon_mirrors.py`)
   vont dans le bon sens, du vault vers le monorepo. Le script écrit en outre sous des chemins v1
   (`02-decisions/adr`, `03-rules/technical`, `06-knowledge`) que le check requis
   `No V1 Paths (ADR-015)` rejette. Il n'a plus tourné depuis le 2026-02-02 ([[sync-log]]).
4. **[[rules-vault]] décrit un outillage qui n'existe pas.** G2 cite `./scripts/check-orphans.sh`,
   alors que le script est `_scripts/check-orphans.sh`. G3 annonce « Branch protection :
   `require_signed_commits: true` ». En réalité, les signatures sont vérifiées par le check requis
   `G3: Commits signes` et par le hook pre-push ; l'état de la protection est documenté dans
   [[branch-protection]].

## Décision

### D1 — Le vault décide

Sont normatifs :

- les ADR du vault en `status: accepted`, sans `superseded_by` actif ;
- les règles du vault (`ledger/rules/rules-*.md`). Elles se modifient par PR signée (G3). Une
  modification qui change une décision passe par un ADR.

Un ADR `proposed`, `deprecated` ou `superseded` n'est pas normatif : c'est du contexte (historique,
chaînes `amends` / `supersedes`).

### D2 — Rang des fichiers `.spec/00-canon/**` du monorepo

Le monorepo exécute (ADR-060). Ses fichiers `.spec/00-canon/**` se rangent en deux catégories. Le
critère est l'état du dépôt, pas l'en-tête du fichier.

| Catégorie | Critère vérifiable | Autorité |
|---|---|---|
| **Contrat** | Consommé par du code, un générateur ou un check CI. Exemples : `role-matrix.md` (lu par le check `scripts/governance/validate-role-coherence.js`), `repository-registry/*.yaml` (lus par les générateurs de `@repo/registry`), `db-governance/sql-governance-rules.md` (check `spec-canon-sql-rule-r2-check.yml`). | Fait foi **dans son domaine**, en tant que contrat au sens d'ADR-062 ([[ADR-062-repository-contract-system-meta-model]]). Il ne peut pas contredire un ADR accepté. Une contradiction est un constat (D3). |
| **Prose de référence** | Aucun consommateur. Exemples : `architecture.md`, `rules.md`, `governance-policy.md`. | Aide à comprendre, ne tranche aucun conflit. Une mention « Status: CANON » dans son en-tête ne lui confère aucune autorité. |

[[REG-002-canon-files]] (ADR-048) inventorie ces états. S'il diverge du dépôt, le dépôt prime et
REG-002 se met à jour.

### D3 — Décision et fait ; une divergence est un constat

- **Ce qui doit être** est fixé par l'ADR accepté.
- **Ce qui est** se lit dans l'état du dépôt (`main`). Un ADR qui décrit faussement l'existant se
  corrige par amendement (précédent : [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]]).
- **Une divergence entre une décision et le code est un constat.** Elle se résout soit par une PR de
  code, qui aligne le code sur la décision, soit par un ADR qui amende la décision. Elle n'est jamais
  arbitrée en silence : un agent ne l'applique pas à l'aveugle et ne l'ignore pas, il la signale.

### D4 — Règles réécrites en conséquence

- [[rules-vault]] v3.0.0 : G1 devient « Le Vault Décide » (D1 à D3). Le chemin de G2 est corrigé.
  G3 décrit ce qui vérifie réellement les signatures. G4 n'est pas modifiée.
- [[rules-governance-process]] v3.0.0 : G5 devient « Autorité Documentaire » (D2).
- [[rules-technical]] v3.0.0 : T2, T5, T6 et T7 sont corrigées d'après les constats ci-dessus. La
  règle de fond reste (SDK Supabase, signatures vérifiées, validation avant merge, tests). Seuls les
  énoncés contredits par le code changent. Le fichier diverge désormais volontairement de
  `.spec/00-canon/rules.md`, qui reste de la prose de référence au sens de D2.

### D5 — Retrait de `_scripts/sync-canon.sh`

Le script est supprimé. La seule synchronisation entre le vault et le monorepo va du vault vers le
monorepo : `sync_canon_mirrors.py`, ADR-061 §3. `_scripts/gov`, qui appelait ce script sous un chemin
déjà inexistant (`./scripts/sync-canon.sh`), est traité avec l'Airlock dans un ADR séparé.

## Options considérées

- **A — Statu quo (deux doctrines).** Rejetée. Chaque agent arbitre seul une contradiction entre
  deux ADR acceptés. Les énoncés T5 et T7 poussent à écrire du code moins sûr ou à contourner les
  suites de tests existantes.
- **B — Revenir à G1 (le monorepo fait foi) et amender ADR-060.** Rejetée. Cela rendrait
  normative une prose que le code contredit (T2, T5, T6, T7). Cela contredirait aussi les décisions
  prises en ADR dans le vault depuis mai 2026, ainsi que le `CLAUDE.md` du monorepo.
- **C — Déclarer le vault normatif sans corriger ses copies.** Rejetée. Cela ratifierait les
  énoncés faux de `rules-technical` et la G5 qui nie l'autorité des ADR.
- **D — Le vault décide, rang des fichiers `.spec/00-canon/` fixé par leur consommation,
  correction des copies, retrait du script à rebours.** Retenue.

## Ce que cet ADR NE fait PAS

- **Il ne touche pas au monorepo.** Il ne réétiquette pas les documents legacy de
  `.spec/00-canon/` (zone owner). Il ne met pas à jour le skill `governance-vault-ops` du monorepo,
  qui énonce encore l'ancienne doctrine et cite `gov` et `./scripts/sync-canon.sh` : c'est un suivi
  monorepo.
- **Il ne traite ni G4, ni `_scripts/gov`, ni l'Airlock** ([[ADR-010-airlock-enforce-activation|ADR-010]]) :
  ADR séparé.
- **Il ne revérifie pas** T1, T3, T4, ni les sections « AI-COS Governance » et « Kill Switches » de
  [[rules-technical]], ni G6 à G9. Seuls les énoncés constatés faux sont corrigés.
- **Il ne réécrit pas les ADR passés** qui citent « G1 (Canon fait foi) » au sens « l'ADR est
  fusionné avant l'exécution ». La nouvelle G1 conserve ce sens.
- **Il ne change pas les checks `check-canon-*`.** Ils vérifient des références entre les deux
  dépôts, pas l'autorité. Seule la docstring de `check-canon-backlinks.py`, qui énonçait l'ancienne
  doctrine, est corrigée.

## Conséquences

### Positives

- Une seule doctrine, énoncée dans les règles et dans les fichiers d'instructions des agents
  (`CLAUDE.md`, `AGENTS.md`, onboarding).
- Les copies de règles ne prescrivent plus ce que le code contredit.
- Plus aucun script du vault ne synchronise dans le sens monorepo vers vault.

### Négatives

- `.spec/00-canon/rules.md` et `governance-policy.md` restent faux côté monorepo jusqu'à leur
  réétiquetage par l'owner. D2 les prive d'autorité en attendant.

### Neutres

- REG-002 garde son format. D2 donne une portée à ses états sans en changer la définition.

## Mise en œuvre (cette PR)

| Fichier | Changement |
|---|---|
| `ledger/decisions/adr/ADR-015-vault-single-source-of-truth.md` | `amended_by: ["ADR-101"]` (frontmatter seul, corps inchangé) |
| `ledger/rules/rules-vault.md` | v3.0.0 : G1, chemin G2, enforcement G3, checklist, sanctions, références |
| `ledger/rules/rules-governance-process.md` | v3.0.0 : G5 |
| `ledger/rules/rules-technical.md` | v3.0.0 : T2, T5, T6, T7, anti-patterns, checklist, en-tête |
| `_scripts/sync-canon.sh` | supprimé |
| `_scripts/check-canon-backlinks.py` | docstring seule |
| `CLAUDE.md`, `AGENTS.md`, `README.md`, `99-meta/onboarding/claude-desktop-instructions.md` | doctrine alignée sur D1 à D3 ; retrait de `sync-canon.sh` |
| `99-meta/{cron-setup,ci-policy,deploy-bot,governance-runtime-map,sync-log}.md`, `ops/moc/MOC-Governance.md`, `ops/moc/MOC-Rules.md`, `ledger/knowledge/README.md` | références à G1, G5 et `sync-canon.sh` mises à jour |
| `ops/moc/MOC-Decisions.md` | index régénéré (`sync_moc_decisions.py --write`) |

## Références

- [[ADR-015-vault-single-source-of-truth]], [[ADR-048-canon-enforcement-coverage]],
  [[ADR-060-repository-roles-doctrine]], [[ADR-061-workspace-governance]],
  [[ADR-062-repository-contract-system-meta-model]], [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport]]
- [[rules-vault]], [[rules-governance-process]], [[rules-technical]], [[REG-002-canon-files]]
