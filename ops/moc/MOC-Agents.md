---
type: moc
status: canon
updated: 2026-04-17
total_agents: 119
---

# MOC: Agents

Index canonique de tous les agents du monorepo AutoMecanik. Les agents sont stockes dans `ledger/agents/<categorie>/` et indexes par un `INDEX-agents-<categorie>.md` par categorie.

> **Source de verite** : `ledger/agents/registry/REG-001-agents.md` (catalogue structure avec metadata).

---

## Categories

| Categorie | # | Index |
|-----------|---|-------|
| AI-COS | 44 | [[INDEX-agents-ai-cos]] |
| Backend | 19 | [[INDEX-agents-backend]] |
| Python | 15 | [[INDEX-agents-python]] |
| Skills | 14 | [[INDEX-agents-skills]] |
| BMAD | 10 | [[INDEX-agents-bmad]] |
| GitHub Actions | 5 | [[INDEX-agents-github-actions]] |
| Lettered | 5 | [[INDEX-agents-lettered]] |
| MCP | 3 | [[INDEX-agents-mcp]] |
| Scripts | 2 | [[INDEX-agents-scripts]] |
| Bundles | 1 | [[INDEX-agents-bundles]] |
| Registry | 1 | [[INDEX-agents-registry]] |
| **TOTAL** | **119** | - |

---

## Descriptions par Categorie

- **AI-COS** - C-Suite IA (CEO/CFO/CMO/CPO/CTO), leads SEO/RAG/Data, QA, prompts R1/R3/R4/R6
- **Backend** - Services NestJS (SEO, monitoring, cache, sitemap delta)
- **Python** - Analyzers A1-A12, Fixproof F0/F1/F15 (read-only audits)
- **Skills** - Modules Claude Agent SDK reutilisables (UI-OS, governance-vault-ops, etc.)
- **BMAD** - Business Model Agent Development (analyst, architect, dev, pm, sm)
- **GitHub Actions** - CI/CD automation (deploy, perf-gates, spec-validation)
- **Lettered** - Series A/B/F/G/M (condensed agents)
- **MCP** - Model Context Protocol servers (Supabase, shadcn)
- **Scripts** - Scripts orchestration (UI audit, governance)
- **Bundles** - Bundles historiques wrapped (legacy)
- **Registry** - Catalog canonique REG-001-agents

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

Voir [[ADR-009-agents-phase1-activation]] pour le framework.

| Verdict | # | Signification |
|---------|---|---------------|
| APPROVED | ~54 | Execution autorisee (observability + enforce) |
| APPROVED_WITH_CONDITIONS | ~15 | Execution avec garde-fous supplementaires |
| NOT_APPROVED | ~46 | Specifie mais pas active (pending review) |

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

---

_Derniere mise a jour: 2026-04-17_
