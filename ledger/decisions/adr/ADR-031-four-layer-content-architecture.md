---
id: ADR-031
title: "Four-Layer Content Architecture — Raw / Wiki / Exports / Consumers (Unified Flow All R0-R8)"
status: proposed
date: 2026-04-28
decision_date: null
decision_makers: ["@fafa"]
supersedes: ["ADR-022", "ADR-026"]
superseded_by: []
amends: ["ADR-029"]
related_rules: ["G1", "G2", "G3", "G5", "AP-10", "AP-11"]
related_incidents: []
related_adr: ["ADR-012", "ADR-013", "ADR-015", "ADR-022", "ADR-026", "ADR-027", "ADR-029"]
reviewed_by: null
---

# ADR-031: Four-Layer Content Architecture — Raw / Wiki / Exports / Consumers

## Contexte

Au 2026-04-28, l'architecture documentaire AutoMecanik souffre de trois incohérences structurelles incompatibles avec le principe utilisateur non-négociable **« tout brut → raw, tout validé → wiki, aucune exception »** :

### Incohérence 1 — Carve-out diagnostic/faq/policies

ADR-026 (proposed) prévoyait de laisser `automecanik-rag/knowledge/{diagnostic,faq,faqs,policies}/` (30 fichiers, 128 KB) sous `automecanik-rag/knowledge/` "tant qu'ADR-031 ne définit pas leur migration", au motif de préserver le chatbot existant.

Investigation empirique (Explore agent 2026-04-28) :

- Aucune ingestion Weaviate active sur ces 3 dossiers (`grep -r "prod:chatbot"` dans scripts actifs → 0 hit)
- `index-md-to-weaviate.py` est un **script archive** dormant
- 1 seul service backend lit `diagnostic/` (`backend/src/modules/seo/validation/diagnostic.service.ts`) — coût migration = 1 fichier env var
- `faq/` + `policies/` = pas de hardcoded path backend

**Verdict** : aucune justification technique au "rester séparé". Le carve-out était une projection prudente, pas une contrainte.

### Incohérence 2 — R8 cas spécial ADR-022 (`__rag_proposals`)

ADR-022 (accepted, signée @fafa 2026-04-25) introduit la table `__rag_proposals` comme gate "propose-before-write" pour R8 (vehicles motorisations), avec rollout en 8 stages.

Investigation empirique 2026-04-28 (3 jours après acceptation) :

| Élément ADR-022 | État réel |
|---|---|
| Table `__rag_proposals` | Créée (migration `20260424_create_rag_proposals.sql`, 188 lignes) |
| `RAG_PROPOSAL_MODE` flag | Existe mais **`off` par défaut** |
| `VehicleRagGeneratorService` | Écrit **directement filesystem** via `writeFileSync` ligne 190 (mode `off`) |
| Endpoints `POST /api/admin/r8/:typeId/publish` | **Non livrés** (grep codebase : 0 hit) |
| Schémas JSON `vehicle-{model,variations,role-map}.schema.json` | **Non migrés** dans vault (ADR-022 §10 mentionne `governance-vault/_scripts/schemas/` — vide) |
| Stages 1-8 rollout | **Stage 0 dormant** (aucun stage activé) |
| Test coverage | 1 ligne de test (2026-04-25) |

**Verdict** : ADR-022 design intent valide, mais en pratique R8 **écrit aujourd'hui exactement comme R3/R4/R6/R7** (filesystem direct). Le mécanisme `__rag_proposals` est code mort. L'asymétrie R8 vs autres R existe uniquement sur papier.

### Incohérence 3 — `automecanik-raw` repo "vide"

ADR-026 §"Phase 3" prévoyait que `automecanik-raw` reste un cadre vide à la phase de cadrage, sans migration physique. Cette position était déjà incohérente avec le principe directeur.

Investigation empirique 2026-04-28 :

| Zone | Volume | Activité |
|---|---|---|
| `/opt/automecanik/rag/knowledge/_raw/` | 299 MB (1 PDF 113 MB) | Sources brutes scrapées |
| `/opt/automecanik/rag/knowledge/web/` | 13 MB / 1771 fichiers | Scrape HTML chunké |
| `/opt/automecanik/rag/knowledge/web-catalog/` | 804 KB / 182 fichiers | Catalogue scraping |
| `/opt/automecanik/rag/knowledge/web-vehicles/` | 244 KB / 12 fichiers | Vehicles scraping |
| **Total** | **313 MB / 3767 fichiers** | **Activement consommé** par `rag-enrich-from-web-corpus.py` |

**Verdict** : raw n'est **pas vide**, c'est éparpillé entre `automecanik-rag/_raw/` et sous-dossiers `web*/`. Maintenir le statu quo signifie laisser le repo `automecanik-raw` décoratif. Le principe directeur impose la migration physique.

---

## Principe directeur (formulation utilisateur figée)

> Toute donnée non validée, générée, importée, recyclée, scrapée ou issue d'un pipeline est considérée brute par défaut et doit résider dans `automecanik-raw`.
>
> Toute connaissance métier exposée dans `automecanik-wiki` doit être sourcée, structurée, lintée et validée humainement.
>
> Aucun consommateur — RAG, SEO, blog, chatbot, outil diagnostic — ne lit directement `automecanik-raw` pour produire une sortie publique.
>
> Les consommateurs lisent uniquement les exports contrôlés du wiki ou les bases métier explicitement conservées comme sources de vérité techniques.

Ce principe est **non-négociable**. Toutes les décisions ci-dessous découlent de son application stricte.

---

## Décision

Adopter une **architecture documentaire à 4 couches** — `automecanik-raw` → `automecanik-wiki` → exports → consommateurs — avec **flux unifié pour toutes les R (R0-R8)** et **migration physique planifiée** des 313 MB de contenu brut existant.

> **Note sur le nommage** : le dépôt initialement nommé `automecanik-content` (créé 2026-04-26 hors ledger, puis renommé en cours de Phase 1+3) est maintenant `automecanik-wiki`. Le nom `automecanik-content` est **réservé**, le cas échéant plus tard, à un dépôt de **contenus éditoriaux produits depuis le wiki** (briefs, articles, FAQ enrichies, guides), et **non** à la base de connaissance canonique. Cette précision évite toute confusion lors d'une relecture d'ADR-026.

### Architecture cible

```
Sources brutes
  ├── _raw/, web/, web-catalog/, web-vehicles/ (313 MB)
  ├── CSV bruts Google Ads / GSC / OEM corpus
  ├── automecanik-rag/knowledge/{8 catégories} (existantes — brutes par défaut)
  ├── monorepo : datasets / fixtures / golden sets / CSV (recyclables après inventaire)
  └── monorepo logique applicative (PAS une source raw)
       ↓
automecanik-raw/  (Git normal pour texte stable, Git LFS ou storage externe pour binaires/gros fichiers — D16)
  ├── sources/         nouvelles sources brutes par origine
  ├── recycled/        rag-knowledge/, monorepo-fixtures/, r8-generation/
  ├── normalized/      sources nettoyées/mappées
  ├── quarantine/      en attente de décision (audit 30j)
  └── manifests/       DuckDB inventories + tombstones.json
       ↓ validation humaine + sourcing + lint
automecanik-wiki/  (5 entity_types : gamme | vehicle | constructeur | support | diagnostic)
  ├── proposals/       FLAT + _index.md + _manifest.json
  ├── wiki/<entity_type>/  (singulier figé)
  └── exports/{rag,seo,support}/  contrats schema pour consommateurs
       ↓ env vars AUTOMECANIK_WIKI_PATH / AUTOMECANIK_RAW_PATH (lecture seule)
Consommateurs (jamais d'écriture)
  ├── RAG chatbot       (Weaviate ingéré depuis wiki/exports/rag/)
  ├── SEO R0-R8         (lit wiki/exports/seo/, traitement uniforme)
  ├── Blog              (table __blog_* monorepo, peut citer wiki)
  ├── Support chatbot   (lit wiki/exports/support/)
  └── Outil diagnostic  (lit wiki/diagnostic/ + DB __diag_* logique métier)
```

### Couche 0 — Sources brutes (existantes ou futures)

Définition : toute donnée non validée, générée, scrapée, importée ou issue d'un pipeline.

Sources connues à 2026-04-28 :

| Source | Localisation actuelle | Migration cible |
|---|---|---|
| Binaires bruts (PDF, images, evidence) | `/opt/automecanik/rag/knowledge/_raw/` (299 MB) | `automecanik-raw/sources/` (Phase C) |
| Scrapes web HTML | `/opt/automecanik/rag/knowledge/{web,web-catalog,web-vehicles}/` (14 MB) | `automecanik-raw/sources/web-corpus/` (Phase C) |
| Fiches RAG brutes recyclables | `/opt/automecanik/rag/knowledge/{8 catégories}/` | `automecanik-raw/recycled/rag-knowledge/<cat>/` (Phase F-G-H prep) |
| CSV bruts Google Ads / GSC | Téléchargements ad hoc | `automecanik-raw/sources/csv-google-ads/` (toujours intacts) |
| CSV nettoyés / normalisés | Ad hoc | `automecanik-raw/normalized/csv-google-ads/` |
| Datasets / fixtures monorepo | `/opt/automecanik/app/scripts/...` | `automecanik-raw/recycled/monorepo-fixtures/` (après inventaire) |

**Le monorepo n'est pas une source raw par nature**, mais les datasets, fixtures, CSV, golden sets ou anciens outputs présents PEUVENT être recyclés après inventaire explicite.

### Couche 1 — `automecanik-wiki` (connaissance canonique)

5 entity_types figés par schema v1.0 (déjà mergé dans `ak125/automecanik-wiki/_meta/schema/`) :

- `gamme` — fiches catégories de pièces (R3/R4/R6 consommateurs)
- `vehicle` — fiches motorisations (R8 consommateur — pas d'exception au flux)
- `constructeur` — hubs marques (R7 consommateur)
- `support` — fiches client (chatbot consommateur, regroupe faq/policies/guides/reference)
- `diagnostic` — fiches symptômes (outil diagnostic auto + R3 S2_DIAG)

**Convention de chemin figée** : `wiki/<entity_type_singular>/` (relatif au repo) ou `/opt/automecanik-wiki/wiki/<entity_type_singular>/` (full path). Pas de variantes pluriel (`wiki/gammes/` interdit). La redondance `automecanik-wiki/wiki/` est cosmétique acceptée — schema v1.0 ancre cette structure.

**proposals/ FLAT + index obligatoire** :
- `proposals/_index.md` humanly readable
- `proposals/_manifest.json` machine readable (schema strict)

### Couche 2 — `wiki/exports/{rag,seo,support}/` (contrats consommateurs)

Générés depuis `wiki/<entity_type>/` par scripts dédiés, avec lint + schema validation. Aucun consommateur ne lit `wiki/<entity_type>/` directement — uniquement `wiki/exports/<audience>/`.

### Couche 3 — Consommateurs (lecture seule)

| Consommateur | Source de lecture | Rôle |
|---|---|---|
| RAG chatbot | `wiki/exports/rag/` (via `scripts/rag/sync-from-wiki.py` → `automecanik-rag/knowledge/`) | Réponses chatbot Weaviate |
| SEO R0-R8 | `wiki/exports/seo/` (uniforme tous les R, pas d'exception R8) | Génération pages publiques. **`wiki/exports/seo/` fournit la matière validée — intentions, angles, données structurées, sourcing — ; la logique SEO R0-R8 (génération, classification, V-Level, rotation, publish gates) reste dans `nestjs-remix-monorepo`. Le wiki n'est pas un moteur SEO.** |
| Blog | Table `__blog_*` monorepo (consommateur secondaire wiki via lien) | Articles éditoriaux |
| Support chatbot | `wiki/exports/support/` | Réponses client (faq, policies) |
| Outil diagnostic auto | `wiki/diagnostic/` + DB `__diag_*` (logique métier) | Diagnostic symptôme/cause |

**Règle stricte sync-from-wiki** : le script lit **uniquement** `wiki/exports/rag/`. Lire `wiki/<entity_type>/` directement est INTERDIT (garde-fou pre-commit hook monorepo). Justification : `wiki/<entity_type>/` peut contenir notes internes, sections legacy, draft fields qui ne sont pas filtrés pour ingestion RAG.

**`automecanik-rag/knowledge/` post-Phase F devient répertoire généré** :
- Modification manuelle interdite sauf rollback documenté
- README banner explicite
- Pre-commit hook `automecanik-rag` refuse les commits manuels touchant `knowledge/<5 catégories métier>` sans label `rollback-documented`

---

## Héritage ADR-022

ADR-022 (accepted 2026-04-25 par @fafa) a posé un design intent valide pour résoudre le problème "R7 pas contrôlé" : **propose-before-write**, **5 gates de validation L0-L5**, **schémas JSON canon**, **rotation déterministe**, **idempotence par fingerprint**.

Ces principes restent **valides et désirables**, et sont **intégrés au design plus large d'ADR-031, généralisés à tous les R via le flux raw → wiki**, plutôt que limités à R8 :

- **Propose-before-write** → généralisation : les sorties de générateur (R3/R4/R6/R7/R8) écrivent dans `automecanik-raw/recycled/<r-source>/` ; la promotion vers `automecanik-wiki/` requiert validation humaine explicite (Phase E pilote, puis Phase F-G-H batch). Le concept "proposal" n'est plus DB-based : il vit dans `automecanik-wiki/proposals/` (FLAT + manifest).
- **Gates L0-L5** → intégrés dans la chaîne raw → wiki : L0 (source contract via schema v1.0 frontmatter), L1 (proposals manifest review), L2 (commit signed G3 dans wiki), L3 (lint exports/rag/ + check-quality-gate), L4 (publish via PR mergée), L5 (observability via systemd timer + tombstones).
- **Schémas R8** (`vehicle-model.schema.json`, `vehicle-variations.schema.json`, `vehicle-role-map.schema.json`) → **archivés dans `automecanik-wiki/_meta/schema/legacy/adr-022/`** (pas supprimés). Le schéma `vehicle.schema.json` v1.0 (déjà mergé dans wiki) couvre les champs équivalents pour le runtime ; les schémas legacy documentent l'intention historique et peuvent informer une fusion future.
- **Idempotence par fingerprint** → couvert par `lineage_id` UUIDv7 + `content_hash` SHA-256 body-only (D8 du plan).
- **Rotation déterministe TemplateRotator** → conservée par décision @fafa (cf. ADR-026 §9), s'applique en raw → wiki via la phase de génération avant validation.

**Conséquence opérationnelle** :

- Phase I (J0) : table `__rag_proposals` deprecated **in-place** (trigger `BEFORE INSERT OR UPDATE` raise EXCEPTION — bloque toute nouvelle écriture **et** toute modification de lignes existantes ; comment SQL deprecated ; retirer écritures applicatives ; retirer flag `RAG_PROPOSAL_MODE`). **Pas de rename**, pas de drop. Observation 30j (`pg_stat_user_tables` + grep codebase + logs).
- Phase J (J+30+) : si preuves d'inutilisation (seq_scan + idx_scan = 0 sur 30j, 0 hit grep, 0 error log), **rename `__rag_proposals_deprecated` OU drop**. Tombstone documenté dans `automecanik-raw/manifests/tombstones.json`. Suppression complète `rag-proposal.service.ts`.

ADR-022 status devient `superseded`, `superseded_by: [ADR-031]`. Son contenu reste lisible comme audit trail historique.

---

## Compatibilité ADR-027

ADR-027 (accepted) déprécie les **URLs publiques R5** (sub-pages 301 vers R3 S2), pas le **contenu éditorial diagnostic**.

Migrer `automecanik-rag/knowledge/diagnostic/*.md` vers `automecanik-wiki/wiki/diagnostic/` est **orthogonal** à ADR-027 :

- R3 S2_DIAG continue de consommer ces fiches via RPC DB `get_observable_symptoms_for_gamme` (lu par `backend/src/modules/seo/services/conseil-enricher.service.ts`)
- Le RPC ne lit pas filesystem, donc le déplacement physique n'impacte pas R3 S2
- Phase H peut s'exécuter sans modifier ADR-027

---

## Plan d'exécution — Phases A-J

| # | Phase | Repo | Livrable | Bloque |
|---|---|---|---|---|
| 1 | **Phase A** — Gouvernance ADR-031 | governance-vault | 3 PRs : PR-A (cette ADR + supersede ADR-022/026), PR-B (amend ADR-029 v2.1.1 paths), PR-C (addendum runbook) | Phases B-J |
| 2 | **Phase B** — Inventaire raw physique | automecanik-raw | `manifests/raw-inventory-2026-04.json` | Phase C |
| 3 | **Phase C** — Migration raw physique | monorepo + automecanik-raw | Migration selon manifest, décisions documentées | Phase D partielle |
| 4 | **Phase D** — Refacto scripts raw path | monorepo | 2 scripts env var `AUTOMECANIK_RAW_PATH` + safe fallback | rien |
| 5 | **Phase E** — Pilote wiki | wiki | 4 propositions (gamme + vehicle + constructeur + support) | Phase F batch |
| 6 | **Phase F** — Migration métier | wiki + monorepo + automecanik-rag | Batch 5 catégories, création `sync-from-wiki.py` (D20), README banner generated dir (D22), pre-commit hook automecanik-rag | Phase G |
| 7 | **Phase G** — Support | wiki | Batch faq + policies + dédup faqs | Phase H |
| 8 | **Phase H** — Diagnostic | wiki + monorepo | Migration diagnostic, refacto `diagnostic.service.ts` | Phase I |
| 9 | **Phase I** — Deprecate `__rag_proposals` (in-place, J0) | monorepo | Trigger BEFORE INSERT, retirer flag, simplifier `VehicleRagGeneratorService`. Observer 30j | Phase J (J+30) |
| 10 | **Phase J** — Cleanup final (J+30+) | monorepo | Si 0 usage : rename `__rag_proposals_deprecated` OU drop. Tombstone | rien |

### Décisions clés (D14-D22) intégrées

- **D14** : Supersede TOTAL ADR-022 (pas partial). Phase I deprecate IN-PLACE → Phase J rename ou drop si 0 usage.
- **D15** : 8 catégories migrent vers wiki (gammes/vehicles/constructeurs/guides/reference/faq/policies/diagnostic), pas 5.
- **D16** : Inventaire taille obligatoire avant migration physique. Décision file-by-file selon taille ET nature : `< 10 MB texte stable` Git normal, sinon LFS ; `> 100 MB` décision explicite.
- **D17** : ADR-027 non bloquant pour migration diagnostic (URLs vs contenu éditorial sont orthogonaux).
- **D17b** : Schémas ADR-022 archivés dans `wiki/_meta/schema/legacy/adr-022/` (pas supprimés).
- **D18** : KW pipeline préservé (DB SoT) ; CSV bruts dans `sources/csv-google-ads/`, normalisés dans `normalized/csv-google-ads/` ; monorepo datasets recyclables après inventaire.
- **D19** : `proposals/` FLAT + `_index.md` + `_manifest.json` obligatoire.
- **D20** : `sync-from-wiki.py` lit `wiki/exports/rag/` UNIQUEMENT, jamais `wiki/<entity_type>/`. Pre-commit hook garde-fou.
- **D21** : Aucune suppression silencieuse. Tombstone documenté dans `automecanik-raw/manifests/tombstones.json` obligatoire.
- **D22** : `automecanik-rag/knowledge/` devient répertoire généré post-Phase F, modification manuelle interdite sauf rollback documenté.

---

## Options Considérées

### Option A — Maintenir ADR-026 + carve-out diagnostic/faq/policies + ADR-022 dormant (rejetée)

Statu quo plan précédent.

**Inconvénients** :
- 3 incohérences identifiées non résolues
- Repo `automecanik-raw` reste décoratif
- R8 reste cas spécial sur papier
- `__rag_proposals` reste code mort sans trajectoire

### Option B — ADR-031 unifié, supersede TOTAL ADR-022 + ADR-026, migration physique planifiée (chosen)

Architecture cohérente, principe directeur appliqué strictement.

**Avantages** :
- Résout les 3 incohérences à la racine
- 1 flux unifié pour toutes les R (pas d'asymétrie)
- `automecanik-raw` devient repo réel avec contenu migré
- Phase I deprecate-in-place protège contre régressions par lectures résiduelles
- Tombstones documentent toute suppression (G2 zero orphelin)
- Pre-commit hooks (sync-from-wiki + automecanik-rag manual edit) garde-fous structurels

**Inconvénients** :
- Migration physique 313 MB nécessite Git LFS (1 PDF 113 MB peut nécessiter storage externe)
- Refacto 2 scripts Python (env var safe fallback)
- Phase F-G-H batch de 8 catégories sur plusieurs jours
- Coordination 3 PRs vault + cross-repos

### Option C — Partial supersede ADR-022 (garder schémas, dropper table, R8 special case persistant) (rejetée)

Compromis intermédiaire qui aurait gardé `__rag_proposals` comme implementation detail backend.

**Inconvénients** :
- Viole le principe utilisateur "tous les R sont pareils"
- Conserve une asymétrie injustifiée par evidence empirique
- Maintient code mort sans trajectoire de cleanup
- "Hybrid workaround" explicitement rejeté par `feedback_no_hybrid_workarounds.md`

---

## Conséquences

### Positives

- Architecture cohérente avec le principe directeur sans exception
- 4/4 copies AEC déjà alignées par hash (Phase B.3 + monorepo PR #204) — fondation gouvernance solide
- Pipeline KW canon (`__seo_keywords`) préservé comme DB SoT
- Outil diagnostic auto continue de fonctionner (RPC DB inchangé, fichiers diagnostic déplacés sans impact)
- R8 traité uniformément avec R3/R4/R6/R7
- `automecanik-raw` devient repo réel et exploitable, pas décoratif
- Tombstones tracent toute suppression (G2 conformité)
- `automecanik-rag/knowledge/` devient répertoire généré stable, élimine drift wiki ↔ rag

### Négatives / Coûts

- 3 PRs vault Phase A + N PRs cross-repos (B-J)
- Migration physique 313 MB avec inventaire size-aware (1-2 jours Phase B+C)
- Refacto 2 scripts Python (Phase D, env var safe fallback)
- Phase F-G-H batch 8 catégories sur plusieurs jours selon volume gammes (1655 cible)
- Période 30j observation entre Phase I et Phase J (volontaire, defense-in-depth)
- Coordination merge ADR-029 amend (PR-B) avec début Phase F (paths cohérents)

### Neutres

- Frontend Remix R0-R8 inchangé (lit via API NestJS qui lit filesystem ou DB ; le path change, le contrat applicatif ne change pas)
- DB `__seo_*`, `__diag_*`, `__blog_*` inchangées
- Schemas wiki v1.0 inchangés (déjà mergés)
- Canon AEC inchangé

---

## Conformité règles vault

- **G1 (Canon fait foi)** : ADR-031 mergée AVANT exécution Phase B-J. Rien n'est exécuté hors canon.
- **G2 (Zéro orphelin)** : tombstones obligatoires (D21), pre-commit hooks raw + rag, repo `automecanik-raw` ratifié dans le ledger.
- **G3 (Signed commits)** : tous les commits ADR + amendements signés via clé `vault-signing@automecanik.com`.
- **G4 (CI read-only sur canon)** : workflows existants `vault-governance.yml`, `vault-weekly-lint.yml`, `canon-publish.yml` inchangés.
- **G5 (`.spec/00-canon/` autoritatifs)** : ADR-031 référencée par `MOC-Decisions` après merge.
- **AP-10 (services <500 lignes)** : `vehicle-rag-generator.service.ts` simplifié en Phase I (réduction de complexité).
- **AP-11 (verify existing first)** : 3 agents Explore parallèles 2026-04-28 ont vérifié empiriquement les 3 incohérences avant proposition.

---

## Mise en œuvre

### Pré-requis (Phase A)

- [ ] Approbation @fafa sur ADR-031
- [ ] Merge sequentielle PR-A → PR-B → PR-C (vault) avec drift check canon-hashes vert
- [ ] Tag `pre-adr-031` sur main monorepo + vault (référence rollback)

### Validation par phase

Chaque phase a ses commandes de vérification documentées dans le plan d'exécution `/home/deploy/.claude/plans/verifier-diagnostic-faq-policies-declarative-rain.md`. Critères de "PASS" :

- **Phase A** : 3 PRs vault mergées, drift check vert, supersede metadata présente sur ADR-022/026
- **Phase B** : manifest exhaustif avec décision par fichier
- **Phase C** : migration byte-identity (sha256 baseline = sha256 migré, sauf exclusions documentées)
- **Phase D** : scripts fonctionnent avec et sans env var (default fallback safe)
- **Phase E** : 4 propositions valident schema, pas de collision slug
- **Phase F** : sync-from-wiki garde-fou D20 testé, pre-commit D22 testé, comptages post-migration cohérents
- **Phase G + H** : pipelines consommateurs non régressés (smoke tests R3, outil diag)
- **Phase I** : trigger INSERT bloquant testé, flag retiré, observation 30j amorcée
- **Phase J** : 0 usage 30j confirmé avant rename/drop

### Rollback

Plan de rollback détaillé par phase dans `/home/deploy/.claude/plans/verifier-diagnostic-faq-policies-declarative-rain.md` §"Risques + rollback". Points clés :

- Phase A : revert PRs vault unitaires, ADR-022/026 reprennent leur status précédent
- Phase C : sha256 baseline permet rollback byte-identity
- Phase D : default fallback env var = no-break by design
- Phase F-H : symlink temporaire diagnostic/wiki en cas de régression cron
- Phase I : table conservée sous son nom d'origine, lectures résiduelles continuent de fonctionner (table peut contenir des lignes historiques) ; seules les nouvelles écritures sont bloquées par trigger
- Phase J : tombstone documenté permet rollback via git revert

---

## Notes

- Memory Claude Code consultées : `feedback_no_hybrid_workarounds`, `feedback_branch_scope_discipline`, `vault-sot-adr013`, `feedback_verify_existing_first`, `feedback_rag_vault_always_first`, `feedback_r8_is_vehicle_not_gamme`, `wiki-raw-architecture-handoff`, `signing-config-gotcha`.
- Plan d'exécution complet : `/home/deploy/.claude/plans/verifier-diagnostic-faq-policies-declarative-rain.md`.
- 3 agents Explore parallèles ont vérifié empiriquement les 3 incohérences avant rédaction (rapports archivés dans transcript de session 2026-04-28).
- Décisions D1-D13 figées au 2026-04-28 (multi-agent review) restent valides ; D14-D22 ajoutées par cette ADR pour résoudre les 3 incohérences flaguées par @fafa post-handoff.
- Phase B.3 (canon AEC + canon-hashes.json + workflows hash-check) déjà fermée 4/4 copies sur tous les repos consommateurs avant rédaction d'ADR-031.

---

## Références

- [[ADR-012-aicos-vps-architecture]] — VPS architecture 3-tiers
- [[ADR-015-vault-single-source-of-truth]] — précédent repo séparé + canonical path /opt/automecanik/governance-vault/
- [[ADR-022-r8-rag-control-plane]] — superseded par cette ADR (héritage intégré)
- [[ADR-026-content-separation]] — superseded par cette ADR (4 layers vs 3)
- [[ADR-027-r5-consolidation-into-r3-s2-diag]] — non bloquant pour migration diagnostic
- [[ADR-029-rag-v2.1-control-plane-closure]] — amendée v2.1.1 (paths only) par PR-B
- [[MOC-Decisions]] — index ADR (cette ADR-031 référencée post-merge)
- `rules-agent-exit-contract.md` (canon) — distribution AEC déjà fermée 4/4 copies
- Plan d'exécution : `/home/deploy/.claude/plans/verifier-diagnostic-faq-policies-declarative-rain.md`
