# ADR-084 (proposé — numéro à attribuer par le vault) — Suppression du niveau-modèle `/constructeurs` (URLs 2-segments) via HTTP 410 Gone

> **Statut** : **DÉPLOYÉ EN PROD 2026-06-14, vérifié live** — formalisation vault en attente (PR signée G3 owner)
>
> **Déploiement** : PR #973 (route 410 + sitemap + JSON-LD) + PR #974 (fix impeccable, prérequis) mergées ; migration `20260614_sitemap_vehicules_drop_model_level` appliquée (vue → 35 marques) ; tag `v2026.06.14-constructeurs-model-410-suppression` (SHA `7b9fef65a`) → PROD.
>
> **Vérification live PROD (2026-06-14)** : modèle 2-seg `/constructeurs/{m}-{id}/{mo}-{id}.html` → **410 + `X-Robots-Tag: noindex, follow`** ; R7 marque + R8 véhicule 3-seg → **200** (préservés) ; `sitemap-vehicules.xml` régénéré → **0 URL modèle** (35 marques) ; `/health` → 200.
> **Date** : 2026-06-14
> **Owner** : Fafa (automecanik.seo@gmail.com)
> **Surfaces** : SEO runtime (Remix routes `/constructeurs/*`), sitemap V10 (vue `__sitemap_vehicules` + hubs), données structurées JSON-LD, validation url-compatibility
> **Mémoires liées** : `feedback_no_url_changes_ever` (410 + page contextualisée, jamais redirect-équivalent), `feedback_no_auto_page_suppression_ever` (suppression manuelle owner-gated), `reference_gsc_index_profile_thin_combinatorial_longtail`, `reference_seo_gsc_daily_mirror_undercaptures_4x`

## Contexte

L'architecture `/constructeurs/` expose 3 niveaux de profondeur :

| Niveau | Format URL | Rôle | Décision |
|--------|-----------|------|----------|
| R7 marque | `/constructeurs/{marque}-{id}.html` | hub marque | **conservé** (200, indexable) |
| **Niveau-modèle (intermédiaire)** | `/constructeurs/{marque}-{id}/{modele}-{id}.html` | « sélecteur de motorisation » (liste des moteurs d'un modèle) | **SUPPRIMÉ** |
| R8 véhicule | `/constructeurs/{marque}-{id}/{modele}-{id}/{type}-{id}.html` | fiche véhicule | **conservé** (200, indexable) |

Le niveau-modèle (2-segments) est une page-entonnoir intermédiaire mince. L'owner a constaté son existence et décidé qu'elle **ne doit pas exister** : seuls R7 (marque) et R8 (véhicule) sont des URLs constructeur légitimes.

**Échelle** : 973 URLs distinctes (35 marques), source `__sitemap_motorisation`.

## Données empiriques (qui tranchent le mécanisme)

Mirror GSC `__seo_gsc_daily`, fenêtre 71 jours (2026-04-01 → 06-10), classe niveau-modèle 2-seg :

- **1 clic total**, 682 impressions, position moyenne 23.6 (page 3).
- ~90 % des 973 URLs n'ont **jamais** affiché en SERP.
- Comparaison : R7 marque = 6 clics / 4795 impr ; R8 véhicule = 23 clics / 2760 impr. Le niveau-modèle est la classe la plus faible.
- Caveat honnête : `__seo_gsc_daily` sous-capture ~4× (anonymisation dim query) → chiffres = **plancher**. Même ×4 ≈ 0,06 clic/jour sur 973 pages = indiscernable de zéro.
- Tables coverage (`__seo_index_history`, `__seo_crawl_log`, `__seo_internal_link`) **vides** → GSC est le seul signal disponible.

**Conséquence** : aucun link-equity organique à préserver. Le débat 410-vs-301 est tranché **par la donnée**, pas par doctrine.

## Décision

**Supprimer le niveau-modèle 2-segments via HTTP 410 Gone**, page contextualisée, avec retrait de tous les émetteurs (sitemap, JSON-LD, liens internes).

### Mécanisme : `410 Gone` (et pourquoi pas les alternatives)

| Option | Verdict | Raison |
|--------|---------|--------|
| **410 Gone** | ✅ **RETENU** | Dé-indexe ~quelques jours plus vite que 404, signale la permanence intentionnelle ; réutilise le mécanisme erreur 3-couches déjà en place ; conforme canon `no_url_changes_ever` (retrait = 410 + page contextualisée). |
| 404 Not Found | ❌ | Quasi-équivalent mais dé-indexation plus lente, ne signale pas la permanence. |
| 301 → marque R7 | ❌ | Google reclasse un redirect non-équivalent (modèle→marque) en **soft-404** (0 signal transmis) ; ET interdit par le canon ; ET la donnée (1 clic) ne justifie aucune préservation d'equity. |
| noindex + 200 | ❌ | Garde 973 pages thin vivantes (anti-pattern `catalog_signature`, crawl gaspillé, dé-indexation plus lente). |
| split 301/410 data-driven | ❌ | Dégénéré : la donnée prouve que le bucket « mérite 301 » est vide. |

### Rollout : pas de feature flag (V1-first justifié)

Blast radius business ≈ nul (1 clic / 71 j) → un flag serait de la sur-ingénierie réfutée par la donnée. **Rollback = revert-PR + re-tag `v*`** (main branch-protected, jamais force-push). Déploiement en un lot (pas de canary par marque).

## Périmètre d'exécution (surfaces exhaustives — vérifié 2× par fan-out adversarial)

1. **Route 410** — `constructeurs.$.tsx` : bloc `segments.length===2` (200 → `throw 410`), + `Cache-Control: public, max-age=86400` sur les throws 410 (cohérence avec le pattern R8 `seoError`), + purge code mort (type/meta/composant motorization_selector, `legacyMatch` devenu inatteignable, imports orphelins). Le noindex est porté par les 3 couches existantes (`headers` export → `ErrorBoundary` → `ErrorGeneric`), **rien à inventer**.
2. **Sitemap, 2 canaux** — (a) vue `__sitemap_vehicules` : `CREATE OR REPLACE VIEW` sans la branche niveau-2, en **préservant** `security_invoker=true` + `REVOKE` ; (b) `sitemap-v10-hubs-vehicle.service.ts` : retrait de l'émission N2 (hubs HTML par marque).
3. **JSON-LD BreadcrumbList** (retrait items « Constructeurs »/« Modèle » + **renumérotation contiguë** 1..N) — `r8-schema.ts`, `constructeurs.$brand[.]html.tsx`.
4. **Fil d'ariane visible + données** — `BreadcrumbSection.tsx`, `r8-transform.ts`, `BrandHero.tsx`, `BrandsGrid.tsx` (CTA homepage).
5. **url-compatibility** — exclure le niveau-modèle du `/report` (sans supprimer de méthode ; R7/R8 intacts).
6. **url-builder** — retrait `buildConstructeurModeleUrl` (code mort, 0 appelant).
7. **Tests** — MAJ `r8-schema.test.tsx`, `catch-all-404-noindex.test.ts` ; ajout test 2-seg → 410.

**Préservé intact** : R7 marque, R8 véhicule 3-seg, `VehicleSelector`, `robots.txt` (`Allow: /constructeurs/` reste — règle de section). **Non touché** : `RelatedBrandsSection` (code mort), `EnrichedVehicleItem` (admin) — notés en dette, hors scope.

## Conséquences

- **Positives** : élagage de 973 pages thin du long-tail combinatoire ; cohérence sitemap↔runtime ; breadcrumbs sans URL en erreur ; rapport url-compatibility honnête.
- **Négatives / risques** : fenêtre transitoire <24 h où le sitemap statique peut encore lister des URLs 410 (mitigée : régénérer + vérifier AVANT tag PROD). Dé-indexation GSC visible en semaines (« Removed/Gone »).
- **Réversibilité** : revert-PR + re-tag ; la vue est un `CREATE OR REPLACE` réversible.

## Vérification (gates obligatoires)

1. **PRE-MERGE** : `turbo build` vert + tests ; valider sur DEV:3000 que le 2-seg sort `410 + X-Robots-Tag noindex,follow + Cache-Control public,max-age=86400` et que R7/R8 restent `200`.
2. **Avant tag PROD** : régénérer le sitemap (2 canaux) et **vérifier 0 URL 2-seg** émise.
3. **POST-MERGE LIVE** (collecteurs coverage vides → vérif runtime obligatoire, `feedback_runtime_verification_mandatory`) : `curl` Googlebot-UA sur 3-5 URLs modèle échantillon → attendu `410`.
4. **Observation J+7 / J+14** : GSC Coverage « Removed » + `__seo_gsc_daily` pattern 2-seg (observabilité interne, zéro canary externe). **Rollback uniquement si** les clics R7 (1-seg) ou R8 (3-seg) régressent — PAS si les 2-seg s'éteignent (attendu).

## Notes / dette signalée (hors scope, report-only)

- `constructeurs.$.tsx` `brandLegacyMatch` : chaîne `301 → /constructeurs/{slug}` (sans id) → 404 (bug latent).
- Split www/non-www en GSC → le host-canonical mérite un contrôle séparé.
- Endpoints `/api/seo/url-compatibility/*` non-guardés (`@UseGuards` absent).
- `RelatedBrandsSection.tsx` + `EnrichedVehicleItem.tsx` : liens sans-id (404) sur code mort/admin → candidats nettoyage séparé.
