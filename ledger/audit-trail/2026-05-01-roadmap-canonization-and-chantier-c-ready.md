---
title: "Session 2026-05-01 — Roadmap globale 2026 canonisée + Chantier C READY"
date: 2026-05-01
type: session-trail
related_adr: ["ADR-031", "ADR-033"]
related_prs:
  - "ak125/governance-vault#128"
  - "ak125/nestjs-remix-monorepo#256"
  - "ak125/nestjs-remix-monorepo#257"
status: closed
session_closed_at: 2026-05-01
---

# Session 2026-05-01 — Roadmap globale + Chantier C READY

## Résumé

Deux livrables imbriqués :

1. **Re-cadrage stratégique** — le plan ADR-033 (raw/wiki/diag) en cours
   était traité implicitement comme « la stratégie projet », alors qu'il ne
   couvre qu'un pilier sur ~9. Création d'une roadmap globale 2026 qui
   définit les **9 chantiers transverses A→I** + une priorité business
   **P0→P8** + une **grille d'arbitrage hebdomadaire** (5 critères : Revenue,
   Risk, Blocking, Effort, Evidence). ADR-033 est désormais explicitement
   identifié comme **Chantier C (1/9)**, pas comme la stratégie globale.

2. **Clôture Chantier C / verdict READY** — la wave Phase 2/3 ADR-033
   livrée le 2026-04-30 (6 PRs) avait un cron cassé au premier dispatch.
   Deux hotfixes en cascade ont restauré la chaîne raw → wiki → exports →
   readiness check. `wiki-readiness-check.yml` retourne **READY** sur tous
   les 6 critères C1-C6 → critère go Partie 3 atteint, garde-fou utilisateur
   #12 levé, consommateurs (DB / RAG / SEO / blog / diagnostic / chatbot)
   débloquables.

## Livré dans cette session

### Roadmap canonization

| Livrable | Statut |
|----------|--------|
| `MOC-Roadmap-2026.md` (vault `ops/moc/`) — 9 chantiers + P0→P8 + grille hebdo | [PR vault #128](https://github.com/ak125/governance-vault/pull/128) ouverte |
| Plan local Claude Code rev 4 (re-titré « Plan — Chantier C : Knowledge / Raw / Wiki / Diagnostic Canon ») | local DEV scratch |

### Chantier C — restauration cron + verdict READY

| Livrable | Commit | Statut |
|----------|--------|--------|
| Hotfix #1 — `psycopg2` → PostgREST (réutilise `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` déjà provisionnés) | `097d3558` | [PR #256](https://github.com/ak125/nestjs-remix-monorepo/pull/256) MERGED |
| Hotfix #2 — `.strip()` env vars (secrets carrient `\n` trailing → `urllib.InvalidURL`) | `b70ca1e6` | [PR #257](https://github.com/ak125/nestjs-remix-monorepo/pull/257) MERGED |
| Run cron post-fix : `automecanik-wiki/exports/diag-canon-slugs.json` créé | wiki commit `99297949` | 62 symptoms, 10716 bytes |
| `wiki-readiness-check.yml` verdict | run `25211859787` | **READY** (C1-C6 all PASS) |

### Critères C1-C6 readiness

| Critère | Verdict | Détail |
|---------|---------|--------|
| C1 — schema v2.0.0 propagated | ✅ PASS | rag/docs/GAMME_PAGE_CONTRACT.md v2 |
| C2 — validateur CI bloquant actif | ✅ PASS | `wiki-validate.yml` |
| C3 — `exports/diag-canon-slugs.json` fresh | ✅ PASS | post hotfix #257 |
| C4 — fiches gamme migrées | ✅ PASS | (N/A actuellement, sera matière en Partie 3) |
| C5 — quality gates green | ✅ PASS | 18/18 PASS, 0 FAIL, 1 WARN (Brembo) |
| C6 — skill `wiki-proposal-writer` operational | ✅ PASS | workspaces/wiki/.claude/skills/ |

## Décisions clés

### Re-cadrage roadmap

- **9 chantiers A→I, lettre = identifiant stable, PAS un rang**. Numérotation
  Ax/Bx/… (jusqu'à 7 sujets max) sert d'identifiant pour les tickets et PRs.
- **Priorité P0→P8 indépendante** de la lettre :
  - P0 F (DevSecOps) — plancher non-négociable
  - P1 A (Runtime e-commerce) — cœur du revenue
  - P2 D (SEO indexation) — débloque C/B/G
  - P3 B (Catalogue) — base SEO/RAG/marketing
  - P4 E (Performance) — conditions matérielles
  - P5 C (Raw/Wiki/Diag) — fondationnel mais effet revenue indirect
  - P6 H (Marketing) — après A/D/B propres
  - P7 G (RAG/support) — dépend C+D+B
  - P8 I (Agents/Paperclip) — capacité, pas finalité
- **Note importante** : ce classement vaut pour la **planification** de
  nouveaux chantiers, pas pour interrompre du travail en cours déjà borné.
- **Grille hebdo** : Revenue / Risk / Blocking / Effort / Evidence — refuser
  les actions « jolies » sans métrique, sans bug, sans dépendance claire.

### Hotfix cron PR-D

- **Hotfix #1 PostgREST** plutôt que provisionner `SUPABASE_DB_PASSWORD`
  (secret manquant) : réutilise les secrets existants, pas de surface
  d'attaque supplémentaire, élimine la dépendance `psycopg2-binary`.
- **Hotfix #2 `.strip()` au point de lecture** plutôt que re-paster le secret
  via UI : robuste contre toute future occurrence du même gotcha sans
  bricolage env-side qui masquerait le problème.

## Mémoires créées (DEV-side, hors vault)

- `feedback_prefer_mv_over_cp_for_relocation.md` — relocalisation fichier =
  `mv` atomique, jamais `cp` seul (laisse duplication).
- `feedback_strip_env_vars_python.md` — `.strip()` env vars au point de
  lecture (secrets GH carry `\n` trailing → `urllib` reject).

## Follow-ups

| Item | Quand | Owner |
|------|-------|-------|
| Merge vault PR #128 (`MOC-Roadmap-2026.md`) | Quand revue OK | humain |
| Routine `trig_01LKqhkSKddud3ywGM9Yjb6z` (audit ADR-033 J+30) | 2026-05-29 | auto-fire |
| Routine `trig_01Tq3Z8ohU29suDmnezZhWnG` (INC + ADR-034 DB freeze) | 2026-05-02 09:00 UTC | auto-fire |
| Maturité G9-B (migrate-template, weekly full sweep, rollback drill C4) | J+17 → J+30 | hors scope wave 2/3 |
| PR-E (`migrate-symptoms-to-relations.py`) | Quand sync-from-rag arrive en Partie 3 | déclenché par contenu |
| Plans dédiés TBD (Runtime A, Performance E, F global, D global) | À la demande, chantier par chantier | humain |
| Décision : promouvoir plans Claude Code locaux C/H vers vault `ops/moc/` ? | Si stabilité durable + besoin cross-session | humain |

## Pourquoi cette session

Le constat « ADR-033 ≠ stratégie globale » est venu après que l'utilisateur
ait remarqué que le plan rev 3 occupait toute la bande passante alors que les
chantiers business critiques (paiement, catalogue, indexabilité, sécurité)
avançaient en sous-priorité implicite. La canonisation de la MOC permet aux
sessions futures d'arbitrer cross-chantiers sur une grille partagée.

Le verdict READY sur Chantier C clôt la wave Phase 2/3 ADR-033 démarrée
2026-04-30. Les 6 PRs (#249-#253) + 2 hotfixes (#256, #257) forment une
chaîne contract → skill → validateur → cron → readiness check cohérente,
livrée sans bricolage hybride transitoire (verrou utilisateur #12 respecté).

## Références

- [[ADR-031-four-layer-content-architecture]] — raw/wiki/exports/consumers
- [[ADR-033-wiki-gamme-diagnostic-relations-contract]] — diagnostic relations canon
- [[MOC-Decisions]] — index ADRs vault
- [[MOC-AuditTrail]] — index audit-trail (ce fichier)
- Vault PR #128 — `MOC-Roadmap-2026.md` (en attente de merge)
- Memory MEMORY.md `adr-033-wave-2-closed.md` — détail wave 2026-04-30
