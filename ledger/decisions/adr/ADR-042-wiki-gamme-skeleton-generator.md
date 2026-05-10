---
id: ADR-042
title: "Wiki gamme skeleton-generator (Pattern A) — débloquer Étape 6 gammes du pivot ADR-031 sans contournement legacy"
status: superseded
date: 2026-05-06
decision_date: 2026-05-06
decision_makers: ["@fafa"]
supersedes: []
superseded_by: ["ADR-031"]
resolution_pr: "ak125/nestjs-remix-monorepo#332"
resolution_note: "Pattern A (skeleton-generator) abandonné. Closure §2.B effectuée via backfill direct RAG mirror sous canon ADR-031 (cf. body §Solution effective)."
amends: []
related_rules: []
related_incidents: []
related_adr: ["ADR-031", "ADR-041", "ADR-039"]
implementation_status: cancelled
---

> **⚠️ SUPERSEDED 2026-05-06** — investigation post-merge (user pushback) a révélé que le problème ADR-042 prétendait résoudre était fondé sur **enquête incomplète**.
>
> Réalité empirique :
> - 169/232 R1 slots avaient déjà 4/5 sections à 100% (DB peuplée)
> - RAG mirror `/opt/automecanik/rag/knowledge/gammes/` toujours disponible avec champs structurés (cost_range, brands.premium, related_parts, confusion_with)
> - Le pipeline canon (agent r1-content-batch → RAG mirror → DB) n'a JAMAIS dépendu du peuplement wiki gamme spécifique
>
> Solution effective : [monorepo PR #332](https://github.com/ak125/nestjs-remix-monorepo/pull/332) — `scripts/seo/backfill-r1-safe-table.py` mirror direct du pattern `backfill-r1-gatekeeper.py`. Run en 1 minute sur 142 slots → `has_safe_table: 169/169 (100%)`. ADR-041 §2.B fermée empiriquement sans pivot wiki gamme.
>
> Le skeleton-generator de cette ADR (monorepo PR #331) a été reverté via [monorepo PR #333](https://github.com/ak125/nestjs-remix-monorepo/pull/333).
>
> Mémoire user-level `feedback_validate_full_context_before_planning_solution` ajoutée pour prévenir récurrence : valider full chain (DB existante + recyclage legacy + pipelines existants + canon flows) AVANT de drafter une ADR débloquante.
>
> Cette ADR reste publiée comme document historique de l'investigation et de l'arbitrage A/B documenté en mémoire `rag-to-wiki-sot-pivot-20260503`. Le **pivot wiki gamme spécifique** (Pattern A vs B) reste un futur sujet possible si curation humaine sur 232 gammes devient justifiée par un autre signal — mais ce n'est PAS le path pour ADR-041 §2.B.

# ADR-042: Wiki gamme skeleton-generator (Pattern A)

## Contexte

ADR-031 (four-layer-content-architecture) §D20/D22 figeait pour 2026-05-04 le pivot architectural **wiki = SoT, automecanik-rag/knowledge/ = mirror via cron VPS DEV**. Pipeline activé bout-en-bout pour les **brands** (36 fiches LIVE, sync `wiki/exports/rag/constructeurs/<slug>.md` → `automecanik-rag/knowledge/constructeurs/<slug>.md`).

Pour les **gammes**, le pivot est resté **bloqué** depuis le 2026-05-04 sur un arbitrage non-tranché documenté en mémoire `rag-to-wiki-sot-pivot-20260503.md` :

> Bloqueur Étape 6 gammes : script enricher pas générateur — arbitrage A (skeleton-generator DB) ou B (import legacy raw) requis next session

Les conséquences empiriques au 2026-05-06 :

- **0 / 143** wiki gamme files dans `wiki/exports/rag/gammes/` (vérifié `find ... -name "*.md"`)
- **143 / 143** RAG gamme files legacy pré-pivot dans `automecanik-rag/knowledge/gammes/` (auto-généré, jamais promu via canon)
- ADR-041 §2.B (acceptée 2026-05-06, vault PR #169) prévoit un backfill `r1s_safe_table_rows` × 143 slots **bloqué structurellement** : pas de SoT wiki à consommer

Cette ADR tranche l'arbitrage A vs B pour débloquer Étape 6 gammes.

## Mesures empiriques (2026-05-06)

### Couverture wiki SoT pour les 143 pg_aliases manquants

| Path | Coverage |
|------|----------|
| `automecanik-wiki/wiki/exports/rag/gammes/*.md` | **0 / 143** |
| `automecanik-wiki/wiki/gammes/**/*.md` | **0 / 143** |
| `app/backend/content/automecanik-wiki/wiki/gammes/` (mirror monorepo) | **0 / 143** |

### Provenance RAG gammes legacy (non-promus, hors SoT)

Distribution `last_enriched_by` sur les 143 slots manquants côté DB :

- 92 / 143 — `script:rag-enrich-from-web-corpus` (web-scraping auto)
- 29 / 143 — `skill:phase5-vague6` (skill auto)
- 13 / 143 — `script:materialize-db-to-md` (matérialisation auto)
- 9 / 143 — autres (`script:rag-fill-remaining-gaps`, `skill:phase5-vague6-final`, `skill:phase5-gates-skf-trw`, `skill:phase5-vague4`, `skill:phase5-hella-ngk`, `script:rag-enrich-metier-templates`)
- **0 / 143 — humain** (pas de `human:@*`, pas de `skill:` curaté humain)

92 + 29 + 13 + 9 = 143 ✓

Tous les fichiers ont `truth_level: L2` et `verification_status: draft`.

### Brands (référence Pattern B canon LIVE)

- 36 fiches dans `wiki/exports/rag/constructeurs/<slug>.md`
- Sync mirror LIVE via `scripts/cron/sync-rag-from-wiki.sh` (PR monorepo #288)
- D22 hook accept marker `synced-from-wiki:` (PR rag #14)

## Décision

### Pattern A retenu : skeleton-generator DB

Créer `scripts/wiki-generators/gamme-skeleton-generator.py` (monorepo) qui :

1. Lit `auto_pieces_gamme` Supabase pour les 232 gammes G1/G2 actives
2. Génère pour chacune une fiche **skeleton** dans `wiki/exports/rag/gammes/<pg_alias>.md` avec frontmatter Zod-conforme (ADR-039) :
   - `slug`, `pg_id`, `pg_name` (canon DB)
   - `category`, `truth_level: L2`, `verification_status: draft`
   - `lifecycle.last_enriched_by: script:gamme-skeleton-generator`
   - `domain.role` initialisé depuis colonnes DB ou laissé vide pour enricher downstream
   - `selection.criteria` skeleton (DB-derived ou vide)
3. L'enricher existant `gamme-from-web-corpus-generator.py` peut alors s'exécuter sur ces skeletons et ajouter `phase5_enrichment`
4. Cron `sync-rag-from-wiki.sh` mirror automatiquement vers `automecanik-rag/knowledge/gammes/<slug>.md` (déjà LIVE pour brands)
5. Une fois RAG mirror peuplé via canon wiki, l'agent `r1-content-batch` (workspace seo-batch) peut générer `r1s_safe_table_rows` proprement → ADR-041 §2.B se débloque naturellement

### Pattern B explicitement exclu (raison canon)

Le pattern B aurait consisté à importer les 241 gammes legacy depuis `automecanik-raw/recycled/rag-knowledge/gammes/` (déjà migrées byte-perfect via PR raw #15) vers `wiki/exports/rag/gammes/`.

Mémoire `feedback_no_bricolage_human_vs_auto_content` :

> Avant ingestion legacy, classifier humain (`skill:*`/`human:@*`) vs auto-généré (`script:*`/`r7-*`). Auto → raw ou regen, **JAMAIS proposals**. `proposals/` est zone curation humaine sacrée.

Or les 143 slots sont **0 humain, 143 auto**. Importer du contenu auto-généré pré-pivot dans `wiki/exports/rag/gammes/` reviendrait à le promouvoir comme s'il était canon-validé — violation de la règle humain-vs-auto. Le contenu legacy est conservé byte-perfect dans raw mais ne remonte pas vers wiki SoT.

### Architecture canon préservée

```
auto_pieces_gamme (DB)
    ↓ scripts/wiki-generators/gamme-skeleton-generator.py [NEW — Pattern A]
wiki/exports/rag/gammes/<slug>.md (skeleton, L2 draft, last_enriched_by=script:gamme-skeleton-generator)
    ↓ scripts/wiki-generators/gamme-from-web-corpus-generator.py (enricher EXISTANT — phase5)
wiki/exports/rag/gammes/<slug>.md (avec phase5_enrichment, toujours L2 draft)
    ↓ commit + push wiki main (humain ou CI)
    ↓ cron VPS DEV : sync-rag-from-wiki.sh (LIVE depuis 2026-05-04)
automecanik-rag/knowledge/gammes/<slug>.md (mirror, marker `synced-from-wiki:`)
    ↓ agent r1-content-batch (workspace seo-batch)
__seo_r1_gamme_slots.r1s_safe_table_rows (143 slots backfilled, ADR-041 §2.B)
```

## Conséquences

### Positives

- **Débloque 6 catégories** : gammes d'abord, puis pattern réplicable pour diagnostic / faq / policies / guides / reference (mêmes contraintes auto-content + DB source disponible)
- **Débloque ADR-041 §2.B** sans contournement : `r1s_safe_table_rows` peut être généré par l'agent canonique sur RAG mirror peuplé proprement
- **Préserve le canon humain-vs-auto** : pas de pollution `proposals/` par auto-content
- **Réutilise infrastructure** : enricher existant, cron LIVE, Pattern B canon (`exports/rag/**` tracked) — aucune dette nouvelle

### Négatives

- **Coût d'écriture** : un nouveau script Python (~200-300 lignes en miroir de `brand-fiche-generator.py`)
- **Délai pour 2.B** : skeleton-generator → enricher → cron sync → agent backfill, soit 4 étapes séquentielles avant que les 143 `r1s_safe_table_rows` soient écrits

### Risques résiduels

- Si `auto_pieces_gamme` colonne `pg_alias` ou `pg_name` contient des null / corruptions, le skeleton-generator doit fail-fast (pas créer de fichier wiki incomplet) → guard à inclure dans le script
- Si une gamme a un `pg_alias` qui collisionne avec un wiki `proposals/` humain pré-existant, le skeleton-generator doit refuser d'écrire (humain-priority) → guard à inclure

## Mise en œuvre

| Étape | Owner | Livrable | Cible |
|-------|-------|----------|-------|
| ADR-042 acceptance | @fafa | `status: accepted` + MOC-Decisions update | T+0 review |
| Skeleton-generator monorepo | dev | `scripts/wiki-generators/gamme-skeleton-generator.py` + tests | T+1 PR monorepo |
| Run sur 232 gammes | dev | `wiki/exports/rag/gammes/*.md` peuplé, commit wiki PR | T+1 PR wiki |
| Phase5 enricher run | dev | `phase5_enrichment` ajouté aux 232 fiches | T+2 PR wiki suite |
| Cron sync auto | LIVE | `automecanik-rag/knowledge/gammes/` peuplé via marker `synced-from-wiki:` | T+2 (cron horaire) |
| Agent r1-content-batch run | dev (workspace seo-batch) | 143 `r1s_safe_table_rows` écrits | T+3 |
| Vérification ADR-041 §2.B | mesure | `audit-r1-coverage.sql` Q1 → `has_safe_table = 169/169` | T+3 verification |

## Références

- ADR-031 — four-layer-content-architecture (cadre §D20/D22 pivot wiki=SoT)
- ADR-041 — R1 Router Posture Reaffirmed (§2.B débloqué par cette ADR)
- ADR-039 — Wiki frontmatter Zod canon (contrainte format skeleton)
- Mémoire `rag-to-wiki-sot-pivot-20260503.md` — pivot LIVE 36 brands, gammes blocker
- Mémoire `feedback_no_bricolage_human_vs_auto_content.md` — règle d'exclusion Pattern B
- Mémoire `feedback_canon_rule_live_iff_adr_accepted.md` — chantier `LIVE` ⟺ ADR `accepted`
- PRs précédentes pivot : monorepo #270/#275/#288/#292/#286, wiki #21/#22, rag #11/#13/#14
