---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: TypeScript Aliases — tsc-alias gotcha (watch + initial pass + race wait-and-start)
slug: typescript-aliases-tsc-alias-gotcha
schema_version: "1.0.0"
lang: fr
updated_at: "2026-04-27"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/nestjs-remix-monorepo#190"
  - "ak125/nestjs-remix-monorepo#192"
status: current
---

# TypeScript Aliases — tsc-alias gotcha

> Lessons learned de la session 2026-04-27 entre @fafa et Claude Code (Opus 4.7 1M).
> Contexte : introduction des alias TypeScript (`@auth/`, `@cache/`, `@common/`, `@config/`,
> `@database/`, `@security/`, `@modules/`) sur backend NestJS. 586 imports relatifs réécrits.

## 1. Pourquoi `tsc-alias` plutôt que `tsconfig-paths/register` au runtime

| Critère | `tsc-alias` | `-r tsconfig-paths/register` |
|---|---|---|
| Quand ça tourne | Build time (réécrit `dist/`) | Runtime (résout à chaque `require`) |
| Overhead runtime | Zéro | Léger mais réel |
| Docker-friendly | ✅ `dist/` autonome | ⚠️ besoin de `tsconfig.json` en runtime |
| Production safety | `dist/` contient les vrais chemins relatifs | Dépend du `register` au boot |

→ **Recommandation 2026** : `tsc-alias` pour tout backend NestJS / Node compilé.

## 2. Trois pièges qui se cumulent en mode `watch`

### 2.1 `tsc-alias --watch` ne fait PAS de passe initiale

Documenté implicitement dans la doc tsc-alias : `--watch` ne réagit qu'aux changements
ultérieurs. Donc le tout premier `dist/main.js` émis par `tsc --watch` garde les literals
`require("@common/exceptions")` non résolus.

**Symptôme** :
```
Error: Cannot find module '@common/exceptions'
Require stack:
- /app/backend/dist/config/app.config.js
- /app/backend/dist/config/csp.config.js
- /app/backend/dist/main.js
```

**Fix** : faire une passe synchrone initiale, puis lancer le watch.

```jsonc
// package.json
{
  "build": "tsc --build && tsc-alias -p tsconfig.json",
  "dev:compile": "tsc --build && tsc-alias -p tsconfig.json && run-p dev:compile:tsc dev:compile:alias",
  "dev:compile:tsc": "tsc --build --watch --preserveWatchOutput",
  "dev:compile:alias": "tsc-alias -p tsconfig.json --watch"
}
```

### 2.2 Race avec `wait-and-start.js` style scripts

Si un orchestrateur dev attend `dist/main.js` et lance nodemon dès qu'il existe, il peut
lancer node **avant** que tsc-alias ait fini sa passe (tsc émet main.js → wait-script
détecte → nodemon lance node main.js ; tsc-alias finit après).

**Fix** : avant de lancer node, vérifier que `dist/` ne contient plus aucun `@alias` résiduel.

```js
// wait-and-start.js
const ALIAS_RE = /require\(["']@(auth|cache|common|config|database|security|modules)\//;
const distHasAliasResidual = () => {
  try {
    const { execSync } = require('child_process');
    execSync(
      `grep -rlE 'require\\(["']@(auth|cache|common|config|database|security|modules)/' --include='*.js' dist/`,
      { stdio: 'pipe' }
    );
    return true;  // exit 0 = au moins un fichier non transformé
  } catch (e) {
    return false; // exit 1 = dist/ propre
  }
};
```

Vérifier sur **toute la dist/**, pas juste `main.js` — le crash peut venir d'un fichier de
config (ex: `dist/config/app.config.js`) chargé indirectement.

### 2.3 Build chain dans Docker

Le `Dockerfile` doit appeler `npm run build` (qui chain `tsc + tsc-alias`), PAS `tsc` directement.
Si le Dockerfile fait `npm prune --omit=dev` après le build, `tsc-alias` (devDep) est supprimé,
mais **ça n'a aucun impact runtime** car `dist/` ne contient déjà plus aucun `@alias`.

## 3. Convention alias backend (canon AutoMecanik)

```jsonc
// backend/tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@auth/*":     ["src/auth/*"],
      "@cache/*":    ["src/cache/*"],
      "@common/*":   ["src/common/*"],
      "@config/*":   ["src/config/*"],
      "@database/*": ["src/database/*"],
      "@security/*": ["src/security/*"],
      "@modules/*":  ["src/modules/*"]
    }
  }
}
```

```jsonc
// backend/jest.config.js
{
  "moduleNameMapper": {
    "^@auth/(.*)$":     "<rootDir>/src/auth/$1",
    "^@cache/(.*)$":    "<rootDir>/src/cache/$1",
    "^@common/(.*)$":   "<rootDir>/src/common/$1",
    "^@config/(.*)$":   "<rootDir>/src/config/$1",
    "^@database/(.*)$": "<rootDir>/src/database/$1",
    "^@security/(.*)$": "<rootDir>/src/security/$1",
    "^@modules/(.*)$":  "<rootDir>/src/modules/$1"
  }
}
```

## 4. Codemod recipe (sed multi-niveaux ancré sur `from '...'`)

```bash
# Pattern (\.\./)+ ratisse 1, 2, 3, 4+ niveaux d'un coup
# Ancré sur 'from \'' pour ne pas toucher strings/commentaires/docs
find backend/src -name "*.ts" -exec sed -i -E \
  -e "s|from '(\.\./)+database/services/supabase-base\.service'|from '@database/services/supabase-base.service'|g" \
  -e "s|from '(\.\./)+common/exceptions'|from '@common/exceptions'|g" \
  -e "s|from '(\.\./)+auth/is-admin\.guard'|from '@auth/is-admin.guard'|g" \
  -e "s|from '(\.\./)+common/utils/error\.utils'|from '@common/utils/error.utils'|g" \
  -e "s|from '(\.\./)+auth/authenticated\.guard'|from '@auth/authenticated.guard'|g" \
  -e "s|from '(\.\./)+cache/cache\.service'|from '@cache/cache.service'|g" \
  -e "s|from '(\.\./)+security/rpc-gate/rpc-gate\.service'|from '@security/rpc-gate/rpc-gate.service'|g" \
  {} +

# Safety net : repérer les fichiers avec un nombre de modifs aberrant
git diff --stat | sort -k3 -n -r | head -20

# Vérification finale : aucun résiduel
grep -rE "from '(\.\./)+(auth|cache|common|config|database|security|modules)/" backend/src --include='*.ts' | head
```

## 5. Vérifications post-codemod (checklist)

```bash
# Compilation
npm run typecheck                       # 0 erreur

# Build + tsc-alias
npm run build
grep -rE "require\(['\"]@(auth|cache|common|config|database|security|modules)/" dist/  # VIDE
grep -rE "from ['\"]@(auth|cache|common|config|database|security|modules)/" dist/      # VIDE

# Syntax sans booter
node --check dist/main.js

# Lint (cache obsolète après ~487 modifs)
rm -rf .eslintcache && npm run lint

# Tests (Jest moduleNameMapper synchro)
npm run test

# Boot dev
npm run dev   # vérifier "Nest application successfully started"
curl localhost:3000/health  # 200 OK
```

## 6. Dette restante

Cette session a migré 586 imports sur le top 7 chemins (~49% du volume relatif). ~510
imports relatifs restent hors top 7 (`config/feature-flags.service`, `workers/processors/*`,
`shared/crypto/*`, etc.). Migration progressive recommandée par PRs successives.

Les alias métier dédiés (`@commerce/*`, `@content/*`, etc.) sont différés à après le
regroupement modules → 6 familles thématiques.

## Références

- PR #190 — `feat(backend): add typescript path aliases for infra layers`
- PR #192 — `fix(backend): resolve tsc-alias race in dev:compile watch mode`
- [tsc-alias docs](https://github.com/justkey007/tsc-alias)
- Plan local : `/home/deploy/.claude/plans/verifier-audit-complet-dreamy-treasure.md`
