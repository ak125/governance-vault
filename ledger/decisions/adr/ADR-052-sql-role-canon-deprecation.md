---
id: ADR-052
title: "SQL role canon deprecation — defer to TS-only canon (ADR-040)"
status: proposed
date: 2026-05-08
decision_date: 2026-05-08
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "AP-04"]
related_incidents: []
related_adr: ["ADR-040", "ADR-046", "ADR-047"]
implementation_status: documentation-only-no-code-change
---

# ADR-052 — SQL role canon deprecation : defer to TS-only canon (ADR-040)

## Contexte

Le monorepo `nestjs-remix-monorepo` contient une migration historique
[backend/supabase/migrations/20260124_add_page_role.sql](https://github.com/ak125/nestjs-remix-monorepo/blob/main/backend/supabase/migrations/20260124_add_page_role.sql)
qui propose un canon RoleId stocké en DB :

- `CREATE TYPE seo_page_role AS ENUM ('R1', 'R2', 'R3', 'R4', 'R5', 'R6')`
- Commentaire interne : `R6=Support`
- Fonction `assign_page_role_from_url()` qui classe `/blog-pieces-auto/*`
  comme R3 et `/support/*` / `/legal/*` comme R6 (interprétation R6=Support).

Cette migration repose sur une **hypothèse architecturale obsolète** :
*"la DB stocke directement le canon RoleId R0..R8"*.

L'architecture actuelle, actée par [[ADR-040-seo-roles-canon-ts-side-only]],
sépare strictement :

- **DB** : stocke worker `page_type` courts (R1, R3, R5...) ou worker
  vocab (`R1_pieces`, `R3_guide_howto`...).
- **TS** : traduit vers canon RoleId via `pageTypeToRoleId()` du package
  `@repo/seo-roles`.
- **UI** : affiche canonical FR via `getRoleDisplayLabel()`.

Le canon TS-only sépare aussi `R6_GUIDE_ACHAT` (guide d'achat) de
`R6_SUPPORT` (support / legal) — l'enum DB historique conflate les deux
sous le label unique `R6` avec interprétation Support, ce qui est
incompatible avec le canon SEO 2026 où R6 = guide d'achat (cf. agents
`r6-content-batch`, tables `__seo_r6_keyword_plan` et
`__seo_gamme_purchase_guide`).

## Décision

1. **La migration `20260124_add_page_role.sql` est `deprecated`** dans le
   ledger vault. Elle reste **physiquement intacte** côté monorepo —
   pas de rename, pas de patch, pas de réécriture corrective.
2. Aucune nouvelle migration corrective ne sera produite. Si un besoin
   runtime DB pour le canon RoleId émerge, ouvrir une nouvelle ADR
   pour acter une dual-side canon (cohabitation TS + SQL avec
   replication explicite).
3. Le canon RoleId reste **strictement TS-only** via `@repo/seo-roles`
   (ADR-040). Tout consommateur DB doit passer par la couche TS pour
   normaliser les valeurs (`normalizeRoleId()`, `tolerantRoleSchema`).
4. L'enum `seo_page_role` (créé par
   `20260124131559_create_seo_observable`, distinct de la migration
   deprecated) **reste en place** car consommé par `__seo_observable`.
   Ne pas le drop. Sa présence ne valide pas l'enum comme canon —
   c'est un vocabulaire worker, pas un canon RoleId.

## Evidence-pack runtime (Supabase MCP, 2026-05-08)

Preuves empiriques que la migration `20260124_add_page_role.sql` n'a
**jamais été appliquée** en prod (`feedback_empirical_proof_external_systems.md`) :

### 1a. Fonction `assign_page_role_from_url` (par nom)

```sql
select proname, pronamespace::regnamespace::text as schema
from pg_proc
where proname = 'assign_page_role_from_url';
```

Résultat : **0 row** — la fonction n'a jamais été créée en prod.

### 1b. Fonction équivalente (par body)

```sql
select proname, pronamespace::regnamespace::text as schema
from pg_proc
where prosrc ilike '%blog-pieces-auto%' or prosrc ilike '%/support%'
limit 20;
```

Résultat : **1 row** — `get_r5_redirect_target` (public) — match
uniquement sur `/support` (gestion redirect R5), **non lié au canon
RoleId**. Aucune fonction de routing role n'existe sous un nom alternatif.

### 2. Colonne `__seo_page.page_role`

```sql
select column_name, data_type, table_name
from information_schema.columns
where table_name = '__seo_page' and column_name = 'page_role';
```

Résultat : **0 row** — la colonne `page_role` n'existe pas sur `__seo_page`.

### 3. Enum `seo_page_role`

```sql
select typname, enumlabel
from pg_type t
join pg_enum e on t.oid = e.enumtypid
where typname = 'seo_page_role'
order by enumsortorder;
```

Résultat : **6 rows** (R1, R2, R3, R4, R5, R6) — l'enum existe en prod,
mais créé par migration `20260124131559_create_seo_observable` (consommé
par `__seo_observable`), **pas** par `20260124_add_page_role.sql`. Ne
pas drop : il sert un autre cas d'usage légitime (worker vocabulary).

### 4. `supabase_migrations.schema_migrations`

Liste extraite via `mcp__supabase__list_migrations` filtrée sur
`like '202601%'` : **aucune** entrée matchant `add_page_role` n'est
présente. Migrations 2026-01 effectivement jouées :
`20260111*`, `20260112*`, `20260116*`, `20260117*`, `20260118*`,
`20260120*`, `20260122*`, `20260123*`, `20260124130543` à
`20260124222954`, `20260126153209` à `20260126154301`,
`20260126185949`, `20260127*`, `20260128*`, `20260129*`,
`20260130*`, `20260131*`. La migration `20260124_add_page_role.sql`
n'apparaît dans aucune entrée `schema_migrations`.

**Conclusion empirique** : la migration est inerte runtime. Aucun
artefact (fonction, colonne, contrainte) qu'elle aurait créé n'est
présent en prod. Sa réapplication serait une régression introduisant
un canon SQL conflictuel avec le canon TS (ADR-040).

## Conséquences

- **Pas de touch au fichier SQL** côté monorepo — l'historique git et
  l'ordre lexicographique des migrations Supabase sont préservés.
- **Tracé canonique** dans le vault : tout futur contributeur qui
  rencontre la migration trouve ici la décision et la preuve runtime.
- **Garde-fou implicite** : si la migration est ré-introduite par
  inadvertance (rebase, cherry-pick), un audit Supabase MCP confirmera
  son inertie ; la deprecation reste valide tant que ADR-040 (canon
  TS-only) tient.
- **Canon SEO 2026 préservé** : R6 = guide d'achat est protégé contre
  toute interprétation "R6 = support" reposant sur l'enum SQL historique.

## Interdictions

- ❌ **Réappliquer la migration** `20260124_add_page_role.sql`.
- ❌ **Réécrire la fonction `assign_page_role_from_url`** sous un nom
  alternatif sans nouvelle ADR.
- ❌ **Drop l'enum `seo_page_role`** (consommé légitimement par
  `__seo_observable`).
- ❌ **Renommer la migration historique** dans
  `backend/supabase/migrations/` (cassure historique git, Supabase CLI
  compare, outils d'audit qui scannent `migrations/*.sql`).

## Références

- [[ADR-040-seo-roles-canon-ts-side-only]] — canon TS-only, base de
  cette deprecation.
- [[ADR-046-r-stack-single-generator-and-layers]] — layers L0-L5 du
  R-stack, contexte canon SEO.
- [[ADR-047-seo-role-contracts-as-code]] — `@repo/seo-role-contracts`
  SoT comportemental.
- Plan d'exécution PR cascade R6 :
  `/home/deploy/.claude/plans/verifier-v-rit-canonique-toasty-lamport.md`
  (PR-D = cette ADR).
- Mémoire opérationnelle :
  `feedback_empirical_proof_external_systems.md`,
  `feedback_no_bricolage_clean_layer.md`,
  `worker-vocab-vs-canon-roleid.md`.
