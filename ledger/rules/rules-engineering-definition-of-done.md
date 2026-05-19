---
type: rules-document
status: canon
scope: engineering
updated: 2026-05-19
related_adrs:
  - ADR-053
  - ADR-058
  - ADR-020
  - ADR-016
  - ADR-021
related_incidents:
  - INC-2026-005
related_rules:
  - rules-engineering-quality
  - rules-deployment-workflow
  - rules-governance-process
  - rules-technical
  - rules-vault
---

# Rules — Engineering Definition of Done (DoD1-DoD9)

> **Source de vérité** — règles canon de "fini" au 2026-05-19
> **Version** : 1.0.0 | **Status** : CANON
> **Taxonomie** : DoD = Definition of Done — invariants qui définissent ce que "MERGED" exige. S'applique APRÈS Q1-Q4 (qualité initiale) et AVANT acceptance opérationnelle (état `MERGED` puis `OBSERVED` puis `CLOSED` per state-machine ADR-053).
>
> Le bricolage Q1 est interdit *avant* le code. La dette DoD est interdite *au moment du merge*. Une PR qui passe Q sans respecter DoD pousse de la dette en prod.

---

## DoD1 — Tests verts (par construction, pas par chance)

**OBLIGATOIRE** : CI verte sur la dernière révision avant merge. Aucun test flaky toléré. Coverage non-régressé sur les fichiers modifiés.

### Test de discrimination

1. **Tous les jobs CI requis** sont verts sur le HEAD final (pas un job précédent rebasé loin).
2. **Aucun `.only()`, `.skip()`, `it.skip`, `xdescribe`** dans les fichiers modifiés (sauf si commenté avec lien issue + TODO daté).
3. **Aucun `@ts-ignore`, `@ts-expect-error`, `eslint-disable`** ajouté sans commentaire indiquant l'invariant et un TODO daté.
4. **Coverage** : si la PR ajoute du code testable, le coverage du fichier n'a pas régressé (mesure : diff coverage report).

### Anti-patterns bloquants

- Re-run d'un job CI jusqu'à ce qu'il passe (= flaky non investigué).
- `npm test -- --testPathIgnorePatterns="<file>"` ajouté pour faire passer le merge.
- Test commenté avec `// FIXME` sans lien issue.
- Snapshot mis à jour sans audit du diff (`--updateSnapshot` aveugle).

### Evidence requise

Dans la description PR :

```text
- [x] CI green: <lien dernier run>
- [x] Aucun .only/.skip ajouté
- [x] Aucun @ts-ignore non motivé
- [x] Coverage diff: +0.X% / -0.X% sur fichiers touchés
```

**Raison** : un test flaky merge est un incident futur certain. Un `@ts-ignore` non motivé est un type-safety hole permanent. Chaque skip silencieux érode la confiance en CI.

---

## DoD2 — Ownership explicite (humain nommé, pas "everyone")

**OBLIGATOIRE** : la PR a un `assignee` clair ET au moins un reviewer humain confirmé. Le domaine touché a un owner identifié dans `audit/registry/planning.json` (champ `owners`).

### Test de discrimination

1. **Assignee non vide** sur la PR GitHub.
2. **≥1 review approval** humain (les bots ne comptent pas, sauf si `audit/registry/canonical.json` documente le bot comme reviewer canonique pour le domaine).
3. **Domain ownership** : le ou les chemins modifiés correspondent à un domaine D1..D15 avec owner non `__unassigned__` dans Layer 2 overlay `ownership.yaml`.
4. **Pas de self-merge** sauf documenté comme exception (cf. AP-self-merge en cas d'urgence avec audit trail).

### Anti-patterns bloquants

- PR sans assignee mergée.
- Self-approve sans audit trail (incident ou justification écrite).
- Reviewer = bot uniquement sur changement non-trivial.
- Modification d'un fichier `D{N}` avec `owners: [__unassigned__]` sans en profiter pour assigner.

### Evidence requise

```text
- [x] Assignee: @<github-user>
- [x] Reviewers approved: @<github-user>, ...
- [x] Domain ownership confirmed in ownership.yaml: <domain> → <owner>
```

**Raison** : sans owner explicite, la dette devient orpheline. Sans reviewer humain, l'erreur logique passe (les bots détectent syntaxe, pas intent). 538 ownership gaps détectés Layer 2 (PR-7a observatory) sont la conséquence directe de DoD2 négligence.

---

## DoD3 — Rollback défini (avant d'appuyer sur merge)

**OBLIGATOIRE** : la PR documente comment annuler le changement si quelque chose tourne mal en prod. Pas "on verra".

### Test de discrimination

1. **Plan de rollback écrit** dans la description PR (revert PR, hotfix, feature flag flip, migration down).
2. **Reversibility classée** : `instant` (revert PR + redeploy), `staged` (revert + data backfill), `forward-only` (rollback impossible, hotfix uniquement).
3. **Pour migrations Supabase** : DOWN migration présente OU justification écrite si forward-only.
4. **Pour deploys** : tag promote précédent identifié (cf. `rules-deployment-workflow` D4) pour rollback PROD.

### Anti-patterns bloquants

- "Si ça pète on revert" sans avoir vérifié que le revert compile (incompatible avec migration forward-only).
- Migration DDL sans DOWN ni justification.
- Feature shippée derrière un flag absent du runtime (DoD3 ↔ DoD4 couplé).

### Evidence requise

```text
- [x] Rollback plan: <revert PR / hotfix / flag flip>
- [x] Reversibility: instant / staged / forward-only
- [x] Si forward-only: justification écrite et acceptée par reviewer DoD2
```

**Raison** : incident `INC-2026-005` (palliatif timeout vehicle page → 30 500 URLs en 5xx pendant 6 semaines) a duré 6 semaines parce que personne n'avait écrit le rollback au moment du merge. Le coût d'écrire le plan AVANT merge < 1 minute. Le coût d'improviser pendant l'incident = 6 semaines.

---

## DoD4 — Observabilité présente (signal sortant sur changement runtime)

**OBLIGATOIRE** : tout code runtime nouveau ou modifié émet un signal observable (log structuré, metric, event log). Pas de boîte noire.

### Test de discrimination

1. **Logs structurés** : Nest `Logger` ou équivalent, level approprié (error/warn/info), context nommé.
2. **Metrics** : si endpoint nouveau ou modifié, latency p50/p95/p99 trackée (cf. perf-gates.yml).
3. **Event log applicatif** : pour les flows business (auth, payment, order, indexation), row dans `__seo_event_log` ou `__governance_event_log` ou table équivalente domaine.
4. **Pas de canary externe** quand observabilité interne existe (per `feedback_no_external_canary_when_internal_observability_exists` (MEMORY)).

### Anti-patterns bloquants

- `console.log` en production code.
- `try { ... } catch { /* silent */ }` sans logger.error.
- Nouveau service NestJS sans Logger constructor inject.
- Métrique inventée hors stack (Datadog ad hoc) alors que `__seo_event_log` ou Sentry existent.

### Evidence requise

```text
- [x] Logger ajouté dans <service.ts>
- [x] Event log row écrite dans <table> sur <action>
- [x] Sentry breadcrumb / metric trackée (si applicable)
- [x] Pas de console.log laissé
```

**Raison** : sans observabilité, l'incident T+1 est invisible jusqu'à ce que GSC affiche -40% impressions. Cf. incident 2026-04-22 sitemap stale (3 semaines de cécité avant détection). La cécité est un choix DoD4.

---

## DoD5 — Drift zéro (schema DB stable au moment du merge)

**OBLIGATOIRE** : aucune migration en attente, aucun drift entre schema canon (`audit/registry/db.json`) et état Supabase live, aucun contrat de type cassé.

### Test de discrimination

1. **`registry-fresh.yml` vert** sur la PR (L1 inventory ↔ L2 overlay ↔ live DB cohérents).
2. **Migrations atomiques** : si DDL, fichier unique sous `backend/supabase/migrations/YYYYMMDD_*.sql`, pas de migration manuelle hors pipeline.
3. **Types regénérés** : si schema DB change, `@repo/database-types` regénéré et commité.
4. **`mcp__supabase__list_migrations`** matche `git ls-files backend/supabase/migrations/` (pas de hand-applied non commité).

### Anti-patterns bloquants

- Migration appliquée en prod via console Supabase sans fichier git.
- `DROP COLUMN` sans audit usage applicatif préalable (Q3 violation rétro).
- Type `any` dans `@repo/database-types` au lieu de regénérer.
- 2 migrations même timestamp (collision).

### Evidence requise

```text
- [x] registry-fresh.yml: green
- [x] Migrations: <list of files added> ou "none"
- [x] Types regenerated: yes / no / N/A
- [x] mcp__supabase__list_migrations matches git: yes
```

**Raison** : chaque drift L1 ↔ live = un crash futur sur deploy frais ou rebuild canonical. Le drift se compose silencieusement. Cf. ADR-058 V4 invariant : `live = canonical = git`.

---

## DoD6 — Docs à jour (pas de comportement non documenté)

**OBLIGATOIRE** : si le comportement runtime, l'API, ou un contrat change, la doc associée change dans le même PR.

### Test de discrimination

1. **README backend/frontend** modifié si surface publique change.
2. **ADR ouvert** si décision archi (cf. AP-decision-without-adr).
3. **CLAUDE.md ou .claude/rules/** modifié si convention de travail change.
4. **PR body** explique le "pourquoi" du changement (pas seulement le "quoi" — diff suffit pour le quoi).
5. **JSDoc/TSDoc** sur API publique nouvelle.

### Anti-patterns bloquants

- Refactor majeur sans note pour le prochain reader.
- ENV var nouvelle absente de `.env.example`.
- Endpoint API nouveau sans annotation Swagger/OpenAPI si stack le supporte.
- "Voir code" comme seule documentation d'un comportement non-trivial.

### Evidence requise

```text
- [x] Docs updated: <list of files> ou "no doc change needed because <reason>"
- [x] .env.example: updated if ENV var added
- [x] PR body explains the "why"
```

**Raison** : le code dit "quoi", la doc dit "pourquoi". Sans le pourquoi, le prochain reader (humain ou agent) bricole par méconnaissance. Cf. INC-2026-005 cascadée à 6 semaines parce que le palliatif timeout n'avait pas d'ADR.

---

## DoD7 — Monitoring post-merge armé (qui-watch-quoi-quand)

**OBLIGATOIRE** : avant merge, identifier qui surveille quel signal pendant combien de temps après deploy.

### Test de discrimination

1. **Owner watch nommé** : `@<github-user>` qui regarde les dashboards/alertes pour T+0 à T+48h.
2. **Signaux watchés listés** : URLs Grafana, Sentry queries, GSC impressions, conversions, etc.
3. **Window définie** : durée d'observation explicite (T+1h, T+24h, T+48h, T+7j selon risque).
4. **Critère d'abort** : sous quel signal le rollback (DoD3) est déclenché.

### Anti-patterns bloquants

- "On verra si ça pète" (= pas de monitoring).
- Owner = "l'équipe" (= personne).
- Window indéfinie ("on watch un peu") = abandon en 2h.
- Critère d'abort flou ("si c'est moche on revert").

### Evidence requise

```text
- [x] Watcher: @<user>
- [x] Dashboards/alerts: <links>
- [x] Window: T+<duration>
- [x] Abort criteria: <specific threshold>
```

**Raison** : un merge sans monitoring est un fire-and-forget. La détection devient réactive (utilisateur ou GSC nous prévient) au lieu de proactive. Pour les `work_type: runtime-critical` ou `seo-runtime`, DoD7 est non-négociable.

---

## DoD8 — No TODO unresolved (TODO légitime = lien issue)

**OBLIGATOIRE** : tout `// TODO`, `// FIXME`, `// HACK`, `// XXX` ajouté dans la PR est lié à une issue/ticket GitHub OU est explicitement temporaire avec date d'expiration < 30 jours.

### Test de discrimination

1. **Pattern accepté** : `// TODO(<owner>, YYYY-MM-DD): description + issue link` OR `// TODO: tracked in #<issue-number>`.
2. **Pattern rejeté** : `// TODO: faire ça plus tard` (= dette anonyme).
3. **TODOs anciens** (>30j) non liés à une issue sont migrés ou supprimés dans la même PR si le fichier est touché (boy-scout rule).

### Anti-patterns bloquants

- `// TODO` orphelin ajouté.
- `// FIXME: c'est cassé mais ça compile` sans suite.
- TODO listant 5 idées à creuser sans owner.

### Evidence requise

```text
- [x] TODOs added: <count> · all linked to issues #<...> or dated < 30j
- [x] TODOs touched in modified files: <kept / migrated / removed>
```

**Raison** : un TODO non tracké est de la dette parfaite — invisible aux dashboards, illisible aux nouveaux contributeurs. Cf. CLAUDE.md backend `rules-engineering-quality` Q1.

---

## DoD9 — No silent skip (test/feature/migration explicitement gated)

**OBLIGATOIRE** : aucun mécanisme caché qui désactive du comportement attendu sans audit trail.

### Test de discrimination

1. **Tests skip** : `.skip()` accompagné de commentaire + issue.
2. **Feature flag** : si `if (process.env.SKIP_X)` ou équivalent, documenté dans `.env.example` et lié à un rollout plan.
3. **Migration skip** : aucun fichier migration ignoré silencieusement par script wrapper.
4. **Validation bypass** : `try { schema.parse() } catch { return defaultValue }` = silent failure interdit (cf. AP-silent-validation-bypass).

### Anti-patterns bloquants

- `if (NODE_ENV === 'test') return;` dans code prod sans justification.
- `catch (e) { /* probably fine */ }`.
- Migration `--dry-run` mergée en prod sans avoir été appliquée.
- Toggle hardcodé `const ENABLE_X = false;` sans plan de retrait.

### Evidence requise

```text
- [x] No silent test skips added
- [x] No catch-swallow added
- [x] All env-gated branches documented in .env.example
```

**Raison** : un skip silencieux est pire qu'une erreur — il fait croire que tout va bien. Cf. AP catalog `silent-failure-hunter` et incidents répétés où une exception swallow a masqué une régression pendant des semaines.

---

## Application aux agents IA

Les agents (Claude Code, Cowork, Codex, Agent SDK, Cursor) DOIVENT :

1. **Avant d'écrire `Merged` / `Done` / `Shipped` en MEMORY ou log.md** : vérifier mentalement les 9 DoD. Si une case n'est pas cochable → l'état canonique reste `REVIEW` ou `VERIFIED`, pas `MERGED`.
2. **Avant de proposer `gh pr merge`** : confirmer DoD1 (CI verte) ET DoD2 (assignee + reviewer) ET DoD3 (rollback documenté). Les 6 autres sont gate de revue.
3. **En cas de PR factice / test / spike** : marquer `draft: true` ET label `experiment` (work_type) qui relâche DoD1, DoD4, DoD6, DoD7 mais pas DoD2, DoD3, DoD5, DoD8, DoD9.
4. **Auto-évaluation DoD obligatoire** dans le body PR (template ci-dessous).

---

## Escape hatch (rare, audité)

Si un blocage opérationnel exige skip d'un DoD spécifique :

**Label PR** : `dod-skip-justified`

**Exigences cumulatives** :
1. Commentaire PR explicitant **lequel** DoD est skippé + **pourquoi** (lien incident/issue).
2. **≥2 approvers** humains distincts confirment le skip.
3. Row écrite dans `__governance_event_log` (table existante per `feedback_no_external_canary_when_internal_observability_exists`) avec : `event_type='dod_skip'`, `pr_number`, `dod_skipped`, `reason`, `approvers[]`.
4. Issue/ADR ouverte pour remédiation post-merge dans les 7 jours.

**Audit** : `weekly-vault-lint` (ADR-020) émet alert si :
- `dod-skip-justified` count hebdomadaire > 2 (signal abus).
- Issue de remédiation > 7 jours sans update.

Le skip n'est pas une exception silencieuse — c'est une dette documentée avec horloge.

---

## Évaluation et contrôle

### Auto-évaluation par agent / dev (à coller dans le body PR)

```text
## Definition of Done — auto-évaluation

- [ ] DoD1 — Tests verts: CI green, no flaky, no .only/.skip added
- [ ] DoD2 — Ownership: assignee + ≥1 human approval
- [ ] DoD3 — Rollback: <plan link>, reversibility=<instant/staged/forward-only>
- [ ] DoD4 — Observabilité: <log/metric/event log added or N/A>
- [ ] DoD5 — Drift zéro: registry-fresh green, migrations atomic
- [ ] DoD6 — Docs: <files updated or "no doc needed">
- [ ] DoD7 — Monitoring: watcher=@<user>, window=T+<duration>, abort=<criteria>
- [ ] DoD8 — No TODO unresolved: <count, all linked>
- [ ] DoD9 — No silent skip: confirmed

Work type (per planning-worktype.yml): <runtime-critical | governance | seo-runtime | observability | cleanup | migration | debt | experiment | emergency>
```

### Contrôle au niveau revue

Le reviewer doit refuser une PR qui :
- Manque la section DoD auto-évaluation.
- Coche DoD1-DoD9 sans evidence concrète (case cochée sans link).
- Tagge `runtime-critical` ou `seo-runtime` sans DoD7 explicite.
- Tagge `migration` sans DoD3 reversibility + DoD5 evidence.
- Utilise `dod-skip-justified` sans 2 approvers + audit trail.

### Enforcement automatique

1. **`vault-governance.yml`** (existing) : vérifie que `rules-engineering-definition-of-done.md` est référencée par les rules dérivées + canon-backlinks.
2. **`pr-dod-gate.yml`** (nouveau, monorepo `ak125/nestjs-remix-monorepo`) : lit cette rule + bloque merge si template DoD absent ou cases vides sans `dod-skip-justified` valide.
3. **`weekly-vault-lint.yml`** (extension) : audit hebdo des skips + remédiation < 7j.

---

## Liens

- Précondition : [[rules-engineering-quality]] (Q1-Q4 s'appliquent AVANT DoD)
- Process : [[rules-governance-process]] (G5-G8 qui décide, DoD décrit fini)
- Process : [[rules-deployment-workflow]] (D1-D6 décrit comment shipper, DoD7 nomme le watcher)
- Anti-patterns : [[rules-ai-antipatterns]] (chaque AP est une violation DoD potentielle)
- Vault discipline : [[rules-vault]] (G1-G4 signed commits, DoD3 rollback documenté)
- Planning : [[ADR-053-planning-live-system]] (state machine PLANNED→…→CLOSED, DoD gate vers MERGED)
- Control Plane : [[ADR-058-repository-control-plane]] (registry L1+L2 référencés par DoD2 ownership, DoD5 drift)
- Quality observability : [[ADR-020-weekly-vault-lint]] (audit DoD skip)
- Exemple Q1 appliqué : [[ADR-016-vehicle-page-matview-persistence]] (DoD3 forward-only justifié)
- Exemple Q3 appliqué : [[ADR-021-database-rls-hardening-zero-trust]] (DoD5 drift contrat RLS)

---

*Proposé le : 2026-05-19*
*Status : CANON dès merge*
*Dernière revue : 2026-05-19*
