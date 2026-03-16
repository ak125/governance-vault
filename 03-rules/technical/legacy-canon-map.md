# Table canonique figee — legacy → canon

> **Version** : 1.1.0
> **Date** : 2026-03-14
> **Status** : BASELINE_AUDIT
> **Complement de** : role-matrix.md V4, pipeline-phases.md V7, role-implementation-map.md V1.1.0

---

## 0. Regle de lecture

Cette table sert a normaliser tout le vocabulaire du systeme.

Elle distingue :

- **Legacy** = ancien nom, alias historique, nom ambigu, nom hybride ou nom technique local
- **Canon** = nom metier officiel a utiliser partout dans la doc cible
- **Statut** = accepte / tolere temporairement / a migrer / interdit
- **Risque** = priorite de migration (fort / moyen / faible)
- **Action** = quoi faire dans le code, les docs, les scripts et les agents

### Hierarchie de verite canonique

En cas de divergence entre plusieurs representations d'un role, l'ordre de priorite officiel est :

1. **Matrice canonique des roles R0..R8 / G1..G5** (role-matrix.md)
2. **Table legacy → canon** (ce document)
3. **Contrats et schemas metier canoniques** (`page-contract-r*.schema.ts`, `r2-content-contract.schema.ts`)
4. **Constantes, planners et gates** (`r*-keyword-plan.constants.ts`, etc.)
5. **Documentation metier de reference** (`.claude/skills/.../references/*.md`)
6. **Agents specialises** (`r*-keyword-planner.md`)
7. **Services, routes, composants et types frontend**
8. **Labels legacy DB, aliases historiques et conventions locales**

Aucune couche inferieure ne peut contredire une couche superieure.

---

# 1. Regle maitresse

## 1.1 Serie canonique des roles metier

Les seuls roles metier canoniques sont :

- `R0_HOME`
- `R1_ROUTER`
- `R2_PRODUCT`
- `R3_CONSEILS`
- `R4_REFERENCE`
- `R5_DIAGNOSTIC`
- `R6_GUIDE_ACHAT`
- `R7_BRAND`
- `R8_VEHICLE`

## 1.2 Serie canonique de gouvernance

La gouvernance n'appartient pas a la serie `R*`.

Elle appartient a la serie `G*` :

- `G1_PURETE`
- `G2_DIVERSITE`
- `G3_ANTI_CANNIBALISATION`
- `G4_PUBLICATION_CONTROL`
- `G5_REVIEW_ESCALATION`

## 1.3 Regle de migration

Tout nom non present dans la serie canonique :

- doit etre soit **mappe** vers un role canonique,
- soit **declare legacy**,
- soit **supprime**.

---

# 2. Table canonique — noms de roles

| Legacy / alias observe | Canon cible | Statut | Risque | Action |
|---|---|---|---|---|
| `R0` | `R0_HOME` | accepte | — | garder |
| `R1` | `R1_ROUTER` | accepte | — | garder |
| `R1_pieces` | `R1_ROUTER` | tolere temporairement | moyen | migrer progressivement |
| `R2` | `R2_PRODUCT` | accepte | — | garder |
| `R2_PRODUCT` | `R2_PRODUCT` | accepte | — | garder |
| `R3` | ambigu | interdit seul | fort | toujours preciser `R3_CONSEILS` |
| `R3_BLOG` | anti-pattern legacy | interdit comme verite metier | fort | desambiguiser obligatoirement en `R3_CONSEILS` ou `R6_GUIDE_ACHAT` |
| `R3_conseils` | `R3_CONSEILS` | tolere temporairement | faible | migrer nommage |
| `R3_GUIDE` | ambigu / legacy | a migrer | fort | remapper vers `R3_CONSEILS` ou `R6_GUIDE_ACHAT` selon contexte |
| `R3_guide` | `R6_GUIDE_ACHAT` | legacy a migrer | fort | remplacer |
| `R3_guide_achat` | `R6_GUIDE_ACHAT` | legacy a migrer | fort | remplacer |
| `R4` | `R4_REFERENCE` | accepte | — | garder |
| `R4_REFERENCE` | `R4_REFERENCE` | accepte | — | garder |
| `R4_GLOSSARY` | `R4_REFERENCE` | tolere temporairement | faible | migrer vocabulaire |
| `R5` | `R5_DIAGNOSTIC` | accepte | — | garder |
| `R5_diagnostic` | `R5_DIAGNOSTIC` | tolere temporairement | faible | migrer |
| `R5_DIAGNOSTIC` | `R5_DIAGNOSTIC` | accepte | — | garder |
| `R6` | ambigu | interdit seul | fort | toujours preciser `R6_GUIDE_ACHAT` ou `R6_SUPPORT_LOCAL` |
| `R6_GUIDE_ACHAT` | `R6_GUIDE_ACHAT` | accepte | — | garder |
| `R6_BUYING_GUIDE` | `R6_GUIDE_ACHAT` | tolere temporairement | moyen | unifier |
| `R6_SUPPORT` | hors matrice editoriale coeur | tolere local uniquement | moyen | n'est pas un role canonique metier — tolere uniquement comme label local de surface support non editoriale — ne jamais confondre avec `R6_GUIDE_ACHAT` |
| `R7` | `R7_BRAND` | accepte | — | garder |
| `R7_BRAND` | `R7_BRAND` | accepte | — | garder |
| `R8` | `R8_VEHICLE` | accepte | — | garder |
| `R8_VEHICLE` | `R8_VEHICLE` | accepte | — | garder |
| `R9` | aucun | interdit | fort | supprimer de la matrice canonique |
| `RX_CHECKOUT` | hors matrice SEO canonique | tolere local | faible | isoler comme surface applicative non editoriale |

---

# 3. Table canonique — page_type legacy → canon

| page_type / libelle legacy | Canon cible | Statut | Risque | Action |
|---|---|---|---|---|
| `R1_pieces` | `R1_ROUTER` | tolere temporairement | moyen | conserver en DB si besoin, mais documenter le mapping |
| `R3_conseils` | `R3_CONSEILS` | tolere temporairement | faible | garder en DB en attendant migration |
| `R3_guide_achat` | `R6_GUIDE_ACHAT` | legacy a migrer | fort | remapper dans docs et services |
| `R4_reference` | `R4_REFERENCE` | tolere temporairement | faible | garder si DB legacy |
| `R5_diagnostic` | `R5_DIAGNOSTIC` | tolere temporairement | faible | garder si DB legacy |
| `R6_support` ou equivalent | `R6_SUPPORT_LOCAL` | hors matrice editoriale canonique | moyen | isoler comme support |
| `brand` / constructeur implicite | `R7_BRAND` | ambigu | moyen | interdit en documentation cible sans renommage |
| `vehicle` / fiche vehicule implicite | `R8_VEHICLE` | ambigu | moyen | interdit en documentation cible sans renommage |

## Regle
Les `page_type` legacy DB peuvent survivre techniquement, mais toute documentation cible doit exposer le **canon**.

---

# 4. Table canonique — page_role legacy → canon

| page_role legacy | Canon cible | Statut | Risque | Action |
|---|---|---|---|---|
| `R1` | `R1_ROUTER` | tolere temporairement | moyen | clarifier |
| `R3_guide` | `R6_GUIDE_ACHAT` | legacy a migrer | fort | remplacer |
| `R3_conseils` | `R3_CONSEILS` | tolere temporairement | faible | remplacer progressivement |
| `R4` | `R4_REFERENCE` | tolere temporairement | moyen | clarifier |
| `R5` | `R5_DIAGNOSTIC` | tolere temporairement | moyen | clarifier |
| `R6` | ambigu | interdit seul | fort | preciser support ou guide achat |
| `R7` | `R7_BRAND` | tolere temporairement | faible | clarifier |
| `R8` | `R8_VEHICLE` | tolere temporairement | faible | clarifier |

## Regle
Dans les nouveaux briefs, nouveaux contrats, nouvelles docs et nouveaux agents, on n'ecrit plus jamais :

- `R3_guide`
- `R3`
- `R6`
- `R4`
- `R5`

sans suffixe metier explicite.

---

# 5. Table canonique — routes frontend → canon

| Route | Canon cible | Statut | Note |
|---|---|---:|---|
| `/` | `R0_HOME` | canon | home |
| `/pieces/{slug}` ou `/pieces/{slug}-{pg_id}.html` | `R1_ROUTER` | canon | router gamme |
| `/pieces/{gamme}/{marque}/{modele}/{type}.html` | `R2_PRODUCT` | canon | listing/produit vehicule |
| `/blog-pieces-auto/conseils/{pg_alias}` | `R3_CONSEILS` | canon | how-to |
| `/reference-auto/{slug}` | `R4_REFERENCE` | canon | reference |
| `/diagnostic-auto/{slug}` | `R5_DIAGNOSTIC` | canon | diagnostic |
| `/blog-pieces-auto/guide-achat/{pg_alias}` | `R6_GUIDE_ACHAT` | canon | guide achat |
| `/constructeurs/{alias}.html` ou equivalent | `R7_BRAND` | canon | brand |
| route fiche vehicule dediee | `R8_VEHICLE` | canon | vehicle |
| `/contact`, `/404`, `/mentions-legales`, `/politique-confidentialite`, login/register | hors matrice editoriale principale | support applicatif | ne pas melanger avec R6 guide achat |

---

# 6. Table canonique — fichiers contrats / schemas → canon

| Fichier reel | Canon cible | Statut | Action |
|---|---|---:|---|
| `page-contract-r1.schema.ts` | `R1_ROUTER` | canon | source de verite |
| `page-contract-r1.json` | `R1_ROUTER` | canon derive | garder aligne au Zod |
| `r2-content-contract.schema.ts` | `R2_PRODUCT` | canon | source de verite |
| `page-contract-r3.schema.ts` | `R3_CONSEILS` | canon metier reel | garder, mais documenter clairement qu'il couvre conseils |
| `page-contract-r3.json` | `R3_CONSEILS` | canon derive | garder aligne |
| `page-contract-r4.schema.ts` | `R4_REFERENCE` | canon | source de verite |
| `page-contract-r4.json` | `R4_REFERENCE` | canon derive | garder aligne |
| `page-contract-r5.schema.ts` | `R5_DIAGNOSTIC` | canon | source de verite |
| `page-contract-r6.schema.ts` | `R6_GUIDE_ACHAT` | canon | source de verite |
| `schemas/PageContractR6.json` | `R6_GUIDE_ACHAT` | canon derive | garder aligne |
| `page-contract-r7.schema.ts` | `R7_BRAND` | canon | source de verite |
| `page-contract-r8.schema.ts` | `R8_VEHICLE` | canon | source de verite |
| `page-contract-hub.schema.ts` | artefact transverse de composition | hors matrice coeur | non equivalent a un role canonique — ne pas confondre avec un R* |
| `r0-page-contract.constants.ts` | `R0_HOME` preparatoire | incomplet | completer plus tard |

---

# 7. Table canonique — constants / gates / planners → canon

| Fichier reel | Canon cible | Statut | Action |
|---|---|---:|---|
| `r1-keyword-plan.constants.ts` | `R1_ROUTER` | canon | garder |
| `r2-keyword-plan.constants.ts` | `R2_PRODUCT` | canon | garder |
| `keyword-plan.constants.ts` | `R3_CONSEILS` | canon historique | nom generique legacy — lire comme source regles R3 conseils, renommer plus tard si besoin |
| `r4-keyword-plan.constants.ts` | `R4_REFERENCE` | canon | garder |
| `r5-diagnostic.constants.ts` | `R5_DIAGNOSTIC` | canon | garder |
| `r6-keyword-plan.constants.ts` | `R6_GUIDE_ACHAT` | canon | garder |
| `r7-keyword-plan.constants.ts` | `R7_BRAND` | canon | garder |
| `r8-keyword-plan.constants.ts` | `R8_VEHICLE` | canon | garder |
| `page-contract-shared.constants.ts` | transverse | canon transverse | garder |
| `role-ids.ts` | transverse | doit etre aligne sur canon | verifier et corriger si besoin |

---

# 8. Table canonique — agents repo → canon

| Agent reel | Canon cible | Statut | Action |
|---|---|---:|---|
| `.claude/agents/keyword-planner.md` | principalement `R3_CONSEILS` historique | ambigu | documenter comme agent legacy/generique |
| `.claude/agents/r2-keyword-planner.md` | `R2_PRODUCT` | canon | garder |
| `.claude/agents/r4-keyword-planner.md` | `R4_REFERENCE` | canon | garder |
| `.claude/agents/r6-keyword-planner.md` | `R6_GUIDE_ACHAT` | canon | garder |
| `.claude/agents/r7-keyword-planner.md` | `R7_BRAND` | canon | garder |
| `.claude/agents/r8-keyword-planner.md` | `R8_VEHICLE` | canon | garder |
| `.claude/agents/r7-brand-rag-generator.md` | `R7_BRAND` | canon | garder |
| `.claude/agents/brief-enricher.md` | transverse | hors matrice role | garder comme couche outil |
| `.claude/agents/research-agent.md` | transverse | hors matrice role | garder comme couche outil |

## Regle
Un agent peut servir plusieurs roles, mais il doit toujours :

- declarer son **role cible canonique**
- ou declarer qu'il est **transverse**
- jamais rester dans un etat ambigu

**Aucun agent generique ou transverse ne constitue une source de verite metier primaire.** Tout agent generique doit etre interprete a la lumiere du canon R0-R8.

---

# 9. Table canonique — docs metier → canon

| Doc reelle | Canon cible | Statut | Action |
|---|---|---:|---|
| `page-roles.md` | transverse roles | canon doc | corriger definitivement R3/R6 |
| `r1-router-role.md` | `R1_ROUTER` | canon | garder |
| `conseils-role.md` | `R3_CONSEILS` | canon | garder |
| `guide-achat-role.md` | `R6_GUIDE_ACHAT` | canon | garder |
| `r4-reference-role.md` | `R4_REFERENCE` | canon | garder |
| `PROCEDURE-SEO.md` | transverse pipeline | canon transverse a durcir | aligner strictement sur R/G |

---

# 10. Table canonique — services metier repo → canon

| Service reel | Canon cible principal | Statut | Action |
|---|---|---:|---|
| `r1-content-pipeline.service.ts` | `R1_ROUTER` | canon | garder |
| `r1-keyword-plan-gates.service.ts` | `R1_ROUTER` + gouvernance | canon | garder |
| `conseil-enricher.service.ts` | `R3_CONSEILS` | canon | garder |
| `buying-guide-enricher.service.ts` | `R6_GUIDE_ACHAT` | canon metier malgre legacy interne | corriger labels legacy |
| `vehicle-rag-generator.service.ts` | `R8_VEHICLE` | canon | garder |
| `content-refresh.service.ts` | transverse | canon transverse | expliciter mappings legacy→canon |
| `page-brief.service.ts` | transverse | canon transverse | garder |
| `brief-template.service.ts` | transverse | canon transverse | garder |
| `section-compiler.service.ts` | transverse | canon transverse | garder |
| `rag-safe-distill.service.ts` | transverse | canon transverse | corriger alias de roles |

---

# 11. Table canonique — alias frontend PageRole → canon

| PageRole frontend observe | Canon cible | Statut | Risque | Action |
|---|---|---|---|---|
| `PageRole.R1_ROUTER` | `R1_ROUTER` | canon | — | garder |
| `PageRole.R2_PRODUCT` | `R2_PRODUCT` | canon | — | garder |
| `PageRole.R3_BLOG` | anti-pattern legacy | interdit comme verite metier | fort | scinder logiquement entre `R3_CONSEILS` et `R6_GUIDE_ACHAT` selon route |
| `PageRole.R4_REFERENCE` | `R4_REFERENCE` | canon | — | garder |
| `PageRole.R5_DIAGNOSTIC` | `R5_DIAGNOSTIC` | canon | — | garder |
| `PageRole.R6_GUIDE_ACHAT` | `R6_GUIDE_ACHAT` | canon | — | garder |
| `PageRole.R6_SUPPORT` | support applicatif | hors matrice editoriale coeur | faible | garder localement |
| `PageRole.RX_CHECKOUT` | applicatif | hors matrice editoriale coeur | — | garder hors canon SEO principal |

---

# 12. Table canonique — support / applicatif hors matrice editoriale coeur

Ces surfaces existent mais ne doivent pas etre melangees a la matrice canonique editoriale R0-R8.

| Surface | Statut |
|---|---|
| login / register | support applicatif |
| checkout / cart / payment return | applicatif transactionnel hors matrice editoriale |
| 404 / gone | support systeme |
| mentions legales / confidentialite | support juridique |
| contact | support relationnel |

## Regle
Ces surfaces peuvent garder des roles techniques locaux, mais elles ne redefinissent pas la matrice editoriale canonique.

---

# 13. Canon final — legacy → canon

## 13.1 Table courte de gel

| Legacy | Canon |
|---|---|
| `R1_pieces` | `R1_ROUTER` |
| `R3_conseils` | `R3_CONSEILS` |
| `R3_guide` | `R6_GUIDE_ACHAT` |
| `R3_guide_achat` | `R6_GUIDE_ACHAT` |
| `R4_reference` | `R4_REFERENCE` |
| `R4_GLOSSARY` | `R4_REFERENCE` |
| `R5_diagnostic` | `R5_DIAGNOSTIC` |
| `R6_GUIDE_ACHAT` | `R6_GUIDE_ACHAT` |
| `R6_BUYING_GUIDE` | `R6_GUIDE_ACHAT` |
| `R7_BRAND` | `R7_BRAND` |
| `R8_VEHICLE` | `R8_VEHICLE` |
| `R9` | supprime |
| `R3_BLOG` | anti-pattern legacy — desambiguiser obligatoirement |
| `R6` | interdit sans suffixe |
| `R3` | interdit sans suffixe |

---

# 14. Regles de gel

1. Aucun nouveau fichier, agent, brief, prompt, contrat ou service ne doit creer un nouveau role hors `R0..R8`.
2. Aucun nouveau code ne doit reintroduire `R9`.
3. Toute occurrence de `R3_guide` ou `R3_guide_achat` doit etre lue et documentee comme `R6_GUIDE_ACHAT`.
4. Toute occurrence de `R3_conseils` doit etre lue comme `R3_CONSEILS`.
5. Toute occurrence de `R3_BLOG` est un **anti-pattern legacy** — elle doit etre desambiguisee obligatoirement en `R3_CONSEILS` ou `R6_GUIDE_ACHAT`.
6. Toute decision de QA, purete, diversite, blocage, review, publication releve de `G*`, jamais d'un role `R*`.
7. Les `page_type` et `page_role` legacy peuvent subsister en base tant qu'un mapping canonique explicite existe.
8. Le canon documentaire prevaut sur les labels legacy techniques.
9. **Non-creation d'alias libres** : aucun nouveau role, alias, libelle metier ou suffixe local ne peut etre introduit sans rattachement explicite a un role canonique R0..R8, ou classification explicite hors matrice editoriale coeur.
10. **Suffixes obligatoires** : les labels ambigus sans suffixe metier explicite (`R3`, `R6`, `R4`, `R5`) sont interdits dans toute nouvelle doc, tout nouveau contrat, tout nouveau prompt, tout nouvel agent et tout nouveau code.

---

# 15. Verdict final

## Matrice role canonique figee
- `R0_HOME`
- `R1_ROUTER`
- `R2_PRODUCT`
- `R3_CONSEILS`
- `R4_REFERENCE`
- `R5_DIAGNOSTIC`
- `R6_GUIDE_ACHAT`
- `R7_BRAND`
- `R8_VEHICLE`

## Couche gouvernance figee
- `G1_PURETE`
- `G2_DIVERSITE`
- `G3_ANTI_CANNIBALISATION`
- `G4_PUBLICATION_CONTROL`
- `G5_REVIEW_ESCALATION`

## Legacy officiellement declasse
- `R3_guide`
- `R3_guide_achat`
- `R3_BLOG` sans sous-qualification
- `R6` sans suffixe
- `R3` sans suffixe
- `R9`

---

_Derniere mise a jour: 2026-03-14_
_Source: code search backend + role-matrix.md V4 + role-implementation-map.md V1.1.0_
