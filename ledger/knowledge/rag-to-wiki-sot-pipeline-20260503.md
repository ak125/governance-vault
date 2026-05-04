---
type: knowledge
status: canon
created: 2026-05-03
updated: 2026-05-04
tags: [adr-031, rag-to-wiki, pipeline-canon, refactor, scripts-placement, wiki-sot, rag-mirror, in-progress]
related-adr: [ADR-031]
related-prs: [automecanik-wiki#17, automecanik-raw#15, nestjs-remix-monorepo#270, nestjs-remix-monorepo#275, nestjs-remix-monorepo#286, automecanik-rag#11, automecanik-rag#12, automecanik-wiki#19, governance-vault#141]
related-memory: [feedback_no_bricolage_clean_layer, feedback_verify_existing_first, feedback_no_hybrid_workarounds, wiki-raw-architecture-handoff, rag-to-wiki-sot-pivot-20260503]
verdict: PARTIAL_COVERAGE (8/9 étapes plan v3 livrées + gardes, reste Étape 6 régénération qui demande exécution dédiée DEV)
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

## État livré 2026-05-02 → 2026-05-04 (8/9 étapes + gardes)

| Étape | PR | Repo | Statut | Contenu |
|---|---|---|---|---|
| 3 | [#17](https://github.com/ak125/automecanik-wiki/pull/17) | wiki | ✅ MERGED | Audit classification 329 fiches : 216 auto, 61 humain, 52 ambigus + 36 role_map |
| 4 | [#15](https://github.com/ak125/automecanik-raw/pull/15) | raw | ✅ MERGED | Import 365 fichiers (329 .md + 36 .role_map.json) → `recycled/rag-knowledge/<cat>/` byte-perfect sha256 |
| 5 PR-1 | [#270](https://github.com/ak125/nestjs-remix-monorepo/pull/270) | monorepo | ✅ MERGED | Refactor placement 6 scripts → `wiki-generators/`, `wiki-exports/`, `rag-sync/`, `raw-downloaders/` (pure git mv, logique inchangée) |
| 5 PR-3 | [#275](https://github.com/ak125/nestjs-remix-monorepo/pull/275) | monorepo | ✅ MERGED | Redirection OUTPUT path wiki-generators vers `wiki/exports/rag/<cat>/` (env `AUTOMECANIK_WIKI_PATH`) |
| 5 follow-up | [#11](https://github.com/ak125/automecanik-rag/pull/11) | rag | ✅ MERGED | Wrapper `run-phase-f.sh` paths post-refactor |
| 2 receveur | [#12](https://github.com/ak125/automecanik-rag/pull/12) | rag | ✅ MERGED | Workflow CI `sync-rag-from-wiki.yml` (3 triggers : repository_dispatch, workflow_dispatch, daily schedule safety net) |
| 2 sender | [#19](https://github.com/ak125/automecanik-wiki/pull/19) | wiki | ✅ MERGED | Workflow CI `dispatch-rag-sync.yml` (push wiki main + path `exports/rag/**` → dispatch event vers rag, mode no-op si PAT absent) |
| 9 | [#286](https://github.com/ak125/nestjs-remix-monorepo/pull/286) | monorepo | 🟢 OPEN (auto-merge) | ast-grep règle `no-direct-rag-knowledge-write.yml` (severity warning, scope wiki-generators/wiki-exports/raw-downloaders) + cleanup defaults raw-downloaders |
| Knowledge | [#141](https://github.com/ak125/governance-vault/pull/141) | vault | ✅ MERGED | Consigne pivot architectural session 2026-05-02→03 |

## Étapes restantes plan v3 (handoff next session)

### Sync activé bout-en-bout 2026-05-04 — 36 brands mirrored ✅

Premier sync réel post-pivot :

```
36 brands DB+Wikidata+Wikipedia
    ↓ scripts/wiki-generators/brand-fiche-generator.py
36 fichiers wiki/exports/rag/constructeurs/<slug>.md
    ↓ wiki PR #22 MERGED (Pattern B Pattern: contenu commit)
main wiki @ 986928a
    ↓ cron VPS DEV (monorepo PR #288 MERGED)
36 fichiers rag/knowledge/constructeurs/<slug>.md (mirror)
    ↓ git commit "synced-from-wiki: 986928a" (D22 hook fix PR rag #14 MERGED)
rag main @ d5e27b62 ✅
```

**Étape 8 backend = no-op** : `rag-pipeline.service.ts:224` lit `path.join(this.knowledgePath, 'gammes', dto.scope)`, le path layout `<root>/<entity>/<slug>.md` est identique entre legacy et mirror. Aucune adaptation nécessaire.

### Découverte Étape 6 gammes — script enricher, pas générateur

`scripts/wiki-generators/gamme-from-web-corpus-generator.py` n'est **pas un générateur** comme `brand-fiche-generator.py` — c'est un **enricher** qui ajoute des données techniques (`phase5_enrichment` block) à des fiches gammes EXISTANTES dans `wiki/exports/rag/gammes/`.

Test dry-run 2026-05-04 :
```
237 gammes avec fichiers web OEM
1149 fichiers mappés total
Résultat : 0 gammes enrichies (0 sans données | 0 filtrées | 0 protégées)
```

**Cause** : `gamme_path = GAMMES_DIR/<slug>.md` n'existe pas → `continue`. L'enricher saute toutes les gammes car aucune fiche initiale n'existe dans `wiki/exports/rag/gammes/`.

**Impact Étape 6 gammes** : pas de pipeline complet sans script générateur initial. 2 options :

1. **Créer `gamme-skeleton-generator.py`** qui génère les fiches gammes initiales depuis DB (`auto_pieces_gamme`), puis lance l'enricher
2. **Importer les 241 gammes du legacy** (`automecanik-raw/recycled/rag-knowledge/gammes/` post PR raw #15) vers `wiki/exports/rag/gammes/`. L'enricher peut ensuite ajouter les blocs phase5

**Décision reportée** : à arbitrer next session. Pour l'instant, Étape 6 gammes bloquée. Brands livrés (36/36).

### Pivot architectural 2026-05-04 — cron VPS DEV remplace GitHub Actions cross-repo

**Décision user** : *« meilleure solution pas de bricolage »*. Les workflows
GitHub Actions du sync (rag #12 receveur + wiki #19 dispatcher avec PAT
`RAG_DISPATCH_PAT`) étaient du bricolage défensif :

| Bricolage initial | Pourquoi c'était inutile |
|---|---|
| 3 `actions/checkout` dans le receveur | Les 3 clones git existent déjà sur DEV VPS |
| `actions/setup-python@v5` | python3 + stdlib disponibles localement |
| PAT cross-repo `RAG_DISPATCH_PAT` rotation 90j | Deploy bot SSH key déjà active |
| Dispatcher HTTP API call | Pour un sync 100% local |
| `schedule: daily` safety net | Redondant avec cron horaire |

**Pattern canonique remplaçant** (PR monorepo #288) :
`scripts/cron/sync-rag-from-wiki.sh` + 1 ligne crontab DEV VPS.
Pull wiki + pull rag + sync filesystem + commit/push avec deploy bot SSH.
Lock global `/tmp/rag-global.lock` (compatible avec `run-phase-f.sh`).

**Reverts associés** :
- PR rag #13 : remove `.github/workflows/sync-rag-from-wiki.yml`
- PR wiki #20 : remove `.github/workflows/dispatch-rag-sync.yml`
- User action post-merge : retirer secret `RAG_DISPATCH_PAT` côté wiki

**Leçon retenue** : pour un setup mono-VPS avec assets locaux complets
(clones git, SSH keys, env vars, cron pattern éprouvé), GitHub Actions
cross-repo est du bricolage. Cron local = pattern canon.

---

### Smoke test Étape 6 — chaîne validée localement 2026-05-04

`brand-fiche-generator.py --brand renault` lancé en DEV avec credentials
chargés depuis `backend/.env` :
- ✅ Wikidata Q6686 résolu (Renault)
- ✅ DB Supabase : 40 vehicles → 8 models, 6 engines
- ✅ Wikipedia FR REST OK (412 chars history)
- ✅ Frontmatter 17 champs valides écrit dans `wiki/exports/rag/constructeurs/renault.md`
- ⚠️ Bug mineur : `BRANDS_DIR.mkdir(parents=True, exist_ok=True)` manquant —
  `mkdir -p` à faire avant ou patcher le script.

**Le pipeline est mécaniquement fonctionnel.** Le smoke output a été nettoyé
post-test (gitignore — voir dilemme ci-dessous).

### Dilemme architectural découvert post smoke test

**`automecanik-wiki/.gitignore` ligne 1-4** :
```
# Exports générés — contenu gitignored, contrats schema commités
exports/rag/**
exports/seo/**
exports/support/**
!exports/**/.gitkeep
```

L'intention initiale Phase B.3 (commit `ebacc7c`) était : le contenu de
`exports/rag/` est régénéré à la demande, pas commité. Mais ça pose problème
pour le CI sync : le runner checkout wiki main et trouve `exports/rag/` vide.

3 patterns possibles à arbitrer next session :

| Pattern | Pro | Con |
|---|---|---|
| **A** : `exports/rag/**` reste gitignored, **le workflow CI sync lance les générateurs** avant copy | Contenu toujours fresh, pas de drift git, philosophie initiale respectée | Sync coûteux (Wikidata + Wikipedia + DB), nécessite SECRET_SERVICE_ROLE_KEY côté rag, fragile si rate limits |
| **B** : Délister `exports/rag/**` du gitignore, **commit le contenu généré** | Sync simple (pure file copy), reproducible, audit trail | Commits "auto" polluent git log, drift possible si génération non-régulière |
| **C** : Workflow séparé côté monorepo qui exécute les générateurs et **push le résultat dans wiki** ; le sync rag fait pure copy | Séparation claire (génération monorepo, stockage wiki, sync rag), pas de secret côté rag | 3-stage pipeline plus complexe à débugger |

**Recommandation** : Pattern **B** (déférence au gitignore par défaut, mais commit
explicite). Pattern A trop fragile (un down réseau bloque le sync). Pattern C trop
complexe pour le ROI. Mais l'arbitrage user reste à faire.

### Étapes 6/7/8

| # | Description | Prereq | Notes |
|---|---|---|---|
| **6** | **Régénération via générateurs refactorisés vers `wiki/exports/rag/`** | toutes Étapes 1-5 + 9 ✅ + arbitrage gitignore (Pattern A/B/C) | Smoke test 1 brand ✅. Reste 35 brands + 200+ gammes + diagnostic. Patcher `mkdir(parents=True, exist_ok=True)` dans les 3 wiki-generators avant batch run. |
| 7 | Activer workflow CI sync (premier run réel) | Étape 6 + arbitrage gitignore + secret `RAG_DISPATCH_PAT` côté wiki | Une fois wiki/exports/rag/ peuplé via Étape 6 → premier sync vers automecanik-rag/knowledge/. Mode `--prune` pour nettoyer orphans legacy. |
| 8 | Cleanup contenu legacy rag/knowledge/ + adapter backend `rag-pipeline.service.ts:224` | Étape 7 | Backend lit `RAG_KNOWLEDGE_PATH/gammes/<scope>` ligne 224 — vérifier compatibilité avec mirror (probablement OK car même path layout), sinon adapter. |

**Note Étape 9** : la garde ast-grep côté monorepo + le hook D22 commit-msg / workflow CI d22-protected-paths côté rag (déjà existants depuis Phase F0.c.2) couvrent ensemble la garde permanente.

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
