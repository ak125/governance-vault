---
id: ADR-012
title: AI-COS VPS Architecture & Agent Placement
status: accepted
date: 2026-03-08
version: 1.0.0
decision_makers: [CEO, CTO]
---

# ADR-012 : AI-COS VPS Architecture & Agent Placement

## Status

**ACCEPTED** — 2026-03-08

## Context

AutoMecanik evolue vers un modele AI-driven company. Le systeme actuel repose sur 2 VPS (DEV + PROD). Un 3e VPS (AI-COS) est necessaire pour centraliser le monitoring, l'observabilite et le pilotage des agents.

Contraintes :
- DEV est le seul point d'ecriture en DB (via MCP Supabase)
- PROD n'est accessible que via git push → GitHub Actions → Docker
- Le VPS AI-COS doit etre en **lecture seule** (zero ecriture DB)

## Decision

### Architecture 3 Zones

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│       DEV VPS       │     │      PROD VPS        │     │    AI-COS VPS       │
│   46.224.118.55     │     │    49.12.233.2       │     │    (nouveau)        │
│                     │     │                      │     │                     │
│ Claude Code IDE     │     │ NestJS + Remix       │     │ Dashboard Remix     │
│ MCP Supabase (R/W)  │     │ Redis (sessions)     │     │ (READ-ONLY)        │
│ Agent execution     │     │ BullMQ workers       │     │                     │
│ Skills interactifs  │     │ Paybox/SystemPay     │     │ Supabase read       │
│ Git push → PROD     │     │ Caddy reverse proxy  │     │ (service_role)     │
│                     │     │                      │     │                     │
│ ECRIT dans DB  ─────┼─────┼──────────────────────┼─────► Lit la DB          │
│                     │     │ Docker logs ─────────┼─────► Lit les logs SSH   │
│ git push main ──────┼─────► GitHub Actions       │     │ Health polling      │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
```

### Agent Placement Rules

| Zone | Role | Acces DB | Agents |
|------|------|----------|--------|
| **DEV** (`local`) | Execution agents + ecriture DB | R/W via MCP | 12 agent prompts SEO, 14 skills |
| **PROD** (`principal_vps`) | Workers backend | R/W via service_role | 8 workers BullMQ, crons |
| **AI-COS** (`aicos_vps`) | Observatoire read-only | READ ONLY | Dashboard, Health Poller, Log Reader |

### AI-COS VPS Specifications

- **Specs** : 2 vCPU / 4 GB RAM
- **Stack** : Docker (Remix Dashboard + Caddy HTTPS)
- **Data sources** : Supabase (service_role read) + PROD Docker logs (SSH) + PROD /health (HTTP)
- **Zero ecriture** : aucun INSERT/UPDATE/DELETE autorise

### Airlock Integration

| Phase | Mode | Comportement |
|-------|------|-------------|
| Phase 1-3 | `observe` | Ecritures agents DEV loggees dans `__airlock_bundles` |
| Phase 4 | `review` | Bundles visibles dans dashboard AI-COS pour review post-hoc |
| Phase 5 | `enforce` | Ecritures agents bloquees jusqu'a approbation dans dashboard |

## Consequences

- Nouvelle zone `aicos_vps` dans ADR-008 (3 zones → 4 zones)
- REG-001 v3.0 avec zone `aicos_vps`
- SSH key dediee pour PROD logs (user `readonly`)
- Tables nouvelles : `__agent_runs`, `__agent_metrics`, `__airlock_bundles`
- Les agents SEO restent sur DEV (pas de migration vers AI-COS)

## Related ADRs

- ADR-002: Zero-Trust Agents
- ADR-005: Airlock Observe Mode
- ADR-008: Agent Placement Rules (3 Zones → 4 Zones)
- ADR-009: Phase 1 Agent Activation
- ADR-011: OpenClaw to Claude API Replacement

---

_Decision Date: 2026-03-08_
_Authors: CEO, CTO, Claude (Governance Analyst)_
