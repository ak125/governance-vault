---
name: supabase-cost-surface-drift-v1
description: Méthodologie V1 du workflow vault-supabase-cost-check (refonte 2026-05-18) — structural drift detection sur la cost surface Supabase, sans projection $ (Management API ne l'expose pas).
type: knowledge
status: canon
date: 2026-05-18
related_adr: ["ADR-028", "ADR-034"]
related_workflows: [".github/workflows/vault-supabase-cost-check.yml"]
related_knowledge: ["supabase-management-token"]
supersedes_method: "USD projection via /v1/organizations/{ref}/billing/subscription (endpoint inexistant — 404 confirmé 2026-05-18, 3 lundis d'échec silencieux 2026-05-04, 05-11, 05-18)"
---

# Supabase Cost Surface Drift Detection (V1)

## Pourquoi cette refonte

Le workflow `vault-supabase-cost-check.yml` (livré 2026-04-30) appelait `GET /v1/organizations/{ref}/billing/subscription` puis tentait d'extraire `plan_price` pour comparer à un seuil $30/mois. Vérification empirique 2026-05-18 (Context7 sur `/websites/api_supabase_v1`) :

> Aucun endpoint Management API v1, à n'importe quel scope (org-scoped ou project-scoped), n'expose un montant USD pour un plan, un add-on, ou un usage. Les seuls endpoints sous `/v1/organizations/{slug}/...` sont `entitlements`, `members`, `projects`. Sous `/v1/projects/{ref}/billing/...` : uniquement `addons` (variantes, pas prix $).

Conséquence : la spec V1 d'origine ("projeter le coût mensuel en USD") n'était pas implémentable. Symptômes observés :

- Run 2026-05-04 : ❌ failure (HTTP 404)
- Run 2026-05-11 : ❌ failure (HTTP 404)
- Run 2026-05-18 : ❌ failure (HTTP 404 — issue détectée + refonte)

## Principe V1 (refonte)

La **cost surface** Supabase = `(plan tier, projects, per-project add-ons)`. Tout dérapage tarifaire significatif passe par une mutation de cette surface :

| Mutation détectée | Effet $ | Severity | Rationale |
|---|---|---|---|
| Plan tier ↑ (free→pro→team→enterprise) | +$25 → +$574/mois selon transition | **P1** | Plus grand levier de coût. Free=$0, Pro=$25, Team=$599, Enterprise=custom (prix indicatifs 2026-05, à valider Dashboard) |
| Add-on ajouté (Branching / IPv4 / Read Replica / PITR) | +$10 → +$100/mois par add-on | **P1** | **Critique** : ces add-ons ne sont PAS couverts par le Spend Cap Supabase. Branching seul peut dériver >$50/mois (compute + disk + egress) sans alerte |
| Project ajouté | +$0 (Free) ou +$25 (Pro) selon tier | **P2** | Informational |
| Add-on supprimé | -$ | **P2** | Informational (vérifier intentionnel) |
| Project supprimé | -$ | **P2** | Informational (vérifier intentionnel) |
| Plan tier ↓ | -$ (significatif) | **P1** | Anomalie — vérifier humainement (downgrade non sollicité = signal d'incident billing) |
| Hash diff sans cause classifiée | mineur | **P2** | opt_in_tags ou metadata projet a bougé — inspecter le diff canonique |

Le workflow capture un snapshot canonique JSON chaque lundi, le compare au snapshot de la semaine précédente (artifact 90j retention), et ouvre une issue P1/P2 sur toute mutation détectée. **Pas de projection $ — délibérément déconnecté du dollar.**

## Defense-in-depth (5 couches)

| Couche | Mécanisme | Localisation | Ce qu'elle couvre |
|---|---|---|---|
| 1 | Supabase Dashboard Spend Cap (hard ceiling) | out-of-CI (configuré par org owner dans Dashboard) | hard cap sur usage-based billing standard (compute Pro, egress, storage) |
| 2 | Email alert Supabase à 80% du Spend Cap | out-of-CI (Dashboard notifications) | early warning sur usage runaway dans le scope du Cap |
| 3 | **Ce workflow** — structural drift audit | in-CI, hebdomadaire (lundi 08:00 UTC) | mutations délibérées de la surface — couvre les **angles morts du Spend Cap** : Branching, IPv4, Read Replica, PITR (non inclus dans Cap) |
| 4 | Artifact replay (snapshots canoniques sha256 stables, 90j) | in-CI | audit-trail rejouable (ADR-034 axis 3 Evidence) |
| 5 | Revue manuelle trimestrielle Dashboard | out-of-CI (org owner) | sanity check humain + ajustement seuils Cap + revue add-ons orphelins |

**Aucune couche n'est suffisante seule.** Le Spend Cap natif (couche 1) ne couvre pas les 4 add-ons les plus coûteux — c'est ce que la couche 3 attrape structurellement.

## Endpoints utilisés (Management API v1, vérifiés 2026-05-18)

```
GET /v1/organizations/{slug}            → { id, name, plan, opt_in_tags, allowed_release_channels }
GET /v1/organizations/{slug}/projects   → [ { id, name, region, status, created_at }, ... ]
GET /v1/projects/{ref}/billing/addons   → { selected_addons: [ { variant, name, price_description, ... } ] }
```

Token scope requis : **`organizations:read` + `projects:read`**. Le scope `organizations:read` seul est insuffisant pour `/v1/projects/{ref}/billing/addons` (project-scoped). Le workflow tolère un HTTP 403 sur cet endpoint (free-tier projects sans permission) en le normalisant en `selected_addons: []`.

## Canonical snapshot (replay-safe deterministic hash)

Format JSON ordonné (clés triées via `jq -cS`, arrays triés par identifiant stable) **excluant les champs per-run mutables** (`snapshot_date`) pour garantir un hash sha256 reproductible — pattern aligné avec les principes de hash canonique pour SoT/replay (fast-json-stable-stringify equivalent en jq).

Structure (le timestamp est conservé dans le fichier mais exclu du hash) :

```json
{
  "snapshot_date": "2026-05-18T11:30:00Z",
  "schema_version": "v1",
  "org": {
    "id": "fezyshchnnrwwpnzbcwb",
    "name": "ak125's Org",
    "plan": "pro",
    "opt_in_tags": [...],
    "allowed_release_channels": [...]
  },
  "projects": [ { "id": "cxpojprgwgubzjyqzmoq", "name": "massdoc", "region": "...", "status": "...", "created_at": "..." } ],
  "addons": { "cxpojprgwgubzjyqzmoq": [ { "variant": "ipv4", "name": "...", "price_description": "..." } ] }
}
```

Deux fichiers uploadés en artifact :

- `snapshot.redacted.json` — pretty-printed, **inclut** `snapshot_date` (lisibilité humaine + audit-trail), champs `token|secret|key|password|refresh|access` masqués par paranoïa
- `snapshot.canonical.json` — compact, clés triées, `snapshot_date` exclu — base du hash sha256

Hash calculé via :

```bash
jq -cS 'del(.snapshot_date)' snapshot.redacted.json | sha256sum
```

Comparaison de runs : le hash précédent est **re-dérivé** à la volée depuis le `snapshot.redacted.json` du run précédent (avec les règles d'exclusion courantes), pour rester robuste si les règles évoluent dans une version future. C'est l'idempotence key : `prev_hash == current_hash` → no drift, exit green sans ouvrir d'issue.

### Découverte empirique 2026-05-18 (fix hash-stability)

Le premier run sur main (run #26032073924) a ouvert un faux-positif issue #293 (P2 `unknown-drift`) parce que `snapshot_date` était initialement inclus dans `snapshot.canonical.json`. Deux runs avec données identiques mais snapshots horodatés différemment → hashs différents → fallback "unknown-drift" tirait. Corrigé par exclusion du timestamp ; issue #293 close comme false-positive lié à la transition.

## Pourquoi pas une projection $ V1 hardcodée

Tentative naïve rejetée : mapper `{ free: 0, pro: 25, team: 599 }` en dur dans le workflow. Rejetée car :

1. **Drift de prix Supabase** : si Supabase change un prix (ils l'ont fait — Pro est passé de $20 à $25), le workflow ment silencieusement.
2. **Add-ons non hardcodables** : Branching plancher $10/mois mais réaliste $10-$50+/mois (compute + disk + egress variables). Hardcoder une fourchette est faux par construction.
3. **Anti-bricolage** : monter d'un cran à "structural drift" est l'approche FinOps industry-standard pour SaaS spend governance — c'est ce que font CloudZero, Vantage, OpenCost (drift de configuration de coût, pas projection $).

La valeur $ exacte est consultée manuellement sur `https://supabase.com/dashboard/org/{slug}/billing` lors de l'instruction d'une issue P1/P2. Le workflow signale la nécessité de cette consultation ; il ne prétend pas la remplacer.

## V2 (futur, non planifié — 4 gates cumulatifs avant escalation)

Conditions cumulatives pour considérer V2 (alignement V1-first discipline) :

- [ ] V1 stable 6 mois (≥24 runs verts hebdomadaires OU toutes alertes P1/P2 émises confirmées légitimes a posteriori)
- [ ] Au moins 2 incidents documentés où V1 a manqué une dérive de coût pourtant détectable
- [ ] Demande explicite et motivée d'un signal $ (pas juste "ce serait sympa")
- [ ] Endpoint Management API stable et documenté qui expose un $ — OU webhook Stripe authentifié, OU export Dashboard automatisable (à ce jour : aucun)

V2 envisagé seulement si les 4 sont remplis. Pistes :

- Signature Stripe webhook → vault ingest (si Supabase facture via Stripe, à vérifier)
- Scraping documenté/officiel du Dashboard billing
- Ouverture d'un ticket Supabase pour exposer un endpoint billing officiel

## Hygiene & rotation token

Le secret `SUPABASE_ACCESS_TOKEN` doit être un PAT Management API dédié, scope minimum `organizations:read + projects:read`, sans aucun scope write. Détails de provisioning et rotation : voir `supabase-management-token.md`.

## Références

- ADR-028 — `ledger/decisions/adr/ADR-028-preprod-supabase-isolation.md`
- ADR-034 — `ledger/decisions/adr/ADR-034-aicos-operating-contract.md`
- Workflow : `.github/workflows/vault-supabase-cost-check.yml`
- Token rules : `ledger/knowledge/supabase-management-token.md`
- Doc Supabase Management API v1 : https://api.supabase.com/api/v1/redoc
- Pattern FinOps SaaS spend governance : structural cost-surface drift detection (vs $ projection)
