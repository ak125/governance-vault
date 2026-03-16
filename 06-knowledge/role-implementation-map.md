# Role Implementation Map — massdoc repo

> **Cartographie role canonique R* → contrats / schemas / scripts / agents reels du repo**
> **Version**: 1.1.0 | **Status**: BASELINE_AUDIT | **Date**: 2026-03-14
> **Complement de**: role-matrix.md V5, pipeline-phases.md V7, schema-governance-matrix.md V1.2.0

---

## 0. Regle de lecture

Cette table distingue systematiquement :

- **Canon cible** = role metier officiel (defini dans role-matrix.md v5)
- **Implementation repo** = fichiers reellement presents
- **Ecart** = confusion ou dette de modelisation encore presente
- **Decision canonique** = ce qu'il faut considerer comme vrai a partir de maintenant

## Hierarchie de verite canonique

En cas de divergence entre plusieurs couches du repo, l'ordre de priorite officiel est :

1. **Contrats metier canoniques** (`page-contract-r*.schema.ts`, `r2-content-contract.schema.ts`)
2. **Constantes metier / gates / sections** (`r*-keyword-plan.constants.ts`, `r5-diagnostic.constants.ts`, etc.)
3. **References metier** (`.claude/skills/.../references/*.md`)
4. **Agents specialises** (`r*-keyword-planner.md`)
5. **Services, routes, composants, types frontend**
6. **Nomenclatures legacy et alias historiques**

Aucune couche inferieure ne peut contredire une couche superieure.

## Maturite canonique par role

| Role | Maturite | Detail |
|------|----------|--------|
| R0 Home | canon stable, contrat partiel | `r0-page-contract.constants.ts` = base preparatoire |
| R1 Router | stable | contrat + pipeline + agent complets |
| R2 Product | stable | contrat distribue (7 fichiers r2-*) |
| R3 Conseils | stable avec legacy residuel | `keyword-plan.constants.ts` = nom generique legacy |
| R4 Reference | stable | contrat + media + agent complets |
| R5 Diagnostic | stable | double couche surface + moteur |
| R6 Guide achat | stable avec alias legacy actifs | `R3_guide*` / `R3_buying_guide` encore dans 14 fichiers |
| R7 Brand | stable | contrat + mapping + agent complets |
| R8 Vehicle | stable | contrat + RAG generator + agent complets |

---

# R0 — HOME

## Canon cible
Surface d'entree principale.
Promesse : orienter rapidement vers les portes d'entree du systeme.

## Contrats / schemas repo
- `backend/src/config/r0-page-contract.constants.ts`

## Types / frontend
- pas de contrat R0 dedie clairement identifie

## Scripts / agents
- aucun agent R0 explicitement repere

## Implementation reelle
- R0 existe conceptuellement
- mais n'a pas encore un contrat aussi explicite que R1/R3/R4/R5/R6/R7

## Ecart
- R0 est reconnu dans la matrice canonique
- mais pas encore modelise comme contrat de premiere classe au meme niveau que les autres roles

## Decision canonique
- **R0 existe officiellement**
- **R0 n'a pas encore de contrat canonique complet implemente**
- `r0-page-contract.constants.ts` est a considerer comme **base technique preparatoire**, pas comme contrat final suffisant

---

# R1 — ROUTER GAMME

## Canon cible
Promesse : aider a trouver la bonne gamme pour le bon vehicule.

## Contrats / schemas repo
- `backend/src/config/page-contract-r1.schema.ts`
- `backend/src/config/page-contract-r1.json`
- `backend/src/config/r1-keyword-plan.constants.ts`

## Services / pipeline
- `backend/src/modules/admin/services/r1-content-pipeline.service.ts`
- `backend/src/modules/admin/services/r1-keyword-plan-gates.service.ts`

## Frontend / routes / types
- `frontend/app/routes/pieces.$slug.tsx`
- `frontend/app/components/pieces/CatalogueSection.tsx`
- `frontend/app/utils/r1-section-pack.ts`
- `frontend/app/utils/page-role.types.ts`

## Agents / docs
- `.claude/skills/seo-content-architect/references/r1-router-role.md`
- `.claude/skills/seo-content-architect/references/page-roles.md`

## Implementation reelle
- R1 est bien present, structure, fortement outille
- pipeline dedie existant
- contrat Zod + JSON presents

## Ecart
- faible
- surtout alignement a maintenir entre contrat, section pack frontend et pipeline admin

## Decision canonique
- **R1 est stable et officiel**
- source principale :
  - contrat = `page-contract-r1.schema.ts`
  - regles pipeline = `r1-keyword-plan.constants.ts`
  - doc role = `r1-router-role.md`

---

# R2 — PRODUCT

## Canon cible
Promesse : vendre la bonne reference compatible.

## Contrats / schemas repo
- `backend/src/config/r2-content-contract.schema.ts` (contrat principal)
- `backend/src/config/r2-content-contract.defaults.ts`
- `backend/src/config/r2-keyword-plan.constants.ts`
- `backend/src/config/r2-meta-builder.utils.ts`
- `backend/src/config/r2-scoring.utils.ts`
- `backend/src/config/r2-fingerprint.utils.ts`
- `backend/src/config/r2-heading-policy.utils.ts`

## Frontend / routes
- `frontend/app/routes/pieces.$gamme.$marque.$modele.$type[.]html.tsx`
- `frontend/app/utils/page-role.types.ts`

## Agents / docs
- `.claude/agents/r2-keyword-planner.md`

## Implementation reelle
- R2 est modelise via des fichiers distribues `r2-*` (pas un schema unifie `page-contract-r2`)
- agent dedie repere
- route produit claire

## Ecart
- pas de schema Zod unifie `page-contract-r2.schema.ts` (architecture distribuee)
- la base contractuelle existe mais est repartie sur 7 fichiers

## Decision canonique
- **R2 est officiel et structure**
- source principale :
  - contrat = `r2-content-contract.schema.ts`
  - plan/gates = `r2-keyword-plan.constants.ts`
  - agent = `r2-keyword-planner.md`

---

# R3 — CONSEILS / HOW-TO

## Canon cible
Promesse : expliquer comment agir, remplacer, controler ou entretenir correctement.

## Contrats / schemas repo
- `backend/src/config/page-contract-r3.schema.ts`
- `backend/src/config/page-contract-r3.json`
- `backend/src/config/keyword-plan.constants.ts`
- `backend/src/config/media-slots.constants.ts`

## Services / pipeline
- `backend/src/modules/admin/services/conseil-enricher.service.ts`
- `backend/src/modules/admin/services/content-refresh.service.ts`
- `backend/src/modules/admin/services/brief-template.service.ts`
- `backend/src/modules/admin/services/page-brief.service.ts`
- `backend/src/modules/admin/services/section-compiler.service.ts`

## Frontend / routes
- `frontend/app/routes/blog-pieces-auto.conseils.$pg_alias.tsx`
- `frontend/app/routes/blog-pieces-auto.conseils._index.tsx`
- `frontend/app/global.css` (sections R3 reperees)
- `frontend/app/utils/page-role.types.ts`

## Docs / references
- `.claude/skills/seo-content-architect/references/conseils-role.md`
- `.claude/skills/seo-content-architect/references/page-roles.md`
- `PROCEDURE-SEO.md`

## Tables / structure metier
- `__blog_advice`
- `__seo_gamme_conseil`

## Implementation reelle
- R3 conseils est tres present et historiquement fort
- structure sectionnelle S1-S8 + META claire
- pipeline et QA bien visibles

## Ecart
- certains composants/services utilisent encore parfois `R3_GUIDE` comme bucket generique
- certaines couches distinguent mal conseils vs guide achat

## Decision canonique
- **R3 = exclusivement conseils / how-to**
- `page-contract-r3.schema.ts` est a lire comme **contrat R3 conseils**
- `keyword-plan.constants.ts` reste la source majeure pour les sections S1-S8

---

# R4 — REFERENCE

## Canon cible
Promesse : definir une piece, un terme ou un concept technique.

## Contrats / schemas repo
- `backend/src/config/page-contract-r4.schema.ts`
- `backend/src/config/page-contract-r4.json`
- `backend/src/config/page-contract-r4-media.schema.ts`
- `backend/src/config/r4-keyword-plan.constants.ts`

## Services / validation
- `backend/src/modules/seo/services/page-role-validator.service.ts`

## Frontend / routes
- `frontend/app/routes/reference-auto.$slug.tsx`
- `frontend/app/routes/reference-auto._index.tsx`
- `frontend/app/routes/reference-auto.intent.$intent.tsx`
- `frontend/app/routes/reference-auto.systeme.$system.tsx`

## Agents / docs
- `.claude/agents/r4-keyword-planner.md`
- `.claude/skills/seo-content-architect/references/r4-reference-role.md`
- `.claude/skills/seo-content-architect/references/page-roles.md`

## Implementation reelle
- R4 est tres clairement modelise
- contrat riche
- media/layout separe
- frontieres metier bien documentees

## Ecart
- faible
- surtout coherence a maintenir entre version JSON et Zod

## Decision canonique
- **R4 est stable et officiel**
- source principale :
  - contrat = `page-contract-r4.schema.ts`
  - layout/media = `page-contract-r4-media.schema.ts`
  - regles = `r4-keyword-plan.constants.ts`

---

# R5 — DIAGNOSTIC

## Canon cible
Promesse : orienter l'utilisateur face a un symptome ou un signal anormal.

## Contrats / schemas repo
- `backend/src/config/page-contract-r5.schema.ts`
- `backend/src/config/r5-diagnostic.constants.ts`
- `backend/src/modules/diagnostic-engine/types/diagnostic-contract.schema.ts`
- `backend/src/modules/diagnostic-engine/types/diagnostic-input.schema.ts`
- `backend/src/modules/diagnostic-engine/types/evidence-pack.schema.ts`

## Services / moteur
- `backend/src/modules/diagnostic-engine/*`
- `backend/src/modules/seo/controllers/diagnostic.controller.ts`
- `backend/src/modules/seo/services/diagnostic.service.ts`

## Frontend / routes
- `frontend/app/routes/diagnostic-auto.$slug.tsx`
- `frontend/app/routes/diagnostic-auto._index.tsx`
- `frontend/app/routes/diagnostic.tsx`
- `frontend/app/components/diagnostic-wizard/*`

## Docs / references
- `.claude/skills/seo-content-architect/references/page-roles.md`

## Implementation reelle
- R5 est a la fois :
  - une surface SEO editoriale
  - un moteur de diagnostic structure
- tres forte richesse de schemas et de regles

## Ecart
- double couche a bien distinguer :
  - **R5 surface editoriale**
  - **diagnostic-engine comme moteur logique**
- il ne faut pas confondre page R5 et moteur expert

## Decision canonique
- **R5 = surface diagnostic**
- le `diagnostic-engine` est un **moteur transverse d'orchestration**, pas un role separe
- source principale :
  - role surface = `page-contract-r5.schema.ts` + `r5-diagnostic.constants.ts`
  - moteur = `diagnostic-contract.schema.ts` et schemas associes

---

# R6 — GUIDE D'ACHAT

## Canon cible
Promesse : aider a acheter la bonne piece sans se tromper.

## Contrats / schemas repo
- `backend/src/config/page-contract-r6.schema.ts`
- `backend/src/config/schemas/PageContractR6.json`
- `backend/src/config/r6-keyword-plan.constants.ts`

## Services / pipeline
- `backend/src/modules/admin/services/buying-guide-enricher.service.ts`
- `backend/src/modules/blog/services/r6-guide.service.ts`
- `backend/src/modules/blog/controllers/r6-guide.controller.ts`

## Frontend / routes / composants
- `frontend/app/routes/blog-pieces-auto.guide-achat.$pg_alias.tsx`
- `frontend/app/routes/blog-pieces-auto.guide-achat._index.tsx`
- `frontend/app/components/guide/r6-guide-schemas.ts`
- `frontend/app/types/r6-guide.types.ts`
- `frontend/app/utils/page-role.types.ts`

## Agents / docs
- `.claude/agents/r6-keyword-planner.md`
- `.claude/skills/seo-content-architect/references/guide-achat-role.md`
- `.claude/skills/seo-content-architect/references/page-roles.md`

## Implementation reelle
- la realite repo montre clairement :
  - `R6_GUIDE_ACHAT` cote frontend
  - `page-contract-r6.schema.ts`
  - constantes R6 dediees
- c'est l'implementation reelle la plus forte

## Ecart
- encore des traces legacy ou guide achat apparait sous `R3_guide` ou `R3_guide_achat`
- plusieurs services admin / refresh utilisent encore l'ancienne nomenclature

## Decision canonique
- **R6 = guide d'achat**
- toute occurrence `R3_guide` ou `R3_guide_achat` doit etre lue comme **legacy / alias technique a migrer**
- source principale :
  - contrat = `page-contract-r6.schema.ts`
  - regles = `r6-keyword-plan.constants.ts`
  - doc role = `guide-achat-role.md`

---

# R7 — BRAND

## Canon cible
Promesse : aider a naviguer dans l'univers pieces d'une marque.

## Contrats / schemas repo
- `backend/src/config/page-contract-r7.schema.ts`
- `backend/src/config/r7-keyword-plan.constants.ts`
- `backend/src/config/brand-role-map.schema.ts`

## Frontend / routes
- `frontend/app/routes/constructeurs.$.tsx`

## Agents / docs
- `.claude/agents/r7-keyword-planner.md`
- `.claude/agents/r7-brand-rag-generator.md`

## Implementation reelle
- R7 est bien reel
- contrat riche et bien separe
- mapping brand/rag explicite

## Ecart
- parfois encore rattache par erreur a R1 dans certaines routes ou handles si lecture superficielle
- mais la base contractuelle R7 est claire

## Decision canonique
- **R7 = Brand**
- source principale :
  - contrat = `page-contract-r7.schema.ts`
  - regles = `r7-keyword-plan.constants.ts`
  - mapping = `brand-role-map.schema.ts`

---

# R8 — VEHICLE

## Canon cible
Promesse : orienter a partir d'un vehicule precis.

## Contrats / schemas repo
- `backend/src/config/page-contract-r8.schema.ts`
- `backend/src/config/r8-keyword-plan.constants.ts`

## Services / generation
- `backend/src/modules/admin/services/vehicle-rag-generator.service.ts`
- `backend/src/modules/rag-proxy/services/rag-ingestion.service.ts` (ingestion RAG vehicule)
- `backend/src/modules/rag-proxy/services/rag-knowledge.service.ts` (lecture corpus vehicule)

## RAG / stockage
- `/opt/automecanik/rag/knowledge/vehicles/*.md`

## Agents / docs
- `.claude/agents/r8-keyword-planner.md`

## Implementation reelle
- R8 est bien present avec contrat schema dedie, generateur RAG dedie et agent
- generation vehicle RAG via `vehicle-rag-generator.service.ts`
- constantes de keyword plan dediees

## Ecart
- faible
- visibilite frontend a renforcer (pas de route publique R8 dediee identifiee)

## Decision canonique
- **R8 = Vehicle**
- source principale :
  - contrat = `page-contract-r8.schema.ts`
  - regles = `r8-keyword-plan.constants.ts`
  - generateur = `vehicle-rag-generator.service.ts`
  - corpus = `/opt/automecanik/rag/knowledge/vehicles/`
  - agent = `r8-keyword-planner.md`

---

# 1. Alias legacy a figer pour eviter la confusion

## Alias historiques observes

| Terme legacy | Lecture canonique |
|---|---|
| `R3_guide` | **R6 Guide d'achat** |
| `R3_guide_achat` | **R6 Guide d'achat** |
| `R3_buying_guide` | **R6 Guide d'achat** |
| `R3_conseils` | **R3 Conseils / how-to** |
| `R3_BLOG` | role frontend trop large ; a desambiguiser selon sous-type reel |
| `R6_GUIDE_ACHAT` | **canon correct** |
| `R4_GLOSSARY` | **R4 Reference** |
| `R5_DIAGNOSTIC` | **R5 Diagnostic** |

## Regle canonique
A partir de maintenant :

- `R3` = conseils uniquement
- `R6` = guide d'achat uniquement
- les anciens `R3_guide*` et `R3_buying_guide` sont des **artefacts legacy**, pas des verites metier

---

# 2. Source de verite canonique par couche

## Couche metier canonique
- `backend/src/config/r0-page-contract.constants.ts` (preparatoire)
- `backend/src/config/page-contract-r1.schema.ts`
- `backend/src/config/r2-content-contract.schema.ts` (+ 6 fichiers r2-*)
- `backend/src/config/page-contract-r3.schema.ts`
- `backend/src/config/page-contract-r4.schema.ts`
- `backend/src/config/page-contract-r5.schema.ts`
- `backend/src/config/page-contract-r6.schema.ts`
- `backend/src/config/page-contract-r7.schema.ts`
- R8 : `r8-keyword-plan.constants.ts` (contrat schema a creer)

## Couche regles / sections / gates
- `backend/src/config/r1-keyword-plan.constants.ts`
- `backend/src/config/r2-keyword-plan.constants.ts`
- `backend/src/config/keyword-plan.constants.ts` (R3 conseils — nom generique legacy, a lire comme source regles R3 conseils)
- `backend/src/config/r4-keyword-plan.constants.ts`
- `backend/src/config/r5-diagnostic.constants.ts`
- `backend/src/config/r6-keyword-plan.constants.ts`
- `backend/src/config/r7-keyword-plan.constants.ts`
- `backend/src/config/r8-keyword-plan.constants.ts`

## Couche doc metier lisible
- `.claude/skills/seo-content-architect/references/page-roles.md`
- `.claude/skills/seo-content-architect/references/r1-router-role.md`
- `.claude/skills/seo-content-architect/references/conseils-role.md`
- `.claude/skills/seo-content-architect/references/guide-achat-role.md`
- `.claude/skills/seo-content-architect/references/r4-reference-role.md`

## Couche agents repo
- `.claude/agents/r2-keyword-planner.md`
- `.claude/agents/r4-keyword-planner.md`
- `.claude/agents/r6-keyword-planner.md`
- `.claude/agents/r7-keyword-planner.md`
- `.claude/agents/r7-brand-rag-generator.md`
- `.claude/agents/r8-keyword-planner.md`
- `.claude/agents/keyword-planner.md` (legacy/generique surtout R3 conseils)

---

# 3. Verdict canonique final

## Verite metier officielle (conforme role-matrix.md v5)
- **R0 = Home** — orienter dans l'ecosysteme
- **R1 = Router gamme** — trouver la bonne gamme pour le bon vehicule
- **R2 = Product** — acheter la bonne reference compatible
- **R3 = Conseils / how-to** — agir correctement sur la piece
- **R4 = Reference** — comprendre ce qu'est la chose
- **R5 = Diagnostic** — orienter un symptome
- **R6 = Guide d'achat** — choisir la bonne piece avant achat
- **R7 = Brand** — entrer par la marque
- **R8 = Vehicle** — entrer par le vehicule

## Verite d'implementation repo
- R1, R4, R5, R6, R7 ont des contrats dedies nets (`page-contract-r*.schema.ts`)
- R2 a un contrat distribue (`r2-content-contract.schema.ts` + utilitaires)
- R3 a un contrat fort mais encore entoure d'anciens noms ambigus
- R0 existe dans le canon mais n'a pas encore le meme niveau de contrat formel
- R8 a des constantes de keyword plan mais pas de contrat schema unifie
- `R3_guide*` / `R3_buying_guide` doivent etre consideres comme **legacy**, remplaces par **R6**

## Regle de gel (conforme pipeline-phases.md v7)

A partir de maintenant, toute doc, agent, script, contrat, audit ou pipeline doit :

1. cibler un role canonique parmi `R0..R8`
2. traiter `R3_guide*` / `R3_buying_guide` comme alias legacy de `R6`
3. ne jamais reintroduire `R9`
4. ne jamais traiter la gouvernance `G*` comme un role metier
5. respecter les regles d'implementation A-I (pipeline-phases.md v7)
6. respecter les etats granulaires de qualification (INGESTED_SAFE → NORMALIZED → ADMISSIBLE_R* → GENERATED_ROLE_PURE)

## Regle sur les agents generiques

Tout agent generique non suffixe par un role R* (ex: `keyword-planner.md`) ne constitue jamais une source de verite metier primaire.
Il doit etre interprete a la lumiere du canon R0-R8 et de la hierarchie de verite canonique (section 0).

## Implementations tolerees mais non canoniques

Les elements suivants sont toleres a court terme mais **non reutilisables pour toute nouvelle implementation** :

- noms historiques encore presents dans les services admin (`R3_buying_guide`, `R3_guide_achat`)
- handles frontend trop larges (`R3_BLOG`, `R3_GUIDE`)
- agents generiques non suffixes par role (`keyword-planner.md`)
- docs anciennes non migrees vers la nomenclature R0-R8
- `keyword-plan.constants.ts` comme nom generique (source R3 conseils)

Regle : tolere en lecture, interdit en creation. Aucune nouvelle implementation ne doit reproduire ces patterns.

## Regle de non-reintroduction

1. aucun nouveau role ne peut etre cree hors matrice R0..R8 sans decision canonique explicite
2. aucun alias libre ne peut etre introduit sans mapping vers un role canonique
3. aucun agent generique, service historique ou route legacy ne peut redefinir un role metier
4. toute occurrence de `R3_guide*` doit etre lue comme legacy de R6
5. `G*` ne doit jamais etre traite comme role metier
6. `R9` ne doit jamais etre reintroduit

---

_Derniere mise a jour: 2026-03-14_
_Source: code search backend + role-matrix.md V5 + pipeline-phases.md V7_
