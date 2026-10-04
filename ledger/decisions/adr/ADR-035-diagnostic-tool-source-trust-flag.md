---
id: ADR-035
title: "Diagnostic Tool Source Trust — provenance WIKI des liens __diag_symptom_cause_link"
status: accepted
date: "2026-05-02"
decision_date: "2026-10-04"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
amended_by: ["ADR-112"]
related_rules: ["G1", "G2", "G3", "Q1", "Q2"]
related_incidents: ["INC-2026-013"]
related_adr: ["ADR-031", "ADR-032", "ADR-033", "ADR-059", "ADR-112"]
reviewed_by: ""
version: "1.0.0"
---

# ADR-035 : Diagnostic Tool Source Trust — provenance WIKI des liens

- **Statut** : Accepted (2026-10-04). La fusion par l'owner vaut ratification.
- **Amendé par** [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] (même PR) :
  - D2 gagne un mode « créer ou remplacer » à partir de la phase 3 d'ADR-112 ;
  - D4 est remplacé par les niveaux plafonnés par la preuve à partir de la phase 4.

  Jusque-là, D1 à D7 s'appliquent tels quels.

> **Révision du 2026-09-30.** La proposition du 2026-05-02 (colonnes `is_trusted` / `source_origin`
> sur `__diag_symptom_cause_link`) n'a jamais été acceptée ni implémentée. Elle est remplacée par
> les décisions D1-D7 ci-dessous ; l'option d'origine est conservée en « Options considérées »
> (option C) pour l'historique. Spec d'implémentation (monorepo, PR #1658) :
> `docs/superpowers/specs/2026-09-30-diagnostic-wiki-provenance-design.md`.

## Contexte

Au 2026-05-02, l'incident [[2026-05-02-diagnostic-tool-unsourced-probas|INC-2026-013]] a documenté que les 162 liens `__diag_symptom_cause_link` du moteur diagnostic portent des `relative_score` copiés depuis un fichier RAG éditorial (truth_level L2, sans source OEM/TecDoc/RTA), affichés au client sur `/diagnostic-auto/*` comme s'ils étaient vérifiés.

Au 2026-09-30 (origin/main et DB en lecture seule), la chaîne SCRAPING → RAW → WIKI → DB est coupée à chaque maillon :

| Maillon | État |
|---|---|
| RAW → WIKI | 3 relations `diagnostic_relations` (filtre-a-air, filtre-a-carburant, filtre-d-habitacle) ; leurs sources sont `to_capture` au catalogue |
| WIKI → DB | aucun producteur : rien ne lit `diagnostic_relations` pour alimenter `__diag_*` |
| DB | aucune colonne ni table de provenance sur les liens |
| Moteur | le score affiché « NN/100 » dérive de `relative_score`, non sourcé |

[[ADR-033-wiki-gamme-diagnostic-relations-contract]] définit côté WIKI `evidence.diagnostic_safe` et la `source_policy`, sans contrepartie DB. Cet ADR définit cette contrepartie.

## Principe directeur

> Une relation symptôme → cause n'est « documentée » en DB que par une provenance WIKI vérifiable, dont toutes les sources sont prouvées dans RAW. Aucun nombre n'est affiché pour un lien tant qu'aucune fréquence sourcée n'existe.

## Décisions

### D1 — Une table de provenance, aucune colonne d'état sur les liens

- `__diag_link_provenance` : une ligne par couple (lien, fiche WIKI) ; `link_id` → `__diag_symptom_cause_link(id)` `ON DELETE RESTRICT`. Colonnes : identité de la fiche (`wiki_path`, `gamme_slug`, `wiki_commit`, `content_hash`), contenu de la relation (`relation_to_part`, `part_role`, `confidence`, `source_policy`, `confidence_score_computed`, `reviewed`, `diagnostic_safe`, `sources`), cycle de vie (`first_run_id`, `last_run_id`, `projected_at`, `retired_at`, `retired_run_id`).
- Un lien est « documenté » si et seulement s'il a une ligne vivante (`retired_at IS NULL`). Retrait doux : une relation qui n'est plus projetée reçoit `retired_at` ; l'historique est conservé.
- `__diag_projection_runs` (un run = une ligne, `exported = projected + conflicts` par `CHECK`) et `__diag_projection_conflicts` (raison bornée par `CHECK`) rendent chaque run et chaque relation non projetée observables.
- `__diag_symptom_cause_link` n'est pas modifiée.
- `wiki_commit` et `content_hash` sont des métadonnées d'audit au sens d'[[ADR-059-seo-runtime-projection]] (§Audit metadata vs replay authority) ; aucune capacité de rejeu n'est revendiquée.

Pourquoi pas des colonnes : un booléen `is_trusted` est un état sans sa preuve (qui l'a basculé, sur quelle source, depuis quand). La table porte la preuve elle-même et se recalcule à chaque run depuis le WIKI.

### D2 — Un seul producteur, qui ne crée rien et ne tranche rien

- Le seul writer est `DiagnosticProjectionModule` (monorepo), par la RPC `__diag_projection_apply(jsonb)` : une transaction, verrou consultatif, droits `service_role` seuls. Il lit `exports/diagnostic/`, vue dérivée déterministe du WIKI publiée par le builder du WIKI ; il ne lit jamais RAW ni RAG ([[ADR-031-four-layer-content-architecture]]).
- Il ne crée aucun symptôme, cause ni lien. Une relation se résout vers un lien existant par une règle déterministe ; zéro ou plusieurs candidats donnent un conflit, jamais un choix.
- Une relation n'est projetée que si toutes ses sources sont `raw_proven` (prédicat G1 : source `active` au catalogue avec `raw_ref.manifest_id`), calculé par le builder du WIKI et recopié tel quel. Sinon : conflit `source_not_raw_proven`.
- Il ne modifie jamais `reviewed` ni `diagnostic_safe`. Leur passage à `true` reste « strictement manuel ou couvert par règle ADR explicite, jamais en automatique » (ADR-033 D4) et se fait dans le WIKI : ni le writer, ni un script, ni une session IA ne le décident.

### D3 — Aucun nombre affiché pour un lien

- Aucun pourcentage, score sur 100 ni sous-score n'est affiché pour un lien tant qu'aucune fréquence sourcée n'existe.
- L'ordre existant, fondé sur `relative_score`, reste transitoire pour les liens non documentés ; il n'est jamais affiché. Le retrait de `relative_score` relève d'une spec distincte.

### D4 — Seuls les liens `diagnostic_safe: true` pondèrent le rang

- En mode primaire (drapeau `PRIMARY`, D5), une contribution pèse 100 si son lien a une ligne vivante avec `diagnostic_safe: true`, 0 sinon (ADR-033, champ `diagnostic_safe` : « autorisé à influencer le moteur diagnostic live »).
- Un lien documenté mais non `diagnostic_safe` est affiché comme documenté, sans jamais peser sur le rang.
- `confidence_score_computed` n'est pas une probabilité et ne pondère pas le rang.

### D5 — Activation par drapeaux, défaut OFF

| Drapeau | Effet |
|---|---|
| `DIAGNOSTIC_PROJECTION_ENABLED` | run quotidien du writer (PROD seul porte le job planifié) |
| `DIAGNOSTIC_PROVENANCE_EXPOSE_ENABLED` | le moteur lit et expose la provenance, sans changer le rang |
| `DIAGNOSTIC_PROVENANCE_PRIMARY_ENABLED` | pondération D4 ; refusée par la plomberie PROD si EXPOSE est OFF |

Les PR à drapeaux OFF avancent sans attendre cet ADR. Attendent son acceptation : toute activation en PROD et la PR frontend, visible sans drapeau.

### D6 — Critères de succès

1. Le premier run activé donne `exported = 3`, `projected = 0`, `conflicts = 3` (`source_not_raw_proven`) : le résultat honnête tant qu'aucune source n'est capturée.
2. Une source passée `active` par le flux gouverné produit une ligne vivante au run suivant, sans intervention manuelle.
3. Une panne de lecture de la provenance n'est jamais présentée comme une absence de preuve.
4. Aucune fiche WIKI approuvée n'est modifiée ; aucun symptôme, cause ni lien n'est créé.

### D7 — Interdictions

- Écrire `__diag_link_provenance` hors de `__diag_projection_apply`.
- Projeter une relation dont une source n'est pas `raw_proven`.
- Afficher un nombre par lien (D3) ; pondérer le rang par un lien non `diagnostic_safe` (D4).
- Alimenter la provenance depuis RAG ou depuis RAW directement.

## Options considérées

### Option A — Supprimer les `relative_score` existants (rejetée)

Destructif et irréversible, sans gain de preuve. Rejetée le 2026-05-02, toujours rejetée.

### Option B — Colonne `score_confidence` low/medium/high (rejetée)

Analogue à l'anti-pattern `evidence_level` plat rejeté par ADR-033. Rejetée le 2026-05-02, toujours rejetée.

### Option C — Colonnes `is_trusted` + `source_origin` (proposée le 2026-05-02, remplacée)

`ALTER TABLE __diag_symptom_cause_link ADD COLUMN is_trusted BOOLEAN NOT NULL DEFAULT FALSE, ADD COLUMN source_origin TEXT NOT NULL DEFAULT 'rag_unverified'`, bascule `is_trusted = true` selon la `source_policy`.

**Remplacée** : l'état serait dissocié de sa preuve, sa bascule demanderait un acteur (manuel ou script) que D2 interdit, et la table de liens, lue par le moteur, serait modifiée.

### Option D — Table de provenance projetée depuis le WIKI (retenue)

D1-D7. Additive, observable par run, recalculée depuis le WIKI, sans aucune bascule manuelle.

## Conséquences

### Positives

- La provenance de chaque lien est vérifiable : fiche, commit, sources et leur preuve RAW.
- Le travail de capture RAW (sous-projet suivant) devient mesurable : conflits `source_not_raw_proven` → projections.
- Aucune table existante n'est modifiée ; chaque étape se coupe par son drapeau.

### Négatives

- Au lancement, aucun lien n'est documenté (0 source capturée) : le moteur affiche toutes ses hypothèses comme « non encore documentées ».
- Le mode primaire reste sans effet tant qu'aucune relation n'est `diagnostic_safe: true`.

### Neutres

- `relative_score` reste en DB et ordonne transitoirement les liens non documentés.
- [[ADR-032-diagnostic-maintenance-unification]] est remplacé par [[ADR-112-diagnostic-knowledge-base-canon|ADR-112]] (2026-10-04) ; cet ADR n'en dépend pas.

## Revue planifiée

**Date** : J+90 après acceptation.

**Critères** :
- runs quotidiens `applied` en PROD, `exported = projected + conflicts` ;
- évolution du nombre de conflits `source_not_raw_proven` avec la capture RAW ;
- aucun nombre par lien affiché sur `/diagnostic-auto/*`.

---

*Proposé le : 2026-05-02*
*Révisé le : 2026-09-30 (D1-D7 remplacent la proposition d'origine)*
*Accepté le : 2026-10-04 (fusion owner = ratification)*
*Dernière revue : TBD*
