---
id: ADR-082
title: "Doctrine d'amélioration continue globale — lightweight advisory filter (amended Voie 3 post INC-2026-016)"
status: proposed
date: "2026-05-27"
decision_date: "2026-05-27"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-013", "ADR-058", "ADR-060"]
related_adr: ["ADR-013", "ADR-015", "ADR-031", "ADR-033", "ADR-058", "ADR-060", "ADR-062", "ADR-081"]
related_rules: ["rules-engineering-quality", "rules-ai-antipatterns", "rules-governance-process", "G3"]
related_incidents: ["INC-2026-016"]
reviewed_by: ""
---

# ADR-082 : Doctrine d'amélioration continue globale — lightweight advisory filter

> **Amended Voie 3 (2026-05-27 post INC-2026-016)** — ce document est l'**amendement avant ratification** de la draft v15.4 du 2026-05-26. La draft originelle prévoyait Phase 3 ratchet bloquant (5 critères cumulatifs + owner GO). Suite à l'incident d'authority drift **[INC-2026-016](../incidents/2026/2026-05-27-monorepo-pr765-adr082-authority-drift.md)** (monorepo PR #765 a déclaré "canon ADR-082" avant ratification vault), la décision Voie 3 ratifie ADR-082 uniquement en **mode lightweight advisory perpétuel**. Toute promotion future vers blocking gate exigera un **amendement vault séparé** (pas owner GO seul). Cf §Amendement Voie 3 ci-dessous.

## Contexte

Multi-itérations méthodologiques 2026-05-26 (15 versions v1→v15.4) ont révélé le besoin d'une doctrine unifiée d'aide à la décision pour toute amélioration AutoMecanik. Règles éparses dans CLAUDE.md, `.claude/rules/`, MEMORY.md ; pas de canon court machine-readable.

Risques observés :

- **"Improvements" non mesurés** — changement aléatoire présenté comme "amélioration produite" sans qualifier le gain (faux READY).
- **Ajouts de couches sans justification** — chaque outil/script/agent ajoute de la dette technique (`complexity-gravity` ADR-081).
- **Pivot de sujet pour éviter blockers** — biais d'évitement, cimetière de failure maps.
- **Sur-loop sans gain marginal** — sur-tester, sur-documenter pendant que l'entreprise a besoin d'avancer.
- **Isolation SEO du système global** — confusion entre "machine SEO" et système global qui produit du SEO comme conséquence.
- **Décisions au feeling sans hiérarchie** — pas de priorité explicite entre cash, SEO, conversion, stabilité, simplification.

**Incident additionnel (INC-2026-016, 2026-05-27)** : Monorepo PR #765 (merge 2026-05-26 23:01 UTC) a livré 3 artefacts revendiquant "canon ADR-082 vault" alors qu'ADR-082 restait en draft non-ratifié. Violation ADR-060 (vault décide → monorepo exécute) + Invariant G3. Cet incident a confirmé qu'une doctrine "canon" précipitée vers blocking gate est elle-même un anti-pattern. L'amendement Voie 3 ci-dessous code en dur l'aprentissage.

## Décision

L'amélioration est **globale**, **mesurable**, **bornée** et **contrôlée**. Elle s'applique à tout changement AutoMecanik via **3 outils complémentaires (pas un nouveau système, pas une nouvelle couche)** :

| Outil | Rôle | Path | Statut normatif |
|---|---|---|---|
| Cette ADR | filtre léger, doctrine d'aide à la décision | `governance-vault/ledger/decisions/adr/ADR-082-*.md` | **advisory perpétuel (Voie 3)** |
| Skill `continuous-improvement-global` | méthode opérationnelle agent | `.claude/skills/continuous-improvement-global/SKILL.md` | **advisory, opt-in par PR** |
| PR template section `## Improvement Gate` | preuve optionnelle (force-pas application humaine) | `.github/PULL_REQUEST_TEMPLATE.md` | **OPTIONAL, jamais obligatoire** |
| JSON Schema `improvement-report.schema.json` | format machine si rapport généré | `.spec/00-canon/improvement-report.schema.json` | **format, pas mandat** |

### Règles canon (8 piliers — résumé court, détails dans le skill)

1. **Définition** : Améliorer = changement borné qui réduit un écart **mesurable** entre l'état réel et l'état attendu, avec gain > coût + risque. **Améliorer ≠ ajouter** — peut être simplification, suppression, consolidation, clarification structurelle.

2. **Boucle obligatoire** : test → control → verify → fix → retest → améliorer, avec critère d'arrêt clair. Pas de boucle infinie sans gain marginal.

3. **Preuve avant/après** : pas de validation sans preuve mesurable. Sans preuve = statut maximum `CONCEPTUEL`.

4. **Anti-complexité hiérarchique** : Étendre > Consolider > Supprimer > Simplifier > Ajouter (en dernier recours). 6 questions avant tout ajout : peut-on corriger l'existant / simplifier / fusionner / supprimer duplication / réduire scripts / obtenir le même résultat avec moins de code ? OUI à l'une = pas d'ajout.

5. **Non-régression** : ne pas casser routes / panier / paiement / SEO indexé / données / pipelines / CI / build / perf / UX.

6. **Hiérarchie 6 priorités** : P1 Survie business (cash/paiement) > P2 SEO/ranking > P3 Conversion > P4 Stabilité technique > P5 Simplification > P6 Gouvernance.

7. **9 verdicts terminaux** (enum du JSON Schema) : `PASS / FIX_AND_RETEST / PARTIAL_READY / OPERATIONAL_READY / SCALE_READY / BLOCKED_OWNER / STOP_LOW_VALUE / STOP_TOO_COMPLEX / ROLLBACK_REQUIRED`. **Verdict < OPERATIONAL_READY = mode d'exécution prudent, PAS un stop.**

8. **Pas de scale sans pilote `OPERATIONAL_READY`** — interdiction de bulk, mass-automation, ratchet CI bloquant, publication SEO large, génération contenu volume tant qu'un pilote n'a pas prouvé le système sur cas réel représentatif.

### Filtre 6 questions (advisory — agent décide quand l'appliquer)

1. Est-ce que ça améliore vraiment ?
2. Est-ce mesurable ?
3. Est-ce prioritaire (P1-P6) ?
4. Est-ce plus simple ?
5. Est-ce sûr ? → cf SAFE intégré
6. Est-ce que ça rapproche un objectif business réel ?

Si NON à l'une → l'agent **doit reconsidérer**, **pas** automatiquement renoncer. Le filtre est aide à la décision, pas vote bloquant.

### SAFE intégré (dimension du score, PAS nouvelle couche)

> *« SAFE n'est pas un frein. SAFE est le calcul intelligent du risque dans le score d'amélioration. »*

4 niveaux ordinaux (`safe_level` du `improvement-report.json`) :

| Niveau | Sémantique | Preuve attendue |
|---|---|---|
| `SAFE_0` | aucun risque runtime (doc, plan, mémoire, audit) | aucune preuve runtime |
| `SAFE_1` | risque faible, réversible (proposal uncommitted, schema additif, edit `.md` Phase 1) | rollback path explicite |
| `SAFE_2` | risque moyen, preuve ciblée nécessaire (skill modif, migration additive, ratchet CI informationnel) | non-régression 9/9 + test cas réel |
| `SAFE_3` | risque critique (payment, prod runtime, migration destructive, bulk SEO, pricing) | rollback testé + preuve avant/après + owner GO explicite |

Action **ralentie SEULEMENT si** : surface critique AND (risque de casse > gain OR rollback absent OR preuve non-régression insuffisante). Sinon SAFE reste signal léger non-bloquant.

---

## ⚖️ Amendement Voie 3 — Lightweight Advisory Filter Perpétuel (canon)

> **Cette section est la décision principale de l'ADR amendée 2026-05-27.**

### A1. Statut normatif par défaut = `advisory perpétuel`

ADR-082 est **ratifiée uniquement comme doctrine légère d'aide à la décision**. Elle n'a **JAMAIS** statut de gate bloquant par défaut.

- ❌ **Pas** d'application obligatoire sur toutes les PRs.
- ❌ **Pas** de blocking gate CI activé par défaut.
- ❌ **Pas** de nouvelle couche de gouvernance ajoutée par cette ADR.
- ❌ **Pas** d'extension implicite à tous les pipelines (Phase 4 originelle **supprimée**).
- ✅ Application **opt-in** par l'agent / la PR au cas par cas, quand utile.
- ✅ Gate CI `vault-canon-exists.yml` reste **warn-only** (cf. INC-2026-016 Action Correctives).

### A2. Promotion future vers blocking — verrou explicite

Toute évolution vers un **gate bloquant** (CI required, PR template mandatory, application universelle, ratchet bloquant) exige :

1. **Un amendement vault séparé** de cet ADR-082 (PR vault G3-signed, pas owner GO seul)
2. **5 critères cumulatifs empiriques** (héritage de la draft originelle, conservés) :
   - ≥3-5 PRs réelles avec gate utilisé volontairement
   - <10 min friction moyenne par PR
   - 0 false blocker observé
   - ≥1 vraie erreur détectée grâce au gate (sinon = absence de valeur prouvée)
   - Owner GO explicite (mais **insuffisant seul** — owner GO + amendement vault G3 sont AND, pas OR)

Le verrou "amendement vault séparé" est la leçon principale d'INC-2026-016 : owner GO seul ne suffit pas à inverser une doctrine fondamentale ADR-060.

### A3. Phase 4 originelle supprimée

L'évolution future "Phase 4 — adoption obligatoire à tous les pipelines AutoMecanik" de la draft originelle est **supprimée**. Une adoption obligatoire universelle = blocking gate par construction → exige amendement séparé (A2).

Si la doctrine prouve sa valeur dans la durée, l'amendement futur pourra réintroduire une Phase 4, mais elle n'est PAS pré-autorisée par cette ADR.

### A4. Application au monorepo (post INC-2026-016)

État durable post-amendement Voie 3 (sans nouvelle PR vault) :

- Skill `.claude/skills/continuous-improvement-global/SKILL.md` peut rester `status: experimental` ou être promu `status: stable` (au choix owner), MAIS doit conserver explicitement dans description + banner : "advisory only, never default-blocking per ADR-082 amended Voie 3".
- Schema `.spec/00-canon/improvement-report.schema.json` : `title` peut perdre le "(proposed)" et devenir simplement "Improvement Report v1 (advisory format per ADR-082)". `$comment` conservé pour signaler "advisory, never default-blocking".
- PR template `Improvement Gate` : section reste **`[OPTIONAL]`** dans `<details>` collapsé. Pas de mandat de remplissage.

### A5. Lecture canon

> *« ADR-082 est un filtre léger d'aide à la décision, opt-in par PR, jamais blocking par défaut. Toute promotion future vers blocking gate exige un amendement vault séparé (PR G3 vault), pas un owner GO seul. C'est la leçon directe d'INC-2026-016. »*

---

### Phasing (post-amendement Voie 3)

- **Phase 1 — Minimal viable shipped** : ADR amendée + SKILL.md advisory + PR template optional + JSON Schema advisory + pilotes empiriques (filtre-a-air, MEMORY.md compaction). **Done.**
- **Phase 2 — Automatisation légère** : si répétition observée, micro-ajouts opt-in possibles (validate-improvement-report.sh wrapper, lazy-loaded checklist). **Reste opt-in, jamais obligatoire.**
- **Phase 3 — Ratchet bloquant** : **interdite** sans amendement vault séparé (A2). Owner GO insuffisant.
- **~~Phase 4 — Adoption obligatoire~~** : **supprimée** par amendement Voie 3 (A3).

### Split Automatique vs Humain

- **AUTO** : tests, lint, typecheck, build, CI, smoke, logs, métriques SEO/business, Redis, DB, frontend, backend, GSC, régression.
- **HUMAIN** : merge risqué, rollback prod, suppression fichiers, migration DB destructive, bulk SEO, publication massive, changement pricing, activation pipeline grande échelle.

### Scope global (anti-isolation SEO)

L'amélioration touche : code / architecture / DB / contenu / SEO / ranking / conversion / UX / performance / pipelines / scripts / CI-CD / observabilité / gouvernance / coûts / simplicité / sécurité / maintenance / business. **SEO ≠ machine isolée** — ranking est conséquence d'un système global sain.

### Sémantique d'exécution v15.3 (PARTIAL_READY ≠ stop)

| Statut / Verdict | Mode d'exécution | Autorisé | Bloqué |
|---|---|---|---|
| `CONCEPTUEL` | CONCEPTUAL | discuter / préparer / cadrer | tout déploiement |
| `DIAGNOSTIC_READY` (+ BLOCKED_OWNER / STOP_LOW_VALUE / STOP_TOO_COMPLEX) | DIAGNOSTIC | mesurer / auditer / produire preuves | mutations |
| `PARTIAL_READY` (+ FIX_AND_RETEST / ROLLBACK_REQUIRED) | **CONTINUE_LIMITED** | PR, pilot, manual gate, test cas réel, correction, observation friction | scale, ratchet, automatisation large, mutations irréversibles, promotion masse |
| `OPERATIONAL_READY` (+ PASS) | STABLE | usage comme processus stable | scale large sans validation préalable |
| `SCALE_READY` | SCALE | automatiser, généraliser, ratchet, blocking CI | — |

**Formule canon :** *« PARTIAL_READY = avancer sans scaler. OPERATIONAL_READY = stabiliser. SCALE_READY = généraliser. »*

### Phrases canon à graver

> *« La doctrine d'amélioration continue ne doit pas être un nouveau système. Elle doit être un filtre léger appliqué à tous les systèmes existants. »*

> *« Phase 1 doit prouver que le filtre améliore les décisions. Phase 2 automatise seulement ce qui est répété et utile. Phase 3 est interdite sans amendement vault séparé (Voie 3 — INC-2026-016). »*

> *« Chaque amélioration doit être utile, mesurable et bornée. Sinon, elle devient elle-même une dette. »*

> *« ADR-082 est advisory, perpétuellement. Toute promotion vers blocking exige un amendement vault G3-signed séparé. Owner GO seul ne suffit pas. »* (Voie 3, post-INC-2026-016)

## Conséquences

### Positives

- Doctrine canonique courte ratifiée vault (statut advisory clair, pas ambigu)
- Application opt-in via skill + template optional → pas de friction systémique
- Output machine-readable format si rapport produit
- Hiérarchie explicite priorités → pas de décisions au feeling
- Leçon INC-2026-016 codée en dur dans la doctrine elle-même (anti-récidive)
- Compatible canon existant (ADR-013, ADR-031, ADR-058, ADR-060)

### Négatives / coûts

- Adoption volontaire = pas garantie d'utilisation systématique (acceptable Voie 3)
- Risque de désuétude si jamais appliqué (atténué par INC-2026-016 visibilité + skill load)
- Toute promotion future = friction (amendement vault G3 séparé) — intentionnel, voulu

## Alternatives rejetées

- **Voie 1 (ratification brute, blocking dès Phase 3)** — rejetée car laisse owner GO seul comme verrou ; insuffisant après leçon INC-2026-016.
- **Voie 2 (rejet total)** — rejetée car le travail de doctrine v15.4 a une valeur réelle (filtre 6 questions, hiérarchie P1-P6, anti-complexité) ; perdre ça serait jeter le bébé avec l'eau du bain.
- **ADR par amélioration** — multiplie les vault PRs, casse simplicité, viole `complexity-gravity` ADR-081.
- **Doctrine 2700+ lignes en memory privée** — viole anti-complexité, pas auditable humain.
- **Nouvel agent "Amélioration globale"** — nouvelle couche sans preuve (anti-pattern "Prefer extension over creation").
- **Hardcoder règles dans CLAUDE.md** — viole "pointer vault uniquement" CLAUDE.md §Gouvernance + viole ADR-060.

## Pilotes empiriques

- `audit/pilot-filtre-a-air-2026-05-26.md` + `pilot-filtre-a-air-2026-05-26.verdict.json` = première application
- `audit/pilot-memory-md-compaction-2026-05-26.verdict.json` = second pilote (cross-domain check)
- Verdicts respectifs : `PARTIAL_READY` (les deux), confirmant la sémantique CONTINUE_LIMITED

## Références

- [ADR-013](./ADR-013-agent-lifecycle-governance.md) (vault SoT)
- [ADR-015](./ADR-015-vault-single-source-of-truth.md) (signed commits G3)
- [ADR-031](./ADR-031-four-layer-content-architecture.md) (four-layer content architecture)
- [ADR-033](./ADR-033-wiki-gamme-schema-v200.md) (wiki gamme schema v2.0.0)
- [ADR-058](./ADR-058-repository-control-plane.md) (Repository Control Plane 3 couches)
- [ADR-060](./ADR-060-repository-roles-doctrine.md) (Repository roles doctrine — leçon principale ADR-082 amendement Voie 3)
- [ADR-062](./ADR-062-repository-contract-system-meta-model.md) (Repository Control Plane runtime)
- [ADR-081](./ADR-081-doctrine-agility-amendments.md) (Sunset Clause + Exploration Budget — pattern complexity-gravity)
- [INC-2026-016](../incidents/2026/2026-05-27-monorepo-pr765-adr082-authority-drift.md) (authority drift incident — source directe amendement Voie 3)
- CLAUDE.md §Anti-bricolage + §Discipline de périmètre + §Heuristiques de décision

## Commit signing (G3 ADR-015)

PR vault doit être commit-signed G3 selon ADR-015 :

```
feat(adr): add ADR-082 lightweight advisory improvement doctrine (Voie 3, post INC-2026-016)

Amendement de la draft v15.4 du 2026-05-26 suite à incident d'authority drift
INC-2026-016 (monorepo PR #765 déclarait "canon ADR-082" avant ratification).

Décision : ratification Voie 3 — advisory perpétuel, jamais blocking par défaut.
Toute promotion future vers blocking exige amendement vault séparé (owner GO
seul insuffisant). Phase 4 originelle (adoption obligatoire) supprimée.

References: ADR-013, ADR-015, ADR-031, ADR-033, ADR-058, ADR-060, ADR-081.
Source incident: INC-2026-016.
Pilotes: audit/pilot-filtre-a-air-2026-05-26.* + pilot-memory-md-compaction-*.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
Signed-off-by: @fafa <automecanik.seo@gmail.com>
```
