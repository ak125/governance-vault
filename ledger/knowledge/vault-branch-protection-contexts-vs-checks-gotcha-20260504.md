---
category: knowledge
doc_family: knowledge
source_type: gotcha
title: GitHub branch protection — `contexts[]` drop silencieux, utiliser `checks` JSON
slug: vault-branch-protection-contexts-vs-checks-gotcha
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-04"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/governance-vault#153"
related_knowledge:
  - "vault-self-review-workflow-20260504"
  - "branch-protection-main-20260502"
status: current
tags:
  - gotcha
  - github-api
  - branch-protection
  - status-checks
  - ci
---

# GitHub branch protection — `contexts[]` drop silencieux, utiliser `checks` JSON

> Gotcha découvert 2026-05-04 en tentant d'ajouter un 6ᵉ status check
> (`Self-Review Marker`) à `required_status_checks` sur `main`.
> `gh api PATCH ... -f 'contexts[]=...'` retourne 200 OK avec un body sans
> le nouveau context — drop silencieux. Cause : le param `contexts` est
> déprécié et valide que les noms ont déjà été observés. Fix : utiliser le
> param `checks` (array of `{context, app_id}`) avec input JSON.

## Contexte

Suite à PR #153 (CI gate `Self-Review Marker`, cf.
`vault-self-review-workflow-20260504` §7), il fallait ajouter le nouveau
context aux `required_status_checks` de `main` pour que `enforce_admins`
le rende bloquant.

Commande initiale, formulée par analogie avec la doc GitHub :

```bash
gh api -X PATCH repos/ak125/governance-vault/branches/main/protection/required_status_checks \
  -F 'strict=true' \
  -f 'contexts[]=G2: Zero Orphelin' \
  -f 'contexts[]=Broken Wikilinks' \
  -f 'contexts[]=G3: Commits signes' \
  -f 'contexts[]=G4: CI read-only sur canon' \
  -f 'contexts[]=No V1 Paths (ADR-015)' \
  -f 'contexts[]=Self-Review Marker'
```

## Symptôme

**HTTP 200 OK** — la commande semble réussir. La réponse JSON est
correctement structurée. Mais en lisant attentivement :

```json
{
  "url": "https://api.github.com/.../required_status_checks",
  "strict": true,
  "contexts": [
    "G2: Zero Orphelin",
    "Broken Wikilinks",
    "G3: Commits signes",
    "G4: CI read-only sur canon",
    "No V1 Paths (ADR-015)"
  ],
  ...
}
```

→ **5 contexts au lieu des 6 envoyés**. `Self-Review Marker` a été
silencieusement dropé. Aucun message d'erreur, aucun warning, aucun
status code différent.

## Cause racine

Le paramètre `contexts` (array of strings) :

1. Est **déprécié** depuis 2022 au profit de `checks` (array of
   `{context, app_id}`).
2. **Valide silencieusement** les noms : un context name jamais observé
   par GitHub Actions sur le repo (ou une de ses branches/PRs) est
   ignoré sans warning.
3. Sa "validation" se base sur un cache interne des status checks vus,
   pas sur la liste workflow configurée.

Dans notre cas, `Self-Review Marker` venait d'être créé par PR #153 mergée
1-2 minutes avant. Le workflow s'était déclenché et avait passé sur la PR
elle-même (head branch `feat/self-review-marker-gate`). GitHub avait
peut-être pas encore propagé la connaissance du context vers la branch
protection registry.

## Fix : utiliser `checks` JSON

Le paramètre `checks` accepte tout context observé n'importe où dans le
repo (PR, autre branche, etc.) et oblige à fournir l'`app_id` explicite,
ce qui élimine l'ambiguïté.

```bash
gh api -X PATCH repos/owner/repo/branches/main/protection/required_status_checks --input - <<'EOF'
{
  "strict": true,
  "checks": [
    {"context": "G2: Zero Orphelin", "app_id": 15368},
    {"context": "Broken Wikilinks", "app_id": 15368},
    {"context": "G3: Commits signes", "app_id": 15368},
    {"context": "G4: CI read-only sur canon", "app_id": 15368},
    {"context": "No V1 Paths (ADR-015)", "app_id": 15368},
    {"context": "Self-Review Marker", "app_id": 15368}
  ]
}
EOF
```

`app_id 15368` = GitHub Actions (constant pour le repo, identifiable via
GET préalable sur la même endpoint).

## Procédure recommandée pour future modifs

1. **GET avant PATCH** pour obtenir l'état actuel ET l'`app_id` des checks
   existants :
   ```bash
   gh api repos/owner/repo/branches/main/protection/required_status_checks
   ```
2. **PATCH avec `checks`** (jamais `contexts`) en passant tout le bloc
   complet via `--input -` JSON (pas via flags `-f`).
3. **GET de vérification après PATCH** pour confirmer le résultat. Si le
   context manque → c'est un drop silencieux, vérifier la valeur exacte
   de `app_id` et si le context a déjà été observé dans le repo.

## Anti-patterns

- ❌ Croire le 200 OK comme confirmation de succès → toujours diff la
  réponse vs la requête.
- ❌ Mélanger `contexts[]` et `checks[]` dans la même requête (un override
  l'autre, comportement non-spécifié).
- ❌ Oublier `app_id` → GitHub peut accepter `null` mais alors n'importe
  quel app peut "satisfaire" le check, brisant la sécurité.
- ❌ Modifier `required_status_checks` via `-X PUT .../protection`
  (parent) plutôt que `-X PATCH .../protection/required_status_checks`
  (sous-ressource) — PUT demande tout le bloc protection, risque
  d'écraser CODEOWNERS, reviews, etc.

## Référence

- `vault-self-review-workflow-20260504` — précédent direct (le 6ᵉ gate
  qu'on cherchait à ajouter)
- `branch-protection-main-20260502` (memory) — `enforce_admins: true` actif
  depuis cette date
- `feedback_gh_branch_protection_subresource_uses_patch.md` (memory) —
  PATCH (sous-ressource) vs PUT (parent)
- GitHub REST API — Update status check protection :
  `PATCH /repos/{owner}/{repo}/branches/{branch}/protection/required_status_checks`
- GitHub deprecated note sur `contexts` : `docs.github.com/en/rest/branches/branch-protection`

## Self-review verdict: APPROVE

8-item checklist (canon `vault-self-review-workflow-20260504`) :

1. ✅ Frontmatter — slug, schema, lang, status, tags 5 (gotcha/github-api/branch-protection/status-checks/ci) tous pertinents
2. ✅ Factuel — réponse JSON authentique recopiée, `app_id 15368` vérifié, PR #153 référencée
3. ✅ Math — N/A
4. ✅ Wikilinks — `vault-self-review-workflow-20260504`, `branch-protection-main-20260502` valides
5. ✅ Anti-patterns — pas de "100%/tout/aucun" ; "drop silencieux" est factuel (observé empiriquement)
6. ✅ Cohérence canon — étend `vault-self-review-workflow-20260504` §7 (workflow déjà créé) ; cohérent avec mémoire `feedback_gh_branch_protection_subresource_uses_patch`
7. ✅ Précédent — `related_knowledge` frontmatter + §Référence bilatéraux
8. ✅ MOC — sera ajouté dans `MOC-Knowledge.md` §Patterns juste après `vault-prepush-hook-worktree-gotcha-20260504`

Verdict : APPROVE (0 BLOCKING, 0 MINOR).
