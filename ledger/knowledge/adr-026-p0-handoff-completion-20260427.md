---
type: knowledge
status: canon
created: 2026-04-27
updated: 2026-04-27
tags: [adr-026, content-separation, handoff, session-log, partial-coverage]
related-adr: [ADR-012, ADR-015, ADR-022, ADR-025, ADR-027, ADR-029]
related-prs: [governance-vault#78, automecanik-content#1]
verdict: PARTIAL_COVERAGE (P0 handoff complete, P1-P6 pending)
---

# ADR-026 P0 — Session de handoff complete (2026-04-27)

> Note de session consignant l'état exact du chantier "Content Repository
> Separation" (ADR-026) à la fermeture session 2026-04-27. Doit servir de
> reprise propre pour la prochaine session sans perte de contexte.

---

## 1. Ce qui a été livré dans cette session

### 1.1 Drafts en scratchpad DEV VPS

| Artefact | Chemin | Taille |
|---|---|---|
| Draft ADR-026 | `/tmp/audit/draft-adr-026-content-separation.md` | 33 KB, 551 lignes |
| Squelette `automecanik-content` | `/tmp/audit/automecanik-content-skeleton/` | ~96 KB, 15 fichiers |

### 1.2 Pull Requests ouvertes

| PR | URL | Branche | Commit signé G3 |
|---|---|---|---|
| Vault — ADR-026 + MOC update | https://github.com/ak125/governance-vault/pull/78 | `docs/adr-026-content-separation` | `e50a5dc` ("Good git signature for vault-signing@automecanik.com") |
| Content — squelette initial | https://github.com/ak125/automecanik-content/pull/1 | `init/skeleton-adr-026` | `24e0205c` (même clé ED25519 `qBBgd1Zl...`) |

### 1.3 Décision architecturale ratifiée

**Option B** parmi 4 pesées : repo séparé `automecanik-content` (déjà créé
2026-04-26 21:05 UTC), pattern 2-repos pairs alimentés par `_raw/` source unique.

Modèle 3 couches :
```
[automecanik-rag/_raw/]
        ├─ refiner SEO ─→ [automecanik-content/wiki/]   → R0-R8 + Weaviate dev:full
        └─ refiner support ─→ [automecanik-rag/knowledge/] → Weaviate prod:chatbot
```

**R8 rotation conservée** (décision @fafa explicite) — amélioration de la
diversité reportée à un ADR séparé futur, hors scope ADR-026.

### 1.4 Stratégies clé documentées

- **Migration atomique P2** : PR `automecanik-rag` (suppression) + PR
  `automecanik-content` (import via `git filter-repo --path`) mergées
  **same-day** pour éviter Frankenstein state
- **Couplage runtime, pas couplage git** : pattern deux-clones-côte-à-côte
  + env vars (`AUTOMECANIK_CONTENT_PATH`, `AUTOMECANIK_RAG_PATH`),
  cohérent ADR-012 / ADR-015 (pas de submodule)
- **Weaviate blue-green P4.1-P4.5** : nouvelle classe `prod:chatbot:v2`
  reindexée en arrière-plan, switch atomique, drop v1 J+7 stable. Zéro
  downtime chatbot (gap matériel patché en cours de session)
- **Diagnostic cross-repo** : `diagnostic/` reste sous `automecanik-rag`
  (audience chatbot prioritaire, ADR-027 déprécie R5 standalone) — R3
  pipeline lit 2 paths via env vars

---

## 2. Conformité G/AP

| Règle | État |
|---|---|
| **G1** Canon fait foi | ADR mergée AVANT exécution P1-P6 (cette PR #78) |
| **G2** Zéro orphelin | MOC-Decisions.md mis à jour dans PR #78 |
| **G3** Signed commits | `e50a5dc` + `24e0205c` signés ED25519 vault-signing |
| **G5** `.spec/00-canon/` autoritatifs | Aucune référence à amender (vérifié grep) |
| **AP-10** Services <500 lignes | N/A (pas de code, juste structure) |
| **AP-11** Verify existing first | 22 dossiers cartographiés, 4 ADRs adjacentes lues, pattern `governance-vault` repo séparé identifié comme précédent |

---

## 3. Reste à faire (P1-P6)

> Toutes les phases dépendent du **merge de la PR #78** d'abord (canon).
> La PR #1 (skeleton) peut être mergée en parallèle ou après.

### P1 — Refacto env vars monorepo (1 PR)

**Précondition** : PR #78 + PR #1 mergées.

- [ ] Inventaire grep exhaustif : `grep -rE
      '/opt/automecanik/rag/knowledge/(gammes|vehicles|constructeurs|guides|reference|seo-data)'
      /opt/automecanik/app /opt/automecanik/rag/scripts
      --include='*.py' --include='*.ts' --include='*.js' -l`
- [ ] Substituer les hardcoded paths par `process.env.AUTOMECANIK_CONTENT_PATH`
      / `os.environ['AUTOMECANIK_CONTENT_PATH']`
- [ ] Default temporaire : `AUTOMECANIK_CONTENT_PATH=/opt/automecanik/rag/knowledge`
      (compat tant que P2 pas mergé)
- [ ] PR monorepo + tests verts (`npm test`, `python -m pytest scripts/seo/`)
- [ ] Smoke test DEV : `auto-enrich-r4-rag.py --mode audit_only` ne casse pas

**Sizing TBD** : "~10-20 fichiers" estimation, à mesurer en début P1.

### P2 — Migration atomique (2 PRs same-day)

**Précondition** : P1 mergé sur monorepo + déployé DEV.

- [ ] `git filter-repo --path knowledge/gammes/ --path-rename
      knowledge/gammes/:wiki/gammes/` (idem vehicles, constructeurs, guides,
      reference, seo-data) sur clone temporaire de `automecanik-rag`
- [ ] PR `automecanik-content` : import du contenu avec history préservée
- [ ] PR `automecanik-rag` : suppression des dossiers migrés + tombstone
      `.MOVED.md` dans chaque dossier supprimé
- [ ] Update env var monorepo : `AUTOMECANIK_CONTENT_PATH=/opt/automecanik/content/`
- [ ] Provisioning VPS DEV + PROD : clone `automecanik-content` sous
      `/opt/automecanik/content/`
- [ ] **Merge des 2 PRs le même jour ouvré + redéploiement monorepo**
- [ ] Smoke test post-migration : 1 page R3 + 1 page R8 generées en preprod,
      diff vs avant migration = 0 différence sémantique

### P3 — Amendement ADR-022 + ADR-029

- [ ] Amendement ADR-022 : paths `/rag/knowledge/vehicles/` →
      `/content/wiki/vehicles/` § "Mise en œuvre" point 9
- [ ] Amendement ADR-029 : paths `/opt/automecanik/rag/knowledge/gammes/`
      → `/opt/automecanik/content/wiki/gammes/` § "Données et migrations"
      et § "Validation"
- [ ] Extension `weekly-vault-lint` (ADR-020) : ajouter `automecanik-content/`
      au scope lint
- [ ] PR vault mergée

### P4 — Ingestion Weaviate (blue-green, zéro downtime)

- [ ] **P4.1** : `prod:chatbot:v1` continue de servir
- [ ] **P4.2** : créer classe `prod:chatbot:v2` scope filtré
      `automecanik-rag/knowledge/`, reindex en arrière-plan
- [ ] **P4.3** : smoke tests v2 sur 20 questions chatbot, delta v1 vs v2 ≤ 5%
- [ ] **P4.4** : endpoint admin `POST /api/chatbot/index/promote-v2`,
      switch atomique
- [ ] **P4.5** : drop `prod:chatbot:v1` après J+7 stable
- [ ] `dev:full` : drop+recreate (downtime acceptable), reindex sur les 2 repos

### P5 — Cleanup

- [ ] Dédupliquer `automecanik-rag/knowledge/faq/` ↔ `faqs/` (1 fichier)
- [ ] Sniffer `seo/`, `structured/`, `tabular/`, `canonical/`, `catalog/`,
      `maintenance/` ; déplacer chaque dossier soit vers `_raw/`, soit
      vers `automecanik-content/`, soit le supprimer s'il est obsolète
- [ ] `web/`, `web-catalog/`, `web-vehicles/` → `automecanik-rag/_raw/web*/`
      (cohérence audience SOURCE)

### P6 — Runbook + provisioning canon

- [ ] `governance-vault/ops/runbooks/content-repo-clone.md` : où cloner,
      droits SSH, branche par défaut, sync DEV/PROD/AI-COS
- [ ] Amendement ADR-012 playbook VPS : étape clone `automecanik-content`
- [ ] CI lint frontmatter `content-lint.yml` activé (rename depuis
      `.placeholder`)

---

## 4. Issues / Observations à la fermeture session

### 4.1 PR #78 (vault) — rebase requis

⚠️ Pendant cette session, `main` du vault a évolué (ajout ADRs 016, 017,
018, 019, 024 et restructuration MOC-Decisions.md avec une **nouvelle
convention "Notes"** pour les ADRs in-flight).

PR #78 a été créée AVANT cette évolution → conflit de structure :
- PR #78 a ajouté ADR-026 directement dans le tableau ADR Actifs
- Convention nouvelle (introduite entre temps sur main) : ADRs in-flight
  vont dans la section "Notes" (lignes 48-50 actuelles), pas dans le
  tableau, jusqu'au merge de leur propre PR

**Action** : avant merge PR #78, rebase sur main + adapter MOC-Decisions.md
pour suivre la nouvelle convention (probablement enlever la ligne ADR-026
du tableau et l'ajouter dans la liste "Notes" en attendant que la PR #78
elle-même soit mergée — chicken-and-egg).

**Workaround possible** : laisser ADR-026 dans le tableau de PR #78
puisque c'est précisément la PR qui mergea ADR-026 (donc plus "in-flight"
au moment du merge). Discuter en review avant merge.

### 4.2 PR #1 (content) — pas de conflit

Repo créé hors ledger 2026-04-26, contenait juste un README auto-généré
22 octets. PR #1 écrase ce README et installe le squelette. Aucun conflit
attendu.

### 4.3 Sizing pipeline P1 TBD

L'ADR-026 estime "~10-20 fichiers Python/NestJS à refacto" pour les paths
hardcodés. Cette estimation n'a **pas été validée** par grep réel — la
mesure exacte est en pré-requis P1.

### 4.4 Refiner agents — hors scope

ADR-026 ne définit pas les refiner agents (raw → wiki, raw → knowledge).
ADR-022 couvre déjà R8 vehicles ; ADR-029 couvre gammes v2.1. Les autres
refiners (R3/R4/R6 gammes, R7 constructeurs, support FAQ, support
diagnostic) feront l'objet d'ADRs dédiées au fur et à mesure.

### 4.5 Cross-pollination — non implémentée

Le diagramme architectural ADR-026 mentionne le refinement bidirectionnel
secondaire (content → rag pour couverture support, rag → content pour
gaps SEO). Aucun mécanisme n'est implémenté — flag pour futur ADR.

---

## 5. Reprise propre — checklist next session

Pour reprendre proprement à la prochaine session, faire dans l'ordre :

1. **Lire cette knowledge note** (ce fichier) en premier
2. **Vérifier l'état des 2 PRs** :
   - https://github.com/ak125/governance-vault/pull/78
   - https://github.com/ak125/automecanik-content/pull/1
3. **Si PRs mergées** : commencer P1 (inventaire grep + refacto env vars)
4. **Si PR #78 pas encore mergée** : voir issue 4.1 ci-dessus
5. **Lire ADR-026 elle-même** :
   `governance-vault/ledger/decisions/adr/ADR-026-content-separation.md`
   (sections "Mise en œuvre" → "Phases" + "Validation" + "Rollback")

---

## 6. Memory updates effectués cette session

- `vault-obsidian-naming-windows.md` mis à jour : coffre Windows post-Phase W
  s'appelle bien `governance-vault/` (pas `-main` qui est l'anti-pattern ZIP
  rejeté). Sync via plugin Obsidian Git auto-pull 10 min.

---

## 7. Liens

- **ADR-026 (cette PR)** :
  `governance-vault/ledger/decisions/adr/ADR-026-content-separation.md` (PR #78)
- **Squelette content** : `automecanik-content/` (PR #1, branche
  `init/skeleton-adr-026`)
- **ADR-015** [[ADR-015-vault-single-source-of-truth]] — précédent pattern
  repo séparé
- **ADR-022** [[ADR-022-r8-rag-control-plane]] — paths à amender en P3
- **ADR-029** [[ADR-029-rag-v2.1-control-plane-closure]] — paths à amender en P3
- **ADR-027** [[ADR-027-r5-consolidation-into-r3-s2-diag]] — diagnostic reste
  sous `automecanik-rag`
- **`99-meta/obsidian-setup.md`** — setup canonique coffre Obsidian Windows
  (référence pour ouvrir `automecanik-content` comme 2ème coffre)

---

_Note de session écrite 2026-04-27 par Claude Code Opus 4.7 (1M context)
sur DEV VPS. Push via PR séparée pour tracer la fermeture session._
