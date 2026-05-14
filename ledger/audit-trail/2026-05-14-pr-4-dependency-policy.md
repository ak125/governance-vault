---
date: 2026-05-14
type: audit-trail
related: [POLICY-DEPENDENCY-MODERNIZATION, TRACKER-DEPENDENCY-UPGRADE-MATRIX, ADR-062, ADR-058, ADR-060, ADR-061, MOC-Policies, MOC-Governance]
verdict: APPROVE
---

# 2026-05-14 — PR-4 Dependency Modernization Policy (création proposed)

## What

PR-4 documentaire dans `governance-vault` :

- `ledger/policies/dependency-modernization-policy.md` — NEW (`status: proposed`)
- `ops/trackers/dependency-upgrade-matrix.md` — NEW (`status: active`), pré-amorcé avec 36 dépendances réelles (13 high-risk, 13 runtime-critical, 10 tooling)
- `ops/trackers/` — NEW directory
- `ops/moc/MOC-Policies.md` — section `## Dependency & Modernization Policies` ajoutée + wikilink
- `ops/moc/MOC-Governance.md` — section `## Trackers` ajoutée + wikilink
- `ledger/audit-trail/2026-05-14-pr-4-dependency-policy.md` — ce fichier

## Why

Le séquence de contracts ADR-062 (PR-0 → PR-3a) gouverne **ce qu'est** le monorepo (files, DB, RPC, architecture). Elle ne gouverne pas encore **comment il évolue** au niveau des dépendances. Une mise à jour future de `typescript`, `@nestjs/core`, `@remix-run/*`, `@supabase/supabase-js`, ou `redis` pourrait invalider silencieusement un contract déjà ratifié (anti-parallel-truth, ADR-062 §9).

PR-4 pose le gate gouvernemental au-dessus de la dépendance : classification 3-tier, decision template required-fields, promotion ladder aligné sur ADR-062 §5. Aucun upgrade n'est appliqué — la PR est purement documentaire.

## Self-review (8 items)

- [x] **Scope** : PR limitée à markdown + wiring MOC. Zéro runtime / package.json / CI modifié. `git diff --name-only origin/main..HEAD` ne montre que des `.md` sous `ledger/` et `ops/`.
- [x] **Frontmatter compliance** : les deux fichiers neufs portent `id`, `title`, `status`, `version`, `date`, `scope`, `authority`, `owner`, `related_adrs`, `tags`. Conforme aux conventions vault (vérifié contre BUNDLE-SPEC.md et rules-engineering-quality.md).
- [x] **Orphan check** : les deux fichiers neufs sont liés depuis au moins un MOC (MOC-Policies pour la policy, MOC-Governance pour le tracker).
- [x] **Wikilinks valid** : chaque `[[target]]` résout vers un note existant. Filename vérifié par `find ledger ops -name '*.md'` au pre-flight — `ADR-060-repository-roles-doctrine` (singulier) confirmé contre la divergence initiale du draft.
- [x] **ADR alignment** : la policy se subordonne explicitement à ADR-062 §1-6 (6-stage pattern) et §5 (promotion gate). Pas de nouvel ADR requis — c'est une policy sous canon existant.
- [x] **Versions are snapshot values, not infra constants** : les chaînes de version dans la matrice sont des snapshots documentés des ranges déclarés dans les manifests `package.json` (root + `backend/` + `frontend/` + `packages/*`) au 2026-05-14, rafraîchis par la `Reconciliation procedure` du tracker. Les valeurs résolues par lockfile ne sont volontairement PAS mirrorées ici (elles vivent dans les commits d'upgrade PR). Pas d'IP, UUID, ni clé.
- [x] **Signed commit** : SSH signing actif (`commit.gpgsign=true`, `gpg.format=ssh`, key `/home/deploy/.ssh/vault_signing_key.pub`). Vérifié post-commit via `git log --show-signature -1`.
- [x] **No CI / runtime change** : `git diff --name-only origin/main..HEAD | grep -E "(package\\.json|\\.github/workflows/|Dockerfile|docker-compose)"` retourne vide.

## Verdict

**APPROVE** — prêt pour admin-merge dès que `vault-governance.yml` est vert.

## Promotion path

Promotion de la policy `proposed → accepted` requiert :

- ≥ 1 upgrade réel landé proprement sous la policy
- ≥ 3 runs verts consécutifs de `vault-governance.yml` sur `main`

Aucun follow-up automatique ne sort de cette PR (anti auto-escalation rule).

## Cross-references

- ADR-062 Repository Contract System (accepted 2026-05-14, commit `f6c2bd3`, PR ak125/governance-vault#269)
- PR series PR-0 → PR-3a (Architecture Contract V1 ak125/nestjs-remix-monorepo#507, DB Contract V1 ak125/nestjs-remix-monorepo#511)
- `.github/dependabot.yml` côté monorepo applicatif (counterpart opérationnel — weekly schedule, max 5 PRs, react/nestjs/remix majors freeze)
