---
adr: 052
title: Hoist `handoff_targets` du canon markdown vers `@repo/seo-roles` + amendement R6 → R1
status: proposed
date: 2026-05-08
deciders: Fafa (owner SEO)
tags:
  - canon
  - seo
  - handoff
  - role-matrix
  - observability
related:
  - ADR-027  # R5 sunset autonome (informe routable-surface-registry)
  - ADR-031  # 4-layer content architecture (raw / wiki / exports / consumers)
  - ADR-037  # Agent naming canon — RoleId enum
  - ADR-046  # Canon roles & contracts (L1.5 CONTRACTS)
  - ADR-051  # R6 canon cascade (R6_GUIDE_ACHAT canonisation, vault PR #212)
links:
  - https://github.com/ak125/nestjs-remix-monorepo/pull/405  # Monorepo PR
---

# ADR-052 — Hoist `handoff_targets` du canon markdown vers `@repo/seo-roles` + amendement R6 → R1

## Status

**proposed** (ouvert 2026-05-08) → **accepted** post-merge monorepo PR #405.

## Context

### Drift identifié (audit 2026-05-08)

Audit empirique du codebase révèle un drift sur **9 rôles sur 10** entre :

- **SoT canon humain** : `.spec/00-canon/role-matrix.md` champ `handoff_targets` (édité manuellement, gouvernance)
- **Runtime backend** : `backend/src/modules/seo/types/page-role.types.ts:109` constante `ALLOWED_LINKS` (matrice ad-hoc accumulée par accrétion)

| Rôle | Backend `ALLOWED_LINKS` | Canon `handoff_targets` | Drift |
|---|---|---|---|
| R0 | R1, R2, R3, R4, R5, R6, R7 | R1, R7, R8, R5, R6 | Backend ajoute R2/R3/R4, omet R8 |
| R1 | R2 | R2, R4, R5, R3, R6 | Backend omet 4/5 cibles |
| R2 | R4, R3 | R1, R3, R4, R6 | Backend omet R1, R6 |
| R3 | R4, R2 | R6, R5, R4 | Backend ajoute R2, omet R5, R6 |
| R4 | R3, R5, R1 | R3, R5, R1, R6 | Backend omet R6 |
| R5 | R4, R1 | R3, R4, R1 | Backend omet R3 |
| **R6_GUIDE_ACHAT** | **R4, R2** | **R2, R3, R5, R4** | **Backend omet R3, R5** ★ |
| R7 | R1, R2, R7, R8 | R8, R1, R2 | Backend ajoute R7 (self-loop) |
| R8 | R1, R2, R7 | R1, R3, R5, R7 | Backend ajoute R2, omet R3, R5 |

### Trou empirique du canon lui-même : R1 ∉ R6.handoff_targets

Le canon markdown actuel **ne liste pas R1** dans `R6_GUIDE_ACHAT.handoff_targets` — alors que :

- **Asymétrie systémique** : R0/R2/R7/R8 listent tous R1 (« retour gamme/compatibilité »). R6 est seul à l'omettre.
- **Mission R6 vs canon** : `prompts/R6_GUIDE_ACHAT/planner.md` § ROLE PURITY déclare *« Securiser la decision d'achat — aider a identifier, verifier, comparer et commander la bonne piece sans erreur »*. **Identifier la bonne pièce = compatibilité véhicule = R1**.
- **Conséquence métier AutoMecanik** : sans R1 dans R6 handoffs, un utilisateur sur le guide d'achat plaquettes ne peut pas vérifier la compatibilité avec sa BMW E90 — exactement le « besoin de compatibilité avant commande » que R6 doit servir.

### Bug latent backend `pageRoleToRoleId(R3_BLOG)`

Audit révèle un 3ᵉ angle mort fonctionnel :

```ts
// backend/src/modules/seo/types/page-role.types.ts (avant fix)
case PageRole.R3_BLOG:
  if (r3SubRole === 'conseils') return RoleId.R3_CONSEILS;
  return RoleId.R3_GUIDE;   // ← R3_GUIDE est @deprecated dans canonical.ts
```

`RoleId.R3_GUIDE` est marqué `@deprecated` dans `canonical.ts:13` (« orphan role — no route, no contract, no prompts »). Ce qui entraîne après hoist : `ROLE_HANDOFF_GRAPH[R3_GUIDE] = []` (handoffs vides). Donc **`isLinkAllowed(R6_GUIDE_ACHAT, PageRole.R3_BLOG) === false` même après amendement canon** — bug fonctionnel qui bloque le bénéfice principal.

## Decision

### 1. Hoist canon markdown → mirror typé TS

Création de `packages/seo-roles/src/handoff-graph.ts` :

- `ROLE_HANDOFF_GRAPH: Readonly<Record<RoleId, readonly HandoffEdge[]>>` — mirror typé exact du champ `handoff_targets` de `role-matrix.md`.
- `ROLE_HANDOFF_GRAPH_VERSION = "1.0.0"` — SemVer canon (incrémenté à chaque amendement).
- `getHandoffTargets(role): readonly RoleId[]`.
- `isHandoffAllowed(source, target): boolean`.
- Test golden **set-equality** (`new Set(tsTargets).toEqual(new Set(mdTargets))`) parse `role-matrix.md` et compare cible-à-cible. Détecte cardinalité égale + contenu divergent (drift silencieux impossible).

### 2. Amendement canon `role-matrix.md:170`

Ajout dans `R6_GUIDE_ACHAT.handoff_targets` :
```
{target: R1, condition: "besoin = verifier compatibilite avant commande"}
```

### 3. Backend devient consommateur

- `ALLOWED_LINKS` **supprimé**.
- `isLinkAllowed(source, target)` réécrit : consulte canon via `pageRoleToRoleId() + isHandoffAllowed()`.
- `isRenderableLinkAllowed(source, target)` **ajouté** : combine `isLinkAllowed` + `hasRoutableSurface(targetRoleId)` (registre runtime backend, ROUTABLE_SURFACES exclut R5 sunset, R3_GUIDE déprécié, R6_SUPPORT info pure).
- `pageRoleToRoleId(R3_BLOG)` **fix critique** : default `R3_CONSEILS` (canon vivant) au lieu de `R3_GUIDE` déprécié. Sub-role `'guide-achat'` explicite garde `R3_GUIDE` pour backwards-compat.

### 4. Observabilité initiale (sans prom-client)

- Log structuré NestJS `event: "seo_handoff_filtered"` indexable Loki + champs `source_role`, `target_role`, `reason ∈ {not_in_handoff_canon, not_routable_surface}`, `graph_version`.
- Compteur in-memory `SeoHandoffMetricsService` pattern aligné `MetricsService` legacy (sync atomic in-memory, sans I/O). Exposé via endpoint admin existant `GET /api/seo-dynamic-v4/internal-links/metrics`.
- **Pas de prom-client** dans cette PR — absent du backend (vérifié `package.json`). Migration Prometheus = follow-up infra séparée (lockfile update + `/metrics` endpoint).

### 5. Discipline observabilité (extensions futures)

Pour les prochaines PR shadow/diff/audit :

1. Logger structuré chemin réponse SEO → `setImmediate(() => void emit(...))` (pas `void emit(...)` direct).
2. Sampling déterministe `hash(source:target:entityId) % 100 < rate`, jamais `Math.random()`.
3. Classification divergence shadow/diff ≥ 3 niveaux (`none | soft | hard`) — n'applique pas au counter événementiel actuel (2 niveaux suffisent).
4. Décisions SEO empiriques basées sur métrique Prometheus/OTel agrégeable, jamais sur grep Loki.
5. Helper canonical/URL **ne jamais** utiliser `decodeURI()` sur path (risque sémantique sur `%2F`).

## Non-decision (hors scope)

- **`forbidden_overlap` reste axe orthogonal** au graphe de handoff. Pas de cross-validation Zod inter-axes (ce serait conceptuellement faux — R6 peut linker vers R3 sans absorber le contenu procédural R3).
- **r5 contract absent** dans `packages/seo-role-contracts/src/contracts/` : orthogonal au link graph (link graph dérivé de `seo-roles`, pas de `seo-role-contracts/CONTRACTS`). Follow-up séparé sous responsabilité owner R5.
- **Frontend identité drift** `'R6'` / `'R6_GUIDE'` (`frontend/app/utils/page-role.types.ts`) : bloqué par migration DB historique — précondition empirique R6 cascade ADR-051 PR-E.
- **Chain v9 service** `seo-internal-linking.service.ts` : absent de la branche `main` (introduit dans cascade seo-v9-pr2c ultérieure). Modification chain reportée à intégration cascade v9 ou PR follow-up. Plan v5.2 §Errata point 2 prévoit explicitement ce cas.
- **Drift sémantique r6.ts contract** (`semantic_intents: ["transactional", "investigational", "informational"]` vs `intents.ts` `primary: "investigation_commerciale"` + `allowedLeakage: []`) : bug réel détecté lors de l'audit, touche la sémantique d'intents, pas le graphe de liens. Follow-up séparé.

## Forward-compatibility

Aligné avec **PR-A.bis future** (`packages/seo-roles/src/intents.ts:18-19` mentionne « future canon.json build pipeline derives this matrix from prompts »). Quand PR-A.bis livrera, `handoff-graph.ts` deviendra à son tour dérivé du `canon.json`. Cette PR pose les rails (TS canon backend-consumable + mirror typé du markdown SoT) sans précéder la décision SoT globale.

## Consequences

### Positives

- **Drift impossible** : golden test set-equality bloque CI à toute désync TS ↔ markdown.
- **9 rôles voient leur matrice de maillage alignée au canon** (extensions ET retraits). Côté R6 : gain R1 + R3 au rendu public ; gain R5 uniquement en handoff conceptuel (filtré au rendu par `isRenderableLinkAllowed`, conformément à ADR-027).
- **Observabilité prod en temps réel** : métrique `seo_handoff_filtered` permet le pilotage empirique des futurs amendements canon (`feedback_decision_must_be_signal_proven_not_intuited`).
- **Forward-compat PR-A.bis** : architecture TS canon-consumable, prête pour migration `canon.json` future.

### Négatives / risques

- **Régression backend silencieuse** : tests `internal-linking.service` qui s'appuyaient sur l'ancienne matrice ad-hoc cassent. Mitigation : tests régression `page-role-links.test.ts` exhaustifs vs canon (alignement testé empiriquement).
- **Amendement canon R6 → R1 perçu comme overreach hors gouvernance** : justification empirique documentée ici (asymétrie + mission planner.md). Reviewer canon (owner R6 + governance) peut bloquer ou valider sur preuve.

## Compliance / patterns

- ADR-046 § L1.5 CONTRACTS — extension du canon SEO via mirror typé.
- `feedback_canon_rule_live_iff_adr_accepted` — chantier LIVE ssi ADR.status=accepted.
- `feedback_no_hybrid_workarounds` — pas de bricolage, suppression backend ad-hoc remplacée par canon.
- `feedback_no_questionnaire_propose_best` — R1 ∈ R6 auto-tranché sur preuve empirique.
- `feedback_decision_must_be_signal_proven_not_intuited` — observabilité prod active dès merge pour piloter futurs amendements.
- `feedback_no_bricolage_align_existing_contract` — chain v9 service consommera le canon (follow-up) au lieu de réimplémenter sa logique `FORBIDDEN_ROLE`.
- `feedback_branch_scope_discipline` — branche `feat/seo-roles-handoff-graph` depuis `main` (pas depuis cascade seo-v9-prX).

## Follow-ups

- Migration Prometheus : PR infra séparée post-merge (installer `prom-client` + `/metrics` endpoint + migrer `SeoHandoffMetricsService` Map → Counter).
- Chain v9 `seo-internal-linking.service.ts` : intégrer `isRenderableLinkAllowed` lors de la cascade seo-v9 ou via PR follow-up.
- Frontend identité drift R6 : débloquer après migration DB historique (cf ADR-051 PR-E precondition).
- r5 contract : owner R5 follow-up (`prompts/R5_DIAGNOSTIC/contract.md` source documentaire existante).
- Drift sémantique r6.ts contract `semantic_intents`.

## Self-review verdict: APPROVE
