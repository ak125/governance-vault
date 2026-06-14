---
id: ADR-086
title: "Content Excellence Contract — loi de composition R2 = R1 ⊕ R8 : enrichir R1 (gamme) + R8 (par motorisation) depuis le WIKI ; R2 est leur combinaison, non écrit séparément"
status: proposed
date: "2026-06-13"
decision_date: "2026-06-13"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-083"]
extends: ["ADR-059", "ADR-031", "ADR-066"]
related_adr: ["ADR-031", "ADR-033", "ADR-046", "ADR-059", "ADR-066", "ADR-083"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
---

# ADR-086 : Content Excellence Contract (loi de composition R2 = R1 ⊕ R8)

## § Contexte (constat vérifié 2026-06-13)

La boucle `RAW → WIKI → exports/seo → projection DB → pages R*` est gouvernée par **ADR-059**
(accepted). Son contrat d'export porte `facts:[{key,value,source_id}]` +
`blocks:[{role, section, content_md, source_ids[], truth_level}]`. Trois constats, vérifiés en
code, registre et en test bout-en-bout :

1. **Trou de contrat amont.** **ADR-083** promeut des proposals → canon WIKI `approved +
   exportable`, mais ne produit que de la **prose** (sections H2). Aucun contrat n'exigeait que le
   canon porte les `facts` / `blocks` structurés qu'ADR-059 projette. Mesure réelle : les 3 gammes
   pilotes promues (`filtre-a-air` / `filtre-a-carburant` / `filtre-d-habitacle`) avaient `facts:[]`
   et `blocks:[]` → export **structurellement valide mais vide de contenu**. Le mapping
   `dimensions → facts/blocks` a été prouvé (PR `feat/export-contract-dimensions-to-blocks`,
   `schema_version 1.1.0`, 32 tests, negative test 0 filler) — mais le contenu projeté restait
   **mince** (compatibilité + 1 ligne entretien) : insuffisant pour du SEO excellent et pour
   différencier des pages quasi-identiques sans tomber dans le duplicate.

2. **R2 traité comme une surface à écrire.** Une version antérieure excluait R2 de l'éditorial
   (« structural-first, distinct »). Correct mais incomplet : **R2 ne s'écrit pas — il se compose.**
   Sa richesse et son unicité viennent d'ailleurs (voir Décision §1).

3. **Architecture Encyclopédie non canonisée.** Le programme construit (générateurs DB-first
   gamme/véhicule/diagnostic, axe motorisation transverse, seed `kg_engine_families`, injecteur
   éditorial multi-source) ne fait foi nulle part — il vit en mémoire agent + plan +
   `automecanik-raw/docs/encyclopedia-contract.md`.

Conséquence : enrichir le RAW sans **modèle de contenu** ni contrat de structure = sur-production
de champs faibles qui n'améliorent ni le SEO ni la variété. L'objectif est un contenu **excellent,
différencié, non-dupliqué** qui atteint réellement les pages.

## § Décision

### 1. Loi de composition de contenu : **R2 = R1 ⊕ R8** (le cœur)

Le contenu ne s'écrit pas page transactionnelle par page transactionnelle. Il s'enrichit sur **deux
surfaces ancrées** et **R2 en est la combinaison déterministe** :

- **Surface GAMME (cluster R1)** — la connaissance *de la pièce* : fonction, principe, critères de
  choix, symptômes de défaillance, normes/standards, FAQ. **Écrite 1× par gamme**, sourcée,
  **partagée** par toutes les variantes véhicule. *(« R1 » désigne ici le cluster gamme-ancré
  R1/R3/R4/R6 du `role-matrix.md` : R1 routage, R3 conseils, R4 référence, R6 guide-achat — tous
  consommateurs du **canon gamme**.)*
- **Surface VÉHICULE (R8)** — la connaissance *du véhicule × motorisation* : pannes connues,
  intervalles d'entretien, références **de CE moteur**. **Écrite par motorisation**
  (`fuel:` → `engine_family:`), consommatrice du **canon véhicule**.
- **R2 (produit, transactionnel) = projection(canon gamme) ⊕ projection(canon véhicule pour la
  motorisation de CETTE page)** — **composé**, **non authored**. Reste structural-first
  (**ADR-066**) : R2 ne porte pas ses propres blocs éditoriaux ; il **joint** le cluster gamme et
  la couche R8. L'URL R2 (`gamme × marque × modèle × motorisation`) encode littéralement cette
  jointure R1 × R8.

**Pourquoi cette loi résout le duplicate à l'échelle.** Le catalogue produit des pages R2
quasi-identiques (même gamme, véhicules voisins). L'unicité ne vient **pas** d'une prose réécrite
par page (irréaliste + pénalisé : Helpful Content / duplicate). Elle vient de la **composante R8
par motorisation** : deux R2 de la même gamme diffèrent parce que leur **moteur** diffère (pannes
du K9K, intervalle du 1.5 dCi, réf OEM propres). Le cluster gamme partagé **ne crée pas** de
duplicate **parce que** R8 différencie chaque R2. La richesse de R2 est exactement
`profondeur(gamme) × spécificité(R8 motorisation)` — d'où l'investissement amont (RAW max) sur
**R1 et R8**, pas sur R2.

### 2. Contrat de contenu structuré (ce que le canon DOIT porter pour être projetable)

Le **canon WIKI** des surfaces enrichies — **gamme** (cluster R1/R3/R4/R6) et **véhicule** (R8),
ainsi que **diagnostic** et **constructeur** (R7) — **DOIT** porter, en plus de la prose
humain-lisible, la représentation **machine-projetable** d'ADR-059 :

- `entity_data.facts[]` : faits atomiques `{key, value, source_id}` (sourcés, `source_id` préfixé
  `db:` | `web:` | `raw:` | `oem:` | `specialist:`).
- `entity_data.blocks[]` : `{role, section, content_md, source_ids[], truth_level}` — contenu
  **role-aware**, reformulé non-verbatim. `truth_level ∈ {db_owned, sourced, inferred, editorial}`.

La **prose** reste l'artefact humain-lisible ; les **blocs/facts** sont la **SoT projetable** (ce
que `build_exports_seo` lit). **R2 ne porte pas de bloc propre** : il consomme les blocs gamme + R8.

**Définition d'un BLOC VALIDE** (le gate, sinon on ne pose rien) : `role` ∈ enum · `section` ∈ enum
contrôlé par rôle · `content_md` non-vide, **FR, non-générique** · `source_ids[]` **préfixés**
(≥1 ; un bloc `db_owned` peut être `db:` seul) · `truth_level` renseigné · **reformulé
non-verbatim**. Échec → **pas de bloc émis** (pas de filler), pas de bloc inventé.

### 2bis. Standard du canon GAMME (R1) — taxonomie de sections + barre tierée

Le canon gamme couvre **l'intégralité des pages** (toute R2 = une gamme ⊕ véhicule) ; **232 unités** =
priorité contenu #1, devant la long-tail moteur (évidence : curer 150 familles moteur ≈ 44 % des
12 062 types indexables ; 232 gammes = couverture totale). Le canon gamme porte un **enum de sections contrôlé
par rôle** :

| Section (`role/section`) | Tier | Source |
|---|---|---|
| `R1_ROUTER/vehicle_selector` | **M** | déterministe (DB) |
| `R3_CONSEILS/function` | **M** | éditorial sourcé |
| `R3_CONSEILS/failure_symptoms` | **M** | éditorial sourcé |
| `R3_CONSEILS/maintenance_interval` | **M** | hybride (axe carburant=DB, valeurs=sourcé) |
| `R4_REFERENCE/variants` | **M** | éditorial sourcé |
| `R4_REFERENCE/compatibility` | **M** | déterministe (DB) |
| `R6_GUIDE_ACHAT/selection_criteria` | **M** | éditorial sourcé |
| `R6_GUIDE_ACHAT/quality_tiers` | R | éditorial sourcé |
| `R4_REFERENCE/standards_norms` | R | éditorial sourcé |
| `R3_CONSEILS/replacement_guidance` | R | éditorial (prescriptif=fail-closed) |
| `R4_REFERENCE/related_parts` | R | déterministe (DB) |
| `R3_CONSEILS/faq` | R | éditorial sourcé |

**M** = obligatoire (plancher) · **R** = recommandée. **Barre tierée déterministe** : **BRONZE** =
7/7 obligatoires valides · **ARGENT** = +≥3 recommandées · **OR** = 5/5 recommandées + média hero
dispo + **≥2 sources indépendantes sur ≥50 % des blocs**. Les 3 sections déterministes
(`vehicle_selector`, `compatibility`, `related_parts`) sont **gratuites sur les 232 gammes** ; les 9
éditoriales sont la curation (et le passage ARGENT→OR = sourcing ≥2 sources/bloc, pas plus de prose).
*(Mêmes principes, profils différents pour véhicule/diagnostic/constructeur — « même pipeline ».)*

**Couture MÉDIA (image-ready, chantier image gouverné À PART).** Le canon **déclare** `media[]`
(`{slot, purpose, alt_text, source, license, status}`) avec `status ∈ {AVAILABLE, DEFERRED}` —
`hero` AVAILABLE depuis `db:pieces_gamme.pg_pic` ; diagrammes/comparatifs DEFERRED. **Le contrat
média est défini ici ; l'acquisition/optimisation d'images (pipeline asset, LCP/CWV, licences) est
un chantier séparé** — sans couplage ni repeinte. Aucune image n'est requise pour la projection.

### 3. Modèle d'enrichissement — RAW + WIKI + DB + KW (les 4 intrants, rôles STRICTS)

- **RAW = faits sourcés (preuve)** : `facts` atomiques **reformulés non-verbatim**, provenance +
  confidence par fait. Jamais de copie longue (un fait n'est pas protégeable, son expression l'est).
  **RAW lit la DB (SELECT) et n'y écrit pas.**
- **WIKI = canon validé + blocs** : couche **humain-validée** ; les `blocks` role-aware sont la
  **SoT projetable**. Le **RAG ne sert pas de source contenu** (chatbot/retrieval only,
  **ADR-031 / ADR-046**) — interdit comme voie de génération.
- **DB = structure catalogue (faits possédés)** : cluster gamme (R1/compat) + véhicule (R8) +
  motorisation + `catalog_signature` (**ADR-066**) — le squelette factuel **vehicle-aware** qui
  rend chaque R2 unique.
- **KW = signal de DEMANDE / INTENTION, GATÉ** (pas du vocabulaire) :
  - `__seo_keywords` est **CONTAMINÉ** (mapping keyword→gamme non fiable : « disque » mappé sur
    `plaquette-de-frein`…). → **seule l'EXISTENCE / le COMPTAGE** de kw (avec seuil) est
    exploitable, comme signal « recherche préparée / demande » — **pas la valeur brute**.
  - **Terme produit = `pieces_gamme.pg_name` autoritaire**, pas le top-kw brut.
  - Un keyword n'enrichit le texte **que s'il contient TOUS les mots-cœur de la gamme** (gate
    `pickGammeKeywordModifier`) ; sinon rejet. **KW pilote l'angle/la priorité, pas le lexique.**
  - Couverture réelle : **19/232 gammes** (filtration + freinage). Gamme sans kw → **signal ABSENT,
    non fabriqué** ; l'intent retombe sur le rôle (`classifyKeywordToRole`), pas sur un kw absent.

### 4. Barre d'excellence + axe motorisation (la clé de jointure R2)

**Barre d'excellence (tier OR)** — un contenu est excellent **ssi** : (a) **sourcé** (≥2 sources
distinctes + provenance) ; (b) **vehicle-aware / motorisation-aware** (la couche R8 porte des faits
réels par moteur, pas du générique) ; (c) **non-dupliqué** (la composante R8 différencie le R2 ;
`catalog_signature` + diversité structurale **ADR-066**, sans filler) ; (d) **demand-targeted**
(angle aligné au signal KW gaté) ; (e) **reformulé non-verbatim**. Filler générique / duplicate
amplifié / kw-brut comme terme = **interdit**.

**Axe motorisation = la clé de jointure qui différencie R2.** Clés normalisées `fuel:` /
`fuel_displacement:` / `engine_family:` + `axis_key_type` explicite. **BRONZE** = regroupement par
**carburant** (DB-fiable, `auto_type.type_fuel`) ; **ARGENT/OR** = raffinement **famille-moteur**
(N47, K9K…) par évidence sourcée — AJOUTÉ, non inventé. **`engine_family:*` ne remplace pas
`fuel:*`** (DB-owned/high) ; il enrichit une sous-clé et ne devient canon que si ≥2 sources
cohérentes OU backfill DB. Les codes moteur EXISTENT (`cars_engine`, dérivation
`__seo_r8_pages.engine_family_key`, `kg_engine_families`) ; le pont par-type `auto_type_motor_code`
est vide (backfill ultérieur) — `engine_code` null **honnête**, non deviné.

### 5. Amendement ADR-083 : la promotion produit les blocs

La porte tiered ADR-083 (TIER A auto / TIER B humain) **n'est franchie que si** le canon porte
`facts` + **≥1 bloc valide** (§2) — en plus des conditions existantes (5 gate wrappers
source/claim/contradiction/risk/confidence + `confidence_score ≥ seuil` + `truth_level ∈ {L1,L2}`
+ ≥2 source-kinds distincts). Fail-closed : pas de bloc valide → reste TIER B / non-projeté.
`build_exports_seo` (ADR-059) demeure **inchangé** (approved-only, 0 LLM / 0 DB / 0 enrichissement).

### 6. Architecture Encyclopédie canonisée (fait foi)

- **4 entités, MÊME PIPELINE, profils DIFFÉRENTS** : gamme · véhicule · diagnostic · constructeur.
  Identique = le flux (générateurs DB-first, RAW→WIKI→porte ADR-083, gates, axe motorisation,
  fail-closed). Différent = profils de complétude + sections par entité. R-roles = consommateurs
  uniformes (cluster gamme ← gamme · R8 ← véhicule · R7 ← constructeur · diagnostic ← diagnostic) —
  flux **ADR-031**, sans exception ni usine séparée.
- **Internal DB first** : seed l'éditorial depuis la connaissance interne curée
  (`kg_engine_families.common_issues`) AVANT scraping ; multi-source = **pondération de confiance**
  (constructeur/OEM > équipementier > fournisseur > presse > forums), **pas exclusion** ; valeurs
  prescriptives exactes à risque physique (couples, pressions, fluides) = **fail-closed**.
- **kg = PROJECTION, pas SoT parallèle** : le diagnostic engine (kg) est un **consommateur** généré
  de l'encyclopédie, non curé en parallèle. Nourrir sa DONNÉE est autorisé même si le MOTEUR
  (r5) est paused — via voie gouvernée, **pas d'INSERT direct** (anti-pattern `__rag_knowledge`).

### 7. Invariants stricts

- **RAW ≠ DB-write.** Flux : `RAW(faits) → WIKI(canon humain-validé + blocs) → exports →
  projection → pages/consommateurs`. Aucun consommateur runtime ne lit RAW.
- **Pas de noindex de contenu.** ADR-086 **n'introduit pas de déclencheur noindex / suppression de
  page**. Une page sans Couche R8 riche **rend ce qui est vrai** (faits DB) + **sans bloc
  fabriqué** ; elle **reste indexée**. L'indexabilité demeure gouvernée **exclusivement** par les
  signaux existants déjà validés (vendabilité — R2 noindex `<1` vendable, PR #916 ; `pg_relfollow` ;
  suppression **manuelle**) — pas par une heuristique de richesse éditoriale.
- **URLs intouchables.** Aucune modification de canonical / routes / slugs (hors périmètre, gelé).

## § Conséquences

### Positives
- Le contenu promu atteint réellement les pages (blocs projetables) ; fin du contenu « faible/vide ».
- **R2 se compose au lieu d'être écrit** : différenciation anti-duplicate *automatique* par la
  couche R8 (motorisation) ; l'effort se concentre sur 2 surfaces (gamme, véhicule), pas N pages R2.
- Une seule source de vérité (l'encyclopédie) ; 4 entités cohérentes ; diagnostic engine nourri
  sans dérive. Replay-safe (blocs versionnés au canon, projetés via ADR-059).

### Négatives / coût
- La promotion devient plus exigeante (blocs sourcés, pas de prose seule) → débit plus lent, mais
  publication réellement utile (qualité > quantité).

### Risques + mitigations
| Risque | Mitigation |
|--------|------------|
| Sur-structuration | BRONZE DB-first suffit pour démarrer ; profondeur OR = enrichissement sourcé ultérieur |
| Prose et blocs divergent | Blocs = SoT projetable ; prose = vue humaine ; gate de cohérence en promotion |
| Tentation d'écrire R2 directement | Contrat : R2 = `gamme ⊕ R8`, pas de blocs propres (ADR-066) |
| Couche gamme partagée perçue comme duplicate | La composante R8 par motorisation différencie chaque R2 ; `catalog_signature` le mesure |
| `engine_family` sur-appliqué (ex. « K9K » sur toutes les Clio) | `engine_family` ne remplace pas `fuel:` ; canon ssi ≥2 sources OU backfill DB |

## § Séquence (post-signature)

1. Étendre les générateurs/injecteurs (déjà construits) pour émettre `facts` + `blocks` role-aware
   **profonds** : surface gamme (cluster R1/R3/R4/R6) + surface véhicule (R8 **par motorisation**).
2. Amender la porte ADR-083 (gate « ≥1 bloc valide »).
3. **Prouver sur 1 gamme exemplaire** (`filtre-a-huile`) : canon gamme riche + 1 véhicule R8 par
   motorisation → composition R2 = R1 ⊕ R8 → export non-vide validé contre le schéma ADR-059 →
   page pilote **shadow** (artefact local, pas la projection DB). Mesurer la barre d'excellence +
   0 régression URL/canonical.
4. **Puis** construire la projection ADR-059 (PR-6 tables/MV + PR-7 RPC/adapter ;
   `seo_runtime_v1` = `PLANNED`) — chantier owner-gated séparé, kill-switch `false` par défaut.
5. **Puis seulement** scaler véhicules / diagnostic / constructeur (même pipeline).

## § Références

- [ADR-059 SEO Runtime Projection](ADR-059-seo-runtime-projection.md) (accepted) — contrat export
  `facts`/`blocks` (schema v1.1.0) ; projection `seo_runtime_v1` = PLANNED.
- [ADR-066 R2 Content Composition v2](ADR-066-r2-content-composition-v2.md) — R2 structural-first ;
  **ADR-086 explicite que les intrants de la composition R2 sont le canon gamme + le canon
  véhicule (R8)**.
- [ADR-083 Tiered WIKI Promotion](ADR-083-tiered-wiki-promotion.md) — **amendé** (gate « ≥1 bloc valide »).
- [ADR-031 Four-Layer Content Architecture](ADR-031-four-layer-content-architecture.md) ·
  [ADR-046 RAG = retrieval chatbot only](ADR-046-rag-retrieval-chatbot-only.md) (RAG ≠ source contenu) ·
  [ADR-033 Wiki Gamme Diagnostic Relations](ADR-033-wiki-gamme-diagnostic-relations.md).
- Preuve de contrat : PR `automecanik-wiki` `feat/export-contract-dimensions-to-blocks` (#43) —
  `dimensions → facts/blocks`, schema v1.1.0, negative test 0 filler.
- Contrat opérationnel : `automecanik-raw/docs/encyclopedia-contract.md` (à linker au canon).
- Mémoires agent liées (monorepo, hors wikilink vault) :
  `feedback_encyclopedia_entity_architecture_motorization_axis`,
  `feedback_source_hierarchy_no_wikipedia_fr_only_injection`,
  `project_adr083_tiered_wiki_promotion_20260610`.
