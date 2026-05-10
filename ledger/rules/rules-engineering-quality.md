---
type: rules-document
status: canon
scope: engineering
updated: 2026-04-27
related_adrs: []
related_incidents: []
related_rules:
  - rules-technical
  - rules-governance-process
  - rules-vault
---

# Rules — Engineering Quality & Modernization Mandate (Q1-Q4)

> **Source de vérité** — règles fondatrices d'ingénierie au 2026-04-27
> **Version** : 1.0.0 | **Status** : CANON
> **Taxonomie** : Q = Quality — règles méta qui s'appliquent AVANT toute autre règle (T*, G*, AP*).
>
> Ces règles codifient ce qui distingue une **solution structurelle** d'un **bricolage**. Elles sont **non-négociables** pour tout agent (humain, Claude Code, Cowork, Codex, Agent SDK) et tout reviewer.

---

## Q1 — Mandat de la meilleure approche (Anti-Bricolage)

**OBLIGATOIRE** : pour tout problème non trivial, choisir et défendre la solution la plus **robuste, moderne et durable** disponible. Le bricolage est interdit.

### Définitions

- **Solution structurelle** : corrige la cause racine, supprime de la dette, garantit un invariant SLA/contrat, reste vraie après éviction de cache, scale event ou montée de version d'outil.
- **Bricolage** : déplace le coût (cache pré-payé, timeout étendu), masque le symptôme (silencer un test flaky), pose une condition fragile (top-N hardcodé), invente du code custom alors qu'un standard moderne existe.

### Test de discrimination

Avant de proposer/coder une solution, répondre par écrit à ces 4 questions :

1. **Cause racine** : qu'est-ce qui CRÉE le problème, pas seulement le déclenche ?
2. **Invariant garanti** : après cette solution, quel invariant tient *par construction*, indépendamment des conditions runtime (cache, charge, version d'outil) ?
3. **Dette** : est-ce que cette solution AJOUTE ou SUPPRIME de la dette nette ? (quantifier : workarounds enlevés, fichiers simplifiés, lignes supprimées)
4. **Précédent** : existe-t-il un pattern établi dans le codebase pour ce type de problème ? (ex : ADR-016 pour pages SSR lourdes → matérialisation). Si oui, l'utiliser ou justifier explicitement la divergence.

Une réponse "ça marche pour l'instant" / "on verra plus tard" / "c'est un quick fix" sur Q1.2 = **bricolage rejeté**.

### Anti-patterns explicites interdits

- **Refresh d'un compteur de baseline** (audit, perf, SEO) au lieu de fixer la cause de la dérive.
- **Augmenter un timeout** sans avoir mesuré la cause de la lenteur.
- **Pré-warmer un cache** comme solution principale (le cache cache le coût, ne le supprime pas).
- **Inventer une nouvelle convention** (ENV var, nom de table, domaine) sans grep préalable de l'existant — voir Q2.
- **Skip d'un test flaky** sans investigation de la cause.
- **`as any`, `// @ts-ignore`, `// eslint-disable`** sans commentaire qui explique l'invariant et un TODO daté.
- **Hardcoder une liste top-N** quand la donnée existe en DB (ex : `idx_pieces_relation_type_popular` sur top-10 hardcodé — incident ADR-016).

**Raison** : chaque bricolage non documenté devient un pattern reproduit ailleurs. La dette se compose. Voir incidents `INC-2026-005` (palliatif timeout vehicle page → 30 500 URLs en 5xx pendant 6 semaines).

---

## Q2 — Vérifier l'existant avant de créer (Grep-First Mandate)

**OBLIGATOIRE** : avant de créer tout nouvel artefact (fichier, ENV var, convention, domaine, nom de service, route, type), **grep** d'abord. Tout est probablement déjà là.

### Commandes obligatoires par type d'artefact

| Si je propose… | Je dois d'abord exécuter… |
|---|---|
| Nouvelle ENV var | `grep -rE "process\.env\.\|configService\.get" backend/src \| grep -i "<topic>"` + `grep -i "<topic>" backend/.env.example` |
| Nouveau domaine / URL canonique | `grep -E "automecanik\." backend/src/config frontend/app/root.tsx` + lire `backend/src/config/site.constants.ts` |
| Nouvelle table DB | voir Q3 (vérification Supabase obligatoire) |
| Nouveau service NestJS | `find backend/src/modules -name "*.ts" \| xargs grep -l "<keyword>"` |
| Nouveau composant React | `find frontend/app/components -name "*.tsx" \| xargs grep -l "<feature>"` |
| Nouveau skill | `ls .claude/skills/` + lire les SKILL.md frontmatters concernés |
| Nouvelle route Remix | `ls frontend/app/routes/ \| grep -i "<pattern>"` |
| Nouveau fichier de règle / ADR | `ls ledger/decisions/adr/ \| ledger/rules/` + auditer numérotation et conventions |

### Règles dérivées

- Pas de nouvelle ENV var sans avoir grep `process.env` ET `.env.example`.
- Pas de nouveau domaine sans avoir lu `site.constants.ts`.
- Pas de nouveau service sans avoir cherché les services équivalents (≥ 3 patterns).
- Si grep retourne du code qui résout déjà 70% du problème → **étendre l'existant**, pas créer de nouveau.
- Si gap réel → confirmer par 2-3 patterns différents avant de proposer.

### Evidence requise

Toute proposition de nouveau fichier/convention DOIT inclure dans la PR/discussion :

```bash
# Preuve d'absence
grep -rE "<convention>" <scopes> | wc -l    # Doit être 0
ls <directory> | grep -i "<keyword>"        # Vide ou non-conflictuel
```

Sans cette evidence, la PR est rejetée par revue (T6 anti-pattern).

**Raison** : incidents répétés où conventions inventées (`GOOGLE_SA_CLIENT_EMAIL`, `GSC_PROPERTY_URL`, `automecanik.fr`) alors que le codebase utilisait déjà `GSC_CLIENT_EMAIL`, `GSC_SITE_URL`, `automecanik.com`. Chaque invention = PR à corriger ou pire, divergence runtime silencieuse.

---

## Q3 — Vérifier la DB Supabase avant de créer table/colonne

**OBLIGATOIRE** : avant toute migration créant une table ou une colonne, **inspecter le schéma Supabase courant** sur le projet `massdoc` (project_id : `cxpojprgwgubzjyqzmoq`). Pas de création à la volée.

### Commandes obligatoires

| Avant de créer… | Vérification obligatoire |
|---|---|
| Une table | `mcp__supabase__list_tables` + `mcp__supabase__execute_sql "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%<keyword>%'"` |
| Une colonne | `mcp__supabase__execute_sql "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='<table>'"` |
| Un index | `mcp__supabase__execute_sql "SELECT indexname, indexdef FROM pg_indexes WHERE tablename='<table>'"` |
| Une RPC / fonction | `mcp__supabase__execute_sql "SELECT proname, prosrc FROM pg_proc WHERE proname LIKE '<pattern>'"` |
| Une vue / matview | `mcp__supabase__execute_sql "SELECT viewname FROM pg_views WHERE viewname LIKE '<pattern>'"` |

### Règles dérivées

- Pas de migration `CREATE TABLE __X` sans avoir grep les `backend/supabase/migrations/` ET interrogé `information_schema`.
- Pas de nouvelle colonne sur une table existante sans avoir audité les colonnes existantes (les schémas `pieces_*` ont fréquemment des doublons TEXT/INTEGER — voir ADR-018).
- Pas de nouvelle RPC sans avoir cherché les RPC voisines (préférer étendre une RPC documentée que créer une variante).
- Tables `__archive` schema = lecture seule, jamais y créer de nouvelles tables.
- Préfixe `__` obligatoire pour toutes les tables applicatives (T2).

### Evidence requise

Toute migration DDL DOIT inclure dans la PR :

```sql
-- Preuve d'absence (à coller dans la PR description)
SELECT table_name FROM information_schema.tables
WHERE table_schema='public' AND table_name LIKE '%<keyword>%';
-- Result: 0 rows OR explanation of why the existing table doesn't fit
```

### Cas particuliers (interdit absolu)

- **Jamais** `DROP TABLE`, `DROP COLUMN`, `TRUNCATE` sans validation humaine explicite + backup vérifié (mémoire `feedback_no_destructive_db`).
- **Jamais** modifier une table avec RLS active sans relire `rules-database-rls` (ADR-021).
- **Jamais** créer une table sans contrat éditorial (qui écrit ? quand ? trigger d'invalidation ?).

**Raison** : incidents répétés de schémas dual TEXT/INTEGER sur `pieces_*` (ADR-017, ADR-018), de tables fantômes créées par scripts ad hoc, de colonnes non utilisées qui s'accumulent. Cleanup -77GB DB (mémoire `supabase-cleanup-2026-03`) avait pour cause précisément l'absence de Q3.

---

## Q4 — Esprit de modernisation continue

**OBLIGATOIRE** : à chaque itération sur un module / DB / process, évaluer s'il est aligné avec l'état moderne de l'art. Pas de "ça marche, on touche pas" si une approche plus moderne existe et est applicable.

### Triggers de modernisation

Une modernisation est **attendue** quand au moins une des conditions suivantes apparaît :

| Trigger | Action attendue |
|---------|-----------------|
| Code utilise une lib/pattern déprécié (ex : Node 20 actions GitHub, callback APIs là où Promise existe) | Plan de migration daté, ADR si breaking |
| Bibliothèque/framework majeur a une version stable plus récente avec gains documentés | Évaluation + PR de bump si compatibility OK |
| Pattern interne dupliqué ≥ 3 endroits | Extraction en utilitaire / module partagé |
| Workaround commenté avec TODO datant de plus de 6 mois | Issue/ADR pour traitement définitif |
| Performance budget dépassé > 2× sur un endpoint | Refactor (jamais juste augmenter le budget) |
| Coverage RPC / monitoring / observabilité < 80% sur module critique | Plan de remédiation |
| Schema DB avec dette structurelle (colonnes dual, FK manquantes, types incorrects) | ADR de consolidation |

### Anti-patterns "anti-modernisation" interdits

- **"On ne touche pas, ça marche"** alors qu'une régression silencieuse est possible (ex : Node 20 deprecated, knip 6.7.0 détecte plus de dette).
- **"On garde le legacy car les utilisateurs sont habitués"** sans avoir évalué le coût de maintenance vs migration.
- **Maintenir 2 implémentations d'une même chose** sans plan de convergence.
- **Bumper toutes les dépendances en une fois** sans avoir compris l'impact (préférer groupes ciblés type Dependabot `audit-tools`).

### Process

- Chaque ADR doit avoir une section "Revue Planifiée" avec date concrète.
- Les ADR `proposed` > 30 jours doivent être traitées (passer à `accepted`/`paused`/`obsolete`) — l'ambiguïté est de la dette.
- Toute revue de code peut/doit signaler un trigger Q4 — c'est un objet de revue légitime, pas du scope creep.

**Raison** : sans Q4, le système accumule mécaniquement de la dette. Les bricolages Q1 et les inventions Q2 deviennent du legacy "intouchable", la DB Q3 devient un musée. La modernisation continue est l'antidote structurel.

---

## Application aux agents IA

Les agents (Claude Code, Cowork, Codex, Agent SDK) DOIVENT :

1. **Q1** : avant tout code, écrire en clair la cause racine et la solution structurelle envisagée. Si l'utilisateur valide une option qui ne tient pas le test Q1.1-Q1.4, **le signaler explicitement** ("approche X demandée, mais Q1 suggère Y plus robuste car…") avant d'exécuter.
2. **Q2** : grep AVANT d'écrire un nouveau fichier. Coller le résultat de grep dans la conversation comme evidence.
3. **Q3** : avant toute migration DB, exécuter `mcp__supabase__list_tables` ou `mcp__supabase__execute_sql` sur `information_schema`. Coller le résultat.
4. **Q4** : à chaque PR / commit / décision, mentionner explicitement les triggers Q4 rencontrés (même si non traités dans la PR — créer issue/ADR).

Les feedbacks utilisateur récurrents ("c'est du bricolage", "meilleure solution", "vérifier l'existant", "vérifier la DB") sont la conséquence directe d'une violation Q1/Q2/Q3 non détectée à temps. Q1-Q4 sont la version **proactive** de ces feedbacks.

---

## Évaluation et contrôle

### Auto-évaluation par agent / dev

Avant de soumettre PR ou de déclarer "fait" :

```text
[ ] Q1 cause racine identifiée et écrite
[ ] Q1 invariant garanti par construction (pas par cache/timeout)
[ ] Q1 dette nette : ___ ajoutée / ___ supprimée
[ ] Q2 grep evidence collée pour chaque nouvelle convention/fichier
[ ] Q3 information_schema interrogé pour chaque DDL (si migration)
[ ] Q4 triggers identifiés et listés (même si reportés)
```

### Contrôle au niveau revue

Le reviewer doit refuser une PR qui :
- Déclare "fait" sans evidence Q2/Q3 quand applicable.
- Propose un nouveau fichier dont l'équivalent existe déjà (Q2 violation).
- Augmente un timeout / refresh une baseline / pré-warm un cache comme solution principale (Q1 violation).
- Crée une table/colonne sans evidence d'absence préalable (Q3 violation).
- Ne mentionne aucun trigger Q4 sur un module qu'il modifie (Q4 négligence).

### Métrique de qualité

`weekly-vault-lint` (ADR-020) sera étendu pour vérifier :
- ADR `proposed` > 30 jours → alert (Q4).
- Tables DB sans contrat éditorial documenté → alert (Q3).
- ENV var documentée mais non lue par le code, ou inverse → alert (Q2 négligence).

---

## Liens

- Related : [[rules-technical]] (T1-T7 techniques — Q domine en cas de conflit)
- Related : [[rules-governance-process]] (G5-G8 process — Q codifie le "comment", G le "qui/quoi")
- Related : [[rules-ai-antipatterns]] (AP-* — instances spécifiques de Q1 violations)
- Related : [[ADR-016-vehicle-page-matview-persistence]] (exemple Q1 appliqué : matérialisation vs timeout adaptatif)
- Related : [[ADR-021-database-rls-hardening-zero-trust]] (exemple Q3 appliqué : RLS comme contrat plutôt que ACL ad hoc)

---

*Proposé le : 2026-04-27*
*Status : CANON dès merge*
*Dernière revue : 2026-04-27*
