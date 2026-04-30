---
type: session-trail
status: canon
date: 2026-04-30
related_adr: [ADR-028, ADR-030]
related_pr: [governance-vault#111-closed-superseded, nestjs-remix-monorepo#223, automecanik-rag#6]
related_plan: /home/deploy/.claude/plans/harmonic-mapping-elephant.md
related_rules: [G2-zero-orphelin, G3-signed-commits, AEC-v1.0.0]
---

# Session-trail — Audit système 6 points → repivot Option C → Option D

## Contexte

Le 2026-04-30 l'utilisateur a soumis un audit en 6 points du monorepo `nestjs-remix-monorepo` + repo RAG (état des gates dependency-cruiser, TS strict backend, Dockerfile, `ALLOW_PROD_ENV_COPY=1`, Weaviate, RAG eval). L'agent a livré 3 PRs en parallèle (vault, monorepo, rag). L'utilisateur a fermé la PR vault pour scope mixing et **repivoté la stratégie d'isolation préprod** après audit plus profond du workflow réel : Option C (Supabase branch $9.66/mois) → **Option D read-only hardening à $0/mois**.

Ce document trace l'itération pour que les sessions futures comprennent les pivots et n'incrémentent pas une dette qui a été explicitement rejetée.

## Itérations du plan (rev 1 → rev 2 → rev 3)

| Rev | Origine | Diagnostic | Action | Status |
|-----|---------|-----------|--------|--------|
| 1 | Agent | "Remplacer `ALLOW_PROD_ENV_COPY` par secrets `PREPROD_*`" | Plan superficiel proposé | Refusé par utilisateur ("no bricolage analyser en profondeur") |
| 2 | Agent (analyse profonde) | Découverte : `backend/.env` et `backend/.env.production` pointent vers le **même projet Supabase `cxpojprgwgubzjyqzmoq`** → préprod et prod partagent la DB. Plan recommande **Option C : Supabase branch $9.66/mois** | 3 PRs livrées (vault #111, monorepo #223, rag #6) | Vault #111 **fermée** (scope mixing) ; #223 et #6 restent valides |
| 3 | Utilisateur (audit plus profond du workflow réel) | Le risque "preprod écrit prod" est **théorique, jamais observé** car (a) workflow DEV humain pointe **délibérément** prod pour vérif live des modifs, (b) `ci.yml:700-799` smoke = read-only GET only (`/health`, `/api/catalog/families`, `/`, `/pieces/catalogue`, admin guards) — aucune migration auto, aucun seed, aucun POST/PUT/DELETE, (c) Compute Branching pas couvert par Spend Cap (surfacturation latente possible >$50/mois) | **Option D — read-only hardening à $0/mois** via 5 couches de défense | Plan canon `/home/deploy/.claude/plans/harmonic-mapping-elephant.md`, 3 PRs successeurs en flight |

## Ce que l'utilisateur a livré (Plan rev 3)

Plan `harmonic-mapping-elephant.md` — 4 PRs séquencées :

| PR | Scope | Dependency |
|----|-------|------------|
| **PR 1** vault | ADR-030 "AI-COS Operating Contract" (observatoire, pas orchestrateur) + AP-XX rule | first to merge (fixe doctrine avant implémentation) |
| **PR 2** monorepo | `ci.yml:700-730` read-only hardening : retire `ALLOW_PROD_ENV_COPY`, retire `SUPABASE_SERVICE_ROLE_KEY` du job, génère `.env.preprod` minimal avec anon key + `READ_ONLY=true` | après PR 1 |
| **PR 3** vault | ADR-028 reviser proposed → accepted (Option D, "fortement réduit" pas "éliminé") + MOC-Decisions update | après PR 2 mergé (statut accepted = implémentation prouvée) |
| **PR 4** vault | ADR-031 npm-ignore-scripts standalone (parallel mergeable) | indépendant |

5 couches de défense Option D (preuve, pas garantie absolue) :

| Couche | Rôle | Garantie |
|--------|------|----------|
| 1. Pas de SERVICE_ROLE_KEY en preprod | Privilege downgrade | Forte |
| 2. Anon key only | Auth limitée | Forte si clé pas leakée |
| 3. RLS hardening (ADR-021, 204 objets) | DB-level enforcement | Forte sur tables hardenizées, **risque résiduel** sur tables créées post-PR #42 sans RLS |
| 4. READ_ONLY guard backend | Couche applicative ceinture+bretelles | Dépend couverture grep |
| 5. write-detect log scan job CI | **Détection**, pas garantie | Capture patterns SQL grossiers, pas tout |

## Apprentissages livrés (mémoires utilisateur mises à jour)

1. **`feedback_no_bricolage_analyse_profondeur.md`** — addendum : avant tout billing/infra-add, faire un audit *workflow réel* (ce qui se passe en pratique, pas ce que le code permet en théorie). Un risque doit être au moins **observé une fois** ou **structurellement présent dans les chemins exécutés** (pas seulement "possible en théorie") avant de mériter une infrastructure pour le mitiger.

2. **`feedback_branch_scope_discipline.md`** — addendum : 1 PR = 1 ADR OU 1 audit OU 1 rule update, jamais 2 ensemble même si thématiquement liés. Test mental : "Si seulement la moitié de cette PR doit être annulée, est-ce facile ?" Si non → split. Incident vault PR #111 (audit-trail + ADR-028 + ADR-030 bundlés) → fermée + supersede en 3.

## Outcome

- **Vault PR #111** : closed by `ak125` à 2026-04-30T13:21:29Z, commentaire de supersede détaillé, 3 PRs successeurs en flight
- **Monorepo PR #223** (`feat/p1.1-report-violations-workflow`) : reste **OPEN, scope-clean** (1 workflow report-violations.yml = mesure depcruise + tsc nightly self-hosted, non bloquant) — utile indépendamment du repivot car alimente PR P1.2/P1.3 du plan original (bump `warn → error` après mesure)
- **RAG PR #6** (`feat/p1.4-rag-eval-nightly-schedule`) : reste **OPEN, mergeable, scope-clean** (schedule cron + self-hosted runner pour atteindre RAG localhost) — utile indépendamment, monitoring continu
- **Coût net économisé** : ~$120/an (12 × $9.66) en évitant Supabase branch + complexité opérationnelle (pause/resume, reset périodique, drift schema)

## Actions de suivi (responsabilité utilisateur)

- Créer les 3 PRs successeurs selon plan rev 3 (PR 1 ADR-030 → PR 2 ci.yml → PR 3 ADR-028 reviser → PR 4 ADR-031)
- Vérifier branche orpheline `feat/adr-028-030-preprod-isolation` côté GitHub (PR closed mais branche reste) — à supprimer si non réutilisée

## Coverage manifest (Agent Exit Contract v1.0.0)

| Champ | Valeur |
|-------|--------|
| `scope_requested` | Consigner l'itération session 2026-04-30 dans le vault |
| `scope_actually_scanned` | 3 itérations du plan (rev 1/2/3) + 3 PRs livrées + 1 closed-superseded + 2 mémoires updated |
| `files_read_count` | ~25 (claims audit + ci.yml + .env files + docker-compose RAG + Supabase MCP + workflows + MOC files) |
| `excluded_paths` | Implémentation des 3 PRs successeurs (responsabilité utilisateur) ; détails contenu ADR-030 AI-COS (sera dans la PR 1) ; coverage grep `READ_ONLY` (sera dans PR 2) |
| `corrections_proposed` | Repivot Option C → Option D (porté par utilisateur, pas par agent) |
| `corrections_applied` | 2 mémoires utilisateur updated, ce session-trail consigné |
| `remaining_unknowns` | Calendrier de merge des 3 PRs successeurs ; numérotation finale npm-ignore-scripts ADR (031 ou autre selon décision PR 4) |
| `final_status` | `SCOPE_SCANNED` — itération consignée, ownership transféré utilisateur |
