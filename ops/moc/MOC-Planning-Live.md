---
type: moc
status: proposed
updated: 2026-06-05
schema_version: planning.v1
semantic_hash: 0bf70f5d6b26544e
adr_link: ADR-053
---

# MOC-Planning-Live

## Items actifs (auto-generated)

| canonical_id | priority | item_type | status | title |
|--------------|----------|-----------|--------|-------|
| github:ak125/governance-vault:pr:59 | P1 | PR | review | docs(knowledge): investigation R8 enricher vehicle-not-found blocker (ADR-022) |
| github:ak125/governance-vault:pr:149 | P2 | PR | review | fix(scripts): check-signatures supports git worktrees |
| github:ak125/nestjs-remix-monorepo:pr:472 | P2 | PR | review | fix(canon): update registries ADR ref to ADR-059 (was ADR-058) |
| github:ak125/nestjs-remix-monorepo:pr:534 | P2 | PR | review | fix(frontend): wrap fetchPriority in lowercase helper for React 18 runtime |
| github:ak125/nestjs-remix-monorepo:pr:662 | P2 | PR | review | fix(observability): calibrate Sentry traces sample rate to 2% for free quota |
| github:ak125/nestjs-remix-monorepo:pr:842 | P2 | PR | review | fix(seo-monitor): scope repeatable-job prune to owned jobs (fixes CWV job eviction) |
| github:ak125/governance-vault:pr:255 | P3 | PR | review | refactor(_scripts): split governance_constants into per-enum-family package |
| github:ak125/nestjs-remix-monorepo:pr:353 | P3 | PR | review | feat(ast-grep): block direct Anthropic SDK import in scripts/seo (PR-B) |
| github:ak125/nestjs-remix-monorepo:pr:479 | P3 | PR | review | feat(scripts/cron): scheduler systemd + immutable snapshots (pr-5b) |
| github:ak125/nestjs-remix-monorepo:pr:481 | P3 | PR | review | feat(db): migrations seo projection 7 tables + 2 mvs (pr-6a) |
| github:ak125/nestjs-remix-monorepo:pr:483 | P3 | PR | review | feat(seo/projection): bullmq workers + contract check (pr-6b) |
| github:ak125/nestjs-remix-monorepo:pr:485 | P3 | PR | review | feat(seo/projection): read rpc + adapter (pr-7a) |
| github:ak125/nestjs-remix-monorepo:pr:486 | P3 | PR | review | feat(seo/projection): frontend wiring + rollout + guards (pr-7b) |
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
| github:ak125/nestjs-remix-monorepo:pr:715 | P3 | PR | review | feat(diagnostic): V1A.0 post-merge hardening guards (ADR-080 amendment follow-up) |
| github:ak125/nestjs-remix-monorepo:pr:719 | P3 | PR | review | feat(research): geo-discovery-probe-2026-05 (G10 ADR-081, B1 capture en cours) |
| github:ak125/nestjs-remix-monorepo:pr:738 | P3 | PR | review | perf(blog-r3): imgproxy AVIF/WebP picture + responsive preload on conseils hero (LCP) |
| github:ak125/nestjs-remix-monorepo:pr:739 | P3 | PR | review | perf(blog-r3): content-visibility:auto on conseils below-fold blocks (LCP) |
| github:ak125/nestjs-remix-monorepo:pr:795 | P3 | PR | review | feat(env-contract): env-var drift ratchet detector (extends Phase 2) |
| github:ak125/nestjs-remix-monorepo:pr:796 | P3 | PR | review | feat(diagnostic): PR-1a Result UX — drivability, rapport garage, toggle (kill-switch, OFF par défaut) |
| github:ak125/nestjs-remix-monorepo:pr:797 | P3 | PR | review | feat(diagnostic): PR-2 knowledge reproducibility (export/check snapshot, anti-perte) |
| github:ak125/nestjs-remix-monorepo:pr:805 | P3 | PR | review | feat(media-factory): Fafa compositions — brand palette align + configurable problem text |
| github:ak125/nestjs-remix-monorepo:pr:806 | P3 | PR | review | feat(media-factory): Fafa V1 visual lock + pilot DRAFT plaquettes/compatibilité (7 gates PASS) |
| github:ak125/nestjs-remix-monorepo:pr:824 | P3 | PR | in-progress | feat(merchant-center): GMC price-competitiveness benchmark (inbound, OBSERVE-only) |
| github:ak125/nestjs-remix-monorepo:pr:840 | P3 | PR | review | feat(cwv): pg_cron for RUM aggregation — decouple from dead DEV worker |
| github:ak125/nestjs-remix-monorepo:pr:858 | P3 | PR | review | feat(seo): read-only multi-role SEO readiness cockpit (/seo-readiness) |
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
| github:ak125/governance-vault:pr:29 | P5 | PR | review | audit: P2 quality hardening — accents FR + Phase 9 QA-contenu |
| github:ak125/governance-vault:pr:294 | P5 | PR | review | adr(governance): ADR-075 deployment topology clarification (amend ADR-001) |
| github:ak125/governance-vault:pr:311 | P5 | PR | review | audit: ADR-033 J+30 review 2026-05-29 — PARTIAL |
| github:ak125/governance-vault:pr:312 | P5 | PR | review | audit(adr-033): revue J+30 — verdict FAIL_PARTIAL, proposed maintenu |
| github:ak125/governance-vault:pr:64 | P5 | PR | review | docs(adr): ADR-024 Claude Session Timeline Logging via log.md + Auto-Commit Hook |
| github:ak125/governance-vault:pr:70 | P5 | PR | review | docs(knowledge): vehicle-selector Radix Select + grouped fuel pattern |
| github:ak125/governance-vault:pr:72 | P5 | PR | review | docs(r8): debrief honnête Stage 1 vehicle enrichment |
| github:ak125/governance-vault:pr:75 | P5 | PR | review | knowledge: claude-code-skill-modular-pattern (concern-based references split) |
| github:ak125/governance-vault:pr:88 | P5 | PR | review | audit: 2026-04-25 fleet advisor + seo monitoring session recap |
| github:ak125/governance-vault:pr:92 | P5 | PR | review | docs(knowledge): r8 distinct render + scraping canon — session wrap 2026-04-25 |
| github:ak125/governance-vault:pr:93 | P5 | PR | review | knowledge: ADR-024 R1 cache session debrief 2026-04-27 (phases 1-6a) |
| github:ak125/nestjs-remix-monorepo:pr:387 | P5 | PR | review | chore(perf): bundle:analyze + bundle:report scripts (Sprint perf PR-1, ADR-051) |
| github:ak125/nestjs-remix-monorepo:pr:395 | P5 | PR | review | chore(frontend): vendor breakdown audit + 9 anomaly checks (Sprint perf PR-5) |
| github:ak125/nestjs-remix-monorepo:pr:396 | P5 | PR | review | chore(frontend): Remix hydration payload audit (Sprint perf PR-5bis) |
| github:ak125/nestjs-remix-monorepo:pr:397 | P5 | PR | review | chore(ci): bundle freshness check + budget README matrix (Sprint perf PR-6) |
| github:ak125/nestjs-remix-monorepo:pr:489 | P5 | PR | review | docs(cleanup): substitution http_live retention pivot — formalize PR #466 lesson |
| github:ak125/nestjs-remix-monorepo:pr:499 | P5 | PR | review | chore(cleanup): drop 5 frontend dead API services (PR-4 batch 3) |
| github:ak125/nestjs-remix-monorepo:pr:679 | P5 | PR | review | chore(gitignore): ignore .claude/worktrees/ |
| github:ak125/nestjs-remix-monorepo:pr:684 | P5 | PR | review | chore(docs): reconcile RAG references with canon ADR-031/046 + anti-drift guard |
| github:ak125/nestjs-remix-monorepo:pr:737 | P5 | PR | review | docs(audit): ahrefs link verdicts (internal + external) — empirical, read-only |
| github:ak125/nestjs-remix-monorepo:pr:838 | P5 | PR | review | docs(runtime): record R2 cache header drift evidence |
| github:ak125/nestjs-remix-monorepo:pr:752 | P6 | PR | review | chore(deps): bump nodemailer and @types/nodemailer |
| github:ak125/nestjs-remix-monorepo:pr:753 | P6 | PR | review | chore(deps): bump meilisearch from 0.52.0 to 0.58.0 |
| github:ak125/nestjs-remix-monorepo:pr:815 | P6 | PR | review | chore(deps): bump the tiptap-ecosystem group across 1 directory with 5 updates |
| github:ak125/nestjs-remix-monorepo:pr:817 | P6 | PR | review | chore(deps-dev): bump @commitlint/config-conventional from 20.5.3 to 21.0.2 |

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
```

## See also

- [[ADR-053-planning-live-system]]
- [[MOC-Roadmap-2026]]
