---
type: audit-trail
status: canon
date: 2026-05-10
updated: 2026-05-10
related: [ADR-015, ADR-020]
audit_scope: vault-pr-backlog
---

# Vault PR Backlog Triage — 2026-05-10

PR-6 de la série « Vault Documentaire → Vault Exécutable ». Mini-PR audit-trail
signée G3 documentant l'état du backlog PR vault au moment de l'ouverture de
la cascade PR-1..3 (#247-#250). **Aucune action destructive** : ce document
inventorie, recommande, n'exécute pas. Décisions de close/merge restent sous
contrôle humain.

## Contexte

Le passage en mode « vault exécutable » (CI gate strict via PR-4 à venir)
nécessite que le backlog PR converge. Les PRs CONFLICTING accumulent du drift
qui sera de plus en plus coûteux à résoudre une fois le strict gate actif.

## Inventaire empirique (2026-05-10)

| Métrique | Valeur |
|----------|-------:|
| Total PRs ouvertes | **38** |
| Âge max | 22j |
| Âge médian | 6j |
| ≥30 jours | 0 |
| 14-29 jours (stale) | 9 |
| <14 jours (recent) | 29 |
| Mergeables | 20 |
| **CONFLICTING** | **18** |
| UNKNOWN | 0 |

## Findings catégorisés

### 🔴 CONFLICTING (18 PRs) — action requise

Ces PRs ne mergent plus contre `main` actuel. Pour chacune :
1. Lire la PR + comprendre l'intention.
2. Décider : (A) rebase + résoudre conflits, (B) close si obsolète, (C) close + ré-ouvrir mini-PR ciblée si scope a dérivé.

| # | Âge | Titre tronqué | Action recommandée |
|---|----:|---------------|---------------------|
| #9 | 22j | INC-2026-003 diagnostic engine seeding | (B) close si incident résolu, sinon (A) rebase |
| #13 | 20j | audit-trail VehicleSelector + ⌘K (PR #85) | (B) close si feature livrée, sinon (A) rebase |
| #59 | 16j | investigation R8 enricher vehicle-not-found (ADR-022) | (B) close — ADR-022 superseded by ADR-031 |
| #70 | 15j | vehicle-selector Radix Select + grouped fuel pattern | (A) rebase si pattern toujours canon |
| #75 | 14j | claude-code-skill-modular-pattern | (A) rebase ou (C) ré-ouvrir avec scope précis |
| #88 | 13j | 2026-04-25 fleet advisor + seo monitoring session recap | (B) close — audit-trail historique, pas urgent |
| #92 | 13j | r8 distinct render + scraping canon (2026-04-25) | (B) close — info dans MEMORY, pas vital |
| #114 | 9j | session 2026-04-30 repivot ADR-028 | (A) rebase, ADR-028 toujours active |
| #131 | 8j | 2026-05-01 Roadmap canonisée + Chantier C READY | (B) close — Roadmap shippée par PR #128 |
| #173 | 4j | R3GuideController backend rename → R3Conseils* | (A) rebase, vérifier si proposal toujours pertinente |
| #196 | 3j | ratify seo-role-contracts canon + quality history ADR | (A) rebase prioritaire, base de PR-3b future |
| #220 | 2j | sprint perf bundle 7 leçons signal-proven | (A) rebase, knowledge utile |
| #217 | 2j | priority planning vault pending work + ADR-051 collision | (A) rebase, lien direct au planning live ADR-053 |
| #214 | 2j | ADR-052 SQL role canon deprecation, defer to TS-only | (A) rebase, scope ADR-040 toujours actif |
| #213 | 2j | R6 canon cascade shipped — 4 PRs + ADR-051 | (A) rebase, audit-trail récent |
| #211 | 2j | ADR-051 frontend bundle budget enforcement | (A) rebase, ADR ratifie un budget actif |
| #242 | 1j | ADR-054 convention governance standard audit-trail | (A) rebase prioritaire (ADR governance) |
| #235 | 1j | seo-v9 cascade state PR-2c shipped | (A) rebase trivial, knowledge vivant |

### 🟢 MERGEABLE — review pending (20 PRs)

Inclut la cascade PR-1..3 ouverte aujourd'hui (#246/#247/#248/#249/#250) +
15 PRs antérieures mergeables. Pour celles >7j sans review :
- **#22, #29, #72, #64** (15-19j) : prêtes à merge après review humaine
- **#136, #149, #151** (6-8j) : idem
- **#240, #241** (2j) : ratifications ADR récentes, prioritaires

## Recommandation globale (anti-drift)

**Phase 1 (immédiate, manuelle)** : trier les 18 CONFLICTING en 3 batches
sequentiels :
1. **Close batch** (5-7 PRs) : les audit-trails / handoffs d'info déjà capturée
   en MEMORY ou dans des PRs ultérieures.
2. **Rebase batch** (8-10 PRs) : les ADRs/knowledge encore pertinents,
   priorité aux ADR-* récents.
3. **Refactor batch** (1-3 PRs) : scope dérivé → close + ré-ouvrir mini-PR.

**Phase 2 (post PR-4 strict gate)** : aucun nouveau PR conflicting toléré
plus de 7j ouverts → règle CI ou flag manuel.

**Phase 3 (cron VPS DEV optionnel)** : script `cron-pr-backlog-alert.sh`
qui émet un warning hebdomadaire si CONFLICTING_COUNT > 5 ou STALE_30D > 0.
Pas dans cette PR — follow-up.

## Pourquoi pas d'action destructive ici

Per CLAUDE.md / `feedback_sandbox_destructive_actions` : fermer une PR est
une action destructive (perte de discussion, attribution, contexte historique).
Ce document **inventorie et recommande**, le humain (Fafa) tranche close vs
rebase pour chaque PR au cas par cas. Aucun script automatique ne fermera
de PR sans intervention manuelle explicite.

## Dépendances

- Cette PR est **parallèle** à PR-1..4 (pas de stack, base = main).
- Mergeable indépendamment.
- Aucun impact runtime sur le vault (pure documentation audit).

## Verification

```bash
# Reproduce l'inventaire
gh pr list --repo ak125/governance-vault --state open \
  --json number,title,createdAt,mergeable --limit 50 \
  | jq 'group_by(.mergeable) | map({status: .[0].mergeable, count: length})'
```

## Self-review verdict: APPROVE
