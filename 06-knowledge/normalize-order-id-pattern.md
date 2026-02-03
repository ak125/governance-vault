# Pattern : Normalisation d'identifiants externes

**Domaine :** Paiements, Intégrations tierces
**Date :** 2026-02-03

---

## Problème

Les systèmes externes (Paybox, SystemPay, etc.) peuvent envoyer des identifiants dans un format différent de celui stocké en base de données.

**Exemple concret :**
- Paybox envoie : `ORD-1762010061177-879`
- Base stocke : `1762010061177`

## Solution : Helper de normalisation centralisé

### Implémentation

```typescript
// utils/normalize-order-id.ts

/**
 * Normalise une référence de commande vers l'ID numérique attendu par la DB.
 *
 * @example
 *   normalizeOrderId("ORD-1762010061177-879") // → "1762010061177"
 *   normalizeOrderId("1762010061177")         // → "1762010061177"
 *   normalizeOrderId("TEST-000")              // → "TEST-000" (fallback)
 *   normalizeOrderId("")                      // → ""
 */
export function normalizeOrderId(ref: string): string {
  if (!ref) return ref;

  // ORD-1762010061177-879 => 1762010061177
  const m = ref.match(/ORD-(\d+)/);
  if (m?.[1]) return m[1];

  // Si déjà numérique, on garde
  if (/^\d+$/.test(ref)) return ref;

  // Fallback : on ne devine pas, on retourne tel quel
  return ref;
}
```

### Tests unitaires

```typescript
// utils/normalize-order-id.spec.ts
import { normalizeOrderId } from './normalize-order-id';

describe('normalizeOrderId', () => {
  describe('format ORD-xxx-yyy', () => {
    it('should extract numeric ID from ORD-1762010061177-879 format', () => {
      expect(normalizeOrderId('ORD-1762010061177-879')).toBe('1762010061177');
    });

    it('should extract numeric ID from ORD-123-456 format', () => {
      expect(normalizeOrderId('ORD-123-456')).toBe('123');
    });
  });

  describe('already numeric ID', () => {
    it('should keep numeric ID unchanged', () => {
      expect(normalizeOrderId('1762010061177')).toBe('1762010061177');
    });
  });

  describe('edge cases', () => {
    it('should return empty string for empty input', () => {
      expect(normalizeOrderId('')).toBe('');
    });

    it('should fallback for unknown formats', () => {
      expect(normalizeOrderId('TEST-000')).toBe('TEST-000');
    });
  });
});
```

## Principes de conception

### 1. Single Source of Truth

Un seul fichier définit la logique de normalisation. Tous les modules importent ce helper.

```typescript
// ✅ Correct
import { normalizeOrderId } from '../utils/normalize-order-id';
const orderId = normalizeOrderId(params.orderReference);

// ❌ Incorrect - duplication de logique
const orderId = params.orderReference.replace('ORD-', '').split('-')[0];
```

### 2. Defense-in-Depth

Normaliser à plusieurs niveaux pour se protéger des oublis :

```typescript
// Controller (première ligne de défense)
const numericOrderId = normalizeOrderId(params.orderReference);

// Service (deuxième ligne de défense)
async createPayment(data: Partial<Payment>) {
  const safeOrderId = normalizeOrderId(data.orderId || '');
  // ...
}
```

### 3. Fallback sûr

Ne jamais deviner un format inconnu. Retourner tel quel et laisser la couche suivante gérer l'erreur.

```typescript
// ✅ Correct - fallback explicite
if (/^\d+$/.test(ref)) return ref;
return ref; // Retourne tel quel si format inconnu

// ❌ Incorrect - devine un format
return ref.replace(/\D/g, ''); // Risque de corrompre des données valides
```

## Utilisation dans le projet

| Fichier | Usage |
|---------|-------|
| `paybox-callback.controller.ts` | Normalise avant `createPayment()` |
| `payment-data.service.ts` | Defense-in-depth dans `createPayment()` |
| `paybox-callback-gate.service.ts` | Normalise pour `checkOrderExists()` |

## Applicabilité

Ce pattern s'applique à tout identifiant externe :
- Références de paiement
- IDs de produits fournisseurs
- Codes de suivi transporteurs
- Références de factures
