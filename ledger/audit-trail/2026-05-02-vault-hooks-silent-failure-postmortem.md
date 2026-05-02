---
title: "Session 2026-05-02 — Vault hooks silent failure post-mortem + G3 client-side guard"
date: 2026-05-02
type: session-trail
related_adr: ["ADR-015", "ADR-035"]
related_prs:
  - "ak125/governance-vault#134"
  - "ak125/governance-vault#135"
status: closed
session_closed_at: 2026-05-02
tags: [vault, githooks, g2, g3, broken-links, signatures, defense-in-depth]
---

# Session 2026-05-02 — Vault hooks silent failure post-mortem

## Résumé

PR #134 (incident `INC-2026-013` + `ADR-035` probabilités non sourcées moteur diagnostic) a déclenché 2 fails CI : **Broken Wikilinks** et **G3 Commits signes**. Investigation : les hooks client-side du vault étaient en réalité **silencieux depuis 2026-04-18**. Trois bugs structurels imbriqués découverts ; correctifs livrés en PR #135 sans bricolage (extraction d'un script canonique, alignement sur le pattern existant `check-orphans.sh` / `check-broken-links.sh`).

## Cause racine — trois bugs imbriqués

| # | Bug | Conséquence |
|---|-----|-------------|
| 1 | `.githooks/pre-commit` mode `664` (depuis 2026-04-18) | Git ignore silencieusement les hooks non-exec — le hook n'a **jamais tourné** |
| 2 | `_scripts/check-orphans.sh` + `check-broken-links.sh` mode `664` | `pre-push` les gardait avec `[ -x "$script" ]` → skip silencieux. `pre-commit` (sans guard) aurait failé bruyamment dès que (1) corrigé |
| 3 | G3 (signing) absent de `pre-push` ; CI avait sa propre logique inline | Pas de gate client-side ; logique G3 dupliquée entre CI et pas-de-hook |

**Net** : depuis l'install des hooks, **G2 + broken-links + G3 reposaient uniquement sur le CI** côté client. Le développeur croyait pousser après vérification locale ; en réalité aucun gate ne tournait avant l'arrivée sur GitHub.

## Découverte

Le PR #134 contenait :

- **Wikilink cassé** : `ADR-035` ligne 21 utilisait `[[INC-2026-013]]` au lieu du format canonique `[[<filename>|INC-AAAA-NNN]]` (cf. `ops/moc/MOC-Incidents.md` lignes 20-24). Le résolveur cherchait `INC-2026-013.md`, fichier inexistant.
- **Commit non signé** : `0aff222` `sigstatus=N`. Config locale `commit.gpgsign=true` présente, mais commit créé depuis un worktree/clone sans la config signing locale.

Les deux ont passé le commit + push sans alerte locale → fail CI.

## Fix structurel (PR #135)

1. `chmod +x .githooks/pre-commit` (mode 100644 → 100755)
2. `chmod +x _scripts/check-orphans.sh _scripts/check-broken-links.sh` (idem)
3. **Extraction de `_scripts/check-signatures.sh`** — script canonique mirror exact de la logique `%G?` du job CI G3 (G/U/X = OK ; N/B = FAIL). Range par défaut `merge-base(origin/main)..HEAD` (pre-push), ou range explicite passé en arg (CI).

**Source unique consommée par 2 endroits** :

- `.githooks/pre-push` : 13 lignes ajoutées, **symétriques aux 2 autres checks** (`check-orphans.sh`, `check-broken-links.sh`).
- `.github/workflows/vault-governance.yml` : passe de **30 lignes inline** à `bash _scripts/check-signatures.sh "$PWD" "$RANGE"`.

Cleanup d'une asymétrie : avant, G2 + broken-links étaient script-based, G3 était inline-only. Après, les 3 gates suivent le même pattern.

## Lessons learned

### Pattern canonique des gates vault

Tout gate `Gn` du vault doit suivre le tryptique :

1. **Un script** `_scripts/check-<gate>.sh` — source unique, exécutable, testable en isolation.
2. **Hook client-side** `.githooks/pre-commit` ou `.githooks/pre-push` — invoque le script, fail-fast localement.
3. **CI workflow** `.github/workflows/vault-governance.yml` — invoque le **même** script, gate de dernier recours.

Pas de logique inline dans le hook ou le workflow — duplication = drift garanti.

### Mode permissions

Les fichiers exécutables (`*.sh` dans `_scripts/`, hooks dans `.githooks/`) doivent être committés en `100755`. Git tracke le mode ; un mode `100644` casse silencieusement les chaînes d'exécution (hook ignoré, script skippé via `[ -x ]`).

### Anti-pattern documenté

Le silent-skip pattern `[ -x "$script" ] || continue` peut **masquer des régressions** — préférer un fail-loud quand un gate est censé être armé :

```bash
if [ ! -x "$SCRIPT" ]; then
  echo "FAIL: $SCRIPT non exécutable — gate désarmée"
  exit 1
fi
```

(Non implémenté dans le scope PR #135 — à considérer pour une itération ultérieure si récidive.)

## Découverte parallèle

Pendant l'audit, vérification de l'équivalent côté monorepo (`/opt/automecanik/app/.husky/`) :

- Husky v9+ utilise `core.hooksPath = .husky/_` et **source** les scripts utilisateur via `sh -e` (n'exec pas directement) → mode `664` sur `.husky/pre-commit` est **normal** dans le monorepo, pas un bug.
- Branche locale `chore/husky-pre-push-main-guard` détectée comme orpheline : son contenu `.husky/pre-push` était byte-identique au PR monorepo #266 déjà mergé. Worktree + branche supprimés.

## Références

- PR vault #134 — incident `INC-2026-013` + `ADR-035` (trigger de la session)
- PR vault #135 — fix githooks + G3 client-side guard + extraction `check-signatures.sh`
- PR monorepo #266 — `chore(husky): pre-push hook blocking direct pushes to main/dev` (déjà mergé, sans rapport direct)
- [[ADR-015-vault-single-source-of-truth]] — vault SoT
- [[2026-04-27-session-vault-governance-hardening]] — précédente session governance hardening
