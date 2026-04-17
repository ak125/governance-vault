# Post-Mortem : Bug Format OrderId Paybox

**Date incident :** 2026-02-03
**Sévérité :** P0 (Critique - Paiements)
**Durée impact :** Inconnue (bug silencieux)
**Résolution :** Même jour

---

## Résumé

Le callback Paybox envoyait des références de commande au format `ORD-1762010061177-879` alors que la base de données stockait uniquement l'ID numérique `1762010061177`. Résultat : les commandes payées restaient marquées comme "impayées" (`ord_is_pay = 0`).

## Timeline

| Heure | Événement |
|-------|-----------|
| 10:00 | Audit Cart & Checkout déclenché par l'utilisateur |
| 10:30 | Découverte du bug de format orderId dans `paybox-callback.controller.ts` |
| 10:45 | Plan de correction établi (helper centralisé) |
| 11:00 | Branche `fix/paybox-callback-orderid-format` créée |
| 11:30 | Implémentation `normalizeOrderId()` + tests |
| 12:00 | Tests passés (build OK, endpoint sécurisé) |
| 12:15 | Push sur main, déploiement CI/CD |
| 12:20 | Commit `f07b3856` en production |

## Cause Racine

```
Paybox callback envoie → orderReference: "ORD-1762010061177-879"
createPayment() cherche → .eq('ord_id', orderReference)
Base de données stocke → ord_id: "1762010061177" (numérique seul)
```

La requête `UPDATE ___xtr_order WHERE ord_id = 'ORD-1762010061177-879'` ne matchait aucune ligne.

## Impact

- **Financier :** Commandes payées non marquées comme telles
- **Opérationnel :** Confusion sur le statut des commandes
- **Client :** Potentiel double paiement ou commandes bloquées

## Correction

### Fichiers modifiés

| Fichier | Modification |
|---------|--------------|
| `utils/normalize-order-id.ts` | **NOUVEAU** - Helper centralisé |
| `utils/normalize-order-id.spec.ts` | **NOUVEAU** - Tests unitaires |
| `paybox-callback.controller.ts` | Utilise `normalizeOrderId()` |
| `payment-data.service.ts` | Defense-in-depth normalisation |
| `paybox-callback-gate.service.ts` | Cohérence avec helper |

### Code clé

```typescript
// utils/normalize-order-id.ts
export function normalizeOrderId(ref: string): string {
  if (!ref) return ref;
  const m = ref.match(/ORD-(\d+)/);
  if (m?.[1]) return m[1];
  if (/^\d+$/.test(ref)) return ref;
  return ref;
}
```

## Actions Préventives

1. ✅ Helper centralisé (single source of truth)
2. ✅ Defense-in-depth dans `createPayment()`
3. ✅ Tests unitaires avec cas limites
4. ⏳ Monitoring des callbacks avec format non-standard

## Leçons Apprises

1. **Toujours valider le format des données entrantes** - Ne jamais assumer que le format callback = format DB
2. **Defense-in-depth** - Normaliser à plusieurs niveaux (controller + service)
3. **Tests exhaustifs** - Couvrir tous les formats possibles (ORD-xxx-yyy, numérique seul, etc.)

## Références

- Commit fix : `f07b3856`
- Branche : `fix/paybox-callback-orderid-format`
- PR : Merge direct sur main (urgence P0)
