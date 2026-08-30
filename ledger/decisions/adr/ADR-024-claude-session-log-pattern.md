---
id: ADR-024
title: "Claude Session Timeline Logging via log.md + Auto-Commit Hook"
status: accepted
date: 2026-04-25
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G3]
related_incidents: []
reviewed_by: "Claude Code Opus 4.7"
---

# ADR-024: Claude Session Timeline Logging via log.md + Auto-Commit Hook

## Contexte

Plusieurs mécanismes de mémoire pré-existent dans l'écosystème AutoMecanik, mais aucun ne couvre simultanément ces trois besoins :

| Mécanisme | Couvre | Limite |
|---|---|---|
| `~/.claude/projects/.../memory/MEMORY.md` | Apprentissages persistants (règles, gotchas, feedback utilisateur) | USER-only, hors git, non partagé avec l'équipe |
| `.remember/logs/memory-*.log` (monorepo) | Transcripts session bruts | Gitignored (`*`), non curated, ~700-800 KB/jour |
| `.remember/remember.md` (skill officiel `remember:remember`) | Handoff overwrite "State / Next / Context" | Single state, non append-only, jamais invoqué chez nous |
| PR descriptions GitHub | Détails techniques par PR | Granularité PR, pas par session, pas centralisé |
| `git log` | Timeline canonique des changements | Trop granulaire, pas de narrative session |
| `governance-vault/` | Décisions canon (ADRs, incidents, retros) | Réservé aux décisions architecturales pérennes |

**Le gap** : trois besoins simultanés non couverts :

1. **Timeline append-only** des sessions Claude Code "importantes" (commits / PRs créés)
2. **Tracked git** (donc visible à l'équipe + `git log` historique + signed commits G3)
3. **Lu automatiquement par Claude au démarrage** (vs uniquement sur demande explicite)

Sans cela, chaque nouvelle session redécouvre l'historique récent en relisant des transcripts ou en greppant le code, ce qui consomme tokens et masque le contexte narratif. Les sessions longues finissent par se "perdre" sans handoff structuré.

## Décision

**Adopter `log.md` à la racine du monorepo `nestjs-remix-monorepo` comme timeline append-only des sessions Claude Code, alimenté automatiquement par un Stop hook et lu en début de chaque nouvelle session.**

L'implémentation comprend trois composants :

### Composant 1 — `log.md` (racine monorepo, tracked git)

Fichier markdown append-only avec entrées datées au format strict :

```markdown
## YYYY-MM-DD — sujet bref (≤ 60 chars)

- **Branche** : `feat/<sujet>`
- **Décision** : 1 ligne FR, l'essentiel
- **Sortie** : PRs #XXX | commits abc1234 | fichiers `path/X`
```

Une entrée = 3-4 lignes. Heading H2 par session = greppable + naviguable. Append-only : jamais éditer une entrée passée ; correction = nouvelle entrée datée.

### Composant 2 — Stop hook auto-commit

`scripts/claude-hooks/stop-log-session-suggest.sh` wired dans `.claude/settings.json` sous le hook `Stop`. À chaque fin de réponse Claude :

1. Détecte si la branche courante a des commits ahead de `origin/main`
2. Si oui : génère une entrée déterministe 3 lignes (depuis `git log` + `gh pr list`)
3. Append à `log.md` + `git add log.md && git commit -m "chore(log): auto session entry for <branch>"`
4. Met à jour un marker file `.claude/.session-log-state/last-suggested-head` pour idempotence

**Aucune intervention de Claude.** Aucun token LLM consommé. 100 % deterministic.

Garde-fous :
- Skip sur `main` / `master` / detached HEAD / 0 commits ahead
- Skip pendant rebase / merge / cherry-pick / bisect (évite collision)
- Skip si `log.md` déjà modifié dans le working tree (évite stomping)
- Honore les pre-commit hooks (pas de `--no-verify`)
- Sur commit failure : rollback `log.md` + write marker (pas de loop)
- Stage **uniquement** `log.md`, jamais d'autres fichiers

### Composant 3 — Skill `/log-session` (manual fallback)

`.claude/skills/session-log/SKILL.md` : skill invocable manuellement par l'utilisateur quand il veut une entrée curée plus riche que le template auto. Le skill impose le même format strict.

Suffixe visuel `(auto)` dans le titre des entrées générées par le hook → traçabilité (entrée déterministe vs curated).

## Délimitation explicite avec les autres mécanismes

`CLAUDE.md` documente la séparation des rôles :

| Quoi | Va dans |
|---|---|
| Timeline session : date, branche, sortie | **`log.md`** (NEW) |
| Règles persistantes, gotchas, feedback utilisateur | `MEMORY.md` (inchangé, USER-only) |
| Détails techniques d'un changement | PR description GitHub |
| Décision architecturale canon | `governance-vault/` |
| Transcripts session bruts | `.remember/logs/` (gitignored) |

Pas de duplication. Chaque artefact a un rôle clair.

## Validation empirique

Pattern validé par 5 tests bout-en-bout exécutés en worktree isolé contre `main` post-merge `39f6ab78` :

| # | Scénario | Résultat |
|---|---|---|
| 1 | 0 commits ahead → silent (exit 0, pas de log change) | PASS |
| 2 | 1 commit ahead → log.md +6 lignes + auto-commit `chore(log)` | PASS |
| 3 | Re-run sur même SHA → idempotent (0 nouveau commit) | PASS |
| 4 | log.md déjà modifié dans WT → bail (pas de stomping) | PASS |
| 5 | Sur `main` → bail (branche protégée) | PASS |

## Conséquences

### Positives

- **Contexte récent disponible** au début de chaque session sans grep / re-lecture transcripts
- **Visible à l'équipe** (tracked git, signed commits par G3)
- **Zero token LLM** sur le chemin nominal (auto-commit)
- **Skill `/log-session` reste disponible** pour entrées curées riches quand utile
- **Signed commits** (les commits `chore(log)` sont signés par l'auteur git, héritent de G3)
- **Format strict imposé** par le skill évite la dérive en quelques semaines

### Négatives / risques

- **Pollution potentielle de l'historique git** : 1 commit `chore(log)` par session avec activité sur une branche feature. Mitigation : ces commits sont squash-mergés avec la PR feature, n'apparaissent pas dans `main`.
- **Marker file local** (`.claude/.session-log-state/`) gitignored, donc pas synchro entre worktrees. Acceptable car le hook re-vérifie SHA à chaque exécution.
- **Format auto déterministe** moins riche qu'une entrée humaine. Mitigation : skill `/log-session` reste invocable manuellement pour les sessions importantes.
- **Pre-commit hook chain** ralentie d'1 commit additionnel sur les branches actives. Impact négligeable (< 2s).

### Risques rejetés

- **Rotation auto** non implémentée (log.md va grossir). Décision : différé. À 200 entrées (~ 6 mois d'activité quotidienne), évaluer une archive.
- **Read at session start auto** : implémenté côté `CLAUDE.md` (instruction "lire `log.md` au début de session"), pas via hook SessionStart séparé. Plus simple, suffisant.

## Alternatives écartées

| Option | Raison du rejet |
|---|---|
| `Claude-Mem` (vector DB sémantique) | Sur-dimensionné pour le besoin. Dependency externe, license à gérer, vector DB à opérer. Fonctionnellement plus large mais nous ne consommons pas la sémantique. |
| `Graphify` (knowledge graph LLM) | Pre-1.0 avec bugs data-loss connus. Extraction docs via API LLM (tension avec [[ADR-015-vault-single-source-of-truth|ADR-015]] et l'airlock). |
| `Serena` MCP (LSP-based) | Excellent pour navigation code mais hors scope timeline. Pas une alternative directe. |
| Étendre `MEMORY.md` au lieu de créer `log.md` | MEMORY.md est USER-only, non shared via git. Le besoin "team-shared timeline" ne peut pas être satisfait par MEMORY.md. |
| Skill officiel `remember:remember` overwrite | Single state, écrase l'historique. Append-only requis. |
| Hook SessionStart pour lire log.md | Redondant avec `CLAUDE.md` qui instruit déjà la lecture. Hook ajouterait complexité sans bénéfice net. |

## Implémentation

| Composant | Fichier | PR de livraison |
|---|---|---|
| `log.md` initial + skill + hook (suggest version initiale) | `log.md`, `.claude/skills/session-log/SKILL.md`, `scripts/claude-hooks/stop-log-session-suggest.sh`, `.claude/settings.json`, `CLAUDE.md`, `.claude/knowledge/README.md`, `.gitignore` | monorepo PR #163 (commit `e45dcd04`) |
| Hook auto-commit (refonte) | `scripts/claude-hooks/stop-log-session-suggest.sh` (rewrite 60%) | monorepo PR #165 (commit `39f6ab78`) |

Branches `chore/log-md-session-timeline-*` et `chore/log-session-hook-auto-commit-*` supprimées après merge.

## Statut et révision

- **Status** : accepted (validé empiriquement 2026-04-25)
- **Réversibilité** : élevée. Suppression du hook + du skill + du fichier `log.md` = retour état antérieur. Pas de migration de données nécessaire.
- **Première révision** : à 6 mois d'usage (vers 2026-10-25), évaluer rotation/archive si log.md > 200 entrées.

## Références

- Monorepo PR [#163](https://github.com/ak125/nestjs-remix-monorepo/pull/163), [#165](https://github.com/ak125/nestjs-remix-monorepo/pull/165)
- `log.md` à la racine du monorepo
- `.claude/skills/session-log/SKILL.md`
- `scripts/claude-hooks/stop-log-session-suggest.sh`
- [[ADR-015-vault-single-source-of-truth]] — vault SoT (le `log.md` ne le duplique pas, il complète au niveau session)
- [[ADR-023-hook-layer-defense]] — pattern hook + script + CI déjà établi pour `.local/governance-vault/` ; cet ADR réutilise le pattern hook côté Stop
- [[rules-vault|G3]] — Signed Commits (les commits `chore(log)` héritent)
