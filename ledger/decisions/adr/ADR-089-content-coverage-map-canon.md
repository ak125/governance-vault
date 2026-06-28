---
id: ADR-089
title: "Content Coverage-Map Canon — claim↔source artefact gouverné (_meta/schema/coverage-map.schema.json), backing de la dimension A du score de substance ADR-088"
status: accepted
date: "2026-06-19"
decision_date: "2026-06-19"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-039", "ADR-059", "ADR-083", "ADR-086", "ADR-088"]
related_adr: ["ADR-031", "ADR-033", "ADR-039", "ADR-040", "ADR-048", "ADR-059", "ADR-083", "ADR-086", "ADR-088"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-089 : Content Coverage-Map Canon (claim ↔ source, backing de la dim A ADR-088)

> **Accepté.** Établit le backing de gouvernance que **ADR-088 §C / §Q2** signalait absent :
> la coverage-map (`_meta/schema/coverage-map.schema.json`, repo wiki) est désormais canon.
> Validateur : `check-coverage-map.py` (wiki PR — FK strict source-catalog, report-only).
> **N'abroge aucun ADR.**

- **Statut** : Accepted
- **Date** : 2026-06-19
- **Établit** : l'autorité canon de `_meta/schema/coverage-map.schema.json` (repo `automecanik-wiki`)
- **Référence inchangée** : ADR-059 (`build_exports_seo.py` approved-only) · ADR-040 (SEO Roles Canon TS — **ce n'est PAS** la coverage-map malgré le titre du schéma) · ADR-048 (canon-enforcement-coverage — audit canon, **différent**)
- **Auteur du draft** : assistant (préparation) — **validation + signature = owner**

---

## Contexte (gap de backing mesuré)

ADR-088 introduit le **score de substance** dont la **dimension A (Sources & preuves, 30 pts)**
est calculée **par claim** en lisant la **coverage-map** plutôt que l'agrégat frontmatter
`source_refs`. Cette coverage-map existe **comme schéma** dans le repo wiki :
`_meta/schema/coverage-map.schema.json` (`title: "Coverage Map Schema v1.0 — ADR-040 §2"`,
`coverage_entries[]: {claim_id, section, source_slug, evidence_type, confidence, source_policy, source_status}`,
FK strict vers `_meta/source-catalog.yaml`).

**Le trou de gouvernance, vérifié sur `origin/main` :**

1. La `description` du schéma s'auto-attribue à « **ADR-040 §2 'Coverage Map as canonical
   artifact'** » et note « *Source de vérité : ... ADR-040 ... (vault PR pending)* ». Or le
   **vrai ADR-040 du vault** est `ADR-040-seo-roles-canon-ts-side-only` (« SEO Roles Canon
   R0..R8 côté TypeScript ») — **il ne parle pas de coverage-map**. Le « ADR-040 §2 » référencé
   n'existe pas : la PR vault « pending » n'a jamais été ouverte sous ce numéro.
2. **ADR-048** (`canon-enforcement-coverage`) couvre l'**audit de couverture canon** (mirrors,
   backlinks), **pas** le contrat claim↔source de contenu.
3. ADR-088 §C l'écrit explicitement : « *la coverage-map existe comme **schéma wiki** mais n'a
   **pas d'ADR vault dédié** vérifié (ni ADR-040, ni ADR-048). Cet ADR-088 doit soit **établir**
   ce backing, soit le **référencer une fois créé** — à trancher par l'owner.* »

Conséquence : la dim A d'ADR-088 lirait un artefact **non gouverné** (schéma orphelin, pointant
un §ADR inexistant). Un score de substance ne peut pas s'appuyer sur une source de vérité dont
l'autorité n'est pas canonisée — sinon on réintroduit le « registry ad-hoc » que la doctrine
interdit.

## Tension à résoudre

Soit (a) on **étend ADR-088** d'une section qui canonise la coverage-map (couplage fort,
ADR-088 déjà mergé/à-accepter, gonfle son scope), soit (b) on **crée un ADR dédié** qui
canonise l'artefact une fois pour toutes — réutilisable par dim A (ADR-088), par le validateur
`check-coverage-map.py`, et par tout futur consommateur. ADR-088 §Q1 préfère ne pas scinder le
*score* ; mais le *backing de l'artefact* est une **préoccupation distincte du score** → un ADR
séparé est la solution structurelle (1 artefact gouverné = 1 ADR), pas du bricolage.

→ **Décision : créer ce backing dédié (ADR-089)** et faire pointer ADR-088 §C/§Q2 dessus. Aucune
réinvention : on **canonise l'existant** (schéma + source-catalog + validateur déjà construits).

## Décision

1. **`_meta/schema/coverage-map.schema.json` (repo `automecanik-wiki`) devient un artefact canon
   gouverné par cet ADR-089.** Sa SoT de gouvernance est ce fichier vault ; son SoT technique
   reste le JSON Schema versionné (`schema_version` semver). Toute évolution du schéma =
   amendement ADR (comme `exports-seo` sous ADR-059, `frontmatter` sous ADR-039).

2. **Le `title` et la `description` du schéma sont corrigés** pour ne plus pointer un « ADR-040
   §2 » inexistant :
   - `title` : « Content Coverage-Map Schema v1.0 — ADR-089 »
   - `description` : « *Source de vérité de gouvernance : governance-vault ADR-089
     (Content Coverage-Map Canon). Backing de la dimension A du score de substance ADR-088.* »
   (Patch additif/cosmétique côté wiki, **owner-sponsorisé après acceptation** — voir §Séquence ;
   aucun champ structurel touché, le contrat reste rétro-compatible.)

3. **Contrat claim↔source (inchangé sur le fond, désormais canonisé)** : chaque
   `coverage_entries[]` lie un `claim_id` stable à un `source_slug` **existant dans
   `_meta/source-catalog.yaml` (FK strict)**, avec `evidence_type`, `confidence` **déclarée**
   (jamais défaut implicite — cohérent avec ADR-088 §D « suppression du défaut `medium` »),
   `source_policy` (§9.1 type→max_confidence) et `source_status`. Une entrée sans source-catalog
   correspondante = **rejet** (anti-gonflement du score, fail-closed).

4. **Place dans la chaîne (aucun chevauchement) :**
   - **ADR-039** = canon frontmatter proposal (Zod/JSON Schema) — *quoi* dans la fiche.
   - **ADR-089 (ce doc)** = canon coverage-map — *quelle preuve pour quel claim*.
   - **ADR-086** = contrat de contenu structuré (facts/blocks/engineBlock) — *quoi est projetable*.
   - **ADR-088** = score de substance — *combien vaut la preuve* (dim A **lit** la coverage-map ADR-089).
   - **ADR-059** = projection export — *inchangé* (approved-only, lit le canon, pas la coverage-map).

5. **Invariants stricts (mêmes que la doctrine) :** 0 LLM, 0 DB dans la validation coverage-map
   (reality-check via `source-catalog.yaml` commité, jamais de requête DB — cohérent avec
   l'invariant `test_no_db_imports` d'ADR-088 §F) ; FK strict vers source-catalog ; pas de
   défaut de confidence ; le RAG n'est jamais source (ADR-031/046).

## Invariant — AVANT / APRÈS

| | AVANT | APRÈS (cet ADR) |
|---|---|---|
| Backing de la coverage-map | **aucun ADR** ; schéma pointe « ADR-040 §2 » inexistant | **ADR-089** (dédié) |
| dim A ADR-088 | lit un artefact non gouverné | lit un artefact **canon** (ADR-089) |
| Évolution du schéma | ad-hoc | **amendement ADR-089** |
| `check-coverage-map.py` | validateur sans canon | validateur **adossé** au canon ADR-089 |
| Projection ADR-059 | — | **inchangée** (ne lit pas la coverage-map) |

## Conséquences

**Positives** : la dim A d'ADR-088 s'appuie sur une source de vérité **gouvernée** ; fin du
schéma orphelin pointant un §ADR inexistant ; 1 artefact = 1 ADR (anti registry ad-hoc) ;
réutilise l'existant (schéma + source-catalog + validateur déjà construits) — **0 système
parallèle**.

**Négatives / coût** : un ADR de plus à maintenir ; un patch cosmétique du `title`/`description`
du schéma wiki (owner-sponsorisé, additif).

**Risques + mitigation** : divergence schéma↔ADR → règle « toute évolution du schéma =
amendement ADR-089 » + freshness check existant ; FK source-catalog cassé → validateur
fail-closed (déjà le cas).

## Ce que cet ADR NE fait PAS

Ne modifie pas `build_exports_seo.py` ni la projection ADR-059 ; ne change pas la sémantique du
score ADR-088 (il en **fonde la dim A**) ; ne touche pas ADR-040 (SEO Roles, distinct) ni
ADR-048 (audit canon, distinct) ; n'introduit aucune lecture DB dans le gate ; ne crée aucune
nouvelle table ni nouveau registre.

## § Séquence (post-signature, owner-sponsorisé, repo wiki)

1. Patch additif du `title`/`description` de `_meta/schema/coverage-map.schema.json` (pointe
   désormais ADR-089, plus « ADR-040 §2 »). Rétro-compatible, champs structurels inchangés.
2. ADR-088 : remplacer en §C / §Référence / §Q2 « backing à établir » par « backing = ADR-089 » ;
   ajouter `ADR-089` à `related_adr[]`.
3. Câbler la dim A du scorer (ADR-088 Phase 3) sur la coverage-map canonisée.

## § Références

- [ADR-088 Gate de promotion de substance](ADR-088-promotion-gate-substance-scoring.md) — dim A lit la coverage-map ; §C/§Q2 demandent ce backing.
- [ADR-086 Content Excellence Contract](ADR-086-encyclopedia-editorial-content-contract.md) — facts/blocks/engineBlock projetables.
- [ADR-083 Tiered WIKI Promotion](ADR-083-tiered-wiki-promotion.md) — porte tiered consommatrice du score.
- [ADR-059 SEO Runtime Projection](ADR-059-seo-runtime-projection.md) — projection inchangée (ne lit pas la coverage-map).
- [ADR-039 Wiki Proposal Frontmatter Zod Canon](ADR-039-wiki-frontmatter-zod-canon.md) — canon frontmatter (distinct du claim↔source).
- ADR-040 (SEO Roles Canon TS) et ADR-048 (canon-enforcement-coverage) : **NE backent PAS** la coverage-map (clarification explicite).
- Artefact technique : `automecanik-wiki/_meta/schema/coverage-map.schema.json` (`origin/main`) + `_meta/source-catalog.yaml` (FK) + `check-coverage-map.py`.

## Action owner (vault G3)

1. Relire ce draft ; confirmer le n° **089** (prochain libre après 088 ; 084 et 089+ libres).
2. Copier `/tmp/vault-drafts/ADR-089-content-coverage-map-canon.md` → `governance-vault/ledger/decisions/adr/` (owner uniquement).
3. Mettre à jour ADR-088 (§C/§Q2 + `related_adr`) dans le **même commit signé** (cohérence).
4. `python3 _scripts/sync_moc_decisions.py --write` puis vérifier la row 089.
5. Commit **signé G3** + PR avec `Self-review verdict: APPROVE`.
