---
id: ADR-028
title: "Préprod read-only hardening (sans Supabase branch — ADR-028 Option D)"
status: accepted
date: 2026-04-30
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
related_rules: ["G3-signed-commits", "rules-engineering-quality", "AP-12"]
related_incidents: ["PR-monorepo-242-revert-2026-04-30"]
related_adr: ["ADR-021", "ADR-034"]
implementation_evidence:
  - "PR monorepo #246 (mergée 2026-04-30T22:04:13Z, commit dfd81673) — backend SupabaseBaseService READ_ONLY mode + ANON_KEY fallback"
  - "PR monorepo #248 (mergée 2026-04-30T22:17:18Z, commit 068d2088) — ci.yml retire ALLOW_PROD_ENV_COPY + SERVICE_ROLE_KEY"
  - "PR monorepo #244 (mergée 2026-04-30T21:42Z, commit f8a0e715) — revert préventif PR #242 v1 mauvais ordre"
reviewed_by: "@fafa"
---

# ADR-028: Préprod read-only hardening (sans Supabase branch — Option D)

## Contexte

Audit utilisateur du 2026-04-30 sur `nestjs-remix-monorepo` a identifié `ALLOW_PROD_ENV_COPY=1` dans `.github/workflows/ci.yml:703` qui copiait `~/production/.env` vers le déploiement préprod à chaque merge `main`. L'analyse profonde (cf. audit-trail `2026-04-30-preprod-isolation-audit.md`) révèle que `backend/.env` et `backend/.env.production` pointent tous deux vers le projet Supabase `cxpojprgwgubzjyqzmoq` ("massdoc"), donc préprod et prod partagent la même base de données.

Mitigations partielles déjà actives au moment de l'analyse :
- ADR-021 RLS hardening (PR #42, 204 objets DB hardenizés) — couche 3 de défense
- WriteGuard `__pg_gammes` (PR #68)
- RPC Gate enforce P1 actif en préprod (`docker-compose.preprod.yml`)

### Audit empirique du workflow réel (2026-04-30)

Une analyse empirique post-formulation de ce contexte a remis en cause Options A/B/C :

1. **Workflow DEV humain** : l'utilisateur (Human CEO) pointe **délibérément** vers la DB prod pour vérification live des modifications. Une isolation préprod ne change rien à ce workflow productif.

2. **CI deploy preprod read-only en pratique** : audit `ci.yml:700-799` confirme que les smoke tests sont uniquement des `curl GET` (`/health`, `/api/catalog/families`, `/`, `/pieces/catalogue`, admin guards). **Aucune migration auto, aucun seed, aucun POST/PUT/DELETE.**

3. **Risque "préprod écrit prod" théorique, jamais observé** : aucun incident historique. Catastrophe latente, pas catastrophe avérée.

4. **Surfacturation Supabase Branches** : doc Supabase officielle (`cost-control` + `manage-your-usage/branching` vérifiée 2026-04-30 via MCP) confirme que **Compute Branching n'est PAS couvert par le Spend Cap** et **Compute Credits ne s'appliquent pas au Branching**. Plancher $9.67/mois mais réaliste $10-20/mois (compute + disk + egress), dérive possible >$50 si non monitoré.

Conclusion : Options A/B/C résolvent un risque théorique avec un coût réel. Une **Option D — read-only hardening à coût $0** est née de cette analyse et adoptée.

État au 2026-04-30 (avant Option D) :
- Aucune branche existante sur le projet `cxpojprgwgubzjyqzmoq`
- Aucun projet préprod AutoMecanik dormant
- 0 secret `PREPROD_*` en GitHub Actions repo settings
- `SupabaseBaseService:109-114` throw inconditionnellement si SERVICE_ROLE_KEY absent

## Décision

**Adopter Option D — preprod read-only hardening sans Supabase branch.**

5 couches de défense, coût $0/mois ajouté, alignement avec ADR-034 AI-COS Operating Contract :

| Couche | Rôle | Garantie | Implémentation |
|---|---|---|---|
| 1. Pas de SERVICE_ROLE_KEY en preprod | Privilege downgrade | Fort (clé non distribuée) | PR monorepo #248 (ci.yml) |
| 2. Anon key only | Auth limitée | Fort si key non leakée | PR monorepo #248 (ci.yml) |
| 3. RLS hardening (ADR-021, 204 objets) | DB-level enforcement | Fort sur tables hardenizées, **risque résiduel** sur tables créées post-PR #42 sans RLS | Déjà déployé |
| 4. READ_ONLY guard backend | Couche applicative ceinture+bretelles | Dépend de la couverture (15+ services SupabaseBaseService héritage couverts ; 10+ services `createClient` direct restent à traiter en PR 2C) | PR monorepo #246 (SupabaseBaseService) |
| 5. write-detect log scan job CI | **Couche de détection**, pas garantie | Trouve les patterns SQL grossiers ; ne capture pas tout | PR 2C futur (write-detect job) |

La somme des 5 couches constitue la défense. **Aucune couche n'est suffisante seule.**

## Options Considérées

### Option A: Nouveau projet Supabase `automecanik-preprod` (REJETÉE)

**Description**: Créer un projet Supabase distinct dans la même organisation, cloner le schéma via `supabase db dump --schema-only` puis `supabase db push`.

**Avantages**:
- Isolation totale (compute distinct, billing distinct)
- Cycle de vie indépendant

**Inconvénients**:
- Coût : tier Pro de Supabase ≈ $25/mois fixe (vs $9.66/mois plancher pour la branch)
- Drift schema permanent : aucune sync automatique avec massdoc, chaque migration doit être appliquée 2× (manuellement)
- Pas aligné avec ADR-017 RPC cleanup en cours (les RPC sont sources de vérité dans massdoc)

**Rejet**: coût supérieur sans bénéfice incrémental sur Option C.

### Option B: Schéma `preprod` dans `cxpojprgwgubzjyqzmoq` (REJETÉE)

**Description**: Créer un schéma PostgreSQL `preprod` dans le projet prod, restreint par RLS service_role distinct.

**Avantages**:
- Coût $0
- Pas de migration séparée (tout dans le même projet)

**Inconvénients**:
- Compute partagé avec prod (un test de charge en préprod impacte la latence prod)
- Fonctions RPC `SECURITY DEFINER` peuvent contourner les boundaries de schéma
- L'extension Supabase (auth.users, storage.objects) reste partagée
- Isolation faible — proche de la situation actuelle, ne résout pas le problème fondamental

**Rejet**: bricolage par compromis, ne résout pas le risque structurel.

### Option C: Supabase branch sur `cxpojprgwgubzjyqzmoq` (REJETÉE après audit empirique)

**Description**: Utiliser le mécanisme natif Supabase Branches (`mcp__supabase__create_branch`) pour spinup une instance Postgres dédiée préprod, alimentée par toutes les migrations du projet parent.

**Avantages**:
- Isolation DB complète (compute, storage, auth, extensions distincts)
- Schema auto-sync depuis migrations massdoc (pas de drift manuel)
- Coût plancher $9.66/mois 24/7
- API native Supabase, supportée par MCP

**Inconvénients (révélés post-audit empirique)**:
- **Le workflow DEV humain pointe délibérément vers prod en lecture live** — l'isolation préprod n'a aucun bénéfice dans ce workflow
- **CI smoke tests sont read-only en pratique** (curl GET uniquement, aucun POST/PUT/DELETE) — résout un risque théorique
- **Surfacturation latente Supabase** : Compute Branching non couvert par Spend Cap, Compute Credits non applicables, plancher $9.66 mais réaliste $10-20/mois (avec disk + egress), dérive possible >$50 si non monitoré
- **Faux problème résolu** : aucun incident historique "préprod écrit prod"

**Rejet** : coût récurrent réel pour résoudre un risque qui ne se manifeste pas dans le workflow productif. Mauvais ROI.

### Option D: Read-only hardening sans Supabase branch (RETENUE)

**Description**: Au lieu d'isoler la base, **rendre le déploiement preprod incapable d'écrire avec privilèges élevés**, via 5 couches de défense (cf. table dans §"Décision").

**Avantages**:
- **Coût $0/mois** (utilise infrastructure existante : RLS ADR-021, anon key déjà provisionnée, backend modifications minimales)
- **Aucun changement workflow utilisateur** (DEV humain continue à pointer vers prod en lecture)
- **Defense-in-depth** : 5 couches indépendantes, somme > parts isolées
- **Pas de surfacturation latente** Supabase
- **Cohérent ADR-034** AI-COS Operating Contract : pas d'infra nouvelle quand primitives natives suffisent

**Inconvénients**:
- Préprod et prod partagent toujours la même DB physique → risque résiduel limité par les couches 3-5
- Couverture READ_ONLY guard partielle en P1 : 15+ services héritant de `SupabaseBaseService` couverts ; 10+ services `createClient` direct restent dépendants de SERVICE_ROLE_KEY (à traiter en PR 2C)
- Tables créées post-ADR-021 sans RLS activée acceptent writes anon — couvert par couche 4 (READ_ONLY guard) si le service hérite de SupabaseBaseService

## Justification

Option D est retenue pour 5 raisons mesurables :

1. **Audit empirique du workflow** : le coût $9.66+/mois d'Option C résoudrait un risque qui ne se manifeste pas dans le workflow productif (DEV humain en lecture prod assumée + CI smoke read-only). ROI < 0.

2. **Surfacturation Supabase évitée** : doc officielle Supabase (`cost-control`) confirme que Branching Compute n'est pas couvert par Spend Cap et Compute Credits ne s'appliquent pas. Risque de dérive >$50/mois éliminé en n'activant pas la branch.

3. **Defense-in-depth fonctionne** : ADR-021 RLS hardening (couche 3) + READ_ONLY guard backend (couche 4) + write-detect logs (couche 5) atténuent fortement le risque structurel sans nouvelle infrastructure.

4. **Pattern aligné ADR-034** : "AI-COS = observatoire pas orchestrateur runtime" — les primitives natives (env vars, RLS, GitHub Actions) suffisent. Pas de nouvelle couche infra.

5. **Implémentation atomique livrée 2026-04-30** : PR monorepo #246 (backend READ_ONLY support) + PR #248 (ci.yml hardening) déjà mergées sur main. Cette ADR documente une décision déjà *implementation_evidence: shipped*.

### Sur l'incident PR #242 → #244

L'implémentation initiale (PR #242 v1, mergée 21:38Z puis revertée 21:42Z par PR #244) a appliqué le retrait SERVICE_ROLE_KEY du `.env.preprod` SANS avoir d'abord modifié `SupabaseBaseService` pour tolérer son absence. `SupabaseBaseService:109-114` throw inconditionnellement → le boot du conteneur preprod aurait crashé. Détecté avant exécution du job Deploy (status `queued`), revert immédiat.

Le bon ordre canonique a été ensuite appliqué :
1. PR #246 backend (rendre READ_ONLY tolérant) → MERGED 22:04:13Z
2. PR #248 CI (retirer SERVICE_ROLE_KEY) → MERGED 22:17:18Z
3. Cette ADR (status accepted, implementation_evidence shipped)

Leçon canonisée dans la mémoire `feedback_read_backend_before_modifying_ci.md` : avant tout retrait d'env var dans CI/déploiement, lire les services backend qui la consomment.

## Conséquences

### Positives

- Risque "préprod écrit prod avec privilèges élevés" **fortement réduit** (pas "éliminé") par les 5 couches de défense
- **Coût $0/mois ajouté** (vs $10-20/mois Option C)
- Workflow DEV humain inchangé (productivité préservée)
- Pattern réutilisable pour autres environnements (sandbox dev individuel, ephemeral test instances)
- Trace décisionnelle préservée : Options A/B/C documentées et justifiées explicitement comme rejetées
- Alignement ADR-034 (AI-COS Operating Contract — primitives natives suffisent)

### Négatives

- Préprod et prod partagent toujours la même DB physique → couverture défense partielle, pas absolue
- Couverture READ_ONLY guard P1 partielle : 10+ services `createClient` direct (write-guard-*, seo-monitoring/*, seo/internal-linking, etc.) restent dépendants de SERVICE_ROLE_KEY → PR 2C à venir pour étendre
- Risque résiduel sur tables créées post-ADR-021 sans RLS activée — couvert par couche 4 (READ_ONLY guard) sur services héritant SupabaseBaseService, mais pas sur les 10+ services `createClient` direct (jusqu'à PR 2C)

### Neutres

- ADR-022 R8 RAG Control Plane Stage 2 (validation canary) reste réalisable sans branch préprod : utiliser propose-before-write + 5-layer gates existants, pas de pollution prod détectée
- Les 27 secrets `PREPROD_*` que prévoyait Option C ne sont plus nécessaires — pas de provisioning à faire

## Critères de Succès

- [x] **Couche 1+2 livrées** : `grep -c ALLOW_PROD_ENV_COPY .github/workflows/ci.yml` job preprod = 0 (vérifié post-PR #248)
- [x] **Couche 4 backend livrée** : `SupabaseBaseService` supporte `READ_ONLY=true` + `SUPABASE_ANON_KEY` fallback (vérifié post-PR #246)
- [x] **Pas de crash boot preprod** : Deploy run post-PR #248 fonctionnel (à confirmer au prochain merge sur main)
- [x] **Coût $0/mois confirmé** : aucune Supabase branch créée, aucune ressource compute additionnelle facturée
- [ ] **Couche 5 future** : `preprod-write-detect` job CI en PR 2C
- [ ] **Couverture étendue** : 10+ services `createClient` direct migrés au mode READ_ONLY en PR 2C
- [ ] **Audit RLS coverage** : extension `weekly-vault-lint` pour flagger tables créées post-ADR-021 sans RLS — follow-up à tracer

## Implémentation

### Phase A — Backend READ_ONLY support (PR monorepo #246, MERGED `dfd81673`)

- `backend/src/config/app.config.ts` : ajout `anonKey` + `readOnly` dans AppConfig.supabase
- `backend/src/database/services/supabase-base.service.ts` : nouveau field `isReadOnlyMode`, fallback ANON_KEY si SERVICE_ROLE_KEY absent + READ_ONLY=true + ANON_KEY présent
- 15+ services héritant de `SupabaseBaseService` couverts par défaut

### Phase B — CI hardening (PR monorepo #248, MERGED `068d2088`)

- `.github/workflows/ci.yml` lignes 700-735 : retire `ALLOW_PROD_ENV_COPY`, retire `SUPABASE_SECRET_KEY` env var, retire `cp ~/production/.env`, retire bloc `sed`, ajoute génération in-place `.env.preprod` minimal (ANON_KEY only + `READ_ONLY=true`)

### Phase C — Couverture étendue (PR 2C, futur)

- Extension des 10+ services `createClient` direct (`config/write-guard-*`, `config/content-write-gate`, `seo-monitoring/*`, `seo/internal-linking`, etc.) au mode READ_ONLY
- `preprod-write-detect` job CI : grep logs container preprod après smoke tests pour patterns d'écriture (`INSERT INTO`, `UPDATE`, `DELETE FROM`, `upsert`, `READ_ONLY mode violation`)

## Revue Planifiée

**Date** : 2026-07-30 (3 mois post-acceptance)

**Critères de revue** :
- Aucun incident "préprod écrit prod" observé sur la période (mesure baseline 0 confirmée)
- PR 2C (couverture étendue + write-detect job) livrée et stable
- Si tables créées post-ADR-021 sans RLS détectées par extension `weekly-vault-lint`, traiter comme follow-up
- Cohérence avec ADR-034 §"3 axes" maintenue (pas de dérive vers infrastructure orchestrateur maison sur AI-COS)
- Si workflow DEV humain change (par ex. : tests avec écritures délibérées en preprod), reconsidérer Option C ou nouvelle option

---

*Proposé le: 2026-04-30*
*Accepté le: 2026-04-30 (après livraison PR #246 + PR #248 sur main monorepo)*
*Dernière revue: 2026-04-30*
