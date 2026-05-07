---
id: ADR-051
title: "Frontend bundle budget enforcement — signal-proven baseline via `bundle-top10.json`"
status: accepted
date: 2026-05-07
decision_date: 2026-05-07
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "Q1"]
related_incidents: ["PR-382-rejected-arbitrary-budget-recalibration-2026-05-07"]
related_adr: []
implementation_status: phase-1-baseline-shipped-2026-05-07
---

# ADR-051 — Frontend bundle budget enforcement : `bundle-top10.json` signal-proven baseline

## Contexte

Le 2026-05-07, PR #382 (`fix(perf): recalibrate Lighthouse budget 1250 →
3500 KB scripts`) a été refusée. La motivation invoquée — "le bundle
actuel dépasse 1250 KB et bloque trois PRs OPEN (#381 fix CI bypass
bootstrap-guard, #359 Metrics+Sentry, #365 seo-role-contracts)" — n'était
pas un signal empirique justifiant un changement de cible. Augmenter
arbitrairement le budget pour débloquer des PRs entrantes est exactement
le pattern bricolage que la rule G1 (signal-proven decisions) interdit.

Trois angles morts ont émergé pendant l'analyse de PR #382 :

1. **Confusion raw vs gzipped per-page**. Le budget Lighthouse `script
   size: 1250 KB` est appliqué **par page** sur les **bytes transférés**
   (gzipped/brotli sur le réseau). La mesure brute "bundle 3128 KB / 192
   fichiers" produite manuellement (`du -shc *.js`) totalisait le bundle
   client raw, toutes pages confondues — non comparable au budget. Le
   pic mesuré CI run `25178882039` (2026-04-30) sur `/pieces/<long-slug>`
   était 1117 KB, sous budget, post-stack TTI home (PR #227 / #229 /
   #230). La régression depuis avril 30 reste à mesurer signal-proven.

2. **Aucune télémétrie bundle durable**. Le seul artefact perf existant
   est `frontend/bundle-report.html` (1 MB HTML, daté 2026-03-02 — stale
   66 jours), regénéré uniquement à la main via `ANALYZE=true npm run
   build`. Pas de baseline diffable, pas d'historique, pas de gate CI
   sur les chunks individuels. Un refactor qui double `react-vendor` ne
   serait visible que si Lighthouse remonte un script size régression
   sur l'une des 3 URLs cibles (`/`, `/pieces/<slug>`, `/constructeurs/<slug>.html`),
   ce qui peut prendre plusieurs PRs avant d'être détecté.

3. **Aucune méthodologie d'arbitrage budget**. Quand le budget Lighthouse
   est dépassé, deux décisions sont possibles : (a) réduire le bundle
   sous le budget canon, (b) recalibrer le budget signal-proven sur un
   plancher technique mesuré. PR #382 a tenté (b) sans la mesure
   préalable. Aucun ADR n'établissait le critère pour basculer de (a)
   vers (b).

## Décision

**1. Source unique de vérité bundle** — `audit-reports/bundle-top10.json`
versionné, regénéré par `npm -w frontend run bundle:report` (script
`scripts/perf/bundle-top10.mjs`). Format : `total` (count + raw + gzip +
brotli), `by_category` (vendor / shared / route / manifest / entry),
`top10` + `chunks` complète. Diffable line-by-line en code review.

**2. Baseline figée** — `audit-reports/bundle-top10.baseline.json` (alias
gelé du report 2026-05-07) sert de référence pour quantifier les gains
des PRs PR-2 à PR-5bis du sprint perf. Aucune régression vs baseline
ne sera mergée sans justification PR.

**3. Fraîcheur garantie en CI** — script `scripts/perf/check-bundle-fresh.mjs`
fail si `bundle-top10.json` est plus ancien que les fichiers de
`frontend/build/client/assets/`. À câbler dans `.github/workflows/perf-gates.yml`
en PR-6 (hors scope ADR-051).

**4. Distinction explicite raw vs gzipped vs per-page** — l'ADR statue :

| Mesure | Sémantique | Comparable au budget Lighthouse `script size: 1250` ? |
|---|---|---|
| `total.size` (raw) | Somme `*.js` non-compressés du bundle client | **Non**, le réseau ne transfère jamais le raw |
| `total.gzip` / `total.brotli` | Somme bundle client compressé | **Non**, le budget mesure par page, pas total |
| Lighthouse `resource-summary.script.size` | Somme scripts chargés sur **une URL**, transferred bytes (gzip/brotli) | **Oui** — c'est ce que le budget mesure |

Toute communication interne / titre PR / handoff session **doit utiliser
la sémantique correcte**. Comparer "bundle total 3128 KB raw" à "budget
1250 KB" produit du bricolage (cf. PR #382 close).

**5. Méthodologie d'arbitrage budget** — branchement décisionnel
documenté dans le plan sprint `budget-r-tabli-tous-les-wondrous-phoenix.md` :

- **Branche A** (préférée) : si après PR-2 à PR-5bis le bundle revient sous
  les valeurs de `lighthouse-budget.json` sur les 3 URLs cibles → pas de
  recalibration, hardening de `perf-gates.yml` avec assertion fine sur
  `bundle-top10.json`.

- **Branche B** : si l'audit `vendor-breakdown.json` (PR-5) +
  `remix-payload-report.json` (PR-5bis) prouvent un plancher technique
  > 1250 KB **et** que toute optimisation supplémentaire est hors-sprint
  (pivot Preact / RSC / Next App Router) → ouvrir ADR-052 amendant
  `lighthouse-budget.json` à `MIN + 10 % marge`. **Ce n'est pas un PR
  #382 réhabilité** : la valeur est calculée à partir d'evidence-pack
  joint (`bundle-top10.json` + `vendor-breakdown.json` +
  `remix-payload-report.json` + `critical-path-analysis.json`), pas
  arbitraire.

**6. Critère sortie sprint** — l'une de :
- Bundle ≤ valeurs `lighthouse-budget.json` sur 3 URLs (Branche A), OU
- ADR-052 mergé avec evidence-pack et nouveau budget signal-proven (Branche B).

Tout autre critère (incluant "débloquer #381/#359/#365") est subordonné.

## Baseline empirique 2026-05-07 (snapshot inclus)

Mesure générée par `npm -w frontend run bundle:report` sur build local
2026-05-07 23:03 (post-merge `main` à eda2dd10) :

| Catégorie | Chunks | Raw | Gzip | Brotli |
|---|---:|---:|---:|---:|
| vendor (4) | 4 | 634 KB | 198 KB | … |
| shared (3) | 3 | 195 KB | 54 KB | … |
| route | 174 | 1705 KB | 482 KB | … |
| manifest | 1 | 69 KB | 6 KB | … |
| entry | 2 | 42 KB | 12 KB | … |
| **TOTAL** | **184** | **2645 KB** | **752 KB** | **660 KB** |

Top 10 chunks (par taille raw) :

| # | Chunk | Catégorie | Raw | Gzip |
|---:|---|---|---:|---:|
| 1 | `react-vendor` | vendor | 421 KB | 139 KB |
| 2 | `app-core` | shared | 154 KB | 42 KB |
| 3 | `radix-vendor` | vendor | 95 KB | 28 KB |
| 4 | `pieces._gamme._marque._modele._type_._html` | route | 87 KB | 22 KB |
| 5 | `manifest` | manifest | 69 KB | 6 KB |
| 6 | `blog-pieces-auto.guide-achat.comment-utiliser-selecteur-vehicule-pieces-auto` | route | 66 KB | 16 KB |
| 7 | `lucide-vendor` | vendor | 63 KB | 12 KB |
| 8 | `use-pieces-filters` | route | 56 KB | 15 KB |
| 9 | `html-parser-vendor` | vendor | 55 KB | 19 KB |
| 10 | `pieces._slug` | route | 50 KB | 14 KB |

**Note** : ces 2645 KB raw / 752 KB gzip totalisent le bundle entier.
Une page donnée charge un sous-ensemble (vendors partagés + route + shared).
PR-5 du sprint produira la décomposition par URL via Lighthouse coverage.

## Conséquences

### Positives

- **Décisions budgétaires signal-proven** : tout amendement à
  `lighthouse-budget.json` exige désormais un evidence-pack joint
  (`bundle-top10.json` ou son successeur). Pattern PR #382 plus possible.
- **Détection de régression précoce** : `bundle-top10.json` versionné
  rend visible en code review tout chunk qui grossit > seuil.
- **Pédagogie** : la matrice raw/gzip/per-page éteint la confusion
  récurrente sur les unités du budget Lighthouse.

### Négatives / contraintes

- Toute PR touchant `frontend/app/**` ou `frontend/vite.config.ts` doit
  régénérer `bundle-top10.json` (script `bundle:report` ~3 sec après
  `npm run build`). Friction modeste mais réelle. Mitigation : ajouter
  hook `pre-commit` qui lance `bundle:report` automatiquement (hors
  scope ADR-051, à évaluer après 2 sprints de retour d'usage).
- `bundle-report.html` (1 MB HTML généré par `rollup-plugin-visualizer`)
  reste **non versionné** — regénérable par `npm -w frontend run
  bundle:analyze`. Ne pas commiter (pollue le diff).

### Risques résiduels

- **Sur-confiance en `bundle-top10.json`** : ce fichier mesure le bundle
  total, pas l'expérience utilisateur. CWV (LCP, INP, TBT, CLS) reste
  l'arbitre final via Lighthouse, complément non substituable. PR-5 du
  sprint étend la mesure à `critical-path-analysis.json` pour combler
  l'angle mort exécution / parse / hydration.
- **`@tanstack/react-query` cache hydration JSON** dans
  `window.__remixContext` peut représenter 100-500 KB transférés
  invisibles à `bundle-top10.json`. PR-5bis du sprint produit
  `remix-payload-report.json` pour couvrir cet angle.

## Alternatives rejetées

1. **Recalibrer 1250 → 3500 KB sans audit** (PR #382). Refusé par user
   2026-05-07 — bricolage par convenance, viole G1.
2. **Versionner `bundle-report.html` directement**. Refusé : 1 MB HTML
   non-diffable, ratio signal/bruit nul, regénérable.
3. **Tracker Top 10 dans `lighthouse-budget.json` lui-même**. Refusé :
   ce fichier est canon de seuils, pas d'observation. Séparer les rôles.
4. **Différer la baseline jusqu'à PR-5/PR-5bis terminées**. Refusé :
   sans baseline figée, les gains des PRs intermédiaires ne sont pas
   quantifiables. PR-1 (cette ADR + script) est foundation.

## Notes d'implémentation

- Script `scripts/perf/bundle-top10.mjs` : Node 20+, dépendances
  natives (`fs`, `zlib`, `path`). Aucun npm-install supplémentaire.
- Script `scripts/perf/check-bundle-fresh.mjs` : idem, fail-fast si
  `bundle-top10.json` plus ancien que les assets construits.
- `frontend/package.json` ajoute :
  - `bundle:analyze` → `ANALYZE=true npm run build` (génère
    `frontend/bundle-report.html` local).
  - `bundle:report` → `node ../scripts/perf/bundle-top10.mjs` (génère
    `audit-reports/bundle-top10.json`).
  - `bundle:check-fresh` → garde-fou CI, à câbler en PR-6.
- ADR-052 sera ouverte uniquement si Branche B activée. Pas de pré-écriture
  spéculative (cf. `feedback_decision_must_be_signal_proven_not_intuited.md`).
