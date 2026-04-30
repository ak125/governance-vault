---
title: Audit isolation préprod — état pré-décision P0.1
date: 2026-04-30
type: audit-trail
related_adr: TBD-preprod-isolation
related_inc: ALLOW_PROD_ENV_COPY (claim 4 audit utilisateur 2026-04-30)
status: pre-decision
---

# Audit isolation préprod — 2026-04-30

## Contexte

Audit utilisateur (2026-04-30) sur `nestjs-remix-monorepo` a identifié `ALLOW_PROD_ENV_COPY=1` dans `.github/workflows/ci.yml` qui copie systématiquement `~/production/.env` du runner self-hosted vers le déploiement préprod à chaque merge `main`. L'analyse profonde révèle un problème plus large : **préprod et prod partagent la même instance Supabase**.

Ce document est le pré-requis P0.0 du plan d'action `verifer-votre-syst-me-keen-fern.md` — produit avant toute décision d'isolation (P0.1.a).

## 1. Diff `~/production/.env` (runner DEV) ↔ `backend/.env.example`

Source : `46.224.118.55:/home/deploy/production/.env` (30 vars actives) vs `backend/.env.example` (63 vars documentées).

### Vars utilisées en prod et présentes dans example (28)

```
APP_URL, BASE_URL, EMAIL_FROM, NODE_ENV,
PAYBOX_DEVISE, PAYBOX_HMAC_KEY, PAYBOX_IDENTIFIANT, PAYBOX_MODE,
PAYBOX_PAYMENT_URL, PAYBOX_RANG, PAYBOX_SITE,
RAG_API_KEY, RAG_SERVICE_URL, REDIS_URL,
RESEND_API_KEY, SESSION_SECRET,
SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL,
SYSTEMPAY_API_URL, SYSTEMPAY_CERTIFICATE_PROD, SYSTEMPAY_CERTIFICATE_TEST,
SYSTEMPAY_HMAC_KEY_PROD, SYSTEMPAY_HMAC_KEY_TEST,
SYSTEMPAY_MODE, SYSTEMPAY_SIGNATURE_METHOD, SYSTEMPAY_SITE_ID,
USE_UNIFIED_RPC
```

### Vars utilisées en prod mais ABSENTES de `.env.example` (2 — drift à corriger)

- `PAYBOX_URL` — utilisée pour callback ou redirect, pas documentée
- `WEAVIATE_URL` — endpoint Weaviate du repo `/opt/automecanik/rag/`, pas documentée côté backend

### Vars dans `.env.example` mais NON utilisées en prod (35 — features off)

```
ANALYTICS_*, ENABLE_RPC_V2, GA4_*, GMAIL_*, GOOGLE_ADS_*, GSC_*,
PAYBOX_CALLBACK_MODE, RAG_KNOWLEDGE_PATH, REDIS_CACHE_TTL,
REDIS_HOST, REDIS_PORT, SEO_ALERTS_*, SEO_MONITORING_ENABLED,
SUPABASE_DB_HOST, SUPABASE_DB_PASSWORD, USE_RM_API,
USE_SEPARATE_OEM_RPC, VEHICLES_CACHE_TTL
```

→ Features documentées mais pas activées en prod actuelle. Pour préprod, ces vars peuvent rester inactives (placeholder ou absentes).

## 2. État GitHub repo secrets (`ak125/nestjs-remix-monorepo`)

```
DATABASE_URL                  2024-12-31
DOCKERHUB_TOKEN              2024-11-13
DOCKERHUB_USERNAME           2024-11-12
GOOGLE_CLIENT_ID             2026-03-10
SUPABASE_ANON_KEY            2026-02-25
SUPABASE_KEY                 2025-12-14   (legacy duplicate)
SUPABASE_SERVICE_ROLE_KEY    2026-02-25
SUPABASE_URL                 2025-12-14
VITE_GOOGLE_CLIENT_ID        2026-03-10
```

**9 secrets — 0 secret `PREPROD_*`.**

Constat important : **les secrets Paybox/SystemPay/Resend/Session/RAG_API_KEY ne sont PAS en GitHub secrets**, ils vivent uniquement dans `~/production/.env` sur le runner self-hosted. C'est pourquoi le pattern `cp ~/production/.env` est la voie actuelle de transmission — le runner est l'unique source de vérité pour ces credentials.

Conséquence pour P0.2 : **27 secrets `PREPROD_*` à provisionner** en GitHub Actions repo settings (non automatisable depuis l'agent — action humaine via UI ou `gh secret set`).

## 3. Inventaire Supabase organisation `fezyshchnnrwwpnzbcwb`

| project_id | name | status | usage |
|-------------|------|--------|-------|
| `cxpojprgwgubzjyqzmoq` | massdoc | ACTIVE_HEALTHY (PG 17) | **AutoMecanik PROD** (~250 tables, ADR-016 cache, KG, RAG, partitions GSC/GA4/CWV) |
| `hesiybmfhjicvahmdifv` | auto pieces equipements | ACTIVE_HEALTHY (PG 17) | Projet distinct (MVP devis : Customer/Quote/MagicLink + admin_gmail_* + 70 kg_nodes) — **PAS un préprod AutoMecanik** |
| `hssigihofbbdehqrnnoz` | Tunisia Jockey Club | ACTIVE_HEALTHY (PG 17) | Autre business (hors scope) |
| `zpoumiwcpsqyvnbxyzor` | ak125's Project | INACTIVE | Dormant |

**`mcp__supabase__list_branches(cxpojprgwgubzjyqzmoq)` → `[]`** : aucune branche existante sur le projet prod.

→ **Aucun projet préprod AutoMecanik dormant à récupérer**. Provisioning doit être créé from scratch.

## 4. Coût Supabase branch (organisation `fezyshchnnrwwpnzbcwb`)

`mcp__supabase__get_cost(branch)` → **$0.01344 / heure** = **~$9.66 / mois** si 24/7.

Acceptable pour un environnement préprod permanent. Optimisations possibles :
- Pause/resume via `mcp__supabase__pause_project` hors heures ouvrées (réduction ~50%)
- Reset périodique de la branche (`mcp__supabase__reset_branch`) pour purger données de test

## 5. Décision triggers pour P0.1.a (ADR à venir)

| Option | Coût | Isolation | Recommandation |
|--------|------|-----------|----------------|
| **A** — nouveau projet `automecanik-preprod` | +$25/mois (Pro tier) | Totale, drift schema possible | Reject — coût supérieur, drift risque |
| **B** — schéma `preprod` dans `cxpojprgwgubzjyqzmoq` | $0 | Faible (RPC `SECURITY DEFINER` cross-schema) | Reject — partage compute, pas d'isolation réelle |
| **C** — Supabase branch sur `cxpojprgwgubzjyqzmoq` | ~$9.66/mois | Isolation DB totale, schema auto-sync | **Recommandé** — coût maîtrisé, alignement ADR-017 |

**Recommandation pour ADR P0.1.a : Option C (Supabase branch).**

Justification :
1. Isolation DB complète (instance distincte, pas seulement schema)
2. Schema auto-sync depuis migrations `cxpojprgwgubzjyqzmoq` (pas de drift manuel)
3. Coût bas (<$10/mois) avec leviers réduction
4. Aligne avec ADR-017 RPC cleanup (les RPC migrent automatiquement)
5. `mcp__supabase__create_branch` supporté nativement

## 6. Outputs cette phase P0.0

- Liste vars prod (30) → input pour `.env.preprod.template`
- Liste vars-only-example (35) → exclues du template (features inactives)
- 2 vars manquantes example (`PAYBOX_URL`, `WEAVIATE_URL`) → à ajouter aussi à `.env.example` lors du PR P0.3
- Liste 27 secrets `PREPROD_*` à provisionner pour P0.2 (Supabase 4 vars seront ajoutées par P0.1.b)

## 7. Coverage manifest (Agent Exit Contract v1.0.0)

| Champ | Valeur |
|-------|--------|
| `scope_requested` | Audit pré-requis P0.0 (3 sous-tâches : env diff, gh secrets, Supabase projects) |
| `scope_actually_scanned` | 3/3 sous-tâches réalisées avec données complètes |
| `files_read_count` | 4 (~/production/.env, .env.example, gh secret list, mcp list_projects+list_branches+get_cost) |
| `excluded_paths` | Inspection contenu vars (valeurs non-lues, juste les clés) ; tables détaillées du projet `auto pieces equipements` (échantillon suffisant) ; `~/preprod/.env` actuel sur runner (s'il existe) |
| `corrections_proposed` | Décision Option C dans P0.1.a (ADR à rédiger) |
| `corrections_applied` | aucune (pré-décision) |
| `remaining_unknowns` | Comportement de pause/resume sur Supabase branch ; processus de provisioning Paybox/SystemPay test accounts (créer compte prestataire ou utiliser keys de test partagés ?) ; faut-il sync les 250+ migrations sur la branche ou repartir d'un schema dump épuré ? |
| `final_status` | `SCOPE_SCANNED` — input prêt pour P0.1.a |
