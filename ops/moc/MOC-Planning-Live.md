---
type: moc
status: proposed
updated: 2026-05-25
schema_version: planning.v1
semantic_hash: 290d8a0dee7e4b5a
adr_link: ADR-053
---

# MOC-Planning-Live

## Items actifs (auto-generated)

| canonical_id | priority | item_type | status | title |
|--------------|----------|-----------|--------|-------|
| github:ak125/nestjs-remix-monorepo:pr:494 | P0 | PR | review | feat(seo): automate post-incident recovery monitoring (D+3 → D+14) |
| github:ak125/governance-vault:pr:59 | P1 | PR | review | docs(knowledge): investigation R8 enricher vehicle-not-found blocker (ADR-022) |
| github:ak125/governance-vault:pr:149 | P2 | PR | review | fix(scripts): check-signatures supports git worktrees |
| github:ak125/nestjs-remix-monorepo:pr:110 | P2 | PR | review | fix(catalog): dedupe + stable mc_sort ordering in catalog hierarchy |
| github:ak125/nestjs-remix-monorepo:pr:472 | P2 | PR | review | fix(canon): update registries ADR ref to ADR-059 (was ADR-058) |
| github:ak125/nestjs-remix-monorepo:pr:490 | P2 | PR | review | fix(seo): require admin auth on SitemapV10 mutating endpoints |
| github:ak125/nestjs-remix-monorepo:pr:534 | P2 | PR | review | fix(frontend): wrap fetchPriority in lowercase helper for React 18 runtime |
| github:ak125/nestjs-remix-monorepo:pr:662 | P2 | PR | review | fix(observability): calibrate Sentry traces sample rate to 2% for free quota |
| github:ak125/nestjs-remix-monorepo:pr:693 | P2 | PR | review | fix(db): get_vehicle_page_data_cached VOLATILE — true root cause of R8 503 (GSC 5xx) |
| github:ak125/nestjs-remix-monorepo:pr:729 | P2 | PR | review | fix(r8): breadcrumb position 5 missing item URL + microdata coverage |
| github:ak125/nestjs-remix-monorepo:pr:741 | P2 | PR | review | fix(seo): 404 catch-all emits X-Robots-Tag noindex,follow |
| github:ak125/governance-vault:pr:255 | P3 | PR | review | refactor(_scripts): split governance_constants into per-enum-family package |
| github:ak125/governance-vault:pr:288 | P3 | PR | review | feat(adr): ADR-073 Canonical Fact Graph (L3) + Editorial Evidence Cache (L4) — extension to ADR-070 |
| github:ak125/nestjs-remix-monorepo:pr:156 | P3 | PR | review | feat(r8): pilier A — enricher motorisation-specific via DB + engine profile |
| github:ak125/nestjs-remix-monorepo:pr:183 | P3 | PR | review | refactor(skill): split seo-content-architect SKILL.md into references (-44% tokens) |
| github:ak125/nestjs-remix-monorepo:pr:315 | P3 | PR | review | refactor(seo-roles): R6 payload discriminators → canonical R6_GUIDE_ACHAT |
| github:ak125/nestjs-remix-monorepo:pr:353 | P3 | PR | review | feat(ast-grep): block direct Anthropic SDK import in scripts/seo (PR-B) |
| github:ak125/nestjs-remix-monorepo:pr:354 | P3 | PR | review | feat(seo-batch): add AGENTS.md ownership canon R0-R8 (PR-C) |
| github:ak125/nestjs-remix-monorepo:pr:394 | P3 | PR | review | perf(frontend): lazy-load PieceDetailModal off-viewport modal (Sprint perf PR-4) |
| github:ak125/nestjs-remix-monorepo:pr:453 | P3 | PR | review | perf(ai-content): enable Anthropic prompt cache on system block |
| github:ak125/nestjs-remix-monorepo:pr:456 | P3 | PR | review | refactor(ai-content): make maxTokens required, drop magic 4096 fallback (stacked on #455) |
| github:ak125/nestjs-remix-monorepo:pr:478 | P3 | PR | review | feat(wiki-promotion): pipeline deterministe raw to proposal (pr-3a) |
| github:ak125/nestjs-remix-monorepo:pr:479 | P3 | PR | review | feat(scripts/cron): scheduler systemd + immutable snapshots (pr-5b) |
| github:ak125/nestjs-remix-monorepo:pr:481 | P3 | PR | review | feat(db): migrations seo projection 7 tables + 2 mvs (pr-6a) |
| github:ak125/nestjs-remix-monorepo:pr:483 | P3 | PR | review | feat(seo/projection): bullmq workers + contract check (pr-6b) |
| github:ak125/nestjs-remix-monorepo:pr:485 | P3 | PR | review | feat(seo/projection): read rpc + adapter (pr-7a) |
| github:ak125/nestjs-remix-monorepo:pr:486 | P3 | PR | review | feat(seo/projection): frontend wiring + rollout + guards (pr-7b) |
| github:ak125/nestjs-remix-monorepo:pr:492 | P3 | PR | review | feat(seo): sitemap freshness SLO endpoint + daily CI watchdog |
| github:ak125/nestjs-remix-monorepo:pr:532 | P3 | PR | review | feat(seo): pr-a1 h1 forensic audit (read-only, zéro ddl) |
| github:ak125/nestjs-remix-monorepo:pr:533 | P3 | PR | review | feat(seo): pr-a2 audit persistence (__seo_content_audit, append-only) |
| github:ak125/nestjs-remix-monorepo:pr:535 | P3 | PR | review | feat(seo): pr-b field authority registry (yaml canon + json projection) |
| github:ak125/nestjs-remix-monorepo:pr:536 | P3 | PR | review | feat(rm): PR-RM-1 cache observability for rm_get_page_complete_v2 |
| github:ak125/nestjs-remix-monorepo:pr:538 | P3 | PR | review | feat(seo): pr-c opa write gateway + scanner anti-bypass (single write path) |
| github:ak125/nestjs-remix-monorepo:pr:539 | P3 | PR | review | feat(seo): pr-d event store minimal (atomic update + event in 1 transaction) |
| github:ak125/nestjs-remix-monorepo:pr:541 | P3 | PR | review | feat(seo): pr-e recovery rollout (orchestration only, no write path bypass) |
| github:ak125/nestjs-remix-monorepo:pr:542 | P3 | PR | review | feat(seo): pr-e+1 wire real deps (growthbook sdk + bullmq scheduler + fetch + gsc) |
| github:ak125/nestjs-remix-monorepo:pr:639 | P3 | PR | review | feat(governance): evidence-gates registry — Diagnostic CP V1 V1.5 deferral lock (ADR-077) |
| github:ak125/nestjs-remix-monorepo:pr:641 | P3 | PR | review | feat(env-contract): enforce SUPABASE_ANON_KEY publishable-shape regex |
| github:ak125/nestjs-remix-monorepo:pr:643 | P3 | PR | review | feat(rm): hoist soft-404 cache constants + declarative TTL invariants |
| github:ak125/nestjs-remix-monorepo:pr:645 | P3 | PR | review | feat(ci): add Supabase live-probe to preflight (catch disabled anon keys) |
| github:ak125/nestjs-remix-monorepo:pr:652 | P3 | PR | review | feat(seo-audit): Reality Audit Phase 0.5 — verdict conversion_funnel (0.17%) |
| github:ak125/nestjs-remix-monorepo:pr:655 | P3 | PR | review | feat(seo-audit): GSC Cannibalization Audit — verdict intra-R2 (84%) |
| github:ak125/nestjs-remix-monorepo:pr:670 | P3 | PR | review | feat(seo-kw): canonical KW classification — end the hand-rolled drift (88% R1 → R2/R5 separated) |
| github:ak125/nestjs-remix-monorepo:pr:687 | P3 | PR | review | feat(commerce-loop): sitemap freshness alert — heartbeat + SITEMAP_STALE_V1 (étape 2) |
| github:ak125/nestjs-remix-monorepo:pr:715 | P3 | PR | review | feat(diagnostic): V1A.0 post-merge hardening guards (ADR-080 amendment follow-up) |
| github:ak125/nestjs-remix-monorepo:pr:719 | P3 | PR | review | feat(research): geo-discovery-probe-2026-05 (G10 ADR-081, B1 capture en cours) |
| github:ak125/nestjs-remix-monorepo:pr:732 | P3 | PR | in-progress | feat(seo-monitoring): bloc 4 — CWV aggregation hourly + daily-rum |
| github:ak125/nestjs-remix-monorepo:pr:733 | P3 | PR | in-progress | feat(seo-monitoring): bloc 5 — runtime errors → __seo_event_log (hydration / longtask / chunk-load) |
| github:ak125/nestjs-remix-monorepo:pr:734 | P3 | PR | in-progress | feat(seo-monitoring): bloc 6 final — dashboard admin + funnel correlation + trend-divergence alerts |
| github:ak125/nestjs-remix-monorepo:pr:738 | P3 | PR | review | perf(blog-r3): imgproxy AVIF/WebP picture + responsive preload on conseils hero (LCP) |
| github:ak125/nestjs-remix-monorepo:pr:739 | P3 | PR | review | perf(blog-r3): content-visibility:auto on conseils below-fold blocks (LCP) |
| github:ak125/governance-vault:pr:110 | P5 | PR | review | docs(knowledge): session handoff MVP G6 + ADR-033 alignment 2026-04-30 |
| github:ak125/governance-vault:pr:114 | P5 | PR | review | docs(audit-trail): consigner session 2026-04-30 — repivot ADR-028 Option C → Option D |
| github:ak125/governance-vault:pr:116 | P5 | PR | review | knowledge(seo): handoff — 4 follow-up PRs merged/in-flight + PR-D3 deferred to ADR |
| github:ak125/governance-vault:pr:122 | P5 | PR | review | docs(knowledge): SEO monitor RPC silent-fail pattern — OBSERVE + catch-and-return-empty |
| github:ak125/governance-vault:pr:13 | P5 | PR | review | docs(audit-trail): diagnostic-auto VehicleSelector + shadcn Command + ⌘K (PR #85) |
| github:ak125/governance-vault:pr:131 | P5 | PR | review | audit(session): 2026-05-01 — Roadmap canonisée + Chantier C READY |
| github:ak125/governance-vault:pr:136 | P5 | PR | review | docs(knowledge): audit baseline refresh-script pattern + cross-branch divergence trap |
| github:ak125/governance-vault:pr:151 | P5 | PR | review | knowledge(governance): bilateral back-links to vault-self-review canon |
| github:ak125/governance-vault:pr:173 | P5 | PR | review | proposal(adr-044): R3GuideController backend rename → R3Conseils* + session audit-trail (renumbered from 043) |
| github:ak125/governance-vault:pr:196 | P5 | PR | review | adr(047+050): ratify seo-role-contracts canon + create quality history ADR (MVP-0 Phase 0) |
| github:ak125/governance-vault:pr:211 | P5 | PR | review | adr(051): frontend bundle budget enforcement signal-proven baseline |
| github:ak125/governance-vault:pr:213 | P5 | PR | review | audit-trail(2026-05-08): R6 canon cascade shipped — 4 PRs + ADR-051 |
| github:ak125/governance-vault:pr:214 | P5 | PR | review | docs(adr): ADR-052 SQL role canon deprecation, defer to TS-only (ADR-040) |
| github:ak125/governance-vault:pr:215 | P5 | PR | review | docs(knowledge): canon design-pack handling — improve existing, never duplicate funnel |
| github:ak125/governance-vault:pr:217 | P5 | PR | review | audit-trail(2026-05-08): priority planning vault pending work + ADR-051 collision résolue |
| github:ak125/governance-vault:pr:22 | P5 | PR | review | ADR-019: AI content advisor escalation via Pattern A |
| github:ak125/governance-vault:pr:220 | P5 | PR | review | knowledge(perf): consigne sprint perf bundle 7 leçons signal-proven (2026-05-08) |
| github:ak125/governance-vault:pr:235 | P5 | PR | review | chore(knowledge): update seo-v9 cascade state with PR-2c shipped |
| github:ak125/governance-vault:pr:237 | P5 | PR | review | chore(knowledge): pattern 5 verrous PR foundation anti-breaking cascade |
| github:ak125/governance-vault:pr:240 | P5 | PR | review | docs(rules): R-SEO-URL-IMMUTABLE : URLs canon strictement immuables |
| github:ak125/governance-vault:pr:241 | P5 | PR | review | docs(adr): ADR-052 hoist handoff_targets canon + R6→R1 amendement |
| github:ak125/governance-vault:pr:242 | P5 | PR | review | docs(adr): ADR-054 convention governance standard — audit-trail vault par défaut sur ADR |
| github:ak125/governance-vault:pr:274 | P5 | PR | review | PR-4 — Dependency modernization policy + upgrade matrix |
| github:ak125/governance-vault:pr:29 | P5 | PR | review | audit: P2 quality hardening — accents FR + Phase 9 QA-contenu |
| github:ak125/governance-vault:pr:290 | P5 | PR | review | adr(seo): ADR-074 unified indexability decision plane v1 |
| github:ak125/governance-vault:pr:294 | P5 | PR | review | adr(governance): ADR-075 deployment topology clarification (amend ADR-001) |
| github:ak125/governance-vault:pr:306 | P5 | PR | review | docs(verdict): VERDICT-2026-001 — conversion_funnel_organic = 0.17% (premier verdict G9 ADR-081) |
| github:ak125/governance-vault:pr:64 | P5 | PR | review | docs(adr): ADR-024 Claude Session Timeline Logging via log.md + Auto-Commit Hook |
| github:ak125/governance-vault:pr:70 | P5 | PR | review | docs(knowledge): vehicle-selector Radix Select + grouped fuel pattern |
| github:ak125/governance-vault:pr:72 | P5 | PR | review | docs(r8): debrief honnête Stage 1 vehicle enrichment |
| github:ak125/governance-vault:pr:75 | P5 | PR | review | knowledge: claude-code-skill-modular-pattern (concern-based references split) |
| github:ak125/governance-vault:pr:88 | P5 | PR | review | audit: 2026-04-25 fleet advisor + seo monitoring session recap |
| github:ak125/governance-vault:pr:92 | P5 | PR | review | docs(knowledge): r8 distinct render + scraping canon — session wrap 2026-04-25 |
| github:ak125/governance-vault:pr:93 | P5 | PR | review | knowledge: ADR-024 R1 cache session debrief 2026-04-27 (phases 1-6a) |
| github:ak125/nestjs-remix-monorepo:pr:158 | P5 | PR | review | chore(cleanup): remove 3 dead search components (batch 2) |
| github:ak125/nestjs-remix-monorepo:pr:160 | P5 | PR | review | chore(cleanup): remove 4 dead forms components (batch 3) |
| github:ak125/nestjs-remix-monorepo:pr:164 | P5 | PR | review | test(skill): seo-vault-verify trigger evals + .skill packaging |
| github:ak125/nestjs-remix-monorepo:pr:191 | P5 | PR | review | chore(audit): tool-version-aware baseline + dedicated dependabot group |
| github:ak125/nestjs-remix-monorepo:pr:314 | P5 | PR | review | chore(seo-roles): migrate 4 blog routes R3_BLOG → R3_CONSEILS |
| github:ak125/nestjs-remix-monorepo:pr:335 | P5 | PR | review | chore(blog): mark R3GuideController/Service/interfaces @deprecated (PR-1, ADR-044) |
| github:ak125/nestjs-remix-monorepo:pr:387 | P5 | PR | review | chore(perf): bundle:analyze + bundle:report scripts (Sprint perf PR-1, ADR-051) |
| github:ak125/nestjs-remix-monorepo:pr:395 | P5 | PR | review | chore(frontend): vendor breakdown audit + 9 anomaly checks (Sprint perf PR-5) |
| github:ak125/nestjs-remix-monorepo:pr:396 | P5 | PR | review | chore(frontend): Remix hydration payload audit (Sprint perf PR-5bis) |
| github:ak125/nestjs-remix-monorepo:pr:397 | P5 | PR | review | chore(ci): bundle freshness check + budget README matrix (Sprint perf PR-6) |
| github:ak125/nestjs-remix-monorepo:pr:451 | P5 | PR | review | chore(db): set ALTER DEFAULT PRIVILEGES before Supabase 2026-10-30 Data API change |
| github:ak125/nestjs-remix-monorepo:pr:455 | P5 | PR | review | obs(ai-content): log cache hit-rate per Anthropic call (stacked on #453) |
| github:ak125/nestjs-remix-monorepo:pr:489 | P5 | PR | review | docs(cleanup): substitution http_live retention pivot — formalize PR #466 lesson |
| github:ak125/nestjs-remix-monorepo:pr:499 | P5 | PR | review | chore(cleanup): drop 5 frontend dead API services (PR-4 batch 3) |
| github:ak125/nestjs-remix-monorepo:pr:679 | P5 | PR | review | chore(gitignore): ignore .claude/worktrees/ |
| github:ak125/nestjs-remix-monorepo:pr:684 | P5 | PR | review | chore(docs): reconcile RAG references with canon ADR-031/046 + anti-drift guard |
| github:ak125/nestjs-remix-monorepo:pr:737 | P5 | PR | review | docs(audit): ahrefs link verdicts (internal + external) — empirical, read-only |
| github:ak125/nestjs-remix-monorepo:pr:740 | P5 | PR | review | chore(registry): add audit/seo-*.md ownership glob (PR #736 follow-up) |
| github:ak125/nestjs-remix-monorepo:pr:301 | P6 | PR | review | chore(deps): Bump dotenv from 17.2.4 to 17.4.2 |

## Ack block (édition humaine — exception I2)

```yaml
ack:
  github:ak125/governance-vault:pr:40:
    acked_at: '2026-05-08T19:54:21Z'
    acked_by: ak125
  github:ak125/governance-vault:pr:65:
    acked_at: '2026-05-08T19:39:47Z'
    acked_by: ak125
  github:ak125/governance-vault:pr:9:
    acked_at: '2026-05-18T13:06:48Z'
    acked_by: ak125
  github:ak125/nestjs-remix-monorepo:pr:494:
    last_alert_at: '2026-05-25T06:00:02.941608+00:00'
```

## See also

- [[ADR-053-planning-live-system]]
- [[MOC-Roadmap-2026]]
