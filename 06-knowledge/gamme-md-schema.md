# Schema gamme.md v4 — Architecture 5 blocs

> Source de verite pour la structure des fichiers `/opt/automecanik/rag/knowledge/gammes/*.md`
>
> Consommateurs : pipeline R4 (`reference.service.ts`), skill `/seo-content-architect` Phase 1d, validateur batch (`scripts/validate-gamme-schema.ts`)

## Vue d'ensemble

```
gamme.md (YAML frontmatter + markdown body)
├── Meta (identite)           → routing, indexation, priorite
├── _sources (provenance)     → tracabilite E-E-A-T
├── domain (Bloc A)           → __seo_reference
├── selection (Bloc B)        → __seo_gamme_purchase_guide
├── diagnostic (Bloc C)       → __seo_reference + purchase_guide
├── maintenance (Bloc D)      → __seo_gamme_purchase_guide
├── installation (Bloc E)     → __seo_reference.content_html
├── rendering                 → __seo_gamme_purchase_guide
├── seo_cluster (optionnel)   → meta SEO
└── Markdown body             → genere par skill depuis blocs B-E
```

---

## Detection de version

Le pipeline detecte la version via `quality.version` :

| Version | Structure | Parser |
|---------|-----------|--------|
| `GammeContentContract.v1` ou absent | page_contract flat | `parseRagGammeFile()` legacy |
| `GammeContentContract.v3` | page_contract enrichi | `parseRagGammeFile()` legacy |
| `GammeContentContract.v4` | 5 blocs | `parseRagGammeFileV4()` |

Coexistence pendant migration. Pas de regression sur v1/v3.

---

## Meta (identite)

```yaml
# ── Tous REQUIS ──
category: string              # famille metier (freinage, filtration, accessoires...)
slug: string                  # identifiant URL (= pg_alias)
title: string                 # nom affiche
pg_id: integer                # FK pieces_gamme
source_type: "gamme"          # fixe
doc_family: "catalog"         # fixe
truth_level: "L1"|"L2"       # L1=expert valide, L2=auto+valide
updated_at: date              # YYYY-MM-DD
verification_status: "draft"|"verified"

intent_targets: string[]      # sous-ensemble de: diagnostic, achat, entretien, reference, compatibilite

# ── Priorite business ──
business_priority: "high"|"medium"|"low"
priority_signals:             # OPTIONNEL
  avg_basket: number          # panier moyen EUR
  monthly_searches: number    # volume recherche mensuel
  margin_tier: "high"|"medium"|"low"

# ── Lifecycle ──
lifecycle:
  stage: "auto_generated"|"v4_converted"|"skill_enriched"|"expert_reviewed"|"published"
  last_enriched_by: string    # "reindex"|"skill:seo-content"|"manual:admin"
  last_enriched_at: date      # YYYY-MM-DD
```

### Intent routing

| Intent | Blocs priorises |
|--------|----------------|
| achat | B (selection) + rendering |
| diagnostic | C (diagnostic) + A (domain) |
| entretien | D (maintenance) + C (diagnostic) |
| reference | A (domain) + B (selection) |
| compatibilite | B (selection) |

---

## Provenance (_sources)

```yaml
# ── OPTIONNEL — au niveau racine ──
_sources:
  {cle_unique}:
    type: "manufacturer"|"norm"|"field-expertise"|"study"|"rag-doc"
    doc: string|null          # chemin fichier RAG ou null
    note: string              # contexte si pas de doc
```

**Usage** : tout champ factuel peut ajouter `source: "{cle}"` inline.

**Hard gate** : chiffre precis dans `arguments` sans `source_ref` → `UNSOURCED_CLAIM` (BLOCK).

---

## Bloc A — Domain (identite metier)

```yaml
domain:
  # ── REQUIS ──
  role: string                # >80 chars, pas de verbe generique
  must_be_true: string[]      # min 2
  must_not_contain: string[]  # min 1
  confusion_with:             # min 2 : piece proche + cause externe
    - term: string
      difference: string

  # ── OPTIONNEL ──
  related_parts: string[]
  norms: string[]

  # ── Cross-gamme ──
  cross_gammes:               # OPTIONNEL
    - slug: string
      relation: "always_together"|"check_on_replace"|"part_of_kit"|"alternative"|"causes_wear_on"
      context: string
```

**DB** : `__seo_reference` (role_mecanique, confusions_courantes, regles_metier)

### Types de relation cross-gamme

| Type | Signification | Exemple |
|------|---------------|---------|
| `always_together` | Toujours remplaces ensemble | disque ↔ plaquette |
| `check_on_replace` | A verifier au remplacement | disque → etrier |
| `part_of_kit` | Composant d'un kit | courroie → kit-distribution |
| `alternative` | Piece alternative | ampoule-H7 ↔ kit-LED-H7 |
| `causes_wear_on` | Accelere l'usure de | disque-voile → plaquette |

---

## Bloc B — Selection (guide d'achat)

```yaml
selection:
  # ── REQUIS ──
  criteria: string[]          # min 3 — specifiques a la gamme
  checklist: string[]         # min 3 — etapes avant commande
  anti_mistakes: string[]     # min 3 — erreurs d'ACHAT uniquement
  cost_range:
    min: number
    max: number
    currency: "EUR"
    unit: string              # "la paire"|"par essieu"|"l'unite"|"le kit"
    source: string|null

  # ── OPTIONNEL ──
  compatibility_notes: string
  brands:
    premium: string[]
    equivalent: string[]
    budget: string[]
```

**DB** : `__seo_gamme_purchase_guide` (howToChoose, antiMistakes, price tiers)

**Hard gate** : `cost_range.max > 10 * cost_range.min` → `SUSPECT_PRICE_RANGE` (BLOCK)

---

## Bloc C — Diagnostic

```yaml
diagnostic:
  # ── REQUIS ──
  symptoms:                   # min 3
    - id: string              # S1, S2... (stable)
      label: string
      severity: "confort"|"securite"|"immobilisation"
  causes: string[]            # min 2 — ordonnees par frequence
  quick_checks: string[]      # min 2 — tests sans outil

  # ── OPTIONNEL ──
  workshop_checks: string[]
  escalation: string
  immediate_replace: string[]
```

**DB** : `__seo_reference.symptomes_associes` + `__seo_gamme_purchase_guide.symptoms`

### Niveaux de severity

| Niveau | Signification | Exemple |
|--------|---------------|---------|
| `confort` | Pas urgent, gene d'usage | Traces essuie-glace |
| `securite` | Faire controler rapidement | Vibrations freinage |
| `immobilisation` | Vehicule inutilisable | Embrayage patine completement |

---

## Bloc D — Maintenance

```yaml
maintenance:
  # ── REQUIS ──
  interval:
    value: string             # "60000-80000"|"6-12"|"selon constructeur"
    unit: "km"|"mois"|"condition"
    note: string              # condition critique
    source: string|null

  # ── REQUIS si unit != "km" ──
  usage_factors: string[]

  # ── OPTIONNEL ──
  good_practices: string[]
  do_not: string[]            # interdits d'ENTRETIEN uniquement
  wear_signs: string[]
```

**DB** : `__seo_gamme_purchase_guide` (sgpg_timing_km, sgpg_timing_years)

**Hard gate** : `unit != "km" AND usage_factors absent` → `MISSING_USAGE_FACTORS` (WARN)

---

## Bloc E — Installation (OPTIONNEL)

```yaml
# ── Bloc entierement ABSENT si non applicable ──
installation:
  # ── REQUIS si present ──
  difficulty: "facile"|"moyen"|"expert"
  time: string
  tools: string[]             # [] si aucun
  steps: string[]             # min 3
  post_checks: string[]       # min 1
  common_errors: string[]     # min 2 — erreurs MONTAGE uniquement

  # ── OPTIONNEL ──
  prerequisite: string
  pro_only: boolean
  pro_reason: string
```

**DB** : `__seo_reference.content_html` (section installation)

**Regle** : `difficulty: "expert"` implique `pro_only: true`

### Applicabilite par type de gamme

| Type | Bloc E | Raison |
|------|--------|--------|
| Freinage (disque, plaquette) | REQUIS | Securite, procedure specifique |
| Filtration (filtre huile, air) | Optionnel | Montage generalement simple |
| Eclairage (ampoule) | Optionnel | Trivial pour la plupart |
| Fluides (huile, liquide) | ABSENT | Pas de montage physique |
| Complexe (embrayage, turbo) | REQUIS + pro_only | Expert obligatoire |

---

## Rendering (couche de rendu)

```yaml
rendering:
  # ── REQUIS ──
  pgId: string
  intro_title: string
  risk_title: string
  risk_explanation: string
  risk_consequences: string[]
  risk_conclusion: string
  arguments:
    - title: string
      icon: string            # lucide-react
      source_ref: string|null # REQUIS si chiffre cite

  # ── GENERE PAR SKILL ──
  faq:
    - question: string
      answer: string

  # ── Schema.org mapping ──
  schema_org:
    - type: "FAQPage"
      source_bloc: rendering
    - type: "HowTo"           # si installation present
      source_bloc: E
    - type: "Product"
      source_bloc: B

  # ── REQUIS ──
  quality:
    score: integer            # 0-100
    source: string
    version: "GammeContentContract.v4"
```

**DB** : `__seo_gamme_purchase_guide` (intro, risk, arguments, faq)

---

## SEO Cluster (optionnel)

```yaml
seo_cluster:
  source: "keyword-dataset"|"gsc"|"manual"
  updated_at: date
  primary_keyword: {text, sd, traffic_range, intent}
  keyword_variants: [{keyword, sd, intent, competition}]
  paa_questions: string[]
```

---

## Separation des types d'erreurs

| Type d'erreur | Bloc | Champ |
|---------------|------|-------|
| Erreur d'ACHAT | B | `selection.anti_mistakes` |
| Erreur de MONTAGE | E | `installation.common_errors` |
| Interdit d'ENTRETIEN | D | `maintenance.do_not` |
| Terme interdit CONTENU | A | `domain.must_not_contain` |
| Consequence NON-REMPLACEMENT | rendering | `risk_consequences` |

---

## Scoring v4

### Grille (score 0-100, non-lineaire)

| Bloc | Critere | Type | Penalite |
|------|---------|------|----------|
| A | `role` > 80 chars ET pas generique | BLOCK | -10 |
| A | `confusion_with` >= 2 | WARN | -3 |
| A | `must_be_true` >= 2 | WARN | -3 |
| B | `criteria` >= 3 | WARN | -3 |
| B | `cost_range` objet ET max < 10*min | BLOCK | -10 |
| B | `anti_mistakes` >= 3 | WARN | -3 |
| B | `checklist` >= 3 | WARN | -3 |
| C | `symptoms` >= 3 avec severity | WARN | -3 |
| C | `causes` >= 2 | WARN | -3 |
| C | `quick_checks` >= 2 | WARN | -3 |
| D | `interval` present avec note | WARN | -3 |
| D | `usage_factors` si unit != km | WARN | -3 |
| E | present avec >= 3 steps | BONUS | +5 |
| R | pas de chiffre sans source_ref | BLOCK | -10 |
| R | `faq` >= 4 | WARN | -3 |
| cross | `cross_gammes` >= 1 | BONUS | +3 |
| prov | `_sources` >= 1 | BONUS | +2 |

**Calcul** : `score = max(0, min(100, 100 - penalties + bonuses))`

### Seuils

| Score | Statut | Action pipeline |
|-------|--------|----------------|
| 0-39 | FAIL | Draft force, skill recommande en urgence |
| 40-69 | WARNING | Draft, enrichissement recommande |
| 70-84 | OK | Draft, auto-publish possible apres gates |
| 85-100 | GOOD | Auto-publish |

### Patterns generiques detectes (BLOCK)

```
/joue un r[oô]le essentiel/i
/Son entretien r[eé]gulier garantit/i
/assure le bon fonctionnement/i
/permet de garantir/i
/est un [eé]l[eé]ment (essentiel|important|cl[eé])/i
```

---

## DB Mapping complet

| Bloc | Table | Colonnes |
|------|-------|----------|
| A domain | `__seo_reference` | role_mecanique, confusions_courantes, regles_metier |
| B selection | `__seo_gamme_purchase_guide` | howToChoose = criteria.join, antiMistakes, price columns |
| C diagnostic | `__seo_reference` + purchase_guide | symptomes_associes + symptoms |
| D maintenance | `__seo_gamme_purchase_guide` | sgpg_timing_km, sgpg_timing_years |
| E installation | `__seo_reference` | content_html (section) |
| rendering | `__seo_gamme_purchase_guide` | intro, risk, arguments, faq |
| cross_gammes | `__seo_gamme_purchase_guide` | sgpg_related_gammes (JSONB) |

---

## Template markdown body

Genere par le skill `/seo-content-architect` depuis les blocs YAML.

```markdown
# {title}

## Reference technique            ← domain.role + domain.norms + selection.criteria
### Types et variantes
### Normes et specifications
### Pieces associees              ← domain.related_parts + cross_gammes

## Diagnostic                     ← diagnostic.*
### Symptomes specifiques         ← tableau severity
### Causes probables              ← liste ordonnee %
### Tests simples                 ← quick_checks
### Tests atelier                 ← workshop_checks (si present)

## Guide d'achat                  ← selection.*
### Criteres de choix             ← 1 sous-section par critere
### Marques recommandees          ← brands (si present)
### Check-list avant commande     ← checklist
### Erreurs a eviter              ← anti_mistakes

## Entretien                      ← maintenance.*
### Intervalles                   ← interval
### Signes d'usure                ← wear_signs (si present)
### Bonnes pratiques              ← good_practices (si present)

## Installation                   ← installation.* (si bloc present)
### Prerequis et outils           ← prerequisite + tools
### Procedure                     ← steps
### Verifications post-montage    ← post_checks
### Erreurs de montage            ← common_errors
```

Chaque section est **absente** si le bloc source n'est pas present ou est vide.

---

## Lifecycle stages

```
auto_generated → v4_converted → skill_enriched → expert_reviewed → published
```

| Stage | Description | Qui |
|-------|-------------|-----|
| `auto_generated` | Genere par reindex, qualite ~76 | Script reindex |
| `v4_converted` | Structure v4 appliquee, donnees nettoyees | Skill Phase 1d ou manuel |
| `skill_enriched` | Contenu genere par skill | `/seo-content-architect` |
| `expert_reviewed` | Valide par admin | Manuel |
| `published` | Publie en production | Pipeline auto-publish |
