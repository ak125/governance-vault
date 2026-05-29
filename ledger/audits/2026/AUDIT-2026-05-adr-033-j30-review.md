---
type: audit
audit_id: AUDIT-2026-05-adr-033-j30
subject_adr: ADR-033
subject_adr_file: ledger/decisions/adr/ADR-033-wiki-gamme-diagnostic-relations-contract.md
audit_type: planned_review_j30
audit_date: 2026-05-29
auditor: claude-code-agent (session automecanik.seo@gmail.com)
verdict: FAIL_PARTIAL
adr_status_before: proposed
adr_status_after: proposed
adr_status_change: none
aec_final_status: PARTIAL_COVERAGE
---

# Revue planifiée J+30 — ADR-033 Wiki Gamme Diagnostic Relations Contract

**Date d'échéance** : 2026-05-29 (J+30 après merge vault PR #108, commit 77085ef, 2026-04-29)  
**Scope audit** : critères §Revue planifiée ADR-033 (4 critères)  
**Repos audités** : `ak125/automecanik-wiki` (main @ d92252ff) · `ak125/nestjs-remix-monorepo` (main @ f6e2ee63)  
**Repo hors scope** : `ak125/automecanik-rag` (non accessible depuis ce session — voir §Limitations)

---

## Tableau des 4 critères

| # | Critère | Verdict | Evidence |
|---|---------|---------|----------|
| C1 | Au moins 1 batch system migré (freinage ~20 fiches) | **FAIL** | `wiki/gamme/` = `.gitkeep` seul. 0 fiche avec `diagnostic_relations[]` non-vide. Aucune PR `migrate-symptoms-to-relations` dans automecanik-wiki. Les db-rich proposals (vanne-egr, filtre-a-huile…) ont `diagnostic_relations: []` vide. automecanik-rag non accessible. |
| C2 | Validateur CI déployé et bloquant ≥ 2 semaines | **PARTIAL** | Script `validate-gamme-diagnostic-relations.py` présent (monorepo, Python). Workflow `wiki-validate.yml` créé 2026-04-30 (29 jours ≥ 14 j ✓), bloquant (exit 1). `wiki-quality-gates.yml` automecanik-wiki active les gates ADR-033. Evidence de catch : PR wiki #10 (fix forcé). Aucune PR formellement *refusée* pour `legacy_symptoms_block` documentée. Écart ADR : `.ts` spécifié, implémenté `.py` (justifié commit d0b32a0). |
| C3 | Aucun fichier `wiki/systemes/*` ou `wiki/diagnostic/<symptom>-*` créé | **PASS** | `wiki/systemes/` : répertoire absent. `wiki/diagnostic/` : 5 fichiers (`faq.md`, `safety-config.md`, `signs.md`, `vocab-clusters.md`, `wizard-steps.md`) — aucun ne matche le regex `(bruit\|grincement\|vibration\|voyant\|fumee\|surchauffe\|fuite\|usure\|symptome\|claquement\|sifflement)-*.md`. |
| C4 | Défaut `diagnostic_safe: false` non contourné en bloc | **PASS** (scope limité) | Commit 768abd9 (PR wiki #8, 2026-04-29) : _«Tous les `evidence.diagnostic_safe: false` (défaut conservateur ADR-033 §D4)»_. 38 commits automecanik-wiki depuis 2026-04-29 examinés : aucun message contenant `diagnostic_safe.*true`. `git log --grep` non disponible via MCP API — voir §Limitations. |

---

## Détail par critère

### C1 — Migration batch (FAIL)

- **wiki/gamme/** : HEAD d92252ff contient uniquement `.gitkeep` (arbre `d564d0bc`).
- **proposals/** actives (tâches 8–9) : `vanne-egr.md`, `filtre-a-huile.md`, `support-moteur.md`, `courroie-d-accessoire.md`, `thermostat.md` — frontmatter `diagnostic_relations: []` (vide), focus sur `entity_data.dimensions` (compatibility_proven_by_runtime_url_and_db), pas sur la migration symptômes.
- **`proposals/plaquette-de-frein.md`** (commit 768abd9) : 4 entrées `diagnostic_relations[]` non-vides (bruit_grincement, vibration_pedale, distance_freinage, voyant_freinage) avec `diagnostic_safe: false` — mais fichier en `proposals/` (status: proposed), pas promu en `wiki/gamme/`.
- Phase 4 ADR-033 (script `migrate-symptoms-to-relations.ts` / `.py`) : non démarrée sur le scope visible.
- **Retard Phase 4** : J+30, 0 batch migré vs objectif ≥ 1 system (freinage ~20 fiches).

### C2 — Validateur CI (PARTIAL)

- **Script** : `nestjs-remix-monorepo/scripts/wiki/validate-gamme-diagnostic-relations.py` (SHA 4cf52ce, ~190 LOC, 7 blocked_reasons couvrant les anti-patterns D3 + FK validation).
- **Workflow monorepo** `wiki-validate.yml` : créé 2026-04-30 par commit d0b32a0 (PR #250). Trigger : PRs sur `workspaces/wiki/**` + `scripts/wiki/**` + schedule lundi 03h UTC. Bloquant (exit 1 si any FAIL).
- **Workflow wiki** `wiki-quality-gates.yml` : créé commit 768abd9 (2026-04-29). Gate `quality-gates.py --all` inclut `legacy_symptoms_block`, `forbidden_systemes_dir`, `forbidden_per_symptom_file` (comment : _"gates ADR-033 + ADR-032"_). Bloquant sur PRs wiki.
- **Evidence catch** : PR wiki #10 (merged 2026-04-30T22:39:49Z) : _"fix(adr-033): retire orphan diagnostic_relations[] from filtre-a-air.md"_ — correction forcée avant merge = démonstration de blocage effectif.
- **Manque** : aucune PR formellement *closed without merge* pour `legacy_symptoms_block` répertoriée dans les 28 PRs wiki listées.
- **Écart implémentation** : ADR-033 §Phase 2 spécifie un script `.ts` (`validate-gamme-diagnostic-relations.ts`) ; implémenté en `.py`. Le commit d0b32a0 documente la justification (alignement avec `_scripts/quality-gates.py` wiki, évite ajout de deps root `js-yaml` / `ajv`).

### C3 — Fichiers interdits (PASS)

- Répertoires automecanik-wiki wiki/ : `constructeur`, `diagnostic`, `gamme`, `support`, `vehicle`. Pas de `systemes/`. ✓
- `wiki/diagnostic/` : `.gitkeep` + `faq.md` + `safety-config.md` + `signs.md` + `vocab-clusters.md` + `wizard-steps.md`. Regex ADR-033 §D3 non matchée. ✓

### C4 — diagnostic_safe (PASS scope limité)

- Evidence principale : commit 768abd9 message explicite _«Tous les `evidence.diagnostic_safe: false` (défaut conservateur ADR-033 §D4)»_ pour les 5 pilots G6.
- `proposals/vanne-egr.md` (HEAD) : `diagnostic_relations: []` vide — aucun champ `diagnostic_safe` à risque.
- 38 commits automecanik-wiki examinés via MCP list_commits (2026-04-29 → 2026-05-29) : aucun message ne contient `diagnostic_safe.*true`.
- **Limitation** : `git log --grep 'diagnostic_safe.*true'` sur le contenu des patches non disponible via MCP. Un audit complet nécessiterait un accès git local ou GitHub Search API sur le contenu des diffs.

---

## Conclusion

ADR-033 ne peut pas passer en `accepted` à J+30.

**Bloquant principal** : Critère C1 FAIL — Phase 4 migration batch non démarrée. `wiki/gamme/` vide (`.gitkeep`), 0 fiche avec `diagnostic_relations[]` non-vide produite et mergée.

**Actions requises avant prochain jalon** :
1. **C1** : Démarrer Phase 4 sur le system freinage (~20 fiches). Merger au moins 1 batch `wiki/gamme/<slug>.md` avec `diagnostic_relations[]` non-vide, `evidence.reviewed: false`, `evidence.diagnostic_safe: false` (défauts ADR-033 §D4 stricts). PR wiki ciblée.
2. **C2** : Documenter formellement au moins 1 PR wiki refusée pour `legacy_symptoms_block` ou anti-pattern D3 (ou confirmer via run CI log d'une PR rejetée) pour valider le critère « bloquant effectif ».
3. **C2 écart** : Le script `.py` vs `.ts` est acceptable opérationnellement mais l'ADR devrait être amendé (ou note de suivi) pour aligner la spec avec l'implémentation réelle.

**Prochaine revue suggérée** : J+60 (2026-06-28) ou après merge du premier batch freinage.

---

## Limitations scope audit

- `ak125/automecanik-rag` : repo hors liste des repos autorisés pour ce session — critère C1 n'a pas pu vérifier la PR `migrate-symptoms-to-relations` côté automecanik-rag (Phase 4 ADR-033 implique aussi un PR monorepo + PR wiki).
- `git log --grep` : non disponible via GitHub MCP API (list_commits filtre sur auteur/path/sha, pas sur contenu de message patch). C4 basé sur analyse des messages de commit et contenu de fichier, pas sur grep contenu patches.
- Période couverte : commits automecanik-wiki depuis 2026-04-29 (38 commits, 28 PRs listées). Monorepo non balayé en totalité.

---

## AEC Coverage Manifest v1.0

```yaml
aec_version: "1.0"
audit_id: AUDIT-2026-05-adr-033-j30
audit_date: 2026-05-29
scope_declared:
  - automecanik-wiki (main, HEAD d92252ff) — wiki/gamme, wiki/diagnostic, wiki/systemes, proposals/
  - nestjs-remix-monorepo (main, HEAD f6e2ee63) — scripts/wiki/, .github/workflows/
  - governance-vault (main, HEAD 68672c2d) — ADR-033 frontmatter
scope_not_covered:
  - automecanik-rag (hors périmètre repos autorisés)
  - git diff patches content (diagnostic_safe grep limité aux messages de commit)
  - CI run logs (aucun accès aux logs GitHub Actions)
criteria_evaluated: [C1, C2, C3, C4]
verdicts: {C1: FAIL, C2: PARTIAL, C3: PASS, C4: "PASS (scope limité)"}
final_status: PARTIAL_COVERAGE
rationale: >
  Critère C1 FAIL (migration batch non démarrée) + scope automecanik-rag non couvert
  + diagnostic_safe grep limité aux messages de commit. Scope suffisant pour les critères
  C3 (PASS confirmé) et C4 (PASS avec réserve scope). Critère C2 PARTIAL avec evidence
  indirecte de blocage (PR wiki #10).
next_review: 2026-06-28
```
