# MOC: Incidents

Index des incidents et post-mortems.

---

## Incidents Récents

| ID | Date | Sévérité | Titre | Status |
|----|------|----------|-------|--------|
| INC-2026-002 | 2026-04-14 | Critical (SEV1) | Paybox payment tunnel — 25 jours IPN bloqué | Closed |
| INC-2026-001 | 2026-02-03 | Critical | Bug Format OrderId Paybox (0% paid since 2025) | Closed |
| INC-2026-000 | 2026-01-11 | Critical | rm/ Module Crash Production | Closed |

---

## Par Sévérité

### Critical
- [[2026-04-14-paybox-tunnel-sev1-ipn-blocked]] — Paybox tunnel 25j (3 bugs cumulés, 559€ GMV perdue)
- [[2026-02-03-paybox-orderid-format]] — Format orderId Paybox (0% paid since 2025, 5 bugs corrigés)
- [[2026-01-11_critical_rm-module-crash]] — Crash production module rm/ (~15min downtime)

### High
- (aucun)

### Medium
- (aucun)

### Low
- (aucun)

---

## Par Année

### 2026
- [[2026-04-14-paybox-tunnel-sev1-ipn-blocked]] — Tunnel Paybox cassé 25j (CF WAF + RPC type + gate errorCode)
- [[2026-02-03-paybox-orderid-format]] — Format orderId Paybox (historique, 0% paid since 2025)
- [[2026-01-11_critical_rm-module-crash]] — rm/ module import error

### 2025
- (aucun incident documenté)

---

## Statistiques

| Métrique | Valeur |
|----------|--------|
| Total incidents documentés | 3 |
| Incidents critiques | 3 |
| MTTR moyen (incidents critiques) | ~8h |
| MTTD pire cas | 25 jours (INC-2026-002, détection externe) |

---

## Actions Correctives Issues d'Incidents

| Incident | Action | Status |
|----------|--------|--------|
| INC-2026-002 | PREV-1 cron 15min alerting Gmail OAuth2 | Complété |
| INC-2026-002 | PREV-4 Phase 1 Caddy retention 30j | Complété |
| INC-2026-002 | M1 sanitize logs paybox.service.ts | Complété |
| INC-2026-002 | M2 gate errorCode fix | Complété |
| INC-2026-002 | PREV-2 canary E2E CI paiement | Planifié (2026-05-15) |
| INC-2026-002 | PREV-4 Phase 2 Cloudflare R2 log ship | Planifié (2026-05-15) |
| INC-2026-002 | ADR Paybox pipeline stability | Planifié (2026-04-30) |
| INC-2026-002 | Runbook payments-tunnel-debug | Planifié (2026-04-30) |
| INC-2026-002 | Lint CI migration-orpheline | Planifié (2026-05-30) |
| INC-2026-001 | Helper `normalizeOrderId()` centralisé | Complété |
| INC-2026-000 | Créer ADR-001 (Environment Separation) | Complété |
| INC-2026-000 | Créer ADR-004 (rm/ Module Scope) | Complété |
| INC-2026-000 | Ajouter verification CI imports | Planifié |

---

## Template

Voir `01-incidents/_templates/incident-template.md`

---

## Processus Incident

1. Détection incident
2. Investigation (max 4h)
3. Résolution
4. Post-mortem (max 48h)
5. Actions correctives identifiées
6. Mise à jour MOC
7. Revue trimestrielle

---

_Dernière mise à jour: 2026-04-18_
