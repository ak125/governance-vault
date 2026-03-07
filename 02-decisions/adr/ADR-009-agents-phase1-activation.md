---
id: ADR-009
title: Phase 1 Agent Activation Framework
status: accepted-revised
version: 2.0.0
date_original: 2026-02-03
date_revision: 2026-03-07
decision_makers:
  - Architecture
  - Governance
supersedes: ADR-009 v1.0 (OpenClaw era)
references:
  - ADR-002 v2.0
  - ADR-011
  - REG-001 v1.4.1
---

# ADR-009: Phase 1 Agent Activation Framework

## Changelog

| Version | Date | Changement |
|---------|------|------------|
| 1.0 | 2026-02-03 | Creation — OpenClaw comme moteur d'activation |
| 2.0 | 2026-03-07 | Claude API remplace OpenClaw. Zones et criteres mis a jour. |

---

## 1. Contexte

Le systeme dispose de :

- **REG-001 v1.4.1** — 140 agents recenses (54 APPROVED, 15 APPROVED_WITH_CONDITIONS, 46 NOT_APPROVED, 25 Lettered Series planned)
- **ADR-002 v2.0** — Zero-Trust avec Claude API comme nouveau moteur
- **agent-submissions** — pipeline de soumission bundles signes HMAC-SHA256
- **governance-vault** — ledger d'audit avec 45 commits, regles R1-R11

**Changement de contexte (v2.0) :**

- OpenClaw supprime — Claude API devient l'orchestrateur principal
- Le cadre d'activation Phase 1 est maintenu mais le moteur d'execution change
- Les 15 agents APPROVED_WITH_CONDITIONS sont le premier perimetre d'activation

---

## 2. Decision

### 2.1 Perimetre Phase 1 — Criteres d'eligibilite

Seuls les agents satisfaisant TOUS les criteres suivants sont activables :

| Critere | Valeur requise | Notes |
|---------|---------------|-------|
| Verdict REG-001 | APPROVED ou APPROVED_WITH_CONDITIONS | NOT_APPROVED = bloque sans nouvel ADR |
| Output type | report, bundle | Pas de deploy direct |
| Acces ecriture direct | INTERDIT | Ni Git write, ni vault write, ni prod deploy |
| Fiche agent | Section Placement Decision complete | Manquante = non activable |
| Moteur d'execution | Claude API (principal_vps) ou Cowork (local) | OpenClaw = reference obsolete |

### 2.2 Zones autorisees par type d'agent

| Type d'agent | Zone autorisee | Moteur | Status Phase 1 |
|-------------|---------------|--------|---------------|
| Analysis / Audit (a1-a12) | external | Claude API | ACTIF |
| SEO Services | principal_vps | Claude API | ACTIF |
| Monitoring / Observability | principal_vps | Claude API | ACTIF |
| Bundle Producers (f0, f1) | external | Claude API | ACTIF avec Airlock |
| BMAD Agents | local | Cowork / Claude Desktop | ACTIF |
| MCP Agents (supabase, shadcn) | local | Cowork / Claude Desktop | ACTIF |
| GitHub Actions Agents | external | GitHub CI | ACTIF |
| AI-COS L1 (CEO/CTO/CPO...) | — | — | INTERDIT Phase 1 |
| AI-COS L2 Leads | — | — | INTERDIT Phase 1 |
| PROD Runtime direct | — | — | INTERDIT Phase 1 |

### 2.3 Explicitement interdit en Phase 1

- **Agents AI-COS Executive Level 1** : agent.ceo.ia, agent.cto.ia, agent.cpo.ia, agent.cmo.ia, agent.cfo.ia
- **Agents AI-COS Leads Level 2** : agent.seo.lead, agent.data.lead, agent.rag.lead, agent.aicos.architect, agent.aicos.governance
- Tout agent avec `write_target = monorepo` ou `write_target = governance-vault`
- Tout agent avec `output = deploy` ou autonomous decision authority
- Les 34 agents Lettered Series (G, F, M, A, B) — planifies, necessitent ADR dedie

---

## 3. Regles d'enforcement

Toute activation d'agent DOIT :

1. Etre listee dans REG-001 avec verdict APPROVED ou APPROVED_WITH_CONDITIONS
2. Avoir une fiche agent approuvee avec section Placement Decision
3. Respecter les regles de zone (ADR-008)
4. Passer l'Airlock en mode enforce (si APPROVED_WITH_CONDITIONS)
5. Referencer Claude API comme moteur (plus OpenClaw)

**Violations** → rejet automatique + entree audit-trail + desactivation agent.

---

## 4. Criteres de sortie Phase 1 → Phase 2

La transition vers Phase 2 necessite :

1. 14 jours d'operation stable avec Claude API comme moteur
2. Zero violation Airlock en mode enforce
3. Mise a jour de toutes les fiches APPROVED_WITH_CONDITIONS (reference OpenClaw supprimee)
4. Revue des bundles rejetes
5. Nouvel ADR explicite autorisant Phase 2 (activation AI-COS L1/L2)

---

## 5. Actions immediates requises

| Action | Priorite | Responsable | Deadline |
|--------|----------|-------------|----------|
| Mettre a jour 15 fiches APPROVED_WITH_CONDITIONS | HAUTE | Governance Team | Sprint actuel |
| Supprimer toutes references OpenClaw des fiches | HAUTE | Governance Team | Sprint actuel |
| Valider pipeline agent-submissions avec Claude API | HAUTE | Architecture Team | Sprint actuel |
| Creer ADR-011 (Remplacement OpenClaw) | HAUTE | Architecture Team | Immediat |
| Tester Airlock enforce mode avec Claude API | MOYENNE | Architecture Team | Sprint suivant |
| Preparer criteres ADR Phase 2 (AI-COS L1) | BASSE | Governance Team | Phase 2 |

---

ADR-009 v2.0 · AutoMecanik Governance Vault · 2026-03-07
