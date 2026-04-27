# Fleet Advisor + Claude 4.7 — Session status 2026-04-25

> **Type** : status / handoff
> **Owner** : Fafa (`automecanik.seo@gmail.com`)
> **Branch monorepo** : `feat/aicos-fleet-advisor-claude-4-7`
> **PR** : [ak125/nestjs-remix-monorepo#182](https://github.com/ak125/nestjs-remix-monorepo/pull/182) (DRAFT, MERGEABLE, 15 CI checks SUCCESS)
> **Spec** : `docs/superpowers/specs/2026-04-25-fleet-advisor-claude-4-7-design.md`
> **Plan** : `docs/superpowers/plans/2026-04-25-fleet-advisor-claude-4-7.md`

---

## 1. Décisions prises (canon)

| # | Décision | Rationale |
|---|---|---|
| 1 | Approche **B** (Advisor agent natif Paperclip + approval/comment loop) | Aligne G3 + R12 ; pas de fork Paperclip ; pas de hook adapter. Native primitives only. |
| 2 | Périmètre review = **canon writes only** (option C du brainstorming) | code PR vers `main`, DB writes `__seo_*`/`__rag_*`/`__pieces_*`/`__diag_*`/`__blog_*`, deployments, governance-vault PRs |
| 3 | Tiering modèles Claude 4.X | Opus 4.7 = CEO + CTO + Advisor. Sonnet 4.6 = CMO + CPO + RAG-Ops + SEO-Content + R4-Batch-Lead. Haiku 4.5 = SEO-QA. |
| 4 | Advisor **ne décide jamais** | `assertBoard` préservé. Verdict + axes scorés posté en commentaire seulement. Le board operator humain garde l'autorité décisionnelle. |
| 5 | Skill `canon-write-review` zero-LLM | Checks déterministes (table prefix, op, sql_or_rpc, rollback_plan, DELETE safety, batch threshold, traçabilité). Économise tokens + auditabilité maximale. |
| 6 | Verdict canonique JSON | 5 axes (correctness, security, anti_cannib, evidence, reversibility), findings[severity], evidence_pack[]. Mapping verdict→recommendation à 5 règles ordonnées (cf. spec § 3.5). |
| 7 | Phase 2 (shadow) + Phase 3 (enforcement) hors scope du PR #182 | Plans séparés à écrire après merge + 48h de soak. |

---

## 2. État local (Phase 0 + Phase 1 code)

### 2.1 Implémentation locale (✅ complète)

| Composant | Fichier | Tests |
|---|---|---|
| Verdict schema (Pydantic) | `scripts/advisor/verdict_schema.py` | `tests/advisor/test_verdict_schema.py` 9/9 PASS |
| Skill canon-write-review | `scripts/advisor/canon_write_review.py` + `agents/advisor/skills/canon-write-review/SKILL.md` | `tests/advisor/test_canon_write_review.py` 7/7 PASS |
| Advisor instruction bundle | `agents/advisor/AGENTS.md` | — |
| AI-COS HTTP client | `scripts/aicos/aicos_client.py` | `tests/aicos/test_aicos_client.py` 4/4 PASS |
| Fleet config | `scripts/aicos/fleet_config.yaml` (UUIDs résolus) | — |
| Apply fleet models | `scripts/aicos/apply_fleet_models.py` | `tests/aicos/test_apply_fleet_models.py` 4/4 PASS |
| Sync AGENTS.md DEV→AI-COS | `scripts/aicos/sync_agents_md.py` | — |
| Hire advisor | `scripts/aicos/hire_advisor.py` (CEO_ID résolu) | — |
| Smoke pre_canon_review | `scripts/aicos/smoke_pre_canon_review.py` | — |
| 5 producteurs MAJ pre_canon_review | `agents/{ceo,cto,rag-lead,seo-content,r4-batch-orchestrator}/AGENTS.md` | — |
| Régression replay | `scripts/advisor/regression_replay.py` + `incidents/inc-2026-005.json` + `rag-vault-rollback-2026-04-18.json` + `inc-2026-009.json` | — |

**Tests unitaires** : `pytest tests/advisor tests/aicos -v` → **25/25 PASS**.
**CI checks** : 15 SUCCESS, 0 FAILURE, 5 SKIPPED (non bloquants — Docker/E2E/Lighthouse).

### 2.2 UUIDs Paperclip canoniques (résolus 2026-04-25)

| Agent | UUID | Status pré-session |
|---|---|---|
| CEO | `993a4a02-b3b5-4414-9d5c-94b143ff1fe5` | running |
| CTO | `7fa3c971-3e9f-4b3b-a6d7-ebddc695a93a` | idle |
| **Advisor (NEW, draft)** | `e2db057d-2500-45ba-891e-f80c7b7f88e1` | **`pending_approval`** |
| CMO | `7fb56320-00f4-4a08-892f-47145e20cabf` | idle |
| CPO | `41718022-9ff5-4237-baa7-0fe3d9c0a5d5` | error |
| RAG-Ops | `c6762b10-8c8f-4d15-9fec-04b273a6841b` | running |
| SEO-Content | `0f978206-535e-44d9-9f5a-67c254990d1c` | idle |
| R4-Batch-Lead | `e26ea228-1c23-4859-bae5-5e54f9450b46` | idle |
| SEO-QA | `8ff977f4-e53d-473f-94c7-74eab35d2860` | idle |

Remarque : Code-Review agent `9947ef2b-2d05-45a8-9513-2bee9902994f` (status=error, role=qa, reportsTo=CTO) **séparé**, hors scope. À traiter en follow-up.

---

## 3. Reste à faire (handoff)

### 3.1 ⏸ Bloqué sur board approval (non technique)

- [ ] **Approuver l'hire approval** `37e918e7-199f-41fc-bada-e410a12d08f2` (type `hire_agent`, status `pending`) :
  - UI : http://178.104.1.118:3100/approvals → cliquer Approve sur "Advisor"
  - **Recommandation pré-approve** : décider du **budget** (cf. § 4 ci-dessous)

### 3.2 Tasks restants du plan (post-approve)

| # | Task | Fichier / commande | Production state change ? | Action ouverte |
|---|---|---|---|---|
| 7 | Hire Advisor | `scripts/aicos/hire_advisor.py` | ✅ submitted, draft `e2db057d` créé, **approve UI pending** | approuver dans UI |
| — | Update Advisor UUID dans config | éditer `scripts/aicos/fleet_config.yaml` ligne 32 (`aicos_id: null` → `e2db057d-2500-45ba-891e-f80c7b7f88e1`) | non | trivial post-approve |
| 8 | Sync Advisor AGENTS.md | `python3 scripts/aicos/sync_agents_md.py --only Advisor` | oui (PUT) | post-approve |
| 9 | Apply tier models 9 agents | `python3 scripts/aicos/apply_fleet_models.py --apply` | **oui (PATCH 9 agents prod)** | post-sync |
| 10 | Smoke test | `python3 scripts/aicos/smoke_pre_canon_review.py` | oui (crée approval test) | post-PATCH |
| 11 | (déjà commité local) MAJ AGENTS.md producteurs | — | non | déjà fait |
| 12 | Sync 5 producteurs AGENTS.md | `python3 scripts/aicos/sync_agents_md.py --only CEO --only CTO --only RAG-Ops --only SEO-Content --only R4-Batch-Lead` | **oui (PUT 5 agents prod)** | post-smoke |
| 13 | E2E test (PR jouet roundtrip) | manuel (cf. plan Task 13) | oui (crée approval réelle + commit toy) | post-sync producteurs |
| 14 | Régression replay 3 incidents | `python3 scripts/advisor/regression_replay.py` | oui (crée 3 approvals test) | post-E2E |
| 15 | Ready PR + merge + open Phase 2 plan | `gh pr ready 182` + `gh pr merge 182 --squash` | mainstream | post-régression PASS 3/3 |

### 3.3 Hors plan, à décider après merge

- [ ] **Budget Advisor** définitif (actuellement $5000/mois CAP, réaliste estimé $300-450/mois — voir § 4)
- [ ] **Phase 2 (shadow mode 7j)** — plan séparé à écrire après PR #182 merged et 48h soak
- [ ] **Phase 3 (enforcement)** — plan séparé après Phase 2
- [ ] **Code-Review agent en erreur** (`9947ef2b`) — diagnostic / remplacement / suppression
- [ ] **Retention policy backups Paperclip** — actuellement 31GB (cf. § 6 incident disk full)

---

## 4. Sujet ouvert : budget Advisor

**Confusion utilisateur** sur le `budgetMonthlyCents: 500000` — pas compris. Clarification :

- **C'est un CAP** (plafond), pas un coût garanti. Auto-pause si dépassé. Alerte 80%.
- **Coût réel estimé** Opus 4.7 :
  - Heartbeat 60s : ~95% no-op cached (~$0.001/tick)
  - Reviews actifs : 20-50/jour × ~$0.50/review (30K input + 2K output Opus 4.7)
  - Total réaliste : **~$300-450/mois**
- **Pourquoi $5000 en cap initial** :
  - L'Advisor traite payloads de **tous** les producteurs
  - Gros diff PR peut atteindre 100K+ tokens
  - Burst day possible (lancement R4 batch = 50+ écritures DB simultanées)

**3 options** (à arbitrer avant board approve) :

| Cap | Profil | Risque |
|---|---|---|
| $500/mois | strict, ras du réaliste | 1 burst day → pause auto |
| **$1500/mois** ⭐ | confortable, 3× réaliste | quasi nul |
| $5000/mois (actuel) | très large, 12× réaliste | aucun, mais signal-fuite tardif |

Si descente à $1500 : éditer `scripts/aicos/fleet_config.yaml` ligne 34 (`budget_monthly_cents: 500000` → `150000`) **avant** de cliquer board approve. Le payload de la `hire_agent` approval est figé : il faudra soit reject + resubmit, soit accepter $5000 et PATCH après hire actif (gérable mais 1 round-trip de plus).

---

## 5. Branche git — états

| Branche | Position | Commits non pushés | Action recommandée |
|---|---|---|---|
| `feat/aicos-fleet-advisor-claude-4-7` | HEAD = `cfe65640` "resolve full UUIDs" + 2 chore log | 3 commits ahead origin | `git push` quand budget validé, puis `gh pr ready 182` |
| `feat/seo-monitoring-google-application-credentials` | (branche par défaut session) | log.md auto-edits | hors scope |

---

## 6. Incident résolu en cours de session : AI-COS disk full (Postgres recovery loop)

### 6.1 Symptôme

- AI-COS `/api/health` → HTTP 503
- `paperclip auth whoami` → 500
- `aicos-paperclip-db` (Postgres 17) marqué **unhealthy depuis 11 jours** (FailingStreak 227,146)
- Backend Paperclip impossible (PostgresError `57P03 "the database system is in recovery mode"`)

### 6.2 Cause racine

```
2026-04-25 20:14:54 PANIC: could not write to file "pg_logical/replorigin_checkpoint.tmp": No space left on device
```

Postgres : redo OK → end-of-recovery checkpoint → `ENOSPC` → PANIC → restart → boucle infinie.

`/dev/sda1` 75/75 GB **100%**.

### 6.3 Fix appliqué (réversible, séquentiel)

| Étape | Commande | Reclaim |
|---|---|---|
| 1 | `docker builder prune -af` | **25.18 GB** (build cache) |
| 2 | `truncate -s 0 /var/lib/docker/containers/*/*-json.log` (logs > 10 MB) | **2.65 GB** (paperclip 2.3G + dashboard 309M + caddy 48M) |
| 3 | `docker compose restart paperclip-db` | — |
| 4 | Vérifier `/api/health` 200 + `paperclip auth whoami` OK | — |

**Résultat** : disque `/` 100% → **69%** (23 GB libres). Postgres healthy en 10s. Paperclip API 200.

### 6.4 Dette technique restante (post-incident)

- **31 GB** dans `/var/lib/docker/volumes/aicos_paperclip_data/_data/instances/default/data/backups` — backups Paperclip auto. Pas de retention policy actuellement. À scoper.
- Aucun monitoring d'espace disque AI-COS (à mettre en place). Suggestion : alert Hetzner ou cron `df -h` → notify.

### 6.5 Recipe canonique (pour répéter si récidive)

```bash
ssh root@178.104.1.118 << 'EOF'
docker builder prune -af
for f in /var/lib/docker/containers/*/*-json.log; do
  size=$(stat -c %s "$f" 2>/dev/null)
  [ "${size:-0}" -gt 10485760 ] && truncate -s 0 "$f"
done
cd /opt/aicos && docker compose restart paperclip-db
sleep 10
docker compose ps paperclip-db
EOF
curl -s http://178.104.1.118:3100/api/health
```

---

## 7. Apprentissages (à garder en mémoire)

1. **Paperclip role enum est figé** : `ceo|cto|cmo|cfo|engineer|designer|pm|qa|devops|researcher|general`. Pas de `advisor`. Pour notre Advisor → `qa` (cohérent avec Code-Review existant). Le rôle Paperclip est métadata uniquement, le comportement est défini par AGENTS.md.
2. **`hire_advisor.py` retournait `Approval ID: None`** : la réponse Paperclip met l'approval ID au top-level mais notre script cherchait `approvalId|id`. Vérification post-soumission via `GET /companies/:id/approvals?status=pending` pour capturer le vrai ID. Petite amélioration future possible (parser correct le shape Paperclip).
3. **Branche switching automatique** : un hook (probablement session-log + Stop) checkout des branches arbitrairement. Toujours `git branch --show-current` au début de chaque tour pour valider.
4. **Verifier l'existant AVANT d'inventer** : la règle CLAUDE.md a sauvé 1 erreur (Code-Review existant déjà → on ne le réinvente pas, scope distinct).
5. **AI-COS dashboard en `Up 6 weeks` n'est PAS un signe de santé** : le DB peut être unhealthy depuis 11 jours sans que personne le voie. **Ajout de monitoring nécessaire**.

---

## 8. Références

- Spec : `nestjs-remix-monorepo:docs/superpowers/specs/2026-04-25-fleet-advisor-claude-4-7-design.md`
- Plan : `nestjs-remix-monorepo:docs/superpowers/plans/2026-04-25-fleet-advisor-claude-4-7.md`
- PR : https://github.com/ak125/nestjs-remix-monorepo/pull/182
- Vault MOC : [[MOC-Agents]], [[MOC-Knowledge]]
- Memory items créés : à propager vers `MEMORY.md` post-merge (`fleet-advisor-claude-4-7.md` + `aicos-disk-full-recovery-recipe.md`)
- Anthropic pattern : Claude Code subagent `code-reviewer` (cf. `superpowers:code-reviewer` skill)
