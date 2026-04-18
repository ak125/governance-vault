---
id: INC-2026-002
date: 2026-04-14
severity: critical
status: closed
impact_duration: "25 jours (2026-03-20 07:53 → 2026-04-17 13:14 UTC)"
affected_systems:
  - paybox-callback-controller
  - paybox-callback-gate
  - mark_order_paid_atomic (RPC Supabase)
  - cloudflare-waf
  - __xtr_order (table)
  - ic_postback (table)
root_cause: "3 bugs cumulés — Cloudflare WAF bloquait IPN Paybox, RPC type error BOOLEAN>INTEGER, gate rejetait errorCode≠00000"
related_rules:
  - "[[03-rules/technical/payments-tunnel-integrity]]"
related_adr:
  - "[[02-decisions/adr/ADR-XXX-paybox-pipeline-stability]] (à créer)"
owner: "@automecanik.seo@gmail.com"
reviewed_by: "Claude Code Opus 4.7"
tags:
  - incident/sev1
  - domain/payments
  - tech/paybox
  - tech/cloudflare
  - tech/supabase
  - post-mortem
  - resolved
---

# Incident : Paybox payment tunnel — 25 jours commandes non-confirmées

> [!danger] Résumé
> Du **2026-03-20 07:53 UTC** au **2026-04-17 13:14 UTC** (25 jours), **100% des callbacks Paybox IPN ne marquaient plus les commandes comme payées** en DB à cause de **3 bugs cumulés** indépendants. Détecté à J+25 via monitoring externe. **559 € GMV non-récupérée** acceptée comme coût.

## Timeline

| Heure UTC | Événement |
|---|---|
| 2026-03-20 07:53 | Dernière commande payée avec succès (ORD-1773993165624-167, 148.30 €) |
| 2026-03-20 ~08-10 | **CLIFF** — tunnel se casse (Bug #1 CF WAF activé à une heure inconnue) |
| 2026-03-20 09:59 | Premier cliff-victim (ORD-1774000750441-805, 34.87 €, Lucas Rabeau) |
| 2026-03-20 22:11 CET | Commit `c91d804e` déployé (gate default → strict) |
| 2026-03-20 22:52 UTC | Commit `c1265fbb` → **Bug #3 RPC introduite** (type error systématique) |
| 2026-03-21 05:28 CET | Commit `d1aa8e09` "unblock deploy RPC bypass" (équipe panique) |
| 2026-04-14 14:32 | **DÉTECTION** via monitoring externe tiers (J+25) |
| 2026-04-14 14:50 | Investigation démarrée (Claude Code) |
| 2026-04-14 16:20 | **Bug #1 CF fixé** via règle #1 skip `/api/paybox/*` |
| 2026-04-14 16:26 | Probe tech E2E OK (gate_log id=1) |
| 2026-04-14 17:42 | 1er paiement test réel (14.37 €) → **Bug #3 révélé** (`ord_is_pay='0'`) |
| 2026-04-14 19:30 | **Bug #3 RPC fixé** via migration MCP (BOOLEAN → INTEGER) |
| 2026-04-17 13:14 | **E2E VALIDÉ** sans intervention (ORD-1776431567939-431, 13.82 €, 91 sec) |
| 2026-04-17 15:22 | Commit main `b52493bb` (incident fix + migration + doc + PREV-1 script) |
| 2026-04-17 16:21 | Commit main `44acbcc2` (CI unblock protobufjs CVE) |
| 2026-04-17 17:45 | Commit main `f4c50fe2` (PREV-1 v2 Gmail OAuth2) |
| 2026-04-18 12:15 | Commit main `f1da70fd` (M1 sanitize logs, 10 tests) |
| 2026-04-18 12:35 | Commit main `a92bc6c6` (M2 Bug #2 gate fix, 13 tests) |
| 2026-04-18 13:12 | **PREV-1 cron LIVE** sur prod */15min |
| 2026-04-18 13:37 | **PREV-4 Phase 1 LIVE** — Caddy logs rétention 30j |
| 2026-04-18 13:40 | 🏁 **INCIDENT CLOS** |

## Impact

- **Utilisateurs affectés** : 4 clients distincts (lucas.rabeau44000@, calassouadrien@, walid.berguiga71@, goderonlucas@) + 2 self-tests + 1 spam probable
- **Transactions perdues** : 8 commandes `ord_is_pay='0'` (dont 5 "vraies")
- **Durée d'indisponibilité** : 25 jours de callback processing cassé
- **Impact business** : **~559 € GMV brute non-récupérée** (accepté comme coût)
- **Détection gap** : 25 jours (objectif post-PREV-1 : <2h)

## Root Cause — 3 bugs cumulés

> [!bug] Bug #1 — Cloudflare WAF bloquait les POST IPN Paybox
> Règle custom #5 `"Challenge hors zones cibles"` + règle #4 `"Block US Datacenter ASNs"` filtraient tout trafic non-humain qui n'était pas dans la liste "Bots connus" Cloudflare. Les serveurs IPN Verifone ne sont pas un "known bot" CF → Managed Challenge JS → Paybox ne sait pas exécuter JS → requête droppée avant d'atteindre Caddy.

> [!bug] Bug #2 — Gate rejetait tout `errorCode ≠ '00000'` en 403
> [[backend/src/modules/payments/services/paybox-callback-gate.service|paybox-callback-gate.service.ts]] ligne 210-215 incluait `errorCode.ok` dans `allCriticalChecksOk`. Confusion entre *check sécurité* (anti-spoofing/replay/tampering) et *info business* (statut bancaire). Les refus bancaires signés valides par Paybox étaient rejetés.

> [!bug] Bug #3 — RPC `mark_order_paid_atomic` type error systématique
> `v_updated BOOLEAN` + `GET DIAGNOSTICS ROW_COUNT` (INTEGER) → `RETURN v_updated > 0` plante en `ERROR: 42883 operator does not exist: boolean > integer`. **La RPC n'a JAMAIS fonctionné** depuis commit `c1265fbb` (2026-03-20 22:52 UTC). Les 5 paiements OK Feb→Mar 20 matin utilisaient l'ANCIEN code SELECT+UPDATE direct.

## Résolution

### Bug #1 — Cloudflare WAF (hors repo)

```
Dashboard Cloudflare → Security → WAF → Custom rules → Rule #1
Action : Ignorer (Skip security)
Expression ajoutée :
  (starts_with(http.request.uri.path, "/api/paybox"))
  or (starts_with(http.request.uri.path, "/api/systempay"))
  or (starts_with(http.request.uri.path, "/api/cyberplus"))
  or (starts_with(http.request.uri.path, "/api/payments/"))
```

### Bug #2 — Gate code

```typescript
// backend/src/modules/payments/services/paybox-callback-gate.service.ts
// AVANT — errorCode inclus dans les checks critiques (bug)
result.allCriticalChecksOk =
  result.checks.signature.ok &&
  result.checks.orderExists.ok &&
  result.checks.amountMatch.ok &&
  result.checks.errorCode.ok &&   // ← bug, retiré
  result.checks.merchantId.ok;

// APRÈS — errorCode propagé au handler mais ne bloque plus le gate
result.allCriticalChecksOk =
  result.checks.signature.ok &&
  result.checks.orderExists.ok &&
  result.checks.amountMatch.ok &&
  result.checks.merchantId.ok;
```

### Bug #3 — RPC SQL

```sql
-- Migration 20260417_fix_mark_order_paid_atomic_type_error.sql
CREATE OR REPLACE FUNCTION public.mark_order_paid_atomic(p_ord_id text, p_date_pay text DEFAULT NULL)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
  v_count INTEGER;      -- ← était BOOLEAN (bug)
BEGIN
  UPDATE "___xtr_order"
  SET ord_is_pay = '1', ord_date_pay = COALESCE(p_date_pay, NOW()::TEXT), ord_ords_id = '3'
  WHERE ord_id = p_ord_id AND ord_is_pay = '0';

  GET DIAGNOSTICS v_count = ROW_COUNT;
  RETURN v_count > 0;
END;
$$;
```

## Preuves

### Commits

| SHA | Description |
|---|---|
| `b52493bb` | Initial fix — migration + incident record + PREV-1 script |
| `44acbcc2` | CI unblock (protobufjs CVE + commitlint devDeps) |
| `f4c50fe2` | PREV-1 v2 Gmail OAuth2 SMTP XOAUTH2 |
| `9561db1b` | PREV-1 doc — default ALERT_EMAIL_TO |
| `f1da70fd` | M1 sanitize logs paybox.service.ts (10 tests) |
| `a92bc6c6` | M2 Bug #2 Gate errorCode fix (13 tests) |

**Tag** : `v2026.04.17-paybox-tunnel-sev1-fix` → commit `44acbcc2`

### Validations E2E

- **2026-04-17 13:14** — ORD-1776431567939-431 (13.82 €) payé E2E en **91 sec sans intervention**
- **Email PREV-1** → `automecanik.seo@gmail.com` reçu en ~1-2 sec (2 tests)
- **Cron prod** → actif `*/15 * * * *`, log `/var/log/check-payment-tunnel.log`

### DB evidence

- Première row jamais insérée dans `__paybox_gate_log` : id=1 (probe sanity check) confirme que CF laisse passer et que le gate fonctionne
- `mark_order_paid_atomic('ORD-1776188437855-943', ...)` appelée via MCP → régularisation manuelle de la commande test du 2026-04-14

## Lessons Learned

1. **Plusieurs bugs peuvent coexister sans se trahir**. RCA initiale pointait Cloudflare (juste à 100%) mais ne suffisait pas — Bug #2 + Bug #3 cachés derrière. Seule validation **progressive** E2E a démasqué chaque couche.
2. **Pas d'observabilité historique = post-mortem aveugle**. Caddy log rotation 2-3h a empêché toute reconstitution HTTP. **PREV-4 non-négociable**.
3. **Pas d'alerte métier = détection J+25**. **PREV-1 cron 15min** est la défense la plus critique.
4. **Déploiement simultané = multi-bug**. Commits `c91d804e` + `c1265fbb` du 2026-03-20 ont introduit Bug #2 ET Bug #3 **en même nuit**. Aucun test E2E ne les a détectés.
5. **Migration SQL orpheline** : `c1265fbb` a créé la RPC via code TS `.rpc()` mais **sans fichier migration** dans `backend/supabase/migrations/`. Lint CI absent.

## Actions Correctives

### Préventions actives (déployées)

- [x] **PREV-1** — Cron 15min alerting email Gmail OAuth2 (`scripts/monitoring/check-payment-tunnel.sh`) — **Owner** : @automecanik.seo — **Deadline** : 2026-04-18 ✅ **FAIT**
- [x] **PREV-4 Phase 1** — Caddy `roll_keep 10→2000` + `roll_keep_for 720h` → rétention 30j — **Owner** : @automecanik.seo — **Deadline** : 2026-04-18 ✅ **FAIT**
- [x] **M1** — Sanitize logs `paybox.service.ts` (PII + merchant IDs) — **Owner** : @automecanik.seo — **Deadline** : 2026-04-18 ✅ **FAIT**

### Préventions planifiées (backlog)

- [ ] **PREV-2** — Canary E2E paiement en CI après chaque merge main (Playwright) — **Owner** : @tech — **Deadline** : 2026-05-15
- [ ] **PREV-4 Phase 2** — Ship Caddy logs vers Cloudflare R2 (backup off-host) — **Owner** : @tech — **Deadline** : 2026-05-15
- [ ] **ADR Paybox pipeline stability** — document gouvernance pour invariants tunnel + règle CI canary obligatoire pour tout merge touchant `backend/src/modules/payments/**` — **Owner** : @automecanik.seo — **Deadline** : 2026-04-30
- [ ] **Runbook** `.spec/runbooks/payments-tunnel-debug.md` — checklist reproductible — **Owner** : @tech — **Deadline** : 2026-04-30
- [ ] **Lint CI migration-orpheline** — détecter tout `.rpc('xxx')` sans migration correspondante — **Owner** : @tech — **Deadline** : 2026-05-30
- [ ] **Dashboard analytics refus CB** — exploiter les `ic_postback` FAILED (taux refus par code Paybox, par BIN) — **Owner** : @product — **Deadline** : 2026-06-01

## Communication

- [x] Équipe notifiée (via commits main + tag)
- [ ] Stakeholders business informés (559 € GMV → décision abandon récupération clients)
- [x] Post-mortem partagé (ce document)

## Références

- Incident précédent similaire : [[2026-02-03-paybox-orderid-format]] (0% paid since 2025, 5 bugs corrigés)
- Tech record détaillé : [[../../../app/.spec/reports/incident-2026-04-14-payments-sev1|incident-2026-04-14-payments-sev1.md]]
- Scripts monitoring : [[../../../app/scripts/monitoring/README|scripts/monitoring/README.md]]
- RPC health check : [[../../../app/backend/supabase/migrations/20260417_add_check_payment_tunnel_health_rpc|migration SQL]]

---

*Créé le: 2026-04-18*
*Dernière mise à jour: 2026-04-18 14:00 UTC*
*Status : CLOSED — tech resolved, business loss accepted*
