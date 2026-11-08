---
id: ADR-123
title: "Exécution automatique conditionnelle de la fusion dans un périmètre adopté — amende ADR-102, ADR-120, ADR-121, G4, RULE-H5/H6, DoD2, AEC et T6 ; delta distinct sur Q2 et Q4"
status: accepted
date: "2026-11-07"
decision_date: "2026-11-08"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-102", "ADR-120", "ADR-121", "rules-vault", "rules-engineering-definition-of-done", "rules-agent-exit-contract", "rules-technical", "rules-engineering-quality"]
extends: []
related_adr: ["ADR-013", "ADR-099", "ADR-101", "ADR-119"]
related_rules: ["AEC", "DoD2", "G4", "T6", "Q2", "Q4"]
related_incidents: []
version: "1.0.0"
---

# ADR-123 : exécution automatique conditionnelle de la fusion dans un périmètre adopté

- **Statut** : Accepted (2026-11-08). Décision de l'owner, décideur humain : Marwane, sur le
  candidat de cette PR (`a3334fb6972ba26f7ecfb5d4e83385f01e57b724`). Les textes repris au §Texte
  approuvé, le paragraphe T6 et les textes Q2 et Q4 sont des décisions de l'owner du 2026-11-03 ;
  ils ne sont pas soumis à une nouvelle approbation de fond. Cet ADR les transcrit le 2026-11-07,
  à la reprise du lot par un agent (Claude CLI), sur mandat de l'owner porté par le département 02
  et coordonné par le département 23. Le commit de ratification est préparé par un agent : son
  auteur et sa clé de signature sont techniques. Canon applicable à la fusion par l'owner de la
  tête qui porte cette décision, sous les contrôles requis (D8 ;
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7) ; avant cette fusion,
  ce statut décrit le candidat ratifié et ne modifie pas le canon de `main`.
- **Modifie**, sur les seuls passages listés en §Amendement : G4 de [[rules-vault]] (3.2.0 →
  3.3.0), RULE-H5 et RULE-H6 de [[GOVERNANCE-HUMAN]], DoD2 de
  [[rules-engineering-definition-of-done]] (1.2.0 → 1.3.0), [[rules-agent-exit-contract]]
  (1.1.0 → 1.2.0), T6 de [[rules-technical]] (3.0.0 → 3.1.0), Q2 et Q4 de
  [[rules-engineering-quality]] (1.1.0 → 1.2.0). Lecture amendée de D2 à D5 et D7 d'ADR-121, de D2
  et D3.2 d'[[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] et de D1
  d'[[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]] ; leurs corps restent inchangés, seul leur
  frontmatter reçoit `amended_by`.
- **N'active rien** : aucun périmètre n'est adopté ni activé par cet ADR. Tant qu'il n'y en a pas,
  toute fusion suit le circuit en vigueur (ADR-121 D4).
- **Méthode** : constats en lecture seule le 2026-11-07 sur `main` du vault au commit
  `a1d004c01590f3f27744f34377c44433325bffab`. Identifiant vérifié le même jour, faute de générateur
  natif sur `main` : `main` s'arrête à ADR-121 ; ADR-122 n'existe que dans la PR ouverte #392 ; aucun
  ADR-123 ou supérieur sur une branche distante, une PR ouverte ou un brouillon local. Effets
  couplés constatés sur les workflows du vault et du monorepo (§Effets couplés).

## Contexte

### C1 — La fusion par l'owner est écrite comme une interdiction universelle

ADR-102 D2 (« Un agent ne fusionne jamais »), G4.2 de [[rules-vault]], ADR-121 D4, RULE-H6, DoD2
point 6 et son anti-pattern, ainsi que les points 2 et 4 de la distribution de l'AEC, réservent
l'exécution de toute fusion à l'owner. Aucun ne prévoit qu'une décision autorisée puisse être
exécutée par un mécanisme dans un périmètre adopté.

### C2 — T6 garde sa formulation initiale

T6 de [[rules-technical]] termine son exemple par « ATTENDRE validation manuelle », puis
`gh pr merge` « APRES approbation explicite uniquement ». La lecture laisse un agent fusionner après
un accord, contrairement à ADR-121 D4, dont la mise en œuvre prévoyait l'alignement de T6.

### C3 — Q2 et Q4 imposent des quotas et des créations automatiques

Q2 fixe des quotas (« ≥ 3 patterns », « 2-3 patterns », « 70% ») et prend un résultat nul pour une
preuve d'absence. Q4 « attend » une modernisation et associe à ses triggers une PR, une issue ou un
ADR, y compris hors du mandat de la session.

## Principe directeur

Décider et exécuter sont deux actes. Une automatisation exécute une décision autorisée ; elle ne la
prend pas et ne lève aucune condition.

## Texte approuvé

Décision de l'owner du 2026-11-03, reproduite sans modification :

> Le département pilote conserve le besoin, les critères de réception et le suivi unique du dossier. Le département 23 coordonne le routage des demandes vers la session Claude responsable et la réception des preuves, sans reprendre les lots actifs ni créer un second suivi. Le département 02 porte les amendements de gouvernance ; le département 21 vérifie le fonctionnement technique des mécanismes autorisés. Claude CLI reste l’exécutant des modifications du dépôt.
>
> Toutes les catégories de PR, y compris les règles et décisions de gouvernance, peuvent être éligibles à l’exécution automatique de leur fusion dans un périmètre explicitement adopté.
>
> Cette automatisation exécute une décision autorisée ; elle ne remplace pas les décisions humaines de gouvernance ni les validations spécifiques maintenues. Pour les changements ordinaires, une politique approuvée peut définir une autorisation préalable par catégorie. Pour une décision de gouvernance, l’adoption humaine du contenu doit être tracée avant la fusion.
>
> La fusion reste conditionnée au périmètre autorisé, à la tête identifiée, aux contrôles et revues applicables et aux protections du dépôt. Un changement de tête impose de réévaluer les preuves affectées ; une condition manquante ou un contrôle non concluant empêche la fusion. Aucun contournement de protection n’est permis.
>
> L’autorisation, la tête fusionnée, le compte exécutant et le résultat sont conservés dans les traces existantes. La fusion n’autorise ni synchronisation des consommateurs, ni déploiement, ni intervention PROD.
>
> Le 02 prépare les amendements cohérents des textes concernés ; le 21 et le 23 qualifient le mécanisme existant à réutiliser. L’activation technique fait l’objet d’un périmètre explicite après adoption et vérification du dispositif.

## Décisions

### D1 — Rôles : le décideur et le processus qui exécute sont distincts

Les rôles sont ceux du premier paragraphe du texte approuvé. L'owner reste le décideur
(`decision_makers`) ; le mécanisme qui exécute une fusion n'en décide pas. Les départements et les
sessions sont nommés séparément selon ADR-121 D8.

### D2 — Éligibilité dans un périmètre explicitement adopté puis activé

Toute catégorie de PR, règles et décisions de gouvernance comprises, peut être éligible. Contenu
minimal proposé, à confirmer à l'adoption du premier périmètre (§Points à décider) : un périmètre
adopté nomme les dépôts et branches cibles, les catégories couvertes,
l'autorisation applicable à chacune (D3), la forme de la trace d'adoption des décisions de
gouvernance qu'aucun ADR ne porte (D3), le mécanisme existant, le compte qui exécute et l'acte
qui l'arme, et les traces (D5). Hors d'un périmètre adopté puis activé (D7), rien n'est éligible.
L'éligibilité d'une catégorie (par exemple `canon-sync` ou Dependabot) n'en autorise pas le
déclenchement.

### D3 — Autorisation

- **Changement ordinaire** : autorisation préalable par catégorie, dans une politique approuvée par
  l'owner.
- **Décision de gouvernance** (ADR, règle, policy) : adoption humaine du contenu, tracée avant la
  fusion ; pour un ADR, le commit de ratification (ADR-121 D7) ; pour un autre changement, dans la
  forme que fixe le périmètre activé (D2).
- **Validations spécifiques maintenues** : elles restent requises et ne sont pas remplacées,
  notamment le niveau C de DoD2 (accord nominatif avant la fusion, ADR-120), les niveaux G1 et G2
  d'[[ADR-013-agent-lifecycle-governance|ADR-013]], les actes humains qu'ADR-119 D7 maintient
  (validation d'une plage chiffrée, autorité d'une source inconnue, flip `diagnostic_safe` et
  `reviewed`, relectures de sécurité du diagnostic et des relations) et la revue humaine des avances
  de pin d'ADR-099 D2.

Le compte ou le geste de fusion ne prouve pas la décision humaine (ADR-121 D4).

### D4 — Conditions, réévaluation et refus

La fusion exige ensemble : le périmètre autorisé, la tête identifiée (fusion épinglée sur le SHA),
les contrôles et revues applicables (enregistrement DoD2 de cette tête) et les protections du
dépôt. Un changement de tête impose de réévaluer les preuves affectées (DoD2 point 4). Une condition
manquante ou un contrôle non concluant empêche la fusion. Aucun contournement de protection n'est
permis. Cas de refus que le mécanisme activé devra démontrer avant toute activation (D7) :

| Cas | Effet |
|---|---|
| Autorisation absente, ou catégorie hors politique | pas de fusion |
| Tête changée depuis l'autorisation ou la revue | pas de fusion avant réévaluation des preuves affectées |
| Contrôle requis absent, en échec ou non concluant | pas de fusion |
| Protection du dépôt non satisfaite | pas de fusion ; aucun contournement |
| Adoption humaine d'une décision de gouvernance non tracée avant la fusion | pas de fusion |
| Lot suspendu ou mis en pause | pas de fusion |
| Effet PROD non autorisé (tag `v*`, déploiement, mutation) | pas de fusion |

### D5 — Trace

L'autorisation, la tête fusionnée, le compte qui exécute et le résultat sont conservés dans les
traces existantes (PR, enregistrement DoD2, historique des fusions du dépôt). Cet ADR ne crée
aucune trace, identité, bot ou label.

### D6 — Aucun effet au-delà de la fusion

La fusion n'autorise ni synchronisation des consommateurs, ni déploiement, ni intervention PROD.
Les effets couplés existants (§Effets couplés) restent à évaluer dans chaque périmètre avant son
activation : une fusion sur `main` du monorepo lance la chaîne PREPROD ; une modification de l'AEC
sur `main` du vault déclenche `canon-publish` puis, côté monorepo, la PR `canon-sync/auto` ; un tag
`v*` reste la décision PROD de l'owner.

### D7 — Activation séparée

Le 02 prépare les amendements ; le 21 et le 23 qualifient le mécanisme existant à réutiliser.
L'activation technique fait l'objet d'un périmètre explicite, après l'adoption de cet ADR et la
vérification du dispositif, y compris de ses cas de refus (D4). Elle ne modifie ni RULE-H0, ni les
protections PROD.

### D8 — Entrée en vigueur sans auto-autorisation

Cet ADR suit le circuit en vigueur : commit de ratification de l'owner, puis fusion par l'owner de
la tête épinglée (ADR-121 D4 et D7). Il ne peut pas s'autoriser lui-même : à sa fusion, aucun
périmètre n'est adopté ni activé.

## Décision distincte — Q2 et Q4

Ce delta ne dépend pas de D1 à D8 et peut être retiré seul.

### D9 — Q2 : rechercher l'existant sans quota

Q2 de [[rules-engineering-quality]] reprend la décision de l'owner du 2026-11-03 :

> Rechercher les équivalents et leurs consommateurs dans les sources pertinentes avant toute création. Adapter les recherches au doute restant, sans quota fixe. Un résultat nul ne prouve pas à lui seul l’absence : préciser la couverture, les limites d’accès et pourquoi l’existant ne convient pas.

Sont retirés les quotas « ≥ 3 » et « 2-3 », le seuil de 70 % et la preuve d'absence par un seul
résultat nul. Sont conservés la recherche préalable, les vérifications par type d'artefact, la
preuve contrôlable et la préférence de Q1 pour la réutilisation.

### D10 — Q4 : évaluer sur problème ou gain documenté

Q4 reprend la décision de l'owner du 2026-11-03 :

> Évaluer les options maintenues et compatibles lorsqu’un problème ou un gain documenté le justifie. La nouveauté seule ne déclenche ni migration, ni PR, ni issue. Réaliser seulement les changements couverts par le mandat ; consigner la suite réellement nécessaire dans le dossier existant.

Seuls l'introduction et les libellés dérivés qui imposent une PR, une issue ou un ADR changent, y
compris l'application aux agents. Q1, Q3, les autres obligations, les dates de revue des ADR et le
traitement des ADR `proposed` de plus de 30 jours restent inchangés. Un ADR reste requis quand une
décision change (G1).

## Amendement

Les textes suivants figurent dans la même PR. Ils deviennent canon applicable à la fusion de la tête
ratifiée (D8) ; avant, ils ne modifient pas le canon de `main`.

- **ADR-121** : D2, ligne « Fusion » : l'owner, ou le mécanisme activé dans un périmètre adopté
  (D2) ; D2, ligne « Décision de gouvernance », et dernier paragraphe de D7 : hors périmètre, la
  fusion par l'owner de la tête épinglée reste la preuve d'adoption d'un changement qu'aucun ADR ne
  porte ; dans un périmètre activé qui couvre les décisions de gouvernance, cette adoption est
  tracée avant la fusion, dans la forme que fixe le périmètre (D2, D3) ; D3 inchangé ; D4
  s'applique hors périmètre, et dans un périmètre la trace suit D5 ; D5 : `canon-sync` inchangé
  hors périmètre ; AP-self-merge inchangé dans tous les cas : aucune exception de ce nom n'existe,
  périmètre compris, et une exécution dans un périmètre activé exige les revues applicables (D4) ;
  l'auto-fusion Dependabot (C9) reste une divergence tant qu'un périmètre ne l'adopte pas ; D7 : la
  ratification reste la preuve d'adoption d'un ADR, et la fusion de la tête ratifiée peut être
  exécutée dans un périmètre activé qui couvre les décisions de gouvernance. La ratification
  d'ADR-121 n'est pas rouverte.
- **ADR-102** D2 (« Un agent ne fusionne jamais ») et D3.2 : hors périmètre adopté puis activé,
  inchangés ; dans un tel périmètre, le mécanisme exécute la décision autorisée, jamais une décision
  de l'agent. Le caractère de règle de conduite et la décision owner de la rendre mécanique sont
  inchangés.
- **ADR-120** D1 : la décision reste humaine ; l'exécution peut être automatique dans un périmètre
  adopté puis activé. DoD2 satisfaite ne vaut toujours ni fusion ni autorisation.
- **ADR-099** D2 : inchangé ; la revue humaine des avances de pin reste une validation spécifique
  maintenue (D3).
- **ADR-119** D7 : inchangé ; sa phrase « Les fusions restent réservées à l'owner (ADR-102) »
  renvoie à ADR-102 et se lit avec lui, tel qu'amendé ici ; ses autres actes humains restent des
  validations spécifiques maintenues (D3).
- **[[rules-vault]] 3.3.0** : G4, introduction, point 2, vérification, checklist et sanctions.
- **[[GOVERNANCE-HUMAN]]** : RULE-H5 (paragraphe ajouté) et RULE-H6 (point 3 et phrases
  conditionnelles) ; RULE-H0 inchangée.
- **[[rules-engineering-definition-of-done]] 1.3.0** : DoD2, énoncé, point 6 et anti-pattern.
- **[[rules-agent-exit-contract]] 1.2.0** : distribution, points 2 et 4 ; manifeste régénéré.
- **[[rules-technical]] 3.1.0** : T6, voir ci-dessous.
- **[[rules-engineering-quality]] 1.2.0** : Q2 et Q4 (D9, D10).

Chaque texte modifié renvoie aux mêmes conditions : « périmètre explicitement adopté puis activé
selon ADR-123 », « aux conditions d'ADR-123 D2 à D6 », et « le mécanisme, le compte qui exécute et
l'acte qui l'arme sont ceux que fixe le périmètre activé ».

### T6 : deux états

Le paragraphe T6 décidé par l'owner le 2026-11-03 est repris sans modification :

> Le mandat explicite couvre la préparation et la vérification de la PR dans ses limites, sans renouveler le même accord. Les contrôles et validations spécifiques applicables restent requis. L’agent remet à l’owner le numéro de PR, le SHA de tête à 40 caractères et la commande épinglée sur ce SHA ; l’owner seul exécute la fusion. Aucune approbation technique, CI verte ou autorisation générale ne permet à l’agent de fusionner ni d’activer l’auto-fusion.

- **État actuel** (avant la fusion de la tête ratifiée de cet ADR) : `main` porte T6 3.0.0, qui se
  lit avec ADR-121 D4 ; la fusion est exécutée par l'owner.
- **Nouveau cadre** (T6 3.1.0) : la règle reproduit le paragraphe ci-dessus comme décision du
  2026-11-03, alignement sur le canon actuel, puis un delta qui nomme ses clauses absolues
  « l’owner seul exécute la fusion » et « ni d’activer l’auto-fusion » : elles s'appliquent hors
  d'un périmètre explicitement adopté puis activé ; dans un tel périmètre, l'exécution peut être
  automatique aux conditions de D2 à D6. Elles ne restent donc pas une interdiction universelle et ne
  sont pas remplacées sans le dire.
- **Traçabilité** : la règle cite la formulation 3.0.0 de T6 et la décision du 2026-11-03 ; le delta
  est désigné comme la rédaction du nouveau cadre préparée pour cet ADR, non comme un texte déjà
  approuvé dans ces termes.

| Adaptation de T6 | Condition approuvée |
|---|---|
| Lignes finales retirées : attente, approbation, `gh pr merge` | ADR-121 D4 ; paragraphe T6 approuvé |
| Ligne « OBLIGATOIRE » : aucun push direct, branche et PR, puis la fusion décrite (rédaction proposée) | G4.1 ; paragraphe T6 approuvé |
| Commentaire `INTERDIT` : `gh pr merge` lancé par l'agent hors d'un périmètre activé (rédaction proposée) | ADR-121 D4 ; paragraphe T6 approuvé ; D2 |
| Paragraphe T6 inséré tel quel, daté du 2026-11-03 | paragraphe T6 approuvé |
| Delta : exécution automatique dans un périmètre adopté puis activé | texte approuvé, paragraphes 2 et 6 ; D2, D7 |
| Delta : autorisation préalable ou adoption tracée avant la fusion | texte approuvé, paragraphe 3 ; D3 |
| Delta : tête identifiée, contrôles, revues, protections ; refus si une condition manque | texte approuvé, paragraphe 4 ; D4 |
| Delta : mécanisme, compte et acte qui l'arme fixés par le périmètre ; trace | texte approuvé, paragraphe 5 ; D2, D5 |
| Raison (PREPROD, tag `v*`) conservée ; T1 à T5 et T7 inchangés | texte approuvé, paragraphe 5 ; D6 |

Les documents opérationnels qui décrivent la procédure effective ne sont pas modifiés : elle reste
inchangée tant qu'aucun périmètre n'est activé (`AGENTS.md` étape 10, `CLAUDE.md` § G4,
`README.md`, `99-meta/ci-policy.md`, `99-meta/branch-protection.md`,
`99-meta/onboarding/claude-desktop-instructions.md`). Ils s'alignent dans le périmètre
d'activation. Seule la ligne G4 de `ops/moc/MOC-Governance.md`, index des règles, renvoie à cet ADR.

## Effets couplés de la fusion de cette PR

Cette PR modifie la source de l'AEC, sa version déclarée dans le générateur et le manifeste
`99-meta/canon-hashes.json`. Le candidat ne déclenche rien ; à la fusion de sa tête ratifiée, le
circuit existant produit les effets suivants (constatés sur les workflows le 2026-11-07) :

1. **Sur la PR du vault** : `canon-publish.yml` exécute seulement son contrôle
   `compute-canon-hashes.py --check` (déclencheur `pull_request` sur ces chemins).
2. **À la fusion sur `main`** : `canon-publish.yml` vérifie les hashes, puis émet `canon-updated`
   vers `ak125/automecanik-wiki`, `ak125/automecanik-raw` et `ak125/nestjs-remix-monorepo`.
3. **Monorepo** : `canon-sync.yml` (sur `canon-updated` et chaque jour à 03:00 UTC) ouvre ou met à
   jour la PR `canon-sync/auto`, étiquetée `canon-sync`, sans auto-fusion. Cette PR suit le circuit
   en vigueur : fusion par l'owner (AEC point 4), tant qu'aucun périmètre adopté puis activé ne la
   couvre ; son éligibilité n'en autorise pas le déclenchement (D2).
4. **Vérifications consommateurs** : `agent-exit-contract-hash.yml` (sur `canon-updated`, chaque jour
   à 03:30 UTC et sur les chemins des copies) compare les copies au `distribution_sha256` du
   manifeste. Il signale un écart jusqu'à la resynchronisation des copies. Les copies wiki et raw se
   mettent à jour par une PR ordinaire.

État préexistant, non causé par ce candidat, constaté le 2026-11-07 : la copie monorepo de l'AEC est
encore en 1.0.0 alors que `main` du vault porte 1.1.0 ; les exécutions planifiées de
`agent-exit-contract-hash.yml` échouent depuis le 2026-11-04 (dernier succès le 2026-11-03) ; la
PR `canon-sync/auto` #1954 est ouverte et ses contrôles attendent une approbation d'exécution
(`action_required`). La fusion de cet ADR déplace le hash attendu vers 1.2.0 : la PR
`canon-sync/auto` est alors mise à jour, et l'écart persiste jusqu'à sa fusion par l'owner.

Un worktree tiers non commité (`codex/aec-clarification-20261020`) modifie les mêmes fichiers (AEC,
générateur, manifeste, index MOC) sur une base plus ancienne : un conflit est attendu si ce travail
reprend. Il n'est pas touché par ce candidat.

## Ce que cet ADR ne fait pas

- Il n'adopte ni n'active aucun périmètre et ne fusionne rien.
- Il ne modifie aucun workflow, fichier `.github/`, protection de branche, droit, identité, bot ou
  label ; il ne touche ni RULE-H0, ni les protections PROD.
- Il ne décide pas l'auto-fusion Dependabot du monorepo (ADR-121 C9).
- Il ne lance aucune synchronisation des consommateurs et ne modifie aucune copie de l'AEC.
- Il ne crée ni registre, ni trace, ni tâche, ni orchestrateur.

## Points à décider (proposés, non adoptés)

- contenu minimal d'un périmètre adopté (D2) ;
- dépôts, branches et catégories du premier périmètre ;
- politique d'autorisation par catégorie et son emplacement dans le vault ;
- mécanisme existant retenu, compte qui exécute et acte qui l'arme, après qualification en lecture
  seule par le 21 et le 23 ;
- forme de la trace d'autorisation dans la PR ;
- traitement des effets couplés (§Effets couplés) avant toute activation qui couvre l'AEC ou
  `canon-sync`.

## Options considérées

- **A — Statu quo, fusion par l'owner seul** : rejetée par le texte approuvé.
- **B — Automatisation sans périmètre adopté** : rejetée ; elle remplacerait des décisions humaines.
- **C — Périmètre explicite, conditions de refus et activation séparée** : retenue.

## Conséquences

- **Positives** : une décision autorisée peut être exécutée sans relais manuel ; T6, Q2 et Q4 ne
  contredisent plus les décisions de l'owner.
- **Négatives** : un texte de plus à lire ; tant qu'aucun périmètre n'est activé, le gain est nul ;
  la modification de l'AEC ouvre une resynchronisation des copies (§Effets couplés).

## Métriques

- Fusions exécutées automatiquement hors d'un périmètre activé : 0.
- Fusions automatiques dont la trace omet l'autorisation, la tête, le compte ou le résultat : 0.

## Retour arrière

Revert de la PR qui porte cet ADR et ses amendements, manifeste régénéré par son générateur ; la
resynchronisation des copies suit alors le même circuit. Le delta Q2/Q4 se retire seul. Aucun
mécanisme n'étant activé par cet ADR, il n'y a rien à désactiver.

## Revue planifiée

**Date** : 2027-02-07.

**Critères** : une fusion exécutée hors périmètre ; une condition de D4 contournée ; un effet couplé
non évalué ; une recherche Q2 sans couverture déclarée.

## Références

- [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] — mandat, revue, décision et fusion
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] — G4
- [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]] — DoD2
- [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]] — D2, pin de sous-module
- [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] — D7, actes humains maintenus
- [[ADR-013-agent-lifecycle-governance|ADR-013]] — niveaux G1 et G2
- [[MOC-Decisions]]

---

*Décisions de l'owner : 2026-11-03*
*Proposé le : 2026-11-07*
*Accepté le : 2026-11-08 (décision de l'owner ; canon à la fusion de la tête ratifiée, D8)*
