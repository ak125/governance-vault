---
title: "Session 2026-04-27 — Vault governance hardening (G2 fixes + auto-merge + CODEOWNERS)"
date: 2026-04-27
type: session-trail
related_adr: ["ADR-015"]
related_prs:
  - "ak125/governance-vault#77"
  - "ak125/governance-vault#88"
  - "ak125/governance-vault#90"
  - "ak125/governance-vault#94"
  - "ak125/governance-vault#95"
status: closed
session_closed_at: 2026-04-27
---

# Session 2026-04-27 — Vault governance hardening

## Résumé

Session courte centrée sur **deux objectifs imbriqués** :

1. **Débloquer 2 PRs ouvertes qui échouaient sur G2 Zero Orphelin** (PR #77 ADR-029 + PR #88 fleet advisor session) — au final, conflit DIRTY contre `main` à régler en plus du link manquant.
2. **Renforcer la protection de `main`** en activant `Allow auto-merge` + `CODEOWNERS` + 5 G* checks requis + 1 approval + code-owner reviews — pour discipline volontaire avec audit-trail des admin-overrides.

L'idée motrice côté gouvernance : passer d'un `main` "CI-protected mais non review-protected" à un `main` "CI + review code-owner" sans bloquer le workflow solo (admin override autorisé mais loggé).

## Décisions prises

### 1. Pattern G2 = MOC update dans la même PR que le nouveau .md

Confirmé par PR #86 (ADR-024) : tout nouveau `.md` hors whitelist (`ops/moc/`, `99-meta/`, `_assets/`, `_templates/`, `_scripts/`) doit être linké dans une MOC dans la **même** PR qui l'introduit. Sinon G2 échoue à l'ouverture.

→ Pattern à appliquer pour toute future ADR / audit-trail / knowledge entry.

### 2. Auto-merge actif + branch protection renforcée

Avant cette session :
- `allow_auto_merge: false`
- 4/5 G* checks requis (manquait `No V1 Paths (ADR-015)`)
- `required_approving_review_count: 0`
- `require_code_owner_reviews: false`
- `enforce_admins: true`

Après cette session :
- `allow_auto_merge: true`
- `delete_branch_on_merge: true` (hygiène)
- 5/5 G* checks requis
- `required_approving_review_count: 1`
- `require_code_owner_reviews: true`
- `enforce_admins: false` ← changement délibéré : permet à l'admin solo (@ak125) de bypasser le 1-approval requirement, **chaque bypass étant tracé publiquement** dans l'historique GitHub de la PR.
- `dismiss_stale_reviews: true` (déjà actif)
- `required_linear_history: true` (déjà actif)

### 3. CODEOWNERS — paths canon-sensibles uniquement

Fichier `.github/CODEOWNERS` (mergé via PR #90, sha 4348555 → squash 2e11d0d sur main) :

```
ledger/decisions/**                          @ak125
ops/rules/**                                 @ak125
.github/CODEOWNERS                           @ak125
.github/workflows/vault-governance.yml       @ak125
.github/workflows/vault-weekly-lint.yml      @ak125
```

→ Routine PRs (audit-trail, knowledge, MOCs, scripts) : **pas** de code-owner review bloquante, juste 1 approval (admin override OK).

→ Canon PRs : 1 approval **+** approval @ak125 spécifiquement (donc admin override obligatoire si solo).

## Évidence runtime

### PRs réparées

| PR | Branche | SHAs (avant → après rebase) | État final |
|---|---|---|---|
| #77 | `feat/adr-029-rag-v2.1-control-plane` | `f4a63e1` (failure G2) → `e2067c7` (orphan fix, mais DIRTY) → `94c4baf` (rebased onto main) | mergeStateStatus: CLEAN, 5/5 G* SUCCESS |
| #88 | `audit/2026-04-25-fleet-advisor-session` | `58be6cd` (failure G2) → `bed866d` (orphan fix, mais DIRTY) → `77c21bc` (rebased onto main) | mergeStateStatus: CLEAN, 5/5 G* SUCCESS |
| #90 | `chore/codeowners-canon-20260427` | `4348555` (CODEOWNERS) | MERGED 14:43:38Z, branch supprimée auto |

### Fichiers MOC modifiés

- `ops/moc/MOC-AuditTrail.md` : 2 entrées ajoutées (PR #77 + PR #88) + 1 entrée pour CETTE session-trail
- `ops/moc/MOC-Decisions.md` : ADR-029 row dans table + entry sous SEO category, note "in-flight" mise à jour pour drop ADR-029 (déjà listée maintenant)

### CI verification finale

```
=== REPO SETTINGS ===
auto_merge: true
delete_on_merge: true

=== PROTECTION main ===
required_checks: ["G2: Zero Orphelin", "Broken Wikilinks", "G3: Commits signes", "G4: CI read-only sur canon", "No V1 Paths (ADR-015)"]
approvals_required: 1
code_owner_reviews: true
dismiss_stale: true
enforce_admins: false
linear_history: true
force_pushes_blocked: true

=== CODEOWNERS on main ===
.github/CODEOWNERS (822 bytes, sha=0665c6f)
```

## Reste à faire (TODO)

### Court terme (cette semaine)

- [ ] **Merger PR #77 (ADR-029 RAG v2.1 Control Plane Closure — proposed)**
  - Touche `ledger/decisions/adr/` → CODEOWNERS s'applique → exige approval @ak125
  - Solo admin → bypass via "Merge without waiting for requirements" (tracé publiquement)
  - Alternative : laisser ouverte tant qu'un 2e reviewer humain ou bot n'est pas en place

- [ ] **Merger PR #88 (fleet advisor session)**
  - Touche `ledger/audit-trail/` uniquement → CODEOWNERS ne s'applique PAS, juste 1 approval requise
  - Solo admin → bypass via admin merge

- [ ] **Vérifier autres PRs ouvertes** (#65, #70, #72, #75, #76, #78, #89) qui passent maintenant en `UNKNOWN` à cause de la nouvelle protection :
  - Si elles touchent `ledger/decisions/**` ou `ops/rules/**` → review code-owner requise
  - Sinon → 1 approval / admin override OK
  - Probablement plusieurs à rebase aussi si elles datent d'avant 2026-04-25

### Moyen terme (~2 semaines)

- [ ] **Auditer le rythme d'admin-overrides** : si > 5/semaine sur canon, c'est que la barre est trop haute et qu'il faut soit retirer la règle, soit ajouter un 2e reviewer (humain ou bot).
  - Source : timeline GitHub des PRs canon → chaque bypass laisse un événement visible.
  - Proposition d'agent scheduled non-confirmée (offerte mais l'utilisateur n'a pas tranché).

### Long terme (ADR séparé)

- [ ] **Concevoir un agent `vault-canon-reviewer`** (Claude API) qui :
  - Auto-review les PRs touchant `ledger/decisions/**` selon les templates ADR (frontmatter, sections obligatoires, related_rules cohérent)
  - Auto-review les PRs touchant `ops/rules/**` selon le format des règles existantes
  - Approve si checklist OK, comment + request-changes sinon
  - Permettrait de retirer `enforce_admins: false` et viser **zéro override** sur canon.
  - **Hors scope de cette session.** À ouvrir comme nouvelle ADR (ADR-030 disponible au 2026-04-27).

## Apprentissages

1. **G2 + main movement = trap classique.** Une PR ouverte avant que main bouge peut devenir DIRTY entre l'ouverture et le merge. Quand ça arrive, `pull_request` event ne re-déclenche pas la CI tant que le merge ref est invalide → la PR semble "stuck" mais en réalité c'est un conflit silencieux. Le diagnostic passe par `gh pr view --json mergeStateStatus`.

2. **GitHub `require_code_owner_reviews` exige `required_approving_review_count >= 1`.** Pas moyen de configurer "approval *uniquement* sur paths CODEOWNERS, zéro ailleurs" via classic branch protection. Les **rulesets** (système plus récent) permettent du path-based, mais c'est un autre design — non utilisé ici par souci de simplicité.

3. **`enforce_admins: false` + admin override loggé = compromis solo viable.** Pour un solo maintainer, exiger 1 approval sans permettre admin override = repo bloqué. Le compromis "admin peut bypasser mais c'est tracé" garde la discipline visible sans paralysie.

4. **Pattern de `.gitignore` côté worktree ne protège pas le WIP user.** Si un worktree principal a des modifs non-committées (cas de cette session : `ops/moc/MOC-Knowledge.md` modifié + investigation file untracked), `git checkout main` échoue. Solution : créer un worktree séparé depuis `origin/main` au lieu de stash/reset.

## Références

- [[ADR-015-vault-single-source-of-truth]] (vault SoT, motivation de la protection)
- PR #77 contenu : `ledger/audit-trail/2026-04-25-session-adr-029-p1-status.md` (sera linkable une fois mergé)
- PR #88 contenu : `ledger/audit-trail/2026-04-25-fleet-advisor-and-seo-monitoring-session.md` (sera linkable une fois mergé)
- PR #86 (ADR-024) — pattern canonique "MOC update dans la même PR" appliqué ici
- PR #90 (CODEOWNERS) — première PR mergée sous le nouveau régime
- PR #94 (fix wikilinks INC-2026-012) — première application du pattern admin-merge documenté en #95
- PR #95 (single-maintainer pattern doc) — codification canon du pattern (CODEOWNERS commentaire + knowledge note)

## Continuation 2026-04-27 (suite, ~17:00–19:30 UTC) — première application du pattern

Reprise de la session le même jour pour exécuter les 2 PRs préalables à la séquence ADR-026 P0 :

### PR #94 — fix wikilinks INC-2026-012 + G2 link MOC-Knowledge

- **Branche** : `fix/broken-wikilinks-inc-2026-012-adr-016`
- **Commits signés** : `f49c81e` (wikilinks fix) + `a7cd201` (MOC-Knowledge link)
- **CI finale** : 5/5 PASS (G2 + G3 + G4 + Broken Wikilinks + No V1 Paths)
- **Merge** : admin squash → `8ed6184` à 17:19:34Z
- **Rationale documentée** : single-maintainer (cf. CODEOWNERS commentaire ajouté en #95)
- **Évidence préalable** : `main` était rouge sur Broken Wikilinks (run `25007061211`) après l'admin-merge initial de PR #48

### PR #95 — single-maintainer + admin-merge pattern

- **Branche** : `docs/single-maintainer-mode-codeowners`
- **Commit signé** : `de8ec21`
- **CI finale** : 5/5 PASS
- **Merge** : admin squash → `7726b91` à ~17:25Z
- **Effet** : pattern codifié en `ledger/knowledge/single-maintainer-merge-pattern.md` + bloc commentaire `.github/CODEOWNERS`. Aucune modification de la branch protection API.

### Pattern observé

- 2/2 admin-merges réalisés sans bypass de gate CI rouge (5/5 verts dans les deux cas)
- 2/2 commits signés G3 (clé `vault-signing@automecanik.com`)
- 2/2 audit-trail (cette section) — la traçabilité est dans ce fichier, mergé via PR #91

→ Le pattern documenté en #95 est **opérationnel et auto-référent** : cette PR #91 elle-même est mergée selon le même flow (signed commit + 5 CI verts + admin-squash + audit-trail dans cette session-trail).
