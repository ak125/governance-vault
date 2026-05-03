---
type: knowledge
status: active
date: 2026-04-28
related_adr: ["ADR-031"]
related_rules: ["G1", "G2", "G3", "AP-11"]
audience: ["@fafa", "claude-code", "cowork"]
---

# Runbook ADR-031 — Migration 4 couches (raw / wiki / exports / consommateurs)

> Plan d'exécution opérationnel pour les Phases B-J d'[[ADR-031-four-layer-content-architecture]] (acceptée 2026-04-28). Plan complet : `/home/deploy/.claude/plans/verifier-diagnostic-faq-policies-declarative-rain.md`.

## Phases A-J — vue synthétique

| Phase | Repo | Coût estimé | Critère de PASS | Bloque |
|---|---|---|---|---|
| **A.PR-A** ✅ | governance-vault | 1h | ADR-031 mergée, ADR-022/026 superseded | B-J |
| **A.PR-B** ✅ | governance-vault | 30 min | ADR-029 v2.1.1 paths-only mergée | F gamme |
| **A.PR-C** (cette PR) | governance-vault | 30 min | Runbook + tombstones schema mergés | rien |
| **B** Inventaire raw | automecanik-raw | 2-3h | `manifests/raw-inventory-2026-04.json` exhaustif | C |
| **C** Migration raw physique | monorepo + automecanik-raw | 1 jour | sha256 byte-identity (sauf exclusions documentées) | D partielle |
| **D** Refacto scripts raw | monorepo | 1-2h | env var `AUTOMECANIK_RAW_PATH` + safe fallback testé | rien |
| **E** Pilote wiki | wiki | 1 jour | 4 propositions valident schema + manifest cohérent | F batch |
| **F** Migration métier | wiki + monorepo + automecanik-rag | 3-5 jours | sync-from-wiki testé, comptages corrects, pre-commit hooks D20 + D22 testés | G |
| **G** Support | wiki | 1 jour | faq + policies + dédup faqs intégrés | H |
| **H** Diagnostic | wiki + monorepo | 1 jour | diagnostic.service.ts refacto, conseil-enricher non régressé | I |
| **I** Deprecate `__rag_proposals` | monorepo | 2-3h | trigger BEFORE INSERT OR UPDATE actif, flag retiré, observation 30j amorcée | J (J+30) |
| **J** Cleanup final | monorepo | 1-2h | 0 usage 30j confirmé, rename ou drop + tombstone | rien |

## Schémas ADR-022 — clarification

ADR-031 §D17b indiquait initialement que les 3 schémas (`vehicle-model.schema.json`, `vehicle-variations.schema.json`, `vehicle-role-map.schema.json`) "n'avaient jamais été migrés" dans le vault. **Vérification empirique post-merge** :

```bash
$ ls /opt/automecanik/governance-vault/_scripts/schemas/
adr.schema.json
incident.schema.json
moc.schema.json
rule.schema.json
vehicle-model.schema.json
vehicle-role-map.schema.json
vehicle-variations.schema.json
```

Les schémas **EXISTENT déjà** dans vault `_scripts/schemas/`. Phase F doit donc :
- **Conserver** les schémas dans `governance-vault/_scripts/schemas/` (ils restent vault-canonical, status `legacy` post-ADR-022 supersede)
- **Optionnellement copier** dans `automecanik-wiki/_meta/schema/legacy/adr-022/` pour documentation locale (audit trail intention historique)
- **Pas de move** — les schémas restent au vault

## Phase B — Inventaire raw physique

### Pré-requis

- Phase A.PR-A mergée (ADR-031 acceptée comme cadre canonique)
- Clone local de `ak125/automecanik-raw` configuré avec signing SSH

### Étapes

1. **Inventaire taille + nature** (lecture seule, ~30 min)

   ```bash
   cd /opt/automecanik/rag/knowledge
   du -sh _raw/ web/ web-catalog/ web-vehicles/

   # Fichiers > 100 MB (décision explicite requise par D16)
   find _raw web web-catalog web-vehicles -type f -size +100M -exec ls -lh {} \;

   # Fichiers 10-100 MB (LFS automatique)
   find _raw web web-catalog web-vehicles -type f -size +10M -size -100M -exec ls -lh {} \;

   # Distribution par extension
   find _raw web web-catalog web-vehicles -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
   ```

2. **Génération manifest** (`automecanik-raw/manifests/raw-inventory-2026-04.json`)

   Structure attendue par fichier :

   ```json
   {
     "generated_at": "2026-04-28T...",
     "total_files": 3767,
     "total_size_bytes": 328155123,
     "files": [
       {
         "original_path": "/opt/automecanik/rag/knowledge/_raw/pdf/b17ef....pdf",
         "size_bytes": 113000000,
         "sha256": "deadbeef...",
         "nature": "binary_pdf",
         "decision": "lfs",
         "decision_reason": "PDF binaire 113 MB, LFS quota OK (vérifié)",
         "target_path": "automecanik-raw/sources/pdf/b17ef....pdf"
       }
     ]
   }
   ```

3. **Validation** : drift check du manifest avant Phase C

   ```bash
   # Total bytes cohérent
   python3 -c "import json; m = json.load(open('manifests/raw-inventory-2026-04.json')); print(sum(f['size_bytes'] for f in m['files']))"

   # Décisions exhaustives (pas de "decision: null")
   jq '[.files[] | select(.decision == null)] | length' manifests/raw-inventory-2026-04.json  # = 0
   ```

## Phase C — Migration raw physique

### Étapes par catégorie de fichier

**< 10 MB texte stable (.md, .json, .yaml, .csv)** :

```bash
cd /opt/automecanik-raw
# Copy via cp avec préservation timestamps
cp -p /opt/automecanik/rag/knowledge/_raw/<...>/{<file>}.json sources/<...>/
git add sources/
```

**10-100 MB OU binaire** : Git LFS

```bash
git lfs install
git lfs track "*.pdf"
git lfs track "*.webp"
git lfs track "*.jpg"
# ...
git add .gitattributes
cp -p /opt/automecanik/rag/knowledge/_raw/pdf/<file>.pdf sources/pdf/
git add sources/pdf/<file>.pdf
```

**> 100 MB** : décision explicite documentée dans manifest avant action

- Si LFS quota OK → ajout LFS comme ci-dessus
- Si storage externe → upload S3/R2, ajout pointer dans manifest, **tombstone** dans `manifests/tombstones.json` pour le fichier non-migré in-place
- Si exclusion documentée → tombstone seulement

### Vérification byte-identity

```bash
# Baseline avant migration
find /opt/automecanik/rag/knowledge/_raw -type f -exec sha256sum {} \; | sort > /tmp/raw-baseline.sha256

# Post-migration
cd /opt/automecanik-raw
find sources -type f -exec sha256sum {} \; | sort > /tmp/raw-migrated.sha256

# Diff doit être vide sauf exclusions documentées
diff /tmp/raw-baseline.sha256 /tmp/raw-migrated.sha256
```

## Phase D — Refacto scripts

### Scripts à modifier

1. `/opt/automecanik/app/scripts/rag/download-oem-corpus.py` ligne 36
2. `/opt/automecanik/app/scripts/rag/download-brand-oem-corpus.py`
3. `/opt/automecanik/app/scripts/rag/rag-enrich-from-web-corpus.py` (lit `WEB_DIR`, `WEB_CATALOG_DIR`)

### Pattern env var safe fallback

```python
import os

# Avant (ligne 36)
WEB_DIR = "/opt/automecanik/rag/knowledge/web"

# Après
WEB_DIR = os.getenv("AUTOMECANIK_RAW_PATH", "/opt/automecanik/rag/knowledge") + "/web"
# OU plus précis :
WEB_DIR = os.getenv("AUTOMECANIK_RAW_PATH_WEB", "/opt/automecanik/rag/knowledge/web")
```

### Validation

```bash
# Avec env var → nouveau path
AUTOMECANIK_RAW_PATH=/opt/automecanik-raw/sources python3 scripts/rag/download-oem-corpus.py --dry-run

# Sans env var → ancien path (no-break)
unset AUTOMECANIK_RAW_PATH
python3 scripts/rag/download-oem-corpus.py --dry-run
```

## Phase E — Pilote wiki (4 propositions)

Choisir 1 fiche par entity_type stratégique :

| Catégorie | Slug suggéré | Source | Justification |
|---|---|---|---|
| gamme | `plaquette-de-frein` | `automecanik-rag/knowledge/gammes/plaquette-de-frein.md` | Canon freinage 13/13 déjà validé, recyclable |
| vehicle | `<modèle low-profile>` | 1 véhicule des 83 fichiers (PAS Clio/208/Golf) | Stage 2 canary low-risk per ADR-022 |
| constructeur | `dacia` ou `seat` ou `skoda` | `automecanik-rag/knowledge/constructeurs/<brand>.md` | Tier 3 brands low-profile |
| support | `livraison` | `automecanik-rag/knowledge/policies/livraison.md` | Politique simple, pas de variabilité technique |

### Critères PASS Phase E

- 4 fichiers `automecanik-wiki/proposals/<slug>.md` créés (FLAT)
- Frontmatter v1.0 valide (`node _scripts/validate-frontmatter.mjs proposals/`)
- `proposals/_manifest.json` mis à jour avec 4 entrées
- `proposals/_index.md` lisible humainement
- Aucune collision slug (`node _scripts/check-slug-uniqueness.mjs`)

## Phase F — Migration métier (4 batches)

> **Mise à jour 2026-04-28** : ce paragraphe absorbe les amendments §D15bis et §D23 (vault PRs #103, #104) et la révision empirique du count `vehicles` (8 sur main, pas 83 — cf [[adr-031-pre-phase-f-audit-corrections-20260428]]).

Batches recommandés par ordre de risque croissant :

| # | Phase | Source | Cible | Files |
|---|---|---|---|---|
| 1 | F.3 | `vehicles/` | `wiki/vehicles/<slug>.md` | 8 (main, pas la branche feat) |
| 2 | F.2 | `constructeurs/` | `wiki/constructeurs/<slug>.md` | 36 |
| 3 | F.1 | `reference/` (1) + `guides/` (13 absorbables) → distribués | `wiki/gammes/<slug>.md` body sections + `entity_data.references[]` | 14 absorptions |
| 4 | F.4 | `gammes/` (incluant les absorptions de F.1) | `wiki/gammes/<slug>.md` | 241 (cible 1655 long-terme) |
| ... | F.tombstones | 3 fichiers redondants `guides/{selecteur-vehicule-pieces-auto, references-oem, cnit-code-national-identification-type}.md` | `automecanik-raw/manifests/tombstones.json` per D21 | 3 |
| ... | (Phase H) | `guides/identifier-panne-auto.md` | `wiki/diagnostic/identifier-panne-auto.md` | 1 (Phase H, hors Phase F) |

**Total Phase F en scope** : 313 fiches (8 + 36 + 14 + 241 + 3 + 1, dont 1 reportée Phase H).

### Convention de chemin (§D23)

Les targets utilisent le **pluriel** pour les 3 collections naturelles (`gammes/`, `vehicles/`, `constructeurs/`) et le **singulier** invariant français pour `support/` + `diagnostic/`. Le frontmatter `entity_type:` et `id:` restent au singulier — ils identifient l'entité, pas le répertoire.

### Mapping `guides/` + `reference/` (§D15bis)

Plutôt que de migrer ces 17 fichiers vers `wiki/support/` (anti-pattern catch-all), ils sont **distribués** :

| Source | Cible structurelle | Pattern |
|---|---|---|
| `reference/freinage__ece-r90.md` | absorbé dans `wiki/gammes/plaquette-de-frein.md` `entity_data.references[]` | absorption |
| `guides/choisir-X.md` (9) | absorbés dans `wiki/gammes/<X>.md` body section "Guide d'achat" | absorption |
| `guides/freinage__purge`, `freinage__quand-changer`, `entretien-batterie` | absorbés dans la gamme correspondante body section "Entretien" | absorption |
| `guides/identifier-panne-auto.md` | `wiki/diagnostic/identifier-panne-auto.md` (Phase H) | promote |
| 3 fichiers redondants (selecteur-vehicule-pieces-auto, references-oem, cnit-code-national-identification-type) | `automecanik-raw/manifests/tombstones.json` per D21 | tombstone |

L'absorption requiert une nouvelle option `--mode enrich` dans `recycle-from-rag.py` (Phase F.0.x — sub-PR à venir) qui, au lieu de produire une nouvelle proposition, modifie une proposition gamme existante en injectant la section body ou l'entrée `entity_data.references[]`.

### Création `scripts/rag/sync-from-wiki.py` (D20) — ✅ livré

`nestjs-remix-monorepo/scripts/rag/sync-from-wiki.py` (PR monorepo #206) :
- Source path **doit** matcher `automecanik-wiki/exports/rag/`. Reject `wiki/<entity_type>/`.
- Dry-run par défaut, `--apply` requis pour write.
- Idempotent (sha256 check avant overwrite).
- 6/6 smoke tests verts (empty / D20 reject / dry-run / apply / idempotent).

### Hook automecanik-rag (D22) — ✅ livré

`automecanik-rag/.githooks/commit-msg` (PR rag #5) — opt-in via `git config core.hooksPath .githooks`.
`automecanik-rag/.github/workflows/d22-protected-paths.yml` — backstop CI (binding regardless of local hook setup).

Regex protégée (les deux formes pluriel + singulier listées pour fenêtre de migration) :

```
^knowledge/(gammes|gamme|vehicles|vehicle|constructeurs|constructeur
            |support|diagnostic|faq|faqs|policies|reference|guides)/
```

Marqueur d'autorisation : `rollback-documented` dans le commit message.

3/3 smoke tests verts :
- TEST 1 edit gammes/ sans label → reject rc=1
- TEST 2 edit gammes/ avec label → allow rc=0
- TEST 3 edit hors protégé → allow sans label rc=0

## Phase F.5 — Runtime hardening (rag service)

> **Phrase pivot** : ADR-031 reste le canon. La Phase F.5 ferme le gap runtime non couvert par D22 : Git protège les fichiers, mais le service HTTP pouvait encore écrire. Le RAG devient un **consumer/indexer readonly** — il ne crée plus la mémoire documentaire, n'édite plus les contenus, importe uniquement les exports wiki validés.

Phase ouverte 2026-05-03. Pas d'ADR-034 séparé (duplication). Cette phase étend D22 du niveau Git (hooks + CI) au niveau service runtime (HTTP + service-layer).

### Defense-in-depth 5 couches

| Couche | Mécanisme | Statut |
|---|---|---|
| **L1** | Git hook `commit-msg` D22 refuse modif `knowledge/<8 cats>/*.md` sans `rollback-documented` | ✅ livré PR rag #5 |
| **L2** | CI workflow `d22-protected-paths.yml` (PR-level) double-check L1 | ✅ livré PR rag #5 |
| **L3** | Pydantic v2 BaseSettings typed config (`RagWriteMode = Literal["readonly","legacy"]`, défaut `readonly`, fail-fast au boot) | À livrer PR rag-A |
| **L4** | Routes admin déprecées RFC 8594 + RFC 9745 : 410 Gone + `Sunset` + `Deprecation: true` + `Link rel="successor-version"` + body JSON `{error, replacement, adr, sunset_at, write_mode}` | À livrer PR rag-A |
| **L5** | Service-layer guards : `knowledge_service.{create,update,delete,promote}_document()` raise `RagReadOnlyError` si readonly. Couvre aussi scripts Python, cron, queue workers, endpoint M2M `/api/rag/admin/ingest/manual` | À livrer PR rag-A |

### Mode legacy encadré (anti-permanence)

`RAG_LEGACY_ADMIN_ENABLED=true` ou `RAG_WRITE_MODE=legacy` exigent **4 variables ensemble**, validées par `model_validator` Pydantic au boot :

| Variable | Format | Contrainte |
|---|---|---|
| `RAG_LEGACY_REASON` | str | obligatoire, cite `INC-YYYY-NNN` ou `P0-XXX`/`P1-XXX` |
| `RAG_LEGACY_EXPIRES_AT` | datetime ISO-8601 | obligatoire, futur, max +14j depuis maintenant |
| `RAG_LEGACY_AUTHORIZED_BY` | str | obligatoire, GitHub handle de l'autorisateur (G3) |
| Refus boot si | `now() >= expires_at` | mode legacy expiré → revenir readonly ou prolonger |

Logs WARNING au boot. Metric Prometheus `rag_legacy_mode_enabled{reason_class}` (gauge à 1) + `rag_legacy_mode_expires_in_seconds`. Audit log JSON-line par appel admin en legacy : `audit.legacy_admin_call{route, method, actor, reason, expires_at, authorized_by}`.

### Sunset date routes admin

J0 = date de merge PR-A. Sunset header = J+30. Drop des contrôleurs Phase J+30+ si critère métrique :

```promql
sum(increase(rag_admin_deprecated_route_hits_total[30d])) == 0
```

Plus aucun appel `legacy_mode_calls` pendant 30j cumulé + inspection logs Caddy/nginx en amont (pas de POST sur `/admin/documents/*` ou `/admin/ingest/pdf/run`).

### Schema Weaviate v2 — KB_Knowledge_v2 (14 properties)

Versioning via nouvelle collection (pas mutation en place). 8 properties existantes + 6 nouvelles :

| Property | Type | Rôle |
|---|---|---|
| `canonical_source` | str (`"automecanik-wiki"\|"legacy-rag-knowledge"`) | discriminant repo source |
| `source_layer` | str (`"exports/rag"\|"knowledge"`) | localisation dans la couche source |
| `source_commit` | str (sha-1 git) | **commit du repo source canonique** : wiki pour exports, rag pour legacy traçable, null sinon |
| `lineage_id` | str (UUIDv7) | trace de la transformation/batch — **PAS** clé d'idempotence |
| `embedding_model` | str (ex `"all-MiniLM-L6-v2"`) | détecte besoin re-indexation si modèle change |
| `origin_batch_kind` | str (`Literal["legacy_migration","wiki_import"]`) | discrimine v1 migré vs v2 natif |

5 properties `indexFilterable: true` minimum : `canonical_source`, `source_path`, `content_hash`, `chunk_index`, `embedding_model`. **Pas de "composite index" relationnel** (Weaviate n'expose pas cette primitive) — l'efficacité vient des inverted indexes filtrables + requête `WHERE And` multi-opérandes.

### Idempotence par clé naturelle

```
(canonical_source, source_path, content_hash, chunk_index)
```

Pas via `lineage_id` qui est généré dynamiquement (UUIDv7 unique par batch). Avant insert dans `KB_Knowledge_v2`, requête Weaviate `WHERE And` sur ces 4 fields → skip si match.

### Filtres ingestion wiki → rag (intentionnellement conservateur)

- `exportable.rag == True`
- `review_status == "approved"` (exclut intentionnellement `auto_passed` jusqu'à amendment futur signed G3 du runbook)
- `truth_level ∈ {"L1", "L2"}` (cf. `rag-foundation-baseline.md`)
- `len(source_refs) >= 1`
- `content_hash` présent + validation Pydantic

Skips → dead-letter `/var/lib/automecanik-rag/quarantine/<reason>/<entity_type>/<slug>.md` + sidecar `<slug>.skip.json` (hors repo Git, volume Docker dédié, `.gitignore` couvre `/var/` et `/quarantine/`).

### Audit log — sécurité, retention

| Champ | Format | Notes RGPD |
|---|---|---|
| `actor.ip` | sha256(ip + salt) | **JAMAIS** IP en clair |
| `actor.user_id` | uuid | — |
| `actor.user_agent_class` | `"browser\|cli\|cron\|m2m"` | classifié, pas de string brute |
| **JAMAIS** | auth token, session ID, X-Internal-Key, query string | retention/leak risk |

Path `/var/log/automecanik-rag/audit-legacy-admin.jsonl`. Permissions Unix `rag:rag` 0640 (writable par service uniquement, lisible par groupe `rag-readers` pour ops/Loki/Vector). Rotation logrotate 90j.

### 4 PRs ordonnées

1. **PR-α (vault)** — cette extension runbook + regen `99-meta/canon-hashes.json` + signed commit G3
2. **PR-A (rag) `feat/f5-runtime-hardening`** — L3+L4+L5 hardening. **Indépendante de Weaviate**. **BLOCKING GATE** avant toute reprise F.0.x/F.1/F.2/F.4/G/H/I/J. Inventaire complet routes via sweep `rg "@(app|router)\.(post|put|delete|patch)" app/`. Couvre minimum : `/admin/documents/{new,edit,delete,promote}`, `/admin/ingest/pdf/run`, `/api/rag/admin/ingest/manual` (M2M X-Internal-Key), `/api/rag/admin/pipeline/launch`. README banner readonly + UI admin (boutons cachés/grisés)
3. **PR-B (rag) `feat/weaviate-kb-v2`** — schema 14 properties + `migrate_kb_v1_to_v2.py` idempotente avec `flock /var/lock/rag-migrate.lock`, batch 500. Script `estimate_v1_to_v2.py` (coverage + coût embeddings préalable). v1 conservée 30j puis drop si critère métrique
4. **PR-C (rag) `feat/import-wiki-exports`** — `scripts/importers/import_wiki_exports.py` Pydantic-validated. Fail-fast si `KB_Knowledge_v2` absente. Lock global `flock /var/lock/rag-import.lock`. `source_commit = git -C $AUTOMECANIK_WIKI_PATH rev-parse HEAD`

### Acceptance criteria globales

- ✅ Routes admin retournent 410 en readonly avec headers RFC 8594/9745 conformes
- ✅ `RAG_WRITE_MODE=invalid` ou legacy mal configuré → ValidationError au boot
- ✅ `RAG_LEGACY_EXPIRES_AT > +14j` ou dans le passé → ValidationError au boot
- ✅ Service-layer `create/update/delete/promote` lèvent `RagReadOnlyError` (testé sans HTTP — couvre scripts/cron/M2M)
- ✅ `KB_Knowledge_v2` créée avec 14 properties (pas mutation v1)
- ✅ Migration v1→v2 idempotente, `count(v1) == count(v2)` après `--apply`
- ✅ `import_wiki_exports.py --dry-run` exit 2 si `KB_Knowledge_v2` absente, exit 4 si `$AUTOMECANIK_WIKI_PATH` invalide
- ✅ Idempotence par clé naturelle `(canonical_source, source_path, content_hash, chunk_index)` testée (insertion concurrente → 1 seul chunk)
- ✅ Dead-letter écrit dans `/var/lib/automecanik-rag/quarantine/`, hors repo Git
- ✅ Audit log ne contient pas de tokens/secrets (test : POST avec `Authorization: Bearer xxx` → token absent du log)
- ✅ Coverage manifest AEC `PARTIAL_COVERAGE` jusqu'à F.5 close, `SCOPE_SCANNED` post-merge

### Plan canonique

`/home/deploy/.claude/plans/verifier-et-analyser-et-pure-rabbit.md` (approuvé 2026-05-03 après 3 rondes de review).

### Anti-patterns à éviter

- ❌ ADR-034 séparé — duplique cette phase
- ❌ `os.getenv("RAG_WRITE_MODE")` éparpillé — bricolage. Pydantic v2 BaseSettings centralisé
- ❌ Mutation Weaviate schema en place — bricolage. Schema versioning v1→v2
- ❌ YAML parsing libre du frontmatter wiki — bricolage. Pydantic models mirror du JSON Schema
- ❌ Idempotence via `lineage_id` seul — généré dynamiquement, doublons garantis. Clé naturelle obligatoire
- ❌ `source_commit = commit du repo rag` — confusion consumer/source. Doit être commit du wiki (ou null si legacy non traçable)
- ❌ Dead-letter dans repo Git canon — confusion `automecanik-raw/quarantine/`. Volume Docker `/var/lib/automecanik-rag/quarantine/`
- ❌ PR-A dépendante de Weaviate v2 — perd indépendance. Hardening doit pouvoir merger seul
- ❌ `delete_class('KB_Knowledge_v2')` dans tests — destructif. Utiliser env var collection inexistante
- ❌ Reprise F.x avant PR-A mergée — enrichit un repo encore writable
- ❌ `RAG_LEGACY_ADMIN_ENABLED=true` permanent — encadrement strict +14j auto-expire obligatoire
- ❌ Glissement silencieux `auto_passed` accepté — passe par amendment runbook signed G3
- ❌ "composite index Weaviate" — primitive relationnelle inexistante. `indexFilterable: true` + `WHERE And`
- ❌ Audit log avec auth tokens / IP en clair / query string — RGPD/secret leak
- ❌ Drop routes admin sans critère métrique — `sum(increase(rag_admin_deprecated_route_hits_total[30d])) == 0` pendant 30j obligatoire avant drop

## Phase G — Support (faq + policies + dédup faqs)

```bash
# Audit duplication faq vs faqs
diff -u /opt/automecanik/rag/knowledge/faq /opt/automecanik/rag/knowledge/faqs

# Migration unifiée vers wiki/support/
# entity_data.category = "faq" ou "policy" pour distinguer
```

## Phase H — Diagnostic

```bash
# Audit conseil-enricher (RPC DB, doit pas lire filesystem)
grep -rn "filesystem\|readFileSync\|fs\\.readFile" /opt/automecanik/app/backend/src/modules/seo/services/conseil-enricher.service.ts

# Refacto diagnostic.service.ts
# AVANT : path hardcodé /opt/automecanik/rag/knowledge/diagnostic/
# APRÈS : env var AUTOMECANIK_WIKI_PATH/wiki/diagnostic/
```

## Phase I — Deprecate `__rag_proposals` in-place (J0)

### SQL migration

```sql
-- /opt/automecanik/app/backend/supabase/migrations/<ts>_deprecate_rag_proposals.sql

-- Comment SQL deprecated
COMMENT ON TABLE __rag_proposals IS
'DEPRECATED 2026-XX-XX par ADR-031 §"Héritage ADR-022". Lectures continuent de fonctionner (lignes historiques préservées) ; toute écriture/modification est bloquée par trigger. Drop ou rename prévu post-J+30 si 0 usage.';

-- Trigger BEFORE INSERT OR UPDATE
CREATE OR REPLACE FUNCTION block_rag_proposals_writes()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Table __rag_proposals deprecated par ADR-031. Toute écriture est bloquée. Voir ledger/decisions/adr/ADR-031-four-layer-content-architecture.md §"Héritage ADR-022".';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_block_rag_proposals_writes
BEFORE INSERT OR UPDATE ON __rag_proposals
FOR EACH ROW
EXECUTE FUNCTION block_rag_proposals_writes();
```

### Refacto `VehicleRagGeneratorService`

- Retirer toutes les `INSERT INTO __rag_proposals`
- Écrire dans `automecanik-raw/recycled/r8-generation/<typeId>.md` au lieu de filesystem RAG direct
- Retirer flag `RAG_PROPOSAL_MODE`

### Observation 30j

```bash
# Quotidien (cron ou manuel)
psql -d $DATABASE_URL -c "SELECT seq_scan, idx_scan, n_tup_ins, n_tup_upd FROM pg_stat_user_tables WHERE relname = '__rag_proposals';"

# n_tup_ins + n_tup_upd doivent rester à 0
# seq_scan + idx_scan = nombre de lectures résiduelles (info, pas blocker)
```

## Phase J — Cleanup final (J+30+)

### Pré-requis

- 30 jours d'observation depuis Phase I
- `pg_stat_user_tables.n_tup_ins + n_tup_upd = 0` (aucune écriture tentée)
- `grep -rn "rag_proposals\|rag-proposal" /opt/automecanik/app/backend/src` = 0 hit
- Aucun error log mentionnant la table

### Décision rename vs drop

| Critère | Rename `__rag_proposals_deprecated` | Drop |
|---|---|---|
| Lectures résiduelles | Préservées (table accessible nouvelle nom) | Cassées (CASCADE potentiel) |
| Espace disque | Conservé | Récupéré |
| Audit trail | Schema/données préservées | Perdu |
| Recommandé si | Lectures résiduelles ≥ 1 sur 30j | seq_scan = 0 sur 30j |

### Tombstone obligatoire

```json
{
  "tombstones": [
    {
      "original_path": "DB:public.__rag_proposals",
      "reason": "Deprecated 2026-XX-XX par ADR-031 §Héritage ADR-022, observed 0 writes 30j, 0 reads 30j. Dropped J+30+.",
      "decided_at": "2026-XX-XX",
      "decided_by": "@fafa",
      "checksum_sha256": "<dump table avant drop>",
      "audit_run_id": "phase-j-cleanup-20260X"
    }
  ]
}
```

## Critères globaux de succès ADR-031

- 4/4 copies AEC alignées par hash (déjà fait Phase B.3)
- 313 MB raw migré ou tombstoné explicitement
- 8 catégories migrées vers wiki (5 métier en F, 2 support en G, 1 diagnostic en H)
- `__rag_proposals` drop ou renamed J+30+
- 0 régression sur pipelines KW canon, R8 ADR-022 (legacy preserved), RAG ingestion (sync-from-wiki)
- Tombstones documentent toute suppression (G2 zéro orphelin)

## Références

- [[ADR-031-four-layer-content-architecture]] — cadre canonique
- [[ADR-029-rag-v2.1-control-plane-closure]] — state machine 7 stages (paths amendés v2.1.1)
- [[ADR-022-r8-rag-control-plane]] — superseded par ADR-031 (héritage intégré)
- [[ADR-026-content-separation]] — superseded par ADR-031 (4 couches au lieu de 3)
- Plan d'exécution complet : `/home/deploy/.claude/plans/verifier-diagnostic-faq-policies-declarative-rain.md`
