# ADR : Suppression de l'endpoint /api/paybox/callback-test

**Date :** 2026-02-03
**Statut :** Accepté
**Décideurs :** Équipe développement

---

## Contexte

L'endpoint `GET /api/paybox/callback-test` permettait de tester le flux de callback Paybox sans vérification de signature HMAC. Cet endpoint était accessible publiquement en production.

## Décision

**Supprimer complètement l'endpoint `/api/paybox/callback-test`.**

## Raisons

### Faille de sécurité critique

```typescript
// AVANT - Code vulnérable (SUPPRIMÉ)
@Get('callback-test')
async handleCallbackTest(@Query() query, @Res() res) {
  // ⚠️ AUCUNE vérification de signature HMAC
  // Permettait de forger des paiements avec n'importe quel orderId
  await this.paymentDataService.createPayment({
    orderId: query.orderId,
    status: 'completed',
    // ...
  });
}
```

### Risques identifiés

1. **Fraude au paiement** - Un attaquant pouvait marquer n'importe quelle commande comme payée
2. **Injection de données** - Pas de validation des paramètres query
3. **Surface d'attaque** - Endpoint documenté (logs, traces)

## Alternatives Considérées

| Option | Avantages | Inconvénients |
|--------|-----------|---------------|
| ✅ **Supprimer** | Sécurité maximale | Pas de test facile |
| ❌ Protéger par IP | Garde fonctionnalité | Complexité, risque bypass |
| ❌ Ajouter auth admin | Garde fonctionnalité | Token dans URL = risque |
| ❌ Environnement dev only | Garde fonctionnalité | Risque de déploiement accidentel |

## Conséquences

### Positives

- Surface d'attaque réduite
- Aucune possibilité de forger des paiements
- Code plus simple et maintenable

### Négatives

- Tests manuels plus complexes (nécessite signature valide)
- Doit utiliser sandbox Paybox pour tests

## Implémentation

**~120 lignes supprimées** dans `paybox-callback.controller.ts`

```typescript
// APRÈS - Commentaire explicatif
// NOTE: L'endpoint /callback-test a été supprimé pour raisons de sécurité.
// Il permettait de créer des paiements sans vérification de signature HMAC.
// Pour tester, utiliser l'environnement sandbox Paybox avec des signatures valides.
```

## Vérification

```bash
# L'endpoint doit retourner 404
curl http://localhost:3000/api/paybox/callback-test
# Attendu: Cannot GET /api/paybox/callback-test
```

## Références

- Commit : `f07b3856`
- OWASP : [Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- Post-mortem associé : `01-incidents/2026-02-03-paybox-orderid-format.md`
