---
id: ADR-057
title: marketingskills (coreyhaines31) — pattern d'adoption wrapper canon-bound
status: proposed
date: 2026-05-09
deciders: [Fafa]
decision_makers: [Fafa]
related: [ADR-036, ADR-038, ADR-039, ADR-040, ADR-047, ADR-054, ADR-055, MOC-Decisions]
---

# ADR-057 : marketingskills — pattern d'adoption wrapper canon-bound

## Context

Le repo public `coreyhaines31/marketingskills` (MIT, 27.5k★, v1.10.0 — 2026-05-06)
expose 40+ skills Agent SDK couvrant CRO, copywriting, SEO, paid ads, email,
analytics, churn, referral, RevOps, sales enablement. Il a été soumis à
vérification le 2026-05-09 (cf. plan
`/home/deploy/.claude/plans/verifier-skip-to-jaunty-zebra.md`).

Le gap analysis a comparé ces 40 skills à l'inventaire interne :

- **26 skills locaux** (8 DEV à `/opt/automecanik/app/.claude/skills/`,
  17 SEO à `workspaces/seo-batch/.claude/skills/`, 1 wiki à `workspaces/wiki/`)
- **Backend SEO seo-v9** mature (`backend/src/modules/seo/`, `seo-monitoring/`,
  `seo-shadow-observatory/` — cf. ADR-047, ADR-055)
- **Workspace marketing Phase 1** (ADR-036) : 3 agents G1 + 11 services backend
  dont `multi-channel-copywriter` + `brand-compliance-gate` + tables
  `__marketing_brief`, `__retention_trigger_rules` (migration `20260430_marketing_layer_phase1.sql`)
- **Canon brand-voice** `canon-mirrors/marketing-voice.md` (status `proposed`)

Verdict de l'analyse :

| Verdict | Nb | Raison |
|---|---|---|
| 🔴 Ignorer | 17 | Doublons SEO/copy/social ou hors scope (paywall/SaaS, ASO, video, community) |
| 🟠 Évaluer | 11 | Pas de signal métier actuel justifiant l'adoption |
| 🟡 Adapter | 6 | Utiles mais exigent FR-isation + intégration brand-compliance |
| 🟢 Adopter | 4 | Comblent un trou réel (page-cro, form-cro, ab-test-setup, customer-research) |

Sans cadre formel, l'adoption hypothétique génère 4 risques empiriques
documentés dans le plan :

1. **Pollution canon** par install bulk (17 doublons écrasent ou concurrencent
   le pipeline SEO + brand voice).
2. **Régression FR** : 14 skills sont des générateurs de copy EN — sortie EN
   par défaut violerait `feedback_french_only_for_content.md`.
3. **Bypass brand-compliance** : copywriting/social externes court-circuitent
   `multi-channel-copywriter` + `brand-compliance-gate` (chaîne canon ADR-036).
4. **Drift fork** : forker upstream + FR-iser localement crée dette de
   maintenance permanente sans lien remote.

Cette ADR fixe l'unique pattern admis pour intégrer ce repo (ou tout repo
de skills tiers analogue), ainsi que les garde-fous anti-régression.

## Decision

### D1. Pattern unique : wrapper canon-bound + 1 skill pilote par cycle

L'adoption de tout skill tiers se fait **exclusivement** via un wrapper local
mince qui délègue à l'upstream read-only et injecte le contexte canon
AutoMecanik (FR + brand-voice + RGPD + véhicule). Schéma cible :

```
.agents/skills/<skill-upstream>/        ← installé via `npx skills add <repo> --skill <name>`
                                         (read-only, pinned via .agents/skills.lock.json)

.claude/skills/<categorie>/auto-<skill-upstream>/SKILL.md
        ← wrapper local (≤ 30 lignes), canon-bound
        ← frontmatter référence canon-mirrors/marketing-voice.md
        ← body : (1) charger contexte FR + canon, (2) appliquer RGPD,
                  (3) déléguer méthodo à upstream, (4) sortie FR uniquement
```

L'upstream **n'est jamais forké, jamais patché localement**. Toute
amélioration upstream remonte par PR au repo source `coreyhaines31/marketingskills`
(licence MIT le permet).

### D2. Cycle d'adoption en 5 étapes — gouvernance avant code

1. **ADR vault** (la présente) — `proposed` puis `accepted` après merge.
2. **Attente fenêtre** — adoption sur monorepo bloquée tant que la branche
   feature en cours (`feat/seo-v9-r7-router-wire` au 2026-05-09) n'est pas mergée.
   Mémoire DEV : `feedback_branch_scope_discipline.md`.
3. **PR pilote unique monorepo** — 1 skill, 1 wrapper, 1 knowledge file,
   1 dry-run documenté en vault audit-trail.
4. **Observabilité 30 jours** — métriques : nb invocations (cible ≥ 3),
   qualité output FR (binaire), régression brand voice (binaire).
5. **Décision T+30** — gate explicite : OK → ADR d'extension (1 PR par
   skill 🟢 restant) | KO → revert PR pilote + `npx skills remove` + close ADR.

Le cycle est **strict-1-skill-à-la-fois** post-pilote. Aucun batch.

### D3. Skill pilote sélectionné : `customer-research`

Critères empiriques de sélection :

- **Méthodologie pure** (interviews, JTBD, synthèse) — aucune génération de
  copy → risque FR/EN nul.
- **Aucun prérequis backend manquant** (vs `email-sequence` qui exige module
  email inexistant).
- **Comble un blocage gouvernance** : alimente la maturation de
  `canon-mirrors/marketing-voice.md` (status `proposed` → `accepted`)
  qui souffre actuellement d'un défaut de research underpinning.
- **Output documentaire** QA-able manuellement — boucle de validation simple.
- Démontre le pattern wrapper sur le cas le plus simple avant extension.

### D4. Skills explicitement bannis (anti-régression)

Les 17 skills suivants ne doivent **jamais** être adoptés via ce pattern,
quelle que soit l'évolution future. Toute PR les introduisant doit être
refusée par revue.

| Bannissement | Raison |
|---|---|
| `seo-audit` | Doublon : `seo-batch/seo-gamme-audit` + `backend/src/modules/seo-monitoring/audit-findings*` |
| `schema-markup` | Doublon : `seo-generator.service.ts` + `dynamic-seo-v4` (JSON-LD industrialisé) |
| `site-architecture` | Doublon : `internal-linking` + `sitemap v10` (10 variants canon) |
| `ai-seo` | Doublon : `seo-batch/seo-content-architect` + chain R6/R7/R8 (ADR-047, ADR-055) |
| `copywriting` | Conflit canon : `multi-channel-copywriter` + `brand-compliance-gate` (ADR-036) |
| `copy-editing` | Conflit canon : `brand-compliance-gate` + `seo-batch/content-quality-gate` |
| `social-content` | Doublon : `marketing/services/social-hub` + GBP via `local-business-agent` (ADR-036, ADR-038) |
| `content-strategy` | Doublon : `seo-batch/seo-content-architect` + `pipeline-orchestrator` + content-roadmap |
| `marketing-ideas` | Doublon : `marketing-lead-agent.md` (ADR-038) + briefs orchestration |
| `product-marketing-context` | Doublon : `canon-mirrors/marketing-voice.md` + `.claude/knowledge/modules/marketing.md` |
| `paywall-upgrade-cro` | Hors modèle : commerce pièces, pas SaaS |
| `revops` | Hors modèle : skill orienté SaaS B2B inadapté |
| `sales-enablement` | Hors organisation : pas d'équipe sales à équiper |
| `pricing-strategy` | Hors méthode : pricing data-driven SQL, pas stratégie produit séparée |
| `aso-audit` | Hors scope : pas d'app mobile actuellement |
| `co-marketing` | Hors phase : pas de signal partenaire à 2026-05-09 |
| `community-marketing` | Hors stratégie : pas de communauté à animer |
| `video` | Hors roadmap : aucun chantier vidéo planifié |

### D5. Anti-patterns explicites (codifiés)

Les pratiques suivantes constituent du bricolage et sont interdites :

- **Bulk install** : `npx skills add coreyhaines31/marketingskills` sans
  drapeau `--skill <NAME>` est interdit.
- **Fork local** des SKILL.md upstream pour FR-isation (drift permanent).
- **Patch upstream** local de tout fichier sous `.agents/skills/<skill>/`
  (bypass de la supply chain Anthropic Skills).
- **Skill custom clone** d'un skill upstream sous une autre étiquette
  (réinvention non-factorisée).
- **Batch multi-skills** dans une PR pilote ou d'extension (1 skill = 1 PR).
- **Adoption de skill 🔴** (cf. D4) sous prétexte d'évolution upstream.

### D6. Branchement gouvernance existante

Le pattern wrapper canon-bound s'inscrit dans la même famille que les
ADR canon en place :

- **ADR-036** (marketing operating layer) : brand voice + 3 agents G1.
  Tout wrapper de skill marketing référence `canon-mirrors/marketing-voice.md`
  dans son frontmatter.
- **ADR-038** (marketing agent naming canon) : `MarketingRoleId` Zod.
  Wrappers concernant les rôles marketing valident contre cet enum.
- **ADR-039** (wiki frontmatter Zod canon) : précédent du pattern
  canon-bound documentaire.
- **ADR-054** (audit-trail convention) : tout ADR destiné au merge génère
  audit-trail (appliqué à la présente).

## Consequences

### Positives

- **Adoption mesurable** d'un repo tiers à grande valeur ajoutée
  méthodologique sans dette de fork ni régression canon.
- **Réversibilité** garantie : `npx skills remove` + `git revert` rollback
  complet en < 15 min.
- **Boucle empirique** : chaque skill candidat passe une fenêtre 30j de
  validation avant extension — pas de big-bang.
- **Documentation exécutable** : le wrapper local sert d'ancrage canon FR
  réutilisable sur d'autres repos de skills tiers à venir.

### Négatives / coûts

- Chaque skill adopté ajoute **1 wrapper SKILL.md à maintenir** (≤ 30 lignes).
  Coût estimé : ~5 min/skill/release upstream majeure.
- **Latence d'adoption** : 30j minimum entre pilote et extension. Skills
  utiles peuvent attendre 30-60j avant d'être disponibles.
- **Asymétrie versions** : si l'upstream introduit une rupture API entre
  releases, le wrapper doit être ajusté. Mitigation : `.agents/skills.lock.json`
  pin SHA, upgrade explicite via PR dédiée.

### Neutres

- Aucun impact runtime backend (skills = couche méthodologique pour
  agents Claude Code, pas code exécuté en prod).
- Aucun impact CI/CD (les skills ne sont pas exécutés par les workflows GHA).

## Validation

Cette ADR est `proposed`. Elle passe `accepted` après :

1. Merge de cette PR vault sur `ak125/governance-vault@main` (commit signed G3).
2. Audit-trail entry présente : `ledger/audit-trail/2026-05-09-adr-057-marketingskills-adoption-pattern.md`.
3. Pas de collision de numéro (vérifié 2026-05-09 : ADR-056 R7 occupé,
   trous 051/052/054 sur drafts ouverts non-mon-scope).

Activation du pattern (PR pilote monorepo) sera bloquée tant que :

- La branche `feat/seo-v9-r7-router-wire` n'est pas mergée sur `main`.
- Cette ADR n'est pas `status: accepted`.

## References

- Plan source : `/home/deploy/.claude/plans/verifier-skip-to-jaunty-zebra.md`
- Repo upstream : `https://github.com/coreyhaines31/marketingskills` (v1.10.0)
- ADR-036 : `ADR-036-marketing-operating-layer.md`
- ADR-038 : `ADR-038-marketing-agent-naming-canon.md`
- ADR-039 : `ADR-039-wiki-frontmatter-zod-canon.md`
- ADR-054 : `ADR-054-audit-trail-convention.md` (PR vault #242, en cours)
- Mémoires DEV invoquées : `feedback_french_only_for_content.md`,
  `feedback_canon_rule_live_iff_adr_accepted.md`,
  `feedback_branch_scope_discipline.md`,
  `feedback_plugin_activation_request_allowed.md`,
  `feedback_no_questionnaire_propose_best.md`,
  `feedback_decision_must_be_signal_proven_not_intuited.md`,
  `feedback_seo_methodology_canon_20260506.md` (règle experimentation-first),
  `feedback_no_overclaim_security_words.md`.
