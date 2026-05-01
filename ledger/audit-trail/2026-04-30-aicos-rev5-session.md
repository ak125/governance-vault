---
title: "Session AI-COS rev5 — 7 PRs livrées (ADR-034 + ADR-030 + ADR-028 Option D + routine cost-check + 3 monorepo)"
date: 2026-04-30
type: audit-trail
related_adr: ["ADR-034", "ADR-028", "ADR-030"]
related_inc: ["PR-monorepo-242-revert-2026-04-30T21-42Z"]
status: session-trail
session_duration: "~6h (analyse + 5 itérations plan + exécution)"
---

# Session AI-COS rev5 — 2026-04-30

## Contexte

Session démarrée par challenge utilisateur d'une stratégie d'architecture AI-COS proposée initialement. Au cours de l'analyse :

1. Première proposition (rev1) spontanément orientée vers reconstruction d'un orchestrateur maison sur AI-COS — **bricolage rejeté** par utilisateur ("no bricolage, best solutions").
2. Repivot rev2 → rev5 successifs sous instruction utilisateur "meilleure approche moderne robuste pas de bricolage", verrouillé par 4 conditions de qualité + 5 verrous additionnels (cf. plan).
3. Découverte secondaire : surfacturation Supabase Branches (Compute Branching non couvert par Spend Cap), invalidation Option C (Supabase branch ~$10-20/mo réaliste) au profit d'**Option D — read-only hardening à $0/mo**.

## Plan exécuté

Plan source : `/home/deploy/.claude/plans/harmonic-mapping-elephant.md` (rev5, "no-bricolage best-solutions" iteration).

### Bloc principal — 7 PRs MERGED

| # | Repo | Sujet | Commit |
|---|---|---|---|
| 119 | governance-vault | ADR-034 AI-COS Operating Contract + AP-12 anti-bricolage | `a0e0b51` |
| 120 | governance-vault | ADR-030 npm-ignore-scripts (rétroactif PR monorepo #168) | `f914e59` |
| 244 | nestjs-remix-monorepo | Revert préventif PR #242 (incident séquencement) | `f8a0e715` |
| 246 | nestjs-remix-monorepo | SupabaseBaseService READ_ONLY mode + ANON_KEY fallback | `dfd81673` |
| 248 | nestjs-remix-monorepo | ci.yml retire ALLOW_PROD_ENV_COPY + SERVICE_ROLE_KEY | `068d2088` |
| 123 | governance-vault | ADR-028 Option D `accepted` (5 couches défense) | `cb8080b` |
| 124 | governance-vault | Routine `vault-supabase-cost-check` V1 LIVE | `36c6327` |

## Décisions architecturales canonisées

### ADR-034 — AI-COS Operating Contract

AI-COS = **observatoire isolé**, pas orchestrateur runtime. 3 axes figés :

| Axe | Outil unique |
|---|---|
| Trigger | GitHub Actions cron OU webhook |
| Execution | self-hosted runner DEV → Claude Code SDK / Python / MCP |
| Evidence | artifact GitHub + audit-trail markdown vault + issue P0/P1 NEW-only |

**Single-trigger discipline** : 1 routine = 1 déclencheur unique.

**6 anti-patterns figés** (AP-12 dans `rules-ai-antipatterns.md`) : pas de bus événementiel maison, scheduler daemon maison, registry agent maison, moteur permissions maison, dashboard custom maison, orchestrateur LangGraph maison.

Validation empirique : ADR-036 marketing applique déjà ce contrat (`OperatingMatrixService.MARKETING`, dual-workspace, single Paperclip routine).

### ADR-028 — Préprod read-only hardening Option D

Option C (Supabase branch $9.66/mo) **rejetée** après audit empirique :
- DEV humain pointe délibérément vers prod en lecture live (workflow productif inchangé)
- CI smoke tests = curl GET only (read-only en pratique)
- Risque "preprod écrit prod" théorique, jamais observé
- Surfacturation Supabase : Compute Branching non couvert par Spend Cap, dérive >$50/mo possible

**Option D adoptée** : 5 couches défense, $0/mois ajouté.

| Couche | Status | Source |
|---|---|---|
| 1. Pas de SERVICE_ROLE_KEY preprod | ✅ LIVE | PR #248 |
| 2. Anon key only | ✅ LIVE | PR #248 |
| 3. RLS hardening ADR-021 (204 objets) | ✅ Pré-existant | PR #42 |
| 4. READ_ONLY guard backend (15+ services SupabaseBaseService) | ✅ LIVE | PR #246 |
| 5. write-detect log scan CI | ⏸ Différé PR 2C | — |

Reformulation honnête : "Risque preprod écrit prod avec privilèges élevés **fortement réduit**" (pas "éliminé"). Risque résiduel listé : 10+ services `createClient` direct + tables post-ADR-021 sans RLS.

### Routine #2 LIVE — `vault-supabase-cost-check`

2ème routine LIVE après `vault-weekly-lint`. Pattern canonique ADR-034 §3-axes appliqué :

- **Trigger** : cron Monday 08:00 UTC + workflow_dispatch
- **Execution** : `curl` GET Management API + `jq` projection
- **Evidence** : artifact (redacted) + audit-trail markdown + issue P1 NEW-only si projection >$30/mo OU +20% delta

Verrou n°4 plan rev5 respecté : endpoint Management API documenté en commentaire workflow + knowledge file, JSON redacted via `jq walk` pour patterns `token|secret|key|password|refresh`, fail propre si HTTP non-200 ou schema response inattendu (pas silent NaN).

Secret `SUPABASE_ACCESS_TOKEN` à provisionner manuellement par owner (knowledge file `ledger/knowledge/supabase-management-token.md` documente procédure + scope `organizations:read` minimum + rotation).

## Incident traité — PR #242 → #244

**Problème** : PR #242 v1 (mergée 21:38Z) a retiré `SUPABASE_SERVICE_ROLE_KEY` du `.env.preprod` SANS avoir d'abord modifié `SupabaseBaseService` qui throw inconditionnellement `ConfigurationException` ligne 109 si la key manque. Deploy preprod aurait crashé au boot.

**Détection** : audit post-merge a révélé l'incohérence avant que le job Deploy `25190625023` (status `queued`) ne s'exécute.

**Résolution** : revert PR #244 mergée 21:42Z (4 min après incident). Aucune casse réelle.

**Leçon canonisée** :

- Mémoire `feedback_read_backend_before_modifying_ci.md` (utilisateur)
- ADR-028 §"Sur l'incident PR #242 → #244" canonisé dans le vault

**Bon ordre rétabli** :
1. PR #246 backend (rendre READ_ONLY tolérant) → MERGED 22:04:13Z
2. PR #248 CI (retirer SERVICE_ROLE_KEY) → MERGED 22:17:18Z
3. PR #123 ADR-028 (status accepted, implementation_evidence shipped) → MERGED 22:27:15Z

## Patterns appliqués (no-bricolage canon)

- `git worktree add` isolé pour chaque PR (skill `superpowers:using-git-worktrees`) — 4 worktrees créés/cleanupés
- Templates canon réutilisés : `_templates/adr-template.md` (ADRs) + `vault-weekly-lint.yml` (routine cost-check)
- Commits atomiques signés G3 ED25519 vault-signing@automecanik.com
- Single-maintainer admin merge pattern (CODEOWNERS vault) — `gh pr merge --admin --squash --delete-branch`
- Conflit MOC-Decisions résolu via rebase + force-with-lease (PR #120 vs PR #119 sur entrées proches)
- 5 couches de défense documentées (defense-in-depth)
- Pas d'overclaim ("fortement réduit" jamais "éliminé")
- ADR-028 préserve Options A/B/C historiques (trace décisionnelle)

## 5 mémoires utilisateur sauvegardées

1. `feedback_audit_workflow_before_proposing_infra.md` — Avant chiffrer infra coûteuse, GREP CI réel + auditer workflow utilisateur
2. `feedback_supabase_cost_traps.md` — Spend Cap ne couvre PAS Branching Compute / IPv4 / Read Replica / etc.
3. `feedback_no_overclaim_security_words.md` — "fortement réduit / atténué par N couches" pas "éliminé / 100% safe"
4. `feedback_git_worktree_for_concurrent_governance.md` — Worktree obligatoire pour gouvernance concurrente
5. `feedback_read_backend_before_modifying_ci.md` — Lire services backend AVANT retirer env var dans CI

## Coverage manifest (AEC v1.0.0)

| Champ | Valeur |
|-------|--------|
| `scope_requested` | Plan AI-COS rev5 bloc principal : ADR-034 + ADR-028 Option D + routine pilote cost-check + ADR-030 standalone |
| `scope_actually_scanned` | 7/7 PRs principales du bloc livrées et mergées sur main (vault + monorepo) |
| `files_read_count` | ~30 (ADR templates, MOCs, ci.yml, SupabaseBaseService, app.config, vault-weekly-lint template, rules canon, audit-trails existants, mémoires utilisateur) |
| `excluded_paths` | PR 2C monorepo (10+ services `createClient` direct + write-detect job CI) ; PR P2 vault (auto-MOC-routines + Healthchecks.io optionnel) — différés explicitement par le plan rev5, pas dans scope main |
| `corrections_proposed` | 7 PRs créées + 2 mémoires sur incidents + plan rev5 séquentiel ; toutes validées par utilisateur via "go" / "ok" / "continue" / "mergé" |
| `corrections_applied` | 7 PRs mergées par admin squash sous plan approuvé + CI verte (single-maintainer pattern documenté) ; 5 mémoires sauvegardées + MEMORY.md index updated |
| `validation_executed` | Tous les CI checks vault (5/5 SUCCESS sur chaque PR) + monorepo (15-18/24 SUCCESS, le reste SKIPPED post-merge conditionnels) + pre-commit local (G2 + check-broken-links + check-frontmatter-schema) |
| `remaining_unknowns` | Provisioning du secret `SUPABASE_ACCESS_TOKEN` (action manuelle utilisateur) ; Premier run réel de la routine cost-check (sera déclenché par cron Monday 08:00 UTC ou workflow_dispatch après provisioning) ; Couverture étendue READ_ONLY pour les 10+ services `createClient` direct (PR 2C, différé) |
| `final_status` | `SCOPE_SCANNED` — bloc principal plan AI-COS rev5 complet et mergé. Reste hors scope listé. |

## Hors scope (différé pour vagues ultérieures)

- **PR 2C monorepo** : extension 10+ services `createClient` direct (write-guard-*, content-write-gate, seo-monitoring/*, seo/internal-linking, etc.) au mode READ_ONLY + write-detect job CI (couche 5 défense)
- **PR P2 vault** : auto-MOC-Routines générateur (régénération depuis YAML front-matter `routine:` des workflows) + Healthchecks.io dead-man switch externe optionnel
- Audit RLS coverage post-ADR-021 (extension `weekly-vault-lint` pour flagger tables créées sans RLS)

## Action utilisateur requise pour activation routine

```bash
# Créer token sur https://supabase.com/dashboard/account/tokens
# Scope minimum : organizations:read uniquement (refuser tout write)
gh secret set SUPABASE_ACCESS_TOKEN --repo ak125/governance-vault --body '<TOKEN>'

# Vérifier provisioning
gh secret list --repo ak125/governance-vault | grep SUPABASE_ACCESS_TOKEN

# Test workflow (validera fail propre si schema change ou token invalide)
gh workflow run vault-supabase-cost-check.yml --repo ak125/governance-vault
```

Procédure complète + rotation : `ledger/knowledge/supabase-management-token.md`.

## Références

- Plan : `/home/deploy/.claude/plans/harmonic-mapping-elephant.md` (rev5)
- ADR-034 — AI-COS Operating Contract (`a0e0b51`)
- ADR-028 — Préprod read-only hardening Option D (`cb8080b`)
- ADR-030 — npm-ignore-scripts standalone (`f914e59`)
- AP-12 — Anti-pattern reconstruire orchestrateur maison sur AI-COS (`rules-ai-antipatterns.md`)
- Audit-trail pré-décision : `2026-04-30-preprod-isolation-audit.md`
- Knowledge token : `ledger/knowledge/supabase-management-token.md`
- 5 mémoires utilisateur sauvegardées dans `/home/deploy/.claude/projects/-opt-automecanik-app/memory/`
