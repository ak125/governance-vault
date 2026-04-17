---
id: ADR-002
title: Airlock & Zero-Trust Agents
status: accepted-revised
version: 2.0.0
date_original: 2026-02-03
date_revision: 2026-03-07
decision_makers:
  - Architecture Team
  - Governance Team
supersedes: ADR-002 v1.0 (OpenClaw era)
superseded_by: null
references:
  - ADR-009
  - ADR-011
  - REG-001 v1.4.1
---

# ADR-002: Airlock & Zero-Trust Agents

## Changelog

| Version | Date | Changement |
|---------|------|------------|
| 1.0 | 2026-02-03 | Creation — OpenClaw comme moteur |
| 2.0 | 2026-03-07 | OpenClaw → Claude API (ADR-011). Pipeline revise. |

### Changelog v2.0

Cette revision acte le remplacement d'OpenClaw par Claude API comme moteur d'execution des agents. Le principe Zero-Trust et l'architecture Airlock sont maintenus. Le pipeline d'execution est redefini.

---

## 1. Contexte

Le projet AutoMecanik utilise des agents IA pour assister le developpement, le monitoring SEO, la gestion des donnees et l'orchestration metier. Ces agents peuvent generer du code, des configurations, et des modifications de fichiers sur une plateforme gerant 4M+ produits et 59k utilisateurs.

**Problemes identifies et maintenus :**

- Un agent peut produire du code non valide ou dangereux
- Aucun mecanisme de validation avant integration = risque critique
- Risque d'injection de vulnerabilites dans le monorepo

**Changement de contexte (v2.0) :**

- OpenClaw supprime — remplace par Claude API comme moteur d'execution
- Le pipeline agent-submissions reste le canal officiel de soumission
- L'Airlock reste obligatoire pour tous les agents APPROVED_WITH_CONDITIONS

---

## 2. Decision

Maintien du principe **Zero-Trust Agents** avec adaptation du pipeline d'execution :

> Tous les agents sont consideres non fiables par defaut. Claude API est le moteur d'orchestration. Aucun agent n'ecrit directement dans les repos critiques.

### 2.1 Nouveau Pipeline d'execution

| Etape | Acteur | Action | Gate |
|-------|--------|--------|------|
| 1 | Claude API / Cowork | Genere output (report ou bundle) | — |
| 2 | agent-submissions | Bundle signe HMAC-SHA256 soumis | Signature verifiee |
| 3 | Airlock | Valide le bundle contre les regles ADR | Enforce mode |
| 4 | GitHub PR | PR automatique creee vers monorepo | CI Gate |
| 5 | Human Review | Validation humaine obligatoire | Merge manuel |

### 2.2 Modes d'operation Airlock

| Mode | Comportement | Usage actuel |
|------|-------------|-------------|
| disabled | Aucune restriction | Tests locaux uniquement |
| observe | Log sans bloquer | Phase d'apprentissage agents nouveaux |
| enforce | Bloque les violations | Production — mode par defaut |

### 2.3 Roles Claude dans le systeme

| Role | Interface | Usage | Zone |
|------|-----------|-------|------|
| Orchestrateur principal | Claude API | Execute agents principal_vps automatiques | principal_vps |
| Concepteur / Specs | Claude Desktop + Cowork | Redige ADR, specs agents, contenu SEO | local |
| Validateur | Claude API | Verifie bundles avant soumission Airlock | external |

### 2.4 Perimetre protege (inchange)

- Monorepo principal (`backend/`, `frontend/`, `packages/`)
- Governance vault (`.local/governance-vault/`)
- Fichiers de configuration critiques (`.env`, `docker-compose.*.yml`)
- Base de donnees Supabase — acces lecture seule pour agents

---

## 3. Consequences

### Positives

- Tracabilite complete maintenue — HMAC-SHA256 + audit trail
- Validation humaine obligatoire preservee
- Claude API = cout previsible vs infrastructure OpenClaw a maintenir
- Cowork permet la gouvernance locale sans VPS supplementaire immediat

### Negatives

- Migration des fiches agents APPROVED_WITH_CONDITIONS requise
- ADR-005 (Airlock Observe Mode) et ADR-009 a mettre a jour

### Neutres

- L'implementation RpcGateService dans `backend/src/security/rpc-gate/` reste valide
- REG-001 reste la source de verite — aucun changement de structure

---

## 4. Implementation

### 4.1 Pour agents APPROVED (54 actifs)

Aucun changement. Ces agents fonctionnent dans leur zone declaree sans gate Airlock.

### 4.2 Pour agents APPROVED_WITH_CONDITIONS (15)

Leurs fiches doivent etre mises a jour pour referencer Claude API a la place d'OpenClaw. La condition Airlock/RPC gate reste obligatoire.

- Mettre a jour la section 'Execution Engine' dans chaque fiche agent
- Remplacer toute reference a OpenClaw par Claude API
- Valider le pipeline agent-submissions pour chaque agent
- Tester en mode Airlock observe avant enforce

### 4.3 Pour agents NOT_APPROVED (46)

Inchange — necessitent un nouvel ADR explicite. Les agents C-suite IA (CEO, CTO, CPO, CMO, CFO) restent interdits en Phase 1.

---

ADR-002 v2.0 · AutoMecanik Governance Vault · 2026-03-07
