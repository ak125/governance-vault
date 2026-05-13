---
date: 2026-05-13
type: audit-trail
related: [ADR-031, ADR-015, ADR-022, ADR-026, ADR-027, ADR-029, ADR-058, ADR-059, ADR-060, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-13 — ADR-031 Four-Layer Content Architecture (proposed → accepted)

## What

ADR-031 « Four-Layer Content Architecture — Raw / Wiki / Exports / Consumers (Unified Flow All R0-R8) » passe de **status: proposed** à **status: accepted**. Décision @fafa, `decision_date: 2026-05-13`.

## Why

ADR-031 a été ouverte en `proposed` le 2026-05-28 (commit `5d76b07` + amendements D14-D23 jusqu'au 2026-04-28). Elle codifie le flux canonique de contenu sur 4 couches (`automecanik-raw` → `automecanik-wiki` → exports → consommateurs) avec migration physique planifiée des 313 MB de contenu brut et supersedes ADR-022 (R8 RAG Control Plane) + ADR-026 (Content Repository Separation).

L'audit architectural du 2026-05-13 a confirmé :

- 3 incohérences originelles (carve-out diagnostic/faq/policies, R8 cas spécial ADR-022, repo `automecanik-raw` vide) sont résolues par la décision ADR-031
- Phases A-J du plan d'exécution complétées dans leurs grandes lignes (skeleton Phase F shippée 2026-04-28 via PR #200, Phase B.3 canon AEC fermée)
- Conventions D14-D23 stables (D23 pluriel adopté 2026-04-28 reflète réalité repo wiki)
- Décisions downstream (ADR-058 Repository Control Plane, ADR-059 SEO Runtime Projection, ADR-060 Doctrine repository roles) référencent ADR-031 comme assise canonique

Le maintien en `proposed` empêchait formellement la mise en LIVE du canon (`feedback_canon_rule_live_iff_adr_accepted.md`) — toute nouvelle contribution pouvait argumenter contre. L'acceptation lève ce blocage.

## How

Acceptation via PR vault `feat/adr-031-ratification` :

1. `ledger/decisions/adr/ADR-031-four-layer-content-architecture.md` frontmatter :
   - `status: proposed` → `status: accepted`
   - `decision_date: null` → `decision_date: 2026-05-13`
2. `ops/moc/MOC-Decisions.md` ligne ADR-031 : `Proposed` → `Accepted` (section « ADR Actifs » + section auto-générée resynchronisée)
3. Ce fichier audit-trail créé (G1/G2 traceability, conforme `feedback_auto_vault_audit_trail_on_adr.md`)

**Aucun changement de body** — ADR-031 reste pur sur le topic 4-layer content. La doctrine inter-repos (qui décide / valide / exécute / consomme) est traitée séparément par ADR-060 (concern orthogonal, créée en parallèle dans une PR vault distincte).

## What changes downstream

Avec `ADR-031.status == "accepted"` :

- **Canon LIVE** : le flux raw → wiki → exports → consumers devient canon courant. Toute violation future est régression.
- **D14-D23** : invariants stables (supersede TOTAL ADR-022/026, mapping D15bis, conv. pluriel D23, garde-fou sync-from-wiki D20, etc.) entrent en canon ratifié.
- **Cross-references** : ADR-058 (Control Plane), ADR-059 (SEO Runtime Projection), ADR-060 (doctrine repository roles) référencent désormais un canon LIVE.
- **Plan d'exécution Phase B-J** : les phases restantes (notamment Phase F complète, Phase G support, Phase H diagnostic) opèrent sous canon LIVE.

## Refs

- [ADR-031](../decisions/adr/ADR-031-four-layer-content-architecture.md) (accepted 2026-05-13)
- [ADR-060](../decisions/adr/ADR-060-repository-roles-doctrine.md) (doctrine repository roles, PR vault séparée)
- [ADR-058](../decisions/adr/ADR-058-repository-control-plane.md) (Control Plane monorepo, complémentaire)
- [ADR-059](../decisions/adr/ADR-059-seo-runtime-projection.md) (SEO Runtime Projection, supplements ADR-031)
- Brainstorm session : `/home/deploy/.claude/plans/verifier-la-meilleure-delightful-kurzweil.md`
