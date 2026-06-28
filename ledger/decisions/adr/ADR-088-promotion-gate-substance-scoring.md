---
id: ADR-088
title: "Gate de promotion de substance — score à planchers (6-dim/100) + engineBlock factuel : amende ADR-083 (formule de score) et ADR-086 (contrat de contenu structuré)"
status: accepted
date: "2026-06-17"
decision_date: "2026-06-17"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-083", "ADR-086"]
extends: ["ADR-059", "ADR-033"]
related_adr: ["ADR-033", "ADR-059", "ADR-083", "ADR-086", "ADR-089"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-088 (PROPOSÉ — numéro à confirmer au vault) : Gate de promotion de **substance** (score à planchers + engineBlock factuel)

> **DRAFT vault — préparé en /tmp, NON appliqué.** À porter dans `ak125/governance-vault`
> via PR signée G3 (single-write-point Deploy VPS). **Amende ADR-083** (formule de score / porte tiered)
> et **ADR-086** (contrat de contenu structuré / engineBlock). Référence **ADR-089** (coverage-map canon),
> **ADR-059** (projection), **ADR-033** (sas wiki), `source-policy §9.1` — sans les abroger.
> Owner décide. Rien n'est écrit dans le vault par l'assistant.

- **Statut** : Accepted
- **Date** : 2026-06-17
- **Amende** : **ADR-083** (§Décision — formule `confidence_score` + bar TIER A) · **ADR-086** (§2 contrat structuré + §5 amendement promotion) — **n'abroge pas**, **durcit**
- **Référence inchangée** : ADR-059 (`build_exports_seo.py` approved-only, 0 LLM/0 DB/0 enrichissement) · `source-policy.md §9.1` (type→max_confidence) · coverage-map = `_meta/schema/coverage-map.schema.json` (schéma wiki — **backing vault = ADR-089**)
- **Auteur du draft** : assistant (préparation) — **validation + signature = owner**
- **Preuves** : PR `ak125/automecanik-wiki#49` (report-only, CI verte) ; plan `/home/deploy/.claude/plans/en-m-moire-pour-la-federated-creek.md`

---

## Contexte (problème mesuré — PR #49, dry-run report-only)

ADR-083 a débloqué la promotion (porte tiered déterministe). **Mais le score actuel récompense la
conformité APPARENTE, pas la vérité exploitable** — mesuré, pas supposé :

- **Cause racine** : la dimension Sources lit l'**agrégat frontmatter `source_refs`** avec un **défaut
  `medium`=0.6** quand `confidence` est absente. Une fiche « gagne » donc **~0.24 sur 0.40 sans rien
  déclarer**. Pire : déclarer honnêtement `confidence: low` (0.12) score **moins** que le silence (0.24)
  → **incitation perverse**. Dry-run corpus : **14/14 proposals = `CONFIDENCE_MISSING`**.
- **~0.48 point de l'écart vers 0.80 est STRUCTUREL** (titres + liens), pas de la qualité de fond : un
  auteur atteint ~0.74 **sans renforcer une seule source**.
- **`entity_data` n'est pas validé contre son schéma** : la délégation à `entity-data/<type>.schema.json`
  est documentée dans `frontmatter.schema.json` mais **NON enforced**. Dry-run : **7/14 proposals
  non-conformes** (ex. Golf 5 : `known_issues_by_engine` keyé `BKC`/`all_engines` en tableaux de strings
  au lieu d'engineBlocks sourcés → « riche par moteur » en apparence, non projetable R8 en réalité).
- **L'ADR-086 §5** (promotion exige `facts` + ≥1 bloc valide) **n'est pas enforced** dans `promote.py`.

## Tension à résoudre

Un score qui monte avec structure + liens + diversité **déclarative** sélectionne du contenu « joli mais
creux » → l'inverse de l'objectif #1 (et un risque « Scaled Content Abuse » côté Google). **Mais** flipper
les gates en hard-fail **maintenant casserait `main`** (la moitié du corpus est non conforme). On ne peut
donc ni laisser le gonflage, ni durcir brutalement.

→ Résolution : **mesurer d'abord (report-only, déjà fait — PR #49), durcir ensuite derrière l'ADR + une
migration**, et faire en sorte que le score **récompense la preuve par claim, la granularité moteur, la
richesse sourcée et la projectabilité** — pas la forme. Le gate reste un **plancher de qualité**, jamais un
générateur de contenu #1 (le #1 vient de la boucle SCRAPING-LARGE).

## Décision

### A. Score = 6 dimensions / 100, avec **PLANCHERS bloquants** (remplace la formule 4-composants 0-1)

| Dim | Poids | Mesure |
|---|---|---|
| A Sources & preuves | 30 | force §9.1 **par claim** via coverage-map |
| B Granularité moteur/véhicule | 20 | applies_to/excluded_from par code, axe correct |
| C Richesse utile | 20 | items diagnostic **rattachés à un evidence-block sourcé** |
| D Mapping commerce | 15 | related_gammes résolues + commerce_intent |
| E Structure & liens | 10 | sections canoniques + wikilinks résolus |
| F Review / traçabilité | 5 | review + lineage + exportable contrôlé |

**TIER A impossible** (planchers — le cœur, le total ne suffit jamais) si : `A<22/30` **OU** `B<15/20` **OU**
`C<15/20` **OU** `D<10/15` **OU** confidence absente **OU** source faible seule **OU** scope moteur générique
**OU** bloc non projectable **OU** `engineBlock`/bloc factuel invalide. **Tiers** : D(0-39)/C(40-59)/B(60-79)/
A(80-89)/S(90+). *Sans planchers, le 100 pts reproduit le défaut actuel.*

### B. Caps par type de source (dérivés de `source-policy §9.1`, non réinventés)
`forum`/`wiki_externe`/`blog_consumer` (low) seul ≤ 8/30 · `blog_pro`/`brochure`/`marketing` (medium) seul
≤ 15/30 · source sans `confidence` déclarée = **0/30** (plus de défaut `medium`). → **un forum ne peut
jamais porter une fiche en TIER A.**

### C. Dimension A = **coverage-map (par claim)** — pas l'agrégat `source_refs`
C'est la correction de la **cause racine** : le scoring lit la `coverage-map` (`_meta/schema/coverage-map.schema.json` :
`claim→source_slug+confidence+source_policy`), ce qui force une **preuve par claim** + l'existence d'une coverage-map
avant de scorer A. ✅ **Backing vault = ADR-089** (Content Coverage-Map Canon) : la coverage-map est
canonisée par ADR-089 (≠ ADR-040 = *seo-roles-canon-ts-side-only*, ≠ ADR-048 = *canon-enforcement-coverage*).
Validée par `check-coverage-map.py` (FK strict vers `_meta/source-catalog.yaml`).

### D. Suppression du défaut `medium` → `BLOCKED_CONFIDENCE_MISSING`
`confidence` absente n'est plus tolérée silencieusement. **Périmètre de durcissement** : blocage réel réservé
aux **nouveaux blocs factuels** (`engineBlock`/`evidence[]`) créés/modifiés ; le stock legacy `source_refs`
reste **report-only** jusqu'à migration (pas de bruit massif rétroactif).

### E. Amendement ADR-086 — `engineBlock` devient un **fait vérifiable** (pas de `facts[]` parallèle)
Le `engineBlock` (vehicle.schema.json) porte désormais : `claim`, `applies_to{engine_codes[],years[]}`,
`excluded_from{engine_codes[],reason}`, `evidence[]{source_ref,strength,confidence,status}`, `projectability`.
Ajout `related_gammes[]`/`commerce_intent[]` sur `vehicle`. **Enforcement réel d'ADR-086 §5** (`facts` + ≥1
bloc valide) dans `promote.py::evaluate_tier`. Validation `entity_data` contre `entity-data/<type>.schema.json`
(la délégation documentée devient enforced).

### F. Sûreté de déploiement (no blast-radius)
- **Report-only d'abord** : la mesure est déjà livrée (PR #49, exit 0, non câblé). **Acquis.**
- **Score v2 en SHADOW** : old (0-1) + new (100) calculés en parallèle, comparés sur le corpus, **avant** tout
  cutover. Cutover = décision owner après dry-run vert.
- **Pas de rétro-démotion** : le canon déjà `approved` n'est jamais démoté en silence ; audit report-only des
  fiches qui échoueraient les nouveaux planchers.
- **`no_disputed_claims:false` plafonne au TIER B** (revue humaine), ne BLOQUE pas (l'honnêteté n'est pas punie).
- **Reality-check 0-DB** : `applies_to.engine_codes`/`related_gammes` validés contre un **manifest commité**
  (export `auto_type_motor_code`/`pieces_gamme`) — **jamais** de requête DB dans le gate (invariant
  `test_no_db_imports`).

## Invariant — AVANT / APRÈS

| | AVANT (ADR-083/086) | APRÈS (cet ADR) |
|---|---|---|
| Score | 4 comp. 0-1, **défaut `medium`** | 6 dim/100, **planchers**, caps §9.1, **0 défaut** |
| Dim Sources | agrégat `source_refs` (fiche) | **coverage-map, par claim** (ADR-089) |
| confidence absente | tolérée (0.6) | **BLOCKED_CONFIDENCE_MISSING** |
| `entity_data` | non validé | **validé contre entity-data/<type>.schema.json** |
| engineBlock | content_md+source_ids+truth_level | **+ claim/applies_to/excluded_from/evidence/projectability** |
| ADR-086 §5 | documenté, non enforced | **enforced dans promote.py** |
| Bascule | — | **shadow + report-only-first + no rétro-démotion** |
| Génération / projection (ADR-059) | — | **inchangé** (0 LLM, approved-only) |

## Conséquences

**Positives** : le score sélectionne la **vérité exploitable** (preuve/claim, granularité moteur, richesse
sourcée, projectabilité) ; l'incitation perverse disparaît ; conforme E-E-A-T + garde-fous Google ; réutilise
l'existant (§9.1, coverage-map, engineBlock, 5 wrappers, promote.py) — **0 système parallèle, 0 OPA**.

**Risques + mitigation** : durcir casserait le corpus → **report-only-first (acquis) + shadow + migration
gouvernée** ; complexité du score → **planchers explicites + observabilité `promotion_evidence`** ; **rollback**
= seuil no-op (1.01) + score v2 désactivable, retour identique à l'actuel sans redeploy.

## Implémentation (à faire APRÈS acceptation ADR — owner-sponsorisé, repo wiki)

1. **Schémas** `_meta/schema/` : enrichir `vehicle.schema.json::engineBlock` (applies_to/excluded_from/evidence/
   projectability) + `related_gammes`/`commerce_intent` ; `frontmatter.schema.json` câble la validation
   `entity_data`→entity-data/. **Additif, owner applique.**
2. **Scorer** `compute-confidence-score.py` : formule 6-dim/100 + caps + planchers ; A depuis coverage-map ;
   **suppression du défaut `medium`** ; **mode SHADOW** (old+new).
3. **Gates** : convertir les checks report-only de PR #49 en gates ; enforcer ADR-086 §5 + conformité schéma
   dans `promote.py` (vehicle-aware) ; **après migration** du corpus non conforme.
4. **Manifest** engine_codes/gammes commité (reality-check 0-DB).
5. **Migration** corpus : amener les proposals existantes aux nouveaux planchers (ou les laisser TIER B).
6. **Dry-run probant** + bascule seuil = décision owner séparée.

## Ce que cet ADR NE fait PAS
Ne modifie pas `build_exports_seo.py`, ni la projection ADR-059, ni le schéma `exports-seo`, ni la génération
(toujours filter+transform sourcé, 0 LLM). Ne crée **aucun `facts[]` parallèle** en entrée véhicule (le
`engineBlock` porte la sémantique de fait). Ne supprime aucun gate. **N'active rien** : la mesure reste
report-only tant que l'owner ne sponsorise pas l'implémentation + la migration. Le **#1 reste produit par la
boucle SCRAPING-LARGE**, pas par ce gate (plancher, pas plafond).

---

## Précisions issues de la revue adversariale (2026-06-17)
Quatre angles morts — ils **ne contredisent pas la décision, ils la durcissent** :

1. **Planchers ENTITY-TYPE-AWARE** (sinon on bloque du contenu légitime non-véhicule — le défaut même qu'on
   combat) : les planchers héritent des **profils par entité d'ADR-086 §2bis**. Le plancher **B (granularité
   moteur) ne s'applique qu'aux `vehicle`** ; **D (commerce) aux `vehicle`/`gamme`** ; `constructeur` /
   `diagnostic` / `support` ont leur propre profil. Une dimension **non applicable à un type est neutralisée**
   (exclue du total ET des planchers, le total étant **renormalisé sur les dimensions applicables**), jamais
   comptée 0.
2. **Séquençage = gel de promotion assumé** : A se calcule depuis la coverage-map ; tant qu'elles ne sont pas
   générées, A≈0 → **auto-promotion ~0 au cutover (INTENTIONNEL, pas un bug)**. Prérequis dur : génération des
   coverage-maps + migration du corpus **AVANT** d'abaisser le seuil. À acter pour éviter la surprise.
3. **Manifest reality-check = fraîcheur garantie** : le manifest engine_codes/gammes doit être **régénérable +
   freshness-checké** (job de refresh + garde anti-stale) ; rejet UNIQUEMENT sur **absence confirmée**, jamais sur
   manifest périmé (sinon faux négatifs sur des codes réels récents).
4. **Critère de cutover shadow MESURABLE** (« dry-run vert » étant subjectif) : bascule autorisée seulement si,
   sur le corpus : (i) **nouvelles auto-promotions ⊆ anciennes** (v2 ne promeut rien que v1 bloquait) ; (ii) les
   fiches known-bad (Golf 5) tombent en TIER B/C ; (iii) après migration **≥1 fiche atteint le nouveau TIER A**
   (le gate n'est pas inerte en permanence).

## Questions ouvertes (à trancher par l'owner en signant)
1. **Un ADR ou deux ?** Regroupé ici car le score B (granularité) dépend de l'engineBlock enrichi. Scinder
   possible (083-bis « score à planchers » + 086-bis « engineBlock factuel ») si granularité gouvernance voulue.
2. **Backing vault de la coverage-map** : ✅ établi = **ADR-089** (Content Coverage-Map Canon), ADR dédié.
3. **`related_rules`** (frontmatter) : hérités d'ADR-086 (`G1, AI1, T1`, même domaine) — à confirmer/ajuster.
4. **Statut d'ADR-083** : encore `proposed` au vault alors que `promote.py` est mergé. Cette signature peut le
   passer `accepted` (cohérence) — ou le laisser. Ta décision.

## Action owner (vault G3 — procédure vérifiée, voir runbook `APPLY-ADR-088.md`)
1. Relire ce draft ; ajuster poids/planchers/caps + les 4 questions ci-dessus.
2. Assigner le n° (**088** proposé ; dernier = 087).
3. Copier `/tmp/vault-drafts/ADR-088-*.md` → `governance-vault/ledger/decisions/adr/` (owner uniquement).
4. **MAJ MOC** : `python3 _scripts/sync_moc_decisions.py --write` (sinon orphelin → gate **G2 Zero Orphelin**
   bloque le push) ; vérifier `grep ADR-088 ops/moc/MOC-Decisions.md` + `_scripts/check-orphans.sh .`.
5. **Commit signé G3** (pas `--amend`, pas force-push) ; `git log --show-signature -1` doit afficher `Good`.
6. Push + PR **avec la ligne `Self-review verdict: APPROVE`** dans le body (gate `check-self-review-marker.sh`).
   Si la branche est BEHIND : `git merge origin/main` signé — **jamais** `gh pr update-branch` (strip Ed25519 → G3 FAIL).
7. Une fois accepté : sponsoriser Phase 3 (schéma + scorer shadow + manifest + migration corpus) dans le repo wiki.
