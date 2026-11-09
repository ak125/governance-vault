---
title: Pattern — 5 verrous PR foundation anti-breaking cascade
date: 2026-05-08
status: validated
domain: engineering-patterns
related_adrs: []
related_memories: [feedback_stacked_pr_pattern_for_atomic_phase, feedback_no_bricolage_align_existing_contract, feedback_perf_migration_must_honor_contract]
related_state_files: [seo-v9-cascade-state-20260508.md]
---

# Pattern — 5 verrous PR foundation anti-breaking cascade

## Contexte

Toute PR qui refactore un **moteur central** consommé par 5+ PRs en cascade (SEO chain orchestrator, RAG pipeline, lookup service, payment gateway abstraction, etc.) verrouille involontairement des contrats internes. Si la signature publique est naïve, les PRs suivantes (`PR-3/5/7/8…`) cassent le contrat → revert ou migration en stack lourde.

Validé empiriquement le 2026-05-08 sur **SEO v9 PR-2c** : sans review utilisateur du plan rev 1, PR-7 (lookup MV pré-calculée batch) aurait cassé la signature `lookup(marker) → string` du `SeoInternalLinkingService`. Avec rev 2, `resolveLinksBatch({markers[], context}) → LinkResolutionResult[]` reste stable même quand l'implémentation interne migre du stub direct vers la MV.

Cumul tests cascade SEO v9 : **153/153 verts** (cf. [`seo-v9-cascade-state-20260508.md`](./seo-v9-cascade-state-20260508.md)).

## Quand appliquer

Pour toute **PR foundation** créant un service consommé par PRs futures connues :

- ✅ Refactor moteur central (orchestrator stateless, registry SoT, policy service)
- ✅ Service `Foo` consommé par 5+ PRs en cascade documentée
- ✅ API publique nouvelle (frontend ↔ backend, package monorepo)
- ❌ CRUD isolé, bug fix ponctuel, helper interne sans consommateur cross-PR

## Les 5 verrous

### 1. Signature batch dès maintenant (pas de boucle implicite)

Si un service est consommé dans une boucle aujourd'hui (1 query/marker), la signature publique doit déjà être batch :

```ts
// ❌ Naïf — PR-7 (perf optimization) cassera le contrat
resolveLink(marker: string): Promise<Result>

// ✅ Anti-breaking — l'impl interne peut rester naïve PR-foundation,
// PR-7 remplace l'impl par lookup MV batch sans casser le caller
resolveLinksBatch(input: {
  markers: string[];
  context: { surface, sourceEntityId, locale };
}): Promise<Result[]>
```

**Pourquoi** : l'optimisation arrive toujours. Préfixer la signature publique avec la forme finale même si l'implémentation interne reste un stub naïf.

### 2. Types discriminés avec reason codes (pas `Map<string, string>`)

Préparer une enum stable de raisons d'échec, même si seuls 2 codes sont remplis aujourd'hui :

```ts
// ❌ Faible — extension = breaking
type Result = Map<string, string | null>

// ✅ Discriminé extensible — ajout de codes = non-breaking
type ResolutionReason =
  | 'NO_TARGET'
  | 'NOINDEX'
  | 'CANONICAL_MISMATCH'
  | 'FORBIDDEN_ROLE'
  | 'SELF_LINK'
  | 'ORPHAN';

type Result = {
  input: string;
  output: string | null;
  indexable: boolean;
  reason?: ResolutionReason;
};
```

**Pourquoi** : enrichir le diagnostic (PR-9 fingerprint duplicate gate) sans casser les consommateurs intermédiaires.

### 3. Discriminated union pour blocs HTML/UI (anti-XSS / hydration drift)

Interdire la concaténation HTML brute :

```ts
// ❌ Point central XSS / hydration drift garanti
let html = '';
html += anchor;
html += `<p>${variable}</p>`;

// ✅ Composition typée, narrowing TS, anti-XSS
type ContentBlock =
  | { type: 'markdown'; content: string }
  | { type: 'html'; content: TrustedHtml }   // brand type
  | { type: 'link'; href: string; label: string; rel?: 'nofollow' };

type TrustedHtml = string & { __brand: 'TrustedHtml' };
```

**Vérification** : lint check `grep -E "html\\s*\\+=|\\+\\s*['\"]"` sur le builder = 0 match.

### 4. Canon clé Redis avec TTL + invalidation + namespace

Documenter dès la PR foundation :

```
Format    : seo:v9:linking:${surface}:${entityId}:${markerHash}
TTL       : 3600s (1h, ajusté selon volatilité)
Invalidation : event `seo.target_indexability_changed` (PR-9) + cron daily
Namespace : seo:v9:* (toutes les clés du moteur SEO v9)
```

**Pourquoi** : sans canon, PR-7/PR-8 doivent casser les clés ou créer un namespace parallèle.

### 5. Trois vérifications pré-merge bloquantes

| Vérif | Commande | Pourquoi |
|---|---|---|
| Cycle DI | `npx madge --circular --extensions ts <module-path>` | Registry + policy + chain + orchestrator = haut risque cycle |
| Bundle/startup | `npx nest build` (ou `npm run build`) | TS check ≠ NestJS DI runtime ; startup peut casser sur cycle même tests verts |
| Snapshot regression | `jest --testPathPattern=...regression` | Tests verts ≠ sortie produit identique. Prouver parité bit-à-bit pour 5+ inputs |

**Snapshot strategy** : capturer OLD output **avant** refactor, comparer NEW output bit-à-bit. Échec si divergence non-annotée. Pour les services qui produisent une sortie déterministe canonique, `toMatchSnapshot()` Jest suffit (freeze le contrat output, casse à la moindre dérive).

## Anti-pattern

> *« Stub naïf maintenant, on optimisera plus tard. »*

L'optimisation arrive toujours, et casse le contrat si la signature publique n'est pas anticipée. Préfixer la signature publique avec la forme finale même si l'implémentation interne reste simple.

## Cas d'usage validés

| PR | Verrou clé | Sans verrou |
|---|---|---|
| SEO v9 PR-2c rev 2 (#401) | Signature batch + reason codes + cache canon | PR-7 MV lookup aurait cassé `Map<string,string>` |
| SEO v9 PR-2c rev 2 (#401) | `ContentBlock[]` discriminé | Builder = point central XSS via concat |
| SEO v9 PR-2c rev 2 (#401) | Snapshot freeze 3 surfaces | Refactor V4 → orchestrator silent diff |

## Références

- Mémoire `feedback_stacked_pr_signature_lock_5_verrous` (2026-05-08, source initiale)
- Mémoire `feedback_stacked_pr_pattern_for_atomic_phase` (cascade max 3 niveaux)
- Mémoire `feedback_no_bricolage_align_existing_contract` (CI fail vs contrat → fix CI adopter)
- Mémoire `feedback_perf_migration_must_honor_contract` (migration perf doit honorer contrat receveur)
- State file SEO v9 : [`seo-v9-cascade-state-20260508.md`](./seo-v9-cascade-state-20260508.md)
- PR exemple : [ak125/nestjs-remix-monorepo#401](https://github.com/ak125/nestjs-remix-monorepo/pull/401)
