---
date: 2026-05-15
type: audit-trail
related: [ADR-067, ADR-066, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-15 — ADR-067 R2 No-Auto-Suppression doctrine pivot (amendement ADR-066)

## What

Création et acceptance de [[ADR-067-r2-no-auto-suppression]] qui **amende** [[ADR-066-r2-content-composition-v2]] :

- ADR-067 `status: accepted` (date 2026-05-15, decision_maker `@fafa`, reviewed_by `@fafa`)
- Doctrine pivot : `SUPPRESSED automatique` est **strictement INTERDIT** pour le pipeline R2 v2
- Nouvelle matrice de décision automatisée : **INDEX | REVIEW | REGENERATE | REJECT** (4 sorties, pas 5)
- `SUPPRESSED` reste dans l'enum mais **manual-only** (admin override via UI uniquement)
- Rego policy `r2-content-write.rego` mise à jour : `pipeline_generated → suppressed` désormais `deny` ; `human_curated → suppressed` autorisé avec invariants canonical
- 69/69 tests OPA passent (22 h1-write + 28 r2-content-write nouveaux/amendés + 15 r2-cluster-health + 4 new tests ADR-067)
- WASM bundle `r2-content-write.wasm` regénéré (nouvelle SHA `ff894e55…`)
- Pas de modification `r2-cluster-health.rego` ni de son WASM (invariants cluster restent valables pour SUPPRESSED manuels)

## Why

[[ADR-066-r2-content-composition-v2]] (mergé `8a92c49`) a livré une matrice 5-décisions avec `SUPPRESSED` automatique sur catalog_overlap > 0.92 + sibling INDEX fiable. Le rationale : éviter le duplicate content massif quand 2 motorisations sœurs partagent > 92% du catalogue.

**Calibration empirique N=200** (Supabase MCP project `cxpojprgwgubzjyqzmoq`, 2026-05-15 post-merge PR 0 #281 + PR 1 #543) a révélé :

| Stratum | N | avg Jaccard piece-overlap | candidats SUPPRESSED auto (>92%) |
|---------|---|---------------------------|----------------------------------|
| G1 | 100 | 49% | 14 / 100 (14%) |
| G2 | 99 | 81% (p50=100%) | **57 / 99 (58%)** |

→ Sous la doctrine ADR-066, **58% des pages G2** auraient été désindexées automatiquement. Volume inacceptable.

**Décision @fafa 2026-05-15** : *"il est strictement interdit de supprimer des pages"*. La compatibilité pièce prime sur la similarité texte. Deux motorisations sœurs peuvent partager 93% des pièces ET pourtant requérir des pages distinctes (OEM différent, montage différent, année/phase différente, équipementier différent, stock/prix différent, risque erreur client différent).

ADR-067 codifie le pivot doctrinal.

## Changements concrets

### Vault (cette PR)

- `ledger/decisions/adr/ADR-067-r2-no-auto-suppression.md` (nouvelle)
- `policies/seo-content/r2-content-write.rego` :
  - Règle 1 `human_curated` désormais `not governance_decision == "suppressed"` (le SUPPRESSED humain passe par Règle 4)
  - Règle 4 `pipeline_generated_suppressed` → **remplacée** par `human_curated_suppressed` (manual override, requiert canonical_target valide)
  - Nouveau deny explicite : `pipeline_generated + decision=suppressed` → reason `ADR-067 — pipeline_generated cannot emit SUPPRESSED`
- `policies/seo-content/r2-content-write_test.rego` :
  - `test_allow_pipeline_suppressed_valid_canonical` → renommé `test_deny_pipeline_generated_suppressed_even_valid_canonical`
  - `test_deny_pipeline_suppressed_carries_adr067_reason` (nouveau)
  - `test_allow_human_curated_suppressed_valid_canonical` (nouveau)
  - `test_deny_human_curated_suppressed_missing_canonical` (nouveau)
  - Tests chain/cross-gamme : pipeline → human_curated source_kind
- `dist/policies/r2-content-write.wasm` regénéré (SHA `ff894e55…`)
- `ledger/audit-trail/2026-05-15-adr-067-r2-no-auto-suppression-accepted.md` (cette entrée)
- `ops/moc/MOC-AuditTrail.md` : nouvelle ligne 2026-05-15 ADR-067

### Monorepo (PR fixup à suivre)

- `R2EligibilityVerdictEnum` : `'eligible' | 'review' | 'reject'` (remove `'suppressed'`)
- `R2EligibilityService.evaluate()` : retire la branche SUPPRESSED auto. Si `score < THRESHOLD` ET `productCount ≥ 2` → `review`. Sinon `reject`.
- `R2DecisionV2Enum` : enum garde `'suppressed'` (DB compat) mais commentaire explicite "manual-only, never emitted by pipeline"
- `r2-eligibility.schema.ts` : `suppressedCanonicalTarget` field repurposed pour `manualCanonicalTarget` ou retiré
- Tests Jest `r2-eligibility.spec.ts` : `suppressed when below threshold + sibling` → `review when below threshold`
- Cross-ref code : ADR-066 + ADR-067 amendement

## Mémoires canon monorepo mises à jour

- **Nouvelle** : `feedback_no_auto_page_suppression_ever` (STRICT anti-régression). SUPERSEDES auto path des doctrines précédentes.
- **Superseded** : `feedback_seo_suppressed_canonical_decision` (marqué superseded_by avec banner contextuel)
- **Amended** : `feedback_canonical_chain_prevention` (anti-chain reste valable pour SUPPRESSED manuels uniquement)
- **Amended** : `feedback_seo_catalog_signature_before_text_diversity` (catalog overlap > 0.92 → REVIEW + enrichissement, JAMAIS canonical auto)
- MEMORY.md `Anti-régressions strictes` : ajout `feedback_no_auto_page_suppression_ever` au top

## Verification locale

```
$ /tmp/opa test policies/seo-content/
PASS: 69/69
```

- 22 h1-write tests (régression PR-V intacte)
- 28 r2-content-write tests (4 nouveaux ADR-067 + autres amendés)
- 15 r2-cluster-health tests (intacts, invariants cluster restent valables)
- 4 new ADR-067 specific tests : pipeline_suppressed deny, human_curated_suppressed allow + invariants

## Impacts cross-canon

- **ADR-066** : amended (matrice 5 → 4 + SUPPRESSED manual-only)
- **ADR-058 (Repository Control Plane)** : pas d'impact ownership (R2 v2 reste D3 SEO)
- **MOC-Decisions** : ADR-067 indexé sous "amendments" à ADR-066
- **MOC-AuditTrail** : ligne 2026-05-15 ajoutée

## Hors scope post-acceptance

- Migration des SUPPRESSED historiques : aucun n'existe (PR 1 #543 mergée 2026-05-15T17:39, zéro page R2 v2 produite)
- Frontend canonical rendering pour SUPPRESSED manuel : conservé tel quel pour PR 2 V1.5
- Comportement R8 ou autres rôles : ADR-067 scope strict R2. R8 garde doctrine propre (mais `feedback_no_auto_page_suppression_ever` flag risque transverse pour autres rôles).
- PR 3 V2 enrichissement LLM auto pour REVIEW à signal faible : non scopé, à discuter quand volume REVIEW empirique mesurable

## Self-review verdict: APPROVE

ADR exhaustif (calibration empirique citée, justification métier détaillée, conséquences concrètes mappées). Doctrine pivot pré-production (zéro impact migration). Rego policies + tests cohérents (69/69 PASS). Mémoires monorepo alignées (1 nouvelle, 3 amendées). Cross-ref ADR-066 préservé via `amends`. Prêt pour merge.
