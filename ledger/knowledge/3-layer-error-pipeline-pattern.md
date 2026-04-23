# Pattern : Pipeline de gestion d'erreur 404/410/301 à 3 couches

**Domaine :** SEO, Routage, Erreurs HTTP
**Date :** 2026-04-23
**Evidence :** PR monorepo [#133](https://github.com/ak125/nestjs-remix-monorepo/pull/133)

---

## Contexte

Le monorepo expose une architecture 3-couches déjà en place pour gérer les 404, 410, 301 et redirections legacy. Toute URL non matchée par une route Remix explicite traverse ce pipeline, qui assure :

- **Telemetry** — chaque hit est loggé dans `__error_logs`
- **Override sans redéploiement** — les règles `REDIRECT_RULE` dans `___xtr_msg` sont consultées en cache (5 min TTL)
- **UX cohérente** — 410 et 404 sont rendus en HTML via `<ErrorGeneric>`, avec `Cache-Control` et `X-Robots-Tag` appropriés

L'antipattern à éviter : ajouter un court-circuit hardcodé dans `RemixController` qui intercepte une URL avant que Remix ne la reçoive. Ce court-circuit by-pass silencieusement les 3 couches, ce qui se traduit concrètement par : 0 log, 0 override DB possible, réponse plain-text au lieu d'HTML. Incident observé 2026-04-23 sur `/pieces-{supplier}.html` — 0 hits 410 tracés dans `__error_logs` sur 30 jours parce que le shortcut sautait le logger.

## Les 3 couches

### Couche 1 — Frontend catchall (`frontend/app/routes/$.tsx`)

Point d'entrée universel pour toute URL non matchée. Responsabilités :

1. **Short-circuit local** avant tout appel API :
   - `isGarbageUrl(pathname)` — patterns base64/spam/tokens → 410 direct avec cache 24h
   - `resolveKnownPattern(pathname)` — redirections statiques (accents, trailing `.html`, `/blog/` → `/blog-pieces-auto/`, etc.)
2. **Appel C2** pour chaque URL légitime :
   - `POST /api/errors/log` — tracer le 404
   - `GET /api/redirects/check?url=...` — chercher une règle DB
   - `GET /api/redirects/resolve-legacy?url=...` — résolution spécifique `/pieces-auto/{alias}`
   - `GET /api/errors/suggestions?url=...` — suggestions intelligentes
3. **Décision finale** :
   - `checkIfOldLink(pathname)` match un pattern obsolète connu → 410 HTML + `Cache-Control: max-age=86400` + `X-Robots-Tag: noindex`
   - sinon → 404 HTML avec suggestions

### Couche 2 — API bridge (`backend/src/api/errors-api.controller.ts`)

Deux contrôleurs NestJS :

- `@Controller('api/errors')` → `ErrorsApiController` (suggestions, log, statistics, recent)
- `@Controller('api/redirects')` → `RedirectsApiController` (check, resolve-legacy, add, statistics)

Rôle : exposer en HTTP les services de la couche 3, avec gestion des erreurs (fallbacks gracieux : retourne `{found: false}` au lieu de throw).

### Couche 3 — Services métier (`backend/src/modules/errors/services/` + `seo/validation/`)

- **`RedirectService`** (`redirect.service.ts`)
  - Cache en mémoire (5 min TTL, `redirectCache: Map<string, RedirectRule>`)
  - Règles stockées dans `___xtr_msg` où `msg_subject = 'REDIRECT_RULE'` et `msg_content` = JSON `{source_path, destination_path, status_code, is_active, is_regex, priority, hit_count}`
  - Méthodes clés : `findRedirect()`, `createRedirect()`, `markAsGone()`, `incrementHitCount()` (fire-and-forget)
- **`ErrorLogService`** (`error-log.service.ts`) — écrit dans `__error_logs`
- **`ErrorService`** (`error.service.ts`) — génère les suggestions (similarité d'URL)
- **`UrlCompatibilityService`** (`seo/validation/url-compatibility.service.ts`) — `resolveLegacyGammeUrl()` pour `/pieces-auto/{alias}`

## Règle canon

> **Tout handler 404/410/301 pour une famille d'URL legacy passe par le pipeline 3-couches.**
> Aucun court-circuit hardcodé dans `RemixController` (ni dans un autre controller backend qui précède le handler Remix).

### Pourquoi

1. **Observabilité** — sans le passage par `__error_logs`, on ne sait pas combien de hits arrivent → impossible de prioriser les redirections 301 les plus impactantes SEO
2. **Flexibilité ops** — les règles de redirection doivent pouvoir être ajoutées/modifiées sans redéploiement, via admin UI ou `RedirectService.createRedirect()`
3. **UX** — un 410 doit retourner une page HTML explicite avec lien vers la home/recherche, pas un plain-text `'Gone'`
4. **Cohérence** — `Cache-Control`, `X-Robots-Tag` et les headers SEO sont gérés uniformément dans `$.tsx`, pas dispersés dans chaque controller qui voudrait émettre un 410

### Cas concrets couverts par le pipeline

| Pattern URL | Traitement |
|-------------|------------|
| `/old-*`, `/archive/*`, `/legacy/*`, `/deprecated/*`, `/*.old` | 410 via `checkIfOldLink` (patterns hardcodés dans `$.tsx`) |
| `/piece/*` (~90K URLs legacy) | 410 via `checkIfOldLink` |
| `/reference-auto/*` | 410 via `checkIfOldLink` |
| `/pieces-{supplier}.html` (ex: `/pieces-purflux.html`) | 410 via `checkIfOldLink` (ajouté 2026-04-23) |
| `/pieces-auto/{alias}` | 301 vers `/pieces/{alias}-{id}.html` si gamme existe, sinon 410 via `resolve-legacy` |
| `/blog/*`, `/conseils/*`, `/guide/*` | 301 via `resolveKnownPattern` |
| `*.html` trailing (non-pieces) | 301 strip `.html` via `resolveKnownPattern` |
| URLs avec règle DB `REDIRECT_RULE` | 301/302/308 via `RedirectService.findRedirect` |

## Ajouter une nouvelle famille d'URL au pipeline

### Option A — Pattern hardcodé (legacy massif, pas d'override DB souhaitée)

1. Éditer `frontend/app/routes/$.tsx`, fonction `checkIfOldLink` :
   ```typescript
   const oldLinkPatterns = [
     // ...
     /^\/votre-pattern-ici/, // commentaire explicite
   ];
   ```
2. Si le pattern inclut `.html` final mais ne doit **pas** être strippé, exclure dans `resolveKnownPattern` :
   ```typescript
   if (
     pathname.endsWith(".html") &&
     !pathname.startsWith("/pieces/") &&
     !/^\/votre-pattern\.html$/.test(pathname)
   ) {
     return pathname.slice(0, -5);
   }
   ```

### Option B — Règle DB (override par admin, hit count, expirable)

1. Appeler en backend :
   ```typescript
   await redirectService.createRedirect({
     old_path: '/pieces-purflux.html',
     new_path: '/',
     redirect_type: 301,
     reason: 'Legacy supplier URL, redirect to home'
   });
   ```
2. Ou via SQL direct dans `___xtr_msg` avec `msg_subject = 'REDIRECT_RULE'`
3. Cache invalidé après 5 min automatiquement (`cacheExpiry`)

### Anti-pattern à ne jamais reproduire

```typescript
// ❌ À BANNIR — court-circuit dans RemixController
@All(':path*')
async handler(@Req() request: Request, @Res() response: Response) {
  // ...
  if (/^\/pieces-[a-z0-9-]+\.html$/i.test(request.url)) {
    response.status(HttpStatus.GONE).send('Gone'); // no log, no HTML, no override
    return;
  }
  // ...
}
```

Ce pattern a été introduit par les commits `108b8af6` et `9660b3e9` (branche `main`) avec l'intention légitime de "bloquer les URLs legacy equipementier". Le problème : la cible a été atteinte (410 retourné) mais au prix de l'observabilité et de la flexibilité. Supprimé par PR #133 au profit du pipeline standard.

## Tables DB

| Table | Rôle | Colonnes clés |
|-------|------|---------------|
| `___xtr_msg` (WHERE `msg_subject='REDIRECT_RULE'`) | Règles de redirection 301/302/410 | `msg_content` (JSON), `msg_open` ('1' = actif) |
| `__error_logs` | Historique des 404/410/500 | `err_url`, `err_code`, `err_created_at`, `err_user_agent`, `err_referrer` |

Pour explorer le trafic sur une famille d'URL :
```sql
SELECT err_url, err_code, COUNT(*) cnt
FROM __error_logs
WHERE err_url LIKE '/pieces-%.html'
  AND err_created_at > NOW() - INTERVAL '30 days'
GROUP BY err_url, err_code
ORDER BY cnt DESC LIMIT 20;
```

## Références

- PR monorepo [#133](https://github.com/ak125/nestjs-remix-monorepo/pull/133) — correction du shortcut `/pieces-{supplier}.html`
- Commits source de l'antipattern : `108b8af6`, `9660b3e9` (monorepo `main`)
- Fichiers canon :
  - `/opt/automecanik/app/frontend/app/routes/$.tsx` (C1)
  - `/opt/automecanik/app/backend/src/api/errors-api.controller.ts` (C2)
  - `/opt/automecanik/app/backend/src/modules/errors/services/redirect.service.ts` (C3 — RedirectService)
  - `/opt/automecanik/app/backend/src/modules/errors/services/error-log.service.ts` (C3 — ErrorLogService)
  - `/opt/automecanik/app/backend/src/modules/seo/validation/url-compatibility.service.ts` (C3 — legacy /pieces-auto/)
- Pattern voisin : [[runbook-admin-brand-editorial]] (pattern d'invalidation de cache)

## Checklist de revue pour tout nouveau handler d'erreur HTTP

- [ ] L'URL traverse `frontend/app/routes/$.tsx` (pas de court-circuit dans un controller backend qui précède Remix)
- [ ] Un hit génère une entrée dans `__error_logs` (vérifiable via `SELECT ... FROM __error_logs WHERE err_url LIKE ...`)
- [ ] Un admin peut ajouter/modifier une 301 via `RedirectService.createRedirect` sans déploiement
- [ ] La réponse HTML utilise `<ErrorGeneric status={...} />` (pas `.send('Gone')`)
- [ ] Les headers `Cache-Control` et `X-Robots-Tag: noindex` sont émis (pattern `throw json(...)` dans `$.tsx`)
- [ ] Le pattern est documenté dans cette note (ajouter une ligne dans la table "Cas concrets")
