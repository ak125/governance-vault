# Schema brand.md v1 — Architecture RAG Constructeur

> Source de verite pour la structure des fichiers `/opt/automecanik/rag/knowledge/constructeurs/*.md`
>
> Consommateurs : agent `r7-brand-rag-generator`, pipeline R7 (keyword planner + content batch)
> Pattern : adapte de `gamme-md-schema.md` v4 avec sections R7_ROUTER safe

## Vue d'ensemble

```
brand.md (YAML frontmatter + markdown body)
├── Meta (identite)              → routing, indexation, priorite
├── domain (identite metier)     → contraintes de purete R7
├── S2_MICRO_SEO_ROUTER          → definition + trust proofs (150-220 mots)
├── S3_SHORTCUTS_INTERNAL_LINKS  → ancres maillage interne (struct)
├── S7_COMPATIBILITY_QUICK_GUIDE → 3 etapes + 3 erreurs (80-120 mots)
├── S8_SAFE_TABLE                → tableau verification (6 lignes)
├── S9_FAQ_ROUTER                → 4-6 Q/R safe (120-180 mots)
└── S10_ABOUT_BRAND              → optionnel, max 800 chars
```

Fichier sidecar : `{alias}.role_map.json` (mapping section → role/purete/chunk_kind)

---

## Meta (identite)

```yaml
# ── Tous REQUIS ──
category: constructeur
slug: string                 # = marque_alias (unique dans auto_marque)
brand_id: integer            # FK auto_marque.marque_id
brand_name: string           # nom affiche
doc_family: catalog          # fixe
source_type: constructeur    # fixe (gamme="gamme", vehicle="vehicle")
truth_level: "L1"|"L2"      # L1=OEM source, L2=curated/enrichi
updated_at: date             # YYYY-MM-DD
verification_status: "draft"|"verified"

intent_targets: string[]     # sous-ensemble de: brand_selection, navigational, commercial_investigation
business_priority: "high"|"medium"|"low"

# ── OPTIONNEL ──
pays: string                 # pays d'origine (france, allemagne, japon...)
groupe: string               # groupe industriel (psa-stellantis, bmw-group, renault-nissan...)

# ── Lifecycle ──
lifecycle:
  stage: "v1_generated"|"enriched"|"expert_reviewed"|"published"
  last_enriched_by: string   # "r7-brand-rag-generator"|"manual:admin"
  last_enriched_at: date     # YYYY-MM-DD
```

---

## Domain (identite metier)

```yaml
domain:
  # ── REQUIS ──
  role: string               # >80 chars, description du hub de navigation
  must_be_true: string[]     # min 2 faits veritables
  must_not_contain: string[] # min 5 termes interdits (diagnostic, symptome, tutoriel, montage, reparation)
```

**Regle** : `must_not_contain` doit inclure au minimum les termes de `R7_FORBIDDEN_FROM_R3` + `R7_FORBIDDEN_FROM_R5` (definis dans `r7-keyword-plan.constants.ts`).

---

## Sections markdown

### S2_MICRO_SEO_ROUTER (150-220 mots)

Bloc de texte SEO "safe router". Mentionne la marque, ses modeles populaires, annees, motorisations, "pieces compatibles".

**Chunk kind** : `definition`, `trust_proofs`
**Purity min** : 90
**Interdit** : howto, diagnostic, procedure, imperatif

```markdown
## S2_MICRO_SEO_ROUTER

AutoMecanik propose un catalogue complet de pieces detachees pour {brand_name}...
[150-220 mots, factuel, safe]
```

### S3_SHORTCUTS_INTERNAL_LINKS (structurel)

Liste d'ancres internes vers les gammes et modeles populaires de la marque.

**Chunk kind** : `anchor_list`
**Purity min** : 95
**Format** :

```markdown
## S3_SHORTCUTS_INTERNAL_LINKS

### Gammes populaires {brand_name}
- [Plaquettes de frein {brand_name}](/pieces/plaquettes-de-frein?marque={brand_id})
- [Disque de frein {brand_name}](/pieces/disque-de-frein?marque={brand_id})
- ...

### Modeles populaires
- [{model_name}](/constructeurs/{brand_alias}-{brand_id}/{model_alias}-{model_id}.html)
- ...
```

### S7_COMPATIBILITY_QUICK_GUIDE (80-120 mots)

Guide de compatibilite en 3 etapes + 3 erreurs frequentes. Safe, pas de procedure technique.

**Chunk kind** : `selection_checks`, `anti_mistakes`
**Purity min** : 90

```markdown
## S7_COMPATIBILITY_QUICK_GUIDE

### 3 etapes pour trouver la bonne piece {brand_name}
1. Selectionner le modele exact (ex : Clio IV, Serie 3 F30)
2. Identifier l'annee et la generation du vehicule
3. Verifier la motorisation via le champ D.2 de la carte grise

### 3 erreurs frequentes
- Confondre deux generations d'un meme modele (ex : Clio III vs Clio IV)
- Ignorer la motorisation exacte (diesel/essence/hybride)
- Utiliser une reference OEM sans verifier l'equivalence aftermarket
```

### S8_SAFE_TABLE (structurel, 6 lignes)

Tableau "element a verifier / comment verifier". Generique, applicable a toutes les marques.

**Chunk kind** : `table_row`
**Purity min** : 90
**Interdit** : km precis, howto, imperatif technique

```markdown
## S8_SAFE_TABLE

| Element a verifier | Comment verifier |
|---|---|
| Plaquettes de frein | Epaisseur visible a travers la roue ou temoin d'usure |
| Filtres (air, huile, habitacle) | Carnet d'entretien ou inspection visuelle |
| Batterie | Tension au voltmetre ou demarrage lent |
| Essuie-glaces | Traces sur le pare-brise, caoutchouc craquele |
| Amortisseurs | Rebond excessif, fuite d'huile visible |
| Kit de distribution | Selon preconisation constructeur ou bruit anormal |
```

### S9_FAQ_ROUTER (120-180 mots, 4-6 Q/R)

FAQ orientee compatibilite/selection. Safe, pas de diagnostic.

**Chunk kind** : `faq`
**Purity min** : 90

```markdown
## S9_FAQ_ROUTER

**Q : Comment trouver la bonne piece pour ma {brand_name} ?**
R : Utilisez notre selecteur de vehicule : choisissez votre modele, annee et motorisation pour afficher uniquement les pieces compatibles.

**Q : Les pieces aftermarket sont-elles compatibles avec {brand_name} ?**
R : Oui, les equipementiers comme Bosch, Valeo ou TRW fabriquent des pieces aux normes constructeur, souvent au meme standard que l'OEM.

[4-6 Q/R total]
```

### S10_ABOUT_BRAND (optionnel, max 800 chars)

Court paragraphe neutre et factuel sur le constructeur.

**Chunk kind** : `definition`
**Purity min** : 85

```markdown
## S10_ABOUT_BRAND

{brand_name} est un constructeur automobile fonde en {year} a {city}, {country}.
[Max 800 caracteres, neutre, pas de superlatif]
```

---

## Sidecar role_map.json

Fichier `{alias}.role_map.json` place a cote du `.md` dans le meme repertoire.

```json
{
  "doc_type": "CONSTRUCTEUR",
  "doc_id": "{alias}-{brand_id}",
  "sections": [
    {
      "section_key": "S2_MICRO_SEO_ROUTER",
      "primary_role": "R7_ROUTER",
      "allowed_roles": ["R7_ROUTER"],
      "purity_min": 90,
      "chunk_kind": ["definition", "trust_proofs"]
    },
    {
      "section_key": "S3_SHORTCUTS_INTERNAL_LINKS",
      "primary_role": "R7_ROUTER",
      "allowed_roles": ["R7_ROUTER"],
      "purity_min": 95,
      "chunk_kind": ["anchor_list"]
    },
    {
      "section_key": "S7_COMPATIBILITY_QUICK_GUIDE",
      "primary_role": "R7_ROUTER",
      "allowed_roles": ["R7_ROUTER"],
      "purity_min": 90,
      "chunk_kind": ["selection_checks", "anti_mistakes"]
    },
    {
      "section_key": "S8_SAFE_TABLE",
      "primary_role": "R7_ROUTER",
      "allowed_roles": ["R7_ROUTER"],
      "purity_min": 90,
      "chunk_kind": ["table_row"]
    },
    {
      "section_key": "S9_FAQ_ROUTER",
      "primary_role": "R7_ROUTER",
      "allowed_roles": ["R7_ROUTER"],
      "purity_min": 90,
      "chunk_kind": ["faq"]
    },
    {
      "section_key": "S10_ABOUT_BRAND",
      "primary_role": "R7_ROUTER",
      "allowed_roles": ["R7_ROUTER"],
      "purity_min": 85,
      "chunk_kind": ["definition"]
    }
  ]
}
```

Schema Zod : `backend/src/config/brand-role-map.schema.ts`

---

## Scoring v1

| Critere | Type | Penalite |
|---------|------|----------|
| S2 absent ou < 150 mots | BLOCK | -15 |
| S7 absent ou < 80 mots | BLOCK | -10 |
| S8 absent ou < 4 lignes | WARN | -5 |
| S9 absent ou < 4 Q/R | WARN | -5 |
| S10 > 800 chars | WARN | -3 |
| Terme interdit present (diagnostic, symptome, etc.) | BLOCK | -20 |
| domain.role < 80 chars | WARN | -3 |
| domain.must_not_contain < 5 termes | WARN | -3 |

**Calcul** : `score = max(0, min(100, 100 - penalties))`

| Score | Statut |
|-------|--------|
| 0-49 | FAIL |
| 50-69 | WARNING |
| 70-84 | OK |
| 85-100 | GOOD |

---

## Retrieval (regles d'extraction)

Quand le pipeline R7 genere une page `/constructeurs/{alias}-{id}.html` :

**Filtres** :
- `doc_type == "CONSTRUCTEUR"`
- `brand_id == X` (ou `brand_alias`)
- `primary_role == "R7_ROUTER"`
- `purity_score >= purity_min` (par section)

**Pack diversifie** :
- S2 : 1 chunk `definition` + 1 chunk `trust_proofs`
- S7 : 1 chunk `selection_checks` + 1 chunk `anti_mistakes`
- S8 : 4-6 chunks `table_row`
- S9 : 4-6 chunks `faq`

**Fallback** : si RAG constructeur vide, la page reste fonctionnelle (microSEO generique + tableau safe generique). Tag `verification_status=draft` pour monitoring.

---

## Anti-cannibalisation

Dans le Gatekeeper, tout chunk contenant les termes suivants est rejete ou voit son `purity_score` chuter :
- symptomes, panne, diagnostic, changer, etape, tutoriel, montage, demonter, visser

Source de verite : `R7_FORBIDDEN_FROM_R3` + `R7_FORBIDDEN_FROM_R4` + `R7_FORBIDDEN_FROM_R5` dans `r7-keyword-plan.constants.ts`.
