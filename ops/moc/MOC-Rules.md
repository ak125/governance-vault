---
type: moc
status: canon
updated: 2026-09-30
---

# MOC: Rules

Index des regles canoniques du projet AutoMecanik, organisees par prefixe (voir Taxonomie).

---

## Taxonomie

| Prefixe | Domaine | Fichier | Scope |
|---------|---------|---------|-------|
| **T** | Technical | [[rules-technical]] | Code (stack NestJS/Remix/Supabase) |
| **G** | Governance (vault) | [[rules-vault]] | Vault Obsidian lui-meme |
| **G** | Governance (process) | [[rules-governance-process]] | Processus, RAG, canon |
| **AI** | AI-COS | [[rules-ai-cos]] | Agents IA (golden rules) |
| **V** | V-Level SEO | [[rules-seo-vlevel]] | Classification keywords SEO |
| **R-SEO** | SEO PageRole | [[rules-seo-pagerole]] | Validation PageRole CI, immutabilite des URL (R-SEO-09) |
| **R-SEO-KW** | SEO KW import | [[rules-seo-kw-import]] | Import Google Ads KP + alias enrichment |
| **AP** | Anti-Patterns | [[rules-ai-antipatterns]] | Anti-patterns IA a eviter |
| **D** | Deployment | [[rules-deployment-workflow]] | Triggers de deploiement (push main vs tag v*) |
| **Q** | Engineering Quality | [[rules-engineering-quality]] | Best-approach mandate (anti-bricolage), verify-before-create (DB et files), modernization continue |
| **DoD** | Engineering Definition of Done | [[rules-engineering-definition-of-done]] | 9 invariants requis avant transition REVIEW→MERGED (tests, ownership, rollback, observabilite, drift, docs, monitoring, no TODO, no silent skip) |
| **AEC** | Agent Exit Contract | [[rules-agent-exit-contract]] | Coverage manifest obligatoire, no overclaim, statuts autorises, 5 etats separes — applique a TOUT agent/audit |

---

## Regles Techniques (T)

- [[rules-technical]] - **T1-T7** : Architecture 3-Tier, Supabase SDK, Sessions Redis, Validation Zod, HMAC Paiements, Git Workflow, Tests

## Regles de Gouvernance (G)

- [[rules-vault]] - **G1-G4** : Canon Fait Foi, Zero Orphelin, Commits Signes, CI Read-Only
- [[rules-governance-process]] - **G5-G8** : Canon-Only Policy, Proof Requirements, RAG Corpus Alignment, Obsolete Handling
  - Le fichier contient aussi G9 (Sunset Clause) et G10 (Exploration Budget), ajoutes par [[ADR-081-doctrine-agility-amendments]], au statut `proposed` au 2026-09-30 : non indexes ici tant que l'ADR n'est pas accepte (decision owner).

## Regles Deployment (D)

- [[rules-deployment-workflow]] - **D1-D6** : triggers de deploiement (push main, tag v*), workflow nominal, rollback

## Regles AI-COS (AI)

- [[rules-ai-cos]] - **AI1-AI10** : Pas d'indicateur = suppression, IA propose Human decide, Doute = blocage, Production sans validation interdit, Rattachement hierarchie, 1 creation = 1 fusion, Diagnostic multi-validation, Contenu critique QTO, Kill-switch CEO, Tracabilite

## Regles SEO (V, R-SEO)

- [[rules-seo-vlevel]] - **V1-V6** : Classification keywords (V1 super-champion, V2 TOP 20, V3 champion local, V4 variant, V5 volume=0, V6 bloc B)
- [[rules-seo-pagerole]] - **R-SEO-01 a R-SEO-09** : Validation PageRole pour CI (R-SEO-01 a 08) ; URL Immutability, aucune URL existante en production ne doit etre modifiee (R-SEO-09)
- [[rules-seo-kw-import]] - **R-SEO-KW-01 a R-SEO-KW-07** : Import Google Ads KP + alias enrichment (review rejets, arbre decision, batch YAML, cross-gamme scope check, RAG_ONLY_ENRICHED state)

## Anti-patterns (AP)

- [[rules-ai-antipatterns]] - **AP-01 a AP-12** : Anti-patterns AI-COS a eviter (incl. AP-11 grep-before-invent, AP-12 no-homemade-orchestrator-on-aicos via [[ADR-034-aicos-operating-contract]])

## Engineering Quality (Q)

- [[rules-engineering-quality]] - **Q1-Q4** : Mandat de la meilleure approche (anti-bricolage), verifier l'existant avant de creer (grep + Supabase information_schema), esprit de modernisation continue. Regles meta qui s'appliquent AVANT toute autre regle (T*, G*, AP*).

## Engineering Definition of Done (DoD)

- [[rules-engineering-definition-of-done]] - **DoD1-DoD9** : Invariants requis avant qu'une PR puisse passer de REVIEW a MERGED (per ADR-053 state machine). Q gate la qualite initiale, DoD gate l'acceptance merge. Inclut escape hatch `dod-skip-justified` avec 2 approvers + audit trail `__governance_event_log`. Premier livrable Etape 1 du Repository Control Plane Operational (plan 2026-05-19).

## Agent Exit Contract (AEC)

- [[rules-agent-exit-contract]] - **AEC-01 a AEC-05** : Coverage manifest obligatoire, no overclaim, statuts autorises (PARTIAL_COVERAGE/SCOPE_SCANNED/REVIEW_REQUIRED/VALIDATED_FOR_SCOPE_ONLY/INSUFFICIENT_EVIDENCE), 5 etats separes (scan/analysis/correction/validation/verdict). **Source canonique unique** — copies dans repos applicatifs verifiees par hash SHA-256. Applique a TOUT agent/run/audit/analyse.

## Marketing Brand Voice

- [[rules-marketing-voice]] - **v1.0.0** : 2 voix de marque (ECOMMERCE `automecanik.com` national / LOCAL magasin 93) + règles HYBRID strictes (zone 93, hybrid_reason obligatoire, CTA + conversion_goal séparés par unit). Section `local_canon` (legal_name, trade_name, address, phone, opening_hours) à compléter par le métier avant `validated: true`. Sync vers monorepo via canon-publish (pattern AEC). Référence canon : [[ADR-036-marketing-operating-layer]].

---

## Plus d'infos

- Architecture : [[architecture]]
- MOC parent : [[MOC-Governance]]
- Decisions : [[MOC-Decisions]]
