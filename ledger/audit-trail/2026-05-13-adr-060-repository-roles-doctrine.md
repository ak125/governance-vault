---
date: 2026-05-13
type: audit-trail
related: [ADR-060, ADR-015, ADR-031, ADR-036, ADR-058, ADR-059, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-13 — ADR-060 Doctrine des rôles repositories (création accepted atomique)

## What

Création de **ADR-060 « Doctrine des rôles repositories — 5 acteurs canon (vault / wiki / raw / monorepo / rag) »** directement en `status: accepted` (decision_date 2026-05-13, signée @fafa), conformément au pattern atomique inauguré par [[ADR-059-seo-runtime-projection]] le même jour (17:14 proposed → 17:27 accepted).

L'ADR codifie :

- **Doctrine 5-layer** : vault *décide*, wiki *valide*, raw *collecte*, monorepo *exécute*, rag *indexe et consomme (jamais source)*.
- **Formule canonique grepable** : « vault décide, wiki valide, raw collecte, monorepo exécute, rag indexe et consomme. »
- **5 invariants** : écriture métier wiki = PR humaine ; écriture canon vault = PR signée G3 ; monorepo n'écrit jamais dans wiki/raw/vault ; rag mirror jamais source ; **aucune section opérationnelle dans le vault** (`growth/`, `marketing/`, `seo/`, `content/`, `infra/` interdits).
- **Restriction `ledger/knowledge/`** : autorisé uniquement pour audit-trail/handoff/connaissance gouvernée, jamais contenu métier opérationnel.
- **Articulation avec ADR-015 / ADR-031 / ADR-036 / ADR-058 / ADR-059** : orthogonale à la 4-layer content flow (ADR-031) et à la manifestation Control Plane monorepo (ADR-058).

## Why

L'écosystème AutoMecanik s'appuie sur 5 repositories canoniques (`governance-vault`, `automecanik-wiki`, `automecanik-raw`, `nestjs-remix-monorepo`, `automecanik-rag`). Leurs responsabilités étaient **canon de fait** depuis ADR-015 + ADR-031, mais **jamais écrites littéralement** comme doctrine inter-repos. Au 2026-05-13, `grep -rE "vault décide|monorepo exécute" ledger/decisions/adr/` retournait 0 hit.

Conséquences observées :
1. Risque récurrent de créer `governance-vault/growth/`, `marketing/`, `seo/`, `content/`, `infra/`
2. Confusion sur l'écriture (qui peut écrire où, sous quelle signature)
3. Rag parfois traité comme source secondaire alors qu'il est strictement mirror (D22 d'ADR-031)
4. Memory rule `feedback_canon_rule_live_iff_adr_accepted` : canon de fait fragile sans ratification

Le brainstorm initial proposait un **amendement ADR-031** intégrant la doctrine 5-layer + Repository Control Plane. Deux problèmes ont émergé pendant la session :

1. **§ 1B Repository Control Plane dupliquait massivement ADR-058** (PR-A #257 mergée 17:02 même jour) — découvert via grep `MOC-*.md`. Course correction : abandon de cette section au profit de cross-références.
2. **§ 1A Doctrine 5-layer mélangeait deux concerns dans ADR-031** : ADR-031 traite du flux de contenu (matériau), pas de la répartition d'autorité inter-repos (qui). Mélanger violait le pattern « une ADR = une décision » confirmé par ADR-058 et ADR-059 créées le même jour avec un concern unique chacune.

**Décision finale** : extraire la doctrine 5-layer dans ADR-060 séparé (concern pur). ADR-031 reste pure sur son topic (4-layer content), ratifiée flip-only en PR vault parallèle (#262).

## How

Création via PR vault `feat/adr-060-repository-roles-doctrine` :

1. `ledger/decisions/adr/ADR-060-repository-roles-doctrine.md` : créé directement en `status: accepted`, `decision_date: 2026-05-13`. Frontmatter `related_adr: [ADR-012, ADR-013, ADR-015, ADR-031, ADR-036, ADR-058, ADR-059]`.
2. `ops/moc/MOC-Decisions.md` : ligne ADR-060 ajoutée en `Accepted` (section « ADR Actifs » + section auto-générée).
3. Ce fichier audit-trail créé (G1/G2 traceability).
4. `ops/moc/MOC-AuditTrail.md` : entrée ajoutée pour audit-trail file linkage.

**Aucune modification** des autres ADRs (ADR-031, ADR-036, ADR-058, ADR-059) ni des autres repositories (monorepo, wiki, raw, rag, workspaces).

## What changes downstream

Avec `ADR-060.status == "accepted"` :

- **Canon LIVE** : la doctrine repository roles devient canon courant. Toute violation future (création `governance-vault/growth/`, briefs marketing en `.md` flottants wiki, monorepo écrivant dans wiki/raw/vault, etc.) est régression.
- **Sous-projets downstream cohérents** :
  - **ADR-061 (futur)** : workspace governance — frontière/lifecycle/ownership `workspaces/*`. ADR-060 invariant 5 mentionne déjà workspaces ; ADR-061 précisera.
  - **CI invariants hardening** : futur lint script « pas de section opérationnelle dans vault » dérivé de ADR-060 invariant 5.
  - **ADR-058 cascade PR-B → PR-H** : déjà en cours, ADR-060 fournit cadre conceptuel pour les agents impliqués.

Aucune modification de runtime, hooks, ou code requise par cette ratification — la doctrine est déclarative.

## Refs

- [ADR-060](../decisions/adr/ADR-060-repository-roles-doctrine.md) (accepted 2026-05-13)
- [ADR-031](../decisions/adr/ADR-031-four-layer-content-architecture.md) (4-layer content, ratifiée même session PR vault #262)
- [ADR-036](../decisions/adr/ADR-036-marketing-operating-layer.md) (marketing operating layer, ratifiée même session PR vault #263)
- [ADR-058](../decisions/adr/ADR-058-repository-control-plane.md) (Repository Control Plane monorepo, complémentaire orthogonal)
- [ADR-059](../decisions/adr/ADR-059-seo-runtime-projection.md) (SEO Runtime Projection, supplements ADR-031)
- [ADR-015](../decisions/adr/ADR-015-vault-single-source-of-truth.md) (vault SoT canonique)
- Brainstorm session : `/home/deploy/.claude/plans/verifier-la-meilleure-delightful-kurzweil.md` (approche 3 PRs disjointes, 1 ADR = 1 décision)
- Memory : `feedback_canon_rule_live_iff_adr_accepted`, `feedback_no_bricolage_align_existing_contract`, `feedback_verify_existing_first`, `cross-repo-and-governance-discipline`
