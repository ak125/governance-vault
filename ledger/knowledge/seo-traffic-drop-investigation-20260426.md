---
type: knowledge
status: canon
created: 2026-04-26
updated: 2026-04-26
tags: [seo, traffic, investigation, honest-debrief, partial-coverage]
related-incidents: [INC-2026-005, INC-2026-012]
related-prs: [monorepo#133, monorepo#134, monorepo#135, monorepo#136]
related-tags: [v2026.04.23-gsc-404-tecdoc-fix]
verdict: INSUFFICIENT_EVIDENCE
---

# SEO traffic drop investigation — 2026-04-26 (honest debrief)

## Contexte

User Fafa signale une chute de trafic SEO **depuis 25/04**. Investigation menée
le 2026-04-26 soir sans accès direct GSC depuis la session main (workspace
`seo-analytics` MCP non chargé).

## Section 1 — Scope scanné

| Item | Source | Resultat |
|---|---|---|
| Dernier deploy PROD | `git tag --sort=-creatordate` | `v2026.04.23-gsc-404-tecdoc-fix` (23/04 18:47). **Aucun deploy PROD entre 23/04 et 26/04**. |
| Status URLs canoniques (12 URLs) | curl prod `https://www.automecanik.com` | **200 OK partout** (gammes core + 7 marques major). Avec `.html` + IDs DB réels. |
| 5xx PROD | `__error_logs` 7j | **3 erreurs en 7j** — quasi-zéro. |
| 404/410 logs | `__error_logs` 7j | spike 7 909 (23/04 = jour deploy) → 72 (26/04). **0 ligne `err_status=410`** (filtre log probable). |
| Volume `__error_logs` total | DB | 10 342 (23/04) → 1 006 (26/04). NB : c'est du log d'**erreur**, pas du trafic. Baisse cohérente avec stabilisation post-fix. |
| Sitemap shards | curl `sitemap-*.xml` | **fonctionnel** : 50k+50k+2 395 pieces, 1 008 véhicules, 36 brands, 231 reference, 330 blog. `<lastmod>2026-04-23</lastmod>` partout. |
| Sitemap purge PR #136 (migration N2) | `__sitemap_p_link` | **NON exécutée** — 99 912 rows / 3 545 type_ids `100001-134362` toujours en DB. Filtrés au moment XML par PR #135. |
| Traffic interne `seo_link_impressions` | DB 14j | **Lundi 26/04 : 241 sessions vs Lundi 21/04 : 397 → -39%**. Un seul point de comparaison. |

## Section 2 — Erreur d'analyse reconnue

Première passe : claim "**catastrophe SEO** — toutes pages R3/R7/R8 en 410/404".
**Faux**. J'ai testé avec des **IDs marques inventés** (renault-128 au lieu de
renault-140, peugeot-94 au lieu de peugeot-128, etc.). Avec les vrais IDs
canoniques DB, **toutes les pages testées renvoient 200**.

User a corrigé sur le vif (`vous racontez des conneries, ça fonctionne, il faut
le .html à la fin`). Reset effectué. Pattern d'erreur classique = **inventer une
convention sans grep préalable** — exactement ce que `feedback_verify_existing_first`
en mémoire interdit. Re-violation 4ᵉ fois en 1 mois.

## Section 3 — Ce qui n'a PAS été scanné

- **GSC réelles** : `__seo_gsc_daily` partitions 04/05/06 toutes vides. Aucune
  ingestion Google Search Console côté DB. **Source d'observation user inconnue**.
- **Crawl Googlebot** : `__seo_crawl_log` table vide (0 ligne). Aucune trace
  serveur Googlebot capturée.
- **Rendu réel** des pages : seul le status code HTTP a été vérifié. Une
  régression RLS post-PR-#102→#121 pourrait laisser des pages **200 mais vides**
  (anon role bloqué sur certaines tables).
- **Core Web Vitals** post-deploy non mesurés.
- **Canonical / JSON-LD / robots meta** non audités sur les pages live.
- **GA4** non interrogé.

## Section 4 — Hypothèses crédibles (NON PROUVÉES)

1. **Effet retardé INC-2026-005** (30,5k 5xx historiques, fix ADR-016 livré
   20/04). Google met des semaines à reindex après reprise.
2. **PR #134 (404→410)** trop agressif. Les URLs `100001-134362` orphelines V1
   généraient peut-être un trafic résiduel marginal pré-410. Bascule de
   "flotte autour de l'index" → "désindex en semaines" cohérente avec un
   tassement court terme.
3. **Sitemap `lastmod=2026-04-23`** sur tous les shards. Si le ping sitemap
   n'a pas été poussé après cette date OU si la regen quotidienne n'a pas
   tourné depuis 3 jours, baisse de fraîcheur.
4. **Cumul des 9 PRs RLS Security** (vagues 2a→4b) merged dans `v2026.04.23`.
   Si une policy anon est trop restrictive, certaines lectures publiques
   (catalog, blog, SEO) peuvent retourner des résultats vides côté SSR.

## Section 5 — Reste à faire (non démarré)

### A. Sourcer le signal user

- [ ] Demander à user **où** la chute est observée :
  GSC `Performance > Last 28 days` ? GA4 ? Sentry ? Autre ?
- [ ] Magnitude exacte : -X% impressions, -X% clicks, -X% sessions ?
- [ ] Périmètre : toutes pages ou un cluster (R1 / R3 / R7 / R8) ?
- [ ] Date exacte de rupture (24/04 ? 25/04 matin ? autre ?).

### B. Brancher GSC sur DB

- [ ] Activer la session MCP `seo-analytics` (workspace `ec5ac33c`) pour
      requêter GSC depuis la session main, OU restaurer l'ingestion
      `__seo_gsc_daily` (cron / endpoint admin à identifier).
- [ ] Vérifier l'état de l'ingestion `__seo_crawl_log` (Googlebot middleware
      probablement désactivé ou breaker ouvert).

### C. Tests de rendu (pas seulement status)

- [ ] curl 30 URLs canoniques + grep : présence H1 / breadcrumb / au moins
      un produit / canonical correct / pas de "no items" / JSON-LD valide.
- [ ] Tester en `User-Agent: Googlebot` (différence rendu / fetch RSC).
- [ ] Spot-check anon-role sur tables RLS migrées : `pieces`, `auto_marque`,
      `auto_modele`, `auto_type`, `__seo_*`.

### D. Ping sitemap

- [ ] Vérifier la date de dernière `regen sitemap` côté backend
      (cron / endpoint `/api/sitemap/v10/...` — **NE PAS trigger sans go user**
      cf. `feedback_sitemap_no_trigger`).
- [ ] Confirmer que `<lastmod>` se met à jour quand la DB bouge.

### E. Décision PR #136 migration N2 (purge orphans)

- [ ] Décider avec user si on **exécute** la migration archive+purge sur
      `__sitemap_p_link` (-99 912 rows / -3 545 type_ids orphelins).
      Aujourd'hui filtrés au XML mais polluent la table.

## Section 6 — Coverage manifest (contrat de sortie)

```yaml
scope_requested:        "diagnostiquer chute trafic SEO depuis 25/04"
scope_actually_scanned: "deploy git, status code 12 URLs canoniques, __error_logs 7j,
                         sitemap shards counts, __sitemap_p_link cohorts,
                         seo_link_impressions 17j, robots.txt diff, code review
                         PR #133/#134, $.tsx + checkIfOldLink, pieces.$slug.tsx"
files_read_count:       4 (CLAUDE.md hooks, $.tsx 240 lignes, pieces.$slug.tsx 50 lignes,
                          MOC-Knowledge.md)
db_queries_run:         15 (info_schema, sitemap counts, error_logs, gsc_daily empty,
                            crawl_log empty, link_impressions, brand IDs, pg IDs)
external_smoke_tests:   25+ curl HTTPS prod
excluded_paths:         "frontend rendering, JSON-LD, canonical tags, RLS anon-role
                         tests, GA4, GSC dashboards, CWV measurements"
unscanned_zones:        "GSC depuis MCP seo-analytics non activée ;
                         crawl_log + gsc_daily ingestion vides ;
                         rendering live pages ;
                         RLS anon impact post-vagues"
corrections_proposed:   0 (aucun fix appliqué)
corrections_applied:    0
validation_executed:    "smoke tests HTTPS prod uniquement"
remaining_unknowns:
  - "Source du signal user (GSC ? GA4 ?) — bloque toute conclusion"
  - "Magnitude réelle (% baisse + cluster + dates précises)"
  - "Pourquoi __seo_gsc_daily est vide depuis 04/2026"
  - "Pourquoi __seo_crawl_log est vide"
  - "Si rendu pages 200 OK contient bien le contenu (pas de RLS empty rows)"
final_status:           INSUFFICIENT_EVIDENCE
```

## Section 7 — Liens

- Tag PROD : `v2026.04.23-gsc-404-tecdoc-fix`
- PRs concernés monorepo : #133, #134, #135, #136
- Memory Claude :
  - `feedback_verify_existing_first` (re-violation 4ᵉ)
  - `feedback_sitemap_no_trigger`
  - `adr-016-vehicle-page-cache`
  - `incident-redis-bsi-20260422` (firewall actif)
- Vault associés :
  - [[ADR-016-vehicle-page-matview-persistence|ADR-016]]
  - [[r8-rag-control-plane-design-20260423]]
- Session log monorepo : `log.md` entrée 2026-04-26
