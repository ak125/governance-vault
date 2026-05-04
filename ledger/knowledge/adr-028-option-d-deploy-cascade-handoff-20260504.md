---
type: handoff
session_date: 2026-05-04
session_class: incident-recovery
adr_refs: [ADR-028, ADR-031]
status: in_progress
next_session_required: true
---

# ADR-028 Option D — 7-class deploy main cascade (handoff 2026-05-04)

## Context

Le 2026-04-30 deux PRs monorepo (`#246` SupabaseBaseService READ_ONLY mode +
`#248` retire SERVICE_ROLE_KEY de `.env.preprod`) ont activé ADR-028 Option D
(preprod read-only hardening) sans auditer **toutes** les dépendances backend
qui consomment SERVICE_ROLE_KEY/SESSION_SECRET/PAYBOX/SYSTEMPAY/RAG_*.

Conséquence : `🚀 Deploy → 🧪 Deploy PREPROD` cassé sur **chaque push main
2026-04-30 → 2026-05-04**. ~12 deploys consécutifs failed sur le step
preprod healthcheck (container restart loop, NestJS bootstrap throw).

## 7 classes de strict-validation découvertes empiriquement (chaque fix
révèle la suivante au boot suivant)

| # | Classe | Site | PR | Status |
|---|---|---|---|---|
| 1 | Boot validator strict 8 vars | `backend/src/config/env-validation.ts` | [#274](https://github.com/ak125/nestjs-remix-monorepo/pull/274) | ✅ MERGED 2026-05-03 14:31 |
| 2 | NestJS ConfigModule load (PAYBOX_*/SYSTEMPAY_*) | `backend/src/config/payment.config.ts` | [#276](https://github.com/ak125/nestjs-remix-monorepo/pull/276) | ✅ MERGED 14:50 |
| 3 | createAppConfig (SERVICE_ROLE_KEY in production) | `backend/src/config/app.config.ts` | [#277](https://github.com/ak125/nestjs-remix-monorepo/pull/277) | ✅ MERGED 15:38 |
| 4 | 15 services Supabase eager constructors | `backend/src/modules/**` | [#284](https://github.com/ak125/nestjs-remix-monorepo/pull/284) | ✅ MERGED 2026-05-04 12:08 |
| 5 | 4 services Supabase config eager (write-guard) | `backend/src/config/{write-guard-cas,ledger,content-write-{gate,executor}}.service.ts` | [#287](https://github.com/ak125/nestjs-remix-monorepo/pull/287) | ✅ MERGED 12:46 |
| 6 | NestJS `getOrThrow` (RAG_SERVICE_URL/RAG_API_KEY) | `.github/workflows/ci.yml` (`.env.preprod` heredoc) | [#291](https://github.com/ak125/nestjs-remix-monorepo/pull/291) | ✅ MERGED 14:14 |
| **7** | **Bootstrap SESSION_SECRET in production** | **`backend/src/main.ts:64`** | **[#298](https://github.com/ak125/nestjs-remix-monorepo/pull/298)** | 🟡 **OPEN, auto-merge en attente CI re-run** |

## Pattern canonique commun

**Cause racine** : NODE_ENV=production est forcé par `Dockerfile` L39+L63 et
`docker-compose.preprod.yml` L9 (intentionnel : Node.js + libs optimisations).
Mais `READ_ONLY=true` est le vrai gating flag pour ADR-028 Option D. Tout
check qui compare `NODE_ENV === 'production'` sans `&& !READ_ONLY` fire à tort.

**Fix canonique** : ajouter `&& !readOnly` (via `isReadOnlyMode()` exporté de
`backend/src/config/env-validation.ts` PR #274) à chaque check strict.

**Helper centralisé** : `backend/src/common/utils/supabase-key.util.ts::getEffectiveSupabaseKey()`
(livré PR #284) pour les sites qui faisaient `createClient(url, SERVICE_ROLE_KEY)`
au constructor — fallback ANON_KEY en read-only.

## État au moment du handoff (2026-05-04 ~16:50 UTC)

- **6 PRs merged** sur 7 (cascade 1-6 closed)
- **PR #298 OPEN** : code prêt, signed commit, prettier ✓, tsc ✓
  - Branche BEHIND main (devops dependabot PRs ont avancé main pendant le cycle)
  - `gh api -X PUT /pulls/298/update-branch` triggered → CI re-tourne
  - Auto-merge `--auto --squash` enabled — fire quand CI complète
- **`DEV Safety (Observe)` GATE-3** échoue mais marqué non-blocking dans le job summary (`Observe gates (non-blocking): GATE-2/GATE-3`). À surveiller mais pas bloquant.
- **Dernier deploy main cassé** : `00fde552` (post-#291), erreur `SESSION_SECRET requis en production` — exactement ce que #298 fixe
- **Phase F.5 ADR-031** (orthogonal, sur `automecanik-rag` + vault) : ALL MERGED hier 2026-05-03

## Actions next session

1. **Vérifier #298 mergé** : `gh pr view 298 --repo ak125/nestjs-remix-monorepo`
2. **Si merged** : surveiller le deploy main qui en découle. Step `🧪 Deploy PREPROD` doit exit 0 (~8m23s historique).
3. **Si deploy vert** : 3-day deploy block définitivement résolu. Mettre à jour mémoire `feedback_sandbox_destructive_actions` avec retex.
4. **Si deploy rouge** (8e classe) : sweep ultra-large
   - `rg "isProd && !\|process.env.NODE_ENV === 'production'" backend/src/`
   - `rg "throw new Error\|throw new ConfigurationException" backend/src/main.ts backend/src/config/`
   - Tout site qui throw au boot sur var manquante en mode prod sans check READ_ONLY
5. **Optionnel** : créer un test e2e bootstrap qui simule `READ_ONLY=true NODE_ENV=production` minimal env pour catcher la 8e classe avant deploy.

## Anti-patterns à éviter (retex de la cascade)

- ❌ Roll-out d'ADR sans audit grep complet de toutes les consommations env vars (PRs #246/#248 ont activé Option D sans cet audit — d'où la cascade)
- ❌ Strict throws sur `NODE_ENV === 'production'` sans considérer un mode de déploiement read-only (préprod ≠ prod canonical)
- ❌ Sweep limité à un sous-arbre (`backend/src/modules/`) quand la même classe vit aussi dans `backend/src/config/` — sweep doit être sur tout `backend/src/` puis `backend/`
- ❌ `getOrThrow` au constructor pour des vars qui ont un default documenté ailleurs — soit le default est wired (env), soit on tolère absent (helper)

## Liens

- PRs cascade : #274 #276 #277 #284 #287 #291 #298 (monorepo)
- Phase F.5 : vault #139 + rag #8/#9/#10 (mergées 2026-05-03)
- Plan canonique Phase F.5 : `/home/deploy/.claude/plans/verifier-et-analyser-et-pure-rabbit.md`
- Memory : `phase-f5-runtime-hardening-plan.md`, `feedback_no_questionnaire_propose_best.md`
