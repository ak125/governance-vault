---
type: moc
status: canon
updated: 2026-04-20
---

# MOC: Incidents

Index des incidents et post-mortems. Cette MOC est la porte d'entree pour tout evenement qui a impacte la production, la securite, ou l'integrite des donnees.

> Les **retrospectives** (non-incident) sont dans [[MOC-AuditTrail]].
> Les **decisions** issues d'incidents deviennent des [[MOC-Decisions|ADRs]].

---

## Incidents Recents

| ID | Date | Severite | Titre | Status |
|----|------|----------|-------|--------|
| [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc\|INC-2026-005]] | 2026-04-20 | High | GSC 5xx vehicle page cold RPC | Investigating |
| INC-2026-004 | 2026-04-20 | High | `___xtr_msg` firehose cascade — timeouts Supabase REST | Resolved |
| INC-2026-002 | 2026-04-14 | Critical | Paybox tunnel SEV1 IPN blocked (25j) | Closed |
| INC-2026-01-30 | 2026-02-03 | Critical | Paybox OrderId Format Bug (silent) | Closed |
| INC-2026-01-11 | 2026-01-11 | Critical | rm/ Module Crash Production | Closed |

---

## Par Severite

### Critical

- [[2026-04-14-paybox-tunnel-sev1-ipn-blocked]] — 3 bugs cumules Paybox, 25j de commandes non-confirmees (559 EUR GMV non-recuperes)
- [[2026-02-03-paybox-orderid-format]] — Bug silencieux format orderId callback Paybox (durée inconnue)
- [[2026-01-11_critical_rm-module-crash]] — Crash production module rm/ (~15min downtime)

### High

- [[2026-04-20_high_xtr-msg-firehose-cascade]] — Firehose logs d'erreur dans `___xtr_msg` sature PostgREST et cree une boucle positive de timeouts (-95 % inserts apres fix, table dediee `__error_logs` + pg_cron 30j)

### Medium

- (aucun)

### Low

- (aucun)

---

## Par Annee

### 2026

- [[2026-04-20_high_xtr-msg-firehose-cascade]] — Error log firehose → boucle positive PostgREST → timeouts 15s (fix: RPC + buffer + table dediee)
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
4. **Linker** l'incident depuis cette MOC (sections "Incidents Recents", "Par Severite", "Par Annee")
5. Si le post-mortem produit une decision architecturale, **creer une ADR** via `_templates/adr-template.md`
6. Commit **signe** avec message clair : `docs(incident): INC-YYYY-MM-DD <short-title>`

---

## Actions Correctives Issues d'Incidents

| Incident | Action | Status |
|----------|--------|--------|
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
| Total incidents documentes | 4 |
| Incidents critiques | 3 |
| Incidents high | 1 |
| MTTR pire cas | 25 jours (INC-2026-002, detection J+25) |
| MTTR moyen hors detection | ~4h (resolution technique une fois detecte) |
| MTTD pire cas | 25 jours (INC-2026-002, pas d'alerte metier avant PREV-1) |
| Incidents ayant produit une ADR | 2 (ADR-001, ADR-004, ADR-014 + ADR-015 a creer) |
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

_Derniere mise a jour: 2026-04-20_
