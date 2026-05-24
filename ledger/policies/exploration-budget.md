---
type: policy
status: canon
rule: G10
source_adr: ADR-081
updated: 2026-05-24
related_rules:
  - rules-governance-process
related_templates:
  - exploration-probe-report.md.tmpl
  - empirical-verdict.yaml.tmpl
---

# Policy : Exploration Budget (G10 exec contract)

> **Statut** : Actif des merge ADR-081
> **Enforcement** : `scripts/governance/validate-exploration-probe.sh` (CI, single check au PR final)
> **Regle canonique** : [[rules-governance-process]] G10

---

## Principe

La doctrine canon reserve un slot pre-autorise pour les probes empiriques strategiques legeres. Objectif : decoupler la velocite exploratoire (mesurer une opportunite en 5 jours) du cycle gouvernance complet (PR vault + ADR + debat). Sans casser les garde-fous structurels.

---

## Eligibilite d'une probe

Une initiative est eligible au slot `EXPLORATION_BUDGET` si **TOUS** les criteres sont satisfaits :

| Critere | Seuil |
|---|---|
| Duree totale | ≤ 5 jours-agent |
| Type d'output | Rapport markdown empirique chiffre (€/mois ou abandon explicite) |
| Touche prod tables ? | NON |
| Touche services NestJS ? | NON |
| Touche admin UI ? | NON |
| Touche migrations DB ? | NON |
| Touche R-roles / @repo/seo-roles ? | NON |
| Lecture seule des tables existantes ? | OUI |
| Plan tient sur 1 page A4 ? | OUI |

Une initiative qui echoue un seul critere = **pas eligible** → cycle complet brainstorm → spec → plan → PR vault.

---

## Slot `top-priorities.md`

```
## EXPLORATION_BUDGET
- <probe-slug-active>
```

**Bornes** : max 3 entrees historiques (rolling) + max 1 entree active a la fois. Enforced par `scripts/governance/validate-top-priorities.sh`.

**Naming convention** : `<topic>-probe-YYYY-MM` (ex. `geo-discovery-probe-2026-05`).

**Cycle de vie** :

1. Owner / agent senior ajoute le slug a la section `EXPLORATION_BUDGET`.
2. Probe demarre (worktree dedie, branche `feat/<probe-slug>`).
3. A la closure : slug deplace vers historique (commit log + report archive).

---

## Anti-patterns explicites (anti `complexity-gravity`)

### Governance cost ratio ≤ 20%

Invariant non-negociable. Le temps total passe a planifier/gouverner une probe ne doit pas exceder 20% du temps d'execution.

**Test simple au demarrage** : "le plan tient sur 1 page A4 ? oui = ratio OK, non = simplifier."

Si a n'importe quel moment le ratio depasse 20%, c'est `complexity-gravity` → couper le scope, pas ajouter de la ceremonie.

### Decoupage interdit

Une probe est **1 slot, 1 work breakdown interne** (B1/B2/B3...), pas N slots. Decoupage interdit :

- ❌ 3 slots `EXPLORATION_BUDGET` separes par sous-checkpoint
- ❌ 3 rapports partiels (1 par sous-checkpoint)
- ❌ Lint AST per-sous-checkpoint
- ❌ Multiples kill-switches gouvernes per-sous-checkpoint

Au lieu de cela :

- ✅ 1 slot unique
- ✅ Work breakdown interne (checkpoints logiques B1 → B2 → B3)
- ✅ 1 rapport final avec N sections
- ✅ Single check au PR final via `validate-exploration-probe.sh`
- ✅ Checkpoint gates = revue PR + naming convention des scripts

### Pre-construction interdite

Pre-construire l'extension produit (admin UI, table, service) "au cas ou signal positif" = viole le scope `measurement-only`. Abort + cycle separe pour le produit si signal le justifie.

### Sequencing conditional encourage

Si un checkpoint dependant (ex. B3 knowledge extraction) n'a de valeur que si un checkpoint precedent (B2) a montre un signal, alors B3 doit etre **conditional** dans le plan, pas systematique. Sinon on construit pour un canal qui n'a pas de signal = coup cognitif inutile.

---

## Lock anti-derive entity-centric (cas typique)

Une probe qui extrait du knowledge (proposals wiki, symptom patterns, failure clusters) **NE DOIT PAS** creer de taxonomies / IDs / entites canoniques en passant. Lock explicite :

- ✅ Output autorise : markdown-only human-readable proposals
- ❌ Output interdit : taxonomies, IDs (symptom_142), graph edges, confidence scores, embeddings, clusters, aliases, normalized entities

Pourquoi : sinon une couche entity-centric implicite se construit en zone grise sans gouvernance, avant d'avoir valide le signal business du canal lui-meme.

---

## Lock anti-overclaim semantique

Tout score / metrique produit par une probe **doit refleter ce qu'il mesure reellement**, pas ce qu'il suggere intuitivement. Exemple historique :

- ❌ "Resolution Confidence" → sonne comme "causal repair truth", "efficacite reparation reelle" → overclaim, derive interpretative
- ✅ "Operational Fulfillment Confidence" → commerce readiness theorique (fitment × supplier × pricing × landing), n'oversells pas la causalite

Discipline : renommer toute metrique dont le nom est plus large que sa mesure reelle.

---

## Workflow type d'une probe (template)

1. **Pre-flight** :
   - Owner ajoute slug a `EXPLORATION_BUDGET` (1 ligne dans `top-priorities.md`)
   - Worktree dedie : `git worktree add ../wt-<slug> -b feat/<slug> origin/main`
   - Plan tient sur 1 page A4

2. **Execution** (≤ 5 jours-agent) :
   - Work breakdown interne (ex. B1 capture → B2 overlay → B3 extraction conditional)
   - Naming convention scripts par responsabilite (ex. `capture.ts` / `compute-X.ts` / `extract-Y.ts`)
   - Checkpoints internes = revue rapide + decision GO/STOP pour suite

3. **Output** :
   - 1 rapport unique `docs/research/YYYY-MM-DD-<topic>-empirical-report.md`
   - Sections = N checkpoints du work breakdown
   - Decision matrix appliquee avec recommandation explicite (escalation produit / arbitrage / close)
   - Conformite template [[exploration-probe-report-template]]

4. **Closure** :
   - PR avec single check `validate-exploration-probe.sh`
   - Slug deplace vers historique
   - Si signal fort → ouverture cycle complet pour produit (brainstorm → spec → plan → PR cycle complet, pas pre-construit)
   - Si signal faible → close + vault doc justifiant (decision empirique)

---

## Verification operationnelle

A la closure d'une probe, verifier :

- [ ] Scope respecte (lint pass)
- [ ] Rapport markdown unique livre
- [ ] Decision matrix appliquee
- [ ] Recommandation explicite (GO produit / arbitrage / close)
- [ ] Slot `EXPLORATION_BUDGET` libere (slug deplace historique)
- [ ] Session-log entry dans `app/log.md`
- [ ] Governance cost ratio verifie ≤ 20%
- [ ] Aucune fuite vers prod (table / service / UI / migration)

---

## References

- ADR-081 (decision source)
- [[rules-governance-process]] G10 (regle canonique)
- [[empirical-verdict-header]] (template G9)
- [[exploration-probe-report-template]] (template G10)
- `scripts/governance/validate-exploration-probe.sh` (lint enforcement)
- `scripts/governance/check-verdict-expirations.sh` (cron G9)

---

_Derniere mise a jour : 2026-05-24_
_Status : CANON des merge ADR-081_
