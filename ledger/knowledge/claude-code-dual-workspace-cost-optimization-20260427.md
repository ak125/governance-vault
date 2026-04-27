---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: Claude Code — split workspace dev/SEO + cost optimization
slug: claude-code-dual-workspace-cost-optimization
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-27"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/nestjs-remix-monorepo#200"
  - "ak125/nestjs-remix-monorepo#201"
  - "ak125/nestjs-remix-monorepo#202"
status: current
tags:
  - claude-code
  - cost-optimization
  - workspace
  - skills
  - agents
---

# Claude Code — split workspace dev/SEO + cost optimization

> Session debrief 2026-04-27. Diagnostic + 3 PRs structurelles pour réduire la
> conso tokens du harness Claude Code sur les sessions dev daily du monorepo
> AutoMecanik, sans toucher à `effortLevel: xhigh` (recommandation Claude /
> Fleet Advisor).

## 1. Contexte / problème

Le `.claude/` racine du monorepo accumulait au fil des mois :

- **40 agents** R0-R8 (`r0-home-execution`, `r1-keyword-planner`, …, `r8-vehicle-validator`)
- **24 skills** (16 SEO + 8 DEV mélangés)
- **7 plugins user-level** activés (`superpowers`, `github`, `goodmem`, `context7`,
  `claude-md-management`, `remember`, `skill-creator`)
- **MCP servers** (Supabase ×2 doublon, Cloudflare, Gmail, Calendar, Drive, etc.)
- **5 hooks** PreToolUse + 1 PostToolUse + 1 Stop

Conséquence : ~30-50 K tokens de system prompt + tool catalog + system-reminder
rechargés à **chaque tour**, **avant même** la question utilisateur. Avec
`effortLevel: xhigh` (recommandation Claude pour Opus 4.7 1M), chaque tour
payait du raisonnement étendu sur ce contexte gonflé, y compris pour des Q&A
descriptives.

Symptôme utilisateur : *"le LLM consomme trop de tokens malgré vault, CLAUDE.md
slim, MEMORY.md sous 200 lignes"*.

## 2. Diagnostic — sources de bloat objectivées

| Source | Volume | Loaded à chaque tour ? |
|--------|--------|------------------------|
| `.claude/agents/*.md` (40 agents SEO-batch) | 424K source | ✅ descriptions injectées dans `Agent` tool catalog |
| `.claude/skills/` (24 skills) | 924K source | ✅ noms+descriptions dans system-reminder |
| `~/.claude/skills/` globaux + 7 plugins skills | ~50 entrées | ✅ chaque plugin pousse ses skills |
| MCP doublon Supabase (`mcp__supabase__*` + `mcp__claude_ai_Supabase__*`) | 60 outils | ✅ schemas déférés |
| 9 commits successifs `chore(log): auto session entry` (Stop hook bug) | — | git history pollution |
| Descriptions skills verbeuses (top 8 ~ 4432 chars) | ~1100 tokens/turn | ✅ system-reminder |
| `.remember/` plugin doublon avec auto-memory `MEMORY.md` | — | SessionStart hook silencieux mais context overhead |

## 3. Approche retenue — séparation par workload, pas patches cosmétiques

**Principe** : pas de hook qui patche `effortLevel` mid-flight, pas
d'archivage `_archive/`, pas d'intercept harness. Utiliser le **mécanisme natif
Claude Code** (un `.claude/` lié au cwd) pour scoper la surface au workload réel.

**Architecture** :

| cwd | Surface chargée | Usage |
|-----|-----------------|-------|
| `/opt/automecanik/app/` | 8 skills DEV (`code-review`, `db-migration`, `frontend-design`, `governance-vault-ops`, `responsive-audit`, `session-log`, `ui-ux-pro-max`, `vehicle-ops`) — **0 agent R\***, **0 skill SEO** | dev backend/frontend, refactor, CI, ADR, governance |
| `/opt/automecanik/app/workspaces/seo-batch/` | 39 agents R0-R8 + 16 skills SEO + rules SEO + settings.json (mêmes hooks paths absolus) | campagnes SEO, KW planning, content gen R*, RAG enrich, audits gammes |

L'auto-memory Claude Code utilise un store distinct par workspace
(`~/.claude/projects/-opt-automecanik-app-workspaces-seo-batch/memory/`),
donc le contexte SEO ne pollue pas la memory dev daily.

## 4. PRs livrées (3, toutes mergées sur main)

### 4.1 PR ak125/nestjs-remix-monorepo#200 — workspace split

`chore(claude): split SEO batch agents/skills into dedicated workspace`
(commit `0127f88c`).

- 39 agents `git mv .claude/agents/*` → `workspaces/seo-batch/.claude/agents/`
- 16 skills SEO `git mv .claude/skills/*` → `workspaces/seo-batch/.claude/skills/`
- Création `workspaces/seo-batch/{CLAUDE.md, README.md, .claude/rules/, .claude/settings.json}`
- Hooks paths absolus → fonctionnent depuis les deux workspaces sans modif
- Update `app/CLAUDE.md` : nouvelle section "Workspaces Claude Code"

### 4.2 PR ak125/nestjs-remix-monorepo#201 — fix Stop hook

`chore(hooks): prevent consecutive auto-log session entries` (commit `7bb88dc4`).

Defence in depth ajoutée à `scripts/claude-hooks/stop-log-session-suggest.sh` :
si le dernier commit est déjà un auto-log entry, bail immédiatement. Garantit
qu'aucune chaîne de N auto-log consécutifs n'est jamais produite, peu importe
la course de marker SHA file.

Cause racine probable : double invocation du Stop hook (deuxième terminal
Claude Code, retry harness, race file marker). 9 paires consécutives observées
sur `feat/aicos-fleet-advisor-claude-4-7` avant fix.

### 4.3 PR ak125/nestjs-remix-monorepo#202 — trim verbose descriptions

`chore(skills): trim 8 verbose SEO skill descriptions to triggers` (commit `d0fc0c64`).

Trim de 8 descriptions `SKILL.md` frontmatter de paragraphes pédagogiques à
des **triggers** conformes convention Anthropic (WHAT + key trigger phrases) :

| Skill | Avant | Après |
|---|---:|---:|
| r8-diversity-check | 916 | 228 |
| seo-vault-verify | 636 | 213 |
| legacy-recycler | 542 | 212 |
| content-quality-gate | 529 | 215 |
| pollution-scanner | 520 | 218 |
| surgical-cleaner | 493 | 210 |
| v5-guardian | 491 | 239 |
| seo-gamme-audit | 305 | 209 |
| **Total** | **4432** | **1744** |

~700 tokens économisés par tour en sessions seo-batch. Le contenu pédagogique
reste intact dans le corps de chaque `SKILL.md` (chargé seulement quand le
skill est invoqué via `Skill` tool — lazy-load).

## 5. Cleanups user-level (hors PR — `~/.claude/settings.json`)

- Plugin `remember@claude-plugins-official` : `true → false` (doublon avec auto-memory `MEMORY.md`)
- Plugin `goodmem@claude-plugins-official` : `true → false` (jamais invoqué)
- Symlink `~/.claude/skills/pipeline-orchestrator` retiré (doublon avec
  version projet `workspaces/seo-batch/.claude/skills/pipeline-orchestrator/`).
  Cible canon paperclip `/opt/automecanik/paperclip/skills/pipeline-orchestrator/SKILL.md`
  préservée.

Reversible : flip à `true` dans `~/.claude/settings.json` et restart Claude Code.

## 6. Lessons learned

### 6.1 `rm -rf <symlink>/` avec trailing slash suit le lien

Incident pendant le dedupe symlink : `rm -rf /home/deploy/.claude/skills/pipeline-orchestrator/`
(avec trailing slash) a vidé la **cible** du symlink (`/opt/automecanik/paperclip/skills/pipeline-orchestrator/`),
pas le symlink lui-même.

Restauré immédiatement via `cp` depuis la copie identique versionnée monorepo
(checksum md5 match). Sans cette redondance, perte du skill canon paperclip.

**Recipe** : pour supprimer un symlink, **toujours** `rm <path>` (sans trailing
slash, sans `-r`, sans `-f`). En cas de doute, `readlink -f <path>` d'abord.

### 6.2 Le Fleet Advisor n'agit pas sur le main loop du harness

Le Fleet Advisor (`fleet-advisor-status-20260425`) optimise le **routing
fleet/sub-agents** (quel agent prend quel job), pas le main loop du harness
Claude Code. `effortLevel: "xhigh"` reste appliqué statiquement à chaque tour
de la session main, peu importe la complexité du prompt.

→ La discipline propre = utiliser les **classes de session prévues par
Anthropic** : main xhigh pour le travail dur (debug cross-module, refactor,
audit DB), `/fast` (Opus 4.6) ou nouvelle session sans xhigh pour les Q&A
descriptives, sub-agents Haiku pour les lookups mécaniques. Pas de hook
auto-downgrade `effortLevel`.

### 6.3 Skill descriptions = triggers, pas docs

Convention Anthropic : la `description` frontmatter sert de **trigger** pour
la décision d'invocation, pas de documentation utilisateur. Descriptions
verbeuses = double pénalité :

1. Coût direct (tokens chargés à chaque tour)
2. Augmente le risque de fausse-trigger sur sujets périphériques (règle "1%
   chance — invoke" du superpowers).

Cible : <250 chars max. Doc usage → corps `SKILL.md` (lazy-loaded).

### 6.4 Workspace split > archivage

L'archivage `_archive/` ou `enabledAgents` flipping reste du patching qui
demande maintenance. La séparation par cwd via Anthropic-native `.claude/`
liée au workspace est structurelle : aucun config à maintenir, le bon outil
au bon endroit, l'utilisateur choisit en `cd`-ant.

## 7. Smoke test à valider (utilisateur, ne peut pas être fait depuis Claude Code)

Spawn deux nouvelles sessions distinctes :

```bash
# Session dev daily (attendu : 0 agent R*, 8 skills DEV uniquement)
cd /opt/automecanik/app && claude

# Session SEO batch (attendu : 39 agents + 16 skills SEO + descriptions trimmed)
cd /opt/automecanik/app/workspaces/seo-batch && claude
```

## 8. Restant non-faisable depuis cette session (à toi)

| Item | Pourquoi | Action utilisateur |
|---|---|---|
| MCP Supabase doublon | `~/.claude.json` contient 0 mcpServers, config vient d'ailleurs (claude.ai web app integrations ou Claude Desktop config). Pas de CLI `claude` disponible sur DEV VPS. | Inspecter `claude mcp list` ou panel claude.ai web. Garder un seul des deux préfixes (`mcp__supabase__*` recommandé, plus court). |
| Mesure empirique gain | Nouveau session requis pour observer la baisse | Comparer `/cost` ou dashboard Anthropic sur 2-3 sessions normales dans les 24-48h |

## 9. Effet attendu sur la facturation

Sur une session **dev daily** typique :

- ~10 K tokens system-prompt en moins par tour (39 agents + 16 skills SEO + descriptions verbeuses)
- Cache prompt plus stable (moins de fichiers `.claude/` modifiés en dev quotidien — l'auto-log Stop hook ne déclenche plus de commits cosmétiques répétés)
- Sub-agents Haiku délégables pour lookups (canonical Anthropic pattern)

Sur une session **seo-batch** :

- ~700 tokens en moins par tour (descriptions trimmed)
- Surface complète SEO disponible quand nécessaire

## 10. References

- PR #200, #201, #202 (monorepo)
- Memory `dual-workspace-claude-context.md`, `feedback_xhigh_advisor_layers.md`,
  `feedback_no_bricolage_clean_layer.md`, `feedback_rm_symlink_trailing_slash_trap.md`,
  `plugins-disabled-20260427.md` (auto-memory)
- Plan diagnostic `~/.claude/plans/je-veux-savoir-pourquoi-zippy-crayon.md`
- Convention Anthropic Skills (description = trigger)
- ADR-015 vault SoT (gouvernance externalisée)
