---
date: 2026-05-08
type: audit-trail
related: [rules-seo-pagerole, MOC-Rules, MOC-AuditTrail]
---

# 2026-05-08 — R-SEO-09 URL Immutability ancrée canon

## What

Ajout de la règle **`R-SEO-09: URL Immutability`** dans
[[rules-seo-pagerole]], section ajoutée après R-SEO-08 et avant la section
"CI Integration" (+76 lignes, 1 fichier, 0 modification existante).

PR vault [#238](https://github.com/ak125/governance-vault/pull/238) MERGED
`f9e2c4b` à 2026-05-08 20:08 UTC. Branche depuis `main`, commit signé
SSH ed25519 `6cc95c8`, pre-push G2 + Broken Wikilinks + G3 PASS, CI vault
6/6 checks PASS (G2/G3/G4/wikilinks/V1-paths/self-review).

Mémoire DEV miroir auto-loaded :
`memory/feedback_no_url_changes_ever.md` (enrichi en parallèle de la PR).

## Why

Rappel utilisateur **2× sur la même session 2026-05-08** :

> « il est strictement interdit de toucher aux URLs »
> « vous n'avez pas le droit de toucher aux URLs »

Déclencheur empirique : commit `369fca35` sur PR-5 monorepo
(`feat/seo-v9-pr5-gamme-shadow`) modifiait unilatéralement le canonical
`R1_GAMME_ROUTER` de `/pieces/{pgAlias}` à `/pieces/{pgAlias}-{pgId}.html`,
au prétexte que la route Remix `pieces.$slug.tsx` extrait l'ID via regex
`-(\d+)\.html$`. Reverté `f065e08c` après le rappel.

Avant R-SEO-09, aucune règle vault ne formalisait l'immutabilité des URLs.
[[rules-seo-pagerole]] R-SEO-02 couvrait seulement la cohérence
`pattern ↔ pageRole`, pas l'interdiction de modifier le pattern lui-même.

État empirique justifiant le verrou strict :
- Régression GSC R3 active, 73% `/pieces/*` `Crawled - currently not indexed`
  (cf. [[2026-05-08-seo-r2-thin-content-forensic-and-decisions-pending]]).
  Toucher aux URLs aggrave drastiquement.
- Sitemap V10 + canonical strict + linking interne sont alignés sur les
  URLs en place — modifier nécessite re-synchroniser 4-5 systèmes.
- Backlinks externes pointent les URLs actuelles, non rattrapables.

## Périmètre R-SEO-09 (résumé canon)

Interdit toute modification de :
- segments de path (`/pieces/...`, `/constructeurs/...`, `/produit/...`)
- slugs (`pg_alias`, `marque_alias`, etc.) et suffixes (`.html`, `-{pgId}`)
- séparateurs entre segments (`.` vs `-` vs `/`)
- query strings indexées
- patterns canonical produits par `SeoCanonicalService`
- noms de fichiers route Remix
- patterns sitemap V10, règles `robots.txt`, redirections 301 vivantes

13 trigger words auto-STOP documentés (`réécrire URL`, `migrer slug`,
`moderniser path`, `optimize slug`, `url_title_optimizer`, …).

Cibles autorisées : surfaces, seuils noindex, chaîne services
(renderer/switch/builder/indexability/canonical), feature flags, contenu,
tables `__seo_*`, fingerprint, linking interne, JSON-LD. **Tout sauf URLs.**

Procédure exception : ADR vault dédié + plan 301 + validation utilisateur
explicite **avant** exécution. Pas de glissement silencieux.

## Impact attendu

- **Plan SEO v9 PR-2** : `SeoSlugService` reste contraint par golden tests
  reproduisant les slugs legacy à l'identique (50 URLs). `SeoCanonicalService`
  produit le canonical exact correspondant à l'URL legacy par rôle.
- **Plan SEO v9 PR-8** : `SeoUnavailablePolicy` (410/412) ne redirige
  jamais vers une "URL équivalente modernisée".
- **Plan SEO v9 PR-11** : `R2IndexabilityGate` ajusté côté indexabilité
  uniquement, jamais côté pattern URL.
- **Auto-stop sessions futures** : toute proposition contenant un trigger
  word listé déclenche STOP + signalement utilisateur avant exécution.

## Cross-références

- Règle canon : [[rules-seo-pagerole]] §R-SEO-09
- Forensic R2 thin content : [[2026-05-08-seo-r2-thin-content-forensic-and-decisions-pending]]
- Mémoire DEV : `memory/feedback_no_url_changes_ever.md` (auto-loaded)
- Précédent technique : commit `369fca35` reverté `f065e08c` (PR-5 monorepo)
- PR vault canonisation : [#238](https://github.com/ak125/governance-vault/pull/238) (MERGED)
