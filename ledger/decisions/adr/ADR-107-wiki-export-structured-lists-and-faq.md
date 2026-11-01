---
id: ADR-107
title: "Listes et FAQ structurées dans l'export WIKI : listes Markdown dans content_md, paires question-réponse typées (qa) pour la FAQ — étend ADR-086 §2bis, évolution MINOR du contrat d'export (ADR-062 §8)"
status: accepted
date: "2026-10-05"
decision_date: "2026-10-05"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-086", "ADR-062"]
related_adr: ["ADR-031", "ADR-046", "ADR-059", "ADR-083", "ADR-086", "ADR-088", "ADR-106"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-107 : Listes et FAQ structurées dans l'export WIKI

- **Statut** : Accepted (2026-10-05). La fusion par l'owner vaut ratification.
- **Numéro** : dérivé le 2026-10-05 (`main` du vault ∪ PR ouvertes) : `main` porte ADR-105, ADR-112
  et ADR-113 ; aucune PR ouverte ne porte un numéro de 106 à 111. Signé après ADR-106. Le script
  owner re-vérifie le numéro avant le commit.
- **Étend** [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2bis (bloc éditorial
  valide) : un bloc peut porter une structure, sans changer ses champs requis.
- **Applique** [[ADR-062-repository-contract-system-meta-model|ADR-062]] §8 : ajout d'un champ
  optionnel = évolution **MINOR** du contrat d'export, avec préavis de 30 jours via le MOC.
- **Débloque** ADR-106, qui renvoie ici les formats structurés : son D6 interdit de déduire une
  liste ou des questions d'une prose.

## Périmètre

- Sections éditoriales des fiches `gamme` (`entity_data.editorial`, 9 sections tier M et R).
- Contrat d'export `exports/seo/*.json`, objet `blocks[]`.
- Les autres types d'entité (vehicle, constructeur, diagnostic) reprendront la même règle quand
  leurs sections éditoriales seront exportées. Aujourd'hui, aucun export de ces types n'existe.

## Contexte

Constats vérifiés le 2026-10-04 : WIKI `origin/main` `042e566`, monorepo `main` `f1c601170`,
vault `main`.
Re-vérifiés le 2026-10-05 : monorepo `main` `658c0a3ce` (aucun fichier cité modifié depuis
`f1c601170`), WIKI épinglé inchangé.

1. **Le format déclaré de `content_md` est le Markdown.**
   - Schéma `entity-data/gamme.schema.json`, `$defs.editorialBlock` : « Stockée comme
     content_md ». Schéma `exports-seo.schema.json` v1.1.0 : `blocks[].content_md`, chaîne non vide.
   - Le builder `build_exports_seo.py` recopie `content_md` tel quel (`str(content)`), sans
     transformation.
   - Le rendu projeté de la PR monorepo #1713 (`projection-markdown.renderer.ts`) rend déjà les
     listes Markdown.
2. **L'aplatissement vient du producteur, pas du contrat.**
   - `author_from_raw._section_prose` reçoit une liste de faits sourcés distincts et les joint
     par une espace (`" ".join(out)`) : « 1 fait = 1 phrase », en un seul paragraphe.
   - Dans le même builder, trois blocs dérivés de la DB (compatibilité, pièces de la même famille,
     critères de choix) joignent aussi une liste en une phrase (`", ".join`, `" ; ".join`).
   - Le corps des fiches, lui, contient des listes : `wiki/gamme/filtre-a-huile.md` a des listes à
     puces (terme en gras, définition, lien source) sous « Définition », « Fonctionnement »,
     « Entretien & bonnes pratiques ». Seul le bloc éditorial exporté est aplati.
3. **La FAQ exportée est une prose.**
   - `filtre-a-huile` : `faq.content_md` = 513 caractères, un seul paragraphe, 4 questions et
     4 réponses enchaînées (« Que remplace-t-on lors de l'entretien ? Le filtre vissé en entier… »).
   - Rien dans le contrat ne distingue une question d'une réponse.
4. **Le seul FAQPage servi aujourd'hui repose sur une devinette.**
   - `frontend/app/components/blog/conseil/section-config.tsx`, `parseFAQFromS8` : une expression
     régulière extrait les paires d'un HTML `<details><summary><b>Q</b></summary><p>A</p></details>`
     du chemin historique (`sg_content`), et n'émet `FAQPage` qu'à partir de 3 paires.
   - 141 des 258 sections S8 en base ont ce format. Leur contenu est sourcé `rag://`, donc hors
     canon (ADR-031, ADR-046).
   - Sur le chemin projeté, la S8 serait de la prose : la page perdrait son `FAQPage` (comparaison
     D7 de `filtre-a-huile`, ADR-106).
5. **Le consommateur tolère un champ ajouté.**
   - Le mapper R3 (`projection-r3.mapper.ts`, `blockContractViolations`) et la garde de qualité
     (`seo-projection-gate.service.ts`) ne vérifient que les champs requis : un champ optionnel
     supplémentaire ne fait rejeter aucun bloc.

## Décision

### D1 — Une liste de faits distincts est une liste Markdown

- Quand une section éditoriale est faite de faits distincts, `content_md` les porte en **liste
  Markdown** : un fait par élément (`- …`). Les faits ne sont jamais joints en un paragraphe.
- Une prose rédigée reste une prose : D1 ne transforme pas un paragraphe en liste.
- Aucun changement de contrat : le Markdown est déjà le format déclaré de `content_md`. Aucun
  changement de version.
- Côté producteur :
  - `author_from_raw._section_prose` émet la liste au lieu de la jointure ;
  - les trois blocs dérivés de la DB du builder émettent leurs éléments en liste ;
  - la sérialisation YAML préserve les sauts de ligne, ce qu'un test d'aller-retour
    (écriture puis relecture de la fiche) prouve.
- Côté consommateur : rien à ajouter. Le rendu Markdown projeté (#1713) traite déjà les listes.

### D2 — La FAQ porte ses paires question-réponse dans un champ typé `qa`

- Le bloc éditorial `faq` peut porter un champ optionnel `qa` :

  ```yaml
  faq:
    qa:
      - question: "Que remplace-t-on lors de l'entretien ?"
        answer_md: "Le filtre vissé en entier, ou seulement l'élément filtrant d'une cartouche."
        source_ids: ["web:…"]
    source_ids: ["web:…"]      # union des source_ids des paires (dérivée)
    truth_level: sourced
  ```

- Chaque paire : `question` (chaîne non vide, finit par « ? »), `answer_md` (Markdown non vide),
  `source_ids` (au moins une source préfixée, même règle que le bloc). Une réponse sans source
  n'est pas une paire valide.
- **Une seule vérité.** Quand `qa` est présent :
  - c'est lui la source ; dans la fiche, le bloc `faq` ne porte pas de `content_md` écrit à la
    main ;
  - le builder dérive `content_md` de `qa` par un rendu déterministe (question en gras, puis
    réponse, une paire par paragraphe) et `source_ids` comme union triée des sources des paires ;
  - une garde du WIKI vérifie l'égalité exacte entre `content_md` exporté et le rendu de `qa` :
    toute divergence bloque l'export.
- Dans l'export, `content_md` reste **requis** : un consommateur qui ignore `qa` continue de
  rendre la FAQ en prose. Le contrat reste rétro-compatible.
- `qa` est réservé à la section `faq`. Aucune autre section ne le porte en v1.

### D3 — Aucun consommateur ne déduit une structure d'une prose

- Un consommateur rend une liste depuis la syntaxe Markdown de liste, et une FAQ structurée
  depuis `qa`, **jamais** depuis une prose :
  - pas de découpage sur « ? » ;
  - pas d'expression régulière sur du HTML ou du Markdown pour reconstituer des paires.
- `FAQPage` ne s'émet sur le chemin projeté que depuis `qa`. Bloc `faq` sans `qa` = FAQ rendue en
  prose, sans données structurées.
- Le seuil d'émission de `FAQPage` (3 paires dans `parseFAQFromS8`) reste une règle du
  consommateur. Le WIKI ne s'y plie pas : **jamais** de question ajoutée pour atteindre un seuil
  (ADR-086 : aucune cible de remplissage, absence = valide).
- `parseFAQFromS8` reste le chemin historique `sg_content`. Il n'est ni étendu au chemin projeté ni
  pris pour modèle.

### D4 — Évolution des contrats (ADR-062 §8, MINOR)

| Contrat | Avant | Après | Nature |
|---|---|---|---|
| `exports-seo.schema.json` (`schema_version`) | 1.1.0 | 1.2.0 | champ optionnel `blocks[].qa` |
| `entity-data/gamme.schema.json` | — | MINOR | `editorialBlock.qa` optionnel ; `content_md` requis sauf quand `qa` est présent (bloc `faq` uniquement) |
| `projection_contract_version` (runtime DB) | 1.0.0 | 1.0.0 | inchangé : aucun champ requis ni retiré |

- Préavis de 30 jours via le MOC avant la première émission de `qa` dans `exports/seo/`.
- **Ordre de déploiement imposé** :
  1. le consommateur recopie `qa` tel quel et le valide (mapper R3, après ratification de cet ADR) ;
  2. le WIKI émet `qa` ;
  3. l'émission de `FAQPage` depuis `qa` est activée entité par entité, avec l'activation canary de
     la page (ADR-106 D7). C'est un changement de données structurées servies sur une page indexée :
     **acte owner**.

### D5 — Fiches déjà promues : aucune réécriture en place

- Les fiches validées (dont `filtre-a-huile`, promue le 2026-10-01) ne sont **jamais** modifiées
  directement pour adopter D1 ou D2.
- Leur passage à la liste ou à `qa` suit le chemin normal : nouvelle proposition, gates de
  qualité (ADR-088), décision du décideur unique de promotion (ADR-083), validation owner.
- D'ici là, leur FAQ projetée reste de la prose sans `FAQPage`. C'est déjà la raison pour laquelle
  `filtre-a-huile` ne doit pas être activée (comparaison D7 d'ADR-106).

## Options considérées

### Option 1 — Conventions Markdown dans `content_md` pour la FAQ (rejetée pour la FAQ, retenue pour les listes)

Écrire chaque question en `### Question ?` ou en gras, puis la faire reconnaître par le consommateur.

- Pour la FAQ, rejetée : le consommateur devrait reconnaître une structure dans du texte. C'est la
  devinette d'exécution interdite (CLAUDE.md, invariant 3) et le défaut de `parseFAQFromS8`. Une
  variation d'écriture ferait disparaître le `FAQPage` sans erreur.
- Pour les listes, retenue (D1) : la liste à puces est la structure native du Markdown, déjà
  traitée par le rendu. Il n'y a rien à reconnaître.

### Option 2 — Champ typé `qa` (retenue pour la FAQ)

Paires explicites, sourcées une à une, validées par schéma ; rétro-compatible grâce au
`content_md` dérivé. Coût : une évolution MINOR et une garde d'égalité côté WIKI.

### Option 3 — Un bloc par paire question-réponse (rejetée)

Chaque paire deviendrait un bloc `R3_CONSEILS/faq`. ADR-106 D2 rend invalide une section
revendiquée par plusieurs blocs d'une même enveloppe, et le nombre de blocs grossirait sans
gain : les paires appartiennent à une même section.

### Option 4 — Statu quo, FAQ en prose (rejetée)

Le chemin projeté perdrait les données structurées FAQ sur toutes les pages qui en ont
aujourd'hui, et rien ne permettrait de les retrouver sans deviner.

## Conséquences

### Positives

- La structure est portée par la source, et chaque réponse est sourcée à son grain.
- Aucun consommateur ne devine ; une FAQ mal formée bloque l'export au lieu de disparaître en
  silence au rendu.
- Les listes ne demandent aucun changement de contrat.

### Négatives / coûts

- Évolution MINOR de deux schémas, garde d'égalité `content_md` ↔ `qa`, test d'aller-retour YAML.
- Les fiches déjà promues ne gagnent la structure qu'au rythme des nouvelles propositions (D5).

### Neutres

- `projection_contract_version` inchangé.
- `parseFAQFromS8` et le chemin `sg_content` restent tels quels jusqu'à leur retrait, décidé
  ailleurs.

## Mise en œuvre (après ratification)

1. **WIKI** — schémas (D4), producteur (`author_from_raw`, D1 et D2), builder (listes des blocs
   dérivés de la DB, dérivation de `content_md` depuis `qa`), garde d'égalité, test d'aller-retour
   YAML. Une PR, CI `quality-gates.py --all-local`.
2. **Monorepo** — mapper R3 : recopier et valider `qa` (paires non vides, sources préfixées) ;
   rendu des paires ; `FAQPage` depuis `qa` seulement, derrière l'activation canary par entité.
   Une PR, après la PR WIKI des schémas.
3. **MOC** — préavis de 30 jours avant la première émission de `qa`.

## Ce que cet ADR ne décide pas

- Il n'active aucune page et n'émet aucune donnée structurée : ce sont des actes owner, par entité
  (ADR-106 D7).
- Il ne change ni URL, ni title, ni meta description, ni H1.
- Il ne crée aucune question : le contenu vient des sources validées. Le RAG n'est jamais une
  source (ADR-031, ADR-046).
- Il ne modifie pas les formats tableau et étapes numérotées des autres sections servies. Une
  procédure est une liste ordonnée Markdown (D1) ; un tableau demandera sa propre décision le jour
  où une section exportée en aura besoin.

## Références

- [[ADR-062-repository-contract-system-meta-model|ADR-062]] §8 — évolution SemVer des contrats.
- [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §2bis — bloc éditorial valide.
- [[ADR-083-tiered-wiki-promotion|ADR-083]] — décideur unique de promotion WIKI.
- [[ADR-088-promotion-gate-substance-scoring|ADR-088]] — gates de qualité des propositions.
- ADR-106 (proposé) — contrat de rendu de la projection R3, D6 et D7.
- [[ADR-031-four-layer-content-architecture|ADR-031]], [[ADR-046-r-stack-single-generator-and-layers|ADR-046]] — le RAG est un consommateur, jamais une source de contenu.
