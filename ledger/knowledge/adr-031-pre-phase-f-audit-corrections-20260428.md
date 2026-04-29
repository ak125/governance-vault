---
type: knowledge
status: active
date: 2026-04-28
related_adr: ["ADR-031"]
related_rules: ["G1", "G2", "G3", "AP-11"]
audience: ["@fafa", "claude-code", "cowork"]
---

# Audit pré-Phase F.x — corrections appliquées (ADR-031)

> Verdict d'audit utilisateur après livraison Phase F.0 (tooling complet) et avant lancement Phase F.1-F.4 (mass-recycle). 5 corrections identifiées et appliquées avant tout batch.

## Contexte

À la fin de Phase F.0 (4 PRs livrées : vault [#103](https://github.com/ak125/governance-vault/pull/103) D15bis, wiki [#4](https://github.com/ak125/automecanik-wiki/pull/4) tooling, monorepo [#206](https://github.com/ak125/nestjs-remix-monorepo/pull/206) sync-from-wiki, rag [#5](https://github.com/ak125/automecanik-rag/pull/5) D22 hooks), l'utilisateur a procédé à un audit visuel de l'état des repos `automecanik-raw` et `automecanik-wiki` sur GitHub.

Verdict : **READY_FOR_PHASE_E_REVIEW** mais **pas encore READY_FOR_MASS_MIGRATION** — 5 corrections à appliquer avant Phase F.1-F.4.

## Les 5 corrections

### D — Visibilité repo `automecanik-raw` : public → private

**Findings** : `ak125/automecanik-raw` était public. Or il est destiné à recevoir :

- PDF fournisseurs (catalogue ATE 113 MB déjà migré Phase C, autres OEM à venir)
- Exports CSV bruts Google Ads / GSC
- Web clips / corpus OEM scrapé
- Anciens fichiers RAG recyclés
- Datasets / fixtures recyclables du monorepo

Même sans secrets explicites, le repo peut contenir des données propriétaires fournisseurs, des documents techniques sous licence implicite, des contenus non publiables.

**Action** : `gh repo edit ak125/automecanik-raw --visibility private`. Vérifié : `isPrivate: true`.

`automecanik-wiki` reste public (connaissance validée publique, opt-in éditorial). Décision à reconsidérer à Phase F.x si nécessaire.

### A — ADR-031 §D23 : convention de chemin pluriel adoptée (vault [PR #104](https://github.com/ak125/governance-vault/pull/104))

**Findings** : ADR-031 corpus impose `wiki/<entity_type_singular>/` (`wiki/gamme/`, `wiki/vehicle/`, ...) et écrit *"Pas de variantes pluriel (`wiki/gammes/` interdit)"*. Mais l'audit GitHub montre la structure réelle déjà déployée :

```
wiki/
  ├── constructeurs/    (pluriel)
  ├── diagnostic/       (singulier — invariant français)
  ├── gammes/           (pluriel)
  ├── support/          (singulier — invariant français)
  └── vehicles/         (pluriel)
```

`README.md`, `CLAUDE.md` du wiki, `ingestion-contract.md`, `_meta/entity-registry.json`, et plusieurs scripts internes référencent le pluriel. Coût rename = 5 dirs + ~10 fichiers gouvernance + paths Phase F.1-F.4 + downstream consumers — strictement supérieur au bénéfice cosmétique.

**Action** : §D23 amendé pour adopter le pluriel comme convention canonique. `entity_type:` et `id:` frontmatter restent au singulier (ils identifient l'entité, pas le répertoire).

| `entity_type` | path canonique |
|---|---|
| `gamme` | `wiki/gammes/<slug>.md` |
| `vehicle` | `wiki/vehicles/<slug>.md` |
| `constructeur` | `wiki/constructeurs/<slug>.md` |
| `support` | `wiki/support/<slug>.md` |
| `diagnostic` | `wiki/diagnostic/<slug>.md` |

Justification §D23 : adapter l'ADR à la réalité opérationnelle quand le coût de l'inverse est strictement supérieur (`feedback_no_hybrid_workarounds.md` n'est PAS contredit ici — D23 n'est pas un workaround mais une décision structurelle d'aligner l'autorité sur le déploiement).

### B — Typos `wiki//` et `exportable.: true` : false alarm

**Findings** : l'audit signalait des typos dans `automecanik-wiki/CLAUDE.md` :

- `Ne jamais écrire directement dans wiki//` — apparemment manquant un placeholder
- `exportable.: true` — apparemment une key vide

**Action** : inspection du fichier réel. Les contenus sont :

```
- Ne **jamais** écrire directement dans `wiki/<area>/` sans instruction humaine explicite
- Ne **jamais** marquer une fiche `validated`, `human_reviewed`, ou `exportable.<x>: true` sans validation humaine
```

Les placeholders `<area>` et `<x>` sont bien présents. Ce qui apparaissait comme typos était un **artefact de rendu de l'outil d'audit** (probable strip HTML des balises ressemblant à des tags). Pas de modification nécessaire.

### C — Recycler `target_path` → pluriel (wiki [PR #5](https://github.com/ak125/automecanik-wiki/pull/5))

**Findings** : suite à l'adoption du pluriel par §D23, le script `_scripts/recycle-from-rag.py` (livré dans wiki #4) émettait encore les chemins singuliers dans le body et le `review_notes` des propositions générées :

```python
f"> À reviewer manuellement avant promotion vers `wiki/{entity_type}/{slug}.md`."
```

→ produit `wiki/gamme/plaquette-de-frein.md` (singulier, contradictoire avec la réalité repo).

**Action** : ajout d'un mapping `ENTITY_TO_WIKI_DIR` qui résout :

```python
ENTITY_TO_WIKI_DIR = {
    "gamme":        "gammes",
    "vehicle":      "vehicles",
    "constructeur": "constructeurs",
    "support":      "support",
    "diagnostic":   "diagnostic",
}
```

Patché dans 2 endroits : le `review_notes` de la frontmatter générée + les 2 lignes du body. Smoke test 5/5 entity_types verts. Bulk dry-run 312/313 OK (1 FAIL = data quality source `vehicles/renault.md` brand-only fiche misplaced).

### E + F — `source_refs.origin_repo` proposals → `automecanik-raw` : déféré

**Findings** : les 4 propositions pilotes Phase E ont :

```yaml
source_refs:
  - kind: recycled
    origin_repo: automecanik-rag
    origin_path: knowledge/policies/livraison.md
    captured_at: '2026-04-28'
```

Or le principe directeur ADR-031 est : *"tout brut / recyclé → automecanik-raw"*. Donc post-Phase F.x, après migration des 5 catégories métier (gammes, vehicles, constructeurs, policies, faq, diagnostic) vers `automecanik-raw/recycled/rag-knowledge/`, les `source_refs` doivent pointer vers le repo raw, pas le rag.

**Action** : **déféré post-Phase F.x**. Le user a explicitement reconnu que c'est acceptable comme état transitoire pour le pilote (*"C'est compréhensible pour le pilote, mais ce n'est pas conforme au principe final"*). Le rewrite des `source_refs` se fait après que les fichiers soient effectivement présents dans `automecanik-raw/recycled/rag-knowledge/<cat>/<slug>.md` (Phase F.x livrera ces copies).

## Découverte annexe — count `vehicles` corrigé

Pendant les smoke tests post-D23, le bulk dry-run a montré `vehicles: total=8` au lieu de 83 vu plus tôt dans la session.

**Cause racine** : la première inspection avait été faite alors que la working copy de `/opt/automecanik/rag/` était checked-out sur la branche `feat/vehicle-web-enrichment-stage1` (75 fiches enrichies non-mergées). Sur `main`, seulement 8 fiches vehicles existent.

**Conséquence** : Phase F.3 batch = 8 fiches au lieu de 83. **Total Phase F = 313 fiches au lieu de 388**.

| Catégorie | Count main | Phase F batch |
|---|---|---|
| gammes | 241 | F.4 |
| constructeurs | 36 | F.2 |
| diagnostic | 18 | (Phase H) |
| vehicles | 8 | F.3 |
| faq | 7 | (Phase G) |
| policies | 3 | (Phase G) |
| reference | 1 | F.1 (absorbé) |
| guides | 16 | F.1 (absorbés/tombstones) |

Le runbook (`adr-031-migration-runbook-20260428.md`) sera amendé en conséquence lors d'une prochaine PR.

## État Phase F readiness — verdict final

| Critère | État |
|---|---|
| ADR-031 corps + amendments (D14-D22, D15bis, D23) | ✅ figé |
| Tooling F.0 (recycler + sync-from-wiki + D22 hooks) | ✅ livré |
| Repo raw private | ✅ done |
| Recycler conforme D23 pluriel | ✅ done |
| 4 propositions pilotes Phase E review-ready | ✅ done |
| `source_refs.origin_repo` proposals → automecanik-raw | ⏸️ déféré post-Phase F.x |

**Statut canonique** : `READY_FOR_PHASE_F_KICKOFF`, autorisation explicite utilisateur requise pour démarrer F.1-F.4.

## Coverage manifest (AEC)

- `scope_requested` : appliquer les 5 corrections issues du verdict d'audit utilisateur pré-Phase F.x
- `scope_actually_scanned` : 5 actions identifiées, traitées
- `files_read_count` : 4 propositions pilotes wiki + ADR-031 + recycle-from-rag.py + CLAUDE.md wiki + GitHub repo settings (3 repos)
- `excluded_paths` : Phase F.x batches eux-mêmes (autorisation explicite séparée requise)
- `unscanned_zones` : aucune
- `corrections_proposed` : 4 (D appliquée, A vault PR, C wiki PR, E+F déférés). B = false alarm.
- `validation_executed` : grep usage (Phase F.x prerequisites), CI green sur les 2 PRs (vault #104, wiki #5), repo visibility verify
- `remaining_unknowns` : Phase F.x autorisation, design exports/ structure interne (TBD Phase F.x)
- `final_status` : `SCOPE_SCANNED`

## Références

- [[ADR-031-four-layer-content-architecture]] §D15bis (vault PR #103) + §D23 (vault PR #104)
- [[adr-031-migration-runbook-20260428]] — runbook Phases B-J
- Plan canonique : `/home/deploy/.claude/plans/verifier-diagnostic-faq-policies-declarative-rain.md`
- PRs livrées dans le scope : vault #103 + #104, wiki #4 + #5, monorepo #206, rag #5
- Memory `feedback_no_hybrid_workarounds.md` — base de la décision §D23 (adapter l'autorité, pas bricolage)
