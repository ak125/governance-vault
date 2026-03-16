# Matrice canonique de rangement documentaire — v2

> **Date** : 2026-03-15
> **Version** : 2.0.0
> **Statut** : CANONIQUE
> **Emplacement RAG** : `/opt/automecanik/rag/knowledge/`

---

## Principe directeur

**Stockage large, exploitation stricte.**

Chaque document doit etre classe selon :
1. Sa nature reelle
2. Son niveau de verite par defaut (`truth_level`)
3. Son statut de verification par defaut (`verification_status`)
4. Son admissibilite metier par defaut (`business_pool_admissible`)
5. Son foundation gate attendu (`foundation_gate_passed`)
6. Sa phase cible suivante (`next_phase_target`)

---

## Matrice de classification (33 types)

### Sources internes validees

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| Documentation interne validee | `knowledge/internal/` | high | verified | yes | pass | 1.5→1.6→2 | retrieval, synthese, enrichissement, refresh, generation |
| Documentation canonique metier | `knowledge/canonical/` | high | verified | yes | pass | 1.5→1.6→2 | retrieval, generation, QA, publication candidate |
| Documentation constructeur/OEM | `knowledge/references/` | high | verified / primary_source | yes | pass | 1.5→1.6→2 | reference forte, claims techniques |
| Documentation fournisseur | `knowledge/technical/suppliers/` | medium-high | validated_secondary | conditional→yes | pass | 1.5→1.6→2 | support, enrichissement, comparaison |

### Referentiels metier

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| Referentiel gamme | `knowledge/gammes/` | medium-high | validated | yes | pass | 1.5→1.6→2 | R1, R6, routing, refresh |
| Referentiel vehicule | `knowledge/vehicles/` | medium-high | validated | yes | pass | 1.5→1.6→2 | R8, contextualisation |
| Referentiel marque | `knowledge/brands/` | medium-high | validated | yes | pass | 1.5→1.6→2 | R7, navigation marque |
| Referentiel diagnostic | `knowledge/diagnostics/` | medium-high | validated | yes | pass | 1.5→1.6→2 | R5, evidence pack, triage |
| Guides/how-to internes | `knowledge/guides/` | high | verified | yes | pass | 1.5→1.6→2 | R3, enrichissement, refresh |
| FAQ validees | `knowledge/faqs/` | medium-high | validated | conditional | pass | 1.5→1.6→2 | support editorial, sections FAQ |
| Policies/regles/canon | `knowledge/policies/` | high | verified | yes (controle) / no (generation) | pass | 1.5→controle | QA, governance, gates |

### Documents de travail valides

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| Briefs valides | `knowledge/briefs/` | medium | validated | conditional | pass | 1.6→2 | planification, generation cadree |
| Evidence packs | `knowledge/evidence/` | derived | derived_validated | yes | pass | 2 | generation, validation, assemblage |

### Sources web

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| Captures web non qualifiees | `knowledge/_raw/web/` | low | unverified | no | conditional | 1.5 ou quarantine | stockage, audit, scoring |
| Articles de presse | `knowledge/web/news/` | medium | secondary_source | no | pass (stockage) | research/review | veille, contexte |
| Blogs externes | `knowledge/web/blogs/` | low-medium | secondary_source | no | pass (stockage) | research/review | veille, comparaison |
| Forums | `knowledge/web/forums/` | low | community_unverified | no | pass (stockage) | research | signaux faibles, patterns |
| Communautes/UGC/Reddit | `knowledge/web/community/` | low | community_unverified | no | pass (stockage) | research | vocabulaire utilisateur |
| Articles editoriaux specialises | `knowledge/web/editorial/` | medium | secondary_source_reviewed | conditional | pass | review→1.6 | support secondaire |
| Sources exploratoires | `knowledge/web/exploratory/` | low | unverified | no | pass (stockage) | research/quarantine | qualification future |

### Documents bruts/non qualifies

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| PDF bruts | `knowledge/_raw/pdf/` | low | unverified | no | conditional | 1.5 ou quarantine | stockage, extraction |
| Imports DB bruts | `knowledge/_raw/db/` | variable | unverified | no | conditional | 1.5 | audit, normalisation |
| Legacy non normalise | `knowledge/_raw/legacy/` | low-medium | legacy_unresolved | no | conditional | 1.5→2A | audit, mapping |
| Documents partiels | `knowledge/_staging/partial/` | low-medium | partial | no | conditional | 1.5 ou review | completion, comparaison |
| Documents staging metier | `knowledge/_staging/` | variable | pending_validation | no | pass/conditional | 1.6→2 | assemblage intermediaire |

### Quarantaine

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| Documents en quarantaine | `knowledge/_quarantine/` | unknown | rejected_or_pending_review | no | fail | review/reprocess | audit, investigation |
| Documents failed foundation | `knowledge/_quarantine/foundation/` | low | foundation_failed | no | fail | review/reprocess | audit, scoring |

### Media et artefacts

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| Media prompts/briefs visuels | `knowledge/media/prompts/` | low-medium | draft | no (verite metier) | pass | media workflow | creation visuelle |
| Assets image/video | `knowledge/media/assets/` | variable | asset_verified/unverified | conditional | pass | media workflow→2 | slots media, UI |

### Documents support/ops

| Type | Zone de stockage | truth_level | verification_status | admissibilite | foundation_gate | phase suivante | usages |
|------|-----------------|-------------|-------------------|---------------|-----------------|---------------|--------|
| Syntheses de recherche | `knowledge/research/` | medium | internally_reviewed | no | pass | review→1.6 | analyse, comparaison |
| Notes d'audit/rapports | `knowledge/audit/` | medium | audit_record | no (generation) | pass | review | audit, observabilite |
| Artefacts shadow legacy→canon | `knowledge/shadow/` | derived | shadow_projection | no | pass | 2A | projection, convergence |
| Docs support/juridique | `knowledge/support/` | medium | validated | no (roles editoriaux) | pass | support workflow | conformite, relation client |
| Documents applicatifs | `knowledge/app/` | medium | validated | no (matrice editoriale) | pass | app workflow | checkout, login, paiement |

---

## Regles canoniques durcies

### R1 — Stockage large, exploitation stricte
Tu peux stocker beaucoup. Tu n'exploites metier que ce qui est explicitement admissible.

### R2 — Source secondaire jamais forte par defaut
Presse, blogs, forums, communautes : stockage oui, exploitation metier forte non par defaut.

### R3 — foundation_gate=fail n'implique pas suppression
Une doc failed reste stockee, lisible, auditable, reprocessable. Mais elle ne doit pas alimenter l'ecriture metier.

### R4 — Le pool admissible ne prend pas tout
Meme une doc "interessante" peut rester exclue si : provenance faible, structure douteuse, validation absente, conflit non resolu.

### R5 — Fusion d'informations, pas de document gagnant
Les phases aval fusionnent les meilleures informations admissibles. La Phase 1 ne designe pas un document gagnant.

---

## Champs minimaux par document

Chaque doc ingere doit porter au minimum :

| Champ | Type | Obligatoire |
|-------|------|:-----------:|
| `source_type` | text | OUI |
| `storage_zone` | text | OUI |
| `truth_level` | enum (L1-L4 ou high/medium/low) | OUI |
| `verification_status` | text | OUI |
| `foundation_gate_passed` | boolean | OUI |
| `business_pool_admissible` | boolean | OUI |
| `doc_family` | text | OUI |
| `canonical_storage_key` | text | OUI |
| `next_phase_target` | text | RECO |

---

## Structure de dossiers canonique

```
knowledge/
  canonical/           # docs canoniques metier validees
  internal/            # docs internes validees
  gammes/              # referentiel gamme (R1/R6)
  vehicles/            # referentiel vehicule (R8)
  brands/              # referentiel marque (R7) — alias constructeurs/
  references/          # docs constructeur/OEM — alias reference/
  diagnostics/         # referentiel diagnostic (R5) — alias diagnostic/
  guides/              # guides/how-to internes (R3)
  faqs/                # FAQ validees — alias faq/
  policies/            # policies/regles/canon
  briefs/              # briefs valides
  evidence/            # evidence packs
  web/                 # sources web classees
    news/
    blogs/
    forums/
    community/
    editorial/
    exploratory/
  research/            # syntheses de recherche
  audit/               # notes d'audit
  shadow/              # artefacts shadow legacy→canon
  support/             # docs support/juridique
  app/                 # docs applicatifs
  media/               # media
    prompts/
    assets/
  _raw/                # bruts non qualifies
    web/
    pdf/
    db/
    legacy/
  _staging/            # staging metier
    partial/
  _quarantine/         # quarantaine
    foundation/
```

---

## Delta structure existante vs recommandee

| Existant | Recommande | Statut |
|----------|-----------|--------|
| `canonical/` | `canonical/` | ✅ Match |
| `gammes/` | `gammes/` | ✅ Match |
| `vehicles/` | `vehicles/` | ✅ Match |
| `constructeurs/` | `brands/` | ⚠️ Alias a creer |
| `diagnostic/` | `diagnostics/` | ⚠️ Alias singulier→pluriel |
| `guides/` | `guides/` | ✅ Match |
| `faq/` | `faqs/` | ⚠️ Alias singulier→pluriel |
| `reference/` | `references/` | ⚠️ Alias singulier→pluriel |
| `web/` | `web/` | ✅ Match (sous-dossiers a creer) |
| `web-catalog/` | — | Legacy, a classifier dans `web/` ou `_raw/` |
| `catalog/` | — | Legacy, a classifier |
| `seo-data/` | — | Legacy, a classifier dans `evidence/` ou `audit/` |
| `structured/` | — | Legacy, a classifier |
| `tabular/` | — | Legacy, a classifier dans `_raw/db/` |
| `_quarantine/` | `_quarantine/` | ✅ Match |
| `_raw/` | `_raw/` | ✅ Match |
| `media/` | `media/` | ✅ Match |
| — | `internal/` | A creer |
| — | `briefs/` | A creer |
| — | `evidence/` | A creer |
| — | `research/` | A creer |
| — | `audit/` | A creer |
| — | `shadow/` | A creer |
| — | `support/` | A creer |
| — | `app/` | A creer |
| — | `_staging/` | A creer |

**Note** : les renommages ne doivent pas casser les references existantes dans `__rag_knowledge.source`. Utiliser des symlinks ou des aliases dans la config d'ingestion.

---

## Refs croisees

| Document | Role |
|----------|------|
| `.spec/00-canon/architecture.md` | Architecture technique |
| `.spec/00-canon/rules.md` | Regles non-negociables |
| `MEMORY.md` → `rag.md` | Architecture RAG 3 couches |
| `backend/src/modules/rag-proxy/services/rag-foundation-gate.service.ts` | Implementation F1-GATE |
| `backend/src/modules/rag-proxy/services/rag-normalization.service.ts` | Implementation Phase 1.5 |
| `backend/src/modules/rag-proxy/services/rag-admissibility-gate.service.ts` | Implementation Phase 1.6 |
