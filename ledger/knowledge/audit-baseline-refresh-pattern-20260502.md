---
type: knowledge
scope: devex/ci
date: 2026-05-02
owner: Fafa
pr_monorepo: https://github.com/ak125/nestjs-remix-monorepo/pull/267
related_pr_monorepo:
  - https://github.com/ak125/nestjs-remix-monorepo/pull/265
  - https://github.com/ak125/nestjs-remix-monorepo/pull/266
tags: [devex, ci, audit, baseline, knip, depcruise, no-bricolage, defense-in-depth]
---

# Audit Baseline Refresh — Pattern Script + Garde Défensive

> **Règle candidate pattern réutilisable**
> **Origine** : session 2026-05-02 monorepo `nestjs-remix-monorepo`. Correction d'un sur-bump baseline post-#236 + livraison du script `audit:baseline:refresh` qui était référencé partout sans exister.

---

## Problème

Un repo qui gate ses PRs sur un audit déterministe (`knip`, `madge`, `dependency-cruiser`, `ast-grep`) avec un baseline JSON commité doit pouvoir **rafraîchir** ce baseline après les PRs cleanup ou les changements intentionnels. Sans outil dédié, le rafraîchissement se fait à la main (édition JSON) → bricolage typique :

- Mesure transitoire silencieusement gravée (un `npm install` partiel, un cache stale, un état incohérent fait apparaître +29 unused_types qui sont ré-écrits dans le baseline)
- Pas de re-mesure atomique des autres métriques (on bumpe un champ, on oublie les autres qui auraient pu descendre)
- Aucune cohérence entre `captured_at` / `captured_on_commit` et le contenu

**Constat empirique** : un pattern référencé partout (`README.md`, notes JSON baseline, message d'erreur du comparateur, knowledge memo) sans implémentation correspondante = signal de bricolage existant dans le repo.

---

## Solution

**Réutiliser les parsers du comparateur existant** — ne jamais réécrire la logique d'audit dans un script séparé.

### Deux ajouts narrow au comparateur

```js
// scripts/cleanup/audit-compare-baseline.js

function refreshBaseline(baseline, current) {
  const today = new Date().toISOString().slice(0, 10);
  const commit = runSilent('git rev-parse --short HEAD').trim();
  return {
    ...baseline,                          // preserve thresholds, notes, version
    captured_at: today,
    captured_on_commit: commit,
    knip:      { ...baseline.knip,      ...current.knip },
    madge:     { ...baseline.madge,     ...current.madge },
    depcruise: { ...baseline.depcruise, ...current.depcruise },
    ast_grep:  { ...baseline.ast_grep,  ...current.ast_grep },
  };
}

if (refresh) {
  const refreshed = refreshBaseline(baseline, current);
  fs.writeFileSync(BASELINE_PATH, JSON.stringify(refreshed, null, 2) + '\n');
  process.exit(0);
}
```

### Garde défensive (obligatoire)

```js
function ensureDepsInstalled() {
  const required = ['knip', 'madge', 'dependency-cruiser', '@ast-grep/cli'];
  const missing = required.filter(
    (pkg) => !fs.existsSync(path.join(REPO_ROOT, 'node_modules', pkg)),
  );
  if (missing.length) {
    die(
      `node_modules out of sync (missing: ${missing.join(', ')}).\n` +
      `Run \`npm ci\` first; the audits depend on installed packages to\n` +
      `resolve imports correctly. Refusing to run with broken environment.`,
    );
  }
}
```

### Exposition npm

```json
"audit:baseline:refresh": "node scripts/cleanup/audit-compare-baseline.js --refresh"
```

---

## Trap empirique : worktree sans `node_modules`

**Première tentative de refresh** dans un worktree fraîchement créé via `git worktree add` (sans `npm ci` préalable) → résultats **silencieusement faux** :

| Métrique | Mesure correcte | Mesure dans worktree sans deps |
|---|---|---|
| `knip.unused_files` | 349 | **623** |
| `knip.unlisted_dependencies` | 10 | **363** |
| `knip.unlisted_binaries` | 5 | **10** |
| `depcruise.violations` | 145 | **0** |

Cause : sans `node_modules`, knip flagge tous les imports comme "unlisted" (les packages ne résolvent pas) et depcruise ne traverse rien (config rejette les imports non-résolus). Si le baseline avait été commité dans cet état, **le gate aurait été silencieusement neutralisé** (chaque mesure future aurait été comparée à un baseline absurdement permissif).

**Sans la garde défensive, la régression était indétectable** — exit code 0, JSON écrit, comparateur passe parce que le delta=0. La garde transforme ce mode silencieusement-cassé en erreur explicite avec instruction de remédiation (`npm ci`).

---

## Trap secondaire : divergence de comptage entre branches

Pendant la session, knip donnait `unused_types: 326` sur la branche typed-cast (PR #265) et `355` sur main. La différence (+29) ne venait pas d'un over-bump — elle venait du **rename d'import** `import { zodToJsonSchema as _zodToJsonSchema }` qui élimine ~29 entrées du comptage knip.

**Conséquence** : un baseline rafraîchi depuis une branche WIP capture un état incohérent avec main. **Toujours rafraîchir depuis `origin/main` HEAD** (worktree dédié), pas depuis la branche en développement.

---

## Invariants respectés

| Invariant | Comment |
|---|---|
| **Réutilisation** | Aucune duplication des parsers — `parseKnip` / `parseMadge` / `parseDepcruise` / `parseAstGrep` partagés entre compare et refresh |
| **Atomicité** | Une seule écriture, toutes les métriques cohérentes entre elles + `captured_at` / `captured_on_commit` |
| **Idempotence** | Deuxième `--refresh` consécutif ne change que `captured_at` (la date) |
| **Préservation** | Thresholds, notes, version, sous-champs non parsés (e.g. `madge.backend_cycles`) conservés |
| **Defense-in-depth** | Garde refuse d'exécuter avec `node_modules` désynchro |

---

## Anti-patterns à éviter

1. **Script séparé qui ré-implémente l'audit** — divergence garantie. Réutiliser les parsers du comparateur.
2. **Refresh sans garde sur les deps** — produit silencieusement un baseline corrompu si exécuté dans un environnement non-installé.
3. **Hand-edit du JSON pour bumper un seul champ** — capture une mesure transitoire sans cohérence avec les autres métriques. Si le tooling manque, le réflexe doit être "écrire le tooling", pas "éditer".
4. **Refresh depuis une branche WIP** — la branche peut introduire des décalages de comptage (cf. divergence import-rename observée). Toujours `git worktree add … origin/main` puis `npm ci` puis `npm run audit:baseline:refresh`.
5. **Référencer un script dans la doc avant de l'écrire** — c'est un orphan reference qui invite au bricolage. Soit on l'implémente, soit on retire la référence.

---

## Applicabilité

Tout repo avec un baseline d'audit déterministe commité (`audit-reports/*.json`, `governance-baseline.yaml`, `quality-gate-baseline/`, etc.) bénéficie de ce pattern :

| Repo | État | Bénéfice attendu |
|---|---|---|
| `nestjs-remix-monorepo` | ✅ Implémenté ([PR #267](https://github.com/ak125/nestjs-remix-monorepo/pull/267)) | Élimine les hand-edits du baseline JSON |
| `governance-vault` | À évaluer si un baseline équivalent existe | — |
| `automecanik-wiki` | Quality-gates Python existants — pattern transposable | Refresh atomique + garde sur `pyyaml` installé |

---

## Règle candidate canon

> **Tout baseline d'audit commité doit avoir une commande `*:refresh` qui (a) réutilise les parsers du comparateur existant, (b) re-mesure toutes les métriques en une passe atomique, (c) refuse de s'exécuter si l'environnement de mesure est désynchro (deps non installées, lockfile drift). Le hand-edit du JSON est un anti-pattern.**

---

## Application de patterns existants dans la même session

Les deux PRs jumelles de #267 instancient des patterns vault déjà canonisés :

- **[PR #266](https://github.com/ak125/nestjs-remix-monorepo/pull/266) — pre-push hook main/dev guard** : application directe de `pre-push-local-check-pattern.md`. Refuse push/create/delete sur `refs/heads/main|dev`. Tag pushes `refs/tags/v*` autorisés (workflow `deploy-prod.yml`). Bypass `--no-verify` documenté pour cas d'urgence (revert + roll-forward où attendre la review est elle-même le risque).
- **[PR #265](https://github.com/ak125/nestjs-remix-monorepo/pull/265) — typed cast remplace `@ts-nocheck`** : application de la règle "no bricolage" — un workaround OOM qui désactivait le type-check entier d'un fichier remplacé par un cast typé local sur la fonction importée (input `unknown`, output narrow `object`), sans `any`, sans `declare module` global, le reste du fichier reste type-checké.

---

## Références

- Script livré : [`scripts/cleanup/audit-compare-baseline.js`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/cleanup/audit-compare-baseline.js)
- Pattern parent : [`pre-push-local-check-pattern.md`](pre-push-local-check-pattern.md)
- Note connexe : `Q1-Q4 — solution structurelle vs bricolage` (`rules-engineering-quality.md`)
- Incident déclencheur : [PR #236](https://github.com/ak125/nestjs-remix-monorepo/pull/236) dependabot dev-deps bump → mesure transitoire `unused_types: 355` jamais réconciliée avec la réalité avant la livraison du refresh script.
