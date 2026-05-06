---
id: ADR-035
title: "Diagnostic Tool Source Trust Flag — is_trusted + source_origin sur __diag_symptom_cause_link"
status: proposed
date: 2026-05-02
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "Q1", "Q2"]
related_incidents: ["INC-2026-013"]
related_adr: ["ADR-031", "ADR-032", "ADR-033"]
reviewed_by: ""
---

# ADR-035 : Diagnostic Tool Source Trust Flag

## Contexte

Au 2026-05-02, l'incident [[2026-05-02-diagnostic-tool-unsourced-probas|INC-2026-013]] a documenté que les 162 liens `__diag_symptom_cause_link` du moteur diagnostic AutoMecanik portent des `relative_score` copiés depuis le fichier RAG éditorial `bruits-freinage.md` (truth_level L2, sans source OEM/TecDoc/RTA). Ces probabilités sont affichées au client final sur `/diagnostic-auto/*` comme si elles étaient vérifiées.

### Chiffres DB (lecture seule — 2026-05-02, projet Supabase `cxpojprgwgubzjyqzmoq`)

| Requête | Résultat |
|---------|----------|
| `SELECT to_regclass('public.__diag_symptom_cause_link')` | `__diag_symptom_cause_link` ✅ |
| `SELECT count(*) FROM __diag_symptom_cause_link` | **162** |
| `SELECT count(*) FROM __diag_symptom_cause_link WHERE relative_score IS NOT NULL` | **162** (100 % des rows ont un score) |

La table ne possède aucun champ permettant de distinguer un score issu d'une source primaire vérifiée d'un score éditorial inventé. [[ADR-033-wiki-gamme-diagnostic-relations-contract]] introduit la notion de `evidence.diagnostic_safe` côté markdown mais n'impose pas de contrepartie DB. Cet ADR-035 comble ce gap.

## Principe directeur

> Une probabilité ne doit être affichée au client que si elle est issue d'au moins une source normative vérifiée. Dans le cas contraire, seule la liste des causes est présentée, sans chiffre.

## Décisions

### D1 — Colonnes `is_trusted` et `source_origin`

```sql
ALTER TABLE __diag_symptom_cause_link
  ADD COLUMN is_trusted     BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN source_origin  TEXT    NOT NULL DEFAULT 'rag_unverified';
```

Sémantique :

- **`is_trusted = false`** : score non sourcé ou source insuffisante. Défaut pour **toutes les 162 rows existantes**. L'application **ne doit pas** afficher de probabilité chiffrée.
- **`is_trusted = true`** : score validé selon la règle D2. L'application peut afficher le `relative_score`.
- **`source_origin`** — valeurs canoniques :

| Valeur | Signification |
|--------|---------------|
| `rag_unverified` | Copié depuis RAG éditorial sans source normative (défaut rows existantes) |
| `wiki_diagnostic_relations` | Alimenté depuis `diagnostic_relations[]` d'une fiche wiki gamme avec `evidence.diagnostic_safe = true` |
| `oem_<slug>` | Issu d'un manuel OEM référencé |
| `tecdoc_<slug>` | Issu d'une source TecDoc vérifiée |
| `manual_review_<reviewer>` | Revu manuellement par un expert nommé, commit signé G3 |

### D2 — Règle de remontée `is_trusted = true`

Un lien passe à `is_trusted = true` **uniquement** si l'une des conditions suivantes est satisfaite, alignée sur la `source_policy` d'ADR-033 D1 :

| Condition | Prérequis |
|-----------|-----------|
| **1 source haute fiabilité** | `source_origin` = `oem_*` ou `tecdoc_*` ET document source référencé dans `sources[]` de la fiche wiki correspondante avec `evidence.confidence = high` |
| **2 sources medium concordantes** | Deux fiches wiki distinctes référencent le même `symptom_slug` / cause avec `evidence.confidence = medium` ET `evidence.diagnostic_safe = true` ET `evidence.source_policy = '2_medium_concordant'` |
| **Revue manuelle** | Reviewer humain (`reviewed_by ≠ auteur_contenu`) crée un commit signé G3 avec annotation explicite, `source_origin = 'manual_review_<reviewer>'` |

**Interdit** : flip automatique `is_trusted = true` depuis pipeline RAG ou session IA sans revue humaine. Même règle que `evidence.diagnostic_safe` dans ADR-033 D4.

### D3 — Comportement applicatif selon `is_trusted`

| `is_trusted` | `DiagnosticEngineDataService` | Frontend `/diagnostic-auto/*` |
|---|---|---|
| `false` | Retourne liste causes ordonnées (statique ou alphabétique), **sans** `relative_score` | Affiche liste causes sans pourcentage |
| `true` | Retourne `relative_score` + liste ordonnée par score | Affiche probabilités chiffrées |

**Invariant absolu** : aucune probabilité chiffrée ne doit apparaître côté client si `is_trusted = false`.

### D4 — Découpage en 4 PRs séquentielles

| Ordre | PR | Repo | Contenu | Prérequis |
|---|---|---|---|---|
| 1 | PR-A | nestjs-remix-monorepo | Migration DB : `ADD COLUMN is_trusted BOOLEAN DEFAULT FALSE, source_origin TEXT DEFAULT 'rag_unverified'` + update toutes rows existantes | Aucun |
| 2 | PR-B | nestjs-remix-monorepo | `DiagnosticEngineDataService` : masquer `relative_score` si `is_trusted = false`, retourner liste causes ordonnée | PR-A mergée |
| 3 | PR-C | nestjs-remix-monorepo | Frontend `/diagnostic-auto/*` : adapter composant rendu probabilités pour `is_trusted: false` | PR-B mergée |
| 4 | PR-D | governance-vault | Plan de re-sourcing structurel : documenter pipeline `wiki diagnostic_relations[]` → `is_trusted = true` | PR-A mergée |

### D5 — Critères de succès

1. Après PR-A : `SELECT count(*) FROM __diag_symptom_cause_link WHERE is_trusted = false` = **162**
2. Après PR-A : `SELECT count(*) FROM __diag_symptom_cause_link WHERE is_trusted = true` = **0**
3. Après PR-B + PR-C : aucune probabilité chiffrée n'apparaît sur `/diagnostic-auto/*` pour les causes avec `is_trusted = false`
4. Au fil du re-sourcing : le compteur `WHERE is_trusted = false` décroît progressivement
5. Horizon T+6 mois : au moins un système complet (ex. freinage, ~20-30 liens) passe à `is_trusted = true` après re-sourcing OEM

### D6 — Interdictions

- Pas de flip `is_trusted = true` via script automatique non supervisé
- Pas d'affichage de `relative_score` côté client si `is_trusted = false`
- `source_origin = 'rag_unverified'` est incompatible avec `is_trusted = true` (contrainte CHECK optionnelle à envisager en PR-A)

## Options Considérées

### Option A — Supprimer les `relative_score` existants (rejetée)

Vider tous les scores DB. Pas de distinction `is_trusted`.

**Rejeté** : destructif et irréversible. Les données ont de la valeur une fois re-sourcées. Perd 8 semaines de travail de scoring sans gain sécurité supplémentaire.

### Option B — Colonne `score_confidence` (text: low/medium/high) (rejetée)

Analogue à l'anti-pattern `evidence_level` plat documenté dans ADR-033 section « Décisions activement rejetées ». Sans booléen binaire, la logique applicative `if is_trusted { show_score }` est ambiguë.

**Rejeté** : trop vague, edge-cases non définis, risque de contournement silencieux.

### Option C — `is_trusted BOOLEAN` + `source_origin TEXT` (retenue)

Sémantique binaire claire, invariant testable, découpage 4 PRs séquentiel.

**Retenu** : conforme à la philosophie ADR-033 (`diagnostic_safe` côté wiki ↔ `is_trusted` côté DB), implémentation minimaliste, réversible.

## Conséquences

### Positives

- Aucune probabilité non sourcée affichée côté client après PR-B + PR-C
- Le re-sourcing progressif est traçable via `source_origin` et mesurable via `SELECT count(*) WHERE is_trusted = true`
- Alignement fort ADR-033 : `evidence.diagnostic_safe = true` côté wiki ↔ `is_trusted = true` côté DB
- Les RPCs `kg_diagnose_*` existants peuvent retourner `is_trusted` comme champ supplémentaire sans breaking change

### Négatives

- PR-A nécessite migration DB (ADD COLUMN safe, mais déclenche dégradation UX temporaire jusqu'à PR-B+C)
- Le re-sourcing manuel de 162 liens est estimé T+3 à T+6 mois pour couverture complète
- Risque de régression si PR-B est déployée sans PR-C : déployer atomiquement ou avec feature flag

### Neutres

- `source_origin = 'rag_unverified'` reste lisible en DB pour audits futurs
- ADR-031 (4-layer) et ADR-032 (kg_* canon) ne sont pas impactés

## Revue Planifiée

**Date** : 2026-08-02 (J+90 post-acceptation)

**Critères** :
- `SELECT count(*) WHERE is_trusted = false` < 162 (re-sourcing initié)
- Au moins 1 système complet (freinage) entièrement re-sourcé (`is_trusted = true`)
- Aucun `relative_score` affiché côté client pour `is_trusted = false` (audit smoke tests `/diagnostic-auto/*`)
- Évaluation : le seuil `2_medium_concordant` s'est révélé suffisant ou doit être renforcé

---

*Proposé le : 2026-05-02*
*Accepté le : TBD*
*Dernière revue : 2026-05-02*
