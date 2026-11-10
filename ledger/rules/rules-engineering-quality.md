---
type: rules-document
status: canon
scope: engineering
updated: 2026-11-10
related_adrs:
  - ADR-123
related_incidents: []
related_rules:
  - rules-technical
  - rules-governance-process
  - rules-vault
---

# Rules — Engineering Quality & Modernization Mandate (Q1-Q4)

> **Source de vérité** — règles fondatrices d'ingénierie au 2026-04-27
> **Version** : 1.2.1 (Q2 et Q4 amendées par [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]], décisions de l’owner du 2026-11-03 ; 1.2.1 : Q3 alignée sur T2, statuts de Q4 alignés sur le schéma) | **Status** : CANON
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

### Clôture post-solution

Après qu'une solution non triviale a été corrigée et prouvée, identifier explicitement ce qu'elle rend obsolète ou redondant : workaround, couche compensatrice, dead path, flag temporaire, scanner, resolver, projection, dépendance ou représentation concurrente. Un élément devenu obsolète est supprimé dans le même PR **uniquement** s'il reste dans le périmètre gelé, relève du même ownership, ne sert aucune fenêtre de compatibilité nécessaire, est couvert par les vérifications pertinentes **et que cette suppression est autorisée par les règles d'autorité existantes**. Sinon, il est tracé dans un follow-up lié ou conservé avec une justification explicite et, lorsque pertinent, une condition de retrait. Toute solution qui ajoute une nouvelle couche doit démontrer pourquoi le mécanisme existant ne pouvait pas être corrigé, étendu ou consolidé.

---

## Q2 — Vérifier l'existant avant de créer (Grep-First Mandate)

**OBLIGATOIRE** : Rechercher les équivalents et leurs consommateurs dans les sources pertinentes avant toute création. Adapter les recherches au doute restant, sans quota fixe. Un résultat nul ne prouve pas à lui seul l’absence : préciser la couverture, les limites d’accès et pourquoi l’existant ne convient pas.

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
- Pas de nouveau service sans avoir cherché les services équivalents et leurs consommateurs.
- Si l'existant résout le problème ou peut être étendu pour le résoudre → **étendre l'existant** (Q1), pas créer de nouveau.

### Evidence requise

Toute proposition de nouveau fichier/convention DOIT inclure dans la PR/discussion la recherche effectuée :

```text
# Recherche de l'existant
sources et commandes utilisées (tableau ci-dessus, adaptées au doute restant)
résultats, y compris nuls, et couverture réelle (dépôts, chemins, motifs)
limites d'accès (dépôt, base ou environnement non consultés)
raison pour laquelle l'existant trouvé ne convient pas
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
- Nom de table : suivre T2 de [[rules-technical]]. Il n'y a pas de préfixe uniforme (`pieces`, `___xtr_order`, `__seo_*` coexistent) ; le nom se lit dans le schéma généré, il ne s'invente pas.

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

**OBLIGATOIRE** : Évaluer les options maintenues et compatibles lorsqu’un problème ou un gain documenté le justifie. La nouveauté seule ne déclenche ni migration, ni PR, ni issue. Réaliser seulement les changements couverts par le mandat ; consigner la suite réellement nécessaire dans le dossier existant.

### Triggers de modernisation

Les conditions suivantes justifient une évaluation. L'action indiquée n'est réalisée que si le mandat la couvre ; sinon, la suite réellement nécessaire est consignée dans le dossier existant :

| Trigger | Action à évaluer |
|---------|-----------------|
| Code utilise une lib/pattern déprécié (ex : Node 20 actions GitHub, callback APIs là où Promise existe) | Évaluation de la migration ; plan daté si elle est retenue (ADR si une décision change, G1) |
| Bibliothèque/framework majeur a une version stable plus récente avec gains documentés | Évaluation ; bump dans le mandat si la compatibilité est vérifiée |
| Pattern interne dupliqué ≥ 3 endroits | Extraction en utilitaire / module partagé |
| Workaround commenté avec TODO datant de plus de 6 mois | Évaluation du traitement définitif ; suite consignée dans le dossier existant |
| Performance budget dépassé > 2× sur un endpoint | Refactor (jamais juste augmenter le budget) |
| Coverage RPC / monitoring / observabilité < 80% sur module critique | Plan de remédiation |
| Schema DB avec dette structurelle (colonnes dual, FK manquantes, types incorrects) | Évaluation de la consolidation (ADR si une décision change, G1) |

### Anti-patterns "anti-modernisation" interdits

- **"On ne touche pas, ça marche"** alors qu'une régression silencieuse est possible (ex : Node 20 deprecated, knip 6.7.0 détecte plus de dette).
- **"On garde le legacy car les utilisateurs sont habitués"** sans avoir évalué le coût de maintenance vs migration.
- **Maintenir 2 implémentations d'une même chose** sans plan de convergence.
- **Bumper toutes les dépendances en une fois** sans avoir compris l'impact (préférer groupes ciblés type Dependabot `audit-tools`).

### Process

- Chaque ADR doit avoir une section "Revue Planifiée" avec date concrète.
- Les ADR `proposed` > 30 jours doivent être traitées : passer à `accepted`, `rejected`, `deferred` ou `superseded` (statuts du schéma, `ADR_STATUSES` de `_scripts/governance_constants.py`) — l'ambiguïté est de la dette.
- Toute revue de code peut/doit signaler un trigger Q4 — c'est un objet de revue légitime, pas du scope creep.

**Raison** : sans Q4, le système accumule mécaniquement de la dette. Les bricolages Q1 et les inventions Q2 deviennent du legacy "intouchable", la DB Q3 devient un musée. La modernisation continue est l'antidote structurel.

---

## Application aux agents IA

Les agents (Claude Code, Cowork, Codex, Agent SDK) DOIVENT :

1. **Q1** : avant tout code, écrire en clair la cause racine et la solution structurelle envisagée. Si l'utilisateur valide une option qui ne tient pas le test Q1.1-Q1.4, **le signaler explicitement** ("approche X demandée, mais Q1 suggère Y plus robuste car…") avant d'exécuter.
2. **Q2** : rechercher l'existant AVANT d'écrire un nouveau fichier, selon Q2. Coller les recherches dans la conversation comme evidence, avec leur couverture et leurs limites.
3. **Q3** : avant toute migration DB, exécuter `mcp__supabase__list_tables` ou `mcp__supabase__execute_sql` sur `information_schema`. Coller le résultat.
4. **Q4** : à chaque PR / commit / décision, mentionner explicitement les triggers Q4 rencontrés. Ce qui n'est pas traité dans le mandat est consigné dans le dossier existant ; aucune issue, PR ou ADR n'est créée pour le seul trigger (un ADR reste requis si une décision change, G1).

Les feedbacks utilisateur récurrents ("c'est du bricolage", "meilleure solution", "vérifier l'existant", "vérifier la DB") sont la conséquence directe d'une violation Q1/Q2/Q3 non détectée à temps. Q1-Q4 sont la version **proactive** de ces feedbacks.

---

## Évaluation et contrôle

### Auto-évaluation par agent / dev

Avant de soumettre PR ou de déclarer "fait" :

```text
[ ] Q1 cause racine identifiée et écrite
[ ] Q1 invariant garanti par construction (pas par cache/timeout)
[ ] Q1 dette nette : ___ ajoutée / ___ supprimée
[ ] Q1 clôture post-solution : obsolètes identifiés ; supprimés, suivis, ou conservation explicitement justifiée
[ ] Q2 recherche de l'existant collée (couverture, limites) pour chaque nouvelle convention/fichier
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
- Ajoute une couche sans démontrer pourquoi l'existant ne pouvait pas être corrigé, étendu ou consolidé (Q1 clôture).
- Conserve un mécanisme devenu obsolète dans le scope du PR sans justification ni disposition tracée (Q1 clôture).

### Métrique de qualité

`weekly-vault-lint` (ADR-020) vérifie déjà :
- ADR `proposed` > 30 jours → avertissement non bloquant (Q4), par `_scripts/check-obsolete-rules.py`.

Il n'est pas encore étendu à :
- Tables DB sans contrat éditorial documenté → alert (Q3).
- ENV var documentée mais non lue par le code, ou inverse → alert (Q2 négligence).

---

## Liens

- Related : [[rules-technical]] (T1-T7 techniques — Q domine en cas de conflit)
- Related : [[rules-governance-process]] (G5-G10 process — Q codifie le "comment", G le "qui/quoi")
- Related : [[rules-ai-antipatterns]] (AP-* — instances spécifiques de Q1 violations)
- Related : [[ADR-016-vehicle-page-matview-persistence]] (exemple Q1 appliqué : matérialisation vs timeout adaptatif)
- Related : [[ADR-021-database-rls-hardening-zero-trust]] (exemple Q3 appliqué : RLS comme contrat plutôt que ACL ad hoc)
- Related : [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte]] (Q2 et Q4 amendées : recherche sans quota fixe, évaluation sur problème ou gain documenté)

---

*Proposé le : 2026-04-27*
*Status : CANON dès merge*
*Dernière revue : 2026-11-10 (Q3 alignée sur T2, statuts de Q4 alignés sur le schéma ; aucune décision changée). Précédente : 2026-11-07 (Q2 et Q4, ADR-123)*
