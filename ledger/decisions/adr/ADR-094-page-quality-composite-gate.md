---
id: ADR-094
title: "Gate cross-domaine page-quality (composite) : orchestre substance WIKI ⊗ surface rendue ⊗ runtime ⊗ diversité ⊗ lineage"
status: proposed
version: "1.0.0"
date: "2026-06-24"
decision_date: ""
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: []
related_adr: ["ADR-092", "ADR-066", "ADR-067", "ADR-059", "ADR-086", "ADR-088", "ADR-091", "ADR-093"]
related_rules: []
related_incidents: []
created: 2026-06-24
updated: 2026-06-24
---

# ADR-094 — Gate cross-domaine page-quality (composite)

> Brouillon préparé en lecture seule, hors vault. La ratification = PR signée par l'owner dans `ak125/governance-vault` (commit signé SSH, single write point DEV). L'agent n'écrit JAMAIS au vault et ne s'auto-approuve pas (mainteneur solo).

## Statut

Proposed.

## Contexte

### Le verdict de page n'a pas de home

La boucle contenu sait, séparément, juger plusieurs domaines — mais **aucun ADR ne les
orchestre en une décision de page unique « cette page est-elle prête à rivaliser ? »** :

- **ADR-092** (`extends` ADR-088/091/040) mesure la **substance WIKI** — un scorer 6+2-dim
  (`_scripts/shadow_score.py`) produisant un `tier`. C'est un gate **strictement WIKI** ; son
  titre « gate terminal rank-#1 capable » est terminal **du scorer de substance**, pas de la page.
- **ADR-066** (monorepo runtime) mesure la **diversité catalogue** via `catalog_signature` +
  LSH, seuil gouverné `0.92`. **ADR-067** l'amende : `>0.92 → REVIEW + enrichissement`, et
  **interdit strictement la suppression/canonicalisation automatique** d'une page.
- **ADR-059** (+ ADR-090) gouverne la **projection SEO runtime** (No Direct Page SQL ; le verdict
  `projection_operational` de l'orchestrateur `raw_to_wiki_content_loop_pilot.py`).

Deux preuves **n'ont aucun canon** : (a) la **surface SEO rendue** (title/desc/H1 réellement
servis en SSR) ; (b) le **lineage** (le contenu *scoré* en WIKI est exactement celui *projeté*
puis *rendu*). Sans elles, un bon `tier` de substance ne prouve **pas** que la page rend ce
contenu, ni qu'elle est unique dans le catalogue.

### Le problème de fond : le DUPLICATE

Le frein n°1 à la progression du site est le **contenu dupliqué** (R8/R2 quasi-identiques entre
motorisations sœurs, prose R1/R3 partagée verbatim entre gammes). Aucun gate actuel ne **ferme**
en exigeant une diversité réelle **à la fois intra-sœurs ET cross-gamme** comme condition de
publication. C'est l'objet du composant `CLUSTER_DIVERSITY_PASS` ci-dessous.

### Nature de cet ADR : ORCHESTRATION, pas nouveau mesureur

Cet ADR **∧-compose des verdicts existants** ; il **ne re-mesure rien** et **n'introduit aucun
scoreur parallèle** (interdit par CLAUDE.md « no-parallel-system » + ADR-092 §Alternatives, qui
rejette explicitement les gates composites parallèles). Il `extends: []` (aucune sémantique
d'amendement d'un parent) ; les ADR qu'il orchestre vivent dans `related_adr`. ADR-092 reste le
gate **terminal de substance WIKI** ; ADR-094 est le gate **terminal de page** (composite) — deux
terminaux **distincts par domaine**, aucune redéfinition d'ADR-092.

## Décision

On grave un **verdict de page composite, additif, fail-closed, flag-gated, observable, réversible**.

### Le verdict composite

```
PAGE_QUALITY_COMPOSITE_PASS  (étiquette informelle : « page rank-#1 capable »)
  = CONTENT_SUBSTANCE_PASS        # ADR-092 : tier ∈ {A,S} ET floors_failed == []  — RÉUTILISÉ, jamais recalculé
  ∧ SEO_SURFACE_PASS             # check EXTERNE monorepo (cf. §Surface) — RÉFÉRENCÉ, non défini/possédé ici
  ∧ SSR_RUNTIME_PASS             # ADR-059 : projection consommée ∧ SSR conforme ∧ intégrité runtime
  ∧ CLUSTER_DIVERSITY_PASS       # ADR-066/067 : intra-sœurs ET cross-gamme (cf. §Diversité)
  ∧ LINEAGE_PASS                 # scoré == projeté == rendu (soft jusqu'à extension schéma, cf. §Lineage)
  ∧ NO_HARD_BLOCKER             # liste énumérée (cf. §Hard-blockers)
```

- **Le nom canonique du verdict est `PAGE_QUALITY_COMPOSITE_PASS`** (et non `PASS_RANK1_CAPABLE`,
  qui *impliquerait* une position SERP garantie). `PASS_RANK1_CAPABLE` est conservé comme
  **étiquette informelle** dans la prose du plan ; il ne doit pas être le flag machine.
- **`missing ≠ false`** : si un composant externe est absent / en erreur, le verdict **n'est pas
  `false` mais `HOLD` (indéterminable → fail-closed)** — jamais un repli silencieux qui publierait.
- **Composition SHALLOW** : le verdict ∧-compose des booléens déjà calculés indépendamment ; il
  ne ré-implémente aucun composant. Si ADR-059/066 changent leur logique, ADR-094 consomme le
  même booléen de sortie.

> **Décidé maintenant, appliqué quand les composants atterrissent (anti-overclaim).** Cet ADR
> **décide** le verdict + sa gouvernance ; il n'**applique** rien tant que (a) ADR-091 puis ADR-092
> ne sont pas `accepted` (en cours, cf. §Plan séquence) ; (b) le scoreur de surface monorepo +
> l'extension schéma lineage (ADR-059) ne sont pas mergés ; (c) l'owner n'a pas donné le GO. Avant
> cela, `PAGE_QUALITY_COMPOSITE_PASS` évalue à **`HOLD` (fail-closed)** — gate **gouverné**, pas
> encore **enforce** (même pattern qu'ADR-092 `check-coverage-map.py` À ÉCRIRE / ADR-093
> `refutation_gate.py` NOUVEAU : un ADR décide un gate dont l'implémentation est planifiée).
> Les noms de composants sont des **étiquettes que cet ADR forge** pour la composition ; chacune
> **consomme** la mesure d'un domaine existant — `CONTENT_SUBSTANCE_PASS` ⟵ tier ADR-092 ;
> `SSR_RUNTIME_PASS` ⟵ `projection_runtime_pass` existant ⊕ conformité SSR ; `CLUSTER_DIVERSITY_PASS`
> ⟵ mesures ADR-066/067 — **aucune nouvelle source de vérité, aucun scoreur parallèle**.

### N'altère PAS les verdicts de l'orchestrateur existant

`PAGE_QUALITY_COMPOSITE_PASS` est **strictement additif**. Il **ne redéfinit pas** et **n'altère
pas** les 3 verdicts déjà gravés dans `raw_to_wiki_content_loop_pilot.py` sur wiki `origin/main`
(`7ecd1c2`, bloc « Verdicts » L305-310 + alias `loop_closed` L340) :

```
projection_operational = static_chain_pass ∧ projection_runtime_pass     # 5 PROJECTION_RUNTIME_KEYS, hors outcome
business_loop_closed   = projection_operational ∧ outcome_status == PASS
loop_closed            = business_loop_closed                            # alias back-compat
```

`PAGE_QUALITY_COMPOSITE_PASS ≠ loop_closed` : une page peut être qualité-prête **avant**
l'outcome externe (7/14/28 j). À l'inverse, `PAGE_QUALITY_COMPOSITE_PASS=true` est **impossible**
sans `CONTENT_SUBSTANCE_PASS` (la substance est gating).

### Surface (`SEO_SURFACE_PASS`) — check externe, jamais un scoreur parallèle

Le scoreur de surface (title/desc/H1 rendus) vit en **monorepo**, **SHADOW/report-only**, ses
**seuils sont gouvernés** et il **réutilise le seuil collision `0.92` gouverné (ADR-066)** — pas
de magic constant. Cet ADR **déclare l'exigence** d'un check de surface et **référence** ce check ;
il ne le **définit ni ne le possède** (sa gouvernance = owner monorepo). *(Renommable
`SSR_SURFACE_VALIDATION` au gré de l'owner.)* Les hard-blockers de surface (title/desc/H1 absent,
mauvaise gamme/véhicule, prix faux) sont actifs immédiatement, indépendamment de la calibration.

### Diversité (`CLUSTER_DIVERSITY_PASS`) — ADR-066/067, deux volets, jamais d'auto-suppression

```
CLUSTER_DIVERSITY_PASS =
      0 EXACT_COLLISION indexable (intra-sœurs ET cross-gamme)
    ∧ 0 REVIEW non résolu
    ∧ 0 DISTINCT_COSMETIC (différenciation cosmétique sans substance)
    ∧ chaque LEGITIMATELY_SHARED documenté + décidé (owner)
```

Mesuré par `catalog_signature` (sha256 OEM + sous-groupes) + LSH/MinHash, **deux volets** :
**(1) intra-cluster** (motorisations sœurs d'un même modèle) et **(2) cross-gamme** (prose
R1/R3 partagée verbatim entre gammes différentes). **ADR-067 préservé** : `>0.92 → REVIEW +
enrichissement` (gate humain) ; **jamais d'auto-suppression ni d'auto-canonicalisation**. Une
variation accent-only (FR, normaliser NFC avant fingerprint) → `manual review`, jamais auto.

### Lineage (`LINEAGE_PASS`) — soft jusqu'à l'extension de schéma

```
LINEAGE_PASS ⇔ wiki_version_id == projection_source_version == resolver_evidence_version == page_render_projection_version
champs = version_id (UUID WIKI_ACCEPTED) + content_hash (sha256 des facts/blocks)   # rescore confidence ≠ change content_hash
```

Les champs `resolver_version` / `render_version` requièrent une **extension de schéma de
projection (ADR-059), chantier PR séparé**. **Jusqu'à sa livraison**, `LINEAGE_PASS` est une
**sonde binaire sur les champs existants** (`content_hash` du snapshot immuable ADR-059) en mode
**log-only / observable, pas fail** : on observe les divergences sans bloquer. `HARD_BLOCKER_
LINEAGE_MISMATCH` n'est **armé** qu'après livraison de l'extension. La dépendance est **explicite**
(pas un gate qui « échouerait toujours » faute de champs).

### Hard-blockers (`NO_HARD_BLOCKER`) — énumérés

```
NO_HARD_BLOCKER = NOT (
     LINEAGE_VERSION_MISMATCH       # une fois le schéma livré
   ∨ PROJECTION_CORRUPT
   ∨ EXPORT_MISSING
   ∨ SSR_INCOMPLETE
   ∨ JSON_LD_MALFORMED
   ∨ PLACEHOLDER_UNRESOLVED         # #…# | {…} | %…%
   ∨ EXACT_COLLISION_INDEXABLE      # collision exacte sœur OU cross-gamme indexable
   ∨ SAFETY_FAMILY_UNREVIEWED       # cf. §Sécurité
)
```

Chaque condition est un **flag observable** dans `promotion_evidence`.

### Anti-overclaim — escalade à 3 niveaux

`PAGE_QUALITY_COMPOSITE_PASS` (qualité interne) `→ OPERATIONAL_READY` (activation : consumer live
sous flag, rollback prouvé, perf OK) `→ OUTCOME_POSITIVE` (externe : CTR/position/indexation,
réduction collisions, commerce stable). **Aucun ne garantit une position SERP.** Le benchmark
(filtre-à-huile pg7 + Clio III, déjà très complets) est une **barre de non-régression**, pas une
cible de score à gonfler : une page déjà optimale → `0 changement = PASS_ALREADY_OPTIMAL` valide.

## Conséquences

### Ce qui devient gouverné

- Une page n'est « qualité-prête » que si elle **rend** réellement sa substance, est **unique**
  (intra + cross-gamme), et est **traçable** de bout en bout — pas seulement « bien scorée en WIKI ».
- Le duplicate cross-gamme, jusqu'ici non gaté, devient une **condition de publication**.

### Ce qui reste (feu vert owner / humain)

- **Activation** : tout est SHADOW d'abord, flag OFF par défaut ; le passage report-only → enforce
  est un **GO owner explicite** (pas d'auto-escalade).
- **Sécurité** : classification **exclusivement** par `safety_families.is_safety_proposal` (SoT
  6-familles, PR #63) — **non dupliquée ici** ; `is_safety ⇒ revue humaine`, jamais auto.
- **Diversité** : `>0.92 → REVIEW` humain, jamais d'auto-suppression (ADR-067).
- **Lineage** dur : armé seulement après l'extension de schéma ADR-059.

### Risque résiduel

1. **Seuils de surface non figés** tant que la calibration pilote (Clio III + benchmark) n'est pas
   owner-validée → mitigé par la fenêtre shadow report-only.
2. **Axe profondeur-vs-SERP** non automatisable → spot-check humain borné (`rank_spotcheck`).
3. **Drift inter-domaines** (substance WIKI vs surface monorepo vs diversité) → mitigé par la
   composition shallow (chaque domaine garde sa SoT) + observabilité `__seo_event_log`.

## Alternatives rejetées

- **Greffer le verdict dans ADR-092 (fusion).** REJETÉ comme défaut — ADR-092 est strictement
  WIKI-substance ; y absorber la surface/SSR/lineage/diversité créerait un scope-creep dans la
  gouvernance monorepo et **deux « gates terminaux »** dans un même document. Une orchestration
  séparée (cet ADR) garde ADR-092 propre. *(Steelman fusion = « EITHER_OK » sous condition d'un
  §Orchestration nettement séparé ; l'owner a tranché pour le nouvel ADR.)*
- **Créer un nouveau scoreur de surface « maison ».** REJETÉ — on **référence** un check externe
  gouverné (monorepo, shadow, seuils gouvernés), on n'invente pas un scoreur parallèle (ADR-092
  §Alternatives, CLAUDE.md no-parallel-system).
- **Nommer le verdict `PASS_RANK1_CAPABLE`.** REJETÉ comme nom machine — overclaim SERP. Conservé
  comme étiquette informelle ; le flag machine est `PAGE_QUALITY_COMPOSITE_PASS`.
- **Auto-suppression / canonicalisation sur collision.** REJETÉ — viole ADR-067 (`>0.92 → REVIEW`,
  suppression manuelle uniquement).
- **Armer `LINEAGE_PASS` dur avant l'extension de schéma.** REJETÉ — gate qui échouerait toujours
  faute de champs ; soft/log-only jusqu'à livraison, dépendance explicite.

## Garde-fous

- **No-silent-fallback.** Composant externe absent/erroné → `HOLD` (indéterminable, fail-closed),
  jamais publication par défaut. Flag OFF par défaut.
- **Observable.** Chaque évaluation trace `page_quality_components` = `{content_substance_pass,
  seo_surface_pass, ssr_runtime_pass, cluster_diversity_pass, lineage_pass, no_hard_blocker}` +
  le verdict, dans `promotion_evidence` / `__seo_event_log` — audit par composant. Pas de canary
  externe : réutilise la trace interne.
- **Réversible.** Additif pur : aucune ligne retirée d'un garde-fou existant ; rollback config-only
  (flag OFF) = retour exact au comportement d'aujourd'hui.
- **Compose, ne réinvente pas.** Aucun nouveau décideur de promotion (promotion WIKI = ADR-092/
  083/088 ; auto-review = ADR-093). Le verdict cross-domaine est un **gate de page**, pas un gate
  de promotion WIKI.

## Plan de mise en œuvre (changements additifs)

> **Séquence canon** : (i) ratifier **ADR-091** (`proposed→accepted`) puis **ADR-092** (dépendance
> dure 092 `extends` 091) ; (ii) ratifier cet ADR-094. Le flip `PROMOTE_GATE_ENGINE` (ADR-092/093)
> reste owner-gated et hors de cet ADR.

1. **`[wiki]` orchestrateur** `raw_to_wiki_content_loop_pilot.py` — **AJOUTER** `page_quality_ready`
   (= `PAGE_QUALITY_COMPOSITE_PASS`) + preuves surface/lineage. **NE PAS recréer** les 3 verdicts
   existants ; un check automatisé « 3 verdicts inchangés vs `7ecd1c2` » garde contre toute dérive.
2. **`[mono]` scoreur de surface** — SHADOW/report-only, seuils gouvernés, réutilise `0.92` ;
   émet un event `__seo_event_log` par évaluation. *Additif.*
3. **`[mono]` ADR-059 — extension schéma projection** (`resolver_version`/`evidence` dans les blocs)
   = chantier PR séparé ; arme `LINEAGE_PASS` dur une fois livré. Jusque-là, sonde soft/log-only.
4. **`[mono]` diversité** — `catalog_signature` + LSH intra **ET** cross-gamme ; rapports séparés ;
   `>0.92 → REVIEW` (ADR-067), jamais auto-suppression. NFC avant fingerprint.
5. **Intégrité graphe (PR vault de suivi, post-ratification)** — ajouter `extended_by` /
   `related_adr: ADR-094` dans ADR-092, ADR-066, ADR-059 ; documenter la séquence
   `ADR-093 (auto-review → promotion WIKI) → ADR-094 (gate de page)`.
6. **`governance-vault`** (PROPOSÉ, NON ÉCRIT par l'agent) — cet ADR, préparé en `/tmp/`, ouvert en
   PR par l'owner ; lié depuis `ops/moc/MOC-Decisions.md` (G2 zéro-orphelin) ; merge signé G3 = ratification.

## Angles morts (honnêteté)

- **Surface non figée.** Les seuils de `SEO_SURFACE_PASS` restent provisoires tant que la
  calibration pilote n'est pas owner-validée (P15 du plan). Avant ça, surface = guidance, pas verdict.
- **Lineage partiel.** Tant que l'extension de schéma ADR-059 n'est pas livrée, `LINEAGE_PASS`
  observe sans bloquer ; un mismatch réel passe en log, pas en hard-blocker.
- **Sémantique non vérifiée.** La diversité prouve la non-collision structurelle, pas la véracité
  sémantique du contenu (déléguée à ADR-092/093 + sources WIKI).
- **Composition shallow.** ADR-094 fait confiance aux booléens des domaines amont ; un bug dans un
  composant amont se propage — mitigé par l'observabilité par-composant.

---

*Ratification = PR vault signée par l'owner (`@fafa`). L'agent a préparé ce brouillon en lecture seule, hors `/opt/automecanik/governance-vault`, et ne l'écrit pas au vault. Frontmatter conforme au schéma `_scripts/schemas/adr.schema.json` (status lowercase, `extends`/`related_adr` conventionnels) et à la structure d'ADR-093 (`origin/main`). Verdicts orchestrateur (`projection_operational`/`business_loop_closed`/`loop_closed`) vérifiés contre wiki `origin/main` (`7ecd1c2`, assignations L308/L310/L340). `safety_families.py` 6-familles (PR #63 `8d491a1`). Statuts ADR (088 accepted / 091 proposed / 092 PROPOSED) vérifiés contre vault `origin/main` (fetch 2026-06-24). ADR-094 = prochain numéro libre. Toutes les refs suivent `origin/main`, jamais le checkout DEV local.*
