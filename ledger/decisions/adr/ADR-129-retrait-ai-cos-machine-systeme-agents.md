---
id: ADR-129
title: "Retrait d'AI-COS : machine arrêtée en octobre 2026 et système d'agents retiré ; amende ADR-012 et ADR-034, propose le sort des règles AI1 à AI10"
status: proposed
date: "2026-11-14"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-008", "ADR-009", "ADR-011", "ADR-012", "ADR-015", "ADR-034"]
extends: []
related_adr: ["ADR-006", "ADR-013", "ADR-028", "ADR-036", "ADR-101", "ADR-102", "ADR-118", "ADR-121", "ADR-128"]
related_rules: ["AI1", "AI2", "AI3", "AI4", "AI5", "AI6", "AI7", "AI8", "AI9", "AI10", "AP-12", "G1", "G8"]
related_incidents: []
reviewed_by: ""
version: "1.0.0"
---

# ADR-129 : retrait d'AI-COS, machine et système d'agents

- **Statut** : Proposed (2026-11-14). Rédigé par un agent (Claude Code CLI, machine DEV) le
  2026-11-14, sur mandat de l'owner (« Mandat K »). **Entrée en vigueur suspendue** à la ratification
  par l'owner, consignée par un commit de ratification sur la branche de la PR, puis à la fusion par
  l'owner de la tête qui porte ce commit ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]]
  D7). La PR reste en brouillon jusque-là.
- **Acte** deux faits fournis par l'owner : l'arrêt de la machine AI-COS (D1) et le retrait du système
  d'agents AI-COS (D2).
- **Propose**, sans les décider : le sort d'[[ADR-034-aicos-operating-contract|ADR-034]] (D3) et celui
  des règles AI1 à AI10 de [[rules-ai-cos]] (D5). L'owner tranche à la ratification ; il peut retenir
  une autre option que celle proposée.
- **Amende** ADR-008, ADR-009, ADR-011, ADR-012, ADR-015 et ADR-034 sur les seuls passages listés en
  D4. Comme pour [[ADR-118-retrait-methodes-bmad-superpowers-spec-kit|ADR-118]], le corps de ces ADR
  n'est pas réécrit ; seul leur frontmatter `amended_by` reçoit `ADR-129`, au commit de ratification.
- **Méthode** : constats relevés le 2026-11-14 sur `main` du vault (`9f7a6eefef9edeffc14df22336558569925e3163`).
  L'inventaire des documents vivants qui citent AI-COS est en annexe A.
- **Numéro** : 129 = plus haut numéro de `main` et des PR ouvertes, plus un. [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] (départements
  autonomes et coordonnés, PR #409) a pris le numéro 128 le 2026-11-14 ; relevé fait vers 22:50 UTC.

## Contexte

### Faits fournis par l'owner (Marwane, 2026-11-14)

- La machine AI-COS a été arrêtée en **octobre 2026**. Le jour exact n'est pas connu ; cet ADR ne
  l'estime pas.
- Le système d'agents AI-COS est retiré avec elle.
- Les règles AI1 à AI10 et ADR-034 n'ont pas été déclarés retirés : leur sort est à proposer.

### Pourquoi le système n'a pas fonctionné

- L'orchestrateur maison prévu par [[ADR-006-ai-orchestrator-architecture|ADR-006]] (LangGraph,
  JobEnvelope, RAG et skills sur AI-COS) n'a **jamais été construit**. ADR-006 est `superseded`.
- Le contexte d'ADR-034 décrit une dérive conceptuelle persistante : « huit concepts opérationnels
  coexistent sans hiérarchie claire » (AI-COS, Paperclip, agents, routines, skills, Claude Code, /loop,
  governance-vault, RAG).
- L'owner résume : « je n'arrivais pas à le faire fonctionner » (Marwane, 2026-11-14, 23:22, heure de
  Paris).

### Ce que le vault déclare encore

| Passage | État sur `main` au 2026-11-14 |
|---|---|
| [[ADR-012-aicos-vps-architecture\|ADR-012]] (accepted) | Architecture à trois machines (DEV, PROD, AI-COS), zone `aicos_vps`, spécifications de la machine AI-COS |
| [[ADR-034-aicos-operating-contract\|ADR-034]] (accepted le 2026-11-10) | « AI-COS est un observatoire isolé, pas un orchestrateur runtime » ; anti-patterns interdits « sur AI-COS » |
| [[REG-001-agents]] v2.4.0 | 28 agents du système AI-COS au statut `planned` |
| `ledger/agents/ai-cos/` | 28 fiches `status: planned` |
| [[AGENTS]] et [[claude-desktop-instructions]] | Tableau « 3-VPS Architecture » avec une ligne AI-COS |
| [[MOC-Agents]] | Zone `aicos_vps` peuplée par « AI-COS leads, C-Suite » |
| [[rules-ai-cos]] | Dix règles « que tout agent AI-COS DOIT respecter » |

[[ADR-101-vault-decides-canon-authority|ADR-101]] D3 traite une divergence entre une décision et
l'état réel par une PR de code ou par un ADR d'amendement. La machine est arrêtée ; cet ADR aligne le
vault.

## Décision

### D1 — La machine AI-COS est retirée ; l'architecture compte deux machines

- La machine AI-COS est arrêtée depuis octobre 2026 (jour exact inconnu). Elle n'est plus une zone
  d'exécution, d'observation ni de lecture du vault.
- L'architecture du projet compte **deux machines : DEV et PROD**. Les contraintes d'ADR-012 sur ces
  deux machines restent en vigueur : DEV est le seul point d'écriture en base par les agents ; PROD
  n'est atteinte que par `git push`, GitHub Actions et Docker.
- Dans ADR-012, ne s'appliquent plus : la troisième colonne du schéma « Architecture 3 Zones », la ligne
  `aicos_vps` de « Agent Placement Rules », la section « AI-COS VPS Specifications », les phases 4 et 5
  de « Airlock Integration » (dashboard AI-COS ; le canal de bundles est déjà retiré par
  [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]]) et les conséquences « nouvelle zone
  `aicos_vps` » et « REG-001 v3.0 avec zone `aicos_vps` ».
- La zone `aicos_vps` ne reçoit plus aucun agent. La valeur reste dans le schéma de validation de
  REG-001 pour lire l'historique.
- ADR-012 prévoyait pour cette machine un accès en lecture à Supabase (`service_role`), une clé SSH
  dédiée vers les logs de PROD (utilisateur `readonly`) et un clone du vault en HTTPS. Cet ADR ne
  vérifie ni ne révoque ces accès : leur état est inconnu et relève de l'owner (voir « Conséquences »).

### D2 — Le système d'agents AI-COS est retiré : 28 agents passent `disabled`

- Dans [[REG-001-agents]] et dans `ledger/agents/ai-cos/`, les 28 agents du système AI-COS passent de
  `planned` à `disabled` :
  - niveau 1 (C-Suite) : [[AGENT-agent-ceo-ia]], [[AGENT-agent-cfo-ia]], [[AGENT-agent-cmo-ia]],
    [[AGENT-agent-cpo-ia]], [[AGENT-agent-cto-ia]] ;
  - niveau 2 (leads et gouvernance) : [[AGENT-agent-aicos-architect]],
    [[AGENT-agent-aicos-governance]], [[AGENT-agent-qto]], [[AGENT-agent-seo-lead]],
    [[AGENT-agent-seo-content-lead]], [[AGENT-agent-seo-exec-lead]], [[AGENT-agent-seo-kp-lead]],
    [[AGENT-agent-seo-qa-lead]], [[AGENT-agent-data-lead]], [[AGENT-agent-rag-lead]],
    [[AGENT-front-agent]] ;
  - exécutants prévus sous Claude API ([[ADR-011-openclaw-claude-api-replacement|ADR-011]]) :
    [[AGENT-agent-data-backup]], [[AGENT-agent-data-cleanup]], [[AGENT-agent-data-validator]],
    [[AGENT-agent-infra-logs]], [[AGENT-agent-infra-monitor]], [[AGENT-agent-rag-indexer]],
    [[AGENT-agent-rag-retriever]], [[AGENT-agent-rag-validator]], [[AGENT-agent-seo-canonical]],
    [[AGENT-agent-seo-content]], [[AGENT-agent-seo-sitemap]], [[AGENT-agent-seo-vlevel]].
- Les fiches restent en place avec `status: disabled` et une ligne de retrait, comme les fiches BMAD
  d'ADR-118. Elles ne sont pas archivées sous `ledger/_archive/` : le dossier `ledger/agents/ai-cos/`
  héberge aussi 16 fiches actives (ci-dessous), et les déplacer changerait les chemins de liens sans
  gain de lecture. Les verdicts d'audit (`NOT_APPROVED`, `APPROVED_WITH_CONDITIONS`) ne sont pas
  réécrits ; avec le statut `disabled`, ils n'autorisent aucune exécution.
- **Ne sont pas retirés**, bien que rangés dans le même dossier :
  - les 4 agents QA ([[AGENT-agent-qa-orchestrator]], [[AGENT-agent-qa-functional]],
    [[AGENT-agent-qa-visual]], [[AGENT-agent-qa-seo-tech]]) : leur fiche les décrit exécutés par
    Bash et Playwright sur la machine PROD (`tests/qa-audit/qa-audit-cron.sh`), pas par AI-COS. Seule
    la mention du dashboard AI-COS qui lisait leurs résultats est alignée. Leur exécution réelle sur
    PROD n'est pas vérifiée par cet ADR ;
  - les 12 fiches `prompt-*` : agents Claude Code de la zone `local` (machine DEV).
- Ce retrait est une modification du catalogue, niveau G1 de
  [[ADR-013-agent-lifecycle-governance|ADR-013]]. Une réactivation suivrait le niveau G2 d'ADR-013, tel
  qu'amendé par ADR-102, et demanderait un ADR qui révoque D2.

### D3 — ADR-034 : amendement proposé (sort à trancher par l'owner)

**Proposition : amender ADR-034, ni le remplacer ni le retirer.** Le contrat des trois axes (Trigger,
Execution, Evidence), la discipline d'un déclencheur unique par routine et les anti-patterns d'AP-12
sont le contrat retenu pour l'organisation autonome des départements (mandat M, [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]], lui aussi
`proposed`). Aucun de ces
éléments ne dépend de la machine AI-COS.

| Passage d'ADR-034 | Lecture après ADR-129 |
|---|---|
| Décision : « AI-COS est un observatoire isolé, pas un orchestrateur runtime » | Sans objet pour la machine : il n'existe plus d'observatoire AI-COS. Les trois axes et la discipline d'un déclencheur unique s'appliquent à toute routine du projet. |
| Axe **Execution** : runner self-hosted DEV | Non amendé ici : [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] D7 en propose la nouvelle rédaction (runner auto-hébergé DEV, « AI-COS » désigne le contrat, pas une machine) et renvoie le retrait de la machine au présent ADR. Les deux amendements portent sur des passages distincts et ne se dupliquent pas. |
| « L'ajout sur AI-COS des composants suivants est interdit par défaut » | Se lit « l'ajout, sur toute machine ou tout dépôt du projet ». La liste des six composants est inchangée. |
| Conséquences neutres : « Paperclip continue d'évoluer hors monorepo (sur AI-COS) » | La mention du lieu ne s'applique plus. Le lieu d'exécution actuel de Paperclip n'est pas vérifié par cet ADR. |
| Critère de succès et revue : aucune nouvelle infra maison « sur AI-COS » | Se lit « sur aucune machine ni aucun dépôt du projet ». |

Le titre d'ADR-034 n'est pas modifié : il date le contrat et il est cité tel quel par le workflow de D6.

Options écartées pour ADR-034 :

- **Remplacer** par un nouvel ADR « contrat des départements » : le contenu du contrat vient d'être
  accepté (2026-11-10) et ne dépend pas de la machine ; un remplacement dupliquerait son texte.
- **Retirer** : supprimerait le seul verrou écrit contre un orchestrateur maison et rouvrirait la
  dérive qu'ADR-006 a produite.

### D4 — Conséquence pour chaque ADR qui cite AI-COS

| ADR | Statut | Passages concernés | Conséquence proposée |
|---|---|---|---|
| [[ADR-008-agent-placement-rules\|ADR-008]] | accepted | Lignes « AI-COS L1/L2 » et « AI-COS L3 » ; extension à quatre zones (`aicos_vps`) | **Amendé** : ces lignes et la zone `aicos_vps` sont sans objet |
| [[ADR-009-agents-phase1-activation\|ADR-009]] | accepted-revised | §2.2 lignes AI-COS L1 et L2 ; §2.3 listes des agents L1 et L2 ; §4.5 critère 5 (Phase 2 AI-COS) ; §5 action « Preparer criteres ADR Phase 2 » | **Amendé** : sans objet, les agents sont `disabled` (D2) |
| [[ADR-011-openclaw-claude-api-replacement\|ADR-011]] | accepted | §2.3 « Claude API (VPS AI-COS) » ; §3 ligne « VPS AI-COS (nouveau) — PLANIFIE » ; risque « ai-cos-system » ; phases B.3 et C.1 | **Amendé** : la machine et l'orchestrateur `ai-cos-system` sont sans objet ; le reste de la décision est inchangé |
| [[ADR-012-aicos-vps-architecture\|ADR-012]] | accepted | Architecture, placement, spécifications, Airlock phases 4–5, conséquences | **Amendé** : deux machines, DEV et PROD (D1) |
| [[ADR-015-vault-single-source-of-truth\|ADR-015]] | accepted | Justification point 3 « Alignement AI-COS » ; conséquence « AI-COS VPS peut consulter… » ; critère « AI-COS consomme effectivement le vault » | **Amendé** sur ces seuls passages, sans objet ; la décision (vault source unique) est inchangée |
| [[ADR-034-aicos-operating-contract\|ADR-034]] | accepted | Voir D3 | **Amendé** (proposition D3) |
| [[ADR-013-agent-lifecycle-governance\|ADR-013]] | accepted | « 11-agent-catalog.md (si agent AI-COS) » | **Inchangé** : mention en passant d'un chemin v1 |
| [[ADR-019-ai-content-advisor-escalation\|ADR-019]] | accepted | `excluded_paths` : « pipelines skills-first sur AI-COS » | **Inchangé** : la mention sert à exclure du périmètre |
| [[ADR-028-preprod-supabase-isolation\|ADR-028]] | accepted | Alignement déclaré sur ADR-034 | **Inchangé** : le contrat d'ADR-034 est conservé (D3) |
| [[ADR-031-four-layer-content-architecture\|ADR-031]] | accepted | Référence « VPS architecture 3-tiers (DEV/PROD/AI-COS) » | **Inchangé** : ligne de référence, se lit avec D1 |
| [[ADR-036-marketing-operating-layer\|ADR-036]] | accepted | Référence à AI2 et AI4 | **Inchangé** tant qu'AI2 et AI4 sont conservées ; si AI4 est réattribuée (D5), la référence se lit avec la nouvelle attribution |
| [[ADR-053-planning-live-system\|ADR-053]] | accepted | Référence « ADR-034 AI-COS Operating Contract » | **Inchangé** : cite le titre d'ADR-034 |
| [[ADR-077-diagnostic-cp-v1-evidence-gates\|ADR-077]] | accepted | « mémoire AI-COS volatile » ; « rotation agents AI-COS » | **Inchangé** : récit daté du contexte |
| [[ADR-101-vault-decides-canon-authority\|ADR-101]] | accepted | Nom de la section « AI-COS Governance » de [[rules-technical]] | **Inchangé** : se lit avec le libellé que retiendra D5 |
| [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4\|ADR-102]] | accepted | Citations d'ADR-012 | **Inchangé** |
| ADR-006, ADR-026 (superseded), ADR-029 (rejected) | non normatifs | Récits et références | **Inchangés** : historique |

Au commit de ratification, `amended_by` reçoit `ADR-129` dans ADR-008, ADR-009, ADR-011, ADR-012,
ADR-015 et ADR-034. Leur corps reste tel qu'il a été accepté.

### D5 — Règles AI1 à AI10 et règles voisines : propositions (aucun texte de règle modifié)

Aucune des dix règles ne vise la seule machine. AI5 a pour objet l'organigramme du système retiré ;
AI2, AI4, AI8 et AI9 nomment un agent ou un mécanisme retiré, mais leur principe vaut pour tout agent IA ;
les autres valent telles quelles pour tout agent IA. **Proposition** : conserver [[rules-ai-cos]] comme règles de tout
agent IA du projet, sous le titre « Règles d'or des agents IA », en gardant le nom du fichier (aucun
lien ne change). Le texte des règles n'est modifié qu'après ratification, dans une PR qui reste en
brouillon jusque-là (ADR-121 D7).

| Règle | Ce qu'elle vise | Proposition |
|---|---|---|
| Axiome zéro | Tout agent IA | Conserver |
| AI1 (pas de KPI = suppression) | Tout agent du catalogue | Conserver. Constat : le champ `metric_id` qu'elle vérifie n'existe dans aucune fiche ; le moyen de mesure reste à définir |
| AI2 (l'IA propose, l'humain décide) | Tout agent IA ; son libellé nomme l'« IA-CEO », agent retiré | Conserver ; libellé « un agent IA propose, l'humain décide » |
| AI3 (doute = blocage) | Tout agent IA | Conserver |
| AI4 (pas de production sans validation) | Tout agent IA ; nomme le QTO, agent retiré | Conserver le principe ; réattribuer la validation du QTO à une validation humaine ou à un contrôle désigné, au choix de l'owner |
| AI5 (aucun agent hors hiérarchie) | Organigramme du système retiré (`reports_to`, `sponsor`, `squad`, C-Level) | Reformuler : tout agent a un propriétaire humain désigné (champ `owner` des fiches) ; ou retirer, au choix de l'owner |
| AI6 (1 création = 1 fusion ou suppression) | Tout agent du catalogue | Conserver |
| AI7 (diagnostic = multi-validation) | Tout agent IA | Conserver |
| AI8 (contenu critique = QTO) | Tout agent IA ; nomme le QTO | Comme AI4 : conserver, réattribuer le rôle du QTO |
| AI9 (kill-switch N1 à N3, Human CEO) | Tout agent IA pour le principe (seul l'humain arrête) ; les niveaux N1 à N3 décrivaient le système retiré, et ADR-102 D4 a retiré le kill-switch d'écriture du vault | Conserver le principe, « Human CEO » lu « owner ». Pour les niveaux : soit les gestes natifs N1 à N3 que propose [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] D6 (arrêt du runner DEV, désactivation d'un workflow, gel d'un mandat), si l'owner ratifie ADR-128 ; soit un renvoi à la réponse à incident de G4 ([[rules-vault]]). Au choix de l'owner |
| AI10 (traçabilité obligatoire) | Tout agent IA | Conserver |

Règles et policy voisines (propositions, non appliquées) :

- **AP-12** ([[rules-ai-antipatterns]]) : conserver ; « sur AI-COS » devient « sur toute machine ou
  tout dépôt du projet », et l'en-tête « Patterns interdits dans le système AI-COS » devient « Patterns
  interdits pour les agents IA du projet ». AP-01 à AP-11 ne sont pas réexaminés ici.
- **[[rules-technical]]**, section « AI-COS Governance » : contenu générique (axiome zéro, règle d'or,
  niveaux de vérité) ; renommer la section « Gouvernance des agents IA ».
- **[[rules-marketing-voice]]**, référence « ADR-012 — 3-VPS architecture (DEV vault SoT, PROD/AI-COS
  read-only) » : devient « ADR-012 — architecture DEV et PROD (amendée par ADR-129) ». Ce fichier est
  publié vers le monorepo par `canon-publish` ; le modifier ouvre une PR de miroir dans le monorepo.
  La ligne voisine « AI4 QTO valide AVANT publication » suit le sort d'AI4.
- **[[PROCESS-G1-design]]** (policy) : la condition « si agent AI-COS Level 2+ » devient sans objet.
- [[rules-vault]] et [[rules-governance-process]] citent `rules-ai-cos.md` : inchangés si le nom du
  fichier est conservé.

### D6 — Workflow `vault-supabase-cost-check.yml` : mention descriptive, sans correction

La ligne `echo "- ADR-034 — AI-COS Operating Contract (3 axes Trigger/Execution/Evidence)"` écrit une
référence dans le rapport de la routine. Elle est **descriptive** : aucune étape ne dépend de cette
chaîne. Elle cite le titre exact d'ADR-034, que D3 conserve ; elle ne présente pas AI-COS comme une
machine active. Elle n'appelle donc aucune correction. Le dossier `.github/` est réservé à l'owner
(G4).

### D7 — Historique conservé

Ne sont pas réécrits : `ledger/_archive/`, `ledger/audit-trail/`, `ledger/incidents/`,
`ledger/compliance/`, `ledger/knowledge/`, les snapshots, `99-meta/reports/` et `99-meta/sync-log.md`,
ni ADR-006, ADR-026 et ADR-029. Ils racontent ce qui a été, à leur date.

## Options considérées

- **A — Amender et désactiver (retenue).** Les ADR et documents vivants décrivent les deux machines
  réelles ; les fiches et verdicts restent lisibles comme historique ; le contrat d'ADR-034 et les
  règles AI survivent à la machine, sous réserve des propositions D3 et D5.
- **B — Remplacer ADR-012 et ADR-034 par de nouveaux ADR.** Réécrit des décisions dont l'essentiel
  reste valable (contraintes DEV et PROD, contrat des trois axes) et multiplie les références à suivre.
- **C — Archiver tout le dossier `ledger/agents/ai-cos/` et `rules-ai-cos` (G8).** Archiverait aussi les
  16 fiches actives et des règles qui valent pour tout agent IA.
- **D — Ne rien faire.** Le vault continuerait de décrire une machine arrêtée et 28 agents prévus,
  contrairement à ADR-101 D3.

## Ce que cet ADR NE fait PAS

- Il ne date pas l'arrêt de la machine au-delà du mois d'octobre 2026.
- Il ne vérifie ni ne révoque les accès que la machine détenait (lecture Supabase, clé SSH vers les
  logs de PROD, jeton GitHub éventuel) et n'agit sur aucune machine, DEV ou PROD.
- Il ne modifie ni le monorepo, ni Paperclip, ni le texte d'aucune règle ou policy (propositions D5).
- Il ne réécrit pas le corps des ADR amendés et ne supprime aucune fiche ni aucun verdict.
- Il ne décide pas seul du sort d'ADR-034 ni d'AI1 à AI10 : il le propose ; l'owner tranche à la
  ratification.
- Il ne modifie pas `.github/` (D6).

## Conséquences

### Positives

- Un agent qui lit le vault trouve deux machines, DEV et PROD, et aucun agent AI-COS prévu.
- Le contrat d'ADR-034 reste disponible pour l'organisation autonome des départements.

### Négatives

- Jusqu'à l'application des propositions D5, [[rules-ai-cos]], [[rules-ai-antipatterns]],
  [[rules-technical]], [[rules-marketing-voice]] et [[PROCESS-G1-design]] gardent le nom AI-COS dans
  leur texte.
- Le dossier `ledger/agents/ai-cos/` garde son nom alors qu'il ne contient plus d'agent du système
  AI-COS actif ; l'index le signale.

### Neutres

- `total_agents: 144` et les compteurs par verdict de REG-001 ne changent pas.
- À traiter par l'owner, hors de cet ADR : confirmer la révocation des accès de la machine AI-COS
  (D1) ; vérifier l'exécution des 4 agents QA sur PROD (D2).

## Critères de succès

- `git grep -n -E '^status: planned' -- ledger/agents/ai-cos/` ne renvoie rien.
- Dans `ledger/agents/registry/REG-001-agents.md`, aucun agent du système AI-COS ne porte le statut
  `planned`.
- [[AGENTS]], [[claude-desktop-instructions]] et [[MOC-Agents]] ne décrivent plus de machine AI-COS.
- `_scripts/check-adr-supersedes.py` ne signale pas d'asymétrie `amends`/`amended_by` après la
  ratification, et `_scripts/ci-vault-gate.sh pr` est vert.

## Mise en œuvre (cette PR)

| Fichier | Changement |
|---|---|
| `ledger/decisions/adr/ADR-129-retrait-ai-cos-machine-systeme-agents.md` | Cet ADR |
| `ledger/agents/ai-cos/AGENT-*.md` (28 fiches) | `status: disabled`, ligne Status du corps, ligne de retrait |
| `ledger/agents/ai-cos/AGENT-agent-qa-orchestrator.md` | Mention du dashboard AI-COS alignée |
| `ledger/agents/ai-cos/INDEX-agents-ai-cos.md` | Bannière de retrait, trois groupes |
| `ledger/agents/registry/REG-001-agents.md` | 28 agents `disabled`, couverture par domaine, note, ADR liés, v2.5.0 |
| `AGENTS.md` | Liste des agents et architecture à deux machines |
| `99-meta/onboarding/claude-desktop-instructions.md` | Architecture à deux machines |
| `ops/moc/MOC-Agents.md` | Zones, catégorie AI-COS, ADR-012 |
| `ops/moc/MOC-Decisions.md` | Index régénéré par `_scripts/sync_moc_decisions.py --write` |

Le commit de ratification ajoute `amended_by: ADR-129` aux six ADR de D4, passe cet ADR à `accepted`,
renseigne `decision_date` et la ligne « Accepté le », régénère [[MOC-Decisions]] et retire de la PR les
mentions qui suspendent l'entrée en vigueur. Il consigne aussi l'option retenue pour D3 et pour
chaque règle de D5.

## Revue planifiée

À l'application des propositions D5 : vérifier que plus aucun document vivant ne cite AI-COS comme
machine ou système actif.

## Annexe A — Inventaire des documents vivants qui citent AI-COS (2026-11-14)

Recherche : motif `(?i)ai[-_ ]?cos` sur `main` (`9f7a6ee`), hors `ledger/_archive/`, `ledger/audit-trail/`,
`ledger/incidents/`, `ledger/compliance/`, `ledger/knowledge/`, snapshots, `99-meta/reports/` et
`99-meta/sync-log.md`. Résultat : **64 fichiers**. S'y ajoutent 12 fiches du système qui ne citent
pas le nom (exécutants Claude API de D2).
Depuis le relevé, [[ADR-128-departements-autonomes-coordonnes-file-github|ADR-128]] (fusionné le
2026-11-14, `proposed`) cite AI-COS comme contrat d'exploitation et précise qu'aucune routine ne
s'exécute sur la machine AI-COS : classe P, aucun traitement.

Classes : **M** machine ; **S** système d'agents ; **R** règle AI ; **P** nom en passant.

| Fichier | Classe | Traitement |
|---|---|---|
| `ledger/decisions/adr/ADR-012-aicos-vps-architecture.md` | M | Amendé (D1, D4), frontmatter à la ratification |
| `ledger/decisions/adr/ADR-011-openclaw-claude-api-replacement.md` | M | Amendé (D4) |
| `ledger/decisions/adr/ADR-015-vault-single-source-of-truth.md` | M | Amendé (D4) |
| `ledger/decisions/adr/ADR-008-agent-placement-rules.md` | M | Amendé (D4) |
| `AGENTS.md` | M | Aligné dans cette PR |
| `99-meta/onboarding/claude-desktop-instructions.md` | M | Aligné dans cette PR |
| `ops/moc/MOC-Agents.md` | M | Aligné dans cette PR |
| `ledger/rules/rules-marketing-voice.md` | M | Proposition D5, non appliquée |
| `ledger/decisions/adr/ADR-031-four-layer-content-architecture.md` | P | Inchangé (D4) |
| `ledger/decisions/adr/ADR-026-content-separation.md` | P | Inchangé, historique (superseded) |
| `ledger/decisions/adr/ADR-034-aicos-operating-contract.md` | S | Amendé, proposition D3 |
| `ledger/decisions/adr/ADR-009-agents-phase1-activation.md` | S | Amendé (D4) |
| `ledger/decisions/adr/ADR-006-ai-orchestrator-architecture.md` | S | Inchangé, historique (superseded) |
| `ledger/agents/registry/REG-001-agents.md` | S | Aligné dans cette PR |
| `ledger/agents/ai-cos/INDEX-agents-ai-cos.md` | S | Aligné dans cette PR |
| 16 fiches `ledger/agents/ai-cos/AGENT-*` qui citent le nom (aicos-architect, aicos-governance, ceo-ia, cfo-ia, cmo-ia, cpo-ia, cto-ia, data-lead, qto, rag-lead, seo-content-lead, seo-exec-lead, seo-kp-lead, seo-lead, seo-qa-lead, front-agent) | S | `disabled` dans cette PR (D2) |
| `ledger/agents/ai-cos/AGENT-agent-qa-orchestrator.md` | S | Agent conservé ; mention du dashboard alignée |
| `ledger/policies/PROCESS-G1-design.md` | S | Proposition D5, non appliquée |
| `ledger/rules/rules-ai-cos.md` | R | Proposition D5, non appliquée |
| `ledger/rules/rules-ai-antipatterns.md` | R | Proposition D5 (AP-12, en-tête), non appliquée |
| `ledger/rules/rules-technical.md` | R | Proposition D5 (titre de section), non appliquée |
| `ledger/decisions/adr/ADR-036-marketing-operating-layer.md` | R | Inchangé (D4) |
| `ledger/rules/rules-vault.md` | P | Inchangé |
| `ledger/rules/rules-governance-process.md` | P | Inchangé |
| `_templates/rule-template.md` | P | Inchangé : valeur `ai-cos` de `category`, nom d'une famille de règles |
| 10 index `ledger/agents/*/INDEX-agents-*.md` (backend, bmad, bundles, github-actions, lettered, mcp, python, registry, scripts, skills) | P | Inchangés : lien vers [[rules-ai-cos]] |
| `ledger/decisions/adr/ADR-013-agent-lifecycle-governance.md` | P | Inchangé (D4) |
| `ledger/decisions/adr/ADR-019-ai-content-advisor-escalation.md` | P | Inchangé (D4) |
| `ledger/decisions/adr/ADR-028-preprod-supabase-isolation.md` | P | Inchangé (D4) |
| `ledger/decisions/adr/ADR-029-rag-v2.1-control-plane-closure.md` | P | Inchangé, historique (rejected) |
| `ledger/decisions/adr/ADR-053-planning-live-system.md` | P | Inchangé (D4) |
| `ledger/decisions/adr/ADR-077-diagnostic-cp-v1-evidence-gates.md` | P | Inchangé (D4) |
| `ledger/decisions/adr/ADR-101-vault-decides-canon-authority.md` | P | Inchangé (D4) |
| `ledger/decisions/adr/ADR-102-airlock-rpc-gate-bundle-channel-retired-g4.md` | P | Inchangé (D4) |
| `ops/moc/MOC-Decisions.md` | P | Index régénéré ; partie rédigée inchangée |
| `ops/moc/MOC-Rules.md` | P | Inchangé : nomme la famille de règles AI ; libellé à revoir avec D5 |
| `ops/moc/MOC-Knowledge.md` | P | Inchangé : indexe des documents historiques de `ledger/knowledge/` |
| `ops/moc/MOC-Roadmap-2026.md` | P | Inchangé : liens vers ADR-034 |
| `ops/moc/MOC-AuditTrail.md` | P | Inchangé : entrée d'historique |
| `.github/workflows/vault-supabase-cost-check.yml` | P | Inchangé : mention descriptive exacte (D6) |

---

_Proposé le : 2026-11-14_
_Accepté le : —_
_Dernière revue : 2026-11-14_
