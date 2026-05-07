---
type: moc
status: canon
updated: 2026-05-07
---

# MOC: Agents

Index canonique de tous les agents du monorepo AutoMecanik. Les agents sont stockes dans `ledger/agents/<categorie>/` et indexes par un `INDEX-agents-<categorie>.md` par categorie.

> **Source de verite** : [[REG-001-agents]] (catalogue structure avec metadata, contient le compte canonique `total_agents` et les compteurs par verdict). Ce MOC n'embarque aucun nombre absolu — ils vivraient en duplication et deriveraient.

---

## Categories

Liste des index par categorie. Pour les compteurs et metadata par agent : [[REG-001-agents]].

- [[INDEX-agents-ai-cos]] — C-Suite IA (CEO/CFO/CMO/CPO/CTO), leads SEO/RAG/Data, QA, prompts R1/R3/R4/R6
- [[INDEX-agents-backend]] — Services NestJS (SEO, monitoring, cache, sitemap delta)
- [[INDEX-agents-python]] — Analyzers A1-A12, Fixproof F0/F1/F15 (read-only audits)
- [[INDEX-agents-skills]] — Modules Claude Agent SDK reutilisables (UI-OS, governance-vault-ops, etc.)
- [[INDEX-agents-bmad]] — Business Model Agent Development (analyst, architect, dev, pm, sm)
- [[INDEX-agents-github-actions]] — CI/CD automation (deploy, perf-gates, spec-validation)
- [[INDEX-agents-lettered]] — Series A/B/F/G/M (condensed agents)
- [[INDEX-agents-mcp]] — Model Context Protocol servers (Supabase, shadcn)
- [[INDEX-agents-scripts]] — Scripts orchestration (UI audit, governance)
- [[INDEX-agents-bundles]] — Bundles historiques wrapped (legacy)
- [[INDEX-agents-registry]] — Catalog canonique REG-001-agents

---

## Regles de Placement (Zones)

Chaque agent est affecte a une zone. Voir [[ADR-008-agent-placement-rules]] et [[ADR-012-aicos-vps-architecture]].

| Zone | Role | Exemples |
|------|------|----------|
| `local` | Dev/CI sandbox | BMAD, Skills, MCP servers, scripts |
| `principal_vps` | Prod controllee | Backend services, AI-COS executors |
| `external` | Analyzers read-only | Python analyzers (A1-A12), GitHub Actions |
| `aicos_vps` | Observatoire | AI-COS leads (SEO, Data, RAG), C-Suite |
| `production` | **INTERDIT** | Aucun agent (voir [[ADR-008-agent-placement-rules]]) |

---

## Verdicts d'Approbation (Phase 1 Activation)

Voir [[ADR-009-agents-phase1-activation]] pour le framework. Compteurs exacts par verdict (APPROVED / APPROVED_WITH_CONDITIONS / NOT_APPROVED / CONCEPTUAL) : voir [[REG-001-agents]] frontmatter et section "Quick Stats".

---

## Decisions Liees

- [[ADR-007-location-independence]] - Regle Maitre
- [[ADR-008-agent-placement-rules]] - 3 zones (etendu a 4)
- [[ADR-009-agents-phase1-activation]] - Framework d'activation
- [[ADR-011-openclaw-claude-api-replacement]] - Remplacement OpenClaw
- [[ADR-012-aicos-vps-architecture]] - AI-COS VPS (4e zone)
- [[ADR-013-agent-lifecycle-governance]] - Cycle de vie

## Regles

- [[rules-ai-cos]] - AI1-AI10 (regles agents IA)

---

## Voir aussi

- [[MOC-Decisions]] - ADR canoniques
- [[MOC-Rules]] - Taxonomie T/G/AI/V
- [[MOC-Compliance]] - Evidence-packs associes
- [[MOC-AuditTrail]] - Audit-trail bundles et RPC
