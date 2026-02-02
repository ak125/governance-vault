# Rules - AutoMecanik

> **Source de verite** - Regles non-negociables au 2026-01-06
> **Version**: 2.0.0 | **Status**: CANON

---

## Regles Critiques (7)

Ces regles sont **NON-NEGOCIABLES**. Toute violation est un bug critique.

---

### R1: Architecture 3-Tier

**OBLIGATOIRE** : Chaque module NestJS doit suivre Controller → Service → DataService.

```typescript
// ❌ INTERDIT
@Controller('products')
export class ProductsController {
  async getProduct() {
    await this.supabase.from('products').select(); // DB direct = NON
  }
}

// ✅ OBLIGATOIRE
@Controller('products')
export class ProductsController {
  constructor(private readonly productService: ProductService) {}

  @Get(':id')
  async getProduct(@Param('id') id: string) {
    return this.productService.findOne(id);
  }
}
```

---

### R2: Supabase SDK Direct (PAS de Prisma)

**OBLIGATOIRE** : Utiliser `@supabase/supabase-js` pour toutes les requetes DB.

```typescript
// ❌ INTERDIT
const product = await prisma.product.findUnique({ where: { id } });

// ✅ OBLIGATOIRE
const { data, error } = await this.supabase
  .from('__products')
  .select('*')
  .eq('id', id)
  .single();
```

**Tables** : Prefixe `__` (ex: `__products`, `__orders`, `__users`)

---

### R3: Sessions Redis + Passport

**OBLIGATOIRE** : Redis pour les sessions, Passport pour l'auth.

```typescript
// Configuration requise
app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  name: 'connect.sid',
  cookie: {
    httpOnly: true,
    sameSite: 'lax',
    maxAge: 30 * 24 * 60 * 60 * 1000, // 30 jours
  },
}));
```

**Cookie** : `connect.sid` (HttpOnly, SameSite: lax)

---

### R4: Validation Zod

**OBLIGATOIRE** : Valider toutes les entrees avec Zod.

```typescript
// ✅ OBLIGATOIRE - Schema Zod dans le DTO
const CreateProductSchema = z.object({
  name: z.string().min(1).max(255),
  price: z.number().positive(),
  categoryId: z.string().uuid(),
});

export class CreateProductDto extends createZodDto(CreateProductSchema) {}
```

---

### R5: Paiements HMAC

**OBLIGATOIRE** : Verifier les signatures HMAC sur tous les callbacks paiement.

| Gateway | Algorithme |
|---------|------------|
| Paybox | HMAC-SHA512 |
| SystemPay | HMAC-SHA256 |

```typescript
// ✅ OBLIGATOIRE - Verification signature
function verifyPayboxSignature(params: Record<string, string>, signature: string): boolean {
  const expectedSignature = crypto
    .createHmac('sha512', process.env.PAYBOX_HMAC_KEY)
    .update(sortedParams)
    .digest('hex')
    .toUpperCase();

  return signature === expectedSignature;
}
```

---

### R6: Git Workflow - Validation Manuelle

**OBLIGATOIRE** : Push sur `main` uniquement apres validation manuelle explicite.

```bash
# ❌ INTERDIT
git push origin main
gh pr merge  # Sans approbation

# ✅ OBLIGATOIRE
git checkout -b feature/xxx
git push origin feature/xxx
gh pr create --title "feat: xxx"
# ATTENDRE validation manuelle
# APRES approbation explicite uniquement:
gh pr merge
```

**Raison** : `main` = production automatique (GitHub Actions)

---

### R7: Tests (curl + Playwright + RTL)

**OBLIGATOIRE** : Utiliser curl, Playwright, @testing-library/react.

| Type | Outil | Usage |
|------|-------|-------|
| API | `curl` | Tests manuels endpoints |
| E2E | Playwright | Tests bout-en-bout |
| Composants | @testing-library/react | Tests unitaires React |

**INTERDIT** : Jest, Vitest

```bash
# ✅ CORRECT - Test API
curl -X GET http://localhost:3000/api/products/123 | jq

# ✅ CORRECT - Test E2E
cd frontend && npm run test:a11y
```

---

## Anti-patterns

### Ne jamais faire

| Anti-pattern | Raison |
|--------------|--------|
| DB dans Controller | Viole R1 |
| Prisma en prod | Viole R2 |
| Sessions en memoire | Viole R3 |
| Body sans validation | Viole R4 |
| Callback sans HMAC | Viole R5 |
| Push main direct | Viole R6 |
| Jest/Vitest | Viole R7 |

### Autres interdits

```typescript
// ❌ INTERDIT - Secrets dans le code
const apiKey = 'sk_live_xxxxx';

// ❌ INTERDIT - console.log en production
console.log('Debug:', data);

// ❌ INTERDIT - any partout
function processData(data: any) {}

// ❌ INTERDIT - Catch vide
try { ... } catch (e) {}
```

---

## AI-COS Governance

### Axiome Zero

```
L'IA NE CREE PAS LA VERITE.
Elle produit. Elle analyse. Elle propose.
LA VERITE EST VALIDEE PAR : Structure + Humain.
```

### Regle d'Or

```
UN AGENT QUI DOUTE DOIT BLOQUER, JAMAIS "INVENTER".
```

- Doute sur un fait → BLOCAGE
- Doute sur une source → BLOCAGE + FLAG
- Doute sur une decision → ESCALADE humain

### Truth Levels RAG

| Level | Description | Validation |
|-------|-------------|------------|
| L1 | Donnees Supabase | Automatique |
| L2 | Docs valides | Quality Officer |
| L3 | Calculs derives | Tests + Review |
| L4 | Contenu genere | Humain obligatoire |

---

## Kill Switches

| Switch | Trigger | Action |
|--------|---------|--------|
| `AI_PROD_WRITE=false` | Defaut prod | Bloque ecriture IA |
| `RAG_GATING` | Score < 0.70 | Refuse reponse |
| `NAMESPACE_GUARD` | PROD | Limite `knowledge:faq` only |

---

## Checklist Validation

Avant tout merge sur main, verifier :

- [ ] Architecture 3-tier respectee (R1)
- [ ] Supabase SDK utilise, pas Prisma (R2)
- [ ] Sessions Redis configurees (R3)
- [ ] Schemas Zod pour validation (R4)
- [ ] Signatures HMAC verifiees (R5)
- [ ] Validation manuelle obtenue (R6)
- [ ] Tests curl/Playwright/RTL (R7)

---

_Derniere mise a jour: 2026-01-06_
_Status: CANON - Source de verite_
