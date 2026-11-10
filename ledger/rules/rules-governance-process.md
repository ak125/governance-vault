# Rules - Governance Process (G5-G10)

> Regles de gouvernance processus au 2026-11-01 (G5 reecrite par [[ADR-101-vault-decides-canon-authority|ADR-101]], amendee par [[ADR-118-retrait-methodes-bmad-superpowers-spec-kit|ADR-118]] et par [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]])
> **Version**: 3.2.2 | **Status**: CANON (regle du vault, normative au sens de G1)
> **Taxonomie**: G = Governance (G1-G4 = vault dans rules-vault.md, G5-G10 = processus ici)
> **Complement de:** rules-technical.md (T1-T7 = technique, G5+ = processus)

---

## G5: Autorite Documentaire

**OBLIGATOIRE:** Une decision ne se tire que d'une source qui fait autorite
(ADR-101 D1-D2). En cas de conflit, l'ordre est celui du tableau.

| Source | Autorite |
|--------|----------|
| ADR du vault `status: accepted` ou `accepted-revised` sans `superseded_by` actif (ADR-121 D6), regles `ledger/rules/rules-*.md` | Decide |
| `.spec/00-canon/**` du monorepo consomme par du code, un generateur ou un check CI (contrat, ADR-062) | Fait foi dans son domaine ; ne contredit pas un ADR accepte |
| `.spec/00-canon/**` du monorepo sans consommateur (prose de reference) | Aide a comprendre ; ne tranche aucun conflit, quel que soit son en-tete |
| ADR `proposed`, `deferred`, `rejected`, `deprecated` ou `superseded` | Contexte historique ; jamais une justification d'implementation |
| `.spec/features/*` | Supplementaire - peut etre obsolete |

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

**OBLIGATOIRE:** Un document obsolete est marque ou archive explicitement. Il
ne reste jamais en place sans signal.

| Document | Traitement |
|----------|------------|
| ADR, regle `rules-*.md` ou policy du vault | Reste a son emplacement. Son `status` passe a `superseded` ou `deprecated`, et `superseded_by` nomme le remplacant. |
| Autre document du vault | Deplace dans `ledger/_archive/` avec `status: archived`, et inscrit dans `ledger/_archive/INDEX-archive.md` avec la raison. Une note gardee comme trace historique peut rester en place si elle s'ouvre sur un bandeau qui la dit remplacee, nomme le texte qui fait foi et interdit de l'executer. |
| Document du monorepo | Traite selon la cloture Q1 de [[rules-engineering-quality]] : supprime, suivi, ou conserve avec une justification ecrite. |

Dans tous les cas :

- aucune MOC ni aucun INDEX ne le presente plus comme courant ;
- il sort du corpus RAG.

**Controle:** `python3 _scripts/check-obsolete-rules.py` signale un ADR, une
regle ou une policy `deprecated` ou `superseded` sans remplacant nomme, et un
fichier de `ledger/_archive/` sans `status: archived`.

**Historique:** jusqu'a la version 3.2.0, G8 renvoyait a `.spec/.archive/` et a
`deprecation_ledger.md`. Le dossier a ete supprime du monorepo le 2026-02-28 ;
le fichier n'existe ni dans le vault ni dans le monorepo.

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

**Effet de l'expiration** : un verdict expire et non renouvele ne justifie plus un blocage. Les `DO_NOT_START` qu'il bloque passent de `blocked` a `OPEN_FOR_REVIEW` a la date `expires_at`. `OPEN_FOR_REVIEW` signifie qu'un nouveau debat est requis avant toute action ; l'entree ne devient pas une priorite.

**Constat de l'expiration : manuel.** Aucun automatisme n'execute ce passage. `scripts/governance/check-verdict-expirations.sh` (monorepo) lit `ledger/verdicts/*.md` et classe chaque verdict `OK`, `SOON` (moins de 14 jours) ou `EXPIRED` : il produit un rapport, sort toujours en 0, n'ecrit pas dans `__seo_event_log` et ne modifie aucune liste `DO_NOT_START`. Aucun cron ni workflow ne le planifie. La planification hebdomadaire et l'alerte prevues par [[ADR-081-doctrine-agility-amendments|ADR-081]] n'ont pas ete livrees (ecart consigne dans sa reconciliation du 2026-11-10) ; tant qu'elles ne le sont pas, l'expiration se constate en lancant ce script a la main.

### Precedent

Le verdict [[2026-05-20-conversion-funnel-organic]] (VERDICT-2026-001, PR #652, value=0.0017, mesure du 2026-05-20) porte son header YAML avec `expires_at: 2026-08-12`. Il a expire a cette date : aucun verdict de renouvellement n'existe dans `ledger/verdicts/`. Les 3 `DO_NOT_START` qu'il bloquait (`r5-diagnostic-engine`, `new-seo-platform`, `new-meta-architecture-adr`) sont donc en `OPEN_FOR_REVIEW`. Refaire la mesure ou rouvrir le debat revient a l'owner (reconciliation d'[[ADR-081-doctrine-agility-amendments|ADR-081]]).

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

Avant tout deliverable:

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

_Derniere mise a jour: 2026-11-10 (3.2.2 : G9 decrit le constat manuel de l'expiration, titre G5-G10 ; 3.2.1 : G8, mecanismes d'archivage existants ; aucune decision changee). Precedente : 2026-11-01 (ADR-121)_
_Status: CANON - Complement de rules-technical.md_
