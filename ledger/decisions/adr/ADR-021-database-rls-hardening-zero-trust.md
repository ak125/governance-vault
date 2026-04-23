---
id: ADR-021
title: "Database RLS Hardening — Zero-Trust per-Table Policies"
status: accepted
date: 2026-04-23
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
related_rules: []
related_incidents: ["INC-2026-011"]
reviewed_by: ""
---

# ADR-021: Database RLS Hardening — Zero-Trust per-Table Policies

## Contexte

Le projet AutoMecanik (Supabase project `cxpojprgwgubzjyqzmoq`) hébergeait
historiquement un grand nombre de tables et de vues dans le schéma `public`
qui étaient directement exposées via PostgREST avec :

- **RLS désactivée** sur 30 tables (incluant `order_idempotency`, `order_resume_tokens`, `pieces_relation_type` (368M lignes), tables KG diagnostic)
- **Policies `USING (true)`** sur 102 tables/policies (catalogue auto, blog SEO,
  mais aussi `___config_admin` contenant `cnfa_pswd` — hashes de mots de passe admin —
  et `ic_postback` exposant 5914 historiques de paiements)
- **Vues `SECURITY DEFINER`** sur 46 vues (incluant `__pg_gammes`, `kg_*`,
  `v_pipeline_*`) qui s'exécutaient avec les droits du créateur (`postgres`)
  et ignoraient les RLS des tables sources
- **Grants `anon` + `authenticated` complets** (DELETE/INSERT/UPDATE/TRUNCATE)
  sur la quasi-totalité des tables

L'audit Supabase advisor remontait :
- `rls_disabled_in_public` : 30 ERRORs
- `security_definer_view` : 45 ERRORs
- `rls_enabled_no_policy` : 18 ERRORs
- `rls_policy_always_true` : 5 ERRORs (advisor seuil) + ~97 non-flagged
- `policy_exists_rls_disabled` : 1 ERROR

L'incident le plus grave découvert pendant l'audit :
[[2026-04-23-admin-password-hashes-anon-leak|INC-2026-011]] — la table `___config_admin`
exposait les hashes de mots de passe admin à toute personne possédant la clé
publique `SUPABASE_ANON_KEY`.

## Décision

Adopter un **modèle zero-trust per-table** pour toutes les tables et vues du
schéma `public` :

1. **RLS activée** sur toutes les tables exposées via PostgREST
2. **Une seule politique `service_role` par défaut** (`PERMISSIVE FOR ALL TO
   service_role USING (true) WITH CHECK (true)`) — le backend bypass RLS via
   le grant `BYPASSRLS` du rôle service_role
3. **Aucun grant `anon` ni `authenticated`** sauf cas explicitement
   documenté et audité
4. **Vues en `SECURITY INVOKER`** sauf cas spécifique cross-schema
5. **Pattern idempotent obligatoire** : `DO $$ BEGIN IF NOT EXISTS … THEN CREATE POLICY … END IF; END $$;` plutôt que `DROP POLICY IF EXISTS … ; CREATE POLICY …`
6. **`-- APPROVED:` honnête et individuel** sur tout `DROP POLICY` réel

## Options Considérées

### Option A: Status quo (rejected)

Garder les policies `USING(true)` sur les tables catalogue, fixer uniquement
les tables sensibles.

**Inconvénients**: ~75 advisor warnings persistants, pattern incohérent,
risque de re-régression.

### Option B: Zero-trust full revoke (chosen)

Verrouiller TOUTES les tables `public` à `service_role` seulement.

**Avantages**: cohérence, 0 advisor flag, sécurité par défaut (deny),
audit clair (toute policy anon/auth qui apparaîtra sera intentionnelle).

**Inconvénients**: 12 PR au lieu de 4, risque consumer externe non-vu
(mitigé par audit callsite exhaustif).

### Option C: Hybrid (rejected)

Zero-trust pour sensibles + maintenir USING(true) sur publiques légitimes,
audit annuel.

**Inconvénients**: charge cognitive, drift au fil du temps.

## Conséquences

### Positives

- **0 advisor flag actif** sur le scope traité
- **204 objets DB hardenizés** (55 tables RLS + 47 vues + 102 policies)
- Pattern reproductible : toute nouvelle table → service_role policy par défaut
- Découverte critique : INC-2026-011 fixée en urgence

### Négatives

- 6 nouveaux `rls_enabled_no_policy` dans schéma `_archive` (faux positifs)
- 3 vues tecdoc cross-schema doivent rester DEFINER (service_role n'a pas
  USAGE sur tecdoc_map/tecdoc_raw)
- Coût d'apprentissage du pattern DO block + service_role policy

### Neutres

- Backend impact zéro (vérifié grep exhaustif backend/src + frontend/app)
- Frontend impact zéro (aucun supabase-js anon direct)

## Plan d'exécution (réalisé)

| Vague | PR | Tables/Vues/Policies | Status |
|-------|----|----------------------|--------|
| 1 | #103 | 2 tables RLS critical (orders) | ✅ Apply |
| 2a | #104 | 4 tables (payment/commerce internal) | ✅ Apply |
| 2b | #105 | 4 tables (catalogue 444M rows) | ✅ Apply |
| 2c | #106 | 8 tables (diagnostic engine) | ✅ Apply |
| 2d | #107 | 15 tables (internal RAG/SEO/agent/tecdoc) | ✅ Apply |
| 2e | #109 | 22 policies (RLS no-policy + always-true) | ✅ Apply |
| 3a-3f | #111-#118 | 47 vues (DEFINER → INVOKER) | ✅ Apply |
| 4a | #119 | 25 policies KG/internal unsafe | ✅ Apply |
| 4b-critical | #120 | 4 policies (admin pswd + payment leak) | ✅ Apply (INC-2026-011) |
| 4b-deferred | #121 | 73 policies + 59 created (catalog/blog/SEO zero-trust) | ✅ Apply |

## Pattern technique canonique

### Pour activer RLS + service_role policy

```sql
ALTER TABLE public.<name> ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public'
    AND tablename='<name>' AND policyname='<name>_service_role_all') THEN
    CREATE POLICY <name>_service_role_all ON public.<name>
      AS PERMISSIVE FOR ALL TO service_role USING (true) WITH CHECK (true);
  END IF;
END $$;
REVOKE ALL ON public.<name> FROM anon, authenticated;
```

### Pour convertir une vue DEFINER → INVOKER

```sql
ALTER VIEW public.<view> SET (security_invoker = true);
REVOKE ALL ON public.<view> FROM anon, authenticated;
```

### Pour supprimer une policy legacy unsafe

```sql
DROP POLICY IF EXISTS "<old_policy_name>" ON public.<table>; -- APPROVED: <raison spécifique factuelle, audit-based>
```

## Évidence & traçabilité

- **12 PR mergées** : #103, #104, #105, #106, #107, #109, #111-#118, #119, #120, #121
- **12 fichiers migration** : `backend/supabase/migrations/20260422_*` et `20260423_*`
- **Audit report initial** : `docs/security/vague3-security-definer-views-audit-20260422.md`
- **Smoke tests** : transaction `BEGIN ... ROLLBACK` documentée par PR
- **Backend health** : `/health` HTTP 200 vérifié après chaque apply

## Rules dérivées (à formaliser)

1. **R-DB-1** : toute nouvelle table dans `public` exposée via PostgREST DOIT
   avoir RLS activée + une policy `service_role` explicite
2. **R-DB-2** : toute nouvelle vue dans `public` DOIT être créée avec
   `security_invoker = true` sauf justification cross-schema documentée
3. **R-DB-3** : aucun `GRANT ... TO anon, authenticated` sur table sans
   policy explicite narrowee approuvée en code review
4. **R-DB-4** : pattern `DO $$ BEGIN IF NOT EXISTS …` pour créer policies
   (idempotent, satisfait CI Migration Safety gate sans `DROP POLICY`)
5. **R-DB-5** : `DROP POLICY` n'est autorisé qu'avec `-- APPROVED: <raison>`
   honnête et individuel par ligne

## Liens

- Incident critique : [[2026-04-23-admin-password-hashes-anon-leak|INC-2026-011]]
- Audit-trail consolidé : [[2026-04-23-db-security-hardening-vagues-1-4]]
- ADR de référence pour gouvernance vault : [[ADR-015-vault-single-source-of-truth]]
