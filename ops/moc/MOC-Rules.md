---
type: moc
status: canon
updated: 2026-04-30
---

# MOC: Rules

Index des regles canoniques du projet AutoMecanik, organisees par taxonomie unique **T / G / AI / V**.

---

## Taxonomie

| Prefixe | Domaine | Fichier | Scope |
|---------|---------|---------|-------|
| **T** | Technical | [[rules-technical]] | Code (stack NestJS/Remix/Supabase) |
| **G** | Governance (vault) | [[rules-vault]] | Vault Obsidian lui-meme |
| **G** | Governance (process) | [[rules-governance-process]] | Processus, RAG, canon |
| **AI** | AI-COS | [[rules-ai-cos]] | Agents IA (golden rules) |
| **V** | V-Level SEO | [[rules-seo-vlevel]] | Classification keywords SEO |
| **R-SEO** | SEO PageRole | [[rules-seo-pagerole]] | Validation PageRole CI |
| **R-SEO-KW** | SEO KW import | [[rules-seo-kw-import]] | Import Google Ads KP + alias enrichment |
| **AP** | Anti-Patterns | [[rules-ai-antipatterns]] | Anti-patterns IA a eviter |
| **D** | Deployment | [[rules-deployment-workflow]] | Triggers DEV/PROD (push main vs tag v*) |
| **Q** | Engineering Quality | [[rules-engineering-quality]] | Best-approach mandate (anti-bricolage), verify-before-create (DB et files), modernization continue |
| **AEC** | Agent Exit Contract | [[rules-agent-exit-contract]] | Coverage manifest obligatoire, no overclaim, statuts autorises, 5 etats separes — applique a TOUT agent/audit |

---

## Regles Techniques (T)

- [[rules-technical]] - **T1-T7** : Architecture 3-Tier, Supabase SDK, Sessions Redis, Validation Zod, HMAC Paiements, Git Workflow, Tests

## Regles de Gouvernance (G)

- [[rules-vault]] - **G1-G4** : Canon Fait Foi, Zero Orphelin, Commits Signes, CI Read-Only
- [[rules-governance-process]] - **G5-G8** : Canon-Only Policy, Proof Requirements, RAG Corpus Alignment, Obsolete Handling

## Regles Deployment (D)

- [[rules-deployment-workflow]] - **D1-D6** : push main = DEV preprod, tag v* = PROD, workflow nominal, rollback

## Regles AI-COS (AI)

- [[rules-ai-cos]] - **AI1-AI10** : Pas d'indicateur = suppression, IA propose Human decide, Doute = blocage, Production sans validation interdit, Rattachement hierarchie, 1 creation = 1 fusion, Diagnostic multi-validation, Contenu critique QTO, Kill-switch CEO, Tracabilite

## Regles SEO (V, R-SEO)

- [[rules-seo-vlevel]] - **V1-V6** : Classification keywords (V1 super-champion, V2 TOP 20, V3 champion local, V4 variant, V5 volume=0, V6 bloc B)
- [[rules-seo-pagerole]] - **R-SEO-01 a R-SEO-08** : Validation PageRole pour CI
- [[rules-seo-kw-import]] - **R-SEO-KW-01 a R-SEO-KW-07** : Import Google Ads KP + alias enrichment (review rejets, arbre decision, batch YAML, cross-gamme scope check, RAG_ONLY_ENRICHED state)

## Anti-patterns (AP)

- [[rules-ai-antipatterns]] - **AP-01 a AP-12** : Anti-patterns AI-COS a eviter (incl. AP-11 grep-before-invent, AP-12 no-homemade-orchestrator-on-aicos via [[ADR-034-aicos-operating-contract]])

## Engineering Quality (Q)

- [[rules-engineering-quality]] - **Q1-Q4** : Mandat de la meilleure approche (anti-bricolage), verifier l'existant avant de creer (grep + Supabase information_schema), esprit de modernisation continue. Regles meta qui s'appliquent AVANT toute autre regle (T*, G*, AP*).

## Agent Exit Contract (AEC)

- [[rules-agent-exit-contract]] - **AEC-01 a AEC-05** : Coverage manifest obligatoire, no overclaim, statuts autorises (PARTIAL_COVERAGE/SCOPE_SCANNED/REVIEW_REQUIRED/VALIDATED_FOR_SCOPE_ONLY/INSUFFICIENT_EVIDENCE), 5 etats separes (scan/analysis/correction/validation/verdict). **Source canonique unique** — copies dans repos applicatifs verifiees par hash SHA-256. Applique a TOUT agent/run/audit/analyse.

## Marketing Brand Voice

- [[rules-marketing-voice]] - **v1.0.0** : 2 voix de marque (ECOMMERCE `automecanik.com` national / LOCAL magasin 93) + règles HYBRID strictes (zone 93, hybrid_reason obligatoire, CTA + conversion_goal séparés par unit). Section `local_canon` (legal_name, trade_name, address, phone, opening_hours) à compléter par le métier avant `validated: true`. Sync vers monorepo via canon-publish (pattern AEC). Référence canon : [[ADR-036-marketing-operating-layer]].

---

## Plus d'infos

- Architecture : [[architecture]]
- MOC parent : [[MOC-Governance]]
- Decisions : [[MOC-Decisions]]
