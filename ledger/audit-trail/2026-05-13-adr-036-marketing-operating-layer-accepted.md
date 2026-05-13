---
date: 2026-05-13
type: audit-trail
related: [ADR-036, ADR-013, ADR-015, ADR-025, ADR-031, ADR-060, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-13 — ADR-036 Marketing Operating Layer (proposed → accepted)

## What

ADR-036 « Marketing Operating Layer — 3 agents G1 (LEAD/LOCAL/RETENTION) + extension OperatingMatrixService + business_unit séparé ECOMMERCE/LOCAL/HYBRID » passe de **status: proposed** à **status: accepted**. Décision @fafa, `decision_date: 2026-05-13`.

## Why

ADR-036 a été ouverte en `proposed` le 2026-04-30 (cf. brainstorm initial). Elle codifie la couche marketing operating au-dessus du module backend NestJS `marketing/` existant : 3 agents G1 spécialisés (LEAD/LOCAL/RETENTION), séparation `business_unit` ECOMMERCE/LOCAL/HYBRID en DB structurée, et 6 services backend mappés (multi-channel-copywriter, weekly-plan-generator, brand-compliance-gate, utm-builder, marketing-data, publish-queue).

L'audit architectural du 2026-05-13 confirme 5/5 claims VRAI dans le body :

1. **Pas de duplication du module marketing backend** ✓ (ligne 46, 211, 241 — backend `marketing/services/` réutilise 9 services existants)
2. **Pas de briefs `.md` flottants dans le wiki** ✓ (ligne 52, 240 — briefs en table DB `__marketing_brief`)
3. **`business_unit` ENUM ECOMMERCE/LOCAL/HYBRID** ✓ (ligne 97, CHECK SQL contraignant + Zod refinement)
4. **Backend NestJS = moteur unique d'exécution** ✓ (ligne 76 — agents consomment, ne réécrivent pas)
5. **Implémentation backend en place** ✓ (`backend/src/modules/marketing/services/` contient 11 services, `marketing-brief.dto.ts` enum `MarketingBusinessUnit`)

Le canon brand voice (`rules-marketing-voice.md` status `canon`) et le workspace `workspaces/marketing/` sont également stables et opérationnels.

Le maintien en `proposed` empêchait formellement la mise en LIVE du canon (`feedback_canon_rule_live_iff_adr_accepted`) — l'acceptation lève ce blocage.

## How

Acceptation via PR vault `feat/adr-036-ratification` :

1. `ledger/decisions/adr/ADR-036-marketing-operating-layer.md` frontmatter :
   - `status: proposed` → `status: accepted`
   - `decision_date: null` → `decision_date: 2026-05-13`
2. `ops/moc/MOC-Decisions.md` ligne ADR-036 : `Proposed` → `Accepted` (section « ADR Actifs » + section auto-générée)
3. Ce fichier audit-trail créé (G1/G2 traceability, conforme `feedback_auto_vault_audit_trail_on_adr.md`)

**Aucun changement de body, aucun changement runtime, aucun changement règles, aucun changement workspaces** — purement gouvernance. Le body ADR-036 est complet (audit 5/5 claims VRAI).

## What changes downstream

Avec `ADR-036.status == "accepted"` :

- **Canon LIVE** : la couche marketing operating layer devient canon courant. Toute violation future (duplication backend marketing, briefs `.md` flottants, etc.) est régression.
- **Cross-references** : ADR-057 (marketingskills adoption pattern) et ADR-060 (doctrine repository roles) référencent désormais ADR-036 comme canon LIVE.
- **Workspace marketing** : continue de tourner sous canon ratifié (`workspaces/marketing/`, 3 agents G1).
- **Rule `rules-marketing-voice.md` status `canon`** : reste alignée avec ADR-036 LIVE.

## Refs

- [ADR-036](../decisions/adr/ADR-036-marketing-operating-layer.md) (accepted 2026-05-13)
- [ADR-060](../decisions/adr/ADR-060-repository-roles-doctrine.md) (doctrine repository roles, PR vault séparée)
- [ADR-031](../decisions/adr/ADR-031-four-layer-content-architecture.md) (4-layer content, ratifiée même session PR vault #262)
- Brainstorm session : `/home/deploy/.claude/plans/verifier-la-meilleure-delightful-kurzweil.md`
