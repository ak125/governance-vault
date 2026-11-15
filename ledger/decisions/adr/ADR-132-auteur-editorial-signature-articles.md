---
id: ADR-132
title: "Auteur éditorial et signature publique : qui rédige, intègre, relit, admet les faits, arbitre et publie ; aucune signature ne nomme un LLM ou un outil d'IA comme auteur"
status: proposed
date: "2026-11-15"
decision_date: ""
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: ["ADR-025", "ADR-044", "ADR-114", "ADR-119", "ADR-120", "ADR-121", "ADR-128"]
related_rules: ["G1", "G4"]
related_incidents: []
reviewed_by: ""
version: "0.1.0"
---

# ADR-132 : auteur éditorial et signature publique des articles

- **Statut** : Proposed (2026-11-15). Rédigé par un agent (Claude Code CLI, machine DEV) sur le mandat
  de l'owner « Mandat Q — Auteur éditorial et signature des articles ». La ratification (`accepted`)
  et la fusion sont des actes réservés à l'owner, décideur humain : Marwane
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7). Rien n'est en vigueur
  par ce texte.
- **Écrit deux règles et rien d'autre** : l'organisation interne de la production d'un contenu
  publié (R1) et l'auteur déclaré de toute signature publique (R2).
- **Nouvel ADR, pas un amendement** : aucun des ADR examinés ne traite du rôle d'auteur éditorial ni
  de la signature des articles (§Contexte, C1). Cet ADR n'amende aucun ADR.
- **N'applique rien.** Aucun fichier du monorepo, aucune balise auteur, aucune donnée structurée,
  aucun skill ni aucune consigne de projet n'est modifié. Le changement du canon Fafa est instruit
  (§Instruction), pas appliqué.
- **Méthode** : constats en lecture seule le 2026-11-15, sur `main` du vault au commit `156b143` et
  sur `main` du monorepo au commit `b40181b3e` (commit du 2026-11-15 à 11:50 UTC, identique à `main`
  sur GitHub au moment du constat), lu par `git grep` et `git show` sur ce commit, sans toucher aucun
  checkout.

## Contexte

### C1 — Aucun ADR ne désigne l'auteur éditorial

Lecture d'ADR-025, ADR-044, ADR-119 et ADR-121 :

- [[ADR-025-seo-department-architecture|ADR-025]] organise le département SEO en modules. Son module
  Content ops prévoit un calendrier éditorial dont la table porte une colonne `assignee` et un score
  E-E-A-T local. Il ne dit pas qui rédige, qui relit, ni qui est déclaré auteur.
- [[ADR-044-seo-strategy-2026-roles-priority|ADR-044]] est `rejected` (2026-11-10). Il traite de la
  priorité des rôles de contenu ; son standard S5 vise la véracité du Schema.org (`AggregateRating`),
  pas le champ `author`.
- [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] remplace la relecture humaine
  des fiches WIKI par une auto-review de sens. Il porte sur la fiche WIKI avant sa promotion, pas sur
  l'article publié ni sur sa signature.
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] sépare mandat, revue d'un diff,
  décision, fusion et mise en production (D2), et demande de nommer séparément département, domaine,
  agent et session (D8). Il ne traite pas de la rédaction d'un contenu ni de son auteur déclaré.

ADR-131 (`proposed`, PR #413 en brouillon, non fusionnée) ajoute la qualification du 11 avant la
promotion WIKI et écrit qu'il « ne traite ni le lot FH-004 ni l'auteur éditorial ».

Le pilotage avait constaté le 13 nov. à 11:35 UTC qu'aucun texte du canon ne désigne l'auteur
éditorial, dans `AGENTS.md`, `CLAUDE.md`, `.claude/rules`, `.spec/00-canon` et le vault. La projection
`.spec/00-canon/ai-registry/agent-operating-map.yaml` du monorepo, non normative (« Reference
projection — non-authoritative », ligne 1), donne au département 6 (« Contenu éditorial »)
`lead: content-lead` et `accountable_owner: null`.

### C2 — Ce que les pages déclarent aujourd'hui

Les pages conseil déclarent comme auteur l'organisation (`"author"` de type `Organization`, nom
« Automecanik ») et une balise `meta author` « Automecanik - Experts Automobile ». Aucun des champs auteur
relevés par l'inventaire (§Inventaire) ne nomme un LLM ou un outil d'IA.

### C3 — Les décisions de l'owner

Marwane, le 14 nov. 2026, citées mot pour mot.

À 11:24 Paris, en réponse à la proposition « chat Claude du département 06 auteur éditorial, Claude
CLI pour le code et l'intégration, relecture par une session distincte » :

> ok mais l'auteur n'est pas mis en ligne sur les article cela est grave de mettre article auteur llm

À 11:28 Paris :

> relecteur codex que pensez vous ,la regles vise toute les signature expert automobile est bien

Lecture de 11:28, retenue par le mandat : le relecteur indépendant est Codex ; la règle vise toutes
les signatures ; la mention « Experts Automobile » est gardée.

Décisions sur Fafa, transcrites en §Instruction et non tranchées ici :

- à 11:33 Paris : « on supprime IA ET AJOUT EXPERT AUTOMOBILE A LA SIGNATURE » ;
- à 11:37 Paris : « 1 », c'est-à-dire que seul le mot « IA » sort de la phrase prononcée, l'indication
  de contenu généré par IA restant ailleurs (étiquette des plateformes, `identity_disclosed`) ;
- à 13:08 Paris, formule confirmée : « Moi, c'est Fafa, le mécano expert automobile d'AutoMecanik ».

## Principe directeur

> Un contenu publié a un auteur déclaré : l'organisation AutoMecanik. Les outils qui le préparent
> ont chacun un rôle, et aucun ne cumule deux rôles qui se contrôlent l'un l'autre.

## Décisions

### R1 — Organisation interne : cinq rôles distincts

S'applique à tout contenu publié : article, page conseil, vidéo, publication sociale.

| Rôle | Qui (ADR-121 D8) | Fait | Ne fait pas |
|---|---|---|---|
| Rédaction (auteur éditorial) | département 6, Contenu éditorial ; session : un chat Claude du département | rédige le texte à partir des faits admis | n'admet aucun fait ; ne relit pas son texte ; n'intègre pas son texte |
| Intégration | Claude Code CLI, session distincte de la rédaction | porte le texte dans le code ou les données, par une PR | ne rédige pas le texte qu'elle intègre |
| Relecture indépendante | Codex, session distincte de la rédaction | relit le texte rédigé, sans le raisonnement de l'auteur, et rend ses constats | ne relit pas un texte qu'elle a rédigé ; ne publie pas |
| Admission des faits | le WIKI : fiche promue par son décideur sur preuve (ADR-114, ADR-119) | fixe les faits qu'un contenu peut porter | — |
| Arbitrage et publication | l'owner, Marwane | tranche un désaccord entre auteur et relecteur ; décide la publication | — |

- L'auteur ne se relit pas lui-même. Une relecture relancée dans la session de l'auteur n'est pas
  indépendante (règle déjà posée pour les diffs par
  [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]]).
- Une session ne peut à la fois rédiger et intégrer un même texte.
- Ni l'auteur, ni l'intégrateur, ni le relecteur n'admettent un fait.
- Un contenu n'est soumis à la publication qu'après la relecture indépendante de son texte. Cette
  relecture n'autorise pas la publication (ADR-121 D3) ; la publication est une mise en production
  au sens d'ADR-121 D2.
- La relecture du texte par Codex n'est pas la revue du diff de la PR d'intégration (DoD2,
  ADR-120) : les deux existent, chacune avec sa preuve.
- Une session ne reçoit ni ownership ni place au catalogue des agents (ADR-121 D8). Cet ADR ne
  renseigne pas `accountable_owner` du département 6 et ne crée aucun agent.

### R2 — Affichage public : l'auteur déclaré est l'organisation AutoMecanik

- Aucune signature ne nomme un LLM ou un outil d'IA comme auteur. La règle vise toutes les
  signatures : balise `meta author`, champ `author` des données structurées, ligne d'auteur visible,
  signature d'une vidéo (prononcée ou écrite), signature d'une publication sociale.
- L'auteur déclaré reste l'organisation AutoMecanik. La mention « Experts Automobile » est gardée.
- R2 porte sur l'auteur déclaré. Elle ne règle pas l'indication qu'un contenu est généré par IA
  (étiquette d'une plateforme, mention à l'écran, `identity_disclosed`) : c'est l'objet des questions
  ouvertes Q1 à Q3.
- La graphie (« AutoMecanik » dans le mandat, « Automecanik » dans le code au constat) n'est pas
  tranchée par cet ADR.

## Inventaire : où l'auteur affiché est écrit (monorepo, `main` au `b40181b3e`)

Constat en lecture seule, aucun fichier modifié. Au constat, aucun de ces fichiers ne nomme un LLM ou
un outil d'IA comme auteur.

Balise `meta author` « Automecanik - Experts Automobile » :

- `frontend/app/routes/blog-pieces-auto._index.tsx:129`
- `frontend/app/routes/blog-pieces-auto.article.$slug.tsx:180`
- `frontend/app/routes/blog-pieces-auto.conseils.$pg_alias.tsx:386`
- `frontend/app/routes/blog-pieces-auto.guide-achat.$pg_alias.tsx:374`
- `frontend/app/routes/blog-pieces-auto.guide-achat.comment-utiliser-selecteur-vehicule-pieces-auto.tsx:310`

Balise `meta author` « AutoMecanik » :

- `frontend/app/routes/blog-pieces-auto.constructeurs._index.tsx:581`
- `frontend/app/components/ui/SEOHelmet.tsx:143`
- `frontend/public/index.html:14`, `frontend/public/index-v2.html:13`

Données structurées, `author` de type `Organization`, nom « Automecanik » :

- `frontend/app/components/guide/guide-schemas.ts:170`
- `frontend/app/components/guide/r6-guide-schemas.ts:44`
- `frontend/app/routes/blog-pieces-auto.article.$slug.tsx:121`
- `frontend/app/routes/blog-pieces-auto.guide-achat.comment-utiliser-selecteur-vehicule-pieces-auto.tsx:179`
- `frontend/app/routes/reference-auto.$slug.tsx:437`

Valeur dynamique, avec repli sur l'organisation :

- `backend/src/modules/layout/services/meta-tags.service.ts:117` (`author: 'Automecanik'`), `:233`
  et `:256-258` (`data.author || 'Automecanik'`, type `Organization`), `:321` (balise émise)
- `frontend/app/utils/seo.server.ts:314`, `:315`, `:326` (`article.author`, fonction
  `createArticleSeoMeta`, sans appelant sur `main` au constat)

Gabarits et documentation :

- `design-system/roles/R3-blog.md:109` : gabarit `"author": { "@type": "Person", "name": "..." }`,
  qui diverge de R2 (constat signalé, non corrigé)
- `workspaces/seo-batch/.claude/skills/seo-content-architect/references/schema-templates.md:215`
  (`Organization`, « Automecanik »)
- `.spec/guides/seo-performance-global.md:504` (`meta author` « Automecanik »)

Texte visible qui décrit l'auteur sans signer :

- `frontend/app/components/blog/EditorialTrust.tsx:10-11` : « Rédigé par des experts » ; « Nos
  contenus sont rédigés et validés par des mécaniciens et techniciens automobile certifiés. »

Hors champ de R2 : `frontend/app/components/ui/SEOHelmet.tsx:283-285`, `author` de type `Person`
d'un avis client (`Review`), qui n'est pas une signature éditoriale.

Signatures de Fafa (vidéo, publication sociale) : voir §Instruction.

## Instruction : changement du canon Fafa (non appliqué)

Le canon de la persona Fafa vit dans le monorepo. Il se déclare figé : « V1 = figée jusqu'à clôture
des 10 pilotes ; V2+ = PR vault dédiée + ADR addendum, jamais ad-hoc »
(`workspaces/marketing/.claude/skills/fafa-persona-canon/SKILL.md`, §Évolution). La décision de
11:33 et 11:37 et la formule de 13:08 sont donc instruites ici et ne sont appliquées à aucun fichier.

### Changement instruit

Phrase de signature prononcée, de « Moi c'est Fafa, le mécano IA d'AutoMecanik. » à « Moi, c'est
Fafa, le mécano expert automobile d'AutoMecanik ». Seul le mot « IA » sort de la phrase prononcée ;
l'indication de contenu généré par IA reste ailleurs (étiquette des plateformes,
`identity_disclosed`).

### Fichiers touchés (monorepo, `main` au `b40181b3e`)

Canon et skills :

- `workspaces/marketing/.claude/skills/fafa-persona-canon/SKILL.md` :
  - ligne 23, Rôle : « Mécano IA d'AutoMecanik (toujours assumée explicitement) » ;
  - ligne 25, Signature : « Moi c'est Fafa, le mécano IA d'AutoMecanik. » ;
  - ligne 28, Identité IA : « TOUJOURS assumée (transparence YouTube/TikTok 2026) » ;
  - ligne 74 : champ de sortie `"identity_disclosed": true`.
- `workspaces/marketing/fafa-media-factory/personas/fafa.md:11` (Rôle), `:13` (Signature), `:16`
  (Identité IA, « conforme transparence YouTube/TikTok 2026 »)
- `workspaces/marketing/fafa-media-factory/personas/fafa-character-bible.md:21`
- `workspaces/marketing/fafa-media-factory/personas/fafa-video-style.md:30-32` (badge « Fafa — mécano
  IA », « Non négociable (conformité plateformes 2026) »)
- `workspaces/marketing/fafa-media-factory/personas/fafa-visual-reference-lock.md:15`, `:26`, `:41`
- `workspaces/marketing/fafa-media-factory/formats/sequences-courtes.md:18` (bloc Identité), `:22`
  (bandeau)
- `workspaces/marketing/fafa-media-factory/prompts/higgsfield/avatar-prompt-template.md:10`, `:24`,
  `:34`, `:35`, `:50` ; `prompts/higgsfield/fafa-reference/avatar-reference-prompt.md:14` ;
  `prompts/higgsfield/README.md:37`
- `workspaces/marketing/.claude/skills/fafa-video-prompt-builder/SKILL.md:48`
- `workspaces/marketing/.claude/skills/fafa-script-generator/SKILL.md:70` (« Fafa est une IA
  assumée »)
- `.claude/prompts/_shared/editorial-review.md:193`, `:208` (« Fafa est un mécano IA, toujours
  présenté comme tel »)

Brouillons et dossiers (aucun publié par cet ADR) :

- `workspaces/marketing/fafa-media-factory/scripts/draft/fafa-filtre-huile-001/disclaimer.json:16`
  et `fafa-plaquettes-frein-001/disclaimer.json:16` : `ai_generated_notice`, « Fafa est un mécano IA
  d'AutoMecanik. », en surimpression continue
- `scripts/draft/fafa-filtre-huile-001/script.json:9` (phrase prononcée) et `:32` (bandeau) ;
  `scripts/draft/fafa-plaquettes-frein-001/script.json:23` et `render-payload.json:24` (bandeau)
- `workspaces/marketing/fafa-media-factory/manifests/renders/fafa-plaquettes-frein-001.json:76`
- `docs/audits/editorial-filtre-huile-20261030/MEDIA.md:69`, `:87`, `:118`, `:170`, `:181`, `:194-197`
  (légendes TikTok, Instagram, YouTube, Facebook), `:221`, `:231`, `:243`, `:262`, `:270`, `:288`

Code : `backend/src/modules/media-factory` ne contient pas la phrase de signature. Le type
`ai_generated_notice` du schéma `disclaimer-plan.schema.json:39` n'a pas d'équivalent dans
`DisclaimerType` (`backend/src/config/video-quality.constants.ts:152-156`, qui a `illustration_ia`) ;
aucune gate ne lit le type (constat C18-22 de `workspaces/marketing/README.md:684`).

### `identity_disclosed` et les `disclaimer.json`

- `identity_disclosed` n'existe que dans le format de sortie de `fafa-persona-canon` (ligne 74).
  Aucune gate ne le calcule ni ne le lit. Le canon ne dit pas ce qui le rend vrai ; aujourd'hui, la
  phrase « mécano IA » prononcée en est la preuve la plus directe. Si cette phrase perd « IA »,
  `identity_disclosed` doit être prouvé par autre chose : bandeau, étiquette de plateforme.
- Les deux `disclaimer.json` portent l'indication `ai_generated_notice` en surimpression continue.
  Cette mention n'est pas la phrase prononcée. La décision de 11:37 ne dit pas si elle reste.

### Ce que devient la transparence YouTube/TikTok citée par le canon

Le canon motive l'identité IA « toujours assumée » par la « transparence YouTube/TikTok 2026 »
(SKILL.md ligne 28, `fafa.md:16`, `avatar-prompt-template.md:34`, `prompts/higgsfield/README.md:37`)
sans citer de texte. Le vault ne contient pas les règles de ces plateformes, et ce constat ne les a pas
lues. Selon la décision de 11:37, la transparence passe par l'étiquette des plateformes et par
`identity_disclosed`, plus par la phrase prononcée. Rien ici ne vérifie que l'étiquette suffit sans
mention dans la vidéo : c'est la question Q3.

## Questions ouvertes (posées, sans réponse)

Trancher ces questions est un acte réservé à Marwane.

- **Q1 — Voie d'entrée du changement Fafa.** La décision de 11:33 et 11:37 et la formule de 13:08
  entrent-elles dans le canon par cet ADR, au moment de sa ratification (il écrirait alors une
  troisième règle), ou par un ADR distinct, comme l'exige le canon Fafa (« PR vault dédiée + ADR
  addendum ») ? Avant ou après la clôture des 10 pilotes (V1 figée) ?
- **Q2 — Portée du retrait du mot « IA ».** Seule la phrase prononcée est visée. Que deviennent :
  la ligne Rôle (« Mécano IA d'AutoMecanik ») et la ligne Identité IA du canon ; le bandeau
  `ai_generated_notice` « Fafa est un mécano IA d'AutoMecanik. » des `disclaimer.json` ; les
  légendes sociales « Conseil informatif ; Fafa est un mécano IA » ; le badge « Fafa — mécano IA » ?
  Qu'atteste `identity_disclosed`, et qui le vérifie ?
- **Q3 — Avis du département 18.** Un avis du département 18 (Juridique & Assurances, « Dormant »,
  « NO-CODE » dans `audit/automecanik-departments-map.md`) sur une obligation d'information est-il
  nécessaire ? Les points qu'un tel avis aurait à examiner, sans réponse ici :
  - une persona générée par IA présentée comme « mécano expert automobile », sans « IA » dans la
    phrase prononcée ;
  - la mention « Experts Automobile » des balises auteur, et la phrase d'`EditorialTrust.tsx`
    (« rédigés et validés par des mécaniciens et techniciens automobile certifiés »), alors que R1
    confie la rédaction à un chat Claude et la relecture à Codex ;
  - les règles d'étiquetage de YouTube et de TikTok, et les obligations de transparence du règlement
    européen sur l'IA (article 50), que ce constat n'a pas lues.

## Ce que cet ADR ne fait pas

- Il ne modifie aucun fichier du monorepo, aucune balise auteur, aucune donnée structurée, aucun
  skill, aucune consigne de projet, aucun brouillon vidéo.
- Il n'applique pas le changement du canon Fafa et ne tranche aucune question ouverte.
- Il n'amende ni ADR-119 (admission WIKI), ni ADR-120 (revue d'un diff), ni ADR-121, ni ADR-131.
- Il ne crée aucun agent, aucun identifiant, aucune gate, aucun check requis, et ne renseigne pas
  `accountable_owner`.
- Il ne reprend ni FH-004, ni les issues #1944, #1947 et #1924 du monorepo.
- Il ne touche pas la PROD et n'autorise aucune publication.

## Options considérées

### Option A — Amender un ADR existant — rejetée

Aucun des ADR examinés (C1) ne traite de l'auteur ni de la signature ; un amendement greffé sur l'un
d'eux mêlerait deux sujets.

### Option B — Déclarer l'outil auteur (« rédigé par une IA ») — rejetée

Contraire à la décision de 11:24 (« cela est grave de mettre article auteur llm »).

### Option C — Déclarer une personne comme auteur (`Person`) — rejetée

Personne n'est désigné ; le gabarit `R3-blog.md` qui l'envisage reste un constat. La décision de
11:28 garde l'organisation et la mention « Experts Automobile ».

### Option D — Organisation déclarée auteur, rôles internes séparés — retenue

Elle transcrit la proposition acceptée à 11:24, les précisions de 11:28, et réemploie les
séparations déjà posées pour les diffs (ADR-120, ADR-121).

## Conséquences

### Positives

- Un contenu publié a un auteur déclaré, le même partout.
- Aucun outil ne rédige et ne contrôle le même texte.
- L'état actuel des pages est déjà conforme à R2 au constat (organisation déclarée, aucun LLM nommé).

### Négatives

- R1 ajoute une relecture par Codex à chaque contenu publié.
- R2 laisse ouverte l'indication d'un contenu généré par IA (Q1 à Q3).
- La mention « Experts Automobile » et la phrase d'`EditorialTrust.tsx` restent à examiner (Q3).

## Mise en œuvre (après ratification et fusion, par l'owner)

1. R2 ne demande aucun changement de page au constat. Le gabarit `design-system/roles/R3-blog.md`
   s'aligne par une PR du monorepo.
2. R1 s'applique aux contenus produits après l'entrée en vigueur ; les mandats nomment les rôles
   selon ADR-121 D8.
3. Le changement du canon Fafa suit la réponse à Q1.

## Revue planifiée

**Date** : 2027-02-15.

**Critères** : un contenu publié dont l'auteur a aussi été le relecteur ou l'intégrateur ; une
signature qui nomme un LLM ou un outil d'IA ; le sort de Q1 à Q3.

## Références

- [[ADR-025-seo-department-architecture|ADR-025]] ·
  [[ADR-044-seo-strategy-2026-roles-priority|ADR-044]] ·
  [[ADR-114-wiki-safety-auto-gate|ADR-114]] ·
  [[ADR-119-wiki-semantic-auto-review-replaces-human-review|ADR-119]] ·
  [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]] ·
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] ·
  [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] · [[MOC-Decisions]]
- ADR-131 : PR #413 du vault, brouillon.
- Monorepo : fichiers de §Inventaire et §Instruction ; `audit/automecanik-departments-map.md` ;
  `.spec/00-canon/ai-registry/agent-operating-map.yaml`.

---

*Proposé le : 2026-11-15*
*Accepté le : —*
*Dernière revue : 2026-11-15*
