# Index : Correctifs Paiement Février 2026

**Date :** 2026-02-03
**Commit :** `f07b3856`

---

## Artefacts liés

| Type | Fichier | Description |
|------|---------|-------------|
| 🚨 Incident | [ledger/incidents/2026/2026-02-03-paybox-orderid-format.md](../../ledger/incidents/2026/2026-02-03-paybox-orderid-format.md) | Post-mortem bug orderId |
| 📋 Décision | [ledger/decisions/adr/ADR-014-remove-paybox-callback-test.md](../../ledger/decisions/adr/ADR-014-remove-paybox-callback-test.md) | ADR suppression endpoint test |
| 📚 Knowledge | [ledger/knowledge/normalize-order-id-pattern.md](../../ledger/knowledge/normalize-order-id-pattern.md) | Pattern de normalisation |

## Résumé des changements

### Bugs corrigés (P0)

1. **Format orderId** - Les commandes payées restaient marquées "impayées"
   - Cause : Format `ORD-xxx-yyy` vs `xxx` numérique
   - Fix : Helper `normalizeOrderId()` centralisé

2. **Endpoint vulnérable** - `/api/paybox/callback-test` sans auth
   - Risque : Forge de paiements frauduleux
   - Fix : Suppression complète (~120 lignes)

### Fichiers modifiés

```
backend/src/modules/payments/
├── utils/
│   ├── normalize-order-id.ts      # NOUVEAU
│   └── normalize-order-id.spec.ts # NOUVEAU
├── controllers/
│   └── paybox-callback.controller.ts # MODIFIÉ
├── repositories/
│   └── payment-data.service.ts    # MODIFIÉ
└── services/
    └── paybox-callback-gate.service.ts # MODIFIÉ
```

## Tests de validation

```bash
# Build OK
npm run build ✅

# Endpoint test supprimé
curl /api/paybox/callback-test → 404 ✅

# Callback protégé
curl /api/paybox/callback → 400 (signature requise) ✅
```

## Liens

- PR : Merge direct sur main (urgence P0)
- CI/CD : GitHub Actions self-hosted runner
- Monitoring : Logs Docker `nestjs-remix-monorepo-prod`
