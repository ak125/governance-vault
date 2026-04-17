---
id: ADR-011
title: Remplacement OpenClaw par Claude API
status: accepted
version: 1.0.0
date: 2026-03-07
decision_makers:
  - Architecture Team
  - Governance Team
supersedes_partially:
  - ADR-002 v1.0 (sections OpenClaw uniquement)
  - ADR-009 v1.0 (sections OpenClaw uniquement)
impacts:
  - REG-001 (15 fiches APPROVED_WITH_CONDITIONS)
  - ADR-002
  - ADR-009
references:
  - ADR-002 v2.0
  - ADR-009 v2.0
  - REG-001 v1.4.1
---

# ADR-011: Remplacement OpenClaw par Claude API

> Ce document acte officiellement la suppression d'OpenClaw et son remplacement par Claude API.

---

## 1. Contexte et motivation

OpenClaw etait le moteur d'execution et de generation de bundles pour les agents AutoMecanik. Il generait les bundles signes soumis a l'Airlock via agent-submissions.

**Raisons de la suppression :**

- **Complexite de maintenance** : OpenClaw necessitait une infrastructure dediee et des mises a jour independantes
- **Redondance avec Claude API** : les capacites de generation et d'orchestration sont directement disponibles via Claude API sans couche intermediaire
- **Cout d'infrastructure** : un moteur dedie represente une charge operationnelle non justifiee au stade actuel
- **Simplicite architecturale** : Claude API + agent-submissions + Airlock couvre le meme perimetre avec moins de composants

---

## 2. Decision

**OpenClaw est supprime.** Claude API devient le moteur officiel d'orchestration et de generation de bundles pour le systeme multi-agents AutoMecanik.

### 2.1 Architecture avant (OpenClaw)

```
OpenClaw → bundle HMAC-SHA256 → agent-submissions → Airlock → PR → merge
```

### 2.2 Architecture apres (Claude API)

```
Claude API / Cowork → bundle HMAC-SHA256 → agent-submissions → Airlock → PR → merge
```

Le pipeline agent-submissions, l'Airlock et la signature HMAC-SHA256 sont inchanges. Seul le generateur de bundles change.

### 2.3 Deux modes d'utilisation de Claude

| Mode | Interface | Usage | Zone | Autonomie |
|------|-----------|-------|------|-----------|
| Automatique | Claude API (VPS AI-COS) | Agents monitoring, SEO, data — taches recurrentes | principal_vps | Haute — sous Airlock |
| Manuel | Claude Desktop + Cowork | Specs, ADR, contenu, revue — taches cognitives | local | Humain dans la boucle |

---

## 3. Impact sur les composants existants

### 3.1 REG-001 — Agent Registry

Aucun changement de structure. Les 15 agents APPROVED_WITH_CONDITIONS doivent avoir leur fiche mise a jour :

- Remplacer `execution_engine: OpenClaw` par `execution_engine: Claude API`
- Valider la section Placement Decision pour chaque fiche
- Conserver toutes les autres regles (zone, trust, output, verdict)

**Agents concernes :**

| Agent ID | Zone | Action requise |
|----------|------|---------------|
| agent.seo.vlevel | principal_vps | Mettre a jour fiche — Claude API |
| agent.seo.sitemap | principal_vps | Mettre a jour fiche — Claude API |
| agent.seo.canonical | principal_vps | Mettre a jour fiche — Claude API |
| agent.seo.content | principal_vps | Mettre a jour fiche — Claude API |
| agent.data.cleanup | principal_vps | Mettre a jour fiche — Claude API |
| agent.data.validator | principal_vps | Mettre a jour fiche — Claude API |
| agent.data.backup | principal_vps | Mettre a jour fiche — Claude API |
| agent.rag.indexer | principal_vps | Mettre a jour fiche — Claude API |
| agent.rag.validator | principal_vps | Mettre a jour fiche — Claude API |
| agent.rag.retriever | principal_vps | Mettre a jour fiche — Claude API |
| agent.infra.monitor | principal_vps | Mettre a jour fiche — Claude API |
| agent.infra.logs | principal_vps | Mettre a jour fiche — Claude API |
| f0_autoimport | external | Mettre a jour fiche — Claude API |
| f1_dead_code_surgeon | external | Mettre a jour fiche — Claude API |
| dev (BMAD) | local | Mettre a jour fiche — Cowork/Claude Desktop |

### 3.2 ADR impactes

| ADR | Action | Status |
|-----|--------|--------|
| ADR-002 v1.0 | Revise → v2.0 (ce package) | DONE |
| ADR-009 v1.0 | Revise → v2.0 (ce package) | DONE |
| ADR-005 (Airlock Observe) | Revise → v1.1 (commit 2eed215) | DONE |
| ADR-003 (RPC Governance) | Verifier — RpcGateService reste valide | A verifier |
| ADR-007 (Location Independence) | Inchange | OK |
| ADR-008 (Agent Placement Rules) | Inchange | OK |

### 3.3 Infrastructure

| Composant | Status | Notes |
|-----------|--------|-------|
| OpenClaw | SUPPRIME | Ne pas reinstaller |
| agent-submissions | INCHANGE | Pipeline bundle → Airlock maintenu |
| Airlock | INCHANGE | Mode enforce maintenu en production |
| HMAC-SHA256 signing | INCHANGE | Signature bundles maintenue |
| GitHub PR automation | INCHANGE | Workflow CI/CD maintenu |
| RpcGateService | INCHANGE | `backend/src/security/rpc-gate/` maintenu |
| VPS AI-COS (nouveau) | PLANIFIE | Hebergera Claude API + orchestrateur ai-cos-system |

---

## 4. Consequences

### Positives

- Reduction du nombre de composants a maintenir
- Claude API couvre generation, validation ET orchestration en un seul service
- Cowork permet la gouvernance locale sans infrastructure supplementaire immediate
- Continuite : le pipeline agent-submissions + Airlock reste intact

### Negatives

- Dependance accrue a l'API Anthropic — cout variable selon usage
- 15 fiches agents necessitent une mise a jour manuelle
- ADR-005 doit etre revise

### Risques identifies

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|------------|
| Rate limit API Anthropic | Moyenne | Eleve | Redis cache + retry logic dans ai-cos-system |
| Cout API impreductible | Faible | Moyen | Budget cap par agent + monitoring tokens |
| Fiche agent obsolete active | Haute | Moyen | Sprint de mise a jour immediat |

---

## 5. Plan de migration

### Phase A — Immediat (Sprint actuel)

1. Archiver toute documentation OpenClaw dans `governance-vault/06-knowledge/`
2. Mettre a jour les 15 fiches APPROVED_WITH_CONDITIONS
3. Reviser ADR-005
4. Valider pipeline agent-submissions avec Claude API en mode observe

### Phase B — Sprint suivant

1. Passer Airlock en mode enforce avec Claude API
2. Monitorer 14 jours → critere Phase 2 (ADR-009)
3. Configurer VPS AI-COS dedie (ai-cos-system)

### Phase C — Phase 2 (futur ADR)

1. Activer agents AI-COS L1/L2 (CEO.ia, CTO.ia...) apres nouvel ADR
2. Activer Lettered Series selon priorisation

---

ADR-011 v1.0 · AutoMecanik Governance Vault · 2026-03-07 · Decision actee par Architecture Team
