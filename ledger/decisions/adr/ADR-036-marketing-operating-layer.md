---
id: ADR-036
title: "Marketing Operating Layer — 3 agents G1 (LEAD/LOCAL/RETENTION) + extension OperatingMatrixService + business_unit séparé ECOMMERCE/LOCAL/HYBRID"
status: proposed
date: 2026-04-30
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "Q1", "Q2", "AI2", "AI4", "AP-01", "AP-10"]
related_incidents: []
related_adr: ["ADR-013", "ADR-015", "ADR-025", "ADR-031"]
---

# ADR-036: Marketing Operating Layer

## Contexte

Au 2026-04-30, AutoMecanik exploite deux entités business distinctes mais
**non séparées techniquement** dans le monorepo :

1. **E-commerce national** (`automecanik.com`) — site SEO, ventes en ligne,
   conversion = achat. Domaine canonique vérifié dans
   `backend/src/config/site.constants.ts` (`SITE_ORIGIN`).
2. **Magasin physique 93** — adresse Pavillons-sous-Bois (RCS Bobigny),
   trafic local, GBP, conversion = appel/visite/devis. Nom légal exact
   à confirmer (cf. décision ouverte §"Décisions ouvertes").

### Audit empirique (session 2026-04-30)

Vérifications grep sur `/opt/automecanik/app` :

| Élément | État | Évidence |
|---|---|---|
| Module marketing backend | **Existe** : 9 services NestJS opérationnels (`multi-channel-copywriter`, `weekly-plan-generator`, `publish-queue`, `brand-compliance-gate`, `utm-builder`, `marketing-content-roadmap`, `marketing-data`, `marketing-hub-data`, `marketing-backlinks`) | `backend/src/modules/marketing/` |
| Routes admin marketing | **Existent** : `admin.marketing._index.tsx`, `admin.marketing.tsx`, `admin.marketing.social-hub.posts.tsx`, `admin.marketing.backlinks.tsx`, `admin.marketing.content-roadmap.tsx` | `frontend/app/routes/` |
| Concept `business_unit` séparant ECOMMERCE/LOCAL | **Inexistant** | grep `business_unit\|store_type\|enseigne\|raison_sociale` = 0 hit |
| Champ `marketing_consent_at` (RGPD) | **Inexistant** | grep `email_opt_in\|marketing_consent\|sms_opt_in\|consent_marketing` = 0 hit |
| Providers marketing externes (GBP, Mailjet, Brevo, Twilio, Meta) | **Aucun branché** | grep `MARKETING_\|MAILJET_\|BREVO_\|TWILIO_\|META_\|FB_\|GBP_` dans `.env.example` = 0 hit |
| OperatingMatrixService | **Introduit** sur branche `feat/seo-agent-operating-matrix` (commit `3985264b`, PR #222 OPEN) | `backend/src/config/operating-matrix.service.ts` |
| Pattern canon-publish vault → monorepo | **Éprouvé** sur AEC (`agent-exit-contract.md` + workflow `agent-exit-contract-hash.yml`) | `governance-vault/.github/workflows/canon-publish.yml` |

### Anti-patterns à éviter (vérifiés contre incidents passés)

- **Dupliquer le module marketing backend** sous prétexte d'agentification (3 des 7
  agents proposés initialement dupliquent les services existants). Viole Q1
  (no bricolage) et Q2 (grep-first).
- **Inventer un schéma Paperclip** (`activation_mode`, `write_scope` n'existent pas).
  Viole feedback `feedback_verify_existing_first.md` (incidents `GOOGLE_SA_*`
  inventé en avril 2026).
- **Stocker les briefs en `.md` flottants** dans `automecanik-wiki/`. Viole le
  principe ADR-031 (5 entity_types figés : `gamme | vehicle | constructeur | support | diagnostic`).
- **Mélanger ECOMMERCE et LOCAL** sans `business_unit` explicite — risque
  cannibalisation SEO + incohérence brand entre site national et magasin local.
- **Lire le filesystem `governance-vault/` depuis le runtime backend** — fragile
  en prod (vault accessible que sur DEV VPS), brise la séparation 3-VPS (ADR-012).

## Décision

Création d'une **Marketing Operating Layer** = extension du pattern
`OperatingMatrixService` (ADR-025-style), composée de :

### 1. Trois agents G1 (lifecycle ADR-013) — workspace dédié

```
workspaces/marketing/.claude/agents/
├── marketing-lead-agent.md       (coordination hebdo, lit ECOMMERCE+LOCAL, exécute aucun)
├── local-business-agent.md       (LOCAL only, refus DTO si tente ECOMMERCE)
└── customer-retention-agent.md   (ECOMMERCE primary, HYBRID autorisé sur clients zone 93)
```

Pas d'extension `workspaces/seo-batch/.claude/agents/` (cohérence dual-workspace
pattern PR #200, scope SEO ≠ scope marketing).

### 2. Backend NestJS = moteur unique d'exécution

Les agents **consomment** `backend/src/modules/marketing/` (9 services existants),
ne le réécrivent pas. Les services marketing sont étendus, pas dupliqués.

| Besoin | Service réutilisé |
|---|---|
| Génération copy multi-canal | `multi-channel-copywriter.service.ts` |
| Calendrier éditorial | `weekly-plan-generator.service.ts` |
| Validation brand voice | `brand-compliance-gate.service.ts` (étendu — voir §"Brand voice canon") |
| UTM tracking | `utm-builder.service.ts` |
| Reporting | `marketing-data.service.ts` |
| Staging + audit publication | `publish-queue.service.ts` |

### 3. Données structurées (4 changes DB Phase 1)

```sql
-- (1) __marketing_brief : canal d'échange agent → engine
CREATE TABLE __marketing_brief (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id text NOT NULL,
  business_unit text NOT NULL CHECK (business_unit IN ('ECOMMERCE','LOCAL','HYBRID')),
  channel text NOT NULL CHECK (channel IN ('gbp','local_landing','website_seo','email','sms','social_facebook','social_instagram')),
  payload jsonb NOT NULL,
  conversion_goal text NOT NULL CHECK (conversion_goal IN ('CALL','VISIT','QUOTE','ORDER')),
  cta text NOT NULL,
  target_segment text NOT NULL,
  coverage_manifest jsonb NOT NULL,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','reviewed','approved','published','archived')),
  created_at timestamptz NOT NULL DEFAULT now(),
  reviewed_by text,
  reviewed_at timestamptz,
  CONSTRAINT marketing_brief_unit_channel_coherence CHECK (
    (business_unit = 'LOCAL'    AND channel IN ('gbp','local_landing','sms')) OR
    (business_unit = 'ECOMMERCE' AND channel IN ('website_seo','email','social_facebook','social_instagram')) OR
    (business_unit = 'HYBRID')
  )
);

-- (2) __marketing_feedback : boucle fermée mesurable
CREATE TABLE __marketing_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id uuid NOT NULL REFERENCES __marketing_brief(id),
  impressions int DEFAULT 0,
  clicks int DEFAULT 0,
  calls int DEFAULT 0,
  visits int DEFAULT 0,
  quotes int DEFAULT 0,
  orders int DEFAULT 0,
  revenue_cents bigint DEFAULT 0,
  measured_at timestamptz NOT NULL DEFAULT now(),
  source text NOT NULL CHECK (source IN ('manual_admin','ga4','gbp_api','mailjet','twilio','phone_tracker','meta_pixel','facebook_insights')),
  created_at timestamptz NOT NULL DEFAULT now()
);

-- (3) __retention_trigger_rules : règles métier data-driven (cycle véhicule)
CREATE TABLE __retention_trigger_rules (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  category text NOT NULL,
  min_days_since_last_order int NOT NULL,
  max_days_since_last_order int NOT NULL,
  trigger_template text NOT NULL,
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO __retention_trigger_rules (category, min_days_since_last_order, max_days_since_last_order, trigger_template) VALUES
  ('freinage', 180, 365, 'controle_freinage'),
  ('vidange', 270, 365, 'rappel_vidange'),
  ('batterie', 1095, 1825, 'remplacement_batterie'),
  ('filtres_habitacle', 365, 540, 'changement_filtre_habitacle');

-- (4) users.marketing_consent_at : RGPD non-négociable
ALTER TABLE users ADD COLUMN marketing_consent_at timestamptz NULL;
CREATE INDEX users_marketing_consent_idx ON users (marketing_consent_at)
  WHERE marketing_consent_at IS NOT NULL;
-- Backfill = NULL (consentement non rétroactif)
```

### 4. OperatingMatrixService étendu

```typescript
// backend/src/config/operating-matrix.types.ts
export enum Module {
  SEO = 'SEO',
  MARKETING = 'MARKETING', // ← nouveau
}

// invariant MARKETING
{
  module: Module.MARKETING,
  subdomains: ['ECOMMERCE', 'LOCAL'],
  requires: ['brand_compliance_gate', 'aec_manifest', 'conversion_goal_defined', 'business_unit_defined'],
  agents: ['marketing-lead-agent', 'local-business-agent', 'customer-retention-agent'],
}
```

Tout brief sans `conversion_goal`, sans `business_unit`, ou ne passant pas
`brand-compliance-gate` est rejeté en amont par l'invariant matrix.

### 5. Brand voice canon (sync canon-publish)

Source unique = `governance-vault/ledger/rules/rules-marketing-voice.md` (PR
séparée mergée Phase 0). Sync vers monorepo via le workflow existant
`canon-publish.yml`, qui ouvre une PR auto copiant la rule sous
`.claude/rules/marketing-voice.md` + écrit le hash SHA-256 dans
`99-meta/canon-hashes.json` clé `marketing_voice`.

Le `brand-compliance-gate.service.ts` lit la copie locale (jamais
le filesystem du vault — viole ADR-012 séparation 3-VPS).

CI monorepo `marketing-voice-hash.yml` (miroir de `agent-exit-contract-hash.yml`)
vérifie hash drift sur chaque PR. Fail = blocage merge.

### 6. RGPD non-négociable

Aucun brief `business_unit IN ('ECOMMERCE','HYBRID')` ciblant des emails/SMS
ne peut être généré si `users.marketing_consent_at IS NULL`. Filtré en triple :

- DTO Zod côté NestJS (refinement)
- Query SQL agent (`WHERE marketing_consent_at IS NOT NULL`)
- Test négatif obligatoire (Phase 1 verification)

### 7. Phasage strict

| Phase | Scope | Durée |
|---|---|---|
| **Phase 0** | Gouvernance & socle (ADR-036 + rule + runbook + workspace + workflow CI) | J+0 → J+5 |
| **Phase 1** | Pilote LOCAL-BUSINESS (1 agent, table briefs, dashboard, validation humaine) | J+5 → J+15 |
| **Phase 2** | LEAD + RETENTION (ajout 2 agents, retention trigger rules, scoring config) | J+15 → J+30 |
| **Phase 3** | Branchement providers externes (GBP API, Mailjet, Twilio) | Différé hors MVP — ADR séparée par provider |

## Conséquences

### Positives

- **Zéro duplication** avec le module marketing backend existant (9 services
  réutilisés, pas réécrits).
- **Séparation business_unit** anticipe la divergence ECOMMERCE/LOCAL avant
  qu'elle crée des incohérences brand (cannibalisation SEO, NAP incohérent).
- **Pattern OperatingMatrix réutilisé** = cohérence avec l'investissement
  ADR-025 récent (SEO Department) + snapshot CI-safe SHA-256 hashable.
- **Pattern canon-publish réutilisé** = cohérence avec AEC, pas de nouveau
  mécanisme à inventer (Q1 no bricolage).
- **RGPD compliant by design** = consentement explicite obligatoire avant tout
  envoi, défense en profondeur (DTO + SQL + test).
- **AEC compliant** = chaque brief a un `coverage_manifest` JSONB obligatoire.

### Négatives / coûts

- **Migration DB** : 4 changes Phase 1 (3 nouvelles tables + ALTER users).
  Validés via Supabase MCP `apply_migration` sur DEV uniquement (pas de prod
  Phase 1).
- **Décision ouverte bloquante** : nom légal exact magasin 93 doit être figé
  avant que `local_canon.validated=true` puisse être posé dans
  `rules-marketing-voice.md` — sans ça, briefs LOCAL bloqués par
  `brand-compliance-gate` (verdict `local_canon_unvalidated`).
- **Pré-requis** : merge PR #222 (`feat/seo-agent-operating-matrix`) requis
  avant Phase 1 (extension OperatingMatrixService).
- **Pas de provider externe Phase 1-2** : briefs produits, validés humain,
  publiés manuellement (copy-paste GBP/email). Phase 3 = automatisation.

### Anti-patterns explicitement écartés (20)

1. Pas de schéma Paperclip inventé.
2. Pas de `.md` flottants pour les briefs.
3. Pas de duplication backend marketing/.
4. Pas de nouvelle ENV var sans grep préalable.
5. Pas d'amendement ADR-031 inutile.
6. Pas d'agent qui publie (validation humaine AI4).
7. Pas de branche partagée avec SEO.
8. Pas de sleep en boucle pour attendre CI.
9. Pas d'auto-escalation après un seul GO.
10. Pas de provider externe au MVP.
11. Pas de prédiction LLM de conversion (`expected_conversion`).
12. Pas de constantes magiques en code (pondération scoring en config).
13. Pas de `if/throw` ad-hoc pour valider (DTO Zod + CHECK SQL).
14. Pas de règles métier hardcodées (`__retention_trigger_rules` data-driven).
15. Pas de « trigger campaign » auto (génération brief uniquement).
16. Pas de fusion ECOMMERCE/LOCAL hors `business_unit='HYBRID'` strict.
17. Pas d'interdiction stricte au LEAD (coordonne, n'exécute pas).
18. Pas de brief RETENTION sans `marketing_consent_at NOT NULL` (RGPD).
19. Pas de canon vault lu directement par runtime backend (canon-publish only).
20. Pas de mélange marketing dans `workspaces/seo-batch/`.

## Plan de migration

### Phase 0 (J+0 → J+5) — bloquante

1. Pré-requis : merge PR #222 `feat/seo-agent-operating-matrix` sur main.
2. PR vault : ADR-036 + `rules-marketing-voice.md` + runbook
   `marketing-pilot-rollback.md` + mise à jour `99-meta/canon-hashes.json`.
3. Workflow vault `canon-publish.yml` exécuté → PR auto monorepo
   avec `.claude/rules/marketing-voice.md` (copie locale).
4. PR monorepo : workflow `marketing-voice-hash.yml` + scaffold
   `workspaces/marketing/{.claude/agents,.claude/skills,settings.json,README.md}`.
5. QTO Phase 1 désigné (mode dégradé CEO si pas désigné).

### Phase 1 (J+5 → J+15) — pilote LOCAL

1. Migration DB Phase 1 (4 changes) sur DEV via Supabase MCP.
2. `local-business-agent.md` créé dans `workspaces/marketing/.claude/agents/`.
3. Routine Paperclip `rt-local-gbp-week` (cron `0 9 * * 3`).
4. Extension `OperatingMatrixService` (ajout enum `MARKETING`).
5. Routes admin briefs/feedback créées + filtre `?unit=` dashboard.
6. Évaluation J+15 : nb briefs, validation rate, BLOCK rate, latence humaine.

### Phase 2 (J+15 → J+30) — LEAD + RETENTION

Ajout `marketing-lead-agent.md` + `customer-retention-agent.md` + routines
`rt-weekly-marketing-plan` + `rt-retention-monthly`. Promotion G1 → G2 si
critères ADR-013 satisfaits (14 jours observe, 0 incident, audit log clean).

### Phase 3 (différée hors MVP)

Branchement providers externes — ADR séparée par provider (Mailjet vs Brevo,
Twilio vs OVH SMS, GBP API).

## Validation

### Phase 0

- [ ] Pré-requis : `git log main --oneline | grep operating-matrix` retourne `3985264b`
- [ ] PR vault ADR-036 mergée et `accepted`
- [ ] PR vault `rules-marketing-voice.md` mergée avec `local_canon.validated=true`
- [ ] PR vault runbook `marketing-pilot-rollback.md` mergée
- [ ] PR vault `99-meta/canon-hashes.json` clé `marketing_voice` ajoutée
- [ ] Workflow `canon-publish.yml` exécuté → PR monorepo auto ouverte
- [ ] PR monorepo workflow `marketing-voice-hash.yml` mergée et CI verte
- [ ] Workspace `workspaces/marketing/` scaffold mergé
- [ ] QTO Phase 1 désigné (ou mode dégradé documenté)

### Phase 1

- [ ] Migration 4 changes appliquée sur DEV (Supabase MCP)
- [ ] Tests négatifs CHECK SQL : 4 INSERT invalides échouent
- [ ] Test RGPD négatif : query RETENTION sur `marketing_consent_at IS NULL` = 0 rows
- [ ] OperatingMatrix snapshot inclut `MARKETING` avec `requires` 4 items
- [ ] Agent dry-run produit ≥ 1 brief avec coverage_manifest AEC valide
- [ ] Smoke-test verrou LOCAL : retirer `local_canon.validated=true` → BLOCK systématique
- [ ] Test négatif HYBRID : sans `hybrid_reason` rejeté en amont DTO Zod
- [ ] Routes admin briefs/feedback fonctionnelles
- [ ] J+15 : rapport pilote livré

### Phase 2

- [ ] Snapshot OperatingMatrix : 3 agents marketing visibles, hash CI-safe stable
- [ ] Routine `rt-weekly-marketing-plan` produit un plan hebdo
- [ ] Routine `rt-retention-monthly` produit ≥ 4 briefs (1 par règle active)
- [ ] Critères ADR-013 G2 satisfaits

## Décisions ouvertes

1. **Nom légal exact du magasin physique 93** (raison sociale RCS Bobigny ?
   enseigne ?) — bloquant pour `local_canon.validated=true`.
2. **Email/SMS providers cibles Phase 3** : Mailjet vs Brevo vs SES ; Twilio
   vs OVH SMS. ADR séparé.
3. **Segments retention prioritaires** : (a) freinage > 6 mois, (b) panier
   abandonné < 14j, (c) clients livraison 93 → push retrait magasin (HYBRID).
   Tous filtrés `marketing_consent_at NOT NULL`.
4. **Téléphone tracking LOCAL** : numéro dédié magasin pour mesure auto
   `calls`, ou saisie manuelle Phase 1 (`source='manual_admin'`).
5. **QTO humain assigné** Phase 1 : métier marketing ? CEO ? Mode dégradé
   par défaut = CEO valide.
6. **UI consentement marketing** : compte création + page profil + checkout.
   À valider UX. Backfill = NULL (RGPD non rétroactif).

## Évolutions futures (hors scope MVP)

- **business_unit étendu** : `B2B`, `WHOLESALE`, `MARKETPLACE` futurs →
  ALTER CHECK + extension OperatingMatrix `subdomains` + nouvelle section
  brand voice.
- **Wiki `local/` 10 communes 93** : si gap qualité Phase 1, sourcing
  via ADR séparé (entité `local_zone` candidate à ADR-031 amendée).
- **`__brand_canon` table DB** : alternative au sync canon-publish si latence
  workflow CI bloquante. Pour l'instant pattern AEC suffit.

## Références

- [[ADR-013-agent-lifecycle]] — G1/G2/G3 governance des agents
- [[ADR-015-vault-single-source-of-truth]] — gouvernance canon vault
- [[ADR-025-seo-department-architecture]] — pattern modules + OperatingMatrix
- [[ADR-031-four-layer-content-architecture]] — raw/wiki/exports/consumers
- [[rules-agent-exit-contract]] — AEC v1.0.0 mandatory
- [[rules-ai-cos]] — AI2 (propose/décide), AI4 (QTO valide avant publication)
- [[rules-engineering-quality]] — Q1 (no bricolage), Q2 (grep-first)
- Plan rev 5 : `/home/deploy/.claude/plans/verifier-la-strategie-une-piped-hummingbird.md`
- PR monorepo cible : `feat/marketing-operating-layer` (à créer après merge PR #222)
- Pré-requis : PR #222 `feat/seo-agent-operating-matrix` (OperatingMatrixService)
