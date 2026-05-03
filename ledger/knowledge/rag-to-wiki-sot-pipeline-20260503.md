---
type: knowledge
status: canon
created: 2026-05-03
updated: 2026-05-03
tags: [adr-031, rag-to-wiki, pipeline-canon, refactor, scripts-placement, wiki-sot, rag-mirror, in-progress]
related-adr: [ADR-031]
related-prs: [automecanik-wiki#17, automecanik-raw#15, nestjs-remix-monorepo#270]
related-memory: [feedback_no_bricolage_clean_layer, feedback_verify_existing_first, feedback_no_hybrid_workarounds, wiki-raw-architecture-handoff]
verdict: PARTIAL_COVERAGE (3/9 étapes plan v3 livrées, 6 restantes)
---

# rag → wiki SoT, rag = mirror — câblage ADR-031 §D20/D22 (session 2026-05-02 → 2026-05-03)

> Session qui acte le pivot architectural majeur :
> **`automecanik-wiki/` devient la source de vérité éditoriale**, et
> **`automecanik-rag/knowledge/` devient un mirror read-only** alimenté par
> CI workflow `sync-from-wiki`. ADR-031 §D20/D22 a toujours dit ça depuis
> 2026-04-28, mais le pipeline n'avait jamais été câblé en pratique : 6+
> générateurs écrivaient directement dans `automecanik-rag/knowledge/`, et
> `automecanik-wiki/exports/rag/` était vide.
>
> Plan figé : `/home/deploy/.claude/plans/je-comprend-rien-a-spicy-reddy.md`.

## Le constat (audit Explore 2026-05-02)

- **6+ générateurs** dans `/opt/automecanik/app/scripts/rag/` écrivaient
  directement dans `automecanik-rag/knowledge/` :
  - `build-brand-rag.py` → 36 constructeurs (Wikidata + Wikipedia + RPC, auto)
  - `rag-enrich-from-web-corpus.py` → 141 gammes (web corpus, auto)
  - `enrich-rag-bulk.py` → gammes via DB templates (auto)
  - `script:materialize-db-to-md` → 37 diagnostic (DB → md, auto)
  - `skill:phase5-vague{4,5,6}-*` → 61 gammes (humain, à préserver)
  - `r7-brand-rag-generator` → 36 constructeurs (auto)
- **`wiki/exports/rag/`** : `.gitkeep` seul depuis création. Destination
  prévue par §D20 jamais alimentée.
- **`sync-from-wiki.py`** : existait dans `app/scripts/rag/` avec garde D20
  enforcement (refuse source ≠ wiki/exports/rag/) + sha256 idempotent — mais
  **aucun `.github/workflows/*.yml` ne l'invoquait**. Pipeline mort.
- Conséquence : tout le contenu vivait dans rag/knowledge/ via générateurs
  qui sautaient l'étape canon, en violation de §"tout brut → raw, validé → wiki".

## Le pivot user (3 décisions cumulées 2026-05-02)

1. *« Pas de bricolage »* — refus initial de l'option d'importer 329 fiches
   en bloc dans `wiki/proposals/` (zone réservée à la curation humaine,
   alors que les 329 fiches sont des outputs de scripts auto-générés).
2. *« Récupère toute cette valeur »* — toutes les fiches préservées byte
   pour byte ; aucune ne peut être perdue avant régénération vérifiée.
3. *« Pourquoi on importe pas de la raw au lieu du proposal ? »* — la vraie
   question architecturale. Les 329 .md sont du brut historique (outputs
   de scripts), donc place naturelle = `automecanik-raw/recycled/rag-knowledge/<cat>/`,
   cohérent avec ADR-031 et avec l'intent déjà documenté dans
   `automecanik-raw/manifests/source-classification.md` ligne 41 :
   > « RAG knowledge | rag-knowledge/ | Anciens fichiers
   > automecanik-rag/knowledge/{gammes,vehicles,constructeurs,guides,reference}/ »
4. *« Si on archive le rag, wiki va écrire dans quel rag ? »* —
   **`automecanik-rag` n'est PAS archivé**. Reste vivant comme mirror
   read-only. C'est seulement son contenu legacy qui migre vers raw, puis
   sera remplacé progressivement par le mirror.

## Pipeline cible (état après plan v3 complet)

```
[automecanik-raw]                    sources brutes (web clips, evidence, PDFs)
        │                            + 365 .md métier importés Étape 4 (recycled/rag-knowledge/<cat>/)
        ▼
[app/scripts/wiki-generators/]       lit raw + DB, produit fiches candidates
        │                            (refactor placement Étape 5 PR-1 fait)
        ▼
[automecanik-wiki/proposals/]        review humaine via PR (existant, déjà éprouvé)
        │
        ▼ promotion humaine
[automecanik-wiki/wiki/<entity>/]    SoT humain canonique
        │
        ▼ export
[app/scripts/wiki-exports/]          transforme wiki → format rag-ready (à créer Étape 5 PR-3)
        │
        ▼
[automecanik-wiki/exports/rag/]      artefact généré, dans le repo wiki
        │
        ▼ CI workflow sync-wiki-exports-to-rag (Étape 7 à créer)
[automecanik-rag/knowledge/]         mirror read-only, consommé par chatbot/RAG
```

## État livré 2026-05-02 → 2026-05-03 (PRs)

| Étape | PR | Repo | Statut | Contenu |
|---|---|---|---|---|
| 3 | [#17](https://github.com/ak125/automecanik-wiki/pull/17) | wiki | ✅ MERGED | Audit classification 329 fiches : 216 auto, 61 humain, 52 ambigus + 36 role_map |
| 4 | [#15](https://github.com/ak125/automecanik-raw/pull/15) | raw | ✅ MERGED | Import 365 fichiers (329 .md + 36 .role_map.json) → `recycled/rag-knowledge/<cat>/` byte-perfect sha256 |
| 5 PR-1 | [#270](https://github.com/ak125/nestjs-remix-monorepo/pull/270) | monorepo | 🟢 OPEN (CI) | Refactor placement 6 scripts → `wiki-generators/`, `wiki-exports/`, `rag-sync/`, `raw-downloaders/` (pure git mv, logique inchangée) |

## Étapes restantes plan v3 (handoff next session)

| # | Description | Prereq | Notes |
|---|---|---|---|
| 5 PR-3 | Redirection OUTPUT path des `wiki-generators/` vers `wiki/exports/rag/<cat>/` | merge PR #270 | Modif constantes Python `OUTPUT_DIR` dans 3 scripts. Frontmatter ajoute `kind: generated`, `produced_by`, `produced_at`. |
| 5 follow-up rag | Update `automecanik-rag/scripts/pipeline/run-phase-f.sh` paths | merge PR #270 | Wrapper référence encore `scripts/rag/` (lignes 49, 55, 140). Cron déjà inactif (dernière run 2026-04-26). |
| 2 | Workflow CI `sync-rag-from-wiki.yml` (dans repo automecanik-rag ou monorepo) | — | Trigger `repository_dispatch` depuis wiki push main + path `exports/rag/**`. Bot account commit avec marker `synced-from-wiki: <wiki-sha>`. |
| 6 | Régénération via générateurs refactorisés vers `wiki/exports/rag/` | Étape 5 PR-3 mergée | Lancer chaque générateur localement DEV. Diff vs legacy doit être minimal. |
| 7 | Activer workflow CI sync (premier run réel) | Étape 2 + 6 | wiki/exports/rag/ rempli → sync vers automecanik-rag/knowledge/. Mode `--prune` pour nettoyer orphans. |
| 8 | Cleanup contenu legacy rag/knowledge/ + adapter backend `rag-pipeline.service.ts:224` | Étape 7 | Backend lit `RAG_KNOWLEDGE_PATH/gammes/<scope>` ligne 224 — vérifier compatibilité avec mirror, sinon adapter le path. |
| 9 | Garde permanente (pre-commit + ast-grep) | Étape 8 | Refus tout commit `knowledge/*.md` sans marker `synced-from-wiki:`. ast-grep règle : refus literal `automecanik-rag/knowledge/` dans monorepo. |

## Décisions canoniques (à NE PAS redécider next session)

- (a) PR #16 (promotion 9 fiches via `recycle-from-rag.py` lecture rag direct)
  → **closed (drop)** — cristallisait la violation §D22.
- (b) Wiki est SoT, rag est artefact mirror. Plus jamais d'écriture directe
  dans `automecanik-rag/knowledge/` par humain ou script.
- (c) Toutes les 329 fiches métier preservées dans `automecanik-raw/recycled/rag-knowledge/`
  byte-perfect. Audit JSON `automecanik-wiki/_audit/rag-content-classification-2026-05-02.json`
  enrichit les manifests raw avec `origin_class` et `last_enriched_by`.
- (d) Refactor scripts = **placement architectural sans réécriture**. La logique
  métier reste à 100%, seuls les paths d'OUTPUT et le placement changent.
- (e) `automecanik-rag` repo n'est PAS archivé. Reste vivant comme mirror
  read-only via CI sync.

## Apprentissages clés (à figer en mémoire)

1. **Avant d'importer en bulk dans wiki/proposals/**, distinguer :
   - Fiches **humainement enrichies** (`skill:*` ou `human:@*`) → légitime
   - Fiches **auto-générées** (`script:*` ou `r7-*`) → vont dans raw ou
     régénérées, JAMAIS dans proposals/.
2. **Quand un repo de "knowledge généré" semble être consommé en prod**
   (référencé par backend), grep le code avant de toucher : risque réel
   de régression invisible.
3. **`wiki/exports/rag/` est un répertoire DUAL-PRODUCTEUR** : à la fois
   rempli par wiki-generators (auto) et écrasable par wiki-exports (humain).
   La version humaine prime, par convention que B passe après A dans le
   pipeline CI.
4. **Refactor de placement** n'est PAS une réécriture. `git mv` preserves
   l'historique. Logique Python intouchée → review trivial. La complexité
   métier vient des PR suivantes (redirection OUTPUT).
5. **Pas de garde de kill-switch defensive** quand aucun script n'est
   invoqué en CI (cas vérifié ici : 0 référence dans `.github/workflows/`).
   Le refactor direct (PR-3) suffit. Évite la garde à arracher plus tard.

## Évidences

- `automecanik-wiki/_audit/rag-content-classification-2026-05-02.json` —
  classification des 329 fiches.
- `automecanik-raw/manifests/rag-knowledge-metier-inventory-2026-05.json` —
  inventaire des 365 imports avec sha256 + origin_class.
- `automecanik-raw/manifests/exemptions.yaml` — 8 patterns Gate A pour
  les 8 catégories métier (deadline 2026-12-31, schema 5.0 legacy preserve).
- 3 PRs (#17 wiki, #15 raw, #270 monorepo) — voir liens ci-dessus.

## Référence

- ADR-031 — Raw / Wiki / RAG / SEO Separation (vault)
- Plan v3 — `/home/deploy/.claude/plans/je-comprend-rien-a-spicy-reddy.md`
- Memory `wiki-raw-architecture-handoff.md` — état Phases A→F.3
