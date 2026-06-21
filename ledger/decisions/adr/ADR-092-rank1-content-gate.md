---
id: ADR-092
title: "Gate terminal « rank-#1 capable » pour la boucle contenu (le score manquant)"
status: PROPOSED
version: 0.1.0
decision_date: 2026-06-22
decision_makers:
  - Fafa (owner, automecanik.seo@gmail.com)
related_adr:
  - ADR-086 (Content Excellence Contract)
  - ADR-088 (scorer SHADOW 6-dimensions, Phase 3.3)
  - ADR-091 (câblage promotion / Phase B)
  - ADR-040 (coverage-map / provenance des claims)
  - ADR-066 (catalog_signature — monorepo runtime, hors contrat WIKI)
  - ADR-083 (seuil de promotion gouverné, exemple no-op)
extends:
  - ADR-088
  - ADR-091
  - ADR-040
---

# ADR-092 — Gate terminal « rank-#1 capable » pour la boucle contenu (le score manquant)

> **Statut** : PROPOSED. Brouillon vault-ready. Ratification = PR signée OWNER dans `ak125/governance-vault` (G3). L'agent n'écrit pas au vault.
> ADR-092 à attribuer par l'owner à l'ouverture de la PR vault.

**Fichiers étendus / touchés (détail body, pas frontmatter) :**
- `_scripts/shadow_score.py` — moteur 6-dim SHADOW (extension G/H + affinage A/B).
- `_scripts/promote.py` — `evaluate_tier` + flag `PROMOTE_GATE_ENGINE=adr088_6dim` (déjà câblé, **non modifié** par cet ADR).
- `_scripts/check-coverage-map.py` — **À ÉCRIRE** (n'existe pas encore sur `origin/main`), puis à composer dans la substance gate.
- `_meta/schema/entity-data/gamme.schema.json` (+ vehicle/diagnostic/constructeur) — champ optionnel `rank_spotcheck`.

## Contexte

La boucle contenu (`scrape RAW → WIKI → exports → consumers`) sait aujourd'hui vérifier
qu'une fiche n'est **pas fausse** (5 gates atomiques `_scripts/gates/`, claim/source/
contradiction/risk/confidence) et calculer un `confidence_score` legacy
(`compute-confidence-score.py`, 4 composantes 0.40/0.30/0.20/0.10). Mais le skill
`seo-content-loop` §5 (`SKILL.md:83-90`) constate qu'il **manque un SCORE terminal** : les
gates existants « vérifient que le contenu n'est pas faux — ils **ne mesurent pas
l'excellence** » (`SKILL.md:85`). Sans ce gate, rien n'empêche structurellement de
promouvoir une fiche médiocre ou dérivée d'un blog qui ranke.

Le skill §5 nomme cinq axes « rank-#1 capable » (`SKILL.md:87-90`) : ① profondeur vs SERP,
② autorité des sources, ③ différenciation / unicité, ④ motorisation-awareness, ⑤ complétude
topique, avec un seuil donné **en exemple non figé** (« ex. ≥85/100, aucun axe <60 » —
`SKILL.md:90` — le préfixe `ex.` interdit de le traiter comme une magic constant). L'ancrage
canon est **ADR-086 (Content Excellence Contract)**.

**Découverte qui corrige une prémisse périmée.** Le skill §5 et les notes d'audit affirment
que « `shadow_score.py` n'existe pas / n'est pas câblé à `promote.py` ». **C'est faux sur
`origin/main`** (working tree d'audit périmé). Vérifié par `git show origin/main` :

- `_scripts/shadow_score.py` **existe** : scorer SHADOW 6-dimensions
  (ADR-088 Phase 3.3), pur, déterministe, report-only. `WEIGHTS = {A:30,B:20,C:20,D:15,E:10,F:5}`
  (l.32), `PROFILES` entity-aware (dims + planchers), `TIERS [(90,S),(80,A),(60,B),(40,C),(0,D)]`
  (l.43), renormalisation `raw_total/max_applicable*100`, planchers qui **capent** le tier à B +
  `FLOOR_NOT_MET`.
- `_scripts/promote.py` le **câble déjà** comme gate de promotion : `_compute_shadow`
  (l.191) appelle `shadow_score.score` via `_ss.score` (l.210), `evaluate_tier` (l.226) consomme
  le tier comme substance gate **si** `PROMOTE_GATE_ENGINE=adr088_6dim` (lecture env l.268, check l.272), seuil =
  `ADR088_PROMOTE_TIERS={A,S}` (l.66). Le flip du flag est **owner-gated** ; défaut = `legacy`
  (OFF), patron no-op `AUTO_PROMOTE_THRESHOLD=1.01` (l.58).

> **Dette docstring à noter.** Le docstring de `shadow_score.py` (l.4) affirme encore que le
> scorer calcule le score « **sans rien remplacer ni câbler** à `promote.py` ». C'est **périmé** :
> `promote.py` l'importe et le consomme déjà (`_compute_shadow` l.191, `_ss.score` l.210). Cette
> dette docstring doit être corrigée (suivi dans le Plan, étape 7).

Conséquence : **le moteur autoritaire existe déjà.** Il manque seulement les axes rank-#1 du
skill §5 comme dimensions du scorer. La bonne action est d'**ÉTENDRE** `shadow_score.py`,
**jamais** de bâtir un gate parallèle (interdit par CLAUDE.md, sanctionné en red-team sur les
designs B et C).

## Décision

### Principe

Le gate terminal « rank-#1 capable » = **deux nouvelles dimensions déterministes G et H**
ajoutées au framework 6-dim existant de `shadow_score.py`, plus des **planchers entity-aware**
correspondants. Le gate de promotion **reste le tier** consommé par `promote.py` via le flag
`PROMOTE_GATE_ENGINE=adr088_6dim` déjà câblé — **aucun nouveau décideur, aucun nouveau
wrapper, aucune nouvelle constante de seuil inline.** La renormalisation
`raw_total/max_applicable*100` absorbe automatiquement les nouveaux poids ; `promote.py` lit
`r.tier` (agnostique du nombre de dimensions) et n'est **pas modifié** par cette extension.

### Les 5 axes du skill §5 → mesures (DÉTERMINISTE-first)

Quatre axes sont mesurables déterministiquement (frontmatter + body + manifest + coverage-map
locaux ; zéro réseau, zéro LLM, zéro random). Un axe ne l'est pas et reste humain.

| Axe §5 | Mesure | Dimension | Déterministe ? |
|---|---|---|---|
| ② Autorité des sources | moyenne `CONFIDENCE_NUMERIC` des coverage_entries (ADR-040) **renforcée** par préfixe `source_ids` (`oem:`/`specialist:` vs `web:`, schéma `gamme.schema.json:17`) + `cross_check_status` du `decision_brief` | `_dim_A` affiné + check provenance | OUI |
| ④ Motorisation-awareness | fraction d'engine-blocks portant `applies_to.engine_codes` validés contre le reality-manifest **renforcée** par `compatibility_factors` (`db_aligned_count`/`proven_url_count`, `motorisation_profiles` `db_status=PASS_DB_ALIGNED`, `gamme.schema.json:~135-196`) | `_dim_B` affiné + `_dim_H` | OUI |
| ⑤ Complétude topique | sections obligatoires remplies vs `SECTIONS_REQUIRED` (gamme=5, `compute-confidence-score.py:46-52`) + nombre de blocs éditoriaux **sourcés** émis (anti-padding `_dim_C`) + H2 (`_dim_E`) | `_dim_C`/`_dim_E` + `_dim_G` | OUI (structurel) ; sémantique **non** déterministe sans référentiel d'angles |
| ③ Différenciation / unicité (**part data-fiche**) | présence et ampleur de **data catalogue jointe à la fiche** : `model_count_distinct`, `len(type_ids)`, `len(motorisation_profiles)` (`gamme.schema.json:~140-186`) | `_dim_H` | OUI **par proxy de présence** |
| ① Profondeur vs SERP | « couvre les tops +davantage » | — | **NON** (voir Angles morts) |

**Provenance par bloc (substance vérifiable).** `$defs.editorialBlock` (`gamme.schema.json:10-26`)
exige `content_md` (≥60), `source_ids` préfixés `^(db\|web\|raw\|oem\|specialist):` et
`truth_level` (`db_owned/sourced/inferred/editorial`). Le `decision_brief` exige `source_kind`
(`deterministic_transform`/`rag_candidate`) et `cross_check_status`
(`WEB_CONFIRMS_RAG>WEB_ONLY>RAG_ONLY>WEB_DIFFERS_FROM_RAG>NEITHER`). Ces champs **existent
déjà** et alimentent les dimensions sans rien inventer.

### Fermeture du trou de self-attestation (correctif red-team, OBLIGATOIRE avant flip)

Le red-team a montré que `_dim_A` (`shadow_score.py:61`) lit **uniquement**
`coverage_map[].confidence` — un enum **auteur-déclaré** — sans vérifier `source_status`
(`pending_capture`/`captured`/`verified`), ni FK-checker `source_slug` contre
`source-catalog.yaml`. Conséquence : une fiche paraphrasée d'un blog avec
`confidence: high` fabriqué obtient `_dim_A=30/30`.

> **État réel de l'enforcement FK aujourd'hui (origin/main).** Le FK `source_slug → source-catalog.yaml`
> est **déjà enforced**, mais **pas** par un script `check-coverage-map.py` — celui-ci **n'existe pas
> encore sur `origin/main`**. L'enforcement vit aujourd'hui dans : (a) `coverage-map.schema.json`
> (FK **strict** : `source_slug` DOIT exister dans `_meta/source-catalog.yaml`, **FAIL si absent**) ;
> (b) le workflow CI cross-repo `cross-repo-source-catalog-gate.yml` (`gate_source_catalog_raw_refs`,
> checkout cross-repo). Le script `check-coverage-map.py` est un **livrable à ÉCRIRE** (référencé
> comme « Phase 0.D, hors scope ADR-040 immédiat » dans le schéma), pas une dépendance existante.

**Correctif retenu** (additif, déterministe) : `_dim_A` doit **pondérer par
`source_status`** (un `pending_capture` ne compte pas comme un `verified`) **et** la substance
gate doit composer un FK-checker `source_slug → source-catalog.yaml`. Comme ce FK-checker
réutilisable (`check-coverage-map.py`) **n'existe pas encore sur `origin/main`**, le correctif
exige de l'**ÉCRIRE PUIS composer** `check-coverage-map.py` dans la substance gate — une
coverage-entry pointant un slug absent du catalogue est neutralisée, pas créditée. Sans ce
correctif, l'axe ② reste gameable et le gate ne mesure pas l'autorité réelle.

### Calcul, seuil, et insertion sans doublon

- **Calcul.** Chaque dimension → points bruts ; total renormalisé sur les dimensions
  applicables ; tier par `TIERS` (`shadow_score.py:43`). Les planchers entity-aware **capent**
  le tier à B + émettent `FLOOR_NOT_MET` si une dimension critique du type est sous son floor —
  c'est le mécanisme rank-#1. G et H entrent dans `WEIGHTS` (`shadow_score.py:32`) + `PROFILES`
  (dims + floors par entité, ex. gamme : floor G complétude, floor H différenciation ;
  vehicle : floor H motorisation).
- **Seuil = le TIER existant, pas une magic constant.** Auto-promotion **ssi** `tier ∈ {A,S}`
  (`promote.py:66` `ADR088_PROMOTE_TIERS`), seuils `TIERS` gouvernés. L'« ex. ≥85/100, aucun
  axe <60 » du skill se traduit en : tier S/A + planchers entity-aware — **pas un nombre codé
  en dur**. Les valeurs numériques des floors G/H sont **à calibrer en fenêtre shadow
  report-only AVANT tout flip**, comme les floors A/B/C/D actuels.
- **Insertion.** Point déjà existant : `_compute_shadow` (`promote.py:191`) → `_ss.score`
  (`promote.py:210`) → `evaluate_tier` (`promote.py:226`). En ajoutant G/H **dans**
  `shadow_score`, ils deviennent automatiquement le gate terminal **sans toucher `promote.py`**.
  Les 5 gates atomiques restent **en amont** (non doublonnés : ils mesurent le non-faux, le
  scorer mesure l'excellence). `compute-confidence-score.py` reste le moteur legacy (coexistence
  observable old↔new, ADR-088 §F). Le CLI `shadow_score --all` reste l'outil report-only
  d'observation de distribution avant cutover.

### Ce qui reste HUMAIN (non délégable)

1. **Axe ① profondeur-vs-SERP** : non automatisable localement (voir Angles morts) →
   **spot-check humain borné**, jamais dans le scorer.
2. **Sécurité — la vraie barrière** : l'invariant « une fiche sécurité ne s'auto-promeut pas »
   est porté à **deux** points sur `origin/main` (PR #61/#63) : (a) **`promote.py::_is_safety_proposal`**
   (l.80, appelé en tête d'`evaluate_tier` l.237) force TIER B avant tout calcul de substance ; (b)
   **`gate_safety_unsourced`** (`quality-gates.py:474`), composé par les 5 gates atomiques **en amont**
   d'`evaluate_tier`, **plus** le flag fail-closed (`promote.py` défaut `legacy`,
   `AUTO_PROMOTE_THRESHOLD=1.01` no-op). Les deux délèguent désormais à un **SINGLE SOURCE**
   `_scripts/safety_families.py::is_safety_proposal` (PR #63, import paresseux des deux côtés). Le périmètre
   **réellement gardé** est `SAFETY_FAMILY_LABELS = {freinage, direction, distribution, electricite-safety,
   airbag, suspension}` (`safety_families.py:21-23`) + détection par slug (`SAFETY_SLUG_PATTERNS`) :
   chaque `diagnostic_relations[]` doit satisfaire son `source_policy` (sources présentes ;
   `manual_review` exige `reviewed`). **`_dim_F` n'est PAS ce mécanisme** : `_dim_F`
   (`shadow_score.py:153-162`) est **générique** (review_status approved +0.5 / lineage_id +0.3 /
   exportable +0.2) et ne porte **aucune logique catégorie-sécurité**. `promote.py` est fail-closed →
   tout doute = TIER B humain.

   > **Périmètre sécurité unifié et élargi (implémenté PR #63).** L'ancienne divergence entre
   > `compute_auto_promotion` (monorepo) et `gate_safety_unsourced` (wiki) est **éliminée** : la
   > constante `SAFETY_FAMILIES` locale à `quality-gates.py` n'existe plus ; les deux modules wiki
   > importent `safety_families.is_safety_proposal`. `airbag` et `suspension` **SONT désormais gardés**
   > (présents dans `SAFETY_FAMILY_LABELS`, `safety_families.py:21-23` + `SAFETY_SLUG_PATTERNS` l.25-44).
   > Le gap de périmètre signalé dans les brouillons antérieurs est **fermé**. Cet ADR ne prétend
   > rien protéger de plus que ce single source.
3. **Flip du gate** : passer `PROMOTE_GATE_ENGINE=adr088_6dim` est **owner-gated** + exige
   ADR-088/cet-ADR acceptés au vault + les critères §F mesurés. Défaut OFF inchangé.
4. **Calibration** des floors G/H et **tuning** des formules v0 (explicitement tunables,
   `shadow_score.py:16-17`) : décision owner guidée par la distribution shadow observée.

Le LLM peut **proposer/enrichir** (advisory) mais n'est **JAMAIS** juge de promotion.

## Conséquences

**Positives.**
- La boucle contenu obtient enfin un gate terminal d'excellence, déterministe et testé, sans
  système parallèle (conforme « ÉTENDRE, jamais réinventer »).
- Le mécanisme rank-#1 (cap par plancher entity-aware) empêche le TIER A même si le total ≥80
  quand un axe critique (autorité, complétude, différenciation) est sous son floor.
- Observable de bout en bout : `floors_failed`, `FLOOR_NOT_MET`, `shadow_score` dans
  `promotion_evidence` ; distribution old↔new en fenêtre shadow.
- Zéro régression tant que le flag est OFF (défaut `legacy`).

**Négatives / coûts.**
- Rééquilibrer `WEIGHTS` change les scores historiques observés en shadow → **un nouveau run
  de cutover-criteria est requis avant tout flip** (la comparaison de distribution ADR-088 §F
  doit être refaite).
- L'axe ① n'est pas couvert par le scorer : passer le gate ≠ garantie de rang SERP. **Ne pas
  surclamer « rank-#1 »** au sens position SERP.
- Le correctif `_dim_A` + composition `check-coverage-map.py` (**à écrire**) ajoute une
  dépendance interne à la substance gate (fail-closed, sans I/O réseau).

## Alternatives rejetées

1. **LLM-juge (l'axe ① jugé par un modèle).** Rejeté : viole la doctrine
   LLM-advisory-jamais-juge et casse le déterminisme pur testé. Un spot-check humain assisté
   par un avis LLM **recopié** dans le verdict serait du « LLM-juge laundering via humain
   tampon » — explicitement interdit. L'axe ① reste un verdict humain, pas une sortie LLM.

2. **Réinventer `shadow_score` / créer un gate composite parallèle (designs B et C).** Rejeté
   (red-team B=34, C=52) : `shadow_score` + son câblage `promote.py` existent déjà ; un
   `run_rank1_gate` ou un wrapper `gates/rank_readiness_gate.py` (a) duplique le tier déjà
   appliqué, (b) viole `test_no_new_atomic_gate` (les wrappers composent des `gate_*`
   existants, n'en créent pas), (c) bâtit sur une prémisse périmée. La capacité existe ;
   on l'**étend**.

3. **Signal SERP live injecté dans le scorer.** Rejeté : casse le déterminisme pur, exige une
   I/O réseau dans le chemin de promotion, et n'est pas reproductible (pas de repro hors
   contexte). La profondeur-vs-SERP reste hors scorer.

4. **Fabriquer un champ `diversity_score` / `catalog_signature`.** Rejeté : `diversity_score`
   est **absent** du contrat WIKI (`grep 0` sur `_scripts/` + `_meta/schema/`) ;
   `catalog_signature` vit côté monorepo runtime (ADR-066), pas dans ce contrat. La
   différenciation est mesurée par la **data catalogue réelle** déjà au schéma + le
   sibling-distinctness délégué hors-scorer (skill app `r8-diversity-check`).

## Garde-fous

- **Déterministe.** G et H sont des fonctions **pures** (frontmatter + body + manifest +
  coverage locaux). Aucun import LLM, aucun `random`, aucune I/O réseau. Vérifié par les tests
  à valeurs fixes étendus.
- **Additif.** WEIGHTS/PROFILES étendus, `_dim_G`/`_dim_H` ajoutés, `_dim_A`/`_dim_B` affinés
  (formules v0 tunables, signatures inchangées, framework figé). `gamme.schema` étendu d'un
  champ **optionnel** (spot-check) — pas de breaking change. `promote.py` **non modifié**.
- **Flag.** Le gate ne devient décisionnel que sous `PROMOTE_GATE_ENGINE=adr088_6dim`
  (owner-gated, défaut OFF). Patron no-op réutilisé (`AUTO_PROMOTE_THRESHOLD=1.01`).
- **Observable.** `floors_failed` / `FLOOR_NOT_MET` / `shadow_score` exposés ; fenêtre shadow
  report-only obligatoire avant flip. Pas de fallback silencieux (un signal manquant
  **dégrade** le score → TIER B humain, avec flag observable, jamais un faux auto-pass).
- **No magic constant.** Le seuil = TIER + planchers gouvernés, pas un nombre inline ;
  l'« ex. ≥85/60 » du skill reste illustratif jusqu'à gravure ADR.
- **Sécurité intacte.** L'invariant « fiche sécurité jamais auto-promue » est garanti par
  `promote.py::_is_safety_proposal` (l.80, appelé l.237) + `gate_safety_unsourced`
  (`quality-gates.py:474`) en amont, tous deux délégant au single source
  `safety_families.is_safety_proposal` (PR #63), + le flag fail-closed
  (`promote.py`), **pas** par `_dim_F` (générique). Le gate ne peut que **rétrograder** (ajouter
  des raisons de bloquer), jamais auto-approuver au-delà des couches inférieures — invariant
  downgrade-only à verrouiller par test (voir Plan, étape 3).

## Plan

> Lecture seule ici : design only. Toute mutation passe par branche dédiée + PR, jamais sur
> `main` ni sur la branche wiki dormante interdite.

1. **`_scripts/shadow_score.py`** (additif) : ajouter G,H à `WEIGHTS` (l.32 ; rééquilibrer pour
   somme brute lisible, ex. A30 B15 C15 D10 E5 F5 G10 H10) ; ajouter G,H dans `PROFILES[*].dims`
   + `floors` entity-aware ; implémenter `_dim_G` (complétude structurelle absolue + profondeur
   absolue proxy) et `_dim_H` (différenciation data catalogue de fiche) **purs** ; les brancher
   dans `computed{}`. Renormalisation/tiers/planchers inchangés.
2. **`_scripts/check-coverage-map.py`** (**À ÉCRIRE** — n'existe pas sur `origin/main`) **PUIS**
   **`_scripts/shadow_score.py` (`_dim_A`/`_dim_B`)** (correctif red-team) : écrire le FK-checker
   réutilisable `source_slug → source-catalog.yaml` (FK strict, déjà spécifié par
   `coverage-map.schema.json` + appliqué en CI par `cross-repo-source-catalog-gate.yml`), puis
   `_dim_A` (l.61) pondère par préfixe `source_ids` OE/specialist **et** par `source_status`
   (≠`pending_capture`) ; **composer `check-coverage-map.py`** dans la substance gate ; `_dim_B`
   intègre `compatibility_factors` (`db_aligned_count`/`proven_url_count`, `motorisation_profiles`
   `PASS_DB_ALIGNED`).
3. **`_scripts/test_shadow_score.py`** (additif) : cas à valeurs fixes
   `test_dim_G_completeness`, `test_dim_H_catalog_differentiation`, `test_profiles_include_GH_floors`,
   `test_floor_caps_tier_when_rank1_axis_below_floor`, `test_dim_A_rejects_pending_capture_source`,
   **et `test_gate_can_only_downgrade_never_auto_approve`** (invariant downgrade-only : l'ajout
   de G/H ne peut qu'**AJOUTER des reasons** / capper le tier à la baisse, jamais transformer un
   refus en auto-approbation au-delà des gates atomiques en amont).
4. **`_meta/schema/entity-data/gamme.schema.json`** (+ vehicle/diagnostic/constructeur,
   additif optionnel) : champ `rank_spotcheck:{verdict enum pass|fail, checked_by, checked_at,
   serp_note}` — porteur du **seul** axe non déterministe (profondeur-vs-SERP), posé par humain,
   non requis.
5. **Fenêtre shadow report-only** : observer la distribution old↔new+G/H, calibrer les floors
   G/H, refaire le run cutover-criteria (ADR-088 §F).
6. **Dépend de ADR-091 Phase B** pour le câblage final / cutover : le flip
   `PROMOTE_GATE_ENGINE=adr088_6dim` n'est activé qu'après acceptation vault + critères mesurés.
   `promote.py` n'est **pas** retouché par cet ADR (le câblage y est déjà).
7. **Dette docstring** : corriger le docstring de `shadow_score.py` (l.4) qui affirme encore
   « sans rien remplacer ni câbler à `promote.py` » — **périmé** depuis que `promote.py`
   l'importe et le consomme (`_compute_shadow` l.191, `_ss.score` l.210).

## Angles morts honnêtes

- **Axe ① profondeur-vs-SERP : NON automatisable déterministiquement.** « Couvre les tops
  +davantage » exige soit un fetch SERP live (interdit/hors scope dans un scorer de promotion),
  soit un LLM-juge (interdit comme juge). Les signaux DB ne comblent pas le trou :
  `demand_level` (tout-LOW), `difficulty_level` (tout-MED), `trends_index` (tout-0),
  `keyword_total` (24/241 seulement) sont dégénérés. **Proposition assumée** : un **spot-check
  humain borné** (1 question fermée : « cette fiche couvre-t-elle autant ou plus que les 3
  premiers résultats ? »), stocké en `rank_spotcheck`, lu comme plancher (cap B +
  `RANK_SPOTCHECK_MISSING` si absent). Le scorer ne mesure qu'une **profondeur absolue proxy**
  (nb sections/sources/facts/longueur), **jamais** la comparaison SERP — et ce proxy est
  reconnu **faible** (un mur de texte paraphrasé maximise la longueur sans excellence).
- **Part « unique vs concurrents » littérale de l'axe ③** : exige le SERP → hors scorer
  (seule la part data-catalogue de fiche est mesurée).
- **Complétude sémantique** (tous les intents/PAA réellement couverts) : non déterministe sans
  référentiel d'angles gouverné.
- **Différenciation au niveau fiche vs agrégat de gamme** : attention à ne PAS créditer la
  différenciation via des agrégats `gamme_aggregates` (`top_brands`, `vlevel_counts`) qui sont
  **constants entre fiches sœurs** d'une même gamme — `_dim_H` doit lire des signaux **de la
  fiche** (`type_ids`/`motorisation_profiles` propres au document), pas un agrégat hérité
  gratuitement.
- **Périmètre sécurité unifié (gap fermé PR #63)** : `gate_safety_unsourced` (et
  `promote.py::_is_safety_proposal`) délèguent désormais au single source
  `safety_families.is_safety_proposal`, couvrant `SAFETY_FAMILY_LABELS = {freinage, direction,
  distribution, electricite-safety, airbag, suspension}` (`safety_families.py:21-23`) + détection par
  slug. `airbag` et `suspension` **sont gardés**. Reste hors-périmètre (non prétendu par cet ADR) :
  toute famille hors de ces 6 labels et des `SAFETY_SLUG_PATTERNS` — extension délibérée via le
  single source, non spéculative.
- **Self-attestation résiduelle** : tant que le correctif §2 (source_status + écriture/
  composition de `check-coverage-map.py`) n'est pas mergé, l'axe ② reste gameable ; le catch
  d'une fiche blog-dérivée pure dépend alors uniquement de `_dim_H`/floor — **non mergeable pour
  flip en l'état**.

---

_ADR-092 à attribuer. Ratification = PR vault signée OWNER (G3). L'agent n'écrit pas au vault._