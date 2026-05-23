---
id: ADR-079
title: "Product Media Control Plane — Operational Asset Truth Layer (extension ADR-058)"
status: accepted
date: 2026-05-23
decision_date: 2026-05-23
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: []
extends: [ADR-058]
related_adr: [ADR-058, ADR-062, ADR-066, ADR-072, ADR-076, ADR-078]
related_rules: []
related_incidents: [INC-2026-015]
reviewed_by: "@fafa"
---

# ADR-079 : Product Media Control Plane — Operational Asset Truth Layer

## Contexte

[[2026-05-23-pieces-media-img-corruption|INC-2026-015]] + [[ADR-078-pieces-media-img-recovery-tier-c|ADR-078]]
ont traité le symptôme (357 009 pièces affichées avec icône cassée → fallback `no.png`
via soft-hide + AVIF/4xx-cache fix). **Mais la cause architecturale demeure** : il
n'existe **aucune identité canonique du média** dans le système. `(folder, filename)`
sert d'identité — fragile, non dédupliquable, non versionnable, non rehydratable,
non migrable. Sans Media Control Plane, chaque future ingestion fournisseur peut
recréer l'incident sous une autre forme.

**9 manques structurels identifiés lors du recadrage post-incident** (formalisés
ci-dessous comme décision) — résumé :

1. Identité média canonique déterministe absente.
2. Pas d'état canonique du média (status enum manquant).
3. Provenance média implicite (« VALEO source ≠ TecDoc » découvert tardivement).
4. Resolver dispersé (`piece.images[0]` brut côté front/back).
5. Pas de Media Projection runtime (recalcul à chaque request).
6. Variants générées dynamiquement uniquement (coût CPU permanent).
7. Pas d'ingestion journal (impossible auditer/replay/comparer fournisseurs).
8. Quarantine status passif (pas de workflow).
9. Pas de stratégie cold storage / lifecycle tiers (explosion stockage future).

## Décision

**Construire un Media Control Plane canonique rattaché à [[ADR-058-repository-control-plane|ADR-058]]
comme « Operational Asset Truth Layer ».** Pas un « module images » : un layer
extensible aux PDFs techniques, schémas OEM, vidéos montage, renders IA, docs
fournisseurs, diagrammes électriques.

### 9 piliers architecturaux canonisés

**1. Identité média canonique déterministe**

Table `product_media_assets` avec :

```text
media_asset_id    = SHA-256(provider || ":" || canonical_source_id || ":" || binary_sha256)
                    encodé en hex 64 chars (cohérent ADR-066 catalog_signature, ADR-072 version_sha).
                    Collision-free assumption explicite : monorepo scope, SHA-256.
source_provider   = ref vers media_sources (pilier 3).
canonical_source_id = identifiant stable côté fournisseur (article ref, doc_id TecDoc, …).
canonical_hash    = SHA-256 du binaire source brut.
perceptual_hash   = pHash 64-bit (similarité visuelle cross-formats).
mime_type, width, height, byte_size.
storage_key       = chemin canonique dans le bucket runtime (pilier 9 hot tier).
status            = MediaStatus enum (pilier 2).
ingestion_run_id  = FK vers media_ingestion_runs (pilier 7).
asset_class       = enum (voir « Asset classes » ci-dessous).
access_policy     = `public | authenticated | customer` (RLS — voir G6 follow-up).
created_at, updated_at, deprecated_at.
```

Lien M:N via `product_media_links` :

```text
piece_id, media_asset_id, role (`main | gallery | diagram | logo | manual`),
display_order, locale (FR/EN/…), created_at.
PK = (piece_id, media_asset_id, role).
FK piece_id ON DELETE CASCADE ; FK media_asset_id ON DELETE RESTRICT (G4).
```

→ Permet dédup cross-fournisseurs, versionning, migration CDN, rehydratation,
replay pipeline, merge variants, cache stability.

**2. MediaStatus enum canonique**

```text
VERIFIED          → asset présent, hash matches, mime valid, dimensions OK.
MISSING_SOURCE    → upstream provider ne le sert plus (source 404 persistant).
MALFORMED         → binaire corrompu / mime mismatch / dimensions absurdes.
INGESTION_PENDING → upload en cours ou retry queue.
INGESTION_FAILED  → toutes tentatives échouées (dead-letter).
QUARANTINED       → bloqué workflow review humain (pilier 8).
```

Sans enum : `no.png` masque 6 cas distincts → impossible piloter qualité,
prioriser recovery, observer dérive fournisseur.

**3. Provenance registry**

Table `media_sources` (référence statique, gouvernée comme `.spec/00-canon/` L2) :

```text
provider          = `valeo-service-pro | skf-vsm | tecdoc | brand-bosch | ai-render | upload-manuel | ...`
ingestion_method  = `external-api | feed-zip | upload-manuel | render-ia | tecdoc-documents`
authoritative     = boolean (TRUE = source officielle du fournisseur).
priority          = int (1 = autorité primaire, fallbacks > 1).
asset_classes_supported = enum[] (un provider peut ne pas servir toutes les classes).
contract_url, credentials_env, observability_endpoint.
```

**Interdiction canonique gravée dans l'ADR** : « ne pas réessayer TecDoc pour
les images VALEO/SKF/MAGNETI sans suivre Brand Connect / VSM ». Le registre
porte cette contrainte, le resolver la respecte. Évite la re-incidence à 6
mois quand un autre agent retentera « réparer via TecDoc ».

**4. Resolver central — UNIQUE entry point**

```text
RPC resolve_piece_media(p_piece_id bigint, p_asset_class text DEFAULT 'product_image',
                        p_locale text DEFAULT 'fr')
RETURNS jsonb (main_media, thumbnail, avif, webp, status, placeholder)
```

Centralise priorité source, fallback, AVIF/WebP, status, quarantine,
placeholder, signed URL, observabilité, locale. Élimine la dispersion
actuelle (`piece.images[0]` brut côté front/back). **Voir G2 (ratchet
anti-`piece.images[0]`).**

**5. Media Projection runtime (séparation 3-tier)**

```text
Raw (sources fournisseur)
  → Canonical (product_media_assets, dédup-déterministe)
    → Projection runtime (media_projection)
```

Table `media_projection` matérialisée :

```text
piece_id, asset_class,
main_media_url, thumbnail_url, avif_url, webp_url, jpg_url, blurhash,
placeholder_url, status, locale, generated_at, source_run_id.
PK = (piece_id, asset_class, locale).
```

Régénérée par job BullMQ idempotent à chaque ingestion validée ou changement
de status. Lecture runtime = lookup PK = O(log n) cache-warm. Évite le
recalcul à chaque request, stabilise cache CDN, simplifie warming.

**6. Variant generation pré-calculée (modèle hybride)**

Variants critiques pré-calculées et stockées comme assets séparés (vs imgproxy
dynamique seul) :

| Variant | Format | Usage | Cible |
|---|---|---|---|
| `avif_800` | AVIF q80 | PDP, listing moderne | Chrome 85+ / Safari 16+ |
| `webp_800` | WebP q80 | PDP, listing fallback | Tous UA récents |
| `jpg_800` | JPG q85 | Legacy | UA très anciens |
| `thumb_240` | AVIF/WebP/JPG q75 | Listing dense, miniatures | Tous |
| `retina_1600` | AVIF/WebP q85 | PDP DPR 2x | Haute densité |
| `blurhash` | string 20-30 chars | LQIP skeleton SSR | Tous |
| `mobile_crop_600x600` | AVIF/WebP | Mobile carousel | Mobile |

**Hybride** = pré-calc pour ces 7 variants critiques + imgproxy pour cas
ad-hoc / non couverts (debugging, admin tools, one-off resize). Réduit coût
CPU récurrent, stabilise cache CDN (URLs déterministes), simplifie warming.

**7. Ingestion journal**

Table `media_ingestion_runs` :

```text
run_id (UUID), provider, started_at, completed_at, status (`running|success|failed|partial`),
raw_count, success_count, failed_count, quarantined_count, duration_ms,
source_snapshot (jsonb : URL/version flux, hash bundle source),
error_summary (jsonb : top-N erreurs catégorisées),
triggered_by (`cron | manual | webhook | replay`).
```

Chaque `product_media_assets.ingestion_run_id` y référence pour traçabilité
forensic complète. **Permet** : audit ingestion, replay run failed, rollback
logique (revert d'un run), comparaison fournisseurs (success rate, latency,
coverage).

**8. Quarantine workflow (pas juste l'enum)**

Workflow complet :

```text
(a) Triggers d'entrée → status = QUARANTINED :
    - MIME invalide (déclaré ≠ binaire)
    - Hash mismatch (canonical_hash change entre runs sans bump version)
    - Dimensions absurdes (< 50px ou > 10000px)
    - Binaire corrompu (parse failed)
    - NSFW classifier flag (futur)

(b) Dashboard review humain — UI admin (`/admin/media/quarantine`).

(c) Actions possibles :
    - REVALIDATE → re-fetch source, re-hash, transition VERIFIED si OK.
    - PURGE     → DELETE asset, status_history conserve trace.
    - RELEASE   → manual override, status = VERIFIED (audit logged).

(d) SLA : entries en QUARANTINED > 30j → alerte ops.
```

Sans workflow, le status reste passif et la quarantaine s'accumule sans
cycle de vie.

**9. Cold storage / lifecycle tiers**

Stratégie 3 tiers explicite (sans tiers : explosion stockage = variants ×
asset_classes × originals × locales) :

| Tier | Storage | Usage | TTL invalidation | Coût |
|---|---|---|---|---|
| `hot` | Supabase `rack-images` (current) | media_projection + variants actifs | court (5min sur fallback) | $$$ |
| `warm` | Supabase `rack-images-warm` (nouveau bucket) | originals + variants peu accédés | 1 an immutable | $$ |
| `cold` | Cloudflare R2 ou Supabase archive | anciens assets (`deprecated_at` > 90j) | infini, retrieval fee | $ |

Migration hot → warm = job BullMQ basé sur `last_accessed_at` (telemetry).
Migration warm → cold = trigger sur `deprecated_at IS NOT NULL AND age > 90j`.

### Asset classes (généralisation au-delà des images)

L'« Asset Truth Layer » n'est pas « images uniquement ». Le modèle supporte
dès le départ :

```text
asset_class enum :
  product_image         → photo produit standard
  technical_pdf         → notice technique, fiche fournisseur
  wiring_diagram        → schéma électrique
  installation_video    → vidéo montage MP4/WebM
  ai_render             → render IA généré (provider = render-ia)
  supplier_document     → document juridique/commercial fournisseur
```

Sans cette généralisation au design, le système dérivera implicitement vers
« images only » et chaque nouvelle classe nécessitera un refactor schéma
(anti-pattern direct).

### Discipline 404 SEO (point critique)

Séparation stricte par type de ressource :

| Ressource | HTTP attendu | Cache-Control |
|---|---|---|
| Endpoint image absente (`/rack/21/INEXISTANT.JPG`) | **404** (via imgproxy + Caddy) | `max-age=300, must-revalidate` |
| Page produit HTML (`/pieces/.../...html`) | **200 obligatoire** ([[ADR-076-soft-404-r2-strategy|soft-404 R2]] inchangé) | inchangé |
| Placeholder image servi par CDN | **200 explicite** | `max-age=300` |

Sans cette séparation : multiplication massive de 404 crawlées sur les endpoints
images → pollution crawl budget GSC. Le P1 (PR monorepo #702) touche QUE les
endpoints images ; les pages produits restent gérées par [[ADR-076-soft-404-r2-strategy|ADR-076]].

---

## Stratégie de migration / coexistence (G1)

Migration de `pieces_media_img` (9,6 M lignes legacy) vers le nouveau modèle :

```text
T0  : Freeze writes legacy `pieces_media_img.{pmi_folder, pmi_name}`.
      Garde mécanique : ast-grep rule bloquant tout INSERT/UPDATE sur ces
      colonnes hors migration officielle (sister-rule de G2 ci-dessous).

T0+ : Backfill `product_media_assets` + `media_projection` depuis les lignes
      bien-formées de `pieces_media_img` (folder + name avec extension valide).
      Job BullMQ batch, par marque. Stats per-batch dans media_ingestion_runs.
      Soft-hidden P1 (1,1 M lignes) reste display='0' jusqu'à recovery brand-media.

T0..T+3 mois : Dual-read via resolver. Resolver tente d'abord
               product_media_projection ; si miss, fallback lecture
               pieces_media_img (sentinel telemetry counter `legacy_fallback_hit`).

T+3 mois : Audit telemetry — si `legacy_fallback_hit_rate < 0.1%` sur 14j
           consécutifs, déclencher Phase de deprecation.

T+3-6 mois : Deprecation phase — supprimer le fallback legacy dans le
             resolver (resolver renvoie placeholder si miss). Ratchet G2
             devient `error` (bloque tout caller direct restant).

T+6 mois : DROP TABLE pieces_media_img après vérification audit
           `legacy_fallback_hit_rate == 0` sur 30j + zero grep refs en codebase.
           Backup table conservée 90j puis archivée cold tier.
```

Sans ce paragraphe, P3 partira et la legacy restera éternelle.

## Resolver deprecation timeline + ratchet anti-`piece.images[0]` (G2)

**Interdiction canonique** : aucune lecture runtime ne doit accéder à
`pieces_media_img.{pmi_folder, pmi_name}` ni à `piece.images[0]` brut.

**Ratchet ast-grep** (sister de `supabase-js-bulk-select-paginate.yml`,
déjà livré P1 INC-2026-015) :

```yaml
id: no-direct-piece-media-access
language: typescript
severity: warning  # Phase 1 — observe baseline + ratchet vers error post-migration G1
message: |
  Direct access to pieces_media_img.{pmi_folder,pmi_name} or piece.images[*]
  bypasses the canonical resolver `resolve_piece_media(piece_id)` (ADR-079).
  See migration G1 for deprecation timeline. Replace with resolver call.
rule:
  any:
    - pattern: $X.pmi_folder
    - pattern: $X.pmi_name
    - pattern: $PIECE.images[$IDX]
ignores:
  - backend/src/modules/media/**  # le resolver est lui-même autorisé
  - scripts/migration/**          # scripts one-shot de backfill
```

Promu `severity: error` après T+3 mois (Phase de deprecation G1).

## Identité déterministe — spec hash explicite (G3)

```text
media_asset_id = sha256_hex(
  provider_id || ":" || canonical_source_id || ":" || binary_sha256
)
```

- **Algorithme** : SHA-256 (cohérent ADR-066 `catalog_signature`, ADR-072
  `version_sha`, déjà infra interne).
- **Encodage** : hex bas 64 chars (utilisable directement en URL et clé Redis).
- **Collision handling** : SHA-256 considéré collision-free dans le scope
  monorepo. Assertion explicite dans ADR, pas implicite. Si collision
  empirique constatée un jour → upgrade SHA-3-256 via ADR amend.

## Orphan cleanup / cascade policy (G4)

```text
1. Cascade FK sur product_media_links :
   - piece_id ON DELETE CASCADE (la pièce supprimée = ses liens disparaissent).
   - media_asset_id ON DELETE RESTRICT (un asset référencé ne peut être DROP).

2. Orphan asset detection (job nightly) :
   - Asset avec 0 link actif depuis > 30j → status = MISSING_SOURCE + soft-archive (move warm tier).
   - Asset orphelin depuis > 90j → migration cold tier (Cloudflare R2 archive).
   - Asset orphelin depuis > 365j → DELETE après vérification audit logs (purge GDPR-aware).

3. Quarantined asset retention :
   - QUARANTINED entries → flag review SLA 30j (pilier 8).
   - Pas de purge auto — humain décide PURGE ou RELEASE.
```

## Idempotency spec ingestion (G5)

Worker ingestion (BullMQ) :

```text
1. Dedup par canonical_hash :
   - Pre-check : asset exists with same (provider, canonical_source_id, canonical_hash)
     → skip (telemetry `ingestion.dedup_hit`), no DB write.

2. Idempotency key = (provider, canonical_source_id, run_id) :
   - At-least-once processing OK ; retry de la même job ne crée pas de duplicate.

3. Hash mismatch entre runs (canonical_change detected) :
   - Si asset exists with same (provider, canonical_source_id) MAIS canonical_hash diff
     → quarantine new version, conserve ancienne VERIFIED, alerte ops.
   - Le humain décide : RELEASE new (update asset + bump version), ou PURGE new.

4. Run state machine :
   running → success | failed | partial
   À chaque batch terminé, update success_count/failed_count/quarantined_count
   atomiquement. Si crash : run reste `running` jusqu'au cron stale-detector
   (T+1h) qui marque `failed` + déclenche retry idempotent.
```

Sinon re-ingestion = duplicates silencieux ou updates qui écrasent le canon.

---

## Conséquences

**Bénéfices** :
- Identité média stable, dédupliquable cross-fournisseurs, rehydratable.
- 6 cas de statut explicites pilotables (vs `no.png` masquant tout).
- Provenance fournisseur explicite empêchant re-incidence INC-2026-015.
- Resolver unique simplifie front+back, ratchet anti-dispersion.
- Projection runtime stable cache CDN, perf P95 < 50ms cohérent ADR-072.
- Variants pré-calculées réduisent coût CPU imgproxy ~70%.
- Ingestion auditable, replayable, comparable inter-fournisseurs.
- Quarantaine avec workflow → pas d'accumulation passive.
- Cold storage tiers évite explosion stockage long-terme.
- Asset classes généralisées extensibles aux PDFs/vidéos/diagrammes.
- 404 SEO discipline protège crawl budget.

**Coûts / limitations** :
- Schéma DB nouveau + migration legacy 9,6 M lignes : effort P3 estimé ~4 sprints.
- Coexistence resolver + lecture directe pendant 3-6 mois (telemetry-driven).
- Variants pré-calculées = storage supplémentaire (chiffré dans pilier 9 cold
  tier strategy).
- Apprentissage : tous les consommateurs (front Remix, back NestJS, batch SEO)
  doivent migrer vers le resolver. Documenté dans la migration G1.

**Risques explicitement traités** :
- Collisions SHA-256 → assertion canon + plan d'amend SHA-3-256.
- Orphan accumulation → policy nightly G4.
- Re-ingestion duplicates → idempotency spec G5.
- TecDoc retentée à tort pour VALEO → interdiction registry pilier 3.
- 404 crawl pollution → discipline SEO `endpoint image=404 / page=200`.
- Dérive « images only » → asset classes généralisées dès design.

## Follow-ups (TIER 2, à scoper en PR séparée P3)

- **G6. RLS / security model par asset_class** — colonne `access_policy`
  (`public | authenticated | customer`) + RLS Supabase pour `wiring_diagram`,
  `technical_pdf` customer-restricted. À spécifier au schéma initial mais
  enforcement RLS peut suivre.

- **G7. Compat soft-404 R2 ([[ADR-076-soft-404-r2-strategy|ADR-076]])** — la
  page soft-404 R2 utilise des thumbnails pour les alternative vehicles
  (`NoProductsAlternatives`). P3 doit s'assurer que le resolver couvre
  AUSSI ces thumbnails. Cross-ref dans ADR-076 amend si besoin.

- **G8. SLO + ratchet CI** :
  - `resolve_piece_media` RPC P95 < 50 ms (cohérent ADR-072 R2 runtime read).
  - Projection refresh P95 < 5 min per provider.
  - Ingestion throughput ≥ 10k assets/min en steady-state.
  - Gate CI = ratchet régression sur baselines instrumentées.

## Roadmap

| Phase | Livrable | Owner | Timeline |
|---|---|---|---|
| **P1** ✅ MERGED (#699) | Tier C soft-hide + gardes structurelles | dev | 2026-05-23 |
| **P1.5** ✅ MERGED (#702) | AVIF auto-negotiation + 4xx cache fix | dev | 2026-05-23 |
| **P2** ✅ Cette ADR | Canon Media Control Plane | governance | 2026-05-23 |
| **P3** | Schéma DB + RPC resolver + projection runtime + migration G1 | dev | T+4 sprints |
| **P3.5** | Frontend/back migration vers resolver + ratchet G2 → error | dev | T+6 sprints |
| **P4** | Media Quality Dashboard + KPIs business | ops | T+8 sprints |

**P3 gating** : ne démarre qu'après cette ADR acceptée + migration script G1
prête. Sans gating, le schéma DB divergera de l'ADR.

## Anti-régressions canonisés

| Régression | Garde |
|---|---|
| `piece.images[0]` brut runtime | ast-grep `no-direct-piece-media-access` (G2) |
| Bulk reads non paginés sur pieces_media_img | ast-grep `supabase-js-bulk-select-paginate` ✅ déjà livrée (ADR-078) |
| `pmi_folder=''` en displayed | audit nightly `audit-pieces-media-img-invariants.sh` ✅ déjà livré |
| imgproxy fallback HTTP 200 cached 1 an | IMGPROXY_FALLBACK_IMAGE_HTTP_CODE=404 + Caddy handle_response ✅ livré P1.5 |
| Re-tentative TecDoc pour VALEO images | provenance registry pilier 3 (interdiction explicite) |
| Schéma dérive vers images-only | asset classes généralisées dès design |
| Collision media_asset_id | SHA-256 assertion canon + amend path |

## Cross-refs

- **Étend** : [[ADR-058-repository-control-plane|ADR-058]] (« Operational Asset
  Truth Layer » comme extension de l'overlay L2).
- **Cohérence** : [[ADR-062-repository-contract-system-meta-model|ADR-062]]
  (les 9 piliers respectent les 9 conformity criteria — contrat humain-édité,
  generator déterministe, derived projetée, engine appliqué, gate verrouille,
  ratchet promeut, owner valide, semver versionne, anti-parallel-truth).
- **Sister patterns** : [[ADR-066-r2-content-composition-v2|ADR-066]]
  catalog_signature (gate structurel), [[ADR-072-r2-cqrs-ddd-snapshot-artifact|ADR-072]]
  CQRS published snapshot pattern.
- **Compat** : [[ADR-076-soft-404-r2-strategy|ADR-076]] soft-404 R2
  (thumbnails alternatives migration G7).
- **Origine** : [[ADR-078-pieces-media-img-recovery-tier-c|ADR-078]] + [[2026-05-23-pieces-media-img-corruption|INC-2026-015]].

Self-review verdict: APPROVE
