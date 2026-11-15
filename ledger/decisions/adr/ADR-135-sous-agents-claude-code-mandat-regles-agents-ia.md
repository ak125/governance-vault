---
id: ADR-135
title: "Sous-agents Claude Code des sessions de mandat : ce sont des agents IA au sens d'AI1, AI5 et AI6 ; trois sous-agents en lecture seule, rattachés au rôle 23, sans changement de la routine de remise"
status: proposed
date: "2026-11-15"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: ["ADR-037", "ADR-121", "ADR-128", "ADR-129", "ADR-130"]
related_rules: ["AI1", "AI2", "AI5", "AI6", "AI9", "G1", "G4"]
related_incidents: []
reviewed_by: ""
version: "0.1.0"
---

# ADR-135 : sous-agents Claude Code des sessions de mandat et règles des agents IA

- **Statut** : Proposed (2026-11-15). Rédigé par un agent (Claude Code CLI, machine DEV) sur mandat de
  l'owner (« Mandat AB », 2026-11-15). Il reste `proposed` tant que l'owner ne l'a pas ratifié par un
  commit de ratification ([[rules-vault|G1]] ; [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D7).
- **Pièce liée** : PR monorepo #2081 (brouillon), `https://github.com/ak125/nestjs-remix-monorepo/pull/2081`.
  Elle porte l'inventaire `audit/agents/inventaire-2026-11-15.md`, les trois fichiers
  `.claude/agents/mandat/*.md` et le patch de carte `audit/agents/agent-operating-map.patch` (non appliqué).
- **Activation** : aucune par cet ADR. La fusion de la PR #2081 par l'owner rend les trois fichiers
  visibles des sessions Claude Code lancées depuis le monorepo : c'est l'acte d'activation.

## Contexte

1. **Un mécanisme natif existe.** Claude Code charge les sous-agents de projet depuis
   `.claude/agents/` : un fichier Markdown avec un en-tête YAML (`name`, `description` requis ;
   `tools`, `disallowedTools`, `model` facultatifs). Chacun a son propre prompt, son propre contexte et
   son propre jeu d'outils. Il hérite des permissions de la session qui l'appelle. Le dossier est lu
   récursivement. Source : documentation officielle `code.claude.com/docs/en/sub-agents` et
   `/docs/en/permissions`, lues le 2026-11-15 (la page n'affiche pas de date de mise à jour) ; CLI
   observée sur le DEV : 2.1.325.
2. **L'inventaire du 2026-11-15** (PR #2081) recense trois sources : 42 sous-agents de workspaces
   (`workspaces/*/.claude/agents/`), 7 agents Paperclip (`agents/*/AGENTS.md`) et les 44 entrées de la
   carte `.spec/00-canon/ai-registry/agent-operating-map.yaml`. Aucun des 42 sous-agents n'a été appelé
   dans les 411 traces `.jsonl` disponibles (2026-10-10 → 2026-11-15). 31 n'ont pas de fiche au
   catalogue. Aucun n'a de `metric_id`.
3. **Les règles ne disent pas si un sous-agent est un agent.** [[rules-ai-cos]] v1.0.0 exige, pour
   « tout agent » : un indicateur ([[rules-ai-cos|AI1]]), un rattachement `reports_to`, `sponsor`,
   `squad` ([[rules-ai-cos|AI5]]) et une fusion ou suppression pour toute création
   ([[rules-ai-cos|AI6]]). [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]] D5 conserve ces règles
   pour tout agent IA du projet et reformule AI5 (« une fiche au catalogue dont le champ `owner` est
   renseigné »). Ce texte n'est pas encore appliqué : `rules-ai-cos.md` reste en v1.0.0.
4. **ADR-128 pose deux limites.** D6 : le pilote (rôle 23) « n'ajoute pas d'agent ». D4 : la routine de
   remise lance `claude -p` dans un worktree isolé, depuis une issue `mandat-prêt`.
5. **La routine de remise en cours (PR monorepo #2080, tête `ff98fd118939c5625365892dc16f8e68ccc2a1c7`,
   ouverte, mandat AA)** lance la session avec `--tools Bash,Read,Edit,Write,Glob,Grep`, sans outil
   `Agent`, dans un environnement vidé, sans `GH_TOKEN`. Lecture seule de son diff ; elle n'est pas
   modifiée ici.
6. **Le scanner SEO d'[[ADR-037-agent-naming-canon|ADR-037]]** (`OperatingMatrixService`) lit
   `.claude/agents/*.md` sans récursion et exige un `role:` canonique. Un fichier sous
   `.claude/agents/mandat/` n'entre pas dans la matrice. Preuve : sortie de
   `scripts/seo/dump-agent-matrix.ts` identique avant et après l'ajout du dossier (`cmp`).

## Décision

### D1 — Un sous-agent Claude Code est un agent IA

Un fichier de sous-agent Claude Code versionné dans un dépôt du projet (`.claude/agents/**/*.md`,
monorepo ou workspace) est un **agent IA** au sens de [[rules-ai-cos]]. Il a un prompt, un contexte
et des outils propres, et agit sans validation humaine pas à pas. [[rules-ai-cos|AI1]],
[[rules-ai-cos|AI2]], [[rules-ai-cos|AI5]], [[rules-ai-cos|AI6]] et [[rules-ai-cos|AI9]] s'y appliquent dès
sa création. Les skills, les commandes et les sessions racines ne sont pas visés par cet ADR.

### D2 — AI1 : un indicateur par sous-agent, déclaré dormant tant qu'il n'est pas mesuré

Chaque sous-agent a un `metric_id` avec des seuils :

| Sous-agent | `metric_id` | Cible | Alerte | Critique |
|---|---|---|---|---|
| `mandat-releve` | `mandat_releve_mutation_free_rate` (part des appels sans mutation) | 100 % | — | < 100 % |
| `mandat-reception` | `mandat_reception_verdict_agreement_rate` (accord avec la réception de l'owner) | ≥ 90 % | < 90 % | < 70 % |
| `mandat-triage-ci` | `mandat_triage_cause_cited_rate` (checks rouges avec une ligne de cause citée) | ≥ 80 % | < 80 % | < 50 % |

Le schéma de la carte refuse ces champs (`node` en `additionalProperties: false`, sous
`.spec/00-canon/**`). Ils sont donc portés en commentaires YAML dans le patch de carte. Aucun
producteur ne mesure encore ces indicateurs : la capacité `mandat-subagents` est déclarée
`status: dormant`. Sans producteur, la vérification « KPI mesuré automatiquement » d'AI1 n'est pas
remplie. Ce point est déclaré ici, pas masqué. Un sous-agent sans indicateur, ou dont l'indicateur
n'a pas de producteur à la revue suivante de l'owner, relève de la sanction d'AI1 (retrait).

### D3 — AI5 : le rattachement, dans les deux lectures

- **Texte en vigueur (v1.0.0)** : `reports_to: ia-agents-lead` (rôle 23, ADR-128 D2) ;
  `sponsor: owner` (« Human CEO » lu « owner », comme dans ADR-129 D5 pour AI9) ;
  `squad: sessions-mandat` (les sessions lancées par mandat). La squad n'existe pas encore comme objet
  du catalogue : la vérification « `squad` existe ? » reste ouverte jusqu'à la ratification.
- **Lecture d'ADR-129 D5** : une fiche au catalogue (`ledger/agents/`) avec un `owner` renseigné. Les
  trois fiches sont créées par une PR Vault distincte, après la ratification de cet ADR. Elles ne sont
  pas dans cette PR, pour qu'aucune fiche ne précède la décision.

Les deux lectures sont tenues jusqu'à l'application du texte d'ADR-129 D5.

### D4 — AI6 : trois créations, trois contreparties proposées, validées par l'owner

| Création | Reprise de | Contrepartie proposée |
|---|---|---|
| `mandat-releve` | `agents/ceo/AGENTS.md` (synthèse d'état en lecture seule) | retrait de `agents/ceo/` |
| `mandat-reception` | `workspaces/seo-batch/.claude/agents/phase1-auditor.md` (verdict sur preuve) | retrait de `workspaces/seo-batch/.claude/agents/conseil-batch.md` (neutralisé) |
| `mandat-triage-ci` | `agents/cto/AGENTS.md` (dérive technique, priorités P1–P3) | retrait de `agents/cto/` |

Les trois contreparties sont déjà inactives : fiches `agent.ceo.ia` et `agent.cto.ia` `disabled`
(ADR-129), `conseil-batch` neutralisé. Une fois les retraits faits, le nombre de fichiers d'agents
ne croît pas. Le nombre d'agents réellement utilisables croît de trois. L'owner juge si cet équilibre suffit. Chaque retrait
exige sa décision écrite et datée (AI6, étape 4). Il est exécuté par une PR distincte. Aucun fichier
d'agent n'est supprimé ni déplacé avant cette décision.

### D5 — ADR-128 D6 : le pilote n'ajoute toujours pas d'agent

Les trois sous-agents ne sont pas des missions du pilote. Ce sont des outils qu'une session de mandat
peut appeler. Ils sont rattachés au rôle 23 comme capacité déclarée (`mandat-subagents`, dormante),
parce que le rôle 23 répond des agents. Ils ne lisent pas la file pour le pilote. Ils ne proposent ni
n'arbitrent rien dans la file. Leur création passe par cet ADR et AI6, sous décision de l'owner. Elle
ne passe pas par le pilote. D6 reste entière.

### D6 — Place dans la routine de remise (ADR-128 D4) : aucun changement

Cet ADR ne modifie ni la routine `mandat-remise`, ni `pilote-file`, ni leur prompt, leurs outils, leurs
labels ou leurs secrets. Telle que proposée dans la PR #2080, la session de la routine n'a pas l'outil
`Agent` ni de jeton GitHub. Les trois sous-agents n'y sont donc **pas appelables**. Après fusion de la
PR #2081, ils servent aux sessions de mandat lancées par l'owner sur le DEV (interactives ou
`claude -p`), où `Agent` et `gh` sont disponibles :

- `mandat-releve` au démarrage ou à la reprise, avant toute mutation ;
- `mandat-triage-ci` quand une PR du mandat a des checks rouges ;
- `mandat-reception` avant de rendre la preuve AEC, ou par l'owner pour recevoir un livrable.

Leur sortie est une donnée. Le commentaire de preuve, les labels `statut:*` et la fusion restent des
actes de la session ou de l'owner (D4.3, [[rules-ai-cos|AI2]]). Les rendre disponibles dans la routine
exigerait d'ajouter `Agent` à ses outils. C'est un changement distinct de la routine, décidé par
l'owner, hors de cet ADR.

### D7 — Garde-fous des sous-agents

- **Outils minimaux** : `Read, Grep, Glob, Bash` ; `disallowedTools: Write, Edit, NotebookEdit`.
- **Modèle fixé** : `haiku` pour le relevé, `sonnet` pour la réception et le triage.
- **Rien d'élargi** : aucune permission ajoutée, aucun secret, aucune adresse dans les fichiers.
- **Limite déclarée** : la lecture seule de Bash tient à la consigne du prompt. Le format natif ne
  restreint pas Bash commande par commande, et le sous-agent hérite des permissions de la session.
  La démonstration (refus prouvé, zéro appel d'outil, aucun fichier créé) ne fait pas de cette consigne
  une permission.
- **Hors scan ADR-037** : les fichiers vivent sous `.claude/agents/mandat/` et ne portent pas de
  `role:`. Si le scanner devient récursif, ce choix est à revoir dans le même changement. Cet ADR
  n'amende pas ADR-037.

### D8 — Retour arrière

| Moment | Geste | Effet |
|---|---|---|
| Avant fusion de #2081 | fermer la PR | rien n'a existé hors branche |
| Après fusion | revert de la PR, ou suppression de `.claude/agents/mandat/` par PR | les nouvelles sessions ne voient plus les sous-agents |
| Patch de carte appliqué | revert du commit de l'owner sur la carte | `nodes: []` et la capacité retirés |
| Urgence | gestes de l'owner d'[[rules-ai-cos|AI9]] (N3 : PR de la session fermée ou repassée en brouillon) | travail gelé |
| ADR | passage à `rejected` ou `superseded` par PR signée | décision retirée |

Aucune donnée, aucune base et aucun état de runtime ne sont touchés. Le retour arrière est immédiat.

## Options Considérées

### Option A : sous-agents natifs, rattachés et équilibrés (retenue)

**Description** : D1 à D8.

**Avantages** :
- mécanisme natif, sans code maison ni registre parallèle ;
- trois outils de lecture que les sessions de mandat refaisaient à la main ;
- AI1, AI5 et AI6 appliquées dès la création ;
- retour arrière immédiat.

**Inconvénients** :
- indicateurs sans producteur ;
- la lecture seule de Bash repose sur le prompt ;
- contreparties AI6 déjà inactives.

### Option B : un sous-agent n'est pas un agent au sens des règles

**Description** : traiter les sous-agents comme de la configuration, hors AI1, AI5 et AI6.

**Avantages** : aucune charge de gouvernance.

**Inconvénients** : 42 sous-agents existent déjà sans indicateur ni fiche pour 31 d'entre eux. Exclure
la catégorie ferait croître l'écosystème sans contrôle, contre le but d'AI6.

### Option C : ne créer aucun sous-agent

**Description** : garder les relevés dans le prompt des sessions.

**Avantages** : aucun agent de plus.

**Inconvénients** : chaque session refait le relevé, la réception et le triage sans format commun ni
trace séparée. Les 42 sous-agents existants restent sans décision.

## Justification

L'option A applique les règles existantes à un mécanisme natif plutôt que d'en inventer un. Elle borne
la création à trois agents en lecture seule, chacun repris d'un agent existant, avec un indicateur, un
rattachement et une contrepartie. Ses faiblesses sont déclarées et confiées à l'owner : producteur
absent, consigne Bash, équilibre AI6.

## Conséquences

### Positives

- Les sous-agents entrent dans le champ des règles des agents IA (D1).
- Les sessions de mandat disposent d'un relevé, d'une réception et d'un triage communs, tracés en
  `.jsonl` par sous-agent.

### Négatives

- Trois fiches catalogue et un producteur d'indicateurs restent à créer.
- Les 42 sous-agents existants deviennent en écart à AI1 et AI5 (constat de l'inventaire, sans
  correction ici).

### Neutres

- Matrice SEO d'ADR-037, routine `mandat-remise` et `pilote-file` inchangées.

## Critères de Succès

- [ ] `mandat_releve_mutation_free_rate` = 100 % sur les appels tracés.
- [ ] `mandat_reception_verdict_agreement_rate` ≥ 90 % sur les réceptions de l'owner.
- [ ] `mandat_triage_cause_cited_rate` ≥ 80 % sur les checks rouges triés.
- [ ] Chaque contrepartie AI6 est validée ou refusée par une décision écrite et datée de l'owner.

## Implémentation

Actes de l'owner, chacun distinct :

1. Ratifier cet ADR (commit de ratification).
2. Décider des trois contreparties AI6 (décision écrite et datée).
3. Poser l'ownership des nouveaux chemins (extrait préparé pour Block-new de la PR #2081).
4. Fusionner la PR #2081 : c'est l'activation.
5. Appliquer, s'il le décide, `audit/agents/agent-operating-map.patch` sur la carte (`.spec/00-canon/**`,
   chemin réservé à l'owner).

Après la ratification : une PR Vault crée les trois fiches catalogue (D3), et une PR monorepo exécute
les retraits validés (D4). Un producteur d'indicateurs fait l'objet d'un mandat distinct.
