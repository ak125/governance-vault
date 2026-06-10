# ADR-083 (PROPOSÉ — numéro à confirmer au vault) : Promotion WIKI auto-tiered

> **DRAFT vault — préparé en /tmp, NON appliqué.** À porter dans `ak125/governance-vault`
> via PR signée G3 (single-write-point Deploy VPS). Amende **ADR-033** (sas wiki / autorité de
> promotion) et référence **ADR-059** (SEO Runtime Projection) sans le modifier.
> Owner décide. Rien n'est écrit dans le vault par l'assistant.

- **Statut** : Proposed
- **Date** : 2026-06-10
- **Amende** : ADR-033 §promotion (review_status: approved = humain) — **n'abroge pas**, **étend l'autorité**
- **Référence inchangée** : ADR-059 (`build_exports_seo.py` reste « approved-only », 0 LLM / 0 DB / 0 enrichissement)
- **Auteur du draft** : assistant (préparation) — **validation + signature = owner**

---

## Contexte (problème mesuré)

- Pipeline contenu R **entièrement codé + testé + gouverné** (ADR-059) : `scripts/wiki_promotion/` → `proposals/` → **promotion** → `wiki/<entity>/<slug>.md (approved)` → `build_exports_seo.py` → `exports/seo/` → DB → R.
- **Goulot unique vérifié (2026-06-10)** : `wiki/gamme/` = **0 gamme approuvée**. La chaîne ne démarre pas faute d'entité promue. L'invariant actuel exige **validation humaine de chaque fiche** → ne passe pas à l'échelle (objectif : 241 gammes, varier les R, ranker #1).
- Demande owner : **automatiser la promotion**, sans détruire le ranking.

## Tension à résoudre

Supprimer toute validation = contenu auto-produit non contrôlé → **Google « Scaled Content Abuse » + perte E-E-A-T + risque sécurité** (contenu réparation auto proche YMYL : freinage, direction). Cela **dé-range** — l'inverse de l'objectif #1. La validation humaine **est** une partie du moat de classement.

→ On ne **supprime** pas le moat ; on **automatise la porte** et on **réserve l'humain au résidu risqué**.

## Décision

La promotion vers `review_status: approved, exportable: true` n'est plus « humain uniquement ».
Elle est décidée par une **porte tiered déterministe** `_scripts/promote.py` qui **compose les gates EXISTANTS** (`_scripts/gates/` : source/claim/contradiction/risk/confidence + `compute-confidence-score.py`) — **aucun nouveau gate, 0 LLM, 0 DB, 0 enrichissement** (mêmes invariants que `build_exports_seo.py`).

### TIER A — AUTO-APPROVE  (`reviewed_by: "skill:promoter@<sha>"`, `auto_promoted: true`)
Promu automatiquement **SSI TOUT** est vrai :
- les **5 gate wrappers** = `PASS` (aucun `warn`/`fail`) ;
- `confidence_score ≥ AUTO_PROMOTE_THRESHOLD` (**proposé 0.80**, owner-tunable) ;
- `truth_level ∈ {L1, L2}` (faits vérifiés / règles métier — **jamais L3 hypothèses, jamais L4 heuristiques**) ;
- **0** `safety_unsourced`, **0** `catalog_leak`, **0** `commercial_promise`, **0** contradiction ;
- **≥ 2 `source_refs` de `kind` distincts** (composante 0.10 de la formule confidence).

### TIER B — HUMAN-REQUIRED  (`reviewed_by: "<email>"`)
Tout le **résidu** : un gate `warn`/`fail`, `confidence_score < seuil`, `truth_level ∈ {L3, L4}`, ou tout flag safety/contradiction/commercial/catalog. Reste `in_review` jusqu'à approbation humaine. **C'est là que vit le jugement E-E-A-T + sécurité.**

### Fail-closed + observabilité (no silent fallback)
- Toute promotion écrit : `auto_promoted` (bool), `promotion_tier` (`A|B`), `promotion_evidence` (résultats gates + score), `reviewed_by`, `reviewed_at`.
- **Erreur de porte → reste `in_review`** (jamais d'auto-approve sur erreur). Aucun repli silencieux.

## Invariant — AVANT / APRÈS

| | AVANT (ADR-033) | APRÈS (cet ADR) |
|---|---|---|
| Autorité `approved` | humain uniquement (`reviewed_by: <email>`) | **porte tiered** : auto (Tier A) **ou** humain (Tier B) |
| Bar auto | — | 5 gates PASS + score≥0.80 + L1/L2 + 0 risque |
| Humain | chaque fiche | **uniquement le résidu risqué** |
| `build_exports_seo.py` | approved-only | **inchangé** (approved-only) |
| Projection/runtime (ADR-059) | — | **inchangé** |
| Génération contenu | filter+transform sourcé | **inchangé** (0 LLM, 0 invention) |

> Le moat n'est pas supprimé : il est **déplacé** du « tampon manuel sur tout » vers « bar déterministe rigoureux + humain sur le risque ». Pattern « auto-apply safe, isolate ambiguous ».

## Conséquences

**Positives** : promotion passe à l'échelle (débloque 0/241) ; E-E-A-T/sécurité préservés (auto réservé au L1/L2 sourcé sans risque ; tout safety/contradiction → humain) ; conforme aux garde-fous Google (oversight humain sur le risque + bar qualité déterministe + sourcé) ; additif (schema enum `approved` existe déjà ; `reviewed_by: skill:<name>` déjà autorisé pour L4 — on l'étend à L1/L2 **sous la porte**).

**Risques + mitigation** : un seuil trop bas laisserait passer du médiocre → seuil **0.80** + L1/L2 only + tous gates PASS ; observabilité (`promotion_evidence`) permet l'audit a posteriori ; **rollback** : `AUTO_PROMOTE_THRESHOLD = 1.01` (inatteignable) → 100% humain, **identique à aujourd'hui**, sans redeploy.

## Implémentation (à faire APRÈS acceptation ADR — owner-sponsorisé, repo wiki)

1. `automecanik-wiki/_scripts/promote.py` : compose `gates/*` + `compute-confidence-score.py` ; modes `--dry-run` / `--apply` ; path-strict ; tests Pytest miroir de `build_exports_seo` (0 LLM, 0 DB, fail-closed, tier A/B). **Ne réinvente aucun gate.**
2. `automecanik-wiki/_meta/schema/frontmatter.schema.json` : **ajout additif** `auto_promoted`, `promotion_tier`, `promotion_evidence` ; `reviewed_by` (pattern `skill:<name>` déjà supporté). Owner applique.
3. `wiki-readiness-check.py` / gate #12 : **inchangé**.
4. Seuil `AUTO_PROMOTE_THRESHOLD` : constante gouvernée (pas de magic number caché).

## Ce que cet ADR NE fait PAS
Ne modifie pas `build_exports_seo.py`, ni la projection ADR-059, ni le schéma `exports-seo`, ni les 13 gates atomiques, ni la génération (toujours filter+transform sourcé, 0 LLM). Ne supprime aucun gate. N'autorise aucune publication sans franchir une bar.

---

## Action owner (vault G3)
1. Relire ce draft, ajuster seuil/tiers si besoin.
2. Assigner le n° ADR libre (≥ 083).
3. Créer la fiche dans `governance-vault/ledger/decisions/adr/` + commit **signé** (single-write-point Deploy VPS) + PR.
4. Une fois accepté : sponsoriser l'implémentation (étapes ci-dessus) dans le repo wiki.
