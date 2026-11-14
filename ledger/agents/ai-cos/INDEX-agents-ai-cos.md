---
type: index
status: canon
category: agents
subcategory: ai-cos
updated: 2026-11-14
---

# INDEX: Agents / AI-COS Agents (C-Suite, SEO, RAG, QA, Data, Infra)

> **Système retiré** ([[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]]) : la machine AI-COS est arrêtée depuis octobre 2026 (jour exact inconnu) et le système d'agents AI-COS est retiré avec elle. Ses 28 fiches sont `disabled`, conservées avec leurs verdicts comme historique. Les 4 agents QA et les 12 prompts gardent leur statut `active` au catalogue : ils ne dépendent pas d'AI-COS.
>
> Agents rangés historiquement sous l'architecture AI-COS : CEO/CFO/CMO/CPO/CTO IA, leads SEO (canonical, content, exec, kp, lead, qa, sitemap, vlevel), RAG (indexer, retriever, validator), QA (functional, orchestrator, seo-tech, visual), Data (backup, cleanup, lead, validator), Infra (logs, monitor), prompts (brief-enricher, content-batch, keyword-planner, R1/R3/R4/R6 batches).

**Parent MOC**: [[MOC-Agents]]

---

## Agents du système AI-COS, retirés (28, `disabled`)

- [[AGENT-agent-aicos-architect]]
- [[AGENT-agent-aicos-governance]]
- [[AGENT-agent-ceo-ia]]
- [[AGENT-agent-cfo-ia]]
- [[AGENT-agent-cmo-ia]]
- [[AGENT-agent-cpo-ia]]
- [[AGENT-agent-cto-ia]]
- [[AGENT-agent-data-backup]]
- [[AGENT-agent-data-cleanup]]
- [[AGENT-agent-data-lead]]
- [[AGENT-agent-data-validator]]
- [[AGENT-agent-infra-logs]]
- [[AGENT-agent-infra-monitor]]
- [[AGENT-agent-qto]]
- [[AGENT-agent-rag-indexer]]
- [[AGENT-agent-rag-lead]]
- [[AGENT-agent-rag-retriever]]
- [[AGENT-agent-rag-validator]]
- [[AGENT-agent-seo-canonical]]
- [[AGENT-agent-seo-content-lead]]
- [[AGENT-agent-seo-content]]
- [[AGENT-agent-seo-exec-lead]]
- [[AGENT-agent-seo-kp-lead]]
- [[AGENT-agent-seo-lead]]
- [[AGENT-agent-seo-qa-lead]]
- [[AGENT-agent-seo-sitemap]]
- [[AGENT-agent-seo-vlevel]]
- [[AGENT-front-agent]]

## Agents QA conservés (4, exécutés sur la machine PROD)

> Rangés ici par l'histoire du dossier ; ils ne dépendent pas d'AI-COS (cron `tests/qa-audit/qa-audit-cron.sh`). Leur exécution réelle sur PROD n'est pas vérifiée par [[ADR-129-retrait-ai-cos-machine-systeme-agents|ADR-129]].

- [[AGENT-agent-qa-functional]]
- [[AGENT-agent-qa-orchestrator]]
- [[AGENT-agent-qa-seo-tech]]
- [[AGENT-agent-qa-visual]]

## Prompts Claude Code conservés (12, zone `local`, machine DEV)

- [[AGENT-prompt-brief-enricher]]
- [[AGENT-prompt-conseil-batch]]
- [[AGENT-prompt-content-batch]]
- [[AGENT-prompt-keyword-planner]]
- [[AGENT-prompt-r1-content-batch]]
- [[AGENT-prompt-r3-image-prompt]]
- [[AGENT-prompt-r4-content-batch]]
- [[AGENT-prompt-r4-keyword-planner]]
- [[AGENT-prompt-r6-content-batch]]
- [[AGENT-prompt-r6-image-prompt]]
- [[AGENT-prompt-r6-keyword-planner]]
- [[AGENT-prompt-research-agent]]

---

## Voir aussi

- [[MOC-Agents]] - Vue d'ensemble des agents
- [[ADR-008-agent-placement-rules]] - Regles de placement par zone
- [[ADR-013-agent-lifecycle-governance]] - Cycle de vie
- [[rules-ai-cos]] - Regles AI1-AI10 pour les agents

---

_Derniere mise a jour: 2026-11-14 (retrait du système AI-COS, ADR-129)_
