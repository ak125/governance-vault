---
id: ADR-033
title: "Wiki Gamme Diagnostic Relations Contract — references-only from R3/R4 to __diag_symptom / __diag_system"
status: accepted
date: 2026-04-29
decision_date: 2026-07-07
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "Q1", "AP-10"]
related_incidents: []
related_adr: ["ADR-015", "ADR-027", "ADR-031", "ADR-032"]
---

# ADR-033: Wiki Gamme Diagnostic Relations Contract

## Reconciliation 2026-07-07

> Statut réel réconcilié. ADR-033 était formellement `proposed` alors que son contrat est vivant et
> gouverné aval. Cette section fige ce qui est accepté, implémenté, incomplet, et **non autorisé**.

**ACCEPTED (canon figé) :**
- forme `diagnostic_relations[]` (top-level frontmatter gamme) ;
- un symptôme appartient à un **système**, pas à une **pièce** ;
- références typées `symptom_slug` / `system_slug` vers le canon `__diag_*` ;
- défaut conservateur `diagnostic_safe = false` (flip = revue humaine) ;
- pas de couche `wiki/systemes/`, pas de fichier-par-symptôme (D3) ;
- **S2_DIAG consomme les relations typées** (source = `__diag_*` + `diagnostic_relations[]`, cf. ADR-027
  §Correction 2026-07-07).

**IMPLEMENTED (déjà livré / vivant) :**
- contrat `diagnostic_relations[]` **top-level frontmatter** (défini dans `frontmatter.schema.json`,
  `schema_version` v2.0.0, ADR-033 §D1 ; cf. `GammeContentContract.v2` §D6) ;
- validateur CI + cron export slugs + `wiki-readiness-check.py` (verdict READY 2026-05-01) ;
- ADR enfant **ADR-039** (accepted, « PR-C ADR-033 ») ; amendement **ADR-083** (accepted).

**NOT COMPLETE (ouvert, gouverné, non débloqué ici) :**
- migration du corpus legacy (Phase 4) — les `symptoms:` legacy (ordre de grandeur historique « 500+ fiches »
  recyclées côté `rag/knowledge/gammes/`) vivent encore côté RAW ; `wiki/gamme/` non peuplé ;
- re-source curé complet symptôme→relation ;
- projection / cutover canonique de S2_DIAG.

**EXPLICITLY NOT AUTHORIZED :**
- RAG → `diagnostic_relations[]` ;
- RAG → S2_DIAG ;
- laundering automatique des `diagnostic.symptoms[]` legacy (migration = re-source gouverné, revue humaine,
  jamais une écriture RAG).

*(Aucune modification de forme du contrat — D1-D6 inchangés. Cette réconciliation formalise le statut et
distingue accepté / implémenté / incomplet ; elle ne réécrit pas la décision.)*

## Contexte

Au 2026-04-29, le contrat documentaire des fiches gamme R3/R4
(`automecanik-wiki/wiki/gamme/<slug>.md`) viole le principe utilisateur
non-négociable « le symptôme appartient à un SYSTÈME, pas à une PIÈCE ».

### Audit empirique (session 2026-04-29)

**Côté DB — moteur diagnostic conforme** :

| Composant | État | Évidence |
|---|---|---|
| `__diag_system` | 13 systèmes (freinage, distribution, embrayage, suspension, direction, échappement, filtration, injection, climatisation, transmission, éclairage, batterie, refroidissement) | Migration `20260308_diagnostic_engine_mvp.sql` |
| `__diag_symptom` | 62-65 symptômes avec FK `system_id` | Symptômes attachés au système, pas à la pièce |
| `__diag_cause` | 60+ causes avec `plausible_km_min/max`, `plausible_age_min/max`, `workshop_priority` | Cause = pièce ou condition mécanique, distincte du symptôme |
| `__diag_symptom_cause_link` | 148+ liens scorés `relative_score 0-100` + `evidence_for[]` + `evidence_against[]` | Modèle probabiliste pièce → symptôme déjà en place |

Le moteur (`__diag_*` + RPCs `kg_diagnose_*` + backend NestJS + frontend
`/diagnostic-auto/*`) **respecte** le principe : symptôme = système, pièce = cause.

**Côté Wiki — anti-pattern actif sur 500+ fiches** :

Le contrat `GammeContentContract.v1` (`rag/docs/GAMME_PAGE_CONTRACT.md`) et
le template `new-gamme.md` codifient un bloc `diagnostic.symptoms[]` redéfini
**localement** dans chaque fiche gamme :

```yaml
# fiche actuelle (ex : disque-de-frein.md) — ANTI-PATTERN
diagnostic:
  symptoms:
    - id: S1
      label: "Vibrations au volant"
    - id: S2
      label: "Pulsation pédale"
    - id: S3
      label: "Grincement"
  causes: […]
  quick_checks: […]
```

**Conséquences mesurables** :

- 500+ fiches gamme dupliquent les symptômes côté markdown au lieu de
  référencer `__diag_symptom` (~6 GB / ~124 000 lignes côté `rag/knowledge/gammes/`).
- Aucun lien typé entre fiches gamme et `__diag_symptom.slug` / `__diag_system.slug`.
- Risque de dérive sémantique : un même symptôme ("vibration au volant")
  peut être formulé différemment dans 30 fiches.
- Validateur CI inexistant : rien ne garantit qu'un symptôme nommé dans
  une fiche existe en DB.
- Mélange « preuve SEO » (suffisante pour enrichir une fiche wiki) et
  « preuve diagnostic » (requise pour influencer le moteur live) sans
  champ pour les distinguer.

### Décisions adjacentes (précisent ce que ADR-033 ne traite PAS)

- **ADR-027** (accepted, 2026-04-25) — fige la consolidation R5 → R3 S2_DIAG.
  ADR-033 n'invalide pas ADR-027 : les fiches R3 continuent d'agréger
  les symptômes diagnostics, mais désormais via références typées.
- **ADR-031** (proposed, 2026-04-28) — fige le cadre 4-layer raw/wiki/exports.
  ADR-033 spécifie un bloc frontmatter pour la couche `wiki` côté gamme,
  conforme au principe directeur d'ADR-031.
- **ADR-032** (accepted, 2026-04-29, PR vault #107) — fige le canon DB+backend
  pour diagnostic/maintenance (`kg_*` canon, `__diag_*` interactif distinct).
  ADR-032 introduit `entity_data.maintenance.{educational_advice, related_pages}`
  côté frontmatter wiki gamme. **`diagnostic_relations[]` est orthogonal**
  à ce bloc : il exprime les relations symptôme/cause, pas les intervalles
  d'entretien. Les deux blocs coexistent dans le même fichier `.md`.

ADR-033 n'introduit **aucun changement** dans le moteur diagnostic,
les RPCs, le backend NestJS, le frontend `/diagnostic-auto/*`, ni la
DB `__diag_*`. Strict scope contrat sémantique côté markdown wiki gamme.

---

## Principe directeur

> Les symptômes vivent dans `__diag_symptom`, rattachés à `__diag_system`.
> Les fiches gamme R3 ne doivent contenir que des _références_ vers les
> symptômes système auxquels la pièce peut contribuer.
>
> Une pièce ne possède pas un symptôme — elle déclare seulement qu'elle
> peut y contribuer comme cause possible (relation contributive).

---

## Décisions

### D1 — Bloc frontmatter `diagnostic_relations[]`

Nouveau bloc frontmatter dans `wiki/gamme/<slug>.md`, structure normalisée :

```yaml
diagnostic_relations:
  - symptom_slug: bruit_freinage           # FK __diag_symptom.slug
    system_slug: freinage                   # FK __diag_system.slug
    relation_to_part: possible_cause        # possible_cause | symptom_amplifier | secondary_effect
    part_role: "plaquette usée, contaminée ou mal montée"
    evidence:
      confidence: medium                    # low | medium | high
      source_policy: "2_medium_concordant"  # 1_high | 2_medium_concordant | manual_review
      reviewed: false                       # validation humaine ?
      diagnostic_safe: false                # autorisé à influencer le moteur diagnostic live ?
    sources:
      - bosch_fad_2020_p27
      - oem_workshop_brake_noise
```

Sémantique :

- **`diagnostic_relations`** (pas `links`) — exprime le modèle métier
  contributif, pas un simple pointeur documentaire.
- **`symptom_slug` / `system_slug`** — FK strictes vers `__diag_symptom.slug`
  et `__diag_system.slug`. Tout slug inexistant en DB est une erreur
  bloquante côté validateur CI.
- **`relation_to_part`** — typage de la relation :
  - `possible_cause` : la pièce peut être la cause directe du symptôme.
  - `symptom_amplifier` : la pièce aggrave un symptôme dont la cause est ailleurs.
  - `secondary_effect` : la pièce manifeste un symptôme conséquence d'un autre défaut.
- **`part_role`** — phrase courte explicative pour la fiche pièce
  (« comment cette pièce intervient sur ce symptôme »). Une phrase, pas un paragraphe.
- **`evidence`** structuré (pas `evidence_level` plat) :
  - `confidence` (low/medium/high) — niveau de confiance global.
  - `source_policy` — règle d'acceptation explicite (`1_high` =
    une seule source haute fiabilité, `2_medium_concordant` = deux
    sources concordantes de fiabilité moyenne, `manual_review` = revue
    éditoriale obligatoire).
  - `reviewed` (bool) — statut de validation humaine.
  - **`diagnostic_safe`** (bool) — séparation explicite « preuve SEO »
    vs « preuve diagnostic ». Une source peut suffire à enrichir la
    fiche wiki sans être assez solide pour influencer le moteur
    diagnostic live (`__diag_*`).
- **`sources[]`** — identifiants stables des références (publications,
  guides OEM, manuels). Format slug stable, pas URLs.

### D2 — Modèle métier : références, jamais redéfinitions

La fiche gamme **ne contient plus** de bloc `diagnostic.symptoms[]` qui
redéfinit localement les symptômes. Tout symptôme nommé doit exister en
DB `__diag_symptom`. Le bloc `diagnostic.causes[]` et `diagnostic.quick_checks[]`
peut être conservé s'ils décrivent des éléments propres à la pièce
(critères d'inspection visuelle de la plaquette, etc.) qui ne sont pas
des symptômes système.

### D3 — Interdictions explicites (anti-patterns figés)

Cette ADR fige trois interdictions structurelles :

| Anti-pattern | Pourquoi c'est interdit |
|---|---|
| Créer `wiki/systemes/<slug>.md` (ou toute entity_type `system`) | DB `__diag_system` est SoT. Surface publique = `/diagnostic-auto/systeme/$slug` (frontend Remix). Une couche wiki système dupliquerait la DB. ADR-031 fige 5 entity_types (`gamme`, `vehicle`, `constructeur`, `support`, `diagnostic`), `system` n'en fait pas partie. |
| Créer `wiki/diagnostic/bruit-freinage.md` (ou tout fichier-par-symptôme) | Explosion du nombre de fichiers (62-65 symptômes), perte SEO (pages thin), duplication DB. La page publique du symptôme est servie par `/diagnostic-auto/symptome/$slug`. |
| Réécrire ou étendre le moteur diagnostic | Hors scope. ADR-032 traite le canon DB+backend. ADR-033 ne touche que le contrat sémantique markdown. |

### D4 — Migration 500+ fiches existantes — défaut conservateur

Le script de migration du `diagnostic.symptoms[]` actuel vers
`diagnostic_relations[]` produit un défaut **strictement conservateur** :

- `evidence.reviewed = false`
- `evidence.diagnostic_safe = false`
- `evidence.confidence = medium` par défaut
- `evidence.source_policy = "manual_review"` par défaut

Le flip à `reviewed = true` ou `diagnostic_safe = true` est **strictement
manuel ou couvert par règle ADR explicite**, jamais en automatique.

Le mapping label → `symptom_slug` est résolu par lookup contre
`__diag_symptom.slug` + `__diag_symptom.label_aliases[]` (à introduire
si non présent ; alternative : table de correspondance manuelle).
Toute ligne dont le mapping échoue produit une erreur bloquante et
nécessite triage éditorial avant migration.

### D5 — Validateur CI obligatoire

Une CI vault + monorepo bloque tout push qui :

1. Contient `diagnostic.symptoms:` dans `wiki/gamme/<slug>.md` (anti-pattern).
2. Référence un `symptom_slug` ou `system_slug` inexistant en DB.
3. Crée un fichier sous `wiki/systemes/` ou `wiki/diagnostic/<symptom>-*.md`.

Le validateur lit la liste des `__diag_symptom.slug` / `__diag_system.slug`
canon depuis un export JSON figé (`exports/diag-canon-slugs.json`)
généré nightly côté monorepo et committé dans le wiki.

### D6 — Évolution du contrat de page

`GammeContentContract.v1` → `GammeContentContract.v2` :

- Ajoute `diagnostic_relations[]` (optionnel mais recommandé).
- Retire `diagnostic.symptoms[]` (interdit).
- Conserve `diagnostic.causes[]` + `diagnostic.quick_checks[]` (réservés
  aux observations propres à la pièce, non couvertes par `__diag_symptom`).
- Cohabite avec `entity_data.maintenance.{educational_advice, related_pages}`
  introduit par ADR-032 (blocs frontmatter distincts, mêmes fiches `.md`).

Schema JSON (`_meta/schema/entity-data/gamme.schema.json`) updated en
conséquence avec validation stricte des champs `diagnostic_relations[]`.

---

## Décisions activement rejetées

| Proposition rejetée | Raison |
|---|---|
| Nom `diagnostic_links[]` | « Links » suggère un pointeur documentaire. « Relations » exprime le modèle métier contributif. |
| Champ `evidence_level` plat (low/medium/high seul) | Trop vague. Sans `source_policy` et `reviewed`, impossible de raisonner sur les edge cases ; sans `diagnostic_safe`, mélange preuve SEO et preuve diagnostic. |
| Couche `wiki/systemes/<slug>.md` | DB `__diag_system` est SoT. Duplication wiki sans valeur. |
| Fichier-par-symptôme `wiki/diagnostic/<symptom>.md` | Explosion fichiers, thin SEO, duplication DB. Frontend Remix sert `/diagnostic-auto/symptome/$slug`. |
| Conservation de `diagnostic.symptoms[]` local | Anti-pattern : pièce ne possède pas le symptôme. |
| Champ `system_slug` seul (sans `symptom_slug`) | Insuffisant : la relation pièce→symptôme se perd, on ne sait plus à quel symptôme la pièce contribue. |
| Migration automatique avec `diagnostic_safe = true` | Bricolage : aucune confiance sans revue humaine. Défaut strict `false`. |
| Feature flag `DIAGNOSTIC_RELATIONS_ENABLED` | Pas de bricolage transitoire (règle utilisateur `feedback_no_hybrid_workarounds`). Big-bang à la sortie du contrat v2. |

---

## Critères de succès

1. `_meta/schema/entity-data/gamme.schema.json` contient le bloc
   `diagnostic_relations` avec les champs D1, validation stricte des FK.
2. `rag/docs/GAMME_PAGE_CONTRACT.md` est en version 2.0 et documente
   l'interdiction de `diagnostic.symptoms[]`.
3. `template/new-gamme.md` reflète le bloc `diagnostic_relations[]` en
   exemple, sans `diagnostic.symptoms[]`.
4. `grep -rn "^  symptoms:" wiki/gamme/*.md` → **0** (toutes les fiches
   migrées vers `diagnostic_relations[]` au moment du flip v2).
5. `find wiki/systemes -type f 2>/dev/null | wc -l` → **0**.
6. `find wiki/diagnostic -type f 2>/dev/null | wc -l` → **0** (couvert
   par contrats `support` ou redirige vers frontend Remix uniquement).
7. CI validateur en place dans monorepo + vault qui bloque les 3
   anti-patterns D3 + slugs inexistants D5.
8. Au moment du flip v2 : pour chaque fiche migrée,
   `evidence.reviewed = false ET evidence.diagnostic_safe = false` par
   défaut (vérifiable par `yq` sur le batch migré).
9. Toute fiche dont `evidence.diagnostic_safe = true` doit avoir un
   commit signé d'un reviewer ≠ auteur du contenu (audit ad hoc).

---

## Implémentation

### Phase 1 — Contrat v2 (1 PR monorepo, 1 PR vault)

- **PR monorepo** : `_meta/schema/entity-data/gamme.schema.json` ajout
  `diagnostic_relations[]`, retrait `diagnostic.symptoms[]` du schéma
  (ou marqué deprecated avec deadline). `rag/docs/GAMME_PAGE_CONTRACT.md`
  bumpe v1 → v2. `template/new-gamme.md` mis à jour. Tests Jest
  validateur sur 5 fixtures (1 valide, 4 anti-patterns).
- **PR vault** : ce fichier ADR-033, lien dans `ops/moc/MOC-Decisions.md`
  (G2 zero-orphan).

### Phase 2 — Validateur CI (1 PR monorepo)

- Script `scripts/wiki/validate-gamme-diagnostic-relations.ts` exécuté
  en pre-commit hook + CI. Lit `exports/diag-canon-slugs.json` (généré
  nightly via cron monorepo : SELECT slug FROM `__diag_symptom`
  UNION SELECT slug FROM `__diag_system`).
- CI step `validate-wiki-gamme-relations` ajoutée à `.github/workflows/ci.yml`.

### Phase 3 — Export slugs canon (1 PR monorepo)

- Cron nightly `scripts/wiki/export-diag-canon-slugs.ts` qui fige les
  slugs canon dans `exports/diag-canon-slugs.json`. PR auto-générée
  vers le wiki si delta.

### Phase 4 — Migration 500+ fiches (1 PR monorepo + 1 PR wiki)

> **NOT COMPLETE (différée)** — les `symptoms:` legacy (≈ « 500+ fiches » recyclées, rag/knowledge) vivent encore côté RAW ; re-source curé requis, jamais RAG→relations (cf. § Reconciliation).

- Script `scripts/wiki/migrate-symptoms-to-relations.ts` :
  1. Lit chaque `wiki/gamme/<slug>.md`.
  2. Pour chaque entrée `diagnostic.symptoms[]`, lookup label →
     `symptom_slug` via mapping éditorial validé (bail si lookup échoue).
  3. Écrit `diagnostic_relations[]` avec défauts D4 stricts.
  4. Retire `diagnostic.symptoms[]`.
- Mode `--dry-run` obligatoire pour audit avant write.
- Mode `--per-system` permet migration progressive (freinage d'abord,
  puis distribution, etc.) si volume difficile à reviewer en bloc.

### Phase 5 — Documentation skill `wiki-proposal-writer` (1 PR monorepo)

- Le skill existant (`/.claude/skills/wiki-proposal-writer/`) est mis à
  jour pour produire `diagnostic_relations[]` et **jamais** `diagnostic.symptoms[]`.

---

## Revue planifiée

**Date** : 2026-05-29 (J+30 après acceptation) *(historique — échéance dépassée ; readiness réel atteint 2026-05-01, cf. `ledger/knowledge/adr-033-wave-2-closed-20260501.md` ; statut formalisé 2026-07-07, voir § Reconciliation)*

**Critères de revue** :
- Au moins 1 batch system migré (idéalement freinage : ~20 fiches).
- Validateur CI déployé et bloquant en CI ≥ 2 semaines.
- Aucun fichier `wiki/systemes/*` ou `wiki/diagnostic/<symptom>-*` créé.
- Feedback éditorial : le défaut `evidence.reviewed = false` n'a pas été
  contourné en bloc (audit `git log --grep "diagnostic_safe.*true"`).

---

## Suivi

- **Plan d'audit source** : `/home/deploy/.claude/plans/verifier-exsitant-tout-agent-dapper-kite.md`
  (session 2026-04-29).
- **Mémoire Claude Code** : `diagnostic-engine-breezy-eagle.md` (corrections
  audit 2026-04-29).
- **Anti-patterns documentés** : couche `wiki/systemes/`, fichier-par-symptôme,
  champ `evidence_level` plat, `diagnostic_safe` défaut `true`.
