---
type: moc
status: canon
updated: 2026-05-18
---

# MOC: Incidents

Index des incidents et post-mortems. Cette MOC est la porte d'entree pour tout evenement qui a impacte la production, la securite, ou l'integrite des donnees.

> Les **retrospectives** (non-incident) sont dans [[MOC-AuditTrail]].
> Les **decisions** issues d'incidents deviennent des [[MOC-Decisions|ADRs]].

---

## Incidents Recents

| ID | Date | Severite | Titre | Status |
|----|------|----------|-------|--------|
| [[2026-05-23-pieces-media-img-corruption\|INC-2026-015]] | 2026-05-23 | P2 | `pieces_media_img` mass corruption — ~50 % rows malformed (`pmi_folder=''` + `pmi_name` sans extension), 357 009 displayed pieces (103 brands incl. VALEO/SKF 100 %, MAGNETI 82 %) avec icône cassée (imgproxy 400 placeholder). Tier C soft-hide (1 107 390 rows / audit table préservée) + 4 gardes structurelles. Tier B (vraie récupération images) différé : files absents partout dans l'infra ([[ADR-078-pieces-media-img-recovery-tier-c\|ADR-078]]). | Contained |
| [[2026-05-14-INC-2026-005-closure\|INC-2026-005-closure]] | 2026-05-14 | High | GSC email (WNC-10031170) — 30 400 pages 5xx, validation 2026-05-06→2026-05-12 FAILED. Root cause déjà fixée par PR #320. Closure : actions manuelles (CF purge safe + force re-crawl GSC) + invariants AST/lint anti-récidive + smoke v2 (150 URLs seedés) + notify503 port pieces.* | Closed (PR-1 monorepo TBD) |
| [[2026-05-06-cf-cache-poisoning-pieces-5xx\|INC-2026-005-recurrence]] | 2026-05-06 | High | Cloudflare cache poisoning sur loader-thrown 5xx Remix (`/pieces/*` 47 % 5xx, s-maxage=86400 leak) — PR #320 + tag PROD `v2026.05.06-cf-cache-5xx-fix` + CF purge | Resolved |
| [[2026-05-02-diagnostic-tool-unsourced-probas\|INC-2026-013]] | 2026-05-02 | High | Probabilités non sourcées dans `__diag_symptom_cause_link` — 162 rows exposées client `/diagnostic-auto/*` | Open |
| [[2026-04-25-503-vehicle-build-payload-slow\|INC-2026-010]] | 2026-04-25 | Medium | 503 R8 vehicle pages — build_vehicle_page_payload sous-requete catalog mal optimisee (Phase 1 ADR-016). Fix root-cause CTE 2-phases + steady-state guarantees (cron + trigger + canon). | Closed-with-followup (J+14 __error_logs 5xx monitoring) |
| [[2026-04-23-gsc-411k-404-tecdoc-orphans\|INC-2026-012]] | 2026-04-23 | High | 411k pages GSC en 404 (TecDoc V1 orphans + hardcoded 410 shortcut) | Closed-with-monitoring (J+30/60/90) |
| [[2026-04-23-admin-password-hashes-anon-leak\|INC-2026-011]] | 2026-04-23 | Critical | Admin password hashes (`___config_admin.cnfa_pswd`) lisibles via PostgREST anon key (4 tables RLS `USING(true)` héritées) — fix PR #120, aucune trace d'exploitation | Resolved |
| [[2026-04-23-paybox-client-regression-post-inc002\|INC-2026-014]] | 2026-04-23 | Medium | Paybox tunnel — alerte régression client (false-positive : tunnel fonctionnel, conversion ~10%). Empirique 2026-05-08 : 4 paiements clients confirmés depuis cliff (GMV 634.66 €, dernier 2026-05-07) | Closed (false-positive) |
| [[2026-04-23-ci-cwv-backend-boot-crash\|INC-2026-009]] | 2026-04-23 | Medium | CI CWV Performance Gate — APP_URL manquant dans perf-gates.yml (fix PR monorepo #123) | Resolved |
| [[2026-04-22-redis-public-exposure-bsi\|INC-2026-008]] | 2026-04-22 | Medium | Redis DEV public exposure (BSI CB-Report#20260422-10008190) | Resolved |
| [[2026-04-21-503-vehicle-pages-rpc-allowlist-stale-image\|INC-2026-006]] | 2026-04-21 | High | 503 /constructeurs/* — allowlist RPC manquante + image preprod obsolete | Closed (structural fix) |
| [[2026-04-21-false-prod-claim-on-main-merge\|INC-2026-007]] | 2026-04-21 | Low | False prod claim after main merge (doc ambiguity) | Resolved |
| INC-2026-004 | 2026-04-20 | High | `___xtr_msg` firehose cascade — timeouts Supabase REST | Resolved |
| [[2026-04-18_high_diag-engine-rag-seeding\|INC-2026-003]] | 2026-04-18 | High | Diagnostic Engine — Seeding contenu metier (~350 entrées) sans validation RAG/vault (rollback OK, pivot délégation RAG pure) | Closed |
| INC-2026-002 | 2026-04-14 | Critical | Paybox tunnel SEV1 IPN blocked (25j) | Closed |
| INC-2026-01-30 | 2026-02-03 | Critical | Paybox OrderId Format Bug (silent) | Closed |
| INC-2026-01-11 | 2026-01-11 | Critical | rm/ Module Crash Production | Closed |

---

## Par Severite

### Critical

- [[2026-04-23-admin-password-hashes-anon-leak]] — Hashes mot de passe admin (`___config_admin.cnfa_pswd`) lisibles via PostgREST anon key. 4 tables avec policy historique `Enable read access for all users` (template Supabase initial). Fix urgence PR #120. Aucune trace d'exploitation détectée. Résolu pendant audit Vague 4b ADR-021.
- [[2026-04-14-paybox-tunnel-sev1-ipn-blocked]] — 3 bugs cumules Paybox, 25j de commandes non-confirmees (559 EUR GMV non-recuperes)
- [[2026-02-03-paybox-orderid-format]] — Bug silencieux format orderId callback Paybox (durée inconnue)
- [[2026-01-11_critical_rm-module-crash]] — Crash production module rm/ (~15min downtime)

### High

- [[2026-05-06-cf-cache-poisoning-pieces-5xx]] — Récurrence INC-2026-005 sur la chaîne pieces RM V2. Cause CDN : `headers: HeadersFunction = () => ({...})` zero-arg appliquait `s-maxage=86400` à toutes les réponses, y compris loader-thrown 5xx → Cloudflare cache 500 pendant 24h. Sample 930 URLs : 47 % `/pieces/*` en 500 cache HIT. PR #320 : helper `~/utils/cache-control` errorHeaders-aware + 7 tests + lint dual-layer (script bash + ast-grep + step CI blocant + pre-commit).
- [[2026-05-02-diagnostic-tool-unsourced-probas]] — 162 scores `relative_score` dans `__diag_symptom_cause_link` copiés depuis RAG éditorial non sourcé (`bruits-freinage.md`), exposés côté client `/diagnostic-auto/*`. 4 PRs planifiées (migration DB `is_trusted`, backend, frontend, re-sourcing). ADR-035 proposé.
- [[2026-04-23-gsc-411k-404-tecdoc-orphans]] — 411 k pages GSC en 404 (TecDoc V1→V2 remap orphans dans `__sitemap_p_link` + shortcut 410 hardcodé). 3 PRs monorepo (#133/#134/#135) + migration N2 (#136) + tag `v2026.04.23-gsc-404-tecdoc-fix`. Sitemap régénéré avec filtre actif (102 395 URLs stable, 0 orphan).
- [[2026-04-20_high_xtr-msg-firehose-cascade]] — Firehose logs d'erreur dans `___xtr_msg` sature PostgREST et cree une boucle positive de timeouts (-95 % inserts apres fix, table dediee `__error_logs` + pg_cron 30j)
- [[2026-04-18_high_diag-engine-rag-seeding]] — INC-2026-003 : Agent Claude Code a fabriqué ~350 entrées contenu métier (synonymes/DTC codes) en DB sans consulter RAG `/opt/automecanik/rag/knowledge/` ni instructions vault. Rollback OK + pivot architectural vers délégation RAG pure (`RagProxyService.search` runtime, zero pre-computed mapping). Source du canon `feedback_rag_vault_always_first`.

### Medium

- [[2026-04-23-paybox-client-regression-post-inc002]] — **FALSE POSITIVE** — alerte régression Paybox post-INC-2026-002. Hypothèse SEV1 invalidée 3h après ouverture par 6 preuves empiriques (tunnel 100 % fonctionnel). Vraie cause = conversion commerciale ~10 % vs 30-40 % norme e-commerce. Confirmé 2026-05-08 : 4 paiements clients réels depuis cliff (GMV 634.66 €, dernier 2026-05-07). Renumeroté INC-010 → INC-014 (collision avec 503 vehicle).
- [[2026-04-23-ci-cwv-backend-boot-crash]] — **RÉSOLU** — root cause trouvée : `APP_URL` manquant dans `.github/workflows/perf-gates.yml`. Fix 1 ligne via monorepo PR #123. Backend crash silencieux dû à `bufferLogs:true` masquant la `ConfigurationException`.
- [[2026-04-22-redis-public-exposure-bsi]] — Redis DEV sur `46.224.118.55:6379` exposé publiquement sans auth, signalé par BSI (CERT-Bund). Remédiation 2 couches (Hetzner Cloud Firewall + alignement compose files). Zero compromission détectée.

### Low

- (aucun)

---

## Par Annee

### 2026

- [[2026-05-06-cf-cache-poisoning-pieces-5xx]] — INC-2026-005-recurrence : Cloudflare cache poisoning 24h sur loader-thrown 5xx Remix (`/pieces/*` 47 % 5xx). PR #320 (commit a93b7dcb) helper buildCacheHeaders + lint guard.
- [[2026-05-02-diagnostic-tool-unsourced-probas]] — 162 scores non sourcés dans moteur diagnostic (probas copiées depuis RAG éditorial), 4 PRs d'atténuation planifiées (ADR-035)
- [[2026-04-23-gsc-411k-404-tecdoc-orphans]] — 411 k GSC 404 backlog (TecDoc V1 orphans + hardcoded shortcut), 3 PRs monorepo + migration N2 + tag `v2026.04.23-gsc-404-tecdoc-fix`
- [[2026-04-23-admin-password-hashes-anon-leak]] — INC-2026-011 (Critical, resolved) : 4 tables RLS `USING(true)` exposaient hashes admin via PostgREST anon key (PR #120, audit Vague 4b ADR-021)
- [[2026-04-23-paybox-client-regression-post-inc002]] — INC-2026-014 (Medium, false-positive) : alerte régression Paybox invalidée 3h après ouverture, vraie cause = conversion commerciale (4 paiements clients confirmés post-cliff, GMV 634.66 €)
- [[2026-04-22-redis-public-exposure-bsi]] — Redis DEV exposé publiquement (BSI), firewall Hetzner + alignement compose files (PR monorepo #102)
- [[2026-04-20_high_xtr-msg-firehose-cascade]] — Error log firehose → boucle positive PostgREST → timeouts 15s (fix: RPC + buffer + table dediee)
- [[2026-04-18_high_diag-engine-rag-seeding]] — Diagnostic engine : violation gouvernance contenu (RAG ignoré, ~350 entrées fabriquées, rollback + pivot délégation RAG pure)
- [[2026-04-14-paybox-tunnel-sev1-ipn-blocked]] — Paybox tunnel IPN blocked 25 jours (Cloudflare WAF + gate errorCode + RPC type error)
- [[2026-02-03-paybox-orderid-format]] — Format orderId callback Paybox mismatch DB
- [[2026-01-11_critical_rm-module-crash]] — rm/ module import error

### 2025

- (aucun incident documente)

---

## Taxonomie de Severite

| Severite | Criteres | SLA detection | SLA post-mortem |
|----------|----------|----------------|------------------|
| **Critical** | Downtime PROD, perte de donnees, breach securite, paiements bloques | Immediate | < 48h |
| **High** | Degradation majeure, SLO viole sur service critique, fuite non-sensible | < 1h | < 72h |
| **Medium** | Bug user-visible contournable, performance degradee, regression sur feature secondaire | < 4h | < 7j |
| **Low** | Defauts cosmetiques, warnings, issues de devex | < 24h | Optionnel |

Un incident de severite `Critical` ou `High` **DOIT** declencher une activation du kill-switch Airlock (`AI_VAULT_WRITE=false`) si une action IA/agent est suspectee dans la chaine causale.

---

## Processus Incident (lifecycle)

| Etape | Duree max | Responsable | Artefact produit |
|-------|-----------|-------------|------------------|
| 1. **Detection** | N/A | Monitoring / utilisateur | Ticket ou alerte |
| 2. **Triage** | 15 min (Critical) / 1h (High) | On-call engineer | Assignation severite |
| 3. **Mitigation** | < 1h (Critical) | Engineer + tech lead | Rollback / hotfix / kill-switch |
| 4. **Investigation** | < 4h | Engineer assigne | Timeline + root cause preliminaire |
| 5. **Resolution** | Variable | Engineer assigne | Fix deploye et verifie |
| 6. **Post-mortem** | Voir SLA severite | Engineer + owner | Document dans `ledger/incidents/YYYY/` |
| 7. **Actions correctives** | Tracees jusqu'a closure | Tech lead | ADR(s), nouvelles rules, tests ajoutes |
| 8. **Revue trimestrielle** | T+90j apres incident | Governance team | Update de cette MOC |

---

## RACI

| Activite | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| Detection | Monitoring / Any | On-call | — | Team |
| Triage | On-call | Tech lead | Engineer concerne | Team |
| Mitigation | On-call + Engineer | Tech lead | Architecture team | Fafa |
| Post-mortem redaction | Engineer assigne | Tech lead | Team, Governance | Fafa |
| Decision architecturale issue de l'incident | Architecture team | Fafa | Engineer, Governance | Team |
| Closure formelle | Governance team | Fafa | — | Team |

---

## Comment declarer un nouvel incident

1. **Copier** le template : `_templates/incident-template.md`
2. **Creer** le fichier dans `ledger/incidents/YYYY/` avec le pattern de nom :
   ```
   YYYY-MM-DD_<severity>_<short-title>.md
   ```
   Exemple : `2026-01-11_critical_rm-module-crash.md`
3. **Remplir** le frontmatter YAML :
   ```yaml
   ---
   type: incident
   status: investigating | mitigated | resolved | closed
   severity: critical | high | medium | low
   date: YYYY-MM-DD
   detected_at: YYYY-MM-DDTHH:MM:SSZ
   resolved_at: YYYY-MM-DDTHH:MM:SSZ
   owner: <nom>
   related_adrs: []
   ---
   ```
4. **Linker** l'incident depuis cette MOC (sections « Incidents Recents », « Par Severite », « Par Annee »)
5. Si le post-mortem produit une decision architecturale, **creer une ADR** via `_templates/adr-template.md`
6. Commit **signe** avec message clair : `docs(incident): INC-YYYY-MM-DD <short-title>`

---

## Actions Correctives Issues d'Incidents

| Incident | Action | Status |
|----------|--------|--------|
| INC-2026-013 | ADR-035 flag `is_trusted` + `source_origin` sur `__diag_symptom_cause_link` | ✅ Draft proposé (cette PR) |
| INC-2026-013 | PR-A migration DB (nestjs-remix-monorepo) | ⏳ Planifiée |
| INC-2026-013 | PR-B backend masque probas si `is_trusted=false` | ⏳ Planifiée |
| INC-2026-013 | PR-C frontend adapte rendu | ⏳ Planifiée |
| INC-2026-013 | Issue coordination monorepo ouverte | ✅ Ouverte (voir INC-2026-013) |
| INC-2026-01-11 | Creer [[ADR-001-environment-separation]] (Environment Separation) | Complete |
| INC-2026-01-11 | Creer [[ADR-004-rm-module-scope]] (rm/ Module Scope) | Complete |
| INC-2026-01-11 | Ajouter verification CI imports | Planifie |
| INC-2026-01-30 | Helper centralise `normalizeOrderId()` + tests | Complete |
| INC-2026-01-30 | Creer [[ADR-014-remove-paybox-callback-test]] | Complete |
| INC-2026-002 | PREV-1 cron 15min alerting email Gmail OAuth2 | Complete (2026-04-18) |
| INC-2026-002 | PREV-4 Phase 1 Caddy logs retention 30j | Complete (2026-04-18) |
| INC-2026-002 | M1 Sanitize logs paybox.service.ts (10 tests) | Complete |
| INC-2026-002 | M2 Bug #2 Gate errorCode fix (13 tests) | Complete |
| INC-2026-002 | PREV-2 Canary E2E paiement en CI (Playwright) | Planifie (2026-05-15) |
| INC-2026-002 | PREV-4 Phase 2 Ship Caddy logs vers Cloudflare R2 | Planifie (2026-05-15) |
| INC-2026-002 | ADR-015 Paybox pipeline stability (a creer) | Planifie (2026-04-30) |
| INC-2026-002 | Runbook `.spec/runbooks/payments-tunnel-debug.md` | Planifie (2026-04-30) |
| INC-2026-002 | Lint CI migration-orpheline (detection `.rpc()` sans migration) | Planifie (2026-05-30) |
| INC-2026-002 | Dashboard analytics refus CB (ic_postback FAILED) | Planifie (2026-06-01) |
| INC-2026-004 | Audit autres services ecrivant dans `___xtr_msg` | Planifie (2026-04-30) |
| INC-2026-004 | Scanner autres tables fourre-tout (ex: `__blog_advice`) | Planifie (2026-05-15) |
| INC-2026-004 | Alerte rate inserts `__error_logs` > 30/min | Planifie (2026-05-15) |

---

## Statistiques

| Metrique | Valeur |
|----------|--------|
| Total incidents documentes | 13 |
| Incidents critiques | 4 |
| Incidents high | 4 |
| MTTR pire cas | 25 jours (INC-2026-002, detection J+25) |
| MTTR moyen hors detection | ~4h (resolution technique une fois detecte) |
| MTTD pire cas | 25 jours (INC-2026-002, pas d'alerte metier avant PREV-1) |
| Incidents ayant produit une ADR | 3 (ADR-001, ADR-004, ADR-014, ADR-035) |
| Incidents ayant declenche un kill-switch | 0 |
| Impact business cumule | 559 EUR GMV (INC-2026-002, accepte comme cout) |

---

## Template

Voir [[_templates/incident-template|_templates/incident-template.md]]

---

## Voir aussi

- [[MOC-AuditTrail]] — Retrospectives de phase, bundles rejetes, audits ponctuels
- [[MOC-Decisions]] — ADRs canoniques (souvent produites par des post-mortems)
- [[MOC-Rules]] — Regles T/G/AI/V (peuvent evoluer suite a incident)
- [[airlock-decisions-reference]] — DEC-004 Kill-Switch Global + DEC-007 Incident Response

---

_Derniere mise a jour: 2026-05-02_
