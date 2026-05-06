---
id: INC-2026-013
date: 2026-05-02
date_detected: 2026-05-02
date_resolved: null
severity: high
status: open
impact_duration: "continu — probabilités non sourcées en production depuis migration 20260308_diagnostic_engine_mvp.sql (~8 semaines)"
affected_systems:
  - "table: __diag_symptom_cause_link (162 rows, 162 avec relative_score)"
  - "service: DiagnosticEngineDataService (NestJS backend)"
  - "route-frontend: /diagnostic-auto/*"
root_cause: "La migration DB 20260308_diagnostic_engine_mvp.sql a copié les probabilités (ex. 70/15/10/5) depuis le fichier RAG éditorial bruits-freinage.md (truth_level: L2, étiqueté 'verified' sans aucune source OEM/TecDoc/RTA citée). Les 162 liens __diag_symptom_cause_link portent donc des relative_score NON SOURCÉS exposés au client final sur /diagnostic-auto/*. Aucun flag DB ne distingue un score sourcé d'un score éditorial. ADR-033 (commit 77085ef, vault PR #108) évoque le problème dans son Contexte mais son scope est strictement le contrat markdown wiki gamme."
related_rules: ["G1", "Q1", "Q2"]
related_adr: ["ADR-032", "ADR-033", "ADR-035"]
related_incidents: []
owner: "@fafa"
reviewed_by: ""
tags:
  - incident/high
  - domain/diagnostic
  - domain/data-quality
  - tech/database
  - tech/trust-flag
---

# Incident INC-2026-013 : Probabilités non sourcées dans le moteur diagnostic

## Synthèse

L'audit de la session 2026-04-29 a révélé que les `relative_score` (probabilités 0-100) de **toutes les 162 lignes** `__diag_symptom_cause_link` ont été copiées depuis le fichier RAG éditorial `bruits-freinage.md` (truth_level: L2, étiqueté `verified` sans aucune référence normative OEM/TecDoc/RTA). Ces scores sont affichés au client final sur `/diagnostic-auto/*` comme s'ils étaient des données vérifiées. Aucun mécanisme DB ni applicatif ne distingue un score sourcé d'un score inventé.

## Constat DB (lecture seule — 2026-05-02)

| Métrique | Valeur | Requête SQL |
|----------|--------|-------------|
| `SELECT to_regclass('public.__diag_symptom_cause_link')` | `__diag_symptom_cause_link` | ✅ table existe (projet Supabase `cxpojprgwgubzjyqzmoq`) |
| `SELECT count(*) FROM __diag_symptom_cause_link` | **162** | total rows |
| `SELECT count(*) FROM __diag_symptom_cause_link WHERE relative_score IS NOT NULL` | **162** | rows avec score (100 % des rows) |
| Rows avec source OEM/TecDoc/RTA vérifiée | **0** (estimé) | audit RAG — aucune référence dans `bruits-freinage.md` |
| Colonne `is_trusted` présente | **NON** | non encore migrée (voir ADR-035) |
| Colonne `source_origin` présente | **NON** | non encore migrée (voir ADR-035) |

**Source des probabilités** : `bruits-freinage.md` — `truth_level: L2` — étiqueté `verified` de façon éditoriale sans référence normative. Les valeurs (ex. 70/15/10/5) sont des estimations d'auteur, pas des données issues de sources primaires (OEM, TecDoc, manuels RTA).

**Exposé client** : l'outil `/diagnostic-auto/*` affiche ces pourcentages comme probabilités de causes, impliquant une fiabilité technique que les données ne possèdent pas.

## Trace causale

```
bruits-freinage.md (RAG, truth_level L2, "verified" sans source)
  → migration 20260308_diagnostic_engine_mvp.sql
    → __diag_symptom_cause_link.relative_score (162 rows)
      → DiagnosticEngineDataService (NestJS)
        → /diagnostic-auto/* (client final)
```

**ADR-033** (commit 77085ef, vault PR #108, 2026-04-29) décrit ce problème dans sa section Contexte mais son scope est exclusivement le contrat markdown wiki gamme — il ne traite pas le freeze des scores DB ni l'exposition client.

## 4 Actions d'atténuation immédiates

### A — Migration DB : ajout colonnes `is_trusted` + `source_origin`

```sql
-- PROPOSITION (non appliquée cette session — voir ADR-035)
ALTER TABLE __diag_symptom_cause_link
  ADD COLUMN is_trusted     BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN source_origin  TEXT    NOT NULL DEFAULT 'rag_unverified';
-- Toutes rows existantes héritent : is_trusted=false, source_origin='rag_unverified'
```

Critère : `SELECT count(*) FROM __diag_symptom_cause_link WHERE is_trusted = false` = **162** après migration.

### B — Backend NestJS : `DiagnosticEngineDataService` — masquer les probabilités non fiables

Modifier le service pour ne PAS retourner de `relative_score` chiffré quand `is_trusted = false`. Retourner uniquement la liste des causes possibles en ordre statique ou alphabétique, sans pourcentage.

### C — Frontend `/diagnostic-auto/*` : adapter le rendu

Adapter le composant qui rend les probabilités pour gérer `is_trusted: false` : afficher uniquement l'ordre des causes sans chiffre, avec mention optionnelle « données en cours de vérification ».

### D — Plan de re-sourcing structurel

À terme, les scores `is_trusted = true` doivent être alimentés exclusivement depuis `wiki/gamme/<slug>.md` `diagnostic_relations[]` (ADR-033) avec `evidence.diagnostic_safe = true` et au moins 1 source `oem_*` OU 2 sources `medium` concordantes (politique définie dans ADR-035).

## Statut des actions

| Action | Repo / PR | Statut | Deadline |
|--------|-----------|--------|----------|
| A — Migration DB `is_trusted` + `source_origin` | nestjs-remix-monorepo / à ouvrir | ⏳ Planifiée | — |
| B — Backend masque probas si `is_trusted=false` | nestjs-remix-monorepo / à ouvrir | ⏳ Planifiée | — |
| C — Frontend adapte rendu | nestjs-remix-monorepo / à ouvrir | ⏳ Planifiée | — |
| D — Plan re-sourcing structurel | ADR-035 (vault) | ✅ Draft proposé | — |

Coordination : issue `ak125/nestjs-remix-monorepo` ouverte — lien à renseigner ci-dessous après création.

## Références

- **ADR-032** : [[ADR-032-diagnostic-maintenance-unification]] — canon DB+backend `kg_*`
- **ADR-033** : [[ADR-033-wiki-gamme-diagnostic-relations-contract]] — contrat wiki gamme (commit 77085ef, vault PR #108, 2026-04-29)
- **ADR-035** : [[ADR-035-diagnostic-tool-source-trust-flag]] — flag `is_trusted` + règle de re-sourcing (proposé, session 2026-05-02)
- **Migration source** : `20260308_diagnostic_engine_mvp.sql` (monorepo)
- **Fichier RAG** : `bruits-freinage.md` (automecanik-raw, PR #6, commit af7f6ff)
- **PRs déclencheurs** : wiki #8 (commit 768abd9) / raw #6 (commit af7f6ff) — `diagnostic_relations[]` v2.0.0
- **Issue coordination monorepo** : `ak125/nestjs-remix-monorepo` — à lier ici après création

---

*Créé le : 2026-05-02*
*Dernière mise à jour : 2026-05-02*
