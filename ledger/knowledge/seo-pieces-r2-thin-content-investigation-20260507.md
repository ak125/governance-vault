---
type: knowledge
status: canon
created: 2026-05-07
updated: 2026-05-07
tags: [seo, pieces, r2, thin-content, forensic, root-cause, gsc, archive, recovery]
related-incidents: [INC-2026-005-recurrence]
related-knowledge: [seo-traffic-drop-investigation-20260426]
related-adrs: [ADR-016-vehicle-page-matview-persistence, ADR-022-r8-rag-control-plane, ADR-026-content-separation, ADR-031-canonical-framework]
verdict: ROOT_CAUSE_IDENTIFIED
related-migration-monorepo: 20260128_get_pieces_for_type_gamme_v4_raw_seo.sql
---

# Forensic — `/pieces/*` thin content root cause (2026-05-07)

> [!important] Verdict
> **R2 (`/pieces/*`) n'a jamais reçu son enricher éditorial complet.** La migration TTFB du 2026-01-28 a déplacé le processing SEO du SQL vers NestJS pour gagner 5-7 s, mais le processor NestJS censé prendre le relais n'a jamais été implémenté à la hauteur de la version SQL d'origine. Résultat : meta descriptions tronquées à 30 caractères, identiques entre toutes les variantes du même modèle (signature « duplicate intra-modèle » détectée par Google). 73 % des `/pieces/*` sont en `Crawled - currently not indexed` chez Google.
>
> Le contenu legacy (`__seo_lexique_matrice` 221 rows, `__seo_gamme_conseil` 2 790 rows, `__seo_r1_gamme_slots`, `__seo_vehicle_granularity_patterns`) **existe encore** — partiellement en `public`, partiellement en `_archive`. Aucun PITR ni Wayback nécessaire. La voie canon est de réimplémenter le pipeline R2 enricher en s'alignant sur le pattern R8 (ADR-022 Pilier 2b).

## Signal d'entrée

GSC URL Inspection live (sample 15 URLs aléatoires de `sitemap-pieces-1.xml`, 50 000 URLs) au 2026-05-07 22:16 UTC :

- 4/15 (27 %) `Submitted and indexed`
- 10/15 (67 %) `Crawled - currently not indexed`
- 1/15 (7 %) `URL is unknown to Google`

GA4 live au même horodatage : organic search 33 sessions sur 2026-05-07 vs moyenne 14 jours = ~64 sessions/jour, soit **−48 %**. La chute aiguë du 07/05 cumule deux causes :
1. **INC-2026-005-recurrence** (Cloudflare cache poisoning, 30 400 pages 5xx-cached 28/04→06/05). Fix `v2026.05.06-cf-cache-5xx-fix` + purge CF + GSC validation lancée 06/05. Recrawl Googlebot 3-7 jours, retour J+7.
2. **Plafond chronique** : 67 % de `/pieces/*` non-indexées en permanence depuis novembre 2025. Cette knowledge documente la cause #2.

## Diff empirique 4 variantes du même triplet (gamme×marque×modèle)

URLs : Renault Laguna II 140028 + alternateur, 4 type_id différents.

| type_id | bytes | text | md5 | meta description | desc len |
|---|---|---|---|---|---|
| 15473 (1.6 16V Phase 1) | 230 KB | 9 325 | 794f6214 | `Alternateur RENAULT LAGUNA II,` | 30 |
| 18681 (1.6 16V Phase 2) | 193 KB | 8 787 | eddfe046 | `Alternateur RENAULT LAGUNA II,` | 30 |
| 18214 (1.9 dCi) | 224 KB | 8 979 | c88303cf | `Alternateur RENAULT LAGUNA II,` | 30 |
| 18579 (1.9 dCi) | 226 KB | 9 065 | 393ca138 | `Alternateur RENAULT LAGUNA II,` | 30 |

→ 4 variantes, 4 textes-différents-mais-similaires, **1 seule meta description** identique à 100 %, tronquée par une virgule. Pas de mention du moteur, de la cylindrée, de l'année, de la puissance, du fuel. Le sitemap contient 18 variantes type_id pour ce triplet seul → 18 pages avec la même meta.

## État réel des tables candidates

### Tables runtime (schema `public`)

| Table | Rows | État | Diagnostic |
|---|---|---|---|
| `__seo_page` | 321 838 | colonnes `title/h1/meta_description` présentes mais **100 % NULL** sur `page_type='product'` | tabula rasa : pipeline ETL prévu, jamais exécuté |
| `__seo_role_content` | 0 | jamais peuplée | pipeline R-stack content compilation jamais branché sur R2 |
| `__seo_r2_keyword_plan` | 0 | jamais peuplée | plan KW R2 jamais exécuté |
| `__seo_page_brief` | 33 | quasi-vide | non utilisable |
| `__seo_type_vlevel` | 6 476 | partielle (12 % des type_id) | classification V-Level absente sur 88 % véhicules |
| `__seo_gamme_conseil` | 2 790 | **HTML riche, quality_score 80-87, sourcing RAG** | utilisée par `/blog-pieces-auto/conseils/*` (R3 hub) — **PAS lue par R2** |
| `__seo_r1_gamme_slots` | inconnu mais existe | FAQ + args R1 structurés | utilisée par R1 — **PAS lue par R2** |
| `__seo_gamme_purchase_guide` | 241 | OK (1 par gamme, 65 colonnes) | guide d'achat gamme-level, pas variante-level |
| `__seo_gamme_car_switch` | 6 542 | 4 colonnes (`sgcs_*`), partiel | switches anchors résiduels |

### Tables legacy (schema `_archive`, déconnectées du runtime)

| Table | Rows | Contenu | Récupération |
|---|---|---|---|
| `__seo_lexique_matrice` | **221** (1 par gamme) | `slm_role_fonctionnel`, `slm_verbes_autorises[]`, `slm_lexique_autorise[]`, `slm_pieces_associees[]`, `slm_symptomes[]`, `slm_claims_interdits[]` | **trivial**, `INSERT INTO public.__seo_lexique_matrice SELECT * FROM _archive.__seo_lexique_matrice` |
| `__seo_vehicle_granularity_patterns` | 34 | patterns granularité (marque/modèle/type/motorisation) | trivial |
| `__seo_variable_patterns` | 4 | patterns de substitution variables | trivial |
| `__seo_keywords_clean` | inconnu | mots-clés normalisés | trivial |
| `__seo_zone_coefficients` + `__seo_zone_severity` + `__seo_zone_config` | n/a | poids des zones SEO (H1/title/desc/content) pour scoring | trivial |
| `__seo_subsystem_components` | 61 | composants sous-systèmes | trivial |
| `__seo_action_definitions` + `__seo_business_rules` + 40+ autres | n/a | système legacy SEO complet (claims, ambiguïté, contradictions, penalty matrix, mandatory fields, indexation status, etc.) | trivial bulk |
| `orphans_gamme_content_2026_04_21` | 88 | snapshots `__seo_r1_gamme_slots` orphelins | utilitaire récupération R1 |
| `content_quality_fixes_2026_04_21` | 418 | snapshots pre-`Q2_accents_Q3_titles` fix | non lié à R2 |
| `gamme_content_deleted` | 0 | journal de suppression | vide donc inutilisable |

**Constat-clé** : tout l'écosystème legacy SEO (50+ tables `__seo_*`) a été **archivé en bloc** dans `_archive`, pas écrasé. Aucun grep de code TS ne référence ces tables — le pipeline a été simplement débranché.

### Code coupable identifié

#### 1. La migration TTFB du 2026-01-28

**Fichier** : `backend/supabase/migrations/20260128_get_pieces_for_type_gamme_v4_raw_seo.sql`

Commentaire en tête :

```sql
-- Purpose: Fix TTFB regression (10.34s → <1s) by removing SEO processing
-- V3 calls process_seo_template() 5 times (H1, Title, Desc, Content, Preview)
-- V4 returns RAW templates without processing
-- NestJS handles processing with Redis cache (TTL 24h per gamme_id+type_id)
```

**Le contrat implicite** : V4 sort des templates non-processés ; NestJS doit les enrichir avant retour HTTP. Ce contrat n'a jamais été honoré côté NestJS.

#### 2. Le builder NestJS qui ne fait que pass-through

**Fichier** : `backend/src/modules/rm/services/rm-builder.service.ts:554, 671`

```ts
seo: { h1: '', title: '', description: '', content: '', preview: '' }
```

Deux fallbacks vides. Quand RPC V4 retourne du raw, le builder le passe tel quel ou met `''`. Aucun appel à un enricher.

#### 3. Le seul enrichissement existant = templating trivial

**Fichier** : `backend/src/config/seo-variations.config.ts`

Pour R2, il n'existe que `SEO_PRICE_VARIATIONS` (7 modifiers : *à prix imbattables / pas cher / à petit prix / économique / à prix réduit / à tarif avantageux / au meilleur prix*) appliqué via `selectVariation(typeId, pgId, offset) = (typeId+pgId+offset) % 7`. Rotation déterministe sur 7 valeurs cosmétiques. Aucune variation par moteur, fuel, puissance, année.

Pour R8 en revanche, le même fichier définit (ADR-022 Pilier 2b) :

- `SEO_R8_INTRO_VARIATIONS` (7 templates avec placeholders {brand} {model} {type} {power} {fuel} {year_from} {year_to})
- `SEO_R8_VARIANT_HIGHLIGHT_VARIATIONS` (11 templates différentiation motorisation vs sœurs)
- `SEO_R8_CATALOG_ACCESS_VARIATIONS` (7 templates accès catalogue familles)
- `SEO_R8_FAQ_OPENING_VARIATIONS` (7 templates amorce FAQ)
- `SEO_R8_TRUST_SIGNAL_VARIATIONS` (5 templates trust signals)

Soit **37 templates riches pour R8** vs **7 cosmétiques pour R2**. R8 utilise des slot offsets (0/100/200/300/400) pour saler les choix entre slots et garantir l'indépendance de chaque section. R2 n'a rien de tel.

#### 4. Le R8 enricher qui n'a pas d'équivalent R2

**Fichier** : `backend/src/modules/admin/services/r8-vehicle-enricher.service.ts`

Imports complets : `R8_TABLES`, `R8_HARD_GATES`, `R8_DIVERSITY_FORMULA_WEIGHTS`, `R8_DIVERSITY_THRESHOLDS`, `RAG_KNOWLEDGE_PATH`, RAG vehicle frontmatter parser, `EnricherTextUtils`, `VehicleRagGeneratorService`.

Pipeline complet : RAG vehicle MD → frontmatter → enrichissement par slot → score diversity → décision SEO `R8SeoDecision`. Tout l'outillage existe.

Aucun fichier `r2-pieces-enricher.service.ts` n'existe dans le monorepo. Aucun `R2_TABLES`/`R2_HARD_GATES`/`R2_DIVERSITY_*`/`SEO_R2_*_VARIATIONS`. R2 est un trou architectural.

## Chronologie probable

| Date | Événement | Source |
|---|---|---|
| < 2025-09 | Système legacy MySQL/PHP : `__seo_lexique_matrice`, `process_seo_template()` SQL, switches HTML riches | présence colonnes `sgc_*` legacy + 50+ tables archive |
| 2025-09 → 2026-01 | Migration vers NestJS+Remix+Supabase. V3 conserve `process_seo_template()` côté SQL | RPC `get_pieces_for_type_gamme_v3` + commentaire migration |
| 2026-01-28 | Migration V4 : SEO processing déplacé SQL→NestJS pour TTFB. Contrat implicite : NestJS doit enrichir les RAW templates avec Redis cache 24 h | `20260128_get_pieces_for_type_gamme_v4_raw_seo.sql` |
| 2026-01-28 → 2026-04 | NestJS reste avec `seo: { h1:'', title:'', description:'', content:'', preview:'' }` fallback. Templating cosmétique seulement (rotation 7 modifiers). 50+ tables legacy déplacées en `_archive` au lieu d'être branchées sur le nouveau pipeline | `rm-builder.service.ts` + `_archive` schema |
| 2026-02 → 2026-04 | Crawl Googlebot des `/pieces/*` détecte le pattern duplicate intra-modèle. Pages des marques majeures restent indexées (PageRank), pages tail désindexées progressivement (`Crawled - not indexed`) | URL Inspection coverageState |
| 2026-04-28 → 2026-05-06 | INC-2026-005-recurrence : 30 400 pages 5xx-cached pendant 8 jours | post-mortem `2026-05-06-cf-cache-poisoning-pieces-5xx.md` |
| 2026-05-06 13:36 UTC | Fix v2026.05.06-cf-cache-5xx-fix + purge CF | tag PROD |
| 2026-05-07 | Cumul (cause aiguë + cause chronique) : organic GA4 −48 % vs baseline | GA4 live |

## Voie canon recommandée (sans bricolage)

Le contrat implicite de la migration TTFB doit être honoré : NestJS doit enrichir les RAW templates retournés par `get_pieces_for_type_gamme_v4`. Trois axes obligatoires.

### Axe 1 — Restaurer les tables legacy en `public`

Read-only `INSERT … SELECT` depuis `_archive`. Aucune perte. Tables prioritaires (alimentent un R2 enricher) :

- `__seo_lexique_matrice` (221 rows, 1 par gamme — verbes/lexique/symptômes/pièces associées)
- `__seo_vehicle_granularity_patterns` (34 patterns de granularité)
- `__seo_variable_patterns` (4 patterns de substitution variables)

Optionnel selon le scope retenu :
- `__seo_keywords_clean` (KW normalisés)
- `__seo_zone_coefficients` + `__seo_zone_severity` + `__seo_zone_config` (scoring zones)
- `__seo_subsystem_components` (composants sous-systèmes)

Garde-fou : ne pas tout restaurer en bloc. Auditer chaque table avant restauration pour confirmer qu'elle est encore alignée avec les autres tables `public` (FK, types, conventions).

### Axe 2 — Implémenter `r2-pieces-enricher.service.ts` calqué sur `r8-vehicle-enricher.service.ts`

Pattern : RAW templates V4 → lecture `__seo_lexique_matrice` (gamme-level) + `auto_type` (variante-level : `type_power_kw`, `type_year_from/to`, `typeFuel`, `typeBody`, `motorCodes`) + `__seo_gamme_conseil` (HTML sections S1/S_GARAGE/S4_DEPOSE) → composition meta description ≥130 chars unique-par-variante → cache Redis 24 h.

Définir dans `seo-variations.config.ts` :

- `SEO_R2_META_DESCRIPTION_VARIATIONS` (7-11 templates avec placeholders {gamme} {brand} {model} {variant} {power} {fuel} {year_from} {motor_code} {symptomes_principaux})
- `SEO_R2_TITLE_VARIATIONS` (7 templates)
- `SEO_R2_INTRO_VARIATIONS` (7 templates avec lexique gamme)
- `SEO_R2_FAQ_OPENING_VARIATIONS` (5 templates)
- `R2_SLOT_OFFSETS` (séparation slots)

Le fichier `r2-pieces-enricher.service.ts` doit aussi exposer un `R2SeoDecision` + `diversityScore` pour QA.

### Axe 3 — Hardening permanent (obligatoire dans tous les cas)

Sans ces garde-fous, la même classe de régression revient à la prochaine optimisation perf.

1. **DB constraints** : `CHECK (length(meta_description) BETWEEN 130 AND 200)` et `CHECK (length(title) BETWEEN 40 AND 70)` sur `__seo_page` (et toute future table runtime SEO).
2. **CI lint canonique** : règle ast-grep + script SQL de QA :
   - `meta_description` non-tronquée (interdit la terminaison par virgule isolée)
   - zéro duplicate `meta_description` intra-modèle (group by `(gamme_id, marque_id, modele_id)`, count distinct meta = count rows)
   - `meta_description` doit contenir au moins une variable variante-level (puissance OU fuel OU motor_code)
3. **Snapshot pré-migration obligatoire** : ADR + skill « avant toute migration touchant `__seo_*` ou `process_seo_template`, dump table-snapshot dans `_archive` schema avec horodatage ; release impossible si snapshot absent ». Le snapshot 2026-04-21 (`orphans_gamme_content_*`, `content_quality_fixes_*`) montre que le pattern est déjà partiellement en place — il manque juste de le rendre obligatoire en CI.

## Annexes

### A. URLs de test

PASS sample :
- `/pieces/alternateur-4/seat-147/leon-iii-147032/1-6-tdi-56777.html`
- `/pieces/courroie-d-accessoire-10/peugeot-128/308-sw-i-128042/1-4-16v-26610.html`
- `/pieces/alternateur-4/renault-140/laguna-ii-140028/1-9-dci-18579.html`

NOT INDEXED sample :
- `/pieces/support-moteur-247/citroen-46/c3-ii-46021/1-6-vti-32030.html`
- `/pieces/demarreur-2/mini-113/mini-r56-113002/1-4-one-22485.html`
- `/pieces/butee-d-embrayage-48/dacia-47/logan-mcv-i-47019/1-6-16v-19898.html`

### B. Sample legacy lexique alternateur

```json
{
  "slm_pg_id": 4,
  "slm_slug": "alternateur",
  "slm_role_fonctionnel": "Recharger la batterie et alimenter les equipements electriques du vehicule moteur tournant",
  "slm_verbes_autorises": ["recharger", "alimenter", "fournir du courant", "maintenir la charge", "produire de l electricite"],
  "slm_lexique_autorise": ["alternateur", "charge", "recharge", "batterie", "alimentation", "courant", "tension", "regulateur"],
  "slm_pieces_associees": ["courroie-d-accessoire", "demarreur", "galet-enrouleur-de-courroie-d-accessoire", "galet-tendeur-de-courroie-d-accessoire", "poulie-d-alternateur", "poulie-vilebrequin"],
  "slm_symptomes": ["voyant batterie allume moteur tournant", "batterie qui se decharge malgre les trajets", "phares qui faiblissent ou clignotent", "sifflement de la courroie d accessoire", "odeur de courroie brulee ou d electrique", "plus de 150 000 km ou tension de charge basse"]
}
```

→ Avec ces données seules, on peut composer une meta description unique-par-variante. Exemple sans LLM, déterministe :

```
Alternateur RENAULT Laguna II 1.9 dCi 120 ch (2001-2007). Recharge batterie + alimentation. Symptômes voyant batterie / décharge / phares qui faiblissent. Pièces associées : courroie d'accessoire, poulie d'alternateur. Compatibilité vérifiée.
```

168 chars, unique-par-variante, lexique gamme-level + specs variante-level + symptômes pertinents = vraie valeur SEO sans bricolage.

### C. Fichiers critiques

- `backend/supabase/migrations/20260128_get_pieces_for_type_gamme_v4_raw_seo.sql` — migration TTFB (origine du contrat non honoré)
- `backend/src/modules/rm/services/rm-builder.service.ts:554,671` — fallbacks vides
- `backend/src/config/seo-variations.config.ts` — templating cosmétique R2 + canon riche R8 (référence)
- `backend/src/modules/admin/services/r8-vehicle-enricher.service.ts` — pattern à répliquer pour R2
- `frontend/app/utils/pieces-vehicle.loader.server.ts` — loader R2, pass-through `rmV2.seo`
- `frontend/app/utils/pieces-vehicle.meta.ts` — meta builder R2

### D. Limites de l'audit

- Sample URL Inspection limité à 15 URLs (quota 2 000/jour disponible — élargir à 200+ recommandé)
- Pas vérifié le rendu sur sample 100+ URLs pour la distribution exacte des cas `noProducts`
- Pas vérifié si `process_seo_template()` SQL existe encore (V3 conservé en parallèle ?) — peut être restauré rapidement comme fallback transitoire si oui
- GSC Performance API a J−3 de retard, donc clicks réels du 05/06/07 mai pas mesurés
- Pas de vérification PITR du projet `cxpojprgwgubzjyqzmoq` (rétention dépend du plan tarifaire) — pas nécessaire car récupération possible depuis `_archive`

## Liens

- Incident parent transitoire : `2026-05-06-cf-cache-poisoning-pieces-5xx.md`
- Audit antérieur INSUFFICIENT_EVIDENCE : `seo-traffic-drop-investigation-20260426.md`
- ADR-022 R8 RAG Control Plane (référence pattern)
- ADR-026 P0 content separation (canon contenu R-roles)
- ADR-031 Canonical Framework 4-layer (raw/wiki/exports/consumers)
