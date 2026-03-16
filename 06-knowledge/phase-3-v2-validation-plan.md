# Phase 3 — Vague 2 : Validation Structurelle (READ-ONLY)

> **Version** : 1.0.2
> **Date** : 2026-03-14
> **Statut** : EXECUTE (2026-03-14)
> **Pre-requis** : full-structural-audit.md V1.2.1 valide
> **Principe** : 100% read-only. Aucune modification schema. Resultats mesures uniquement.

---

## Safety rules

1. **Pas de `count(DISTINCT)` global** sur tables >10M rows — utiliser `GROUP BY ... HAVING`
2. **Toujours `EXPLAIN`** sur requetes Tier 1 avant execution reelle
3. **Lancer hors heures de pointe** (catalog tables >1 GB)
4. **`LIMIT 100`** d'inspection avant comptages complets
5. **Separer non-castables et orphelins** — ne pas melanger dette de typage et integrite referentielle

---

## Ordre d'execution

| Ordre | Bloc | Raison |
|-------|------|--------|
| 1 | **V2.5** SoT | Si SoT floue, PK/FK sur mauvaise table = inutile |
| 2 | **V2.4** Doublons | Si tables doublons, renforcer la mauvaise = contre-productif |
| 3 | **V2.1** PK | Maintenant qu'on sait quelle table est la bonne |
| 4 | **V2.3** Castability | Types TEXT avant FK (FK necessite parfois un cast) |
| 5 | **V2.2** FK orphans | Derniere verif avant formalisation |
| 6 | **V2.6** Readiness | Synthese finale |

---

## V2.5 — Confirmation source de verite (PREMIER)

**Methode** : recherche multi-surface pour chaque table avec SoT = `unknown` ou a confirmer.

**Surfaces de recherche** :
- `backend/src/` — services, controllers, data services
- `backend/supabase/` — migrations, RPCs, vues, fonctions
- `frontend/app/` — appels RPC nommes, loaders
- `scripts/` — jobs, seed, admin, cron

Tables a verifier :
- `__cross_gamme_car_new` (SoT = unknown)
- `__cross_gamme_car` (SoT = unknown → derived ? legacy ?)
- `pieces_ref_search` (SoT = derived — confirmer)

> **Regle** : chercher aussi les aliases SQL, noms de vues, noms de fonctions RPC qui encapsulent la table, pas seulement le nom brut. Une table peut etre consommee via une vue, une RPC, ou un repository avec alias.

**Sortie standard V2.5** :

```
Table: {name}
Consumers backend: {count} ({files})
Consumers frontend: {count}
Consumers SQL/RPC direct: {count}
Consumers SQL/RPC indirect: {count} (vues, fonctions encapsulantes)
SoT verdict: source / derived / reference / legacy / unknown
Confidence: high / medium / low
```

---

## V2.4 — Audit doublons table/table (DEUXIEME)

### Etape 1 — Comparer schemas

```sql
SELECT column_name, data_type, ordinal_position
FROM information_schema.columns
WHERE table_name IN ('__cross_gamme_car', '__cross_gamme_car_new') AND table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

### Etape 2 — Identifier cle metier de recouvrement

> **Regle** : la cle de recouvrement doit etre validee apres comparaison schema (etape 1), AVANT calcul d'overlap. Ne pas deviner la cle.

### Etape 3 — Mesurer overlap (apres identification de la cle)

```sql
-- Adapter {KEY_COL} selon resultat etape 1
-- old_only
SELECT count(*) as in_old_only
FROM __cross_gamme_car old
WHERE NOT EXISTS (
  SELECT 1 FROM __cross_gamme_car_new new WHERE old.{KEY_COL} = new.{KEY_COL}
);

-- new_only
SELECT count(*) as in_new_only
FROM __cross_gamme_car_new new
WHERE NOT EXISTS (
  SELECT 1 FROM __cross_gamme_car old WHERE old.{KEY_COL} = new.{KEY_COL}
);

-- common
SELECT count(*) as common_count
FROM __cross_gamme_car old
WHERE EXISTS (
  SELECT 1 FROM __cross_gamme_car_new new WHERE old.{KEY_COL} = new.{KEY_COL}
);

-- totaux
SELECT
  (SELECT count(*) FROM __cross_gamme_car) as total_old,
  (SELECT count(*) FROM __cross_gamme_car_new) as total_new;
```

### ___meta_tags_ariane vs __blog_meta_tags_ariane

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('___meta_tags_ariane', '__blog_meta_tags_ariane') AND table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

**Sortie standard V2.4** :

```
Paire: {table_a} vs {table_b}
Schema: identical / compatible / incompatible
Key: {col(s)} (validated after schema comparison)
Old rows: {N}
New rows: {N}
Common: {N}
Old only: {N}
New only: {N}
Verdict: subset / superset / disjoint / identical
```

---

##V2.4 — Audit doublons table/table (DEUXIEME)

### Etape 1 — Comparer schemas

```sql
SELECT column_name, data_type, ordinal_position
FROM information_schema.columns
WHERE table_name IN ('__cross_gamme_car', '__cross_gamme_car_new') AND table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

### Etape 2 — Identifier cle metier de recouvrement

> **Regle** : la cle de recouvrement doit etre validee apres comparaison schema (etape 1), AVANT calcul d'overlap. Ne pas deviner la cle.

### Etape 3 — Mesurer overlap (apres identification de la cle)

```sql
-- Adapter {KEY_COL} selon resultat etape 1
-- old_only
SELECT count(*) as in_old_only
FROM __cross_gamme_car old
WHERE NOT EXISTS (
  SELECT 1 FROM __cross_gamme_car_new new WHERE old.{KEY_COL} = new.{KEY_COL}
);

-- new_only
SELECT count(*) as in_new_only
FROM __cross_gamme_car_new new
WHERE NOT EXISTS (
  SELECT 1 FROM __cross_gamme_car old WHERE old.{KEY_COL} = new.{KEY_COL}
);

-- common
SELECT count(*) as common_count
FROM __cross_gamme_car old
WHERE EXISTS (
  SELECT 1 FROM __cross_gamme_car_new new WHERE old.{KEY_COL} = new.{KEY_COL}
);

-- totaux
SELECT
  (SELECT count(*) FROM __cross_gamme_car) as total_old,
  (SELECT count(*) FROM __cross_gamme_car_new) as total_new;
```

### ___meta_tags_ariane vs __blog_meta_tags_ariane

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('___meta_tags_ariane', '__blog_meta_tags_ariane') AND table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

**Sortie standard V2.4** :

```
Paire: {table_a} vs {table_b}
Schema: identical / compatible / incompatible
Key: {col(s)} (validated after schema comparison)
Old rows: {N}
New rows: {N}
Common: {N}
Old only: {N}
New only: {N}
Verdict: subset / superset / disjoint / identical
```

---

---

## V2.3 — Audit castability TEXT (QUATRIEME)

**Cible** : tables P0-P2 de la matrice TEXT

### pieces_price — 11 prix TEXT

```sql
-- Identifier les colonnes prix TEXT
SELECT column_name FROM information_schema.columns
WHERE table_name = 'pieces_price' AND table_schema = 'public'
  AND (column_name LIKE '%_ht' OR column_name LIKE '%_ttc' OR column_name LIKE '%achat%'
       OR column_name LIKE '%vente%' OR column_name LIKE '%price%' OR column_name LIKE '%gros%')
  AND data_type = 'text';

-- Test cast robuste (template par colonne)
SELECT
  count(*) AS total,
  count(*) FILTER (WHERE {COL} IS NULL OR btrim({COL}) = '') AS empty_values,
  count(*) FILTER (WHERE btrim({COL}) ~ '^-?[0-9]+([.][0-9]+)?$') AS castable_dot,
  count(*) FILTER (WHERE btrim({COL}) ~ '^-?[0-9]+([,][0-9]+)?$') AS castable_comma,
  count(*) FILTER (
    WHERE {COL} IS NOT NULL AND btrim({COL}) <> ''
      AND btrim({COL}) !~ '^-?[0-9]+([.,][0-9]+)?$'
  ) AS invalid_values
FROM public.pieces_price;
```

### auto_type — 4 IDs TEXT + 4 dates TEXT

```sql
-- IDs TEXT → INTEGER
SELECT count(*) AS total,
  count(*) FILTER (WHERE {COL} IS NULL OR btrim({COL}) = '') AS empty,
  count(*) FILTER (WHERE btrim({COL}) ~ '^[0-9]+$') AS castable_int,
  count(*) FILTER (WHERE {COL} IS NOT NULL AND btrim({COL}) <> '' AND btrim({COL}) !~ '^[0-9]+$') AS invalid
FROM public.auto_type;

-- Dates TEXT → DATE
SELECT count(*) AS total,
  count(*) FILTER (WHERE {COL} IS NULL OR btrim({COL}) = '') AS empty,
  count(*) FILTER (WHERE btrim({COL}) ~ '^\d{4}-\d{2}(-\d{2})?$') AS castable_date,
  count(*) FILTER (WHERE {COL} IS NOT NULL AND btrim({COL}) <> '' AND btrim({COL}) !~ '^\d{4}-\d{2}(-\d{2})?$') AS invalid
FROM public.auto_type;
```

**Seuil** : `invalid_ratio = invalid / (total - empty_values)`. Si < 0.001 (0.1%) → shadow column safe. Sinon → investigation valeurs invalides. NULL et chaines vides ne comptent pas comme invalides.

**Sortie standard V2.3** :

```
Table: {name}
Column: {col}
Type cible: NUMERIC / INTEGER / DATE
Total: {N}
Empty: {N}
Castable: {N}
Invalid: {N}
Invalid ratio: {%}
Verdict: cast_safe / cast_needs_cleanup(N) / cast_blocked
```

---

## V2.2 — Audit orphelins FK (CINQUIEME)

**Cible** : 8 jointures (6 cat. A + 2 cat. B)

### Etape 1 — Compter non-castables (dette typage, separe des orphelins)

```sql
-- Template par table (si colonne TEXT)
SELECT count(*) AS non_castable
FROM public.{TABLE}
WHERE {COLUMN} IS NOT NULL AND btrim({COLUMN}) <> '' AND btrim({COLUMN}) !~ '^[0-9]+$';
```

### Etape 2 — Orphelins (cast-safe uniquement)

```sql
-- Template cat. A (vers pieces.piece_id) — castables seulement
SELECT count(*) AS orphan_count
FROM public.{TABLE} t
LEFT JOIN public.pieces p
  ON CASE WHEN btrim(t.{COLUMN}) ~ '^[0-9]+$' THEN btrim(t.{COLUMN})::integer ELSE NULL END = p.piece_id
WHERE t.{COLUMN} IS NOT NULL
  AND btrim(t.{COLUMN}) ~ '^[0-9]+$'
  AND p.piece_id IS NULL;
```

| Table | Colonne | Cat. |
|-------|---------|------|
| pieces_media_img | pmi_piece_id | A |
| pieces_ref_ean | pre_piece_id | A |
| pieces_ref_search | prs_piece_id | A |
| pieces_price | pri_piece_id | A |
| pieces_list | pli_piece_id | A |
| pieces_criteria | pc_piece_id | A |

### Cat. B — jointures inter-catalogue

```sql
-- rcp_type_id → rtp_type_id (meme type, pas de cast)
SELECT count(*) AS orphan_count
FROM public.pieces_relation_criteria prc
LEFT JOIN public.pieces_relation_type prt ON prc.rcp_type_id = prt.rtp_type_id
WHERE prt.rtp_type_id IS NULL AND prc.rcp_type_id IS NOT NULL;

-- rtp_piece_id → piece_id (cast-safe)
SELECT count(*) AS non_castable FROM public.pieces_relation_type
WHERE rtp_piece_id IS NOT NULL AND rtp_piece_id::text !~ '^[0-9]+$';

SELECT count(*) AS orphan_count
FROM public.pieces_relation_type prt
LEFT JOIN public.pieces p
  ON CASE WHEN prt.rtp_piece_id::text ~ '^[0-9]+$' THEN prt.rtp_piece_id::integer ELSE NULL END = p.piece_id
WHERE prt.rtp_piece_id IS NOT NULL AND p.piece_id IS NULL;
```

**Seuils** :
- 0 orphelins → `FK_READY`
- ≤0.01% des lignes → `FK_READY_AFTER_CLEANUP`
- \>0.01% → `FK_BLOCKED` (investigation)

**Sortie standard V2.2** :

```
FK candidate: {source.col} → {target.col}
Category: A / B / C
Source rows: {N}
Non-castable: {N}
Orphan count: {N}
Orphan ratio: {%}
Verdict: FK_READY / FK_READY_AFTER_CLEANUP(N) / FK_BLOCKED(N)
Gate: ready / needs_cleanup / blocked
```

---

## V2.6 — Verdict readiness TecDoc (DERNIER)

Synthese des resultats V2.5 → V2.2. Pour chaque table `source_catalog` :

| Table | SoT (V2.5) | Doublons (V2.4) | PK (V2.1) | Types (V2.3) | FK (V2.2) | Readiness finale |
|-------|-----------|----------------|-----------|--------------|-----------|-----------------|
| pieces | source | — | ✓ | OK | ✓ (ref) | ready |
| pieces_relation_type | ? | ? | ? | OK | ? | ? |
| pieces_media_img | ? | ? | ? | OK | ? | ? |
| pieces_price | ? | — | ✓ | ? | ? | ? |
| pieces_criteria | ? | — | ✓ | ? | ? | ? |
| auto_type | ? | — | ✓ | ? | — | ? |

**Criteres de passage** (cf. full-structural-audit.md section 11) :
1. SoT confirmee (pas `unknown`)
2. PK validee ou strategie arretee
3. FK orphelins mesures et plan traitable
4. Cast < 0.1% invalide
5. Consumers cartographies

> Une table sort de V2 avec statut `ready_for_v4`, `blocked`, ou `deferred`.

---

## Execution

| Ordre | Bloc | Outil | Estimation |
|-------|------|-------|-----------|
| 1 | V2.5 | Agent Explore (grep multi-surface) | 1 session |
| 2 | V2.4 | MCP Supabase (4 requetes) | meme session |
| 3 | V2.1 | MCP Supabase (6 requetes) | 1 session |
| 4 | V2.3 | MCP Supabase (5-10 requetes) | meme session |
| 5 | V2.2 | MCP Supabase (10 requetes) | 1 session |
| 6 | V2.6 | Synthese documentaire | meme session |

**Livrable** : `full-structural-audit.md` V1.3.0 avec resultats mesures + verdicts finaux.

---

## Refs croisees

| Document | Role |
|----------|------|
| full-structural-audit.md V1.2.1 | Matrice source, verdicts, preconditions |
| perf-findings.md V1.0.3 | F4 jointure baseline |
| domain-map.md V1.4.3 | Classification domaines |
