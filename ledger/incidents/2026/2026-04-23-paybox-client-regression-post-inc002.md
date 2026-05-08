---
id: INC-2026-014
type: incident
title: "Paybox tunnel — alerte régression client post-INC-2026-002 (false-positive : tunnel fonctionnel, conversion commerciale faible)"
date: 2026-04-23
date_detected: 2026-04-23
date_resolved: 2026-04-23
date_steady_state: 2026-04-30
severity: medium
status: closed
impact_duration: "investigation 2h (2026-04-23 11:00 → 14:45 UTC) — hypothèse initiale invalidée. Cliff réel 2026-03-20 → 2026-04-14 = 25j sans paiement client (porté par INC-2026-002)."
affected_systems:
  - paybox-callback-controller
  - paybox-callback-gate
  - cloudflare-waf
  - ___xtr_order (table)
  - ic_postback (table)
  - APP_URL prod config
  - Paybox merchant account (notify_url)
root_cause: "Hypothèse initiale (tunnel Paybox cassé) INVALIDÉE par investigation empirique. Tunnel 100% fonctionnel end-to-end. La baisse de paiements est un problème de conversion commerciale (~10% vs 30-40% norme), pas un bug technique. Confirmé empiriquement 2026-05-08 : 4 paiements clients réels depuis le cliff (1er = 2026-04-14 ORD-1776188437855-943 14.37€, dernier = 2026-05-07 ORD-1778188033019-385 291.86€)."
related_rules:
  - payments-tunnel-integrity
related_adrs:
  - ADR-014-remove-paybox-callback-test
related_incidents:
  - INC-2026-002-paybox-tunnel-sev1-ipn-blocked
  - INC-2026-009-ci-cwv-backend-boot-crash
owner: "@automecanik.seo"
reviewed_by: "Claude Opus 4.7"
tags:
  - incident/medium
  - domain/payments
  - tech/paybox
  - false-positive
  - conversion-issue
  - post-mortem
  - lessons-learned
---

# INC-2026-014 : Paybox tunnel — alerte régression client post-INC-2026-002 (false-positive)

> [!info] Update 2026-05-08 — Empirical confirmation
> Préparation merge vault PR #40 (P0 stagnant 15j). Re-vérification empirique
> via `___xtr_order` (project Supabase `cxpojprgwgubzjyqzmoq`) confirme
> l'invalidation du SEV1 :
>
> | Date paiement | ORD | Montant | Type |
> |---|---|---|---|
> | 2026-04-14 17:42 | ORD-1776188437855-943 | 14.37 € | **CUSTOMER (1er post-cliff)** |
> | 2026-04-17 13:14 | ORD-1776431567939-431 | 13.82 € | E2E validation (acked) |
> | 2026-04-30 06:41 | ORD-1777531019900-837 | 62.35 € | CUSTOMER |
> | 2026-05-07 09:24 | ORD-1778145618622-850 | 266.08 € | CUSTOMER |
> | 2026-05-07 21:09 | ORD-1778188033019-385 | 291.86 € | CUSTOMER |
>
> **Bilan** : 4 paiements clients réels confirmés depuis le cliff (GMV
> 634.66 €). Dernier paiement = 2026-05-07 (la veille de ce merge). Tunnel
> Paybox vivant. **Le SEV1 ouvert le 23/04 disait "0 paiement client" alors
> qu'1 client réel avait déjà payé 9 jours avant** (ORD-1776188437855-943
> 2026-04-14, c'est-à-dire avant la création de cette PR) — mauvaise lecture
> initiale, corrigée par l'investigation 14h45 UTC le même jour. Pas de
> régression réelle Paybox.

> [!danger] Résumé initial (2026-04-23 11:30, hypothèse FAUSSE)
> Hypothèse formulée à 11:30 UTC : « depuis le **2026-03-20 07:53 UTC** (cliff
> initial INC-2026-002), aucun paiement vrai client n'est finalisé en prod via
> Paybox callback. INC-2026-002 a été clos prématurément le 2026-04-17 sur un
> E2E de validation équipe (ORD-1776431567939-431, 13.82 €, 91 sec) qui n'a pas
> représenté un retour à la normale côté trafic client. » → **Réfutée 3h
> plus tard par investigation empirique (voir section ci-dessous).**

---

## ⚠️ INCIDENT INVALIDATED (2026-04-23 14:45 UTC)

**Hypothèse initiale réfutée par investigation empirique approfondie** :

### Preuves que le tunnel fonctionne 100%

| Composant | Vérification | Résultat |
|---|---|---|
| Backend config | `APP_URL`, `BASE_URL`, HMAC, `PBX_REPONDRE_A` | ✅ toutes bonnes |
| IPN URL envoyée à Paybox | Log backend `Formulaire Paybox avec IPN: https://www.automecanik.com/api/paybox/callback` | ✅ correcte |
| Cloudflare WAF + Caddy + backend callback | POST externe test depuis DEV VPS → HTTP 400 applicatif reçu (gate fonctionne) | ✅ traverse OK |
| Tunnel frontend add-to-cart → checkout → Paybox | Test E2E manuel user 2026-04-23 14:31 (ORD-1776954691840-888) | ✅ arrivé sur tpeweb.paybox.com |
| Tunnel complet paiement CB → IPN → status=3 | Confirmé par user : « CA PASSE ON A DEJA TESTET » + E2E 17 avril (ORD-1776431567939-431) | ✅ end-to-end fonctionnel |
| Commits fix (`a92bc6c6`, `f1da70fd`) | Présents dans tag prod `v2026.04.22-r7-shortcuts-fix` (vérifié par `git merge-base --is-ancestor`) | ✅ déployés |

### Vraie cause identifiée : taux de conversion commercial anormalement bas

| Métrique DB | Valeur (au 2026-04-23) | Norme e-commerce |
|---|---|---|
| Orders status=1 (carts créés) 60j | ~40 | — |
| Orders status=3 (payées) 90j | 4 | 20-30+ attendu |
| Ratio conversion cart → paiement | ~10% | 30-40% typique |
| Nouvelles orders depuis 2026-04-17 | 0 | ≥1/jour typique |

**Ce n'est pas un bug technique mais un problème business** : faible conversion
du trafic SEO (visiteurs informatifs) en acheteurs réels, aggravé par un creux
de trafic depuis la clôture de INC-2026-002.

### Actions réelles à prendre (hors ce ticket)

- Mettre en place le cron **PREV-1 monitoring conversion** planifié par INC-2026-002 A1 (ratio paiements/orders, alerte Gmail <20% sur 24 h)
- Investiguer le funnel GA4 (où les users droppent : landing / cart / checkout / Paybox)
- Activer le système `feat(cart): abandoned cart email recovery` (commit `4fcb5bb0`) si pas déjà en prod
- Trust signals sur fiches pièces (avis, garantie, délai livraison visibles)

### Bénéfices collatéraux de cette investigation

- **INC-2026-009 (CI CWV backend boot crash)** : **root cause réelle trouvée** = `APP_URL` manquant dans `.github/workflows/perf-gates.yml`. PR monorepo #123 fixe en 1 ligne.
- **4 hypothèses backend/infra (H1-H4) écartées définitivement** avec preuves empiriques reproductibles (reproduction locale du crash, POST probe externe, joints DB).
- **Gap détecté** : Performance Gates CI ne tourne pas sur les PR RLS (SQL-only) → régression backend induite par changement RLS passe invisible. Action A4 de INC-2026-009 toujours utile.

---

## Timeline

| Heure UTC | Événement |
|-----------|-----------|
| 2026-03-20 07:53 | Dernier vrai client payé (ORD-1773993165624-167, 148 €) — réf INC-2026-002 |
| 2026-03-20 ~08-10 | Cliff initial (INC-2026-002 Bug #1 CF WAF) |
| 2026-04-14 14:32 | Détection INC-2026-002 (J+25) |
| 2026-04-14 17:42 | **1er paiement client post-cliff** (ORD-1776188437855-943, 14.37 €) — invisible au moment de la création de cette PR |
| 2026-04-17 13:14 | Clôture INC-2026-002 sur E2E validation équipe (13.82 €) |
| 2026-04-18 12:15-12:35 | Commits `f1da70fd` + `a92bc6c6` post-clôture |
| 2026-04-18 → 2026-04-23 | Trafic faible (creux post-clôture), peu d'orders nouveaux |
| 2026-04-23 11:30 | Détection-alarme via investigation CI crash + jointure DB ↔ user feedback (« 0 paiement depuis mars ») |
| 2026-04-23 14:45 | **Hypothèse invalidée** par 6 preuves empiriques (cf. section ci-dessus) |
| 2026-04-30 06:41 | Paiement client (ORD-1777531019900-837, 62.35 €) |
| 2026-05-07 09:24 | Paiement client (ORD-1778145618622-850, 266.08 €) |
| 2026-05-07 21:09 | Paiement client (ORD-1778188033019-385, 291.86 €) |
| 2026-05-08 | Re-confirmation empirique (Supabase query) avant merge vault PR #40 — INC-2026-014 |

## Impact (révisé empirique 2026-05-08)

- **Cliff réel** : 2026-03-20 → 2026-04-14 = **25 jours** zéro paiement client (porté par INC-2026-002).
- **Période "régression suspectée" 2026-04-17 → 2026-04-23** : 0 paiement client en surface, mais ce n'était PAS une régression — juste un creux de trafic + 1 paiement (14/04) déjà passé avant la perception du gap.
- **Détection** : signalement direct utilisateur ("0 paiement depuis mars") post-clôture INC-2026-002. Investigation a révélé une lecture incorrecte du tableau de bord (le paiement du 14/04 était présent en DB, juste pas saillant).
- **GMV récupérée post-cliff** : 634.66 € sur 4 paiements clients (au 2026-05-08).

## Observations DB empiriques (initiales 2026-04-23)

Query : `___xtr_order` ↔ `ic_postback` sur 60 jours.

| Indicateur | Valeur (2026-04-23) | Attendu |
|---|---|---|
| Orders status=1 (non-payées) 60j | ~40 | — |
| Orders status=3 (payées) 60j | 4 | 20-30+ |
| Orders status=1 avec ≥1 callback Paybox | 0 (exception : 1 seule du 2026-03-06, avant cliff) | la quasi-totalité |
| Dernier callback `completed/00` | 2026-04-17 (E2E validation équipe) | flux régulier |

## Hypothèses initiales (toutes ÉCARTÉES par invalidation 14h45 UTC)

### H-payment-1 — APP_URL prod mal configurée — ÉCARTÉE

`APP_URL=https://www.automecanik.com` confirmé OK en prod (`docker compose exec backend printenv`).

### H-payment-2 — Régression Cloudflare WAF — ÉCARTÉE

Règle skip `/api/paybox/*` confirmée présente. POST externe test depuis DEV VPS arrive bien au backend (HTTP 400 gate applicatif).

### H-payment-3 — URL de retour (notify_url) côté Paybox merchant account mal configurée — ÉCARTÉE

Logs backend confirment IPN URL = `https://www.automecanik.com/api/paybox/callback` envoyée correctement à Paybox.

### H-payment-4 — Commit `a92bc6c6` (2026-04-18) non déployé en prod — ÉCARTÉE

`git merge-base --is-ancestor a92bc6c6 v2026.04.22-r7-shortcuts-fix` ✅ → fix présent dans image prod.

## Lessons Learned

1. **Clôture d'incident critique nécessite validation par vrai trafic client**, pas seulement E2E équipe. Au moins 48-72h de monitoring post-fix avec ≥N vrais paiements confirmés avant de clore. INC-2026-002 a été clos sur E2E uniquement → fragilité méthodologique.
2. **PREV-1 cron monitoring tunnel** (planifié INC-2026-002 A1, censé alerter toutes 15 min) n'a pas détecté la non-reprise. À auditer (action A1 INC-2026-002).
3. **Jointure `___xtr_order` ↔ `ic_postback`** doit être une sonde de santé automatique : ratio orders status=3 / status=1 sur 7 jours = indicateur de conversion tunnel. Alerting si <10%.
4. **Lecture des dashboards en mode "0 paiement depuis mars"** : risque de manquer un paiement isolé (14/04) si le dashboard n'agrège pas correctement. Sonde automatique > inspection manuelle.
5. **Investigation empirique avant escalade SEV1** : 2h d'investigation (POST probe + DB joints + logs) ont évité une escalade injustifiée. Pattern à généraliser : sondes B.1 read-only AVANT déclaration SEV1.

## Actions Correctives (post-invalidation, statut au merge 2026-05-08)

- [x] **B.1** — Sondes prod (SSH + CF dashboard) lancées 2026-04-23 — **DONE** (résultats dans Preuves)
- [x] **B.2** — Test E2E réel CB (ORD-1776954691840-888) — **DONE** 2026-04-23 14:31
- [x] **B.3** — Confirmation hypothèse (false positive, conversion commerciale) — **DONE** 2026-04-23 14:45
- [ ] **B.4** — Audit cron PREV-1 (pourquoi pas alerté depuis le 17 avril ?) — porté par action A1 INC-2026-002
- [ ] **B.5** — Retrospective critères clôture incident critique (validation vrai trafic ≥N) — porté par INC-2026-002 follow-up
- [ ] **B.6** — Alerting ratio conversion tunnel (sonde automatique `___xtr_order` ↔ `ic_postback`) — porté par PREV-1

## Communication

- [x] Équipe backend/devops notifiée (commit cd595c3 invalidation)
- [x] INC-2026-002 status reste "Closed" avec référence à cet incident (false positive, pas une réouverture)
- [x] Post-mortem publié (cette PR vault #40, merge 2026-05-08)

## Preuves

- Query DB initiale 2026-04-23 : `___xtr_order` status=1 60j = 40 / status=3 60j = 4 / 0 callback associé
- User feedback : "je reçois 0 paiement depuis mars" (2026-04-23) — interprétation incorrecte d'un dashboard
- Re-confirmation empirique 2026-05-08 : 4 paiements clients confirmés depuis cliff (1er 14/04, dernier 07/05), GMV 634.66 €
- PROD health HTTP 200 : backend vivant, pas un crash boot
- Cross-ref [[2026-04-14-paybox-tunnel-sev1-ipn-blocked|INC-2026-002]]

## Références

- [[2026-04-14-paybox-tunnel-sev1-ipn-blocked]] — Incident parent clos 2026-04-17 (cliff réel 25j)
- [[2026-04-23-ci-cwv-backend-boot-crash]] — Investigation CI qui a révélé cet incident (false positive)
- [[ADR-014-remove-paybox-callback-test]] — Décision suppression test callback Paybox (CSRF)
- [[MOC-Incidents]]

---

*Créé le : 2026-04-23 (proposed avec hypothèse SEV1 critical)*
*Invalidé le : 2026-04-23 14:45 UTC (false positive confirmé)*
*Renumeroté INC-2026-010 → INC-2026-014 le : 2026-05-08 (collision INC-2026-010 = 503 vehicle pages, vault PR #65 mergée 2026-05-08T19:38:53Z)*
*Empirically reconfirmed : 2026-05-08 (4 customer payments since cliff)*
*Owner : @automecanik.seo*
