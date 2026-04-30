---
id: ADR-034
title: "AI-COS Operating Contract — Observatory + Single-Trigger Routines"
status: proposed
date: 2026-04-30
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
related_rules: ["AP-12", "Q1", "Q4", "AEC"]
related_incidents: []
related_adr: ["ADR-006", "ADR-011", "ADR-012", "ADR-015", "ADR-020", "ADR-025", "ADR-028", "ADR-036"]
reviewed_by: ""
---

# ADR-034: AI-COS Operating Contract — Observatory + Single-Trigger Routines

## Contexte

Le 2026-04-30, lors d'une session de revue d'architecture, une dérive conceptuelle persistante a été identifiée : huit concepts opérationnels coexistent sans hiérarchie claire (AI-COS, Paperclip, agents, routines, skills, Claude Code, /loop, governance-vault, RAG). Au cours de la même session, un premier plan rev1 a été spontanément orienté vers la reconstruction d'un orchestrateur maison sur AI-COS — bus événementiel, scheduler daemon, registry agent, dashboard custom — alors que l'utilisateur (Human CEO) avait précisément demandé "no bricolage, best solutions".

Historique :

- [[ADR-006-ai-orchestrator-architecture]] (proposed 2026-02-03) prévoyait un orchestrateur LangGraph + JobEnvelope + RAG + Skills sur AI-COS. **Jamais construit.** Superseded par [[ADR-011-openclaw-claude-api-replacement]] + [[ADR-025-seo-department-architecture]] (de facto joint coverage, MOC-Decisions 2026-04-27).
- [[ADR-012-aicos-vps-architecture]] (accepted 2026-03-08) a déjà cadré AI-COS comme une 4ème zone (observatoire), mais **sans verrou anti-dérive** : rien n'empêche un agent ou une session future de relancer un chantier orchestrateur maison.
- [[ADR-020-weekly-vault-lint]] (accepted 2026-04-23) a livré la **première routine opérationnelle LIVE** dans le pattern cible : GitHub Actions cron + artifact + diff vs previous + issue NEW-only. Le template existe, il fonctionne, il n'est pas exploité au-delà.
- [[ADR-036-marketing-operating-layer]] (proposed 2026-04-30, mergé sur `main` peu avant cet ADR via PR #113) applique déjà empiriquement plusieurs morceaux du contrat ci-dessous (extension OperatingMatrixService, dual-workspace `workspaces/marketing/`, single Paperclip routine, canon-publish brand voice). Cet ADR-034 codifie le contrat que ADR-036 valide en pratique.

État au 2026-04-30 :

- 119 agents catalogués dans [[MOC-Agents]] (44 AI-COS, 19 backend, 15 Python, 14 skills, etc.) — **pas de drift agents**, c'est le drift *infrastructure orchestrante* qui pose problème.
- 0 MOC-Routines existante. Les routines opérationnelles ne sont pas tracées comme catégorie distincte.
- 1 routine LIVE (`weekly-vault-lint`), 0 autre routine en pipeline figée hors marketing.
- 27 branches feature locales touchent des ADRs déjà mergés — signe d'hygiène manquante mais hors scope direct.

Le risque sans cet ADR : un futur agent (Claude Code session, Cowork, Codex) rebricolera un orchestrateur maison parce que rien d'écrit ne l'interdit explicitement. Ce qui aurait été perdu : Claude Code routines, Paperclip cockpit, GitHub Actions cron+webhooks, vault audit-trail markdown, GH issues — primitives natives qui couvrent déjà 95 % des besoins.

## Décision

**AI-COS est un observatoire isolé, pas un orchestrateur runtime.** Les opérations transverses se structurent autour de **3 axes figés** et d'une **single-trigger discipline**.

### Architecture canonique (3 axes)

| Axe | Outil unique autorisé | Source de vérité |
|---|---|---|
| **Trigger** | GitHub Actions cron OU webhook (`workflow_dispatch`, `repository_dispatch`) | `.github/workflows/*.yml` (front-matter `routine:` schema) |
| **Execution** | Self-hosted runner DEV → Claude Code SDK / scripts Python / MCP Supabase / `gh api` | Code dans monorepo ou vault `_scripts/` |
| **Evidence** | Artifact GitHub (retention 90j) + audit-trail markdown vault + issue P0/P1 si NEW finding | `governance-vault/ledger/audit-trail/YYYY-MM-DD-*.md` |

### Single-trigger discipline

Chaque routine a **un et un seul** déclencheur. Pas de double-trigger (cron GitHub + Paperclip routine + cron Linux pour le même job). La règle se documente dans le front-matter `routine:` du workflow YAML.

### Anti-patterns figés

L'ajout sur AI-COS des composants suivants est interdit par défaut (override = ouvrir un ADR explicite, pas un patch silencieux) :

1. Bus événementiel maison
2. Scheduler daemon maison
3. Registry agent maison ([[MOC-Agents]] existe déjà)
4. Moteur de permissions maison
5. Dashboard custom maison (Paperclip cockpit + GitHub Actions UI suffisent)
6. Orchestrateur LangGraph / JobEnvelope maison (vision [[ADR-006-ai-orchestrator-architecture]] superseded, ne pas resusciter)

Le pattern est codifié dans la nouvelle règle [[rules-ai-antipatterns#AP-12]].

### Healthchecks.io comme dead-man switch externe

Adopté **optionnellement** : si une routine définit la variable `HEALTHCHECKS_<routine>_URL` dans gh secrets vault, elle ping cette URL après run réussi. Si la variable n'existe pas, skip propre. Pas obligatoire en V1 — la cron GitHub elle-même suffit à détecter une exécution ratée via les notifications GitHub Actions.

### MOC-Routines auto-générée (en P2, pas bloquante)

La matrice des routines vit dans `governance-vault/ops/moc/MOC-Routines.md`, **régénérée automatiquement** à chaque merge depuis le front-matter YAML `routine:` des workflows (vault + monorepo + autres repos via `gh api`). Pas de doc manuelle qui pourrit. Implémentation différée à PR séparée (P2 du plan AI-COS rev5).

## Options Considérées

### Option A: Reconstruire un orchestrateur maison sur AI-COS (vision originale ADR-006)

**Description** : LangGraph + JobEnvelope + bus événementiel + scheduler + registry agent + dashboard custom, comme prévu dans [[ADR-006-ai-orchestrator-architecture]] proposed 2026-02-03.

**Avantages** :
- Cohésion conceptuelle d'un système sur mesure
- Contrôle fin de chaque primitive

**Inconvénients** :
- ADR-006 superseded — la vision a déjà été abandonnée empiriquement (jamais construite en 3 mois)
- Duplique des primitives natives qui marchent (GitHub Actions, Paperclip, Claude Code SDK)
- Aucune équipe pour maintenir un système maison à long terme
- Le coût de maintenance (debug, doc, formation, alertes) > bénéfice incrémental
- Incidents répétés de dérive conceptuelle (8 concepts non hiérarchisés)

### Option B: Tout faire via Claude Code CLI sans structure (zero infra)

**Description** : pas de routines formalisées, l'utilisateur lance les checks à la main via Claude Code quand il en a besoin.

**Avantages** :
- Coût zéro
- Zéro maintenance

**Inconvénients** :
- Pas d'observabilité centralisée — impossible de savoir si un check est passé hier
- Pas de single-trigger discipline — chacun lance ce qu'il veut
- Pas d'évidence durable (audit-trail) — perdu après la session
- Dépendance forte à la mémoire et la discipline de l'utilisateur

### Option C: AI-COS = observatoire + 3 axes figés + single-trigger discipline (retenue)

**Description** : codifier que AI-COS n'est PAS un orchestrateur runtime, qu'il s'appuie sur les primitives natives existantes (GitHub Actions, Paperclip, Claude Code SDK, vault audit-trail), et que les routines suivent le pattern [[ADR-020-weekly-vault-lint]] livré et éprouvé.

**Avantages** :
- Coût zéro infra ajoutée (réutilise GitHub Actions runner self-hosted DEV + vault Git + Paperclip existant)
- Anti-dérive durable via [[rules-ai-antipatterns#AP-12]]
- S'appuie sur un pattern déjà LIVE et testé ([[ADR-020-weekly-vault-lint]])
- Validation empirique : [[ADR-036-marketing-operating-layer]] applique déjà ce contrat (extension OperatingMatrixService, dual-workspace, single Paperclip routine `rt-local-gbp-week`, canon-publish brand voice)
- Auto-MOC garantit qu'aucune routine ne devient invisible
- Single-owner-per-concern : Trigger = GHA, Execution = runner DEV, Evidence = vault — chaque axe a un et un seul propriétaire

**Inconvénients** :
- Contrainte explicite sur futurs agents (AP-12 rule à respecter avant toute proposition d'infra AI-COS)
- Healthchecks.io = dépendance externe optionnelle (mitigée par "skip propre si non configuré")
- Demande discipline auteur PR (front-matter `routine:` à remplir)

## Justification

L'option C est retenue pour 5 raisons mesurables :

1. **Primitives natives suffisent** : GitHub Actions cron (trigger) + self-hosted runner DEV (execution) + Claude Code SDK / Python / MCP Supabase (logic) + GHA artifacts + vault Git audit-trail markdown + GH issues (evidence). Tous existent déjà, payés, opérationnels. Ajouter un orchestrateur maison = travail sans bénéfice incrémental.

2. **Pattern éprouvé** : [[ADR-020-weekly-vault-lint]] LIVE depuis 2026-04-23. Workflow `vault-weekly-lint.yml` réutilisable directement comme template (artifact upload, diff vs previous, issue NEW-only, retention 90j, concurrency `vault-write`). Le seul travail = dupliquer + adapter l'input.

3. **Anti-dérive enforce-able** : la règle [[rules-ai-antipatterns#AP-12]] est checkable manuellement par tout reviewer PR ("est-ce que cette PR construit un bus événementiel maison ? un scheduler ? un dashboard ?"). Pas de surface code à maintenir.

4. **Cohérent ADR-015 (vault SoT)** : 3 axes alignés sur la séparation existante : décision = vault, code = monorepo, evidence = vault audit-trail. Pas de nouvelle catégorie inventée.

5. **Validation empirique préexistante** : [[ADR-036-marketing-operating-layer]] (mergé sur main 2026-04-30) applique déjà le contrat avant qu'il soit codifié — extension `OperatingMatrixService` (Module.MARKETING enum), workspace dédié `workspaces/marketing/.claude/agents/` (3 agents G1 LEAD/LOCAL/RETENTION), single Paperclip routine `rt-local-gbp-week`, canon-publish `rules-marketing-voice` vers monorepo. Cet ADR-034 ne crée pas le contrat — il le rend explicite et anti-bricolable.

## Conséquences

### Positives

- 8 concepts (AI-COS, Paperclip, agents, routines, skills, Claude Code, /loop, RAG) hiérarchisés en 3 axes opérationnels — réduction cognitive substantielle pour onboarding et debug
- Anti-dérive durable via [[rules-ai-antipatterns#AP-12]] : tout futur agent qui veut construire un orchestrateur maison se heurte à une règle écrite, pas à une convention orale
- Auto-MOC élimine la dette doc (la matrice ne peut PAS pourrir car régénérée — voir [[ADR-020-weekly-vault-lint]] pattern)
- Coût zéro infra ajoutée (utilise GitHub Actions runner self-hosted DEV + vault Git + Paperclip existant)
- Alignement [[ADR-015-vault-single-source-of-truth]] (vault = mémoire) + [[ADR-020-weekly-vault-lint]] (1ère routine pattern) + [[ADR-036-marketing-operating-layer]] (2ème extension validée)
- Possibilité de `weekly-vault-lint` extension pour flagger les routines sans front-matter `routine:` valide (audit auto)

### Négatives

- Discipline auteur PR : remplir le front-matter `routine:` correctement à chaque nouveau workflow (mitigeable via lint en P2)
- Healthchecks.io = dépendance externe si activée (mitigée par "skip propre si secret absent" et caractère optionnel V1)
- L'AP-12 peut être perçue comme rigide par un agent qui voudrait innover — c'est précisément le verrou voulu

### Neutres

- Paperclip continue d'évoluer hors monorepo (sur AI-COS) sans contrainte additionnelle de cet ADR — Paperclip est un cockpit existant, pas un orchestrateur runtime maison
- Les 39 agents R*-batch dans `app/workspaces/seo-batch/.claude/agents/` restent des fiches Claude Code statiques `.md` (pas Paperclip dynamic agents) — inchangé
- ADR-006 reste superseded ; cet ADR-034 ne le remplace pas formellement, il fige seulement ce que la supersession implique pour AI-COS

## Critères de Succès

- [ ] AP-12 ajouté à `rules-ai-antipatterns.md` pointant vers ADR-034 (cette PR)
- [ ] MOC-Decisions entrée ADR-034 ajoutée + note ligne 56 ("ADR-034, ADR-035 réservés à drafts en cours") mise à jour pour retirer ADR-034 (cette PR)
- [ ] MOC-Rules.md ligne 56 actualisée à "AP-01 a AP-12" (cette PR)
- [ ] PR ADR-028 réécrit Option D (read-only hardening, $0/mois) mergée — PR 3 du plan AI-COS rev5
- [ ] 1 routine pilote `supabase-cost-check` LIVE et stable ≥1 semaine — PR 4 du plan
- [ ] `_scripts/generate-moc-routines.py` créé + `MOC-Routines.md` généré automatiquement (P2)
- [ ] Aucune nouvelle "infra orchestrateur maison" introduite sur AI-COS au cours des 90 prochains jours, mesuré via extension `weekly-vault-lint` (follow-up à tracer)

## Implémentation

Plan détaillé : `/home/deploy/.claude/plans/harmonic-mapping-elephant.md` (rev5, 2026-04-30, "no-bricolage best-solutions" iteration verrouillée par 4 conditions + worktree-only execution).

Ordre des PRs (séquence figée) :

| Ordre | Repo | Branche | Contenu | Dépendance |
|---|---|---|---|---|
| 1 | governance-vault | `feat/adr-034-aicos-operating-contract` | **Cette PR** : ADR-034 + AP-12 + MOC-Decisions + MOC-Rules | Aucune |
| 2 | nestjs-remix-monorepo | `feat/preprod-readonly-hardening` | `ci.yml` retire `ALLOW_PROD_ENV_COPY` + anon key only + READ_ONLY guard backend + write-detect job + RPC whitelist | PR 1 mergée |
| 3 | governance-vault | `feat/adr-028-readonly-hardening-option-d` | ADR-028 réécrit directement Option D (préserve Options A/B/C historiques) + audit-trail `related_adr` updated | PR 2 mergée |
| 4 | governance-vault | `feat/routine-supabase-cost-check-v1` | Routine V1 simple + secret `SUPABASE_ACCESS_TOKEN` setup + endpoint Management API documenté | PR 3 mergée |
| Parallèle | governance-vault | `feat/adr-030-npm-ignore-scripts-formalize` | ADR-030 npm-ignore-scripts standalone (extracted from ex-PR #111 fermée 2026-04-30) | Aucune (peut être fait en parallèle) |
| 5+ | governance-vault | `feat/auto-moc-routines` puis `feat/healthchecks-deadman-optional` | Auto-MOC + Healthchecks.io optionnel | PR 4 stable ≥1 semaine |

Cette PR (PR 1) ne contient **aucun code** — uniquement gouvernance (ADR + rule + 2 MOCs).

## Revue Planifiée

**Date** : 2026-07-30 (3 mois post-merge)

**Critères de revue** :
- Routine `supabase-cost-check` LIVE et stable depuis ≥2 mois (mesure réelle vs projection théorique)
- Aucune dérive vers infra maison observée sur AI-COS pendant la période (extension `weekly-vault-lint` à activer)
- MOC-Routines auto-générée fonctionne sans intervention manuelle
- Si AP-12 a effectivement bloqué des tentations (nombre de PRs refusées, ADRs ouverts pour override)
- Si Healthchecks.io a été activé spontanément (signal de besoin réel) ou pas (signal qu'il était bien optionnel)
- Si [[ADR-036-marketing-operating-layer]] continue à respecter le contrat (3 axes + single-trigger) ou si la pression métier a forcé des écarts — auquel cas mettre à jour cet ADR-034 avec les leçons apprises

---

*Proposé le: 2026-04-30*
*Accepté le: TBD (en attente revue Human CEO)*
*Dernière revue: 2026-04-30*
