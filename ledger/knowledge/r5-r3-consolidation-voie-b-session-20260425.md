---
type: knowledge
status: canon
created: 2026-04-25
updated: 2026-07-07
tags: [seo, r5-diagnostic, r3-conseils, s2-diag, voie-b, session-debrief, partial-coverage]
related-adr: [ADR-027]
related-prs: [vault#76, monorepo#186]
related-rules: [G1, G2, R-SEO-04]
verdict: PARTIAL_COVERAGE
---

# R5→R3 S2_DIAG consolidation — Session debrief 2026-04-25

## Reconciliation 2026-07-07

> Cette note conserve la **vérité historique** de la session du 25 avril 2026 (constats, PRs, incidents,
> patterns). Mais ses **prescriptions de production S2_DIAG ont été superseded** par ADR-027 § Correction
> 2026-07-07. La SoT de statut ADR = le frontmatter ADR-027 / ADR-033.

**Ne sont plus des autorités d'exécution :**
- **B3 — Batch RAG primaire** (§2.1) ;
- la **priorité `RAG primary > __diag_* > observable`** (§2.2 pilier 4) ;
- la règle **« choisir P1 ou P2 par gamme »** (§2.3) ;
- **toute Phase C de production S2_DIAG depuis le RAG** (§4.1 : `audit-rag-coverage-s2diag`,
  `batch-enrich-s2-diag.ts`, `ConseilEnricherService.enrichGamme`) ;
- la clause **Phase D « résidu après RAG insuffisant »** et **tout fallback `observable|diag_engine` comme
  hiérarchie de sources** (§4.2) ;
- **toute métrique post-Phase-C** (51 %→≥85 %, ≥95 %, GSC +20 %) présentée comme **objectif actuel**.

**Autorité actuelle (ADR-027 § Correction 2026-07-07) :**
- **INPUT A** = `__diag_*` — vérité symptôme / système / cause ;
- **INPUT B** = WIKI `diagnostic_relations[]` — relation typée pièce ↔ symptôme ;
- **S2_DIAG** = **composition déterministe de A + B** sur la surface **R3** ;
- **RAG** = **zéro autorité de contenu** ; **inventory pointer historique** seulement ;
- **`__seo_observable`** = legacy / historique uniquement ;
- **Entrée canonique absente ⇒ aucune nouvelle S2_DIAG canonique ⇒ jamais** de fallback RAG ni observable.

Cf. `feedback_rag_zero_content_write_authority_remove_not_secure`, ADR-027 § Correction, ADR-033.

## Contexte

User Fafa propose un **repositionnement stratégique marketing** : passer du
funnel "intention pièce → produit" à "symptôme/panne → diagnostic → pièce
→ entretien". Six leviers identifiés : SEO symptômes, YouTube, CRM
entretien, freemium outil, brand, ads différenciantes.

Demande explicite : **vérifier 4 questions avant d'aller plus loin** —
maturité de l'outil de diagnostic, inputs supportés, outputs produits, data
d'usage. Puis arbitrer la séquence d'exécution avec contrainte explicite
*"meilleure solution pas de bricolage"*.

## Section 1 — Scope scanné (Phase 0 audit)

| Item | Source | Résultat |
|------|--------|----------|
| Maturité moteur diagnostic | `backend/src/modules/diagnostic-engine/` | **Production-ready core** : 7 endpoints actifs, 6 engines chaînés (356 lignes orchestrator), schémas Zod input/output validés, 13 systèmes seed |
| Tests unitaires | `find diagnostic-engine -name "*.test.ts"` | **Absent** — aucun test dans le module |
| Auth/rate limit POST analyze | controller | **Absent** — endpoint ouvert sans quota |
| Inputs supportés | `diagnostic-input.schema.ts` | 6 modes (`diagnostic_symptom`, `warning_light_analysis`, `dtc_analysis`, `maintenance_check`, `revision_check`, `preventive_check`) + 4 modes de signal + contexte véhicule + contexte usage |
| Outputs produits | `evidence-pack.schema.ts` | Evidence pack riche : hypothèses scorées, catalog_guard avec `suggested_gammes` + `pg_id`, safety_alert, rag_facts L1-L4 |
| Data d'usage live (MCP DB) | `__diag_session` | **101 sessions total**, 10 sur 30j, 2 sur 7j → **~0.3 session/jour** ; 100% en `intent_type='diagnostic_symptom'` (5 autres modes jamais utilisés) |
| FK sessions ↔ customer | schéma | **Absente** — `__diag_session` stateless, conversion diag→achat **non mesurable** |
| Pages R5 publiées | `__seo_observable` | **24 published / 1152 drafts** sur 1176 lignes |
| Qualité contenu R5 | sample symptom_description | 24 published : 200-921 chars symptom (qualité éditoriale) ; 1152 drafts : **79-105 chars** (stubs squelettiques produit cartésien `voyant-X / odeur-X / fuite-X × système`) |
| `schema_org` peuplé | DB | **0/1176** (gros gap JSON-LD) |
| Sitemap diagnostic réel | `curl /sitemap-diagnostic.xml` | **1 URL** (le hub `/diagnostic-auto`), pas 5 ni 24 |
| Décision sous-jacente | `git log -S "R5 consolidation"` | Commit `a57cefc7` (2026-03-22) : "R5 sub-pages (1176 URLs, **~15 clics totaux, positions 30-60**) now 301 redirect to R3 conseil pages with `#diagnostic-rapide` anchor" |
| ADR formel pour cette décision | `grep -rln "R5.*consolidat" governance-vault/` | **Aucun** — dette G1 (décision en code uniquement) |
| Sections R3 conseil gamme | `__seo_gamme_conseil` | 259 gammes publiées, sections S1-S8 ~100% couverture |
| Section S2_DIAG | DB | **133/259 = 51%** couverture — gap majeur |
| Quality score S2_DIAG existants | DB | avg **85.4**, tous > 70 |
| S2_DIAG enrichis via observable_fallback | DB | **0/133** (0% — fallback structurellement mort) |
| Cause root du fallback mort | RPC `get_observable_symptoms_for_gamme` | Filtre `so.is_published = true` → 1152 drafts invisibles, 24 published couvrent 11 gammes seulement |
| Mapping gamme ↔ diag_system | schéma DB | **Absent** — `__diag_symptom`/`__diag_cause` ont `system_id` mais pas `pg_id` ; moteur `__diag_*` isolé du graphe gammes |

## Section 2 — Décisions prises

> **HISTORICAL DECISION — NOT CURRENT EXECUTION AUTHORITY (réconcilié 2026-07-07).** Les choix de source
> ci-dessous (B3 Batch RAG, priorité RAG > `__diag_*` > observable, « choisir P1 ou P2 ») sont **superseded**
> par le contrat d'autorité A + B (voir § Reconciliation). Conservés comme trace historique.

### 2.1. Voie stratégique retenue : **B (consolidation R3 + qualité S2_DIAG)**

Trois sous-voies envisagées, **B3 puis B2**, **B1 abandonnée** :

| Sous-voie | Description | Statut |
|-----------|-------------|--------|
| B1 | Réécrire 1152 observable drafts en quality | **Abandonnée** — gaspillage, archi sunsettée |
| B2 | Refonte RPC : moteur `__diag_*` + mapping `__diag_gamme_system_map` | Phase D du plan |
| B3 | Batch RAG primaire sur 126 gammes manquantes | Phase C du plan |

### 2.2. ADR-027 formalisé (Phase A)

Quatre piliers canoniques :

1. **R5 sub-pages = sunsetted permanent** — 301 perpétuels vers R3 `#diagnostic-rapide`, sitemap figé à 1 URL
2. **R5 hub `/diagnostic-auto` = produit/wizard** — indexable seul, optimisé conversion
3. **S2_DIAG = section canonique R3** avec ancre `#diagnostic-rapide` (cible des 301)
4. **3 sources d'enrichissement par priorité** : RAG primary > moteur `__diag_*` > observable fallback (legacy)

### 2.3. Anti-patterns explicitement interdits

- ❌ Réécrire les 1152 observable drafts squelettiques
- ❌ Retirer le filtre `is_published = true` de la RPC fallback (polluerait S2_DIAG)
- ❌ Re-créer des pages `/diagnostic-auto/{slug}` indexables (revient sur la décision data-driven de mars 2026)
- ❌ Doubler les sources : choisir P1 ou P2 par gamme, pas concaténer

## Section 3 — Livrables session (PRs ouvertes)

| Phase | Livrable | PR | Statut |
|-------|----------|-----|--------|
| **A** | ADR-027 vault — formalise R5→R3 (4 piliers, 5 phases, métriques chiffrées, rollback) | [vault#76](https://github.com/ak125/governance-vault/pull/76) | OPEN |
| **B** | Migration `__diag_session.customer_id TEXT FK` + view `v_diag_funnel` + GA4 event `diagnostic_completed` | [monorepo#186](https://github.com/ak125/nestjs-remix-monorepo/pull/186) | OPEN |

### 3.1. Détails PR vault#76 (ADR-027)

- 256 lignes ADR
- 4 piliers + 5 phases (A→E) + métriques chiffrées + rollback procedures
- Branche `adr/027-r5-consolidation-r3-s2-diag` depuis `main`
- Commit signé `c67864a`

### 3.2. Détails PR monorepo#186 (Phase B)

3 fichiers, +213 lignes :

- `backend/supabase/migrations/20260426_diag_session_customer_fk_v_diag_funnel.sql` (+126)
  - `ALTER TABLE __diag_session ADD COLUMN customer_id TEXT NULL` (TEXT car `___xtr_customer.cst_id` est TEXT, pas UUID)
  - FK `ON DELETE SET NULL`
  - Index partiel `WHERE customer_id IS NOT NULL`
  - View `v_diag_funnel` : agrégation jour × sessions × orders × revenue + `conversion_rate_pct` (casts explicites schéma legacy)
  - Smoke test DO block au runtime
- `frontend/app/utils/analytics.ts` (+66) — `trackDiagnosticCompleted` + `trackDiagnosticHypothesisClick`
- `frontend/app/components/diagnostic-wizard/DiagnosticWizard.tsx` (+21) — wiring après `analyze` success
- Branche `feat/diag-session-customer-fk-adr027` cherry-pickée propre depuis `015458bb` (origin/main)
- Dry-run view validé en live MCP : queriable, casts OK

## Section 4 — Reste à faire (phases C/D/E + leviers parallèles)

> **HISTORICAL DECISION — NOT CURRENT EXECUTION AUTHORITY (réconcilié 2026-07-07).** La Phase C (Batch RAG
> S2_DIAG) et la clause Phase D « résidu après RAG » / fallback `S2_DIAG_SOURCE=observable|diag_engine` sont
> **superseded** ; **ne pas exécuter cette checklist**. Le mécanisme déterministe `__diag_*` (mapping +
> `buildS2DiagFromDiagEngine`) reste valide comme **INPUT A** du contrat d'autorité (voir § Reconciliation).

### 4.1. Phase C — Batch RAG enrichissement S2_DIAG (3-5 jours)

Démarrer après merge de PR vault#76 + monorepo#186.

- [ ] Audit `scripts/audit/audit-rag-coverage-s2diag.py` sur les 126 gammes manquantes
  - Identifier celles avec gamme `.md` éligible (`≥2 symptoms AND ≥2 quick_checks`)
  - Output : rapport markdown listant éligibles vs non-éligibles
- [ ] Runner `scripts/seo/batch-enrich-s2-diag.ts` invoquant `ConseilEnricherService.enrichGamme(pgId)` sur les éligibles
- [ ] Quality gate : `sgc_quality_score ≥ 70` obligatoire pour upsert
- [ ] Cible : passer de 51% → ≥85% couverture S2_DIAG
- [ ] Métrique de sortie : combien de S2_DIAG produites + combien restent vides (= input Phase D)

### 4.2. Phase D — RPC moteur `__diag_*` (~2 sprints)

Pour le résidu après Phase C (gammes sans RAG suffisant).

- [ ] Migration : table `__diag_gamme_system_map(pg_id INT, system_id INT, weight SMALLINT, primary_match BOOL)`
- [ ] Seed : ~400 mappings `(pg_id, system_id)` validés humainement (gouvernance à définir — outil LLM-suggéré + review ?)
- [ ] RPC `build_s2_diag_from_diag_engine(p_pg_id)` SQL STABLE joignant `__diag_symptom × __diag_symptom_cause_link × __diag_cause × __diag_safety_rule`
- [ ] Refactor `buildS2DiagFromObservable` → `buildS2DiagFromDiagEngine` avec source RPC switchée (flag env `S2_DIAG_SOURCE=observable|diag_engine`)
- [ ] Cible : passer de ≥85% → ≥95% couverture
- [ ] Décision pendante : prioriser `primary_match` ou ranger par poids quand un symptôme concerne plusieurs gammes ?

### 4.3. Phase E — Archivage legacy

- [ ] Marquer les 1152 observable drafts squelettiques en `is_archived = true` (ou suppression conditionnelle après PR review)
- [ ] Déprécier la RPC `get_observable_symptoms_for_gamme` au profit de la nouvelle RPC moteur
- [ ] Audit GSC J+30 post-Phase C : vérifier zero 404 sur les anciens slugs `/diagnostic-auto/*`

### 4.4. Rule canon à actualiser

- [ ] PR séparée sur `rules-seo-pagerole.md` : R-SEO-04 (longueur de contenu R5 min 200 words) — actualiser pour préciser que la contrainte ne s'applique qu'au hub `/diagnostic-auto`, pas aux sub-pages (qui n'existent plus en page indexable)

### 4.5. Leviers marketing parallèles (hors voie B SEO)

- [ ] **Levier 3 — CRM entretien** (~3 sprints, après Phase B mergée) — tables `customer_vehicles` + `maintenance_schedule` + cron + templates email. RGPD à valider en amont.
- [ ] **Levier 4 — Outil gratuit / Acquisition** (~2 sprints) — landing pages `/lp/diagnostic`, freemium quotas, retargeting
- [ ] **Levier 6 — Ads différenciantes** (~2-3 jours) — Pixel Meta + TikTok, audience lookalike "users qui ont diagnostiqué" basée sur GA4 event `diagnostic_completed`
- [ ] **Levier 2 — YouTube/Shorts** — décision business sur budget production, infra 100% à construire (pas de table vidéo, pas d'API YouTube intégrée)
- [ ] **Levier 5 — Brand positioning** — choix business hors scope technique

## Section 5 — Notes opérationnelles (incidents session)

### 5.1. Auto-renumber agressif des ADRs vault

Lors de la création initiale d'ADR-026, observation d'un comportement
filesystem watcher qui auto-renomme les fichiers ADR pour éviter les
collisions de numéro :

- Création de `ADR-026-r5-...` → orphan préexistant `ADR-026-rag-v2.1-control-plane-closure.md` (frontmatter `id: ADR-026`) apparaît
- Renommage personnel en ADR-027 → orphan auto-renommé en ADR-029
- Tentative ADR-028 → orphan suit (ADR-028)

Cause non identifiée (pas de hook visible dans `.githooks/`, pas de cron
nommé). Hypothèse : Obsidian sync filesystem watcher côté Windows, ou
agent paperclip en parallèle.

**Mitigation appliquée** : choisir un numéro éloigné (ADR-027) et
committer rapidement après le `git add` pour minimiser la fenêtre de
race.

### 5.2. Branch hijacking pendant édition monorepo

Pendant l'édition Phase B sur `feat/diag-session-customer-fk-adr027`,
la branche courante a été automatiquement switchée plusieurs fois vers
`fix/seo-monitoring-add-cwv-gsclinks-endpoints` et autres branches
appartenant à du travail parallèle.

**Mitigation appliquée** : commit sur la branche actuellement active,
puis cherry-pick sur ma branche dédiée à la fin (commit `4f8ce9f6` cherry-picked
depuis `10e3529a`).

### 5.3. Hook commit-msg lowercase strict

Convention conventional commits : subject lowercase obligatoire.
`feat(diag): ADR-027 Phase B...` → rejeté ; `feat(diag): adr-027 phase b...` → accepté.

## Section 6 — Verdict et coverage manifest

### Final status: **PARTIAL_COVERAGE**

- **Scope requested** : vérifier 4 questions outil + arbitrer voie marketing structurelle
- **Scope actually scanned** :
  - 7 endpoints API diagnostic-engine + schémas Zod input/output
  - 6 tables `__diag_*` + 17 fichiers RAG diagnostic
  - Tables/services SEO R5 (1176 lignes audit)
  - Module marketing + module mail + intégrations GA4/GSC
  - DB live (compteurs sessions + qualité S2_DIAG via MCP)
  - Code conseil-enricher (S2_DIAG fallback path)
  - Code sitemap-v10-static (R5 hub-only)
  - Vault rules-seo-pagerole + ADR-022/025
  - Git log historique commit `a57cefc7`
- **Files read count** : ~30 fichiers + 12 requêtes SQL live
- **Excluded paths** : tests, configs Docker, RAG enrichment engine interne (lu en surface), pages admin diagnostic, RLS policies sur `__diag_*`, pixel Meta/TikTok integration
- **Unscanned zones** :
  - Code complet `RagEnrichmentEngine`
  - Frontend `DiagnosticResults` component (où câbler `trackDiagnosticHypothesisClick`)
  - Schéma exact des 1176 redirects 301 actifs (audit GSC J+30 requis)
  - Conformité RGPD CRM entretien (Levier 3)
- **Corrections proposed** : 4 phases C-E + 5 leviers marketing — séquencés, non appliqués
- **Corrections applied** : Phase A (ADR-027 vault PR#76) + Phase B (monorepo PR#186) — commits poussés, **PRs en attente de review/merge par @fafa**
- **Validation executed** : SQL dry-run view `v_diag_funnel` sur DB live, smoke test queriable
- **Remaining unknowns** :
  - Volume cible final pages C-D (dépend du résultat audit RAG coverage)
  - ROI réel ads diagnostic post-instrumentation
  - Capacité prod vidéo (Levier 2)
  - Décision gouvernance seed `__diag_gamme_system_map` (~400 mappings)

### Suite recommandée

1. **Reviewer + merger** PR vault#76 (ADR-027) — foundation canon
2. **Reviewer + merger** PR monorepo#186 (Phase B) — instrumentation
3. **Vérifier J+1 post-deploy DEV** : event GA4 `diagnostic_completed` visible DebugView, view `v_diag_funnel` queriable
4. **Démarrer Phase C** dans nouvelle session : audit RAG coverage S2_DIAG des 126 gammes éligibles
5. **Programmer follow-up J+30** : audit GSC zero 404 + courbe `conversion_rate_pct` du `v_diag_funnel`

## Références

- ADR-027 (cette session) — `governance-vault/ledger/decisions/adr/ADR-027-r5-consolidation-into-r3-s2-diag.md`
- Plan d'exécution (local DEV VPS) — `/home/deploy/.claude/plans/verifier-ce-que-mutable-cake.md`
- Commit consolidation initiale — `a57cefc7` (monorepo, 2026-03-22)
- ADR-015 (Vault SoT, dette G1)
- ADR-022 (R8 RAG Control Plane — pattern propose-before-write similaire)
- ADR-025 (SEO Department Architecture — Module 2 On-page intelligence)
- `rules-seo-pagerole.md` (R-SEO-02, R-SEO-04, R-SEO-05)
