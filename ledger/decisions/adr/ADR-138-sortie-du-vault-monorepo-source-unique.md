---
id: ADR-138
title: "Sortie du vault : le monorepo devient la seule source de la gouvernance, le vault passe en archive (décisions 72 et 73) ; remplace ADR-015, amende dix-huit ADR et l'AEC (1.3.0)"
status: accepted
date: "2026-11-16"
decision_date: "2026-11-15"
decision_makers: ["@fafa"]
supersedes: ["ADR-015"]
superseded_by: []
amends: ["ADR-013", "ADR-020", "ADR-023", "ADR-048", "ADR-049", "ADR-053", "ADR-060", "ADR-061", "ADR-081", "ADR-101", "ADR-102", "ADR-120", "ADR-121", "ADR-123", "ADR-124", "ADR-125", "ADR-126", "ADR-127", "rules-agent-exit-contract"]
extends: []
related_adr: ["ADR-015", "ADR-031", "ADR-101", "ADR-102", "ADR-119", "ADR-121", "ADR-123", "ADR-124", "ADR-129"]
related_rules: ["AEC", "G1", "G3", "G4", "DoD2"]
related_incidents: []
reviewed_by: ""
version: "1.0.0"
---

# ADR-138 : sortie du vault, le monorepo devient la seule source

- **Statut** : Accepted. Les décisions sont celles de l'owner, décideur humain : Marwane. La
  décision 72 date du 2026-11-15 : le monorepo `ak125/nestjs-remix-monorepo` est la seule source de
  la gouvernance. La décision 73 suit : `ak125/governance-vault` passe en archive en lecture seule,
  une fois déplacé ce qui vit encore. La décision 103 (2026-11-16, 20:15 heure de Paris) demande la
  meilleure approche, sans bricolage. Rédigé par un agent (Claude Code CLI, machine DEV) sur le
  complément AR-4 du mandat AR. Le texte a été préparé sans signature : la signature des commits
  et la fusion sont des actes de l'owner. Canon applicable à la fusion par l'owner de la tête
  signée qui le porte, sous les contrôles requis
  ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] ; [[rules-vault|G1]] ;
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7). Avant cette fusion,
  ce statut décrit le candidat et ne modifie pas le canon de `main`.
- **Dernière PR de décision du vault.** Après elle, le vault ne reçoit plus que les PR techniques
  du plan de sortie (D5) ; aucune nouvelle décision n'y est écrite.
- **Corps des ADR amendés inchangé.** Seul leur frontmatter reçoit `amended_by: ["ADR-138"]`
  (ADR-015 : `status: superseded`, `superseded_by: ["ADR-138"]`). Le tableau de D6 dit, pour
  chacun, ce qui change et ce qui reste valable.

## Contexte

ADR-015 a fait du vault la source unique de la gouvernance, et ADR-101 a fait de ses ADR et de ses
règles le seul texte normatif. En pratique, la règle appliquée se lit déjà dans le monorepo : les
contrats de département sont vérifiés par schéma en CI
(`.spec/00-canon/ai-registry/agent-operating-map.yaml`), le classeur des circuits de fusion est
`scripts/ci/merge-circuit.mjs`, et le journal des principes
(`.claude/governance/journal-des-principes.md`) condense les 29 principes encore valables. Ces trois
pièces sont fusionnées sur `main` du monorepo depuis la PR ak125/nestjs-remix-monorepo#2093
(commit `f9e288348`, 2026-11-16 14:03:56 UTC). Deux textes se disent donc normatifs pour la même
règle : c'est une source concurrente.

Le relevé du 2026-11-16 (monorepo, `docs/audit/mandat-ar-20261116/`) donne le détail :
`tri-adr.md` (120 ADR lus, 19 en conflit avec les décisions 72 et 73), `inventaire-vault-et-plan.md`
(26 lecteurs du vault et plan de déplacement en 9 étapes), `contradictions.md` (23 lignes, groupes
A à F).

## Décision

### D1. Une seule source : le monorepo (décision 72)

Est normatif ce qui est fusionné sur `main` de `ak125/nestjs-remix-monorepo` : le journal des
principes, les contrats de département et les réglages vérifiés par schéma en CI. Une ADR du vault
n'est plus normative par elle-même. Elle reste l'archive de la raison d'une décision, et le
journal cite l'ADR d'où vient chaque principe. En cas d'écart, le journal prime ; l'écart est
signalé et corrigé par une PR du monorepo.

ADR-015 est remplacé. ADR-101 D1 (« seule une décision acceptée et non remplacée est normative »)
reste vrai pour lire l'archive ; pour la règle en vigueur, le critère devient « fusionné sur `main`
du monorepo ».

### D2. Un changement de règle = une PR du monorepo, fusion par circuit (décision 72)

Une règle, un principe ou un contrat change par une PR du monorepo. La fusion suit l'un des trois
circuits que calcule `scripts/ci/merge-circuit.mjs` (workflow `.github/workflows/merge-circuits.yml`) :
faible (CI verte), moyen (CI verte et verdict GO de la revue Claude sur la tête, décision 91), élevé
(approbation de l'owner sur la tête ; zones CODEOWNERS, risques `high`/`critical` d'`ownership.yaml`,
chemins non classés). Un agent ne fusionne jamais et n'arme jamais l'auto-fusion : seul le workflow
des circuits l'arme. Tant que l'owner n'a pas réglé la protection de `main` du monorepo pour ce
workflow, la porte d'ADR-124 reste celle qui s'applique.

### D3. Le vault devient une archive en lecture seule (décision 73)

L'archivage du dépôt est un acte de l'owner. Il vient en dernier, après le déplacement de ce que
le vault sert encore : l'AEC et sa distribution, la politique de fusion d'ADR-124, le vecteur JCS,
les bundles OPA. Jusqu'à l'archivage, ces lecteurs restent servis par le vault, et les mécanismes
internes du vault (lint, G2, G3) continuent de s'appliquer à ses propres PR.

### D4. AEC 1.3.0 : la source de l'AEC est nommée

L'AEC passe en 1.3.0 : seul le §« Distribution canonique » change, et son en-tête. La nouvelle
source est `.spec/00-canon/canon-distribution/rules-agent-exit-contract.md` dans
`ak125/nestjs-remix-monorepo`, avec son manifeste `.spec/00-canon/canon-distribution/canon-hashes.json`.
Le transfert a lieu à la fusion de l'étape 1 du plan (D5), corps identique à l'octet près. Avant ce
transfert, le document du vault reste la seule source. Après, il est figé. Il n'y a jamais deux
sources modifiables en même temps.

### D5. Ordre du déplacement

Le plan de `docs/audit/mandat-ar-20261116/inventaire-vault-et-plan.md` (monorepo) s'applique dans
son ordre : une étape = une PR prouvée, reçue par le pilotage avant la suivante.

1. AEC : source et manifeste dans le monorepo.
2. AEC : contrôles du monorepo rendus locaux, `canon-sync` retiré.
3. AEC : publication vers WIKI et RAW depuis le monorepo.
4. WIKI et RAW vérifient contre le monorepo.
5. Sort des pièces de la chaîne AEC dans le vault.
6. Politique de fusion d'ADR-124 déplacée **avant** l'archivage.
7. Vecteur JCS, bundles OPA, contrôle de coût Supabase, recherche des ADR citées.
8. Machine DEV et agents.
9. Archivage par l'owner.

### D6. ADR amendés ou remplacé : ce qui change, ce qui reste valable

| ADR | Effet | Ce qui change (décision 72 ou 73) | Ce qui reste valable |
|---|---|---|---|
| [[ADR-015-vault-single-source-of-truth\|015]] | remplacé | La source unique n'est plus le vault, et `CLAUDE.md` n'est plus un pointeur vers lui (D1). | L'idée d'une source unique, désormais le monorepo ; l'incident d'origine reste une archive. |
| [[ADR-013-agent-lifecycle-governance\|013]] | amendé | Les niveaux G1/G2 du cycle de vie renvoient au circuit de PR du vault : ils deviennent une PR du monorepo, fusionnée par circuit (D2). | Le cycle de vie des agents : création, activation et restructuration décidées, jamais implicites. |
| [[ADR-020-weekly-vault-lint\|020]] | amendé | Sans objet après l'archivage (D3). | Le lint s'applique aux PR du vault jusqu'à l'archivage. |
| [[ADR-023-hook-layer-defense\|023]] | amendé | La défense vise une copie locale du vault, qui n'est plus une source (D1, D3). | L'interdiction d'écrire une copie locale de la gouvernance (`app/.local/governance-vault/`) et la défense par hooks. |
| [[ADR-048-canon-enforcement-coverage\|048]] | amendé | Le registre REG-002 quitte le vault, vers le Repository Control Plane du monorepo (étape 7 de D5). | L'audit de couverture : toute règle déclarée a un contrôle nommé, ou l'absence est déclarée. |
| [[ADR-049-db-governance-canon-enforcement\|049]] | amendé | Même registre REG-002 (étape 7 de D5). | Les contrôles de gouvernance de la base qu'il recense. |
| [[ADR-053-planning-live-system\|053]] | amendé | Le MOC figé par ADR-104 reste dans l'archive (D3). | Rien de vivant : writer déjà retiré par ADR-104 ; la file de travail est celle d'ADR-128. |
| [[ADR-060-repository-roles-doctrine\|060]] | amendé | « Le vault décide », canon écrit par PR signée G3 au vault, le monorepo n'écrit jamais dans le vault : remplacé par D1 et D2. | Les rôles de RAW, WIKI, du RAG et du monorepo, et la chaîne RAW → WIKI → projections → consommateurs (amendée par ADR-119). |
| [[ADR-061-workspace-governance\|061]] | amendé | §3 : les canon-mirrors ne se synchronisent plus depuis le vault ; ils se génèrent depuis la source du monorepo (D4, étapes 1 et 2 de D5). | Frontière, cycle de vie et propriété des workspaces ; pas de mini-monorepo. |
| [[ADR-081-doctrine-agility-amendments\|081]] | amendé | G9 et G10 ne se lisent plus dans `rules-governance-process` du vault, mais dans le journal (principe P28). | Toute dérogation porte une clause d'expiration ; l'exploration a un budget borné. |
| [[ADR-101-vault-decides-canon-authority\|101]] | amendé | Le vault ne décide plus ; une règle ne se modifie plus par PR signée au vault (D1, D2). | D1 pour lire l'archive ; le rang des fichiers `.spec/00-canon/` (contrat s'ils sont lus par du code ou une CI, prose sinon) ; le retrait de `sync-canon.sh`. |
| [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4\|102]] | amendé | G4 (PR signée au vault, fusion humaine) ne s'applique plus aux changements de règle, et « un agent ne fusionne jamais » se lit avec les trois circuits (D2). | Airlock = RPC gate ; canal de bundles retiré ; canal unique branche + PR ; l'agent ne fusionne pas et n'arme pas la fusion. |
| [[ADR-120-dod2-preuve-de-revue-liee-au-sha\|120]] | amendé | La règle source de la DoD (`rules-engineering-definition-of-done`) devient une source du monorepo à son déplacement. | La preuve de revue est liée au SHA de tête (DoD2). |
| [[ADR-121-mandat-revue-decision-fusion-actes-distincts\|121]] | amendé | Les niveaux G1/G4 des règles du vault sont remplacés par D1 et D2. | Mandat, revue, décision et fusion sont des actes distincts ; le mandat couvre son exécution. |
| [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte\|123]] | amendé | Le périmètre adopté n'est plus une politique du vault : les trois circuits le remplacent une fois activés (D2). | D9 : avant de créer, on cherche l'existant ; les cas de refus de fusion automatique. |
| [[ADR-124-premier-perimetre-fusion-automatique-monorepo\|124]] | amendé | Sa politique (`ledger/policies/merge-perimeter.v1.json`) se déplace dans le monorepo avant l'archivage (étape 6 de D5), puis cède aux circuits. | La porte reste en place jusqu'à l'activation des circuits ; une PR ne s'autorise jamais elle-même. |
| [[ADR-125-amendements-cibles-coherence-wiki-seo-autorite\|125]] | amendé | La partie qui amende G1 de `rules-vault` est sans objet après l'archivage. | Tous les amendements WIKI/SEO : validation sur preuve, seuil 0.85, chemins WIKI au singulier, pilote R2. |
| [[ADR-126-obsidian-lecteur-facultatif-circuit-ecriture-unique\|126]] | amendé | Sans objet après l'archivage (D3). | Obsidian reste un lecteur facultatif tant que le vault vit, sans circuit d'écriture propre. |
| [[ADR-127-identite-wikilink-par-chemin-g2-liens\|127]] | amendé | Sans objet après l'archivage (D3). | La règle s'applique aux liens du vault jusqu'à l'archivage. |

## Options considérées

- **A. Laisser le vault normatif et ajouter le journal en copie** : deux sources pour une même
  règle. Rejeté (invariant 2 du `CLAUDE.md` du monorepo : pas de source concurrente).
- **B. Archiver le vault sans PR finale** : le dernier texte normatif du vault dirait encore qu'il
  est la source, et la porte d'ADR-124 lirait une politique qu'on ne pourrait plus changer. Rejeté.
- **C. Une dernière PR du vault qui acte la sortie, puis un déplacement par étapes prouvées**
  (retenue) : l'archive dit d'elle-même qu'elle n'est plus la source, et chaque lecteur est
  déplacé avant l'archivage.

## Ce que cet ADR ne fait pas

- Il ne déplace aucun fichier, ne modifie aucun workflow et n'archive rien : ce sont les étapes 1
  à 9 de D5.
- Il ne tranche pas le sort des ADR `deferred` (018, 057, 073) ni des numéros en PR ouverte : des
  verdicts sont proposés à l'owner dans la PR, sans décision.
- Il ne modifie aucune règle de l'AEC autre que le §« Distribution canonique ».

## Conséquences

- La fusion de cet ADR change le hash de distribution de l'AEC. `canon-publish.yml` émet
  `canon-updated` ; les copies déclarées (monorepo : PR `canon-sync/auto` ; WIKI et RAW : PR
  ordinaire) se mettent à jour. Les contrôles `agent-exit-contract-hash` des trois dépôts sont
  rouges jusqu'à ces PR de copie : c'est le comportement prévu par l'AEC.
- Le `CLAUDE.md` du monorepo est réservé à l'owner : son texte (ligne 5 et §Gouvernance) se met en
  accord par un correctif qu'il applique.

## Références

- Monorepo, PR ak125/nestjs-remix-monorepo#2093 (`f9e288348`) : journal des principes, contrats,
  circuits ; dossier `docs/audit/mandat-ar-20261116/`.
- [[ADR-015-vault-single-source-of-truth|ADR-015]], [[ADR-101-vault-decides-canon-authority|ADR-101]],
  [[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]], [[rules-agent-exit-contract]].
