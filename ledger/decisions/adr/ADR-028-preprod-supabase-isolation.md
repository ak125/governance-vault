---
id: ADR-028
title: "Préprod Supabase isolation via branch (resoudre ALLOW_PROD_ENV_COPY)"
status: proposed
date: 2026-04-30
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G3-signed-commits, rules-engineering-quality]
related_incidents: []
reviewed_by: ""
---

# ADR-028: Préprod Supabase isolation via branch

## Contexte

Audit utilisateur du 2026-04-30 sur `nestjs-remix-monorepo` a identifié `ALLOW_PROD_ENV_COPY=1` dans `.github/workflows/ci.yml:703` qui copie `~/production/.env` vers le déploiement préprod à chaque merge `main`. L'analyse profonde (cf. audit-trail `2026-04-30-preprod-isolation-audit.md`) révèle un problème plus large : `backend/.env` et `backend/.env.production` pointent tous deux vers le projet Supabase `cxpojprgwgubzjyqzmoq` ("massdoc"), donc **préprod et prod partagent la même base de données**.

Mitigations partielles déjà actives :
- ADR-021 RLS hardening (PR #42, 204 objets DB hardenizés)
- WriteGuard `__pg_gammes` (PR #68)
- RPC Gate enforce P1 actif en préprod (`docker-compose.preprod.yml`)

Mais ces garde-fous ne remplacent pas une isolation DB réelle : tout service en préprod qui appelle `supabase.from('xxx').update()` avec service_role contourne RLS et écrit dans la DB de prod. Catastrophe latente sur les premiers tests d'écriture en préprod.

État au 2026-04-30 :
- Aucune branche existante sur le projet `cxpojprgwgubzjyqzmoq` (`mcp__supabase__list_branches → []`)
- Aucun projet préprod AutoMecanik dormant dans l'organisation `fezyshchnnrwwpnzbcwb` (4 projets, 3 hors scope, 1 INACTIVE)
- 0 secret `PREPROD_*` en GitHub Actions repo settings
- Coût Supabase branch : $0.01344/heure ≈ $9.66/mois si 24/7

## Décision

**Adopter Option C : créer une Supabase branch nommée `preprod` sur le projet `cxpojprgwgubzjyqzmoq`** comme instance de base de données dédiée à l'environnement préprod.

Toute la chaîne préprod (backend NestJS, jobs CI, workers, RAG ingest) utilisera les credentials de cette branche via les nouvelles variables `PREPROD_SUPABASE_URL`, `PREPROD_SUPABASE_SERVICE_ROLE_KEY`, `PREPROD_SUPABASE_ANON_KEY`, `PREPROD_DATABASE_URL` provisionnées en GitHub secrets.

`ALLOW_PROD_ENV_COPY` et la copie `cp ~/production/.env` sont retirés du workflow `.github/workflows/ci.yml` et remplacés par un rendu de template `.env.preprod.template` injecté à partir des secrets `PREPROD_*`.

## Options Considérées

### Option A: Nouveau projet Supabase `automecanik-preprod`

**Description**: Créer un projet Supabase distinct dans la même organisation, cloner le schéma via `supabase db dump --schema-only` puis `supabase db push`.

**Avantages**:
- Isolation totale (compute distinct, billing distinct)
- Cycle de vie indépendant

**Inconvénients**:
- Coût : tier Pro de Supabase ≈ $25/mois fixe (vs $9.66/mois pour la branch)
- Drift schema permanent : aucune sync automatique avec massdoc, chaque migration doit être appliquée 2× (manuellement)
- Pas aligné avec ADR-017 RPC cleanup en cours (les RPC sont sources de vérité dans massdoc)

### Option B: Schéma `preprod` dans `cxpojprgwgubzjyqzmoq`

**Description**: Créer un schéma PostgreSQL `preprod` dans le projet prod, restreint par RLS service_role distinct.

**Avantages**:
- Coût $0
- Pas de migration séparée (tout dans le même projet)

**Inconvénients**:
- Compute partagé avec prod (un test de charge en préprod impacte la latence prod)
- Fonctions RPC `SECURITY DEFINER` peuvent contourner les boundaries de schéma
- L'extension Supabase (auth.users, storage.objects) reste partagée
- Isolation faible — proche de la situation actuelle, ne résout pas le problème fondamental

### Option C: Supabase branch sur `cxpojprgwgubzjyqzmoq`

**Description**: Utiliser le mécanisme natif Supabase Branches (`mcp__supabase__create_branch`) pour spinup une instance Postgres dédiée préprod, alimentée par toutes les migrations du projet parent.

**Avantages**:
- Isolation DB complète (compute, storage, auth, extensions distincts)
- Schema auto-sync depuis migrations massdoc (pas de drift manuel)
- Coût maîtrisé : ~$9.66/mois 24/7, réductible via pause hors heures
- API native Supabase, supportée par MCP — aucun outillage custom
- Aligne avec ADR-017 RPC cleanup (les RPC migrent automatiquement vers la branch)

**Inconvénients**:
- Production data ne carry-over pas automatiquement (mais c'est un bénéfice pour préprod : pas de risque de leak data prod)
- Le cycle de vie de la branch est lié au projet parent (suppression du projet parent supprime la branch)
- Nécessite de re-seeder les tables non-migrations (ex: `kg_confidence_config`, `__quarantine_rules`) manuellement après création

## Justification

L'Option C est retenue pour 4 raisons :

1. **Isolation réelle, coût bas** : $9.66/mois est le prix marginal pour bloquer la classe d'incidents "préprod écrit en prod". 0 incident à amortir = ROI infini.
2. **Pas de drift schema** : la branch absorbe automatiquement les migrations massdoc. Évite le piège classique de l'environnement secondaire qui dérive du primaire et masque des bugs.
3. **Outillage natif** : `mcp__supabase__create_branch` + `reset_branch` + `merge_branch` couvrent tous les besoins opérationnels (provisionner, reset, promote schema changes preprod→prod via PR Supabase).
4. **Alignement gouvernance** : compatible avec ADR-021 RLS hardening, ADR-017 RPC cleanup, et le principe G2 (Zero Orphelin) — la branch est traçable dans la même org et les mêmes outils.

## Conséquences

### Positives

- Élimination du vecteur "préprod écrit en prod" (catastrophe latente fermée)
- Possibilité de tester migrations destructives en préprod sans risque (DROP TABLE, schema rebuild)
- Onboarding nouveau dev : un test e2e de bout en bout sans toucher prod
- Préparation infrastructure pour Stage 2 ADR-022 R8 RAG Control Plane (validation canary sur 10 modèles low-profile sans pollution prod)

### Négatives

- Coût mensuel récurrent ~$9.66 (acceptable, < 2 minutes de temps ingé/mois)
- Provisioning des 27 secrets `PREPROD_*` en GitHub Actions : action manuelle, ~30min
- Compte Paybox/SystemPay test à activer ou créer (dépend du contrat actuel)
- Première migration : ~5min pour créer la branch + sync ; le déploiement préprod doit attendre

### Neutres

- La branch capte automatiquement les migrations futures du projet parent — à documenter comme propriété attendue, pas comme magie
- Les vraies données de test (orders, customers fictifs) doivent être seedées explicitement après création (script `scripts/preprod/seed.sql` à créer si nécessaire — hors scope ADR)

## Critères de Succès

- [ ] Métrique 1 : `mcp__supabase__list_branches(cxpojprgwgubzjyqzmoq)` retourne 1 branch active nommée `preprod`
- [ ] Métrique 2 : `gh secret list --repo ak125/nestjs-remix-monorepo | grep -c PREPROD_` ≥ 27
- [ ] Métrique 3 : `grep -c ALLOW_PROD_ENV_COPY .github/workflows/ci.yml` = 0
- [ ] Métrique 4 : un déploiement préprod après merge `main` ne touche AUCUNE table du projet `cxpojprgwgubzjyqzmoq` direct (validation via `__write_audit_log` filtré sur l'IP runner)
- [ ] Métrique 5 : facture Supabase mois suivant montre une ligne "Branches" ≈ $9.66

## Implémentation

### Phase 1 — Branch + secrets (P0.1.b + P0.2 du plan)

1. `mcp__supabase__get_cost(branch)` → `confirm_cost(branch)` → `create_branch(name="preprod")`
2. Récupérer `PREPROD_SUPABASE_URL`, `PREPROD_SUPABASE_SERVICE_ROLE_KEY`, `PREPROD_SUPABASE_ANON_KEY`, `PREPROD_DATABASE_URL`
3. Provisionner les 27 secrets `PREPROD_*` via `gh secret set --repo ak125/nestjs-remix-monorepo`
4. Mapping doc : `governance-vault/ledger/audit-trail/2026-04-30-preprod-secrets-mapping.md`

### Phase 2 — CI refactor (P0.3 du plan)

Fichiers concernés (monorepo `nestjs-remix-monorepo`) :
- `.github/workflows/ci.yml` : remplacer le bloc lignes 700–730
- `.env.preprod.template` (nouveau, versionné) : 30 lignes `VAR=__PREPROD_PLACEHOLDER__`
- `scripts/preprod/render-env.sh` (nouveau)
- `scripts/preprod/check-secrets.sh` (nouveau, pre-flight CI)
- `backend/.env.example` : ajout `PAYBOX_URL`, `WEAVIATE_URL` (vars utilisées prod absentes example — 2 vars drift à corriger)

### Phase 3 — Validation

- Trigger CI manuel via `workflow_dispatch` sur branche dédiée
- Vérifier `__write_audit_log` côté `cxpojprgwgubzjyqzmoq` ne reçoit aucun WRITE depuis le runner après refactor
- Smoke test fonctionnel préprod : login, panier, devis, tunnel pièces

## Revue Planifiée

**Date**: 2026-07-30 (3 mois post-merge)

**Critères de revue**:
- Coût réel facturé vs estimation $9.66/mois
- Nombre d'incidents évités vs effort de maintien (mesuré par tickets ouverts mentionnant "préprod" sur la période)
- Si pause/resume nightly est implémentée et fonctionne
- Si le pattern peut être étendu à d'autres environnements (sandbox dev individuel)

---

*Proposé le: 2026-04-30*
*Accepté le: TBD (en attente confirmation owner sur coût $9.66/mois récurrent)*
*Dernière revue: 2026-04-30*
