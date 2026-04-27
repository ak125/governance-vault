---
type: moc
status: canon
updated: 2026-04-17
---

# MOC: Audit Trail

Journal chronologique des **evenements de gouvernance** : audits ponctuels, retrospectives de phase, bundles rejetes par l'Airlock, audits RPC, post-mortems formalises.

> Les **ADR** sont dans [[MOC-Decisions]].
> Les **evidence-packs** (preuves structurees) sont dans [[MOC-Compliance]].

---

## Retrospectives & Audits (2026-02)

| Date | Document | Type |
|------|----------|------|
| 2026-02-02 | [[2026-02-02-rpc-safety-gate-audit]] | Audit (RPC Safety Gate) |
| 2026-02-03 | [[2026-02-03_governance-formalization-complete]] | Completion (v1 governance) |
| 2026-02-03 | [[2026-02-phase4-post-hardening-summary]] | Retrospective (Phase 4) |
| 2026-02-03 | [[2026-02-paybox-compatibility-audit]] | Audit (Paybox) |
| 2026-02-04 | [[2026-02-04_phase13-14-vault-sync-complete]] | Completion (vault sync) |
| 2026-04-17 | [[2026-04-17-governance-vault-v2-refactor]] | Retrospective (v2 refactor, 6 phases) |
| 2026-04-18 | [[2026-04-18-phase7-residuels-and-option-b]] | Retrospective (Phase 7 cloture — residuels + Option B + EP meta-vault) |
| 2026-04-21 | [[2026-04-21-session-r7-brand-complete]] | Retrospective (R7 brand live-sync + Wikidata + admin UI + 11 PRs) |
| 2026-04-21 | [[2026-04-21-pipeline-content-hardening]] | Evidence-pack (pipeline R1/R3/R4/R6 hardening, Zod SSOT parser) |
| 2026-04-21 | [[2026-04-21-session-r7-curation-prep]] | Retrospective (R7 curation prep P1→P4, gate + UI + corpus + runbooks, 6 PRs) |
| 2026-04-22 | [[2026-04-22-session-r7-full-curation]] | Retrospective (R7 P1 complète : 36/36 marques curées, score avg +5.03, fix S3_SHORTCUTS 410) |
| 2026-04-22 | [[2026-04-22-alias-expansions-batch-preventif]] | Evidence-pack (SEO alias dictionary + apostrophe normalization fix) |
| 2026-04-23 | [[2026-04-23-alias-dict-roman-arabic-normalization]] | Evidence-pack (alias dict wiring + roman/arabic modele matching for V-Level) |
| 2026-04-23 | [[2026-04-23-seo-kp-alias-maitre-cylindre-frein]] | Evidence-pack (alias canonicalization `maitre-cylindre-de-frein`) |
| 2026-04-23 | [[2026-04-23-seo-kw-pipeline-cable-frein-main]] | Evidence-pack (pipeline SEO KW bout-en-bout `cable-de-frein-a-main` gamme 15/232 + V-Level SQL port) |
| 2026-04-23 | [[2026-04-23-seo-kw-pipeline-maitre-cylindre]] | Evidence-pack (pipeline SEO KW `maitre-cylindre-de-frein` gamme 16/232 + découverte bug regex TS script) |
| 2026-04-23 | [[2026-04-23-seo-kw-vehicle-rpc-refactor]] | Evidence-pack (refactor `insert-missing-keywords.ts` : regex hardcodées → RPC SQL dynamique `match_keyword_text_to_vehicle`) |
| 2026-04-23 | [[2026-04-23-seo-kw-pipeline-pompe-vide-freinage]] | Evidence-pack (pipeline SEO KW `pompe-a-vide-de-freinage` gamme 17/232 + arbitrage canon cross-gamme) |
| 2026-04-23 | [[2026-04-23-r6-gatekeeper-wiring-and-vlevel-script-port]] | Evidence-pack (wire R6 `sgpg_gatekeeper_*` symétrie R1, port `rebuild-type-vlevel.py` canon, backfill 223 rows 235→18 NULL) |
| 2026-04-23 | [[2026-04-23-freinage-completion-backlog]] | Evidence-pack (completion freinage 13 gammes : backlog V-Level pg=70/82/402, classify tambour pg=123, diagnostic legacy pg=3859) |
| 2026-04-24 | [[2026-04-24-seo-kw-pipeline-repartiteur-frein]] | Evidence-pack (pipeline SEO KW `repartiteur-de-frein` gamme 18/232 + première application formelle R-SEO-KW-06 sur synonymes techniques) |
| 2026-04-24 | [[2026-04-24-seo-kw-kit-frein-arriere-3-incidents-db]] | Evidence-pack (pipeline SEO KW `kit-de-freins-arriere` gamme 19/232 + 3 incidents DB systémiques découverts et corrigés : trigger polyglot, pg_id désynchro, executor UPDATE no-op) |
| 2026-04-25 | [[2026-04-25-rag-only-enriched-stage-canon]] | Evidence-pack (canon stage `RAG_ONLY_ENRICHED` ajouté à `v_kw_pipeline_status` ; débloque 147 gammes G1/G2 (63%) artificiellement NO_CSV ; freinage 13/13 canon ; R-SEO-KW-07 ajoutée) |
| 2026-04-25 | [[2026-04-25-p1-deploy-inc3-verify-rag-content-gaps]] | Evidence-pack (P1 deploy unblock @ast-grep Alpine + INC-3 verify post-deploy + 28 "BLOCK" audit reclassifiés en RAG content gaps, pas bugs code) |
| 2026-04-25 | [[2026-04-25-r1-gatekeeper-symmetry-backfill]] | Evidence-pack (closure follow-up §7 #4 R6 audit — symmetry audit complète, R1 100% scored 48→0 NULL via backfill-r1-gatekeeper.py) |
| 2026-04-25 | [[2026-04-25-r6-100pct-closure-and-di-fix]] | Evidence-pack (R6 100% scored 241/241 — closure §7 #1 cluster RAG-incomplet 18→0 NULL via PR #180 early-return write + PR #181 DI fix RContentAuditorService) |
| 2026-04-25 | [[2026-04-25-r8-refactor-and-parallel-agent-incident]] | Retrospective (R8 route refactor 1+2a+2b mergés, 2020→1258 lignes −38%, 7/13 sections, + incident parallel-agent + R-AGENT-01 proposée) |
| 2026-04-27 | [[2026-04-27-session-closure-r6-r1-gatekeeper-todo]] | Session-closure (bilan 3 sessions R6/R1 gatekeeper, R1+R6 100% scored, 5 follow-ups TODO classés priorité) |
| 2026-04-27 | [[2026-04-27-session-vault-governance-hardening]] | Session-trail (G2 fixes PR #77/#88 + auto-merge ON + CODEOWNERS canon + branch protection main : 5 G* + 1 approval + code-owner reviews + enforce_admins=false) |

---

## Sous-Sections

### Bundles Rejetes (par Airlock)

Les rejets Airlock sont journalises pour prouver le fonctionnement du garde-fou.

- [[INDEX-bundles-2026-02]] - 8 bundles rejetes en fevrier 2026

### Audits RPC

- [[INDEX-audit-trail-rpc]] - Baselines P2 enforce, audits RpcGateService

---

## Processus

1. **Evenement** detecte (rejet Airlock, incident, completion de phase, audit planifie)
2. Document cree dans `ledger/audit-trail/` ou son sous-dossier thematique
3. Frontmatter : `type: audit-report | retrospective | completion | bundle-rejection`
4. Lien retour vers ADR(s) et plan(s) concernes
5. Si post-mortem -> peut produire une nouvelle ADR (voir [[MOC-Incidents]])

---

## Voir aussi

- [[MOC-Decisions]] - ADR canoniques
- [[MOC-Compliance]] - Plans d'execution et evidence-packs
- [[MOC-Incidents]] - Post-mortems formalises
- [[MOC-Rules]] - Regles T/G/AI/V
- [[validator-engine-spec]] - Les 10 gates qui produisent les bundles REJECTED

---

_Derniere mise a jour: 2026-04-17_
