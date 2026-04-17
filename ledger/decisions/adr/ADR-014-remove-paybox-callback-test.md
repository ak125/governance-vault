---
id: ADR-014
title: Suppression de l'endpoint /api/paybox/callback-test
status: accepted
date: 2026-02-03
decision_makers: [Equipe developpement]
version: 1.0.0
supersedes: null
related_rules: [T5]
related_incidents: [2026-02-03-paybox-orderid-format]
owasp: "A01:2021 - Broken Access Control"
promoted_from: "DEC-004 (legacy)"
---

# ADR-014: Suppression de l'endpoint /api/paybox/callback-test

## Contexte

L'endpoint `GET /api/paybox/callback-test` permettait de tester le flux de callback Paybox **sans vérification de signature HMAC**. Cet endpoint était accessible publiquement en production.

**Problème identifié** :
- Un attaquant pouvait forger un paiement en appelant l'endpoint avec n'importe quel `orderId`
- Aucune validation des paramètres query
- Surface d'attaque exposée (endpoint documenté dans logs et traces)

Cette vulnérabilité viole directement la règle technique [[rules-technical]] **T5** (Paiements HMAC) qui impose la vérification HMAC-SHA512 sur tous les callbacks Paybox.

## Décision

**Supprimer complètement l'endpoint `/api/paybox/callback-test`.**

Aucun mécanisme de contournement n'est autorisé : les tests d'intégration doivent désormais passer par l'environnement **sandbox Paybox** avec signatures HMAC valides.

## Options Considérées

### Option A : Supprimer l'endpoint (retenue)

**Description** : Retrait complet du controller et de toutes ses routes. Tests via sandbox Paybox uniquement.

**Avantages** :
- Sécurité maximale (élimination de la surface d'attaque)
- Aucune ambiguïté sur le flux production
- Code plus simple et maintenable

**Inconvénients** :
- Tests manuels plus complexes (signature HMAC requise)
- Nécessite accès sandbox Paybox

### Option B : Protection par IP allowlist

**Description** : Conserver l'endpoint mais restreindre l'accès aux IPs internes.

**Avantages** : Garde la fonctionnalité de test.

**Inconvénients** :
- Complexité accrue (gestion allowlist)
- Risque de bypass (IP spoofing, proxies mal configurés)
- L'endpoint reste présent dans le code de production

### Option C : Authentification admin (token dans URL)

**Description** : Ajouter un token admin passé en query string.

**Avantages** : Garde la fonctionnalité avec une barrière d'authentification.

**Inconvénients** :
- **Token dans l'URL = risque majeur** (logs, historique navigateur, referers)
- Viole les bonnes pratiques OWASP A07 (Identification and Authentication Failures)

### Option D : Flag environnement (dev only)

**Description** : Activer l'endpoint uniquement si `NODE_ENV=development`.

**Avantages** : Garde la fonctionnalité en dev.

**Inconvénients** :
- Risque de déploiement accidentel (`NODE_ENV` mal configurée)
- Violation [[ADR-001-environment-separation]] (Environment Separation) : tout module DEV-only doit être explicitement documenté et barré par ESLint + .dockerignore, pas par une simple variable d'environnement

## Justification

**Critère décisif** : T5 (Paiements HMAC) est une **règle non-négociable** du canon. Un endpoint qui bypass HMAC en production est une violation structurelle, pas un problème de configuration.

Les options B/C/D maintiennent un code vulnérable "gardé" par des mécanismes contournables. Seule l'option A élimine définitivement la vulnérabilité. Le coût (tests via sandbox) est acceptable face au gain (suppression d'un vecteur de fraude au paiement).

## Conséquences

### Positives

- Surface d'attaque réduite de manière permanente
- Impossible de forger des paiements via cet endpoint
- Code de `paybox-callback.controller.ts` simplifié (~120 lignes supprimées)
- Alignement strict avec T5 et [[ADR-003-rpc-governance]] (RPC Governance)

### Négatives

- Tests manuels plus complexes (signature HMAC valide requise)
- Dépendance à la disponibilité de la sandbox Paybox pour les tests d'intégration

### Neutres

- Les équipes doivent documenter le workflow de test sandbox dans le runbook Paybox

## Critères de Succès

- [x] Endpoint retourne 404 en production (`curl http://api.../paybox/callback-test`)
- [x] ~120 lignes supprimées dans `paybox-callback.controller.ts`
- [x] Aucun test automatisé ne dépend de l'endpoint supprimé
- [ ] Runbook "test sandbox Paybox" créé et référencé

## Implémentation

**Fichier impacté** : `backend/src/payments/paybox-callback.controller.ts`

```typescript
// AVANT - Code vulnérable (SUPPRIMÉ)
@Get('callback-test')
async handleCallbackTest(@Query() query, @Res() res) {
  // ⚠️ AUCUNE vérification de signature HMAC
  await this.paymentDataService.createPayment({
    orderId: query.orderId,
    status: 'completed',
  });
}

// APRÈS - Commentaire explicatif conservé
// NOTE: L'endpoint /callback-test a été supprimé pour raisons de sécurité (ADR-014).
// Pour tester, utiliser l'environnement sandbox Paybox avec signatures HMAC valides.
```

**Vérification post-déploiement** :

```bash
# L'endpoint doit retourner 404
curl http://localhost:3000/api/paybox/callback-test
# Attendu: Cannot GET /api/paybox/callback-test
```

## Revue Planifiée

**Date** : 2026-08-01 (6 mois post-déploiement)
**Critères de revue** : cette ADR reste en vigueur tant que T5 (HMAC obligatoire) est la politique de paiement. Toute exception nécessite un nouvel ADR superseding celui-ci.

## Références

- **Commit** : `f07b3856`
- **OWASP** : [A01:2021 - Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- **Post-mortem associé** : [[2026-02-03-paybox-orderid-format]]
- **Règle technique** : [[rules-technical]] §T5
- **ADR liée** : [[ADR-001-environment-separation]], [[ADR-003-rpc-governance]]

---

*Proposé le* : 2026-02-03
*Accepté le* : 2026-02-03
*Promoted from DEC-004 (legacy)* : 2026-04-17
