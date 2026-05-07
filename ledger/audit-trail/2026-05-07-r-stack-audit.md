---
type: audit-trail
date: 2026-05-07
session_id: r-stack-baseline-2026-05-07
domain: r-stack
related_adr: ["ADR-046", "ADR-047"]
status: baseline-snapshot
---

# Audit baseline R-stack — 2026-05-07

> Snapshot pré-refondation pour [[ADR-046-r-stack-single-generator-and-layers]]
> et [[ADR-047-seo-role-contracts-as-code]]. Tous chiffres re-runnable
> via les commandes citées (1 commande = 1 chiffre, principe `Q1`).

## 1. RAG legacy — surface consommée en runtime sans curation

**Localisation** : `/opt/automecanik/rag/knowledge/{gammes,vehicles,...}/`

| Topic | Folders | Fichiers `.md` | Total bytes | Avg bytes / fichier |
|---|---|---|---|---|
| `gammes` | 241 (1 / gamme) | **1655** | 17 634 515 (~16.8 MiB) | ~10 656 (~10.6 KiB) |
| `vehicles` | 8 | 8 | (à mesurer) | (à mesurer) |
| `constructeurs` | n/a (sync via wiki) | 36 | n/a | n/a |

**Commandes re-runnables** :

```bash
ls /opt/automecanik/rag/knowledge/gammes | wc -l               # 241 folders
find /opt/automecanik/rag/knowledge/gammes -name "*.md" | wc -l # 1655 files
find /opt/automecanik/rag/knowledge/gammes -name "*.md" \
  -exec wc -c {} + | tail -1                                    # 17634515 total
ls /opt/automecanik/rag/knowledge/vehicles | wc -l              # 8
```

**Constat** : 1655 fichiers consommés par L4 enrichers sans
`validated_by` ni lineage. Pas de promotion gate. Origine pré-[[ADR-031-four-layer-content-architecture]]
(architecture 4-layer).

## 2. Wiki state — SoT théorique vs réalité

**Localisation** : `/opt/automecanik/automecanik-wiki/`

| Surface | Contenu actuel | État canon |
|---|---|---|
| `wiki/constructeurs/` | (peuplé) | ✅ R7 brands fonctionne |
| `wiki/gammes/` | **vide** ou squelette | ❌ Wiki SoT non opérationnel |
| `wiki/vehicles/` | **vide** | ❌ Wiki SoT non opérationnel |
| `wiki/diagnostic/` | (peuplé partiel) | ⚠️ ADR-033 Phase D pendante |
| `wiki/support/` | (peuplé partiel) | ⚠️ Hors-scope refondation |
| `wiki/proposals/legacy/` | inexistant | ❌ À créer Phase 3A PR-K |
| `wiki/proposals/auto/` | inexistant | ❌ À créer Phase 3A PR-L |
| `exports/rag/constructeurs/` | **36 fichiers** ✅ | Pattern de référence |
| `exports/rag/gammes/` | (à mesurer) | ❌ Cible Phase 3B |
| `exports/rag/vehicles/` | (à mesurer) | ❌ Cible Phase 3B |

**Commandes** :

```bash
ls /opt/automecanik/automecanik-wiki/wiki                                 # 5 topics
ls /opt/automecanik/automecanik-wiki/exports/rag/constructeurs | wc -l    # 36
```

**Constat** : seul R7 brands respecte la chaîne `wiki/constructeurs/ →
exports/rag/constructeurs/ → rag/knowledge/constructeurs/`. Les 1655
fichiers gammes RAG legacy sont **hors-chaîne**.

## 3. Enrichers backend — fragmentation R\*

**Localisation** : `/opt/automecanik/app/backend/src/modules/admin/services/`

### 3.1 Liste des 8 enrichers actuels

```bash
$ find backend/src/modules/admin/services -name "*-enricher.service.ts"
backend/src/modules/admin/services/r1-enricher.service.ts
backend/src/modules/admin/services/r2-enricher.service.ts
backend/src/modules/admin/services/conseil-enricher.service.ts        # R3
backend/src/modules/admin/services/r4-content-enricher.service.ts
backend/src/modules/admin/services/buying-guide-enricher.service.ts   # R6
backend/src/modules/admin/services/r7-brand-enricher.service.ts
backend/src/modules/admin/services/r8-vehicle-enricher.service.ts
backend/src/modules/admin/services/gamme-detail-enricher.service.ts   # transversal
```

8 enrichers, 1 par rôle (R5 sunset [[ADR-027-r5-consolidation-into-r3-s2-diag]]). `gamme-detail-enricher`
est transversal — à reclasser en Phase 2.

### 3.2 Fragmentation R1 (10 fichiers identifiés)

```bash
$ find backend/src -name "r1-*"
backend/src/config/r1-media-rules.constants.ts
backend/src/config/r1-keyword-plan.constants.ts
backend/src/modules/gamme-rest/utils/r1-image-normalizer.ts
backend/src/modules/gamme-rest/services/r1-related-resources.service.ts
backend/src/modules/gamme-rest/types/r1-related-links.types.ts
backend/src/modules/admin/services/r1-keyword-plan-gates.service.ts
backend/src/modules/admin/services/r1-enricher.service.ts             # canon Phase 2
backend/src/modules/admin/services/r1-content-from-rag.service.ts     # canon Phase 2 (HTML page)
backend/src/modules/admin/services/r1-image-prompt.service.ts
backend/src/modules/admin/services/r1-keyword-plan-batch.service.ts
```

**Verdict** :
- 2 enrichers canon : `r1-enricher` (slots) + `r1-content-from-rag` (HTML)
  — responsabilités distinctes, ne pas fusionner.
- 8 fichiers orthogonaux : KP, media, image-prompt, related-resources,
  types — scope distinct, **ne pas merger en 1 mais imposer 1 LIVE par
  responsabilité** (Phase 1 PR-C AGENTS.md ownership).

### 3.3 Règles métier en dur (drift programmé)

```bash
$ grep -rEn "min_chars\\s*[:=]\\s*[0-9]|max_chars\\s*[:=]\\s*[0-9]|MIN_CHARS\\s*=\\s*[0-9]|MAX_CHARS\\s*=\\s*[0-9]" \
    backend/src/modules/admin/services/*-enricher.service.ts
backend/src/modules/admin/services/r1-enricher.service.ts:30:const R1_MICRO_SEO_MIN_CHARS = 1500;
backend/src/modules/admin/services/r1-enricher.service.ts:31:const R1_MICRO_SEO_MAX_CHARS = 3000;
```

**Constat** : R1 a des règles métier hardcodées (1500/3000 — bump récent
PR monorepo #346). Les autres enrichers n'ont pas ce pattern grep-able
mais peuvent avoir des seuils ailleurs (à étendre Phase 2 PR-H).

```bash
$ grep -rEn "FORBIDDEN_TERMS|forbidden_overlap" \
    backend/src/modules/admin/services/*-enricher.service.ts
backend/src/modules/admin/services/conseil-enricher.service.ts:156:      forbidden_overlap?: string[];
backend/src/modules/admin/services/conseil-enricher.service.ts:407:      // Load section_terms (include_terms, micro_phrases, forbidden_overlap)
```

**Constat** : `conseil-enricher.service.ts` (R3) lit `forbidden_overlap`
depuis section_terms DB — pas de hardcode. R1 et autres n'utilisent pas
encore ce mécanisme — c'est exactement ce que [[ADR-047-seo-role-contracts-as-code]] généralise via
contracts.

### 3.4 R1 bump 1500/3000 — déjà shipped

PR monorepo #346 `feat(seo): r1 micro-seo synth richer 1500-3000c`,
commit `9f72a0bd` sur `origin/main`. Phase 4 PR-S devra reconnaître ce
fait et **migrer** la constante existante vers le contract
`seo-role-contracts/r1.ts`, pas re-bumper.

## 4. `@repo/seo-roles` — version + scope actuel

```bash
$ cat packages/seo-roles/package.json | grep version
  "version": "0.5.0",
$ ls packages/seo-roles/src
branded.ts canonical.ts colors.ts display.ts forbidden-overlap.ts
index.ts intents.ts keyword-cluster.schema.ts keyword-intent.ts
legacy.ts normalize.ts schema.ts text-normalize.ts __tests__/
```

**Scope actuel** : identité (canonical, normalize, display, colors,
intents, keyword-cluster) + **comportement** (`forbidden-overlap.ts`).

**Cible post-[[ADR-047-seo-role-contracts-as-code]]** : identité only. `forbidden-overlap.ts` →
`@repo/seo-role-contracts/src/contracts/r{N}.ts`. Bump major 1.0.0.

## 5. ast-grep rules existantes (Phase 1 partial)

```bash
$ ls /opt/automecanik/app/.ast-grep/rules
backend-no-console-log.yml
backend-no-remote-io-in-onmoduleinit.yml
frontend-no-zero-arg-headers-with-s-maxage.yml
no-direct-rag-knowledge-write.yml                    ← déjà actif (PR-A déjà partiellement done)
payments-no-raw-equality.yml
seo-no-bare-role-literal.yml
seo-no-inline-role-keyword-pattern.yml
```

**Constat** : `no-direct-rag-knowledge-write.yml` existe déjà. PR-A
Phase 1 doit donc **étendre** (allowlist `sync-wiki-exports-to-rag.py`),
pas créer de zéro.

**À créer (Phase 1 PR-B)** : `no-anthropic-direct-import-in-scripts-seo.yml`.
**À créer (Phase 2 PR-H étendu)** : `no-hardcoded-rules-in-enrichers.yml`.

## 6. Sentry / observability — état post-V0

| Surface | État |
|---|---|
| Sentry backend init `instrument.ts` | ✅ commits #324/#327/#334 |
| Sentry frontend init `entry.client.tsx` | ✅ existant |
| Sentry frontend `beforeSend` scrubber PII | 🟡 PR #347 V0.B en auto-merge `12:26:54Z` |
| CSP `connect-src` Sentry | ❌ à ajouter Phase 5 PR-U |
| GA4 multi-events client | 🟡 PR #347 V0.B en auto-merge |

## 7. ADRs amont à respecter

- [[ADR-027-r5-consolidation-into-r3-s2-diag]] — R5 sub-pages sunset, R5 = section S2_DIAG dans R3 only
- [[ADR-031-four-layer-content-architecture]] — chaîne 4-layer raw/wiki/exports/consumers
- [[ADR-033-wiki-gamme-diagnostic-relations-contract]] — `diagnostic_relations[]` top-level
- [[ADR-037-agent-naming-canon]] + [[ADR-038-marketing-agent-naming-canon]] — frontmatter `role:` Zod
- [[ADR-039-wiki-frontmatter-zod-canon]] — frontmatter v2.0.0 wiki proposals
- [[ADR-040-seo-roles-canon-ts-side-only]] — foundation `@repo/seo-roles` (sera amendé par [[ADR-047-seo-role-contracts-as-code]])
- [[ADR-044-seo-strategy-2026-roles-priority]] — priorités R6/R8/R7
- [[ADR-045-seo-monitoring-cron-v0]] — V0.A monitoring cron

## 8. Dépendances externes — état

- **Vault PR #286** (mentionnée dans plan source) : non trouvée dans
  `gh pr list` vault. Probablement référence erronée, à confirmer ou
  remplacer par numéro réel lors de PR-A Phase 1.
- **Cron VPS DEV `wiki/exports → rag/knowledge/`** : opérationnel pour
  R7 brands (36/36 sync). À étendre gammes + vehicles en Phase 3B PR-P.

## Conclusion baseline

Système actuel : R7 brands fonctionne canoniquement, le reste (R1, R3,
R4, R6, R8) consomme RAG legacy hors-chaîne avec règles métier dupliquées
en dur. La refondation [[ADR-046-r-stack-single-generator-and-layers]] + [[ADR-047-seo-role-contracts-as-code]] vise à étendre le
pattern R7 à tous les rôles + factoriser les règles métier en
`seo-role-contracts`.

**État pré-Phase 1** : 7 ADRs amont accepted/proposed cohérents, ast-grep
rule `no-direct-rag-knowledge-write` déjà active, R7 pattern en place,
PR #347 V0.B en finalisation. Aucun blocage avant Phase 1.

---

> Snapshot canonique pour [[ADR-046-r-stack-single-generator-and-layers]] et [[ADR-047-seo-role-contracts-as-code]]. Tout chiffre
> re-runnable via la commande citée. Pas d'extrapolation, pas de
> précision factice.
