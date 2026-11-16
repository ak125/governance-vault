---
id: ADR-137
title: "Skills tiers : surfaces d'emploi, installation versionnée au niveau du dépôt, wrapper local et cycle d'adoption et de retrait (généralise ADR-057)"
status: accepted
date: "2026-11-16"
decision_date: "2026-11-16"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-057"]
extends: []
related_adr: ["ADR-057", "ADR-061", "ADR-101", "ADR-102", "ADR-118", "ADR-121", "ADR-129"]
related_rules: ["AI6", "G1", "G3", "G4", "G5"]
related_incidents: []
reviewed_by: ""
version: "1.0.0"
---

# ADR-137 : skills tiers, surfaces, installation et cycle d'adoption

- **Statut** : Accepted (2026-11-16). Décision de l'owner, décideur humain : Marwane : instruction
  explicite « ratifie ADR-137 » donnée dans le chat de pilotage (session claude.ai
  `011BVGEN3a4TYQ7Kbm3Qm7Np`) le 2026-11-16 à 01:04, heure de Paris (00:04 UTC), sur le texte
  proposé de la PR #421 (tête `48a82ab34393f264dd35cc962432331446f85d56`). Les trois choix inscrits
  en D2.4 et D6 sont pris par le chat de pilotage sur délégation de Marwane : « utiliser la meilleure
  approche pas de bricolage », le 2026-11-16 à 01:00, heure de Paris. Rédigé par un agent (Claude
  Code CLI, machine DEV) le 2026-11-16 sur le mandat AL de l'owner (« Vault (département 02) :
  skills tiers, surfaces d'emploi et cycle d'adoption ; analyse du catalogue skills.sh sans
  installation ») et son complément n° 1 ; le commit de ratification est préparé par un agent sur
  cette instruction : son auteur et sa clé de signature sont techniques. Canon applicable à la
  fusion par l'owner de la tête qui porte cette ratification, sous les contrôles requis
  ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] ; [[rules-vault|G1]] ;
  [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 et D7) ; avant cette fusion,
  ce statut décrit le candidat ratifié et ne modifie pas le canon de `main`.
- **Amende** [[ADR-057-marketingskills-adoption-pattern|ADR-057]] (`deferred`) : seul son
  frontmatter reçoit `amended_by: ["ADR-137"]`, son corps reste inchangé, comme pour ADR-118. Le
  champ, posé dans la PR de proposition comme l'a fait la PR #413, est conservé par la
  ratification.
- **N'installe rien.** Aucun skill n'est ajouté, retiré ou modifié par cet ADR, ni dans le
  monorepo, ni dans le vault, ni au niveau utilisateur (§ « Ce que cet ADR ne fait pas »). Les
  retraits retenus en D2.4 sont des actes de l'owner, après la fusion.

## Contexte

ADR-057 a écrit un pattern d'adoption pour un seul dépôt tiers (`coreyhaines31/marketingskills`)
: wrapper local mince, amont jamais forké, un skill par cycle de 30 jours. Il est `deferred`
depuis le 2026-11-10 et n'est donc que du contexte historique au sens de G5
([[rules-governance-process]]). Aucun texte normatif ne dit aujourd'hui où un skill écrit hors
AutoMecanik peut vivre, comment il entre, ni comment il sort. Le catalogue public skills.sh
(CLI `skills`, éditeur Vercel) rend pourtant l'installation d'un skill tiers immédiate, à une
commande près, et les outils de la plateforme y renvoient (le connecteur Supabase de claude.ai
conseille `npx skills add supabase/agent-skills`).

### Faits relevés le 2026-11-16 (lecture seule)

Le détail, les commandes et les empreintes sont dans le rapport du mandat AL
(`RAPPORT-MANDAT-AL.md`, hors dépôt). Chaque fait porte sa source.

- **Monorepo** (`ak125/nestjs-remix-monorepo`, `origin/main` à
  `9908188b380d6cf5f5d8c0b64db8544977818a13`) : 45 `SKILL.md`, tous écrits pour AutoMecanik (17
  à la racine `.claude/skills/`, 16 dans `workspaces/seo-batch`, 11 dans `workspaces/marketing`,
  1 dans `workspaces/wiki`). Aucun skill tiers, aucun fichier de lock de skills.
  `.agents/skills` est un lien symbolique suivi par Git vers `../.claude/skills`.
- **Écart avec ADR-061** : ADR-061 veut que l'`AGENTS.md` de chaque workspace liste
  exhaustivement ses skills locaux. Sur les 45 skills, 3 sont nommés dans l'`AGENTS.md` de leur
  workspace (`seo-content-loop`, `wiki-proposal-writer`, `keyword-planner`). Le tableau
  d'ADR-061 compte 8 skills à la racine ; il y en a 17. Constat seulement, non corrigé ici.
- **Machine DEV, utilisateur `deploy`** :
  - `~/.claude/skills` porte deux skills tiers : `grill-me` (marqueur `.origin` : dépôt
    `RobMitt/grill-me-skill`, commit `31d61d68fc406f8cc2a944b4b10e6f23877720f1`, installé le
    2026-10-27, description modifiée localement) et `typesafe-ai` (licence MIT, sans marqueur
    d'origine) ;
  - il porte aussi quatre liens symboliques `paperclip*` vers `/opt/automecanik/paperclip/skills/`,
    répertoire absent : liens morts. `~/.codex/skills` porte les mêmes quatre liens morts et
    `typesafe-ai` ;
  - `~/.agents` n'existe pas ; aucun `skills-lock.json` n'existe sur la machine hors
    `node_modules` ;
  - les transcripts de session Claude Code de ce projet ne montrent aucune invocation par l'outil
    Skill de `grill-me` ni de `typesafe-ai`. Un skill global se charge pourtant dans toutes les
    sessions de l'utilisateur, ce qui revient à charger leur description à chaque fois.
- **claude.ai** (manifeste synchronisé dans `~/.claude/skills/synced/`) : 20 skills, dont 14
  fournis par Anthropic et 6 créés pour le compte. L'un d'eux, `grill-me`, se déclare « repris
  tel quel » du skill Codex `grill-me`. Son texte est pourtant réécrit : lots de dix questions
  numérotées, réponse recommandée par question, brief de décision ; l'amont procède par arbre de
  décisions, branche par branche. Ce n'est donc pas un fork (lecture du chat de pilotage le
  2026-11-15 vers 23:59 UTC, comparée à `mattpocock/skills@grill-me` ; relue par l'agent contre le
  `grill-me` global de DEV, dont l'origine est `RobMitt/grill-me-skill`).
- **CLI `skills`** (paquet npm `skills` 1.8.1 ; source `vercel-labs/skills` lue à
  `b716f9dc2ba36b6aa8f0080615e5a3a6caeac63b`) :
  - le lock projet s'appelle `skills-lock.json`, à la racine du projet (`src/local-lock.ts:12`).
    Il est versionné (v2) et chaque entrée enregistre `source`, `ref`, `commit` et `skillPath`.
    ADR-057 le nomme à tort `.agents/skills.lock.json` (D1 et § « Négatives / coûts ») ;
  - l'agent `claude-code` installe dans `.claude/skills`, `codex` dans `.agents/skills`
    (`src/agents.ts:166-176`, `:235-241`). En mode par défaut, la CLI copie le skill dans le
    répertoire canonique `.agents/skills/<nom>`, puis crée un lien depuis le répertoire de
    l'agent. Elle compare les `realpath` et ne crée rien quand les deux chemins désignent le
    même répertoire (`src/installer.ts`, `createSymlink`). Dans le monorepo, une installation
    produit donc une seule copie physique, `.claude/skills/<nom>/`, vue par Claude Code et par
    Codex ;
  - la télémétrie part vers `https://www.skills.sh/tele/t` ; `DISABLE_TELEMETRY` ou
    `DO_NOT_TRACK` la coupent (`src/telemetry.ts`).
- **Audits affichés par skills.sh** : trois verdicts par skill (Gen Agent Trust Hub, Socket,
  Snyk), qui divergent souvent. Par exemple, au 2026-11-16, `getsentry/skills@gha-security-review`
  affiche Gen « Fail », Socket « Warn » et Snyk « Pass ». Ces audits sont un signal d'entrée, pas
  une preuve de sûreté.
- **Plugins Claude Code** : la note de connaissance
  [[claude-code-plugin-enablement-policy-20260504]] décrit les 27 plugins user-level déclarés
  (tous `@claude-plugins-official`), dont 5 actifs. Elle n'est pas normative et ne traite pas des
  skills tiers.

## Décision

### D1 — Périmètre

Un **skill tiers** est un `SKILL.md`, avec ses fichiers, dont le texte est écrit hors
AutoMecanik et qui entre sur une surface par une action d'installation, quelle qu'elle soit :
CLI `skills`, copie manuelle, plugin ou import sur claude.ai.

Sont hors périmètre :

- les skills écrits pour AutoMecanik ;
- les skills livrés par la plateforme elle-même et non installés par nous : skills Anthropic de
  claude.ai, `.system` de Codex. Ils sont listés pour information, sans décision ici.

### D2 — Surfaces

1. **Claude Code et Codex sur DEV, au niveau du dépôt seulement**, à la racine du monorepo, par
   une PR. Les workspaces `workspaces/*` n'en reçoivent pas : ADR-061 les borne à leurs skills
   de domaine, et la découverte par Codex des skills imbriqués n'est pas garantie
   (`.claude/knowledge/workspaces.md` du monorepo). Un ADR ultérieur peut ouvrir un workspace.
2. **claude.ai, projet de pilotage compris : aucun skill tiers.** Seuls y vivent des skills écrits
   pour AutoMecanik. Copier le `SKILL.md` d'un dépôt amont sur claude.ai est un fork, interdit par
   ADR-057 D5 ; s'en inspirer pour écrire un texte propre reste permis.
3. **Interdits pour un skill tiers** :
   - l'installation globale (`-g`, `~/.claude/skills`, `~/.agents/skills`, `~/.codex/skills`) ;
   - un plugin Claude Code user-level servant de véhicule à un skill tiers.

   Les plugins officiels déjà activés restent régis par la note de politique plugins. En activer
   un nouveau qui apporte des skills tiers passe par le cycle D5.
4. **Sort des skills globaux existants.** Le tableau donne la proposition du texte soumis, avec la
   ligne `grill-me` sur claude.ai corrigée à la ratification. Cet ADR ne retire rien.

   | Élément constaté | Proposition |
   |---|---|
   | 4 liens `paperclip*` morts (Claude Code et Codex) | Retrait : ils ne pointent sur rien |
   | `typesafe-ai` (Claude Code et Codex) | Retrait : tiers sans origine, aucune invocation trouvée, description chargée dans chaque session |
   | `grill-me` global (Claude Code) | Retrait du niveau global. S'il sert, deux voies : réadoption au niveau du dépôt par le cycle D5, sans la description modifiée localement ; ou réécriture comme skill AutoMecanik |
   | `grill-me` sur claude.ai | Reste en place : texte réécrit, pas un fork. Sa mention « Repris tel quel du skill Codex `grill-me` » est à préciser par Marwane sur son compte |
   | `.trash/` de `~/.claude/skills` (3 skills AutoMecanik) | Laissé à l'owner : hors périmètre des skills tiers |

   **Choix retenus** (chat de pilotage, sur délégation de Marwane : « utiliser la meilleure
   approche pas de bricolage », 2026-11-16 à 01:00, heure de Paris) :
   - retrait des 4 liens `paperclip*` morts, de `typesafe-ai` et de `grill-me` au niveau global ;
   - la suppression est un acte de Marwane, après la fusion de cet ADR ; l'ADR n'exécute rien ;
   - `grill-me` sur claude.ai reste en place (ligne ci-dessus).

### D3 — Installation versionnée

1. **Une seule forme de commande**, lancée depuis un worktree dédié du monorepo, à sa racine :
   `DISABLE_TELEMETRY=1 npx skills@<version exacte> add <propriétaire>/<dépôt> --skill <nom> -a claude-code`.

   Sont interdits :
   - toute installation sans `--skill`, ou avec `--all`, `-g` ou un joker ;
   - toute installation en lot ;
   - une seconde commande `-a codex`. Le lien `.agents/skills -> .claude/skills` sert déjà Codex
     par la même copie.

   La version de la CLI est écrite dans la PR.
2. **`skills-lock.json` est commité à la racine** dans la même PR. Il fait foi sur ce qui est
   amont : dépôt, `ref`, `commit` et `skillPath` de chaque skill tiers. Mettre à jour un skill
   amont, c'est une nouvelle PR qui montre le diff de l'amont entre les deux commits.
3. **Aucun fichier du dossier amont n'est modifié**, frontmatter compris (ADR-057 D5). Une
   correction remonte au dépôt source.
4. **Séparation lisible entre amont et local** :
   - le dossier amont garde le nom donné par l'amont ;
   - le wrapper local s'appelle `amk-<nom>` ;
   - `skills-lock.json` liste l'amont ;
   - l'`AGENTS.md` racine liste les skills en deux sections, « locaux » et « tiers (amont,
     `skills-lock.json`) ».

   Le registre des skills du monorepo (`.spec/00-canon/ai-registry/skills.registry.json`) devra
   reconnaître une entrée amont par le lock, au lieu d'exiger le frontmatter local que son schéma
   impose. Ce changement de code se fait dans le monorepo, hors de cet ADR, et recoupe le
   producteur du registre traité par le mandat AK.
5. **Lecture avant installation**, consignée dans la PR, au commit qui sera épinglé :
   - le `SKILL.md`, ses scripts et ses références ;
   - la licence ;
   - les trois audits skills.sh, datés ;
   - ce que le skill fait faire à l'agent : commandes, réseau, écritures en base, outils autorisés.

   Les cas suivants sont refusés, sauf si le wrapper les neutralise explicitement :
   - un skill qui exécute des scripts ou demande `Bash` sans motif ;
   - un skill qui écrit en base ou qui appelle le réseau.

### D4 — Wrapper d'un skill technique

Un skill tiers technique entre avec un wrapper local
`.claude/skills/amk-<nom>/SKILL.md`, écrit pour AutoMecanik, de 30 lignes de corps au plus. Il
contient au minimum :

1. la base de données en lecture seule (`SELECT`) ; aucun DDL ni DML ; une migration passe par
   un fichier de migration et le workflow du dépôt (skill local `db-migration`) ;
2. la primauté des règles du dépôt : invariants et zones STOP de `CLAUDE.md`, `.claude/rules/*` ;
3. le français pour tout texte publié ;
4. le renvoi au skill local voisin quand il existe ;
5. le commit amont épinglé, repris du lock.

Le wrapper ne peut pas empêcher Claude Code de charger l'amont seul, par sa propre description.
Les invariants de `CLAUDE.md` s'appliquent dans tous les cas ; l'observation D5 mesure si le
wrapper est suivi.

### D5 — Cycle d'adoption et de retrait

Repris d'ADR-057 D2, pour tout skill tiers :

1. **Une PR monorepo par skill**, qui contient seulement :
   - le dossier amont ;
   - son wrapper ;
   - `skills-lock.json` ;
   - la ligne de l'`AGENTS.md` racine (ADR-061) ;
   - la grille d'évaluation (D3.5).

   Pas de second skill dans la même PR.
2. **Contrepartie AI6 nommée dans la PR** ([[rules-ai-cos]], AI6 conservé par ADR-129) : le texte
   local qui sera fusionné ou retiré si le skill est adopté. À défaut, « aucune », avec le motif.
3. **Observation de 30 jours** à partir de la fusion :
   - nombre d'invocations, cible au moins 3 ;
   - respect des contraintes du wrapper, critère binaire : aucune violation ;
   - doublon ressenti avec un skill local.
4. **Décision explicite à T+30**, par l'owner, écrite dans le chat de pilotage et reportée sur la
   PR : garder ou retirer. Sans décision écrite, le skill est retiré.
5. **Retrait** en une PR : `npx skills remove <nom>` dans un worktree, puis revert de la PR
   d'adoption (dossier, wrapper, lock, ligne `AGENTS.md`).

Un seul skill tiers à la fois : le suivant n'entre pas avant la décision T+30 du précédent.

### D6 — Premier pilote

Pilote retenu : `supabase/agent-skills@supabase-postgres-best-practices`, lu au commit
`c9be0e931b7930f7d02126d04774d904c381e7d7`, avec le wrapper
`amk-supabase-postgres-best-practices` et la contrepartie AI6 ci-dessous. Choix du chat de
pilotage sur délégation de Marwane (« utiliser la meilleure approche pas de bricolage »,
2026-11-16 à 01:00, heure de Paris). Les raisons :

- il porte sur le cœur de la pile (Supabase et Postgres) ;
- il ne contient que des références : aucun script, aucun appel réseau, aucun outil MCP ;
- sa licence est MIT ;
- au 2026-11-16, skills.sh affiche 487 027 installations et trois audits « Pass ».

Son risque tient à sa description, qui le fait charger avant toute écriture Postgres, RLS et
migrations comprises, c'est-à-dire en zone STOP. Le wrapper `amk-supabase-postgres-best-practices`
le borne (D4) et renvoie à `db-migration`.

Contrepartie AI6 : si le skill est gardé à T+30, les passages génériques de `db-migration` qu'il
couvre (« Safe Patterns », « RLS Audit Patterns ») sont réduits à un renvoi. S'il est retiré, rien
ne change.

`getsentry/skills@secret-serialization` (Apache-2.0, outils `Read Grep Glob` seulement, trois
audits « Pass ») n'est pas une alternative pour ce premier cycle : 487 installations, et une
présence sur skills.sh depuis le 2026-09-29 seulement. Il reste un candidat « plus tard ».

### D7 — Nom du lock

Le fichier de lock s'appelle `skills-lock.json`, à la racine du projet. La mention
`.agents/skills.lock.json` d'ADR-057 (D1 et § « Négatives / coûts ») est erronée. Le corps d'ADR-057 reste
inchangé : cet ADR fait foi sur ce point.

## Options considérées

| Option | Verdict | Motif |
|---|---|---|
| A. Laisser ADR-057 `deferred` et décider au cas par cas | Rejetée | Rien n'encadre l'installation globale déjà constatée ni la copie sur claude.ai |
| B. Interdire tout skill tiers | Rejetée | Elle oblige à réécrire des références publiques maintenues par les éditeurs de la pile (Supabase, Sentry), avec un coût de maintenance local |
| C. Autoriser l'installation globale | Rejetée | Chargement dans toutes les sessions, hors PR, sans lock commité ni revue |
| D. Copie manuelle ou `git subtree` | Rejetée | Pas de lock lisible par la CLI ; dérive de fork (ADR-057 D5) |
| E. Niveau dépôt, lock commité, wrapper, cycle un par un (retenue) | Retenue | Réversible par PR, traçable par le lock, borné par les règles du dépôt |

## Conséquences

### Positives

- Une seule voie d'entrée pour un skill tiers, réversible par une PR.
- Le lock donne la version exacte de l'amont ; le diff entre deux commits rend une mise à jour
  relisible.
- Une installation sert Claude Code et Codex à la racine, sans double copie.

### Négatives

- Un wrapper par skill technique à maintenir.
- Le registre des skills du monorepo doit apprendre à reconnaître l'amont par le lock (travail
  monorepo séparé).
- Trente jours au moins entre deux adoptions.

### Neutres

- Les plugins officiels déjà activés restent régis par leur note de politique.
- Les skills fournis par la plateforme restent hors périmètre.

## Ce que cet ADR ne fait pas

- Il n'installe, ne retire et ne modifie aucun skill, à aucun niveau.
- Il ne retire pas les skills globaux : les retraits retenus en D2.4 sont des actes de l'owner,
  après la fusion.
- Il ne modifie ni le registre des skills, ni son schéma, ni un workflow, ni un `AGENTS.md`.
- Il ne corrige pas l'écart constaté avec ADR-061.
- Il ne rouvre pas ADR-057 pour `marketingskills` : D3 et D4 d'ADR-057 restent du contexte
  historique.

## Inconnues

- Les motifs des verdicts « Fail » et « Warn » des audits skills.sh ne sont pas détaillés sur les
  pages relevées.
- Le comportement de Codex avec un skill installé derrière le lien `.agents/skills` n'a pas été
  testé, puisque rien n'a été installé.
- L'efficacité du wrapper face au chargement autonome de l'amont n'est pas mesurée.
- La source lue de la CLI (`b716f9dc`) et le paquet npm 1.8.1 utilisé pour la recherche ne sont
  pas prouvés identiques.

## Critères de succès

- À la ratification, aucun skill tiers n'est installé hors du niveau dépôt sans décision
  explicite de l'owner.
- Le premier pilote entre par une PR conforme à D5.1, avec `skills-lock.json` et contrepartie
  AI6.
- La décision T+30 du pilote est écrite.

## Retour arrière

Revert de la PR de cet ADR : retrait du fichier et de la ligne `amended_by` d'ADR-057.
Un skill adopté sous cet ADR se retire selon D5.5.

## Revue planifiée

À la décision T+30 du premier pilote, ou au plus tard le 2027-02-16.

## Références

- [[ADR-057-marketingskills-adoption-pattern]] (D1, D2, D5)
- [[ADR-061-workspace-governance]] (`AGENTS.md` exhaustif)
- [[ADR-118-retrait-methodes-bmad-superpowers-spec-kit]] (précédent : frontmatter seul amendé)
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts]] (D4, D7)
- [[ADR-129-retrait-ai-cos-machine-systeme-agents]] (AI6 conservé)
- [[rules-ai-cos]] (AI6)
- [[claude-code-plugin-enablement-policy-20260504]]
- CLI : <https://github.com/vercel-labs/skills>, commit `b716f9dc2ba36b6aa8f0080615e5a3a6caeac63b`,
  lu le 2026-11-16
- Catalogue : <https://skills.sh/supabase/agent-skills/supabase-postgres-best-practices>, lu le
  2026-11-16
- Pilote : <https://github.com/supabase/agent-skills>, commit
  `c9be0e931b7930f7d02126d04774d904c381e7d7`, lu le 2026-11-16

---

*Proposé le : 2026-11-16*
*Accepté le : 2026-11-16*
