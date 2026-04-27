---
id: ADR-026
title: "Content Repository Separation — automecanik-content as SEO Refined Layer"
status: proposed
date: 2026-04-26
decision_date: null
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
related_rules: ["G1", "G2", "G3", "G5", "AP-10", "AP-11"]
related_incidents: []
related_adr: ["ADR-012", "ADR-015", "ADR-022", "ADR-025", "ADR-027", "ADR-029"]
reviewed_by: null
---

# ADR-026: Content Repository Separation — `automecanik-content` as SEO Refined Layer

## Contexte

Au 2026-04-26, `automecanik-rag/knowledge/` héberge **22 sous-dossiers** mélangeant
quatre natures de contenu pour deux audiences distinctes, sans aucune frontière
explicite ni au filesystem ni au pipeline d'ingestion :

| Sous-dossier | Volume | Nature réelle | Audience cible |
|---|---|---|---|
| `_raw/` | 5 entrées, **299 MB** | Sources brutes (PDF, videos, evidence, web-images) | aucun consommateur direct — SOURCE |
| `web/` | 1687 fichiers, 13 MB | Scraping HTML brut chunké | aucun consommateur direct — SOURCE |
| `web-catalog/` | 182 fichiers, 804 KB | Scraping catalogue brut | aucun consommateur direct — SOURCE |
| `web-vehicles/` | 12 fichiers, 244 KB | Scraping véhicules brut | aucun consommateur direct — SOURCE |
| `gammes/` | 241 fichiers, 20 MB | Fiches gammes (lifecycle stage `v5_ssot` → `v5_indexed`) | **SEO R3/R4/R6** + chatbot |
| `vehicles/` | 83 fichiers, 444 KB | Fiches véhicules au niveau modèle | **SEO R8** (cf. ADR-022) |
| `constructeurs/` | 72 fichiers, 304 KB | Hubs marques | **SEO R7** |
| `guides/` | 16 fichiers, 100 KB | Guides pratiques | **SEO** + chatbot |
| `reference/` | 1 fichier, 8 KB | Références techniques (ECE-R90) | **SEO** |
| `diagnostic/` | 18 fichiers, 136 KB | Diagnostics symptôme/cause/solution | chatbot support + R5 (ADR-027 déprécie R5 standalone) |
| `faq/` | 7 fichiers, 32 KB | Questions/réponses support | chatbot support |
| `faqs/` | 1 fichier, 8 KB | duplicate `faq/` (à fusionner) | chatbot support |
| `policies/` | 3 fichiers, 20 KB | Politiques retours/garantie/livraison | chatbot support |
| `seo-data/` | 7 fichiers, 388 KB | CSV Google Ads, search volumes | input pipeline SEO |
| `structured/`, `tabular/`, `canonical/`, `catalog/`, `seo/`, `maintenance/` | < 50 fichiers cumul | Outputs intermédiaires pipeline / fixtures / vides | mixte / inconnu |
| `_quarantine/`, `media/` | 0 fichier | Dossiers système | aucun |

**Conséquences concrètes du mélange** :

1. **Pollution chatbot RAG**. Le README de `knowledge/` (lignes 38-43) annonce
   indexation Weaviate sur tout `knowledge/` ; en pratique 299 MB de PDF binaires
   et 1687 fragments HTML scrapés cohabitent avec les fiches éditoriales —
   filtrage actuel implicite, non documenté, fragile.

2. **Pas de séparation d'audience**. SEO publishers (R0-R8, audience Google +
   visiteurs) et chatbot support (audience client en service) consomment des
   formats différents (longue prose structurée vs Q&A courtes), mais piochent
   dans le même panier.

3. **Editorial vs pipeline confondus**. Tout contenu humain rédigé/raffiné
   partage repo + PR queue + CODEOWNERS avec le code Python du pipeline RAG +
   le scraping généré machine. Effets : git log pollué par 299 MB `_raw/`,
   reviews mélangent code + prose, pas de granularité d'accès éditorial.

4. **ADR-022 (R8) en tension**. La couche L2 "Content repository : commit via
   PR signée G3" canonise déjà *implicitement* la séparation : les schemas R8
   (`vehicle-model.schema.json`, `vehicle-variations.schema.json`, `vehicle-role-map.schema.json`)
   vivent au vault, mais les fichiers `vehicles/*.md` restent sous-locataires
   du repo `automecanik-rag`. Pas un repo dédié.

5. **ADR-029 (RAG v2.1 closure)** introduit `__rag_enrichment_runs` + state
   machine 7 stages pour les **gammes**. Sans séparation de couche, la
   transition `v5_ssot` → `v5_indexed` mélange refinement éditorial (output
   SEO) et indexation Weaviate (output chatbot) sur les mêmes frontmatters.

Le repo `ak125/automecanik-content` a été créé hors ledger canon ; cette ADR
documente formellement la décision pour respecter G1 (canon fait foi), G5
(`.spec/00-canon/` ou `ledger/decisions/adr/` autoritatifs), G2 (zéro orphelin —
référence ADR du repo), AP-10 (services <500 lignes / structure lisible),
AP-11 (verify existing first — confirmé via inspection 22 sous-dossiers
+ 4 ADRs adjacents).

## Décision

Adopter une **architecture deux-repos pairs alimentés par une couche source
commune**, avec frontière explicite par **audience finale** (SEO publishers
vs chatbot support), refinement bidirectionnel orchestré par agents
déterministes, et migration atomique unique vers `ak125/automecanik-content`.

### Modèle conceptuel — 3 couches, 2 repos, refinement bidirectionnel

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 0 — SOURCE (SoT brut, repo automecanik-rag)                    │
│   automecanik-rag/_raw/  — PDF, videos, evidence, web-images         │
│   automecanik-rag/_raw/web/, web-catalog/, web-vehicles/  — scraping │
│   Source unique de vérité pour toute donnée brute. Jamais éditée     │
│   manuellement. Accédée en lecture par les refiner agents.           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
┌─────────────────────────┐  ┌──────────────────────────────────────┐
│ REFINER SEO             │  │ REFINER SUPPORT                      │
│ (NestJS / Python,       │  │ (NestJS / Python,                    │
│  déterministe, gates    │  │  déterministe, gates                 │
│  ADR-022/ADR-029)       │  │  ADR-029)                            │
└────────────┬────────────┘  └──────────────────┬───────────────────┘
             ▼                                  ▼
┌──────────────────────────────┐  ┌────────────────────────────────────┐
│ LAYER 1A — CONTENT REFINED   │  │ LAYER 1B — RAG REFINED             │
│ (repo automecanik-content)   │  │ (repo automecanik-rag/knowledge/)   │
│                              │  │                                    │
│   wiki/gammes/*.md           │  │   knowledge/diagnostic/*.md         │
│   wiki/vehicles/*.md         │  │   knowledge/faq/*.md                │
│   wiki/constructeurs/*.md    │  │   knowledge/policies/*.md           │
│   wiki/guides/*.md           │  │   knowledge/maintenance/*.md (?)    │
│   wiki/reference/*.md        │  │                                    │
│   _data/*.csv (seo-data)     │  │                                    │
│                              │  │                                    │
│ Audience : SEO publishers,   │  │ Audience : chatbot client support  │
│   R0-R8 generators, lecteurs │  │   (Weaviate index `prod:chatbot`)  │
│   Google                     │  │                                    │
│ Format : prose structurée    │  │ Format : Q&A courtes, decision-    │
│   longue, sections H2/H3,    │  │   trees, policies                  │
│   media slots, JSON-LD       │  │                                    │
└─────────────────┬────────────┘  └─────────────────┬──────────────────┘
                  │                                 │
                  ▼                                 ▼
        R0-R8 SEO pipeline               Weaviate `prod:chatbot`
        (génération pages publiques)     (réponses chatbot client)
                  ▲                                 ▲
                  └─────────────┬───────────────────┘
                                │
                  CROSS-POLLINATION (refinement secondaire)
                  Articles SEO peuvent être dérivés en Q&A support.
                  Patterns chatbot peuvent suggérer gaps de contenu SEO.
                  Orchestré par scripts dédiés (hors scope ADR-026).
```

### Éléments structurants

1. **Repo cible** : `ak125/automecanik-content` (déjà créé hors ledger ; cette
   ADR le ratifie). Aucun autre repo introduit.

2. **Layer 0 (`_raw/`) reste dans `automecanik-rag`**. Le scraping, l'ingestion
   PDF, l'extraction web restent sous `automecanik-rag/_raw/` et
   `automecanik-rag/_raw/web*/`. Aucune migration de cette couche. Pourquoi :
   `_raw/` ≠ contenu refiné ≠ audience SEO ; le pipeline d'ingestion existant
   y écrit.

3. **Migration LAYER 1A — `automecanik-rag/knowledge/{gammes,vehicles,constructeurs,guides,reference}/`
   → `automecanik-content/wiki/`**. Default mapping (à confirmer en review
   de PR) :

   | Source | Destination | Justification |
   |---|---|---|
   | `automecanik-rag/knowledge/gammes/` (241) | `automecanik-content/wiki/gammes/` | Audience SEO R3/R4/R6 |
   | `automecanik-rag/knowledge/vehicles/` (83) | `automecanik-content/wiki/vehicles/` | Audience SEO R8 (ADR-022) |
   | `automecanik-rag/knowledge/constructeurs/` (72) | `automecanik-content/wiki/constructeurs/` | Audience SEO R7 |
   | `automecanik-rag/knowledge/guides/` (16) | `automecanik-content/wiki/guides/` | Audience SEO majoritaire |
   | `automecanik-rag/knowledge/reference/` (1) | `automecanik-content/wiki/reference/` | Audience SEO |
   | `automecanik-rag/knowledge/seo-data/` (7 CSV) | `automecanik-content/_data/` | Input pipeline SEO |
   | `automecanik-rag/knowledge/seo/` (2) | **review au cas par cas** | À sniffer par le réviseur PR |
   | `automecanik-rag/knowledge/structured/`, `tabular/`, `canonical/`, `catalog/` | **reste** dans `automecanik-rag` (`/_raw/` si vraiment scraping output) | Données pipeline brutes |

4. **LAYER 1B — `automecanik-rag/knowledge/{diagnostic,faq,faqs,policies,maintenance,_quarantine,media}/`
   reste sous `automecanik-rag/knowledge/`**. Audience chatbot support ; format
   adapté Weaviate `prod:chatbot`. La duplication `faq` vs `faqs` est nettoyée
   séparément hors scope migration (1 fichier à fusionner).

5. **Cas spécial `diagnostic/`**. Audience double (chatbot support + ADR-027
   déprécie R5 standalone, consolide dans R3 S2). Décision : reste sous
   `automecanik-rag/knowledge/diagnostic/`. Le pipeline R3 (qui consommait
   `automecanik-rag/knowledge/diagnostic/`) continue d'y lire — change après
   migration : R3 lit désormais le contenu R3 dans `automecanik-content/wiki/gammes/`
   (déjà migré), et conserve l'accès `diagnostic/` côté `automecanik-rag/`
   pour la sous-section S2 diag (path absolu via env var, voir §6).

6. **Couplage runtime, pas couplage git** — pattern deux-clones-côte-à-côte +
   env var, **pas** git submodule. Précédent : `governance-vault` est cloné
   indépendamment et lu via path absolu (`/opt/automecanik/governance-vault/`
   sur DEV, ADR-012 / ADR-015). Variables d'environnement ajoutées :

   ```
   AUTOMECANIK_CONTENT_PATH   # défaut /opt/automecanik/content/
   AUTOMECANIK_RAG_PATH       # défaut /opt/automecanik/rag/  (existant)
   ```

   Aucune variable globale unique substituée — refacto progressif des scripts
   qui hardcodent `/opt/automecanik/rag/knowledge/{gammes,vehicles,…}/` pour
   pointer `${AUTOMECANIK_CONTENT_PATH}/wiki/{gammes,vehicles,…}/`.

7. **Ingestion Weaviate filtrée** — l'ingestion vers `prod:chatbot` (chatbot)
   ne doit consommer **que** `automecanik-rag/knowledge/` (post-migration :
   diagnostic + faq + policies + …). L'ingestion vers `dev:full` (agents
   internes) consomme **les deux** (`automecanik-rag/knowledge/` +
   `automecanik-content/wiki/`). Une nouvelle index `prod:seo` peut être
   introduite pour les R0-R8 mais hors scope ADR-026 (non bloquant).

8. **Refiner agents — hors scope ADR-026**. Les agents qui transforment
   `_raw/*` → `wiki/*` (côté SEO) ou `_raw/*` → `knowledge/*` (côté support)
   ne sont pas définis ici. ADR-022 couvre déjà le refiner SEO R8 (vehicles).
   ADR-029 couvre la state machine v2.1 sur gammes. Les autres refiners
   feront l'objet d'ADRs dédiées au fur et à mesure (suggestion :
   ADR-031 refiner SEO R3/R4/R6 gammes, ADR-032 refiner support diagnostic,
   etc.).

9. **R8 rotation conservée** — Décision @fafa explicite : la rotation
   déterministe TemplateRotator d'ADR-022 (SHA-256(salt:slug:typeId)) est
   conservée. L'amélioration de la diversité (au-delà du fingerprint gate
   + rotation actuels) fera l'objet d'un ADR séparé futur. Cette ADR-026
   ne touche pas le contrat R8 ; elle déplace seulement les fichiers
   `vehicles/*.md` du repo `automecanik-rag` vers `automecanik-content`.

10. **Pas de Frankenstein state — migration atomique en 1 PR par repo**.
    PR `automecanik-rag` (suppression des dossiers migrés + tombstone README)
    et PR `automecanik-content` (import via `git filter-repo`) **mergent
    le même jour**. Les deux PRs référencent cette ADR. Pré-requis avant
    merge des deux : refacto pipeline Python/NestJS (env vars) déjà mergé
    sur `main` du monorepo. Sinon le pipeline casse pendant la fenêtre
    inter-merges.

### Format `automecanik-content`

Squelette de référence livré dans `/tmp/audit/automecanik-content-skeleton/` :

```
automecanik-content/
├── CLAUDE.md                    # pointer vault SoT + scope du repo
├── README.md                    # vue d'ensemble + ingestion contract
├── .gitignore                   # exclus build artifacts, .DS_Store
├── .github/
│   ├── CODEOWNERS               # éditorial team par sous-dossier
│   └── workflows/
│       └── content-lint.yml.placeholder   # JSON Schema + frontmatter lint (futur)
├── docs/
│   ├── architecture.md          # le diagramme 3-couches ci-dessus
│   ├── migration-plan.md        # plan de migration phasée
│   └── ingestion-contract.md    # interface vers Weaviate `dev:full` + R0-R8
├── wiki/
│   ├── gammes/                  # post-migration : 241 .md
│   ├── vehicles/                # post-migration : 83 .md (R8)
│   ├── constructeurs/           # post-migration : 72 .md (R7)
│   ├── guides/                  # post-migration : 16 .md
│   └── reference/               # post-migration : 1 .md
└── _data/                       # post-migration : seo-data CSVs
```

Aucun `.spec/00-canon/` dans `automecanik-content` — le canon vit
uniquement au vault (ADR-015). Aucun script Python (`scripts/seo/rag-*.py`
restent dans monorepo). Aucun fichier de gouvernance (G1).

### Conventions ENV (réutilisation, AP-11)

Aucune nouvelle variable hors les deux ci-dessus :

| Var | Rôle | Défaut |
|---|---|---|
| `AUTOMECANIK_CONTENT_PATH` | Chemin clone `automecanik-content` | `/opt/automecanik/content/` (DEV), `/opt/automecanik/content/` (PROD) |
| `AUTOMECANIK_RAG_PATH` | Chemin clone `automecanik-rag` (existant) | `/opt/automecanik/rag/` |

Pas de `CONTENT_REPO_URL`, `CONTENT_BRANCH`, etc. : les deux clones sont
gérés par les playbooks de provisioning VPS (cf. ADR-012), pas par le code
applicatif.

## Options Considérées

### Option A : Status quo (rejected)

Garder tout dans `automecanik-rag/knowledge/`, ajouter au mieux un
`README.md` clarifiant l'audience par sous-dossier.

**Inconvénients** :
- Ne résout aucun des 5 problèmes du contexte (pollution chatbot, pas
  d'audience séparée, editorial+code mélangés, ADR-022 en tension,
  ADR-029 transitions floues).
- Pattern de bricolage explicitement rejeté par @fafa
  (`feedback_no_hybrid_workarounds.md`).
- Toute amélioration future (CODEOWNERS éditorial, lint frontmatter,
  ingestion Weaviate filtrée) reste empêchée par la frontière manquante.

### Option B : Repo séparé `automecanik-content` (chosen)

Décision @fafa explicite + déjà créé sur GitHub. Cette ADR le ratifie
et cadre la migration.

**Avantages** :
- Sépare audiences (SEO vs support) au niveau repo, ce qui propage
  CODEOWNERS distincts, PR queue distincte, history non polluée par
  299 MB `_raw/`, lint workflows ciblés.
- Cohérent avec ADR-015 (vault déjà repo séparé) et ADR-012
  (governance-vault hors monorepo). Précédent organisationnel valide.
- Permet à `prod:chatbot` Weaviate de cibler `automecanik-rag/knowledge/`
  proprement, sans heuristique de filtrage implicite.
- Permet le refinement bidirectionnel propre : refiner SEO et refiner
  support n'écrivent plus dans le même filesystem.
- Repo éditorial accessible à un futur contributeur SEO/rédactionnel
  sans accès au pipeline Python ni aux 299 MB `_raw/`.

**Inconvénients / coûts** :
- Migration ~450 fichiers cross-repo (`git filter-repo --path` pour
  préserver history).
- Refacto pipeline Python : `find scripts -type f -exec grep -l
  '/opt/automecanik/rag/knowledge/\(gammes\|vehicles\|constructeurs\|guides\|reference\)' {} +`
  → ~10-20 fichiers à éditer (env var substitution).
- ADR-022 paths (couche L2) à amender : section "Mise en œuvre" point 9
  (`weekly-vault-lint scope /rag/knowledge/vehicles/` → désormais
  `/content/wiki/vehicles/`) — 1 commit ADR-022 update.
- ADR-029 paths : la state machine v2.1 sur gammes pointe
  `/opt/automecanik/rag/knowledge/gammes/` → idem, amendement.
- Provisioning VPS : ajouter clone de `ak125/automecanik-content`
  côté DEV + PROD (cf. ADR-012 — playbook à mettre à jour).
- Coordination de merge : PR monorepo refacto env vars → mergée AVANT
  les deux PRs migration (sinon pipeline casse).

### Option C : Reorg in-place tier-prefixed (rejected)

Refactor `automecanik-rag/knowledge/` en `_raw/`, `_refined/`, `_support/`
in-place sans nouveau repo.

**Inconvénients** :
- Ne sépare pas les audiences au niveau repo : éditorial + pipeline
  toujours dans le même PR queue.
- CODEOWNERS toujours unique pour le repo entier.
- `git log` / clone / CI toujours pollués par 299 MB `_raw/`.
- ADR-015 précédent (vault repo séparé) suggère que l'audience-split
  mérite un repo, pas un dossier.
- Décision @fafa explicite **rejette** cette option : "utiliser new repo
  déjà créé automecanik-content" (échange 2026-04-26).

### Option D : Migration vers monorepo `automecanik-app/content/` (rejected)

Bouger les fichiers dans le monorepo NestJS/Remix existant.

**Inconvénients** :
- ADR-015 dit explicitement que la gouvernance + content stratégique
  vivent hors monorepo (vault). Précédent à respecter.
- Mélange code applicatif + contenu éditorial : pire que status quo.
- CI monorepo (build NestJS + Remix) déclenché à chaque modif d'une
  fiche gamme — gaspillage runner GitHub Actions.
- Aucune indépendance d'access pour rédacteurs.

## Conséquences

### Positives

- Frontière explicite par audience (SEO vs support chatbot), propagée
  jusqu'au CODEOWNERS, PR queue, lint workflows.
- Repo `automecanik-content` ratifié dans le ledger canon (G1, G2 ; n'est
  plus orphelin).
- Cohérence ADR-015 (vault SoT) ↔ ADR-026 (content SoT) ↔ `automecanik-rag`
  (raw + support SoT) : 3 repos, 3 audiences, 1 monorepo applicatif.
- ADR-022 (R8) clarifié : la couche L2 "Content repository" pointe
  désormais explicitement `automecanik-content/wiki/vehicles/` au lieu
  d'un sous-dossier ambigu de `automecanik-rag`.
- ADR-029 (RAG v2.1) clarifié : la state machine s'applique aux gammes
  qui vivent dans `automecanik-content/wiki/gammes/` ; les transitions
  écrivent dans le frontmatter du repo content, pas du repo rag.
- Ingestion Weaviate `prod:chatbot` cible `automecanik-rag/knowledge/`
  uniquement → réduction du bruit chatbot.
- Cross-pollination future (refinement secondaire SEO ↔ support) explicite
  et auditable : un script qui lit content et écrit rag passe par 2
  filesystems distincts, traceable.

### Négatives / coûts

- 1 ADR-022 à amender (paths) + 1 ADR-029 à amender (paths) : 2 commits
  ledger.
- ~10-20 fichiers Python/NestJS à refacto (env vars).
- Provisioning VPS DEV + PROD : ajouter clone `automecanik-content`,
  mettre à jour playbook ADR-012.
- Migration ~450 fichiers `git filter-repo` : ~30 min de manipulation
  + revue diff.
- Coordination de merge à 3 PRs (monorepo env vars + automecanik-rag
  suppression + automecanik-content import) — fenêtre de 1 jour
  recommandée.
- Documentation runbook à écrire : `docs/runbooks/content-repo-clone.md`
  (où cloner, branche par défaut, droits SSH).

### Neutres

- Aucun impact frontend Remix : R0-R8 lisent via API NestJS qui lit
  filesystem ; le path change, le contrat applicatif ne change pas.
- Aucun impact DB : pas de migration SQL, pas de table modifiée.
- Aucun impact LLM : refinement reste skills-first / scripts déterministes
  (pas d'introduction LLM par cette ADR).
- Aucun impact sur ADR-027 (R5 → R3 S2) : R5 standalone reste déprécié,
  diagnostic reste sous `automecanik-rag`.

## Mise en œuvre

### Pré-requis

- [ ] Approbation @fafa sur ADR-026.
- [ ] Inventaire des hardcoded paths : `grep -rE
      '/opt/automecanik/rag/knowledge/(gammes|vehicles|constructeurs|guides|reference|seo-data)'
      /opt/automecanik/app /opt/automecanik/rag/scripts` → liste
      exhaustive avant Phase 1.
- [ ] Provisioning VPS DEV + PROD : clone `ak125/automecanik-content`
      sous `/opt/automecanik/content/`, branche `main`, droits user
      `deploy` (cf. ADR-012 playbook à amender).

### Phases (séquentielles, chacune mergée avant la suivante)

| Phase | Périmètre | Livrable | Repo |
|---|---|---|---|
| **P0** — Cadrage | Cette ADR + squelette | ADR-026 mergée vault, squelette pushé `automecanik-content` | governance-vault, automecanik-content |
| **P1** — Refacto env vars | Pipeline Python/NestJS lit `${AUTOMECANIK_CONTENT_PATH}/wiki/...` ; defaults pointent encore l'ancien path tant que migration pas faite | PR monorepo + tests verts | automecanik-app |
| **P2** — Migration atomique | `git filter-repo --path` pour 5 dossiers → import dans `automecanik-content/wiki/` ; suppression côté `automecanik-rag` ; merge même jour | PR `automecanik-rag` + PR `automecanik-content` | les deux |
| **P3** — Amendement ADR-022 + ADR-029 | Paths corrigés dans les deux ADRs ; weekly-vault-lint scope mis à jour (cf. ADR-020) | PR governance-vault | governance-vault |
| **P4** — Ingestion Weaviate (blue-green, zéro downtime) | Voir détail § "P4 detail" ci-dessous : nouvelle classe `prod:chatbot:v2` reindexée en arrière-plan, switch atomique, drop v1 après J+7 stable | PR config Weaviate + endpoint admin | automecanik-app (config) |
| **P5** — Cleanup | `automecanik-rag/knowledge/faq` ↔ `faqs/` dédupliqués ; tombstone README dans `automecanik-rag/knowledge/{gammes,vehicles,...}/.MOVED.md` pointant `automecanik-content` | PRs ciblées | automecanik-rag |
| **P6** — Runbook + provisioning canon | `docs/runbooks/content-repo-clone.md` ; ADR-012 playbook amendé | PRs vault + monorepo | governance-vault, automecanik-app |

### Validation

- **P1** : `npm test` + `python -m pytest scripts/seo/` verts ; smoke test
  `auto-enrich-r4-rag.py --mode audit_only` lit bien les deux paths.
- **P2** : `git log --follow automecanik-content/wiki/gammes/freinage.md`
  préserve l'history pré-migration ; `automecanik-rag/knowledge/gammes/`
  vide ; pipeline ne casse pas (deploy DEV puis vérification logs
  `r3-keyword-planner`).
- **P3** : weekly-vault-lint cron Monday 02:00 UTC s'exécute sans erreur
  sur les nouveaux paths.
- **P4** : `prod:chatbot:v2` doc count = baseline
  `automecanik-rag/knowledge/` (~450 docs en moins vs v1 = gammes +
  vehicles + constructeurs + guides + reference exclus). Smoke tests
  sur 20 questions chatbot représentatives : delta qualité v1 vs v2
  ≤ 5%. Switch atomique exécuté sans interruption de service. v1 dropé
  J+7 après stabilité confirmée.
- **P5** : `find automecanik-rag/knowledge -name '.MOVED.md' | wc -l`
  retourne le nombre de dossiers migrés.

### P4 detail — Stratégie blue-green Weaviate (zéro downtime)

Reindex `prod:chatbot` post-migration peut prendre 1-2 h sur le volume
actuel. Pour éviter toute interruption chatbot, blue-green strict :

1. **P4.1 (blue stable)** — `prod:chatbot:v1` continue de servir les
   requêtes (état actuel post-migration disque, mais index pas encore
   reindexé : contient encore les fragments gammes/vehicles/etc. comme
   avant — dégradation acceptable temporaire car même contenu logique
   pendant la fenêtre).
2. **P4.2 (green build)** — Créer nouvelle classe Weaviate
   `prod:chatbot:v2` avec scope filtré uniquement sur
   `automecanik-rag/knowledge/`. Reindex complet en arrière-plan,
   sans toucher v1.
3. **P4.3 (validation green)** — Smoke tests sur v2 : panel de 20
   questions chatbot représentatives, comparaison réponses v1 vs v2.
   Si baisse qualité > 5%, investiguer avant switch.
4. **P4.4 (atomic switch)** — Endpoint admin
   `POST /api/chatbot/index/promote-v2` bascule le pointeur de runtime
   chatbot de `v1` vers `v2`. Rollback immédiat possible
   (re-bascule v1 en 1 commande).
5. **P4.5 (cleanup blue)** — Après 7j de stabilité v2 confirmée, drop
   classe `prod:chatbot:v1`. Espace disque récupéré.

`dev:full` (audience interne) suit le même pattern blue-green ou simple
drop+recreate (downtime acceptable côté dev). Lit les deux repos
post-switch (`automecanik-rag/knowledge/` + `automecanik-content/wiki/`).

### Rollback

- **P1** : revert PR env vars → defaults reprennent l'ancien path
  (path inchangé tant que P2 pas mergé).
- **P2** : revert atomique des deux PRs (monorepo + automecanik-rag)
  re-importe le contenu et rétablit le filesystem. Fenêtre 7 jours.
  Au-delà : `git filter-repo --reverse` ou rollback manuel par diff.
- **P3-P6** : revert PR ledger / config / runbook unitaires ; pas de
  dépendance entre.

Plan d'urgence si pipeline casse en P2 :
1. `AUTOMECANIK_CONTENT_PATH=/opt/automecanik/rag/knowledge` (override
   env var pour pointer vers ancienne arbo si rollback partiel).
2. Symlink temporaire `/opt/automecanik/content/wiki/gammes ->
   /opt/automecanik/rag/knowledge/gammes` (uniquement si revert P2
   impossible immédiatement).
3. Communication équipe + ouverture incident `INC-2026-XXX`.

### Suivi (post-merge P2)

| Métrique | Cible J+7 | Source |
|---|---|---|
| PRs migration mergées le même jour | 2 PRs (rag + content) | GitHub timeline |
| `git log --oneline automecanik-content/wiki/gammes/` | ≥ 1 commit pré-migration visible (history préservé) | git |
| Pipeline `auto-enrich-r4-rag.py` weekly cron | runs verts × 1 (premier weekend post-merge) | logs |
| Weaviate `prod:chatbot` doc count | baisse de ~450 docs (gammes + vehicles + constructeurs + guides + reference exclus) | Weaviate API |
| Monorepo CI | tests verts sur `main` post-P1 et P2 | GitHub Actions |

## Conformité règles vault

- **G1 (Canon fait foi)** : ADR-026 mergée AVANT exécution P1-P6 ; rien
  n'est exécuté hors canon.
- **G2 (Zéro orphelin)** : `automecanik-content` désormais référencé
  dans le ledger ; weekly-vault-lint à étendre pour valider ce repo
  (extension ADR-020 hors scope, à prévoir en P6).
- **G3 (Signed commits)** : tous les commits ADR + amendements ADR-022/029
  signés GPG.
- **G5 (`.spec/00-canon/` autoritatifs)** : aucun fichier `.spec/00-canon/`
  ne pointe `gammes/` actuellement (vérifier `grep -rE
  'rag/knowledge/(gammes|vehicles|constructeurs)' .spec/00-canon/`) ;
  si oui, amender en P3.
- **AP-10 (services <500 lignes)** : aucun service modifié, juste env
  vars + paths.
- **AP-11 (verify existing first)** : structure inspectée (22 dossiers
  cartographiés § Contexte), 4 ADRs adjacentes lues (022/025/027/029)
  pour cohérence, pattern `governance-vault` repo séparé identifié
  comme précédent.

## Notes

- Memory Claude Code consultées : `feedback_no_hybrid_workarounds`,
  `feedback_branch_scope_discipline`, `vault-sot-adr013`,
  `feedback_verify_existing_first`, `feedback_rag_vault_always_first`.
- R8 rotation conservée par décision @fafa explicite — amélioration de
  la diversité (au-delà du fingerprint gate ADR-022) reportée à un ADR
  futur dédié.
- Cross-pollination refinement bidirectionnel (content → rag pour
  meilleure couverture support, rag → content pour gaps SEO) reconnue
  dans le diagramme architectural mais sans implémentation prescrite —
  fera l'objet d'ADRs dédiées par axe (SEO refiner, support refiner)
  au fur et à mesure des chantiers.
- Cette ADR est une **décision de structure**, pas une **décision de
  contenu**. Elle ne dicte pas le format des fichiers `.md`, ni le
  schema YAML frontmatter, ni les conventions éditoriales — ces
  contrats sont déjà gérés par ADR-022 (R8), ADR-029 (gammes v2.1),
  et le canon `.spec/00-canon/gamme-md-schema.md`.

## Références

- [[ADR-012-aicos-vps-architecture]] — VPS architecture 3-tiers
  (DEV/PROD/AI-COS) + provisioning playbook
- [[ADR-015-vault-single-source-of-truth]] — précédent repo séparé du
  monorepo (gouvernance), même pattern réutilisé ici (content)
- [[ADR-022-r8-rag-control-plane]] — paths `/rag/knowledge/vehicles/`
  à amender en P3
- [[ADR-025-seo-department-architecture]] — consomme `automecanik-content`
  en aval (services SEO `seo-monitoring`/`seo-content-ops`)
- [[ADR-027-r5-consolidation-into-r3-s2-diag]] — diagnostic reste sous
  `automecanik-rag` (R5 standalone déprécié)
- [[ADR-029-rag-v2.1-control-plane-closure]] — paths
  `/opt/automecanik/rag/knowledge/gammes/` à amender en P3
- [[MOC-Decisions]] — index ADR (cette ADR-026 référencée)
- Mémoire `rag-enrichment-pipeline.md` — historique scripts pipeline
  qui touchent `gammes/` / `vehicles/`
- `feedback_no_hybrid_workarounds.md` — pas de "pragmatique en attendant"
- Squelette repo : `/tmp/audit/automecanik-content-skeleton/` (livré
  avec cette ADR pour copie dans `ak125/automecanik-content` après
  approbation)

---

_Draft livré 2026-04-26 par Claude Code Opus 4.7 (1M context) dans
scratchpad `/tmp/audit/`. Ne sera ni pushé sur governance-vault ni
copié dans `ak125/automecanik-content` par cet agent — handoff Cowork._
