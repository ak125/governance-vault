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

## Phase F — Migration métier (5 catégories)

Batches recommandés par ordre de risque croissant :

1. `reference/` (1 fichier) → `wiki/support/<slug>.md` (smallest, validates flow)
2. `guides/` (16 fichiers) → `wiki/support/<slug>.md`
3. `constructeurs/` (72 fichiers) → `wiki/constructeur/<slug>.md`
4. `vehicles/` (83 fichiers) → `wiki/vehicle/<slug>.md`
5. `gammes/` (241 fichiers actuels, cible 1655) → `wiki/gamme/<slug>.md`

### Création `scripts/rag/sync-from-wiki.py` (D20)

Garde-fous obligatoires :
- Source path **doit** matcher `automecanik-wiki/exports/rag/`. Reject `wiki/<entity_type>/`.
- Dry-run par défaut, `--apply` requis pour write.
- Idempotent (sha256 check avant overwrite).

### Pre-commit hook automecanik-rag (D22)

```bash
# .githooks/pre-commit dans automecanik-rag
if git diff --cached --name-only | grep -E "^knowledge/(gammes|vehicles|constructeurs|guides|reference)/" >/dev/null; then
  if ! git log -1 --format=%B | grep -q "rollback-documented"; then
    echo "ERROR: Modification manuelle de knowledge/<5 catégories métier> interdite (D22 ADR-031)."
    echo "Pour rollback documenté, ajouter 'rollback-documented' dans le commit message."
    exit 1
  fi
fi
```

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
