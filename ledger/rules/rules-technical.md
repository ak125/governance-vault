# Rules - AutoMecanik

> Regles non-negociables au 2026-11-07. T2, T5, T6 et T7 corrigees par [[ADR-101-vault-decides-canon-authority|ADR-101]] d'apres l'etat de `main` du monorepo ; T6 alignee sur [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D4 par la decision de l'owner du 2026-11-03, et completee par [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]] (delta conditionnel).
> **Version**: 3.1.1 | **Status**: CANON (regle du vault, normative au sens de G1)
> Ancienne copie de `.spec/00-canon/rules.md` (monorepo, prose de reference sans autorite) ; diverge volontairement depuis ADR-101.

---

## Regles Critiques (7)

Ces regles sont **NON-NEGOCIABLES**. Toute violation est un bug critique.

---

### T1: Architecture 3-Tier

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

### T2: Supabase SDK Direct (PAS de Prisma)

**OBLIGATOIRE** : Utiliser `@supabase/supabase-js` pour toutes les requetes DB.

```typescript
// ❌ INTERDIT
const product = await prisma.product.findUnique({ where: { id } });

// ✅ OBLIGATOIRE
const { data, error } = await this.supabase
  .from('pieces')
  .select('*')
  .eq('piece_id', id)
  .single();
```

**Tables** : les noms viennent du schema genere (`packages/database-types/src/supabase-generated.types.ts`
du monorepo). Il n'y a pas de prefixe uniforme : `pieces`, `___xtr_order`, `__seo_*` coexistent.
Ne jamais inventer un nom de table : le lire dans le schema genere.

---

### T3: Sessions Redis + Passport

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

### T4: Validation Zod

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

### T5: Paiements - Signatures Verifiees

**OBLIGATOIRE:** Verifier la signature de tout retour de paiement **avant** de passer une commande a « payee ».

| Gateway | Requete sortante | Retour (callback / IPN) |
|---------|------------------|-------------------------|
| Paybox | HMAC-SHA512 | Signature RSA verifiee avec la cle publique Paybox |
| SystemPay | HMAC-SHA256 | HMAC-SHA256 recalcule, comparaison a temps constant |

```typescript
// ✅ OBLIGATOIRE - comparaison a temps constant sur des tampons de meme longueur
// (pattern de cyberplus.service.ts et payment-validation.service.ts)
const a = Buffer.from(expectedSignature);
const b = Buffer.from(receivedSignature);
return a.length === b.length && timingSafeEqual(a, b);

// ❌ INTERDIT - comparaison de signatures par === (fuite temporelle)
return signature === expectedSignature;
```

Les cles et certificats ne sont jamais ecrits dans le code ni dans la documentation.

---

### T6: Git Workflow - Validation Manuelle

**OBLIGATOIRE** : aucun push direct sur `main` ; toute modification passe par une branche et une PR, puis par la fusion decrite ci-dessous.

```bash
# ❌ INTERDIT
git push origin main
gh pr merge  # lance par l'agent hors d'un perimetre active selon ADR-123 (ADR-121 D4)

# ✅ OBLIGATOIRE
git checkout -b feature/xxx
git push origin feature/xxx
gh pr create --title "feat: xxx"
```

Decision T6 de l'owner du 2026-11-03 (alignement sur le canon actuel, ADR-121 D4), reproduite sans modification :

> Le mandat explicite couvre la préparation et la vérification de la PR dans ses limites, sans renouveler le même accord. Les contrôles et validations spécifiques applicables restent requis. L’agent remet à l’owner le numéro de PR, le SHA de tête à 40 caractères et la commande épinglée sur ce SHA ; l’owner seul exécute la fusion. Aucune approbation technique, CI verte ou autorisation générale ne permet à l’agent de fusionner ni d’activer l’auto-fusion.

**Delta du nouveau cadre ([[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]])** : les clauses
absolues « l’owner seul exécute la fusion » et « ni d’activer l’auto-fusion » s'appliquent hors d'un
perimetre explicitement adopte puis active selon ADR-123. Dans un tel perimetre, l'execution de la
fusion peut etre automatique, aux conditions d'ADR-123 D2 a D6 : decision autorisee (politique
approuvee par categorie, ou adoption humaine du contenu tracee avant la fusion pour une decision de
gouvernance), tete identifiee, controles, revues et validations specifiques applicables, protections
du depot ; une condition manquante ou un controle non concluant empeche la fusion. Le mecanisme, le
compte qui execute et l'acte qui l'arme sont ceux que fixe le perimetre active ; ni l'agent ni son
compte n'en decident. Tant qu'aucun perimetre n'est adopte puis active, la decision ci-dessus
s'applique sans exception.

_Tracabilite : en 3.0.0 (ADR-101), T6 se lisait « Push sur `main` uniquement apres validation manuelle
explicite », puis `gh pr merge` « APRES approbation explicite uniquement ». La decision du 2026-11-03
reproduite ci-dessus en est l'alignement sur ADR-121 D4 ; le delta est la redaction du nouveau cadre
preparee pour ADR-123 (correspondance : ADR-123 §T6)._

**Raison** : `main` est protegee ; un merge sur `main` redeploie le container PREPROD de CI (`ci.yml`). La PROD part d'un tag `v*` (`release-prod.yml`), decision owner.

---

### T7: Tests - Suites du Workspace

**OBLIGATOIRE:** Les tests s'ecrivent avec l'outil de leur perimetre, dans la suite de leur workspace executee en CI (`ci.yml`).

| Perimetre | Outil |
|-----------|-------|
| Backend (unitaires, integration) | Jest (`backend/`) |
| Frontend (unitaires, composants) | Vitest + @testing-library/react (`frontend/`) |
| E2E, accessibilite, visuel | Playwright |
| API (verification manuelle) | `curl` |

```bash
# ✅ Backend
cd backend && npx jest <chemin>

# ✅ Frontend
cd frontend && npx vitest run <chemin>

# ✅ API
curl -s http://localhost:3000/health
```

---

## Anti-patterns

### Ne jamais faire

| Anti-pattern | Raison |
|--------------|--------|
| DB dans Controller | Viole T1 |
| Prisma en prod | Viole T2 |
| Sessions en memoire | Viole T3 |
| Body sans validation | Viole T4 |
| Retour paiement sans verification de signature, ou comparaison par `===` | Viole T5 |
| Push main direct | Viole T6 |
| Runner de test hors du tableau T7 | Viole T7 |

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

- [ ] Architecture 3-tier respectee (T1)
- [ ] Supabase SDK utilise, pas Prisma (T2)
- [ ] Sessions Redis configurees (T3)
- [ ] Schemas Zod pour validation (T4)
- [ ] Signatures de paiement verifiees, comparaison a temps constant (T5)
- [ ] PR preparee ; fusion executee par l'owner sur la tete epinglee, ou automatiquement dans un perimetre adopte puis active selon ADR-123 (T6)
- [ ] Tests dans la suite du workspace (Jest / Vitest / Playwright) (T7)

---

_Derniere mise a jour: 2026-11-07 (T6 : decision du 2026-11-03 sur ADR-121 D4, delta ADR-123)_
_Status: CANON - Regle du vault_
