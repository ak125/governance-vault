---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: Claude Code — politique d'activation plugins + autorisation propose-only
slug: claude-code-plugin-enablement-policy
schema_version: "1.0.0"
lang: fr
updated_at: "2026-11-15"
updated_by: "@fafa"
related_adr: []
related_prs: []
related_knowledge:
  - "claude-code-dual-workspace-cost-optimization-20260427"
status: current
tags:
  - claude-code
  - cost-optimization
  - plugins
  - harness
  - policy
---

# Claude Code — politique d'activation plugins + autorisation propose-only

> Session 2026-05-04. Rationalisation du jeu de plugins user-level
> (`~/.claude/settings.json` clé `enabledPlugins`) pour la session
> `/opt/automecanik/app/` et formalisation de la règle « Claude peut proposer
> de réactiver un plugin désactivé, jamais l'activer en silence ».
> Suite directe de `claude-code-dual-workspace-cost-optimization-20260427`.

## 1. Contexte / problème

Au 2026-05-04, le user-level `~/.claude/settings.json` listait **28 plugins**
officiels (`claude-plugins-official`) dont **24 actifs** (4 déjà désactivés :
`frontend-design`, `security-guidance`, `remember`, `goodmem`). À chaque
session Claude Code dans `/opt/automecanik/app/`, la liste de skills associée
(descriptions courtes) gonfle le system-reminder initial — typiquement 100+
entrées dans le bloc `Available skills`.

Conséquence : tokens consommés à chaque tour pour des plugins non-pertinents
au workload monorepo (dev backend NestJS / frontend Remix / governance vault),
notamment les outils marketing/ads, les alternatives à CodeRabbit, et les
plateformes non utilisées (Cloudflare Workers, Netlify) — alors que la stack
déploiement est Docker + Caddy self-hosted (cf. `.claude/rules/deployment.md`).

Question utilisateur explicite : *« plusieurs plugins installés — peut-il être
activé et désactivé automatiquement quand le LLM juge nécessaire pour pas
consommer des tokens inutilement ? »*

## 2. Vérité architecturale (Claude Code harness)

**Les plugins ne s'auto-activent pas.** C'est une limite intentionnelle du
harness Claude Code :

| Mécanisme | Acteur | Note |
|-----------|--------|------|
| `/plugin enable <name>` | Utilisateur (REPL) | Action manuelle |
| `enabledPlugins` (settings.json) | Utilisateur (déclaratif) | Persistant |
| Auto-toggle par le LLM | **Impossible** | Architecturalement bloqué |

Progressive disclosure réel observable :

- **Descriptions skill** (1 ligne par skill) : toujours chargées si plugin actif
  → ~50-100 tokens chacune, listées dans le system-reminder `Available skills`.
- **Contenu complet skill** : chargé uniquement à l'invocation explicite
  (`Skill` tool) ou auto-invoke si la `description` matche la requête.
- **Outils MCP** : déjà en deferred mode — schémas chargés via `ToolSearch`
  uniquement si le LLM décide de les appeler. Coût initial : ~ nom seul.

Donc le coût marginal d'un plugin activé mais inutilisé ≈ **liste des
descriptions de ses skills** dans le system-reminder.

## 3. Décision opérationnelle (session app/)

### 3.1 Décision du 4 mai 2026 (historique)

Cette sous-section décrit l'état visé le 4 mai 2026. Elle ne décrit plus la
configuration réelle : voir 3.2.

8 plugins désactivés dans `~/.claude/settings.json` user-level :

| Plugin | Raison |
|--------|--------|
| `searchfit-seo` | Déjà couvert par `workspaces/seo-batch/` (16 skills SEO dédiés) |
| `cloudflare` | Stack déploiement = Docker + Caddy, pas de Workers (cf. `.claude/rules/deployment.md`) |
| `netlify-skills` | Idem, pas de Netlify |
| `pagerduty` | Pas d'incidents PagerDuty actifs sur le workload |
| `adspirer-ads-agent` | Pas de campagnes ads (scope marketing géré par `workspaces/marketing/`) |
| `optibot` | Redondant avec `coderabbit` (déjà actif) |
| `qodo-skills` | Idem, redondant code-review |
| `firecrawl` | Rarement utile en dev backend/frontend daily ; à réactiver si recherche web ponctuelle |

Plugins conservés (16) : `code-review`, `coderabbit`, `superpowers`, `github`,
`supabase`, `hookify`, `playwright`, `context7`, `feature-dev`,
`typescript-lsp`, `commit-commands`, `pr-review-toolkit`, `agent-sdk-dev`,
`claude-md-management`, `code-simplifier`, `skill-creator`.

### 3.2 Liste réelle relevée le 15 nov. 2026 (machine DEV, utilisateur `deploy`)

Relevé en lecture seule de la clé `enabledPlugins` de `~/.claude/settings.json`
le 2026-11-15 à 18:34:54 UTC (fichier modifié pour la dernière fois le
2026-11-15 à 14:13:55 UTC) :

```bash
jq -r '.enabledPlugins | to_entries[] | "\(.key)\t\(.value)"' ~/.claude/settings.json
```

27 plugins déclarés, tous suffixés `@claude-plugins-official` : 5 à `true`,
22 à `false`.

Actifs (5) : `code-review`, `skill-creator`, `security-guidance`,
`claude-md-management`, `context7`.

Désactivés (22) : `frontend-design`, `code-simplifier`, `github`, `remember`,
`goodmem`, `playwright`, `feature-dev`, `typescript-lsp`, `commit-commands`,
`pr-review-toolkit`, `supabase`, `agent-sdk-dev`, `hookify`, `firecrawl`,
`coderabbit`, `qodo-skills`, `searchfit-seo`, `cloudflare`, `pagerduty`,
`optibot`, `adspirer-ads-agent`, `netlify-skills`.

Écarts avec 3.1 constatés au relevé : 28 plugins déclarés au 4 mai, 27 au
15 nov. (`superpowers` n'est plus déclaré) ; `security-guidance` est actif ;
des 16 plugins conservés le 4 mai, 4 restent actifs et 11 sont désactivés. La sauvegarde
`~/.claude/settings.json.before-token-budget-20260920` en déclare 28, dont 7
actifs (les 5 actuels, plus `superpowers` et `remember`). La date et l'auteur
du passage de 16 à 7 actifs sont inconnus.

### 3.3 Plugins de mémoire désactivés : `remember` et `goodmem`

- `remember` (version installée 0.43.1, portée utilisateur) : désactivé une
  première fois le 27 avril 2026, comme doublon de l'auto-memory `MEMORY.md`
  (`claude-code-dual-workspace-cost-optimization-20260427`, section 5) ;
  trouvé réactivé, puis désactivé de nouveau le 15 nov. 2026. La version
  0.43.1 déclare quatre hooks (`SessionStart`, `UserPromptSubmit`,
  `PostToolUse`, `SessionEnd`). Au démarrage de chaque
  session, le hook `SessionStart` injecte des résumés produits par Haiku à
  partir d'autres sessions (`.remember/now.md`, `.remember/today-*.md`). Une
  session de mandat reçoit donc un contexte que personne n'a relu et qui
  concurrence le mandat et le Vault. Détail en section 8.
- `goodmem` (version installée 0.1.0, portée utilisateur) : désactivé le
  27 avril 2026 parce qu'il n'était jamais invoqué
  (`claude-code-dual-workspace-cost-optimization-20260427`, section 5) ; à
  `false` au 4 mai, au 20 sept. et au 15 nov. 2026. S'il était actif, il
  ajouterait un serveur MCP (`node`) et des skills de gestion d'une mémoire
  externe (embedders, spaces, memories), soit une autre source de contexte
  hors Vault. Il n'a pas été modifié le 15 nov. 2026 : entre la sauvegarde
  `settings.json.bak-20261115` et le fichier actuel, seule la valeur de
  `remember` change.

## 4. Règle de comportement (memory feedback)

Mémoire utilisateur enregistrée :
`feedback_plugin_activation_request_allowed.md`

> Si une tâche bénéficierait d'un plugin actuellement désactivé, Claude
> **propose** explicitement la réactivation à l'utilisateur. Il ne modifie
> jamais `~/.claude/settings.json` en silence et n'assume pas que la
> désactivation est définitive.

Pratique :

1. Détection contextuelle : la requête utilisateur déclenche un domaine
   couvert par un plugin off (ex : « audit SEO sur cette page »
   → `searchfit-seo` désactivé).
2. Annonce explicite : « Plugin X est désactivé dans tes settings — veux-tu
   le réactiver pour cette tâche ? »
3. Si refus : continuer sans relance, sans plugin.
4. Si accord : éditer `~/.claude/settings.json` clé `enabledPlugins`, puis
   prévenir qu'un redémarrage de session est nécessaire (les plugins se
   chargent au démarrage).

## 5. Alternative : override par projet

Pour qu'un plugin soit actif uniquement dans un sous-projet (ex : `firecrawl`
dans `workspaces/seo-batch/` pour scraping ad-hoc), placer un
`enabledPlugins` dans `.claude/settings.json` du projet — les settings projet
override les settings user.

Exemple `workspaces/seo-batch/.claude/settings.json` (illustratif) :

```jsonc
{
  "enabledPlugins": {
    "searchfit-seo@claude-plugins-official": true,
    "firecrawl@claude-plugins-official": true
  }
}
```

## 6. Anti-patterns détectés

- ❌ Auto-toggle silencieux par Claude (architecturalement impossible — bonne
  contrainte, ne pas chercher à contourner via hooks).
- ❌ Désactiver un plugin globalement parce qu'inutile *à un instant donné*
  → préférer override projet si usage occasionnel récurrent.
- ❌ Considérer la liste d'activation comme figée → la revisiter à chaque
  changement majeur de scope (nouveau workspace, nouvelle stack déploiement).
- ❌ Laisser actif, dans les sessions de mandat, un plugin qui injecte du
  contexte au démarrage (hook `SessionStart`, par exemple `remember`) : la
  session reçoit un texte non relu qui concurrence le mandat et le Vault.
  Vérifier les hooks déclarés par un plugin (`hooks/hooks.json`) avant de
  l'activer au niveau utilisateur.

## 7. Métrique attendue

Estimation conservative (sur la base des descriptions de skills observées
dans le system-reminder courant) :

- 8 plugins × ~3-6 skills/plugin × ~80 tokens/description
  ≈ **1900–3800 tokens économisés** par tour sur le system-reminder initial.

À mesurer empiriquement en next session via comparaison du nombre d'entrées
listées dans `Available skills` avant/après redémarrage.

## 8. Écart du 15 nov. 2026 : réactivation silencieuse de `remember`

Faits :

- 27 avril 2026 : `remember` passe de `true` à `false`, doublon de
  l'auto-memory `MEMORY.md` (note du 27 avril, section 5).
- 4 mai 2026 : `remember` est à `false` (section 1 de cette note).
- `~/.claude/settings.json.before-token-budget-20260920` (dernière écriture
  le 2026-09-20 à 12:27:50 UTC) : `remember` est à `true`. Le plugin était
  donc réactivé au plus tard à cette date.
- Date et auteur de la réactivation : inconnus. Une recherche de `remember`
  dans `ledger/`, `ops/` et `99-meta/` ne trouve que la note du 27 avril et
  celle-ci.
- 15 nov. 2026 à 14:13:55 UTC : `remember` repasse à `false` dans
  `~/.claude/settings.json` ; l'état précédent est conservé dans
  `~/.claude/settings.json.bak-20261115` (seule différence entre les deux
  fichiers sur `enabledPlugins`).
- Version 0.43.1, installée le 2026-10-16 à 14:40 UTC selon
  `~/.claude/plugins/installed_plugins.json` : tant que le plugin était
  actif, son hook `SessionStart` (niveau utilisateur, donc toutes les sessions
  de l'utilisateur `deploy`) injectait au démarrage les résumés Haiku de
  `.remember/now.md` et `.remember/today-*.md`. Comportement des versions
  antérieures : non vérifié. Nombre de sessions de mandat concernées :
  inconnu.
- Les dossiers `.remember/` n'ont pas été supprimés.

Constat : la liste d'activation a changé entre le 4 mai et le 20 sept. 2026
sans trace dans ce Vault, et cette note n'a pas été mise à jour. Le relevé
daté de `enabledPlugins` (section 3.2) sert de référence pour le prochain
contrôle.

## 9. Références

- Précédent : `ledger/knowledge/claude-code-dual-workspace-cost-optimization-20260427.md`
- Memory feedback : `feedback_plugin_activation_request_allowed.md`
  (path : `~/.claude/projects/-opt-automecanik-app/memory/`)
- ADR-012 — 3-VPS architecture (DEV / PROD / AI-COS)
- `.claude/rules/deployment.md` (monorepo) — Docker + Caddy, no Cloudflare/Netlify
