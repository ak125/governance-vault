---
type: runbook
scope: seo/r7/curation
surface: R7_BRAND
date: 2026-04-22
owner: Fafa
script: scripts/seo/curate-r7-batch.py
tags: [runbook, r7, curation, batch, ops, admin-api]
---

# Runbook — `curate-r7-batch.py`

> **Script** : [`scripts/seo/curate-r7-batch.py`](https://github.com/ak125/nestjs-remix-monorepo/blob/main/scripts/seo/curate-r7-batch.py) (monorepo, PR #108)
> **Rôle** : ré-applique les drafts éditoriaux R7 sur disque vers `__seo_brand_editorial` via l'API admin
> **Sibling** : [[runbook-build-brand-rag]] (facts stables) · [[runbook-download-brand-oem-corpus]] (corpus support) · runbook-admin-brand-editorial ([vault PR #26](https://github.com/ak125/governance-vault/pull/26))

---

## À quoi ça sert

Industrialise l'orchestration `login → PUT → enrichSingle → log` qui était d'abord exécutée comme scripts ad-hoc `/tmp/wave{N}-drafts.py` lors de la session 2026-04-22 (curation 36/36 marques).

Lit chaque draft JSON sur disque à `/opt/automecanik/rag/knowledge/web/brands/{alias}/editorial-draft.json` et le PUT à `/api/admin/r7/editorial/:marqueId`. L'auto-trigger `enrichSingle` se déclenche par défaut, régénérant `__seo_r7_pages.rendered_json.blocks[R7_S9_FAQ]`.

## Ce que le script ne fait PAS

- **Aucune génération de contenu** — les drafts sont rédigés humainement, sourcés Wikipedia FR + RAG (cf. [[runbook-admin-brand-editorial]] et [[r7-brand-editorial-live-sync]])
- **Aucune synthèse LLM**
- Ne crée/modifie pas les drafts eux-mêmes
- Ne touche pas à `__seo_r7_pages` directement (passe par l'enricher)

## Quand lancer

| Trigger | Fréquence | Commande |
|---------|-----------|----------|
| Rollback Supabase de `__seo_brand_editorial` | rare | `--all` |
| Ajout d'une nouvelle marque au catalogue (avec draft créé manuellement) | à la demande | `--brand <alias>` |
| Re-synchro après refactor R7 enricher | rare | `--all` |
| Migration entre environnements via DB partagée | rare | `--all --skip-enrich` puis trigger batch enrich |
| Test de la chaîne login → PUT → enrich | à la demande | `--brand peugeot --dry-run` puis sans `--dry-run` |

**NE PAS lancer en cron.** Les drafts changent rarement et un ré-enrich injuste produit du bruit DB pour aucun gain.

## Pré-requis

```bash
cd /opt/automecanik/app
pip install requests  # déjà installé sur DEV
```

Variables d'env optionnelles (defaults dans le script) :
- `R7_BASE_URL` (default `http://localhost:3000`)
- `R7_ADMIN_EMAIL` (default `superadmin@autoparts.com`)
- `R7_ADMIN_PASSWORD` (override en env sécurisé)

Backend NestJS local doit être up (`/health` → 200) ou pointer un environnement distant via `R7_BASE_URL`.

## Commandes

### Dry-run global (planification)

```bash
python3 scripts/seo/curate-r7-batch.py --all --dry-run
```

Liste tous les drafts trouvés sur disque sans aucun appel réseau. Utile pour vérifier que tous les `marque_id` sont valides et combien de drafts seront appliqués.

### Re-apply une marque (ré-curation ciblée)

```bash
python3 scripts/seo/curate-r7-batch.py --brand peugeot
```

Sortie attendue :
```
=== curate-r7-batch — 1 brand(s) to apply ===
Base URL : http://localhost:3000
  ✅ peugeot         (id=128): score=86.14 PUBLISH

=== SUMMARY ===
  Total applied : 1
  ✅ PUBLISH: 1
```

### Re-apply tous les drafts (rollback recovery)

```bash
python3 scripts/seo/curate-r7-batch.py --all
```

Boucle sur tous les drafts présents dans `/opt/automecanik/rag/knowledge/web/brands/*/editorial-draft.json`. Chaque PUT déclenche un `enrichSingle` séquentiel (~150 ms par marque + scoring).

### Skip l'auto-enrichissement (pour batch import)

```bash
python3 scripts/seo/curate-r7-batch.py --all --skip-enrich
```

Utile quand on veut écrire les 36 drafts en DB rapidement et déclencher l'enrichissement plus tard via `POST /api/admin/r7/enrich-batch` (parallèle/throttlé).

## Format draft attendu

Conforme à `BrandEditorialPayloadSchema` (Zod, backend) :

```json
{
  "_meta": {
    "brand_alias": "peugeot",
    "marque_id": 128,
    "generated_at": "2026-04-22",
    "rule_applied": "R7 marque-level strict"
  },
  "curated_by": "claude-code-2026-04-22",
  "faq": [
    { "q": "...", "a": "..." }
  ],
  "common_issues": [],
  "maintenance_tips": []
}
```

Le bloc `_meta` est ignoré par le backend (purement informatif). Les 3 listes (`faq`, `common_issues`, `maintenance_tips`) doivent respecter les limites Zod (15 / 20 / 20 max, `q` 5-200 car, `a` 20-1000 car, etc.).

## Output codes

| Status backend | Icône | Signification |
|---|---|---|
| `PUBLISH` | ✅ | Décision SEO finale, page R7 prête |
| `REVIEW_REQUIRED` | ⚠️  | Sous le seuil PUBLISH (typiquement 70). Ajouter du contenu |
| `REGENERATE` | 🔄 | L'enricher demande une nouvelle exécution |
| `REJECT` | ❌ | Échec critique (RAG manquant, payload invalide) |

Exit code script : 0 si tous les PUT réussissent (HTTP 200), > 0 si argparse error ou aucun draft trouvé pour `--brand`.

## Pièges connus

### Backend down / OOM

Si `npm run start` n'est pas up ou turbo dev a crashé OOM (cf. session 2026-04-22), le script échoue au login. Vérifier `curl localhost:3000/health` avant de lancer.

### `_meta.marque_id` manquant

Le script skip silencieusement les drafts dont `_meta.marque_id` est absent ou non numérique. Un message warning est affiché sur stderr. Cause typique : draft édité à la main sans copier le bloc `_meta`.

### Ordre alphabétique vs ordre wave

Le script trie par `glob` alphabétique (audi, bmw, chevrolet…). L'ordre wave1-4 historique n'est pas reproduit. Sans incidence sur le résultat final.

### Crédentials dans l'env

Le default `R7_ADMIN_PASSWORD` du script est l'admin DEV connu. Pour PROD ou un environnement avec credentials différents, surcharger via env :

```bash
R7_ADMIN_PASSWORD='secret-prod-password' \
R7_BASE_URL='https://www.automecanik.com' \
python3 scripts/seo/curate-r7-batch.py --all
```

⚠️ Attention : pointer `R7_BASE_URL` vers PROD écrit en DB partagée. Tester d'abord en DEV.

## Performances mesurées

Session 2026-04-22 sur 36 marques (Peugeot inclus) :

| Mode | Durée |
|---|---|
| `--all` (avec auto-enrich) | ~4 min (~6.5 s/marque incluant scoring) |
| `--all --skip-enrich` | ~30 s (juste les upserts DB) |
| `--brand <one>` | < 1 s |

## Workflow type — rollback recovery

```bash
# 1. Verify backend health
curl http://localhost:3000/health  # → 200

# 2. Verify drafts exist on disk
ls /opt/automecanik/rag/knowledge/web/brands/*/editorial-draft.json | wc -l

# 3. Dry-run pour confirmer le plan
python3 scripts/seo/curate-r7-batch.py --all --dry-run

# 4. Apply pour de bon
python3 scripts/seo/curate-r7-batch.py --all

# 5. Spot check
psql ... "SELECT COUNT(*) FROM __seo_r7_pages WHERE seo_decision='PUBLISH';"
# Attendu : 36
```

## Workflow type — ajout d'une nouvelle marque

```bash
# 1. Créer le draft à la main pour la nouvelle marque <alias>
# (suivre le squelette 5 FAQ canoniques décrit dans memory r7-curation-method)
mkdir -p /opt/automecanik/rag/knowledge/web/brands/<alias>
$EDITOR /opt/automecanik/rag/knowledge/web/brands/<alias>/editorial-draft.json

# 2. Apply
python3 scripts/seo/curate-r7-batch.py --brand <alias>
```

## Règles dérivées

1. **Génération humaine, orchestration scriptée** — le script ne génère rien, il oriente les artefacts existants vers l'API. La règle `feedback_rag_vault_always_first.md` (memory) est respectée par construction.
2. **Idempotent** — re-lancer `--all` plusieurs fois est inoffensif (l'enricher recompose les blocs avec les mêmes inputs, le score reste stable à ±1).
3. **Drafts comme source de vérité** — les drafts sur disque sont l'asset re-jouable. La table DB est un cache du dernier PUT. En cas de perte DB, les drafts permettent de reconstituer l'état.
4. **Skip-enrich pour batch import** — si on veut alimenter rapidement la DB sans déclencher 36 enrichissements séquentiels, utiliser `--skip-enrich` puis `POST /api/admin/r7/enrich-batch`.

## Références

- Script monorepo : https://github.com/ak125/nestjs-remix-monorepo/pull/108
- Drafts archivés : `/opt/automecanik/rag/knowledge/web/brands/{alias}/editorial-draft.json`
- Méthode de génération des drafts : memory `r7-curation-method.md`
- Sibling runbook (corpus download) : [[runbook-download-brand-oem-corpus]]
- Sibling runbook (facts stables) : [[runbook-build-brand-rag]]
- Architecture R7 : [[r7-brand-editorial-live-sync]]
- Règle canon : [[r7-surface-purity-no-cross-surface-urls]]
- Retro session : [[2026-04-22-session-r7-full-curation]]
