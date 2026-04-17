# AI Skill Anti-Patterns

> Patterns interdits dans le système AI-COS. À éviter absolument.

---

## AP-01: Direct Skill Execution

**Pattern interdit**: Exécuter un skill directement sans passer par le JobManager.

```typescript
// ❌ WRONG: Direct execution without envelope
await skillRegistry.execute('seo_audit', { urls: ['...'] });

// ✅ CORRECT: Always use JobManager with envelope
await jobManager.enqueue(createJobEnvelope({
  intent: JobIntent.SEO_AUDIT,
  scope: { entityType: 'page', entityIds: ['...'] },
  idempotencyKey: generateKey(),
}));
```

**Pourquoi**: Pas de tracing, pas d'idempotence, pas de retry, pas d'audit.

---

## AP-02: Database Access in Trigger

**Pattern interdit**: Accéder à la base de données dans un trigger.

```typescript
// ❌ WRONG: DB access in trigger
triggers.on('product.updated', async (event) => {
  const relatedProducts = await db.query('SELECT...'); // NO!
  await jobManager.enqueue({ scope: { entityIds: relatedProducts } });
});

// ✅ CORRECT: Delegate scope calculation
triggers.on('product.updated', async (event) => {
  await jobManager.enqueue({
    intent: JobIntent.PRODUCT_SYNC,
    scope: scopeCalculator.fromEvent(event), // Delegated
  });
});
```

**Pourquoi**: Les triggers doivent être légers et rapides. La logique complexe appartient au ScopeCalculator ou au skill.

---

## AP-03: Missing Idempotency Key

**Pattern interdit**: Enqueue un job sans clé d'idempotence.

```typescript
// ❌ WRONG: No idempotency key
await jobManager.enqueue({
  intent: JobIntent.RAG_REINDEX,
  scope: { entityType: 'all' },
  // Missing idempotencyKey!
});

// ✅ CORRECT: Always include idempotency key
await jobManager.enqueue({
  ...envelope,
  idempotencyKey: `${envelope.intent}:${hash(envelope.scope)}:${dateKey}`,
});
```

**Pourquoi**: Sans idempotence, un job peut être exécuté plusieurs fois, causant des effets de bord.

---

## AP-04: Unbounded Scope

**Pattern interdit**: Scope sans limite qui peut traiter des millions d'items.

```typescript
// ❌ WRONG: Unbounded scope
scope: { entityType: 'all' } // Will process ALL items!

// ✅ CORRECT: Always bound scope
scope: {
  entityType: 'page',
  filters: { updatedSince: lastRunTime },
  limit: 1000, // Always bounded
}
```

**Pourquoi**: Un scope non borné peut causer des timeouts, des OOM, ou des coûts excessifs.

---

## AP-05: Any Type in Skill Handler

**Pattern interdit**: Utiliser `any` pour les paramètres de skill.

```typescript
// ❌ WRONG: Any type
async function runSkill(name: string, params: any) {
  return this.skills[name].execute(params);
}

// ✅ CORRECT: Typed with Zod validation
async function runSkill(name: string, input: SkillInput) {
  const skill = this.registry.get(name);
  skill.manifest.inputSchema.parse(input.params); // Validate
  return skill.handler(input);
}
```

**Pourquoi**: `any` bypasse la validation et peut causer des erreurs runtime difficiles à debugger.

---

## AP-06: Direct DB in Business Logic

**Pattern interdit**: Accès direct à Supabase dans la logique métier du skill.

```typescript
// ❌ WRONG: Direct DB access in skill logic
async function diagnose() {
  const result = await this.supabase.from('kg_nodes')
    .select('*')
    .eq('type', 'symptom');
  // Business logic with result...
}

// ✅ CORRECT: Use DataService layer
async function diagnose() {
  const symptoms = await this.kgDataService.getSymptoms();
  // Business logic with symptoms...
}
```

**Pourquoi**: Couplage fort à la DB, difficile à tester, pas de caching possible.

---

## AP-07: Ignoring Budget Constraints

**Pattern interdit**: Ignorer les contraintes de budget dans l'exécution.

```typescript
// ❌ WRONG: Ignore budget
async function executeSkill(state: GraphState) {
  // Process without checking budget
  const result = await processAll(state.input);
  return result;
}

// ✅ CORRECT: Check and respect budget
async function executeSkill(state: GraphState) {
  if (state.budget.tokensRemaining <= 0) {
    return { ...state, error: 'Budget exhausted' };
  }

  const result = await processWithLimit(
    state.input,
    state.budget.tokensRemaining
  );

  return {
    ...state,
    budget: {
      ...state.budget,
      tokensUsed: state.budget.tokensUsed + result.tokensUsed,
      tokensRemaining: state.budget.tokensRemaining - result.tokensUsed,
    },
  };
}
```

**Pourquoi**: Sans contrôle de budget, les coûts peuvent exploser.

---

## AP-08: Generating Without RAG Context

**Pattern interdit**: Générer du contenu sans contexte RAG (risque d'hallucination).

```typescript
// ❌ WRONG: Generate without RAG
async function generateContent(topic: string) {
  return await llm.invoke(`Write about ${topic}`);
}

// ✅ CORRECT: Always use RAG context
async function generateContent(topic: string, ragContext: RagContext) {
  if (ragContext.documents.length === 0) {
    throw new Error('Cannot generate without sources - refusing to hallucinate');
  }

  const sources = ragContext.documents.map(d => d.content).join('\n');
  return await llm.invoke(`Based on these sources:\n${sources}\n\nWrite about ${topic}`);
}
```

**Pourquoi**: Sans RAG, le LLM peut halluciner des informations incorrectes.

---

## AP-09: Circular Module Dependencies

**Pattern interdit**: Dépendances circulaires entre modules.

```typescript
// ❌ WRONG: Circular dependency hack
@Module({
  imports: [forwardRef(() => CatalogModule)],
})
export class VehiclesModule {}

// ✅ CORRECT: Extract shared types to contracts package
// packages/contracts/src/vehicle.ts
export interface VehicleRef { id: string; name: string; }

// Both modules import from contracts
import { VehicleRef } from '@repo/contracts';
```

**Pourquoi**: ForwardRef est un hack qui rend le code difficile à tester et à comprendre.

---

## AP-10: God Service

**Pattern interdit**: Services avec plus de 500 lignes ou 10+ méthodes.

```typescript
// ❌ WRONG: God service (2000+ lines)
export class VehiclesService {
  // 50+ methods covering everything
}

// ✅ CORRECT: Split by responsibility
export class VehicleLookupService { /* lookup logic */ }
export class VehicleCompatibilityService { /* compatibility logic */ }
export class VehicleCacheService { /* caching logic */ }
```

**Pourquoi**: Les god services sont untestables, difficiles à maintenir, et violent SRP.

---

## Checklist de Revue

Avant de merger un PR touchant au système AI:

- [ ] Pas d'exécution directe de skill (AP-01)
- [ ] Pas d'accès DB dans les triggers (AP-02)
- [ ] Clé d'idempotence présente (AP-03)
- [ ] Scope borné avec limit (AP-04)
- [ ] Pas de type `any` (AP-05)
- [ ] DataService pour l'accès DB (AP-06)
- [ ] Budget vérifié avant exécution (AP-07)
- [ ] Contexte RAG pour la génération (AP-08)
- [ ] Pas de dépendances circulaires (AP-09)
- [ ] Services < 500 lignes (AP-10)

---

## Voir aussi

- [[06-minilo-weaver]] - Patterns corrects pour MiniLo
- [[02-ai-cos-contracts]] - Contrats typés
- [[ADR-006-ai-orchestrator-architecture]] - Architecture cible

---

_Créé: 2026-02-03 | Source: Architecture Report Section 8.4_
