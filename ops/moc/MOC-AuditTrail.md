---
type: moc
status: canon
updated: 2026-05-07
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
| 2026-04-25 | [[2026-04-25-session-adr-029-p1-status]] | Session-trail (ADR-029 P1 fondation — state machine 7 stages, follow-ups P2/P3/P4) |
| 2026-04-27 | [[2026-04-27-session-closure-r6-r1-gatekeeper-todo]] | Session-closure (bilan 3 sessions R6/R1 gatekeeper, R1+R6 100% scored, 5 follow-ups TODO classés priorité) |
| 2026-04-27 | [[2026-04-27-session-vault-governance-hardening]] | Session-trail (G2 fixes PR #77/#88 + auto-merge ON + CODEOWNERS canon + branch protection main : 5 G* + 1 approval + code-owner reviews + enforce_admins=false) |
| 2026-04-30 | [[2026-04-30-preprod-isolation-audit]] | Audit pré-décision ADR-028 (état working tree + Supabase orga + cost branch + recommandation Option C, ensuite revue post-empirical-audit en Option D — voir [[ADR-028-preprod-supabase-isolation]]) |
| 2026-04-30 | [[2026-04-30-aicos-rev5-session]] | Session-trail AI-COS rev5 (7 PRs livrées + ADR-034 AI-COS Operating Contract + ADR-028 Option D accepted + routine LIVE `vault-supabase-cost-check` + incident PR #242 → #244 + 5 mémoires utilisateur canonisées) |
| 2026-05-01 | [[2026-05-01-roadmap-canonization-and-chantier-c-ready]] | Session-trail (Roadmap globale 2026 canonisée — 9 chantiers A→I + P0→P8 + grille hebdo, vault PR #128 + Chantier C ADR-033 verdict READY après hotfixes #256/#257) |
| 2026-05-01 | [[2026-05-01-humble-cuddling-scott-strategic-audit-execution]] | Evidence-pack vérification audit stratégique externe (19 claims + 1 ajout, 3 errata) + 6 principes architecturaux unifiés (schema-first / derived artifacts / content-addressing / pre-commit primary / readonly derived / AEC unified runner) + Sprints 1-3 livrés (5 PRs : wiki #11 #12, raw #7 #8, monorepo #259), Sprint 4 P2 cross-repo content-addressing pendant |
| 2026-05-01 | [[2026-05-01-verifier-en-profondeure-p0-p3-execution]] | Session-trail audit factuel claims user 4 repos canon + exécution disciplinée P0/P3 (4 PRs MERGED : raw #10 Gate C inventory_complete + exemptions.yaml, wiki #14 cross-repo workflow CI, monorepo #260 5 dep-cruiser rules warn→error, monorepo #261 phantom deps fix + no-non-package-json error) + leçon canonisée `gh pr list --state merged` AVANT scope estimation |
| 2026-05-02 | [[2026-05-02-vault-hooks-silent-failure-postmortem]] | Session-trail post-mortem hooks vault silencieux (PR #134 a déclenché 2 fails CI : Broken Wikilinks + G3) — 3 bugs racines (pre-commit non-exec mode 664 depuis 2026-04-18, scripts skippés via `[ -x ]`, G3 absent côté pre-push) — fix structurel PR #135 : extraction `_scripts/check-signatures.sh` canonique (mirror logique CI), pattern aligné sur `check-orphans.sh` / `check-broken-links.sh`, CI workflow passe de 30 lignes inline à 1 appel script |
| 2026-05-05 | [[2026-05-05-seo-canon-r0-r8-stack-shipped]] | SEO Canon R0..R8 — 9 PRs livrées (#304-#312) cumulées via squash cascade (5 commits sur main : 0a792dcc 7f139d91 0545f36c d06677ae 179bbfdb). Architecture 4 couches enforcement (TS branded + Zod runtime + lint statique + observability), couche DB CHECK retirée. Inventaire MCP révèle migration `20260124_add_page_role.sql` jamais appliquée — pivot Option C (no migration needed). Canon `@repo/seo-roles@0.2.0` est SoT TS-side. ADR-040 formalise. 14 commits follow-up sur 3 vagues review automatique (10 reviews cumulées) |
| 2026-05-06 | [[2026-05-06-sprint-arbitrage-F]] | Session-trail sprint arbitrage F vs A vs D post-canonisation MOC-Roadmap-2026 (vault PR #128 mergée). Application règle décision conditionnelle (A rouge → F rouge → D rouge → défaut F). Signaux mesurés : F NOT RED (npm audit 0 CVE CVSS≥7.0 + exploit path runtime ; secret-grep 30j clean), A/D NOT MEASURED (creds Sentry/GSC absents env DEV). Verdict : **F par défaut P0→P8**. Plan F threat-model first NIST SSDF + OWASP SAMM + SLSA, 4 couches enforcement (réplicant ADR-040). 1er ticket = provisionner Sentry/GSC creds DEV-side |
| 2026-05-06 | [[2026-05-06-plan-F-phase-0-verdict]] | Plan F Phase 0 verdict CLOSE — 4 livrables analyse (F0.2 STRIDE 4 surfaces, F0.3 SAMM v2, F0.4 SLSA baseline, F0.5 verdict). 12 findings (5 critiques + 7 importants) + 4 patterns transverses (T1 audit log, T2 rate limit, T3 secrets, T4 defense in depth). Score SAMM 1.26 → cible 2.07 sur 6 mois. SLSA actuel L0.5 → cible L2. F1-F7 ré-ordonnés par criticité empirique. Plan Phase 1 = 3 sprints × 2 sem (~22-25j cumulés). F0.1 (provisioning Sentry/GSC) reste bloqueur humain |
| 2026-05-06 | [[2026-05-06-signal-d-empirical-update]] | Signal D mesuré empiriquement post-GSC SA add (action humaine 1-clic). top 30 URLs traffic-driving = **100% indexed** (verdict ✅ NOT RED). Aggregate 28j : 2093 clicks / 126K impressions / CTR 1.66% / position avg 14.9 (page 2 Google). Verdict sprint reste F par défaut, désormais avec evidence empirique 3 signaux. Implication D : priorité Phase 1+ devient "qualité position" (D1+D5) plutôt que "coverage" (déjà OK). Caveat : env var `GSC_SITE_URL` URL-prefix-format alors que propriété GSC = Domain — à aligner Sprint 1 |
| 2026-05-06 | [[2026-05-06-signal-A-empirical-correction]] | Signal A mesuré empiriquement (Sentry déjà provisionné — découvert via SOPS encrypted file). 4 projets Sentry actifs (DEV+PROD × backend+frontend), `@sentry/nestjs` + `@sentry/remix` intégrés, CI inject via SOPS exec-env. Mesure : **0 issues PROD 14d, 0 events PROD 24h** (verdict ✅ NOT RED). Correction : audit-trails #163/#164/#166 annonçaient « A NOT MEASURED » à tort. **3/3 signaux désormais mesurés empiriquement NOT RED**. Plan F Phase 1 inchangé sur le fond. Leçon : étendre recherche secrets aux `secrets/*.sops.env` avant conclure « manquant » |
| 2026-05-06 | [[2026-05-06-9-chantiers-state-handoff]] | Snapshot canon état 9 chantiers A→I à clôture session 2026-05-06. F en `proposed` Sprint 1 (2 PRs monorepo #338/#339 OPEN auto-merge), A TBD (signal NOT RED), D `partial` (ADR-040 LIVE, signal NOT RED), B/E/G/I `partial` (ADRs proposed avec implementation_status), C infra close (verdict READY 2026-05-01), H Phase 1 mergée. Handoff vers nouvelle session : 3/3 signaux empiriques NOT RED, action user = vérifier #338/#339 mergé puis Sprint 1 ticket #5 (gitleaks/trufflehog CI). 6 mémoires DEV créées cette session |
| 2026-05-06 | [[2026-05-06-r1-drift-canon-shipped]] | R1 drift canon — 3 PRs séquencées (#317/#318/#319) éliminent le drift R1 transactionnel par construction via `@repo/seo-roles@0.3.0` `classifyKeywordToRole` (R2_PRODUCT priorité 1 dans orderedRoles). Étend opérationnellement ADR-040 sans nouvelle décision architecturale. 4 couches enforcement actives (TS branded + Zod + 46 golden tests `node:test` + ast-grep `seo-no-inline-role-keyword-pattern`). Smoke 3 gammes verts (R1 conserve volume, 0 drift transactionnel, excludedTransactionalKeywords collecté). Décisions tracées : R3_guide split transitionnel, liste marques R6 inline conservatrice, PR-4 `PurchaseGuideDataService.getR1Slots` rename différée |
| 2026-05-06 | [[2026-05-06-sentry-prod-go-live]] | Sentry+SOPS go-live PROD — 4 PRs monorepo livrées (#324/#327/#329/#334). Wiring complet (`instrument.ts`, `@SentryExceptionCaptured()` decorator, frontend SDK via `window.ENV`), infra SOPS+age multi-recipient (`dev_vps` triage + `runner_vps` runtime), `sops exec-env` wrapper dans ci.yml (preprod) et deploy-prod.yml (prod), tag `v2026.05.06-sentry-prod` poussé → CI run #25450146001 success → `https://www.automecanik.com/` retourne `window.ENV.VITE_SENTRY_DSN` populé. 4 email alert rules canon (2 default high-priority + 2 custom "first error level≥error 30min throttle"). 3 events captés en preprod validation (issue `2a32cd25` "Invalid API key" — surface ADR-028 anon-only-key bug en 30s, exactement la valeur d'observabilité). Décisions canon : SOPS+age vs GH Secrets/dotenvx/Doppler/Vault (auto-hosted, multi-recipient, no SaaS deploy-time) ; fallback `::warning::` si sops absent (observability ne bloque jamais deploy) ; `set -a; . .env; set +a` avant compose pour éviter env stripping (PR #329 hotfix). Précondition Plan F Sprint 1 "Signal A mesurable" désormais débloquée empiriquement |
| 2026-05-06 | [[2026-05-06-r1-router-audit-cycle]] | Audit verifier-premier-constat R1 Router — cycle complet 12 PRs (9 monorepo : #321 #322 #325 #326 #328 #331 #332 #333 #337 ; 3 vault : #169 ADR-041 / #170 ADR-042 / #171 supersede). Audit externe vérifié 12 claims (10 VERIFIED + 2 PARTIALLY). Gains DB : `has_safe_table` 26→**169/169 (100%)** via PR #332 backfill direct from RAG mirror, `total_with_drift` 3→**0** via PR #321+#328 cleanup, `@repo/seo-roles` 0.3.0→**0.4.0** mappings frontend shorts. ADR-041 R1 router posture reaffirmed (`proposed`) ; ADR-042 wiki gamme skeleton-generator over-engineered (`proposed`→`superseded` post-pushback "déjà les 232 gamme on du contenu en R1"). 5 mémoires user-level capitalisées (verify_file_state, branch_freshness, gh_pr_edit_silent_fail, audit_hypotheses_validated, validate_full_context_before_planning_solution) |
| 2026-05-07 | [[2026-05-07-r-stack-audit]] | Audit baseline R-stack pré-refondation [[ADR-046-r-stack-single-generator-and-layers]] + [[ADR-047-seo-role-contracts-as-code]]. Mesures empiriques : RAG legacy gammes = **1655 fichiers** (~16.8 MiB total, ~10.6 KiB/fichier), 8 vehicles legacy ; wiki SoT vide pour gammes/vehicles (R7 brands seul fonctionne, 36/36 sync `exports/rag/constructeurs/`) ; 8 enrichers backend, R1 fragmenté en **10 fichiers** (services + configs), R1 bump 1500/3000 déjà shipped PR monorepo #346 commit `9f72a0bd` ; règle métier hardcodée détectée `R1_MICRO_SEO_MIN_CHARS = 1500` à `r1-enricher.service.ts:30` (sera migrée vers `seo-role-contracts/r1.ts` Phase 2 PR-S) ; `@repo/seo-roles@0.5.0` détient identité **et** comportement (`forbidden-overlap.ts` à déplacer Phase 2 PR-G, bump major 1.0.0) ; ast-grep `no-direct-rag-knowledge-write.yml` déjà actif (Phase 1 PR-A étendra l'allowlist plutôt que créer). 7 ADRs amont cohérents, aucun blocage avant Phase 1. Plan détaillé : `.claude/plans/je-remarque-une-faiblesse-eventual-flamingo.md` (7 phases, 23 PRs, 6-8 semaines) |
| 2026-05-07 | [[2026-05-07-pr339-deploy-regression]] | Audit-trail régression deploy DEV preprod : PR #339 fail-fast `SESSION_SECRET` (commit `6c7df152`) a touché uniquement `main.ts` sans propager l'env var dans `ci.yml`/`docker-compose.preprod.yml`/`gh secret`. 5 deploys consécutifs failed depuis 2026-05-06 18:03 UTC. Cascade : tag PROD bloqué, ship Sentry CSP fix (PR #344) bloqué. Fix forward via PR monorepo #351 (3 fichiers, 12+ lignes) aligné pattern existant `SUPABASE_*` (GH secret → heredoc → compose), pas SOPS. Memory `feedback_check_secret_propagation_when_adding_fail_fast` créée. Mesure préventive proposée : CI gate `secret-propagation-check` croisant `getOrThrow` backend × `.env.example` × `ci.yml` × compose |

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
