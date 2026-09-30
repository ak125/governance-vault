# Rules - Governance Process (G5-G8)

> Regles de gouvernance processus au 2026-10-01 (G5 reecrite par [[ADR-101-vault-decides-canon-authority|ADR-101]])
> **Version**: 3.0.0 | **Status**: CANON (regle du vault, normative au sens de G1)
> **Taxonomie**: G = Governance (G1-G4 = vault dans rules-vault.md, G5-G8 = processus ici)
> **Complement de:** rules-technical.md (T1-T7 = technique, G5+ = processus)

---

## G5: Autorite Documentaire

**OBLIGATOIRE:** Une decision ne se tire que d'une source qui fait autorite
(ADR-101 D1-D2). En cas de conflit, l'ordre est celui du tableau.

| Source | Autorite |
|--------|----------|
| ADR du vault `status: accepted` sans `superseded_by` actif, regles `ledger/rules/rules-*.md` | Decide |
| `.spec/00-canon/**` du monorepo consomme par du code, un generateur ou un check CI (contrat, ADR-062) | Fait foi dans son domaine ; ne contredit pas un ADR accepte |
| `.spec/00-canon/**` du monorepo sans consommateur (prose de reference) | Aide a comprendre ; ne tranche aucun conflit, quel que soit son en-tete |
| ADR `proposed`, `deprecated` ou `superseded` | Contexte historique ; jamais une justification d'implementation |
| `.spec/features/*` | Supplementaire - peut etre obsolete |
| `_bmad-output/*` | Artefacts versionnes - read-only |

**Divergence** entre une decision et l'etat du depot : c'est un constat, a
signaler, puis a resoudre par une PR de code ou un ADR d'amendement (ADR-101 D3).
Jamais appliquee a l'aveugle, jamais ignoree.

**Raison:** Prevenir la confusion documentaire et garantir une source de decision unique.

---

## G6: Proof Requirements (Anti-BS Rule)

**OBLIGATOIRE:** Chaque claim "fait" doit inclure preuves.

```bash
# Preuves requises pour tout deliverable
ls -lah <fichier>           # Existence + taille
sha256sum <fichier>         # Hash integrite
head -n 25 <fichier>        # Apercu contenu
git status --porcelain      # Etat git
```

| Claim | Preuve requise |
|-------|---------------|
| "Fichier cree" | ls -lah + sha256sum |
| "Contenu modifie" | git diff |
| "Migration appliquee" | psql query result |
| "Test passe" | curl output |

**Raison:** Eliminer les claims sans verification. "Trust but verify" → "Verify first".

---

## G7: RAG Corpus Alignment

**OBLIGATOIRE:** RAG corpus reference UNIQUEMENT documents valides.

| Regle | Valeur |
|-------|--------|
| PROD Namespace | `knowledge:faq` UNIQUEMENT |
| truth_level requis | L1 ou L2 obligatoire |
| RAG status | **OFF jusqu'a golden tests 100%** |
| Gating | Score < 0.70 = REFUSE |

**Kill Switches actifs:**
- `AI_PROD_WRITE=false` - Bloque ecriture IA en prod
- `NAMESPACE_GUARD=knowledge:faq` - Limite namespace PROD
- `MIN_SCORE_THRESHOLD=0.70` - Refuse reponses incertaines

**Raison:** Prevenir hallucinations et reponses hors-sujet du RAG.

---

## G8: Obsolete Handling

**OBLIGATOIRE:** Documents obsoletes doivent etre explicitement archives.

```
Document identifie comme obsolete
      ↓
Deplacement vers .spec/.archive/
      ↓
Entry dans deprecation_ledger.md
      ↓
Retrait de tout INDEX
      ↓
Exclusion du corpus RAG
```

| Action | Commandes |
|--------|-----------|
| Archiver | `mv .spec/features/xxx.md .spec/.archive/` |
| Logger | Ajouter entry dans `deprecation_ledger.md` |
| Verifier | `grep -r "xxx.md" .spec/` doit retourner 0 resultats |

**Raison:** Prevenir l'empoisonnement du contexte par documents perimes.

---

## G9: Sunset Clause sur verdicts empiriques (ADR-081)

**Regle canonique**

> Tout verdict empirique cite comme justification d'un `DO_NOT_START`, d'un pivot strategique ou d'une priorite `TOP` **expire 12 semaines apres sa date de mesure**, sauf renouvellement explicite par re-instrumentation et nouveau commit verdict.

### Implementation

**Header YAML obligatoire** dans tout fichier verdict empirique (`ledger/verdicts/YYYY-MM-DD-<topic>.md`) — voir [[empirical-verdict-header]] :

```yaml
---
id: VERDICT-YYYY-NNN
metric: <metric_slug>
value: <numeric_value>
measured_at: YYYY-MM-DD
expires_at: YYYY-MM-DD   # measured_at + 12 weeks
methodology: "<methodologie courte>"
pr_ref: <pr_number>
blocks_until_expiry: [<slug_1>, <slug_2>]
---
```

**Escalation automatique** : verdict expire non-renouvele → les `DO_NOT_START` qu'il bloque passent de `blocked` a `OPEN_FOR_REVIEW` automatiquement. Mecanisme : cron weekly `scripts/governance/check-verdict-expirations.sh` + alerte vers `__seo_event_log` (reutilise observabilite existante, pas de nouveau canary externe).

### Precedent immediat

Le verdict `conversion_funnel` (05-20 PR #652, value=0.0017) doit recevoir son header YAML retroactif avec `expires_at: 2026-08-12`. A cette date sans re-mesure, les 3 `DO_NOT_START` qu'il bloque (`r5-diagnostic-engine`, `new-seo-platform`, `new-meta-architecture-adr`) deviennent `OPEN_FOR_REVIEW`.

### Raison

Sans sunset clause, un verdict mesure 1 fois devient permanent et bloque par effet de cliquet toute exploration paradigmatique. Path-dependency garantie, angles morts non-instrumentes (ex. shift GEO 2026). 12 semaines = 1 trimestre = cadence naturelle de business review.

---

## G10: Exploration Budget alloue (ADR-081)

**Regle canonique**

> La doctrine canon reserve un slot machine-readable `EXPLORATION_BUDGET` dans `top-priorities.md` (max 3 entrees, 1 active a la fois). Toute probe strategique legere (≤ 5 jours-agent total, measurement-only) peut occuper ce slot sans PR vault prealable, a condition de respecter le scope lint + livrer un rapport empirique.

### Implementation

**Nouveau slot dans `top-priorities.md`** :

```
## EXPLORATION_BUDGET
- <probe-slug-active>
```

Max 3 entrees historiques (rolling), 1 entree active. Bornes enforced par `scripts/governance/validate-top-priorities.sh`.

**Scope strict** (enforced par `scripts/governance/validate-exploration-probe.sh` au PR final, **single check**, pas per-checkpoint) :

- ≤ 5 jours-agent total
- Measurement only : aucune nouvelle table production, aucun service NestJS, aucun admin UI, aucune migration DB, aucune modification R-role / `@repo/seo-roles`
- Lecture seule sur tables existantes
- Output unique = 1 rapport markdown final `docs/research/YYYY-MM-DD-<topic>-empirical-report.md` avec chiffrage € ou abandon explicite

**Trigger** : owner ou agent senior peut ouvrir une probe sans PR vault. La doctrine pre-autorise dans la bande. Le PR final (a la closure) est reviewable normalement.

### G10.X — Anti-patterns explicites (anti `complexity-gravity`)

**Governance cost ratio ≤ 20%** : invariant non-negociable. Le temps total passe a planifier/gouverner une probe ne doit pas exceder 20% du temps d'execution. Test simple au demarrage : "le plan tient sur 1 page A4 ? oui = ratio OK, non = simplifier."

Anti-patterns interdits sur toute probe `EXPLORATION_BUDGET` :

| Anti-pattern | Correction |
|---|---|
| 3 slots `EXPLORATION_BUDGET` separes par sous-checkpoint | 1 slot unique, work breakdown interne |
| 3 rapports partiels | 1 rapport final avec sections |
| Lint AST par sous-checkpoint | Single check au PR final via `validate-exploration-probe.sh` |
| Pre-construire admin UI / table / service "au cas ou signal positif" | Viole scope `measurement-only`, abort + cycle separe |
| Reflexe d'ajouter Reality Audit / nouvelle ceremonie | Voir `complexity-gravity` — ajouter seulement quand besoin empirique manifeste |

### Raison

Avant G10, toute divergence strategique exigeait PR vault + debat de cadrage (frottement social eleve). Observe : 11 rounds de brainstorm pour decider d'investir 5 jours dans un probe empirique. Cout de gouvernance > cout d'execution = anti-pattern direct. G10 pre-autorise dans la bande pour debloquer la velocite exploratoire sans casser les garde-fous structurels.

---

## Checklist Governance

Avant tout workflow BMAD:

- [ ] Sources qui font autorite uniquement, divergences signalees (G5)
- [ ] Claims avec preuves (G6)
- [ ] RAG alignment verifie (G7)
- [ ] Obsolete archive (G8)
- [ ] Verdicts empiriques portent header YAML + `expires_at` (G9)
- [ ] Probe `EXPLORATION_BUDGET` respecte scope `measurement-only` + ratio ≤ 20% (G10)

Apres chaque deliverable:

- [ ] sha256sum genere
- [ ] git status propre
- [ ] INDEX.md mis a jour si applicable

---

## References

- **rules-technical.md** - T1-T7: Regles techniques code
- **rules-ai-cos.md** - AI1-AI10: Regles d'or agents IA
- **rules-vault.md** - G1-G4: Regles de gouvernance du vault
- **architecture.md** - Architecture NestJS/Remix/Supabase
- **repo-map.md** - Structure monorepo

---

_Derniere mise a jour: 2026-10-01 (ADR-101)_
_Status: CANON - Complement de rules-technical.md_
