---
id: SPEC-002
title: "Validator Engine - Decision Card Validation"
status: draft
date: 2026-02-02
author: "@claude"
category: security
related: ["DEC-001"]
---

# SPEC-002: Validator Engine

> Service déterministe PROD/FACTORY pour valider les Decision Cards avant exécution.

---

## 1. Rôle et Positionnement

### 1.1 Ce que c'est

Le Validator Engine est un **service déterministe** (pas un agent LLM) qui :
- Prend une Decision Card en entrée
- Retourne un verdict : `APPROVE | REJECT | NEED_HUMAN`
- Fournit une liste de gates passées/ratées
- Calcule un risk score par règles (pas par LLM)
- Génère un plan de tests requis (smoke, diff, dry-run, etc.)

### 1.2 Positionnement Architectural

```
┌─────────────────────────────────────────────────────────────┐
│                    PROD / FACTORY                           │
├─────────────────────────────────────────────────────────────┤
│  Vit proche de l'Action API                                 │
│                                                             │
│  Dépendances AUTORISÉES:                                    │
│  ✅ Read-only: métriques, états (last deploy, health)       │
│  ✅ Write: audit log + idempotency store                    │
│                                                             │
│  Dépendances INTERDITES:                                    │
│  ❌ Aucun accès DB business                                 │
│  ❌ Aucun accès tables métier (sauf read-only contrôle)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline de Validation (10 Gates)

**Ordre strict - Fail-closed par défaut**

| # | Gate | Description | Fail Action |
|---|------|-------------|-------------|
| 1 | **Parse + Schema** | Zod strict, rejet si champ inconnu | REJECT |
| 2 | **Canonicalization** | Trier clés, normaliser types → `decision_hash` | REJECT |
| 3 | **Signature Check** | HMAC/mTLS + clé connue | REJECT |
| 4 | **Expiry/Nonce/Replay** | Anti re-submit | REJECT |
| 5 | **Capability Check** | Scope token + action whitelist | REJECT |
| 6 | **Param Bounds** | max_files, mode, env, etc. | REJECT |
| 7 | **Risk Policy** | D0/D1/D2 + blast radius + heure + état prod | REJECT/NEED_HUMAN |
| 8 | **Test Plan Requirement** | Si action critique → tests obligatoires | REJECT |
| 9 | **Approval Requirement** | Validator + éventuellement 2-man rule | NEED_HUMAN |
| 10 | **Emit Verdict + Audit** | Append-only log | - |

### Règle Fail-Closed

```
⚠️ Si un composant est down (audit store, idempotency store) → REJECT
```

---

## 3. Détail des Gates

### Gate 1: Parse + Schema Strict

```typescript
import { z } from 'zod';

const DecisionCardSchema = z.object({
  id: z.string().uuid(),
  action: z.enum(['DEPLOY', 'MIGRATE', 'SCRIPT_EXEC', 'CONFIG_UPDATE']),
  params: z.record(z.unknown()),
  requester: z.string(),
  timestamp: z.string().datetime(),
  signature: z.string(),
  nonce: z.string().uuid(),
  expires_at: z.string().datetime(),
}).strict(); // ⚠️ Rejette champs inconnus
```

### Gate 2: Canonicalization → Hash

```typescript
function canonicalize(card: DecisionCard): string {
  const sorted = sortKeysRecursive(card);
  return JSON.stringify(sorted);
}

function computeHash(card: DecisionCard): string {
  return crypto.createHash('sha256')
    .update(canonicalize(card))
    .digest('hex');
}
```

### Gate 3: Signature Check (HMAC)

```typescript
function verifySignature(card: DecisionCard, secret: string): boolean {
  const payload = canonicalize(omit(card, 'signature'));
  const expected = crypto.createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(card.signature, 'hex'),
    Buffer.from(expected, 'hex')
  );
}
```

### Gate 4: Expiry / Nonce / Replay

```typescript
// Redis key: validator:nonce:{nonce} avec TTL = expires_at - now
async function checkReplay(nonce: string, expiresAt: Date): Promise<boolean> {
  const key = `validator:nonce:${nonce}`;
  const exists = await redis.exists(key);
  if (exists) return false; // Replay detected

  const ttl = Math.ceil((expiresAt.getTime() - Date.now()) / 1000);
  await redis.setex(key, ttl, '1');
  return true;
}
```

### Gate 5: Capability Check

| Scope | Actions Autorisées |
|-------|-------------------|
| `ops:deploy` | DEPLOY |
| `ops:migrate` | MIGRATE |
| `ops:script` | SCRIPT_EXEC |
| `admin:config` | CONFIG_UPDATE |

### Gate 6: Param Bounds

```yaml
# validator-bounds.yaml
DEPLOY:
  max_files: 100
  allowed_envs: [staging, production]

SCRIPT_EXEC:
  allowed_scripts:
    - generate_all_seo_switches.js
    - recalculate-vlevel.js
  require_kill_switch: true

MIGRATE:
  max_statements: 50
  require_backup: true
```

### Gate 7: Risk Policy (D0/D1/D2)

| Niveau | Blast Radius | Heure | État Prod | Verdict |
|--------|--------------|-------|-----------|---------|
| D0 | Low | Any | Any | APPROVE |
| D1 | Medium | Business | Healthy | APPROVE |
| D1 | Medium | Business | Degraded | NEED_HUMAN |
| D1 | Medium | Off-hours | Any | APPROVE |
| D2 | High | Any | Any | NEED_HUMAN |

### Gate 8: Test Plan Requirement

```typescript
const TEST_REQUIREMENTS: Record<Action, TestPlan> = {
  DEPLOY: { smoke: true, healthcheck: true },
  MIGRATE: { dry_run: true, rollback_test: true, diff_check: true },
  SCRIPT_EXEC: { sandbox_run: true },
  CONFIG_UPDATE: { config_diff: true },
};
```

### Gate 9: Approval Chain

```typescript
interface ApprovalChain {
  requester: string;        // Celui qui soumet
  validator: string;        // Le Validator Engine (auto)
  human_approver?: string;  // Si NEED_HUMAN
  second_approver?: string; // Si 2-man rule pour D2
}
```

### Gate 10: Audit Log (Append-Only)

```sql
CREATE TABLE validator_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_card_id UUID NOT NULL,
  decision_hash TEXT NOT NULL,
  verdict TEXT NOT NULL CHECK (verdict IN ('APPROVE', 'REJECT', 'NEED_HUMAN')),
  gates_passed TEXT[] NOT NULL,
  gates_failed TEXT[] NOT NULL,
  risk_score INTEGER NOT NULL,
  test_plan JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT no_duplicate_hash UNIQUE (decision_hash)
);

-- RLS: insert-only pour le validator service role
```

---

## 4. Architecture Module NestJS

```
backend/src/modules/validator-engine/
├── validator-engine.module.ts
├── validator-engine.service.ts       # Orchestrateur 10 gates
├── services/
│   ├── schema-gate.service.ts        # Gate 1
│   ├── canonicalize-gate.service.ts  # Gate 2
│   ├── signature-gate.service.ts     # Gate 3
│   ├── replay-gate.service.ts        # Gate 4
│   ├── capability-gate.service.ts    # Gate 5
│   ├── bounds-gate.service.ts        # Gate 6
│   ├── risk-policy-gate.service.ts   # Gate 7
│   ├── test-plan-gate.service.ts     # Gate 8
│   ├── approval-gate.service.ts      # Gate 9
│   └── audit-gate.service.ts         # Gate 10
├── schemas/
│   └── decision-card.schema.ts       # Zod schema strict
├── config/
│   ├── bounds.config.ts              # Limites par action
│   ├── risk-policy.config.ts         # Matrice D0/D1/D2
│   └── test-requirements.config.ts   # Plans de test
└── types/
    └── validator.types.ts            # ValidationResult, Verdict, etc.
```

---

## 5. Intégration Stack Existante

| Composant Existant | Réutilisation |
|--------------------|---------------|
| `ZodValidationPipe` | Gate 1 (Schema) |
| `PaymentValidationService` | Gate 3 (HMAC pattern) |
| Redis sessions | Gate 4 (Nonce store) |
| Supabase RLS | Gate 10 (Audit append-only) |

---

## 6. Flow Diagram

```
┌─────────────┐     ┌──────────────────┐
│ Claude Code │────▶│  Decision Card   │
│   Agent     │     │    (JSON + sig)  │
└─────────────┘     └────────┬─────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────┐
│              VALIDATOR ENGINE                       │
│  ┌─────────────────────────────────────────────┐   │
│  │ Gate 1: Schema Parse (Zod strict)           │   │
│  │ Gate 2: Canonicalize → Hash                 │   │
│  │ Gate 3: HMAC Signature                      │   │
│  │ Gate 4: Nonce/Replay (Redis)                │   │
│  │ Gate 5: Capability/Scope                    │   │
│  │ Gate 6: Param Bounds                        │   │
│  │ Gate 7: Risk Policy (D0/D1/D2)              │   │
│  │ Gate 8: Test Plan Required                  │   │
│  │ Gate 9: Approval Chain                      │   │
│  │ Gate 10: Audit Log (append-only)            │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ APPROVE  │      │  REJECT  │      │NEED_HUMAN│
    │   ──▶    │      │   ──▶    │      │   ──▶    │
    │Action API│      │  Stop    │      │ Slack/   │
    └──────────┘      └──────────┘      │ Dashboard│
                                        └──────────┘
```

---

## 7. Verdict Output Format

```typescript
interface ValidatorVerdict {
  verdict: 'APPROVE' | 'REJECT' | 'NEED_HUMAN';
  decision_hash: string;
  gates: {
    name: string;
    passed: boolean;
    reason?: string;
    duration_ms: number;
  }[];
  risk_score: number;        // 0-100
  risk_level: 'D0' | 'D1' | 'D2';
  test_plan?: {
    smoke: boolean;
    dry_run: boolean;
    diff_check: boolean;
    rollback_test: boolean;
  };
  approval_chain: {
    requester: string;
    validator: 'auto';
    human_required: boolean;
    second_approver_required: boolean;
  };
  timestamp: string;
}
```

---

## 8. Prochaines Étapes

| Phase | Action | Effort |
|-------|--------|--------|
| P1 | Implémenter Gates 1-4 (parsing, hash, signature, replay) | M |
| P2 | Implémenter Gates 5-7 (capability, bounds, risk) | M |
| P3 | Implémenter Gates 8-10 (test plan, approval, audit) | M |
| P4 | Intégrer avec Action API | S |
| P5 | Dashboard NEED_HUMAN (Slack webhook) | S |

---

## 9. Questions Ouvertes

- [ ] Format exact JSON de la Decision Card (exemple concret)
- [ ] Clé HMAC dédiée ou réutiliser Paybox ?
- [ ] Notification NEED_HUMAN : Slack ? Email ? Dashboard admin ?
- [ ] Classification D0/D1/D2 des actions existantes

---

*Créé le 2026-02-02*
