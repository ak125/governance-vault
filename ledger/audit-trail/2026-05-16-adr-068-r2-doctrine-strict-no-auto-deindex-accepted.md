---
date: 2026-05-16
type: audit-trail
related: [ADR-068, ADR-067, ADR-066, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-16 — ADR-068 R2 doctrine STRICT renforcée (4 actions auto interdites + règle affirmative + REJECT scope énumérable)

## What

Création et acceptance de [[ADR-068-r2-doctrine-strict-no-auto-deindex]] qui **amende** [[ADR-066-r2-content-composition-v2]] ET [[ADR-067-r2-no-auto-suppression]] :

- ADR-068 `status: accepted` (date 2026-05-16, decision_maker `@fafa`, reviewed_by `@fafa`)
- **4 actions auto INTERDITES** sur page valide (extension scope ADR-067) :
  1. SUPPRESSION auto (déjà ADR-067)
  2. DÉSINDEXATION auto (`decision='noindex_follow'` sur page valide)
  3. CANONICALISATION auto vers sœur
  4. EXCLUSION SITEMAP auto
- **Règle affirmative canon** : `productCount ≥ 2 + compatibilité réelle = DOIT rester candidate INDEX`
- **REJECT scope strict 4 raisons UNIQUES** : `productCount_under_2`, `data_invalid`, `url_impossible`, `compatibility_absent` (pas similarité)
- **Renommage** `review` → `review_required` (cohérence canon vs DB enum)
- Rego policy `r2-content-write.rego` : 3 nouveaux deny invariants ADR-068
- Règle 6 `pipeline_generated_reject` durci : exige `reject_reason ∈ {4 strict reasons}`
- 77/77 tests OPA pass (22 h1-write + 33 r2-content-write amendés/nouveaux + 15 r2-cluster-health intact + 7 nouveaux ADR-068 specific)
- WASM bundle `r2-content-write.wasm` regénéré (nouvelle SHA `918111a9…`)
- Pas de modification `r2-cluster-health.rego` ni de son WASM

## Why

Doctrine évolutive post-calibration empirique :

| ADR | Date | Doctrine |
|-----|------|----------|
| ADR-066 | 2026-05-15 | Pipeline 4-gates avec **5 outcomes** dont SUPPRESSED auto |
| ADR-067 | 2026-05-15 | Amend : SUPPRESSED **automatique** interdit → **4 outcomes** (manual-only path conservé) |
| ADR-068 | 2026-05-16 | Renforce : **4 actions auto interdites** (étend SUPPRESSED à désindex + canonical + sitemap exclu) + règle affirmative + REJECT scope énumérable |

Décision @fafa 2026-05-16 : la doctrine ADR-067 reste incomplète. Un pipeline peut techniquement "suppress" une page via plusieurs chemins :

1. `status='suppressed'` (déjà bloqué par ADR-067)
2. **`decision='noindex_follow'` sur page valide** (pas bloqué jusqu'à ADR-068)
3. **`<link rel="canonical">` vers sibling auto** (pas bloqué jusqu'à ADR-068)
4. **Exclusion sitemap auto** (pas bloqué jusqu'à ADR-068)

ADR-068 ferme les 3 portes dérobées et énonce positivement que **toute page valide DOIT rester candidate INDEX**.

REJECT scope également durci : 4 raisons UNIQUES exhaustives (productCount<2, data invalid, URL impossible, compatibility absent). Similarité forte n'est PAS une raison REJECT — uniquement REVIEW_REQUIRED.

## Changements concrets

### Vault (cette PR)

- `ledger/decisions/adr/ADR-068-r2-doctrine-strict-no-auto-deindex.md` (nouvelle)
- `policies/seo-content/r2-content-write.rego` :
  - **DENY 1 ADR-068** : `pipeline_generated + decision='noindex_follow' + productCount >= 2` → deny (anti désindexation auto sur page valide)
  - **DENY 2 ADR-068** : `pipeline_generated + decision='reject' + reject_reason ∉ {4 strict}` → deny (REJECT scope énumérable)
  - **DENY 3 ADR-068** : `pipeline_generated + decision IN {index, review_required} + canonical_url != self_url` → deny (anti canonical sibling auto)
  - Règle 6 `pipeline_generated_reject` : nouvelle exigence `is_valid_reject_reason(input.reject_reason)`
  - Helper `valid_reject_reasons` set : `{productCount_under_2, data_invalid, url_impossible, compatibility_absent}`
- `policies/seo-content/r2-content-write_test.rego` :
  - 7 nouveaux tests ADR-068 (deny noindex valide, deny REJECT pour similarité, allow REJECT 4 raisons, deny canonical sibling auto, allow canonical self, etc.)
  - Test `test_allow_pipeline_reject` → `test_allow_pipeline_reject_with_valid_reason` (ajout `reject_reason: 'productCount_under_2'`)
- `dist/policies/r2-content-write.wasm` regénéré (SHA `918111a9…`)
- `ledger/audit-trail/2026-05-16-adr-068-r2-doctrine-strict-no-auto-deindex-accepted.md` (cette entrée)
- `ops/moc/MOC-AuditTrail.md` : ligne 2026-05-16 ADR-068

### Memoire monorepo `feedback_no_auto_page_suppression_ever`

Réécrite (2026-05-16) — étendue de "1 interdiction (SUPPRESSED)" à **"4 interdictions strictes"** :
- 4 actions auto interdites listées explicitement (suppression + désindex + canonical + sitemap exclusion)
- Règle affirmative canon (page valide DOIT rester INDEX candidate)
- REJECT scope strict (4 raisons UNIQUES)
- "Similarité forte signifie" : enrichissement OU REVIEW_REQUIRED, jamais des 4 actions
- Cross-refs ADR-066 + ADR-067 + ADR-068

### Monorepo (PR fixup à suivre, séparée)

À implémenter :
- `R2EligibilityVerdictEnum` : `['eligible', 'review', 'reject']` → `['eligible', 'review_required', 'reject']`
- `R2EligibilityService.evaluate()` :
  - Below threshold + productCount ≥ 2 → `verdict: 'review_required'` (was `'review'`)
  - REJECT scope : raisons explicites parmi les 4 strict
- DTO `R2EnrichSingleResponse.eligibility.verdict` : enum update
- Tests Jest mis à jour

## Verification locale

```
$ /tmp/opa test policies/seo-content/
PASS: 77/77
```

- 22 h1-write tests (régression PR-V intacte)
- 33 r2-content-write tests (ADR-066+067+068 cumulés)
- 15 r2-cluster-health tests (intacts, invariants cluster valables)
- 7 new ADR-068 specific tests

WASM reproducible (paths relatifs depuis vault root) :
- `h1-write.wasm` SHA inchangé `ce9ba9f2…`
- `r2-content-write.wasm` SHA nouvelle `918111a9…` (3 deny rules + reject_reason validator ajoutés)
- `r2-cluster-health.wasm` SHA inchangé `e66f857493…`

## Impacts cross-canon

- **ADR-066** : amended par ADR-067 + ADR-068
- **ADR-067** : amended par ADR-068 (étend interdictions)
- **ADR-058 (Repository Control Plane)** : pas d'impact ownership
- **MOC-Decisions** : ADR-068 indexé sous "amendments" cascade ADR-066/067
- **MOC-AuditTrail** : ligne 2026-05-16 ajoutée

## Hors scope post-acceptance

- Migration historique : aucun (zéro page R2 v2 publiée encore)
- Frontend canonical rendering : Remix route `pieces.$gamme...` doit émettre canonical self pour INDEX et REVIEW_REQUIRED (à valider PR 2 V1.5)
- Sitemap V10 R2 shards : doit INCLURE `decision IN ('index', 'review_required')`, EXCLURE `('reject', 'suppressed')` — à valider PR 2 V1.5
- Comportement R8/autres rôles : ADR-068 scope strict R2. Doctrine 4-actions-interdites documentée comme **canon transverse** dans memory `feedback_no_auto_page_suppression_ever` (anti-régression future)

## Self-review verdict: APPROVE

3 ADR successifs (066 → 067 → 068) en 2 jours = preuve doctrine évolutive pré-production. Coût correction = zéro (aucune page R2 v2 publiée). Bénéfice = doctrine étanche AVANT PR 2 V1.5 (pipeline complet). Tests 77/77 pass. WASM reproducible. Mémoire monorepo cohérente. Cross-refs ADR-066+067 préservés via `amends`. Prêt pour merge.
