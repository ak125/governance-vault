---
type: audit-trail
date: 2026-05-08
session_id: seo-r2-thin-content-forensic-2026-05-07-08
domain: seo-r2-pieces
related_knowledge:
  - "seo-pieces-r2-thin-content-investigation-20260507"
  - "seo-traffic-drop-investigation-20260426"
related_incidents:
  - "2026-05-06-cf-cache-poisoning-pieces-5xx"
related_adrs:
  - "ADR-016-vehicle-page-matview-persistence"
  - "ADR-022-r8-rag-control-plane"
  - "ADR-026-content-separation"
  - "ADR-031-canonical-framework"
related_prs:
  - "ak125/governance-vault#218"
status: shipped
verdict: ROOT_CAUSE_IDENTIFIED
---

# SEO R2 thin content — forensic livré, décisions en attente (2026-05-07/08)

> Session 2026-05-07 22:10 UTC → 2026-05-08 14:00 UTC. Investigation déclenchée
> par observation utilisateur d'une chute de trafic le 2026-05-07. GA4 et GSC
> consultés en live (clés service-account du backend, pas de MCP). Forensic
> publié dans le vault knowledge, voie canon validée, implémentation différée.

## 1. Question d'entrée

L'utilisateur observe une chute de trafic sur `automecanik.com` le 2026-05-07.
La session démarre par un diagnostic empirique côté DB (Supabase) puis bascule
sur les API Google quand le besoin s'est précisé.

## 2. Évidence empirique collectée

### GA4 live (property `311870207`)

Connexion via `google-analytics-data` lib + creds backend `GA4_*` dans
`backend/.env`. Comparaison 14 jours :

| Métrique | 2026-05-07 | Moyenne 14j (hors 06/05) | Variation |
|---|---|---|---|
| Sessions total | 158 | ~241 | −34 % |
| **Organic Search** | **33** | ~64 | **−48 %** |
| Direct | 125 | ~191 | −34 % |

Realtime 30 min : 2 active users (1 FR, 1 MM). Confirme un creux réel.

### GSC live (property `sc-domain:automecanik.com`)

Connexion via `googleapiclient` + creds backend `GSC_*`. Sample 15 URLs
aléatoires de `sitemap-pieces-1.xml` (50 000 URLs) :

| Verdict | Nombre | % |
|---|---|---|
| Submitted and indexed | 4 | 27 % |
| Crawled - currently not indexed | 10 | 67 % |
| URL is unknown to Google | 1 | 7 % |

Pages PASS = marques majeures (Renault 140, Peugeot 128, VW 173, Seat 147).
Pages NOT INDEXED = marques secondaires (Mercedes 108, Dacia 47, Skoda 150,
Mini 113, Citroën 46), `lastCrawlTime` distribué entre 2025-11 et 2026-03.

Top 10 URLs par clicks 7 jours : 0 URL `/pieces/*` dans les 9 premières
positions, dominé par `/blog-pieces-auto/conseils/*` et home. 1 seule
`/pieces/*` à 3 clicks (capteur-abs Peugeot 128).

GSC Performance API a J−3 de retard normal — données 04/05 dispos, pas 07/05.
État de validation GSC pour les 30 400 pages 5xx : **Commencé 2026-05-06**
(jour du fix INC-2026-005-recurrence).

### Diff HTML 4 variantes du même triplet (gamme×marque×modèle)

URLs : alternateur × Renault Laguna II 140028, 4 type_id différents :

| type_id | bytes | text | md5 | meta description | desc len |
|---|---|---|---|---|---|
| 15473 (1.6 16V Phase 1) | 230 KB | 9 325 | 794f6214 | `Alternateur RENAULT LAGUNA II,` | 30 |
| 18681 (1.6 16V Phase 2) | 193 KB | 8 787 | eddfe046 | `Alternateur RENAULT LAGUNA II,` | 30 |
| 18214 (1.9 dCi) | 224 KB | 8 979 | c88303cf | `Alternateur RENAULT LAGUNA II,` | 30 |
| 18579 (1.9 dCi) | 226 KB | 9 065 | 393ca138 | `Alternateur RENAULT LAGUNA II,` | 30 |

Quatre meta descriptions strictement identiques, 30 caractères, sans
mention du moteur/cylindrée/année/puissance/fuel. Le sitemap contient 18
variantes type_id pour ce seul triplet → 18 pages avec la même meta.

## 3. Cause racine

Migration `20260128_get_pieces_for_type_gamme_v4_raw_seo.sql` (2026-01-28)
a déplacé le SEO templating SQL→NestJS pour gagner TTFB 10 s→1 s. Commentaire
explicite de la migration : *« V3 calls process_seo_template() 5 times. V4
returns RAW templates without processing. NestJS handles processing with
Redis cache »*. Le receveur NestJS n'a jamais été implémenté à la hauteur
de V3. `backend/src/modules/rm/services/rm-builder.service.ts:554,671`
retourne `seo: { h1:'', title:'', description:'', content:'', preview:'' }`
fallback. Le seul enrichissement vivant côté R2 est le pool
`SEO_PRICE_VARIATIONS` (7 modifiers cosmétiques rotation `(typeId+pgId) % 7`)
défini dans `backend/src/config/seo-variations.config.ts`.

R8 (`/constructeurs/*`) a un système symétrique mais riche (37 templates
ADR-022 Pilier 2b avec placeholders {brand} {model} {type} {power} {fuel}
{year_from} {year_to} {engine_code} {families_count}, services
`r8-vehicle-enricher.service.ts` complet, RAG vehicle frontmatter parsing).
R2 n'a aucun équivalent. Aucun fichier `r2-pieces-enricher.service.ts`
n'existe dans le monorepo.

## 4. Inventaire récupération

50+ tables `__seo_*` legacy dorment **intactes** dans le schema `_archive`,
non écrasées :

| Table | Rows | Contenu |
|---|---|---|
| `_archive.__seo_lexique_matrice` | 221 | 1 par gamme : verbes/lexique/symptômes/pièces associées |
| `_archive.__seo_vehicle_granularity_patterns` | 34 | patterns granularité véhicule |
| `_archive.__seo_variable_patterns` | 4 | substitutions variables |
| `_archive.__seo_keywords_clean` | n/a | mots-clés normalisés |
| `_archive.__seo_zone_*` (3 tables) | n/a | poids zones SEO |
| `_archive.__seo_subsystem_*` (4 tables) | n/a | sous-systèmes |
| `_archive.__seo_action_definitions` + 40 autres | n/a | système legacy complet |
| `_archive.orphans_gamme_content_2026_04_21` | 88 | snapshots `__seo_r1_gamme_slots` orphelins |
| `_archive.content_quality_fixes_2026_04_21` | 418 | snapshots pre-Q2/Q3 fix accents/titres |

Tables encore en `public` mais non lues par R2 :
- `__seo_gamme_conseil` (2 790 rows HTML riche, quality_score 80-87) — alimente R3 hub blog
- `__seo_r1_gamme_slots` — alimente R1
- `__seo_gamme_purchase_guide` (241 rows, 65 colonnes)

Récupération triviale par `INSERT … SELECT FROM _archive.…`. **Aucun PITR
ni Wayback Machine nécessaire.** L'écrasement supposé n'a jamais eu lieu —
le pipeline a été simplement débranché.

## 5. Voie canon (sans bricolage) — 3 axes

Détaillée dans le knowledge `seo-pieces-r2-thin-content-investigation-20260507`.
Synthèse :

1. **Restauration `_archive` → `public`** des tables critiques (lexique
   matrice, granularity patterns, variable patterns). Petit PR DB, low risk.
2. **Implémentation `r2-pieces-enricher.service.ts`** calqué sur
   `r8-vehicle-enricher.service.ts`. Définir `SEO_R2_*_VARIATIONS` dans
   `seo-variations.config.ts` (équivalent ADR-022 Pilier 2b pour R2). C'est
   l'effort principal — débloque l'indexation durable.
3. **Hardening permanent** : DB `CHECK (length(meta_description) BETWEEN
   130 AND 200)` + CI lint zéro duplicate intra-modèle + ADR snapshot
   pré-migration obligatoire. Préviens la régression future.

## 6. Livrables produits dans cette session

| Artefact | Path | Statut |
|---|---|---|
| Forensic vault knowledge | `ledger/knowledge/seo-pieces-r2-thin-content-investigation-20260507.md` | MERGED PR #218 commit `ca703cba` |
| Lien MOC-Knowledge | `ops/moc/MOC-Knowledge.md` section *Investigations & honest debriefs* | MERGED |
| Mémoire Claude project | `~/.claude/.../memory/seo-r2-thin-content-root-cause-20260507.md` | indexée |
| Mémoire Claude feedback | `~/.claude/.../memory/feedback_check_archive_schema_first.md` | indexée |
| Mémoire Claude feedback | `~/.claude/.../memory/feedback_perf_migration_must_honor_contract.md` | indexée |
| Audit-trail entry (ce fichier) | `ledger/audit-trail/2026-05-08-seo-r2-thin-content-forensic-and-decisions-pending.md` | en cours |

## 7. Décisions en attente (next session)

Aucune action de fix n'a été lancée. L'utilisateur a explicitement scopé
cette session à l'**investigation seule**. Quatre options ouvertes :

1. **Surveillance court terme** — courbe GA4/GSC à J+3 (10/05), J+7 (13/05),
   J+14 (20/05) pour valider la récupération de la cause aiguë
   (INC-2026-005-recurrence) avant tout autre changement.
2. **Élargir le forensic** — sample URL Inspection 200+ URLs (quota 2 000/j
   disponible) pour quantifier la distribution des verdicts par marque ×
   gamme × count produits. Augmente la confiance avant ré-architecture R2.
3. **Lancer Axe 1 récupération `_archive`** — petit PR DB, low risk,
   débloque les axes 2 et 3.
4. **Lancer Axe 2 implémentation R2 enricher** — chantier principal,
   nécessite scope dédié et probablement un ADR séparé pour formaliser le
   pattern (calqué sur ADR-022 Pilier 2b R8).

Recommandation : commencer par 1 (surveillance) en parallèle de 2
(forensic élargi) pour distinguer empiriquement la part transitoire (INC)
de la part chronique (R2 thin content) avant d'engager les axes
d'implémentation.

## 8. Patterns canonisés cette session

- **Vérifier `_archive` schema avant de proposer une refonte** — 50+ tables
  trouvées intactes alors qu'on s'apprêtait à proposer un nouveau pipeline.
  Memory Claude `feedback_check_archive_schema_first.md` créée.
- **Migration perf qui déplace processing entre couches doit honorer le
  contrat dans le même sprint** — la migration TTFB 28/01 a cassé 4 mois
  d'indexation Google sans signal d'alerte. Memory Claude
  `feedback_perf_migration_must_honor_contract.md` créée.
- **Connexion API live > tables ingérées** — la table `__seo_ga4_daily`
  s'arrêtait au 04/05 (cron arrêté), mais GA4 API live a renvoyé 2026-05-07
  immédiatement. La table DB n'est pas la source de vérité pour le « today ».
- **Trois agents Explore en parallèle, mais validation manuelle obligatoire** —
  l'agent #3 a affirmé « 100 % pages title=0 » qui était empiriquement faux
  (curl Googlebot a montré titles + meta + JSON-LD partout). Cf. memory
  existante `feedback_verify_file_state_not_agent_summary.md`.

## 9. Limites de la session

- Sample URL Inspection 15 URLs uniquement (élargir à 200+ pour stats
  fiables sur distribution marque × gamme × produits)
- Pas vérifié si la fonction SQL `process_seo_template()` V3 existe encore
  en parallèle (peut être restaurable comme fallback transitoire si oui)
- GSC Performance API a J−3 lag normal, donc clicks 05/06/07 mai pas
  mesurables avant 10/05
- MCP `seo-analytics` (workspace `ec5ac33c`) jamais activé — connexions
  GA4/GSC faites via lib Python directe avec creds backend

## 10. Liens

- PR vault mergée : https://github.com/ak125/governance-vault/pull/218
- Forensic knowledge : `ledger/knowledge/seo-pieces-r2-thin-content-investigation-20260507.md`
- Incident parent transitoire : `ledger/incidents/2026/2026-05-06-cf-cache-poisoning-pieces-5xx.md`
- Audit antérieur INSUFFICIENT_EVIDENCE : `ledger/knowledge/seo-traffic-drop-investigation-20260426.md`
