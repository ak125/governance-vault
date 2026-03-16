# Cadre canonique des phases — Pipeline RAG v2

> Version figee : 2026-03-14 v7

## Principe directeur

Le pipeline ne confond jamais : faire entrer / stabiliser / autoriser / produire.

Les phases ciblent des roles R* (metier/surface). Les controles G* (gouvernance transverse) peuvent intervenir a chaque phase mais ne remplacent jamais la fonction de la phase.

## Matrice des phases

| Phase | Nom canonique | Finalite | Nature | Peut ecrire ? | Peut muter la ressource canonique ? | Ecritures autorisees | Interdit principal | Bloque l'aval ? |
|-------|--------------|----------|--------|---------------|-------------------------------------|----------------------|-------------------|-----------------|
| 1 | Ingestion securisee | Faire entrer sans corruption | technique | oui | oui, dans le perimetre d'entree | stockage, sync, provenance, logs | toute ecriture metier | oui |
| 1.5 | Normalisation canonique | Stabiliser l'identite canonique sans muter le sens metier | structurelle | oui | oui, sur identite et mapping | identite canonique, alias, mapping, anti-collision | toute generation metier, mutation du sens metier | oui |
| 1.6 | Admissibilite metier | Qualifier les roles R* candidats et borner l'usage aval | decisionnelle | oui | non sur le fond, oui sur les verdicts | verdicts, scores, limitations, policies | toute generation / publication | oui |
| 2 | Exploitation metier controlee | Produire les artefacts metier | metier | oui | non sur la source brute, oui sur les derives | drafts, sections, contracts, assemblage metier | contourner 1 / 1.5 / 1.6 | oui |

## Tableau canonique — entrees / sorties / blocages / garde-fous

| Phase | Fonction canonique | Entrees autorisees | Sorties autorisees | Blocages natifs | Garde-fous G1 a G5 |
|-------|-------------------|-------------------|-------------------|-----------------|---------------------|
| 1 | Ingestion securisee | sources brutes (PDF, URL, markdown, CSV, JSON, exports DB, medias, documents techniques, corpus SEO, fichiers RAG) | fichier stocke, enregistrement DB sync, metadonnees minimales, provenance tracable, log d'ingestion | provenance absente, collision destructive, ecriture sauvage, sync incomplete, source illisible/corrompue | G1 purete provenance. G2 non bloquant, signal faible uniquement. G3 collision destination potentielle. G4 interdit ecriture aval si provenance KO. G5 escalation si doute source |
| 1.5 | Normalisation canonique | sorties validees de phase 1 uniquement | matiere canonisee, identite canonique stabilisee, mapping de champs, typologie source stabilisee, conventions de nommage unifiees, structure exploitable par les phases aval | structure non reconciliable, mapping ambigu, champs critiques manquants, collision de schema, perte de tracabilite, fusion destructive | G1 empeche changement de nature metier. G2 repere doublons structurels. G3 repere collisions inter-surfaces. G4 interdit passage aval si structure canonique non stabilisee. G5 review si arbitrage necessaire |
| 1.6 | Admissibilite metier | matiere canonisee issue de phase 1.5 | verdict d'admissibilite (ADMISSIBLE, ADMISSIBLE_AVEC_LIMITES, INCOMPLETE, AMBIGU, BLOCKED, REVIEW_REQUIRED), role R* candidat qualifie, niveau de confiance, limites d'usage, besoins d'enrichissement | role non determinable, matiere insuffisante, conflit inter-roles, dependance vehicule/contexte non resolue, risque de cannibalisation fort, manque de preuve matiere | G1 verifie purete de role. G2 verifie risque de quasi-duplicate. G3 verifie frontieres R/R. G4 interdit phase 2 sans admissibilite explicite. G5 escalation si ambiguite metier |
| 2 | Generation metier ciblee | uniquement matiere declaree admissible par phase 1.6 + contraintes de role + contrats de sections + eventuels briefs | artefact metier ciblant un role R* : brief, contrat rempli, draft structure, blocs de sections, liens internes, metadonnees du role | tentative de generation sans admissibilite, violation de role, contrat incomplet, matiere insuffisante, contenu hors frontiere, score/qualite insuffisants | G1 purete de role. G2 diversite. G3 anti-cannibalisation. G4 publication control (PASS/REVIEW/BLOCK). G5 review ou escalation humaine |

## Lecture canonique par phase

### Phase 1

Entree : source brute.
Sortie : source securisee et tracable.
Question : "Peut-on faire entrer cette matiere dans le systeme sans l'abimer ni corrompre l'existant ?"

### Phase 1.5

Entree : source securisee.
Sortie : matiere canonique.
Question : "Peut-on rendre cette matiere stable, comparable et exploitable sans lui faire dire autre chose ?"

### Phase 1.6

Entree : matiere canonique.
Sortie : admissibilite metier.
Question : "Cette matiere a-t-elle le droit d'alimenter un role principal unique R*, et lequel ?"

### Phase 2

Entree : matiere admissible pour un role R*.
Sortie : artefact metier.
Question : "Peut-on produire un artefact metier propre et pur pour ce role ?" (la publication releve de G4)

## Verifications obligatoires par phase

### Phase 1 — Ingestion securisee

#### P1. Provenance
- la source doit etre identifiable
- la provenance doit etre attachable a l'artefact
- l'origine ne doit pas etre ambigue

#### P2. Securite d'ecriture
- ecriture uniquement dans les zones autorisees
- aucune ecriture hors perimetre
- aucun overwrite implicite non controle
- aucune ecriture non atomique si un fichier existe deja

#### P3. Non-destruction
- pas d'ecrasement sauvage
- pas de fusion silencieuse
- pas de remplacement sans politique explicite
- pas de collision destructive entre plusieurs sources

#### P4. Sync DB
- la representation DB doit etre coherente avec le stockage disque / objet
- les champs de provenance doivent etre presents
- les mappings minimaux doivent etre persistes

#### P5. Tracabilite minimale
- `source_url`, `truth_level`, `source_type`
- `gamme_aliases` ou equivalent si resolu
- identifiant d'ingestion / job / timestamp

### Phase 1.5 — Normalisation canonique

La phase 1.5 stabilise la structure et l'identite canonique de la matiere.

#### N1. Normalisation des identifiants
- slugs, aliases, ids metier, cles de mapping, conventions de chemins

#### N2. Normalisation des metadonnees
- `source_url`, `source_type`, `truth_level`, `verification_status`
- `doc_family`, `updated_at`, `lifecycle.stage`

#### N3. Normalisation de structure
- frontmatter / schema minimal coherent
- hierarchie stable des blocs
- alignement des noms de champs
- suppression des variantes parasites de structure

#### N4. Normalisation semantique
- eviter qu'un meme concept ait 3 noms concurrents
- eviter qu'un role soit exprime par plusieurs taxonomies incompatibles
- eviter les collisions entre "guide achat" et "R6", entre "conseils" et "R3", etc.

#### N5. Separation des couches
- matiere source / matiere enrichie / prompts-agents / contrats-schemas / rendus-sorties / QA-gouvernance

### Phase 1.6 — Admissibilite metier

#### A1. Unicite de promesse centrale
La matiere doit porter une promesse dominante compatible avec un seul role cible principal.

#### A2. Suffisance minimale
La matiere doit etre suffisante pour produire ce role sans invention forte ni remplissage artificiel.

#### A3. Compatibilite d'intention
La matiere doit correspondre a l'intention utilisateur principale du role cible.

#### A4. Non-collision inter-roles
La matiere ne doit pas etre simultanement mieux expliquee par plusieurs roles concurrents sans arbitrage.

#### A5. Admissibilite operationnelle
La matiere doit etre exploitable par la phase 2 sans rebasculer en collecte amont.

## Loi de pipeline

**Loi absolue** : aucune phase superieure ne peut ecrire sur le plan metier si la phase precedente n'a pas valide son propre contrat.

**Formulation durcie** : aucune phase n'a le droit de compenser une phase amont non validee par une logique locale.

Consequences :
- Aucune phase > 1 sans provenance validee et securite d'ecriture validee
- Aucune phase > 1.5 sans identite canonique stabilisee
- Aucune phase > 1.6 sans admissibilite metier explicite
- Aucune phase 2 sans bornes de role et bornes de preuve

## Invariants de gouvernance

### A — Non-destruction
Aucune phase avant la phase 2 ne doit produire d'ecriture metier destructrice.

### B — Provenance d'abord
Toute ressource utilisee par l'aval doit avoir une provenance lisible et verifiable.

### C — Identite avant usage
Une ressource non canonisee ne peut jamais etre utilisee comme source metier.

### D — Admissibilite avant production
Une ressource non admise ne peut jamais alimenter un role R0-R8.

### E — Separation des responsabilites
- Phase 1 ne decide pas du role
- Phase 1.5 ne redige pas
- Phase 1.6 ne publie pas
- Phase 2 ne revalide pas la securite d'entree a la place de la phase 1

### F — Pas de correction silencieuse
Toute ambiguite, collision, insuffisance ou contradiction doit produire soit une resolution explicite, soit un blocage explicite, soit une escalade explicite. Jamais une absorption silencieuse.

### G — Decision tracable
Toute decision bloquante ou autorisante prise en phase 1.5, 1.6 ou 2 doit etre :
- attribuable
- justifiable
- horodatee
- rejouable au minimum en audit

## Contrats de passage entre phases

### 1 -> 1.5
La phase 1.5 ne demarre que si :
- la ressource est ingeree
- la provenance minimale existe
- la ressource n'est pas quarantined/rejected
- la securite d'ecriture est validee

### 1.5 -> 1.6
La phase 1.6 ne demarre que si :
- la ressource a une identite canonique
- les alias sont stabilises
- les collisions sont resolues ou explicitement escaladees
- le mapping technique minimal est coherent

### 1.6 -> 2
La phase 2 ne demarre que si :
- les roles autorises sont definis
- les limites d'usage sont definies
- les blocs interdits sont connus
- le statut final n'est pas BLOCKED
- `phase2Eligible = true`

## Etats de sortie canoniques par phase

| Phase | Etats |
|-------|-------|
| 1 | `INGESTED_SAFE`, `INGESTED_WITH_WARNINGS`, `BLOCKED_WRITE_SAFETY`, `BLOCKED_PROVENANCE`, `BLOCKED_SYNC`, `QUARANTINED` |
| 1.5 | `NORMALIZED`, `NORMALIZED_WITH_WARNINGS`, `BLOCKED_SCHEMA_DRIFT`, `BLOCKED_TAXONOMY_CONFLICT`, `BLOCKED_SEMANTIC_COLLISION` |
| 1.6 | `ADMISSIBLE_R0`..`ADMISSIBLE_R8`, `BLOCKED_ROLE_AMBIGUITY`, `BLOCKED_INPUT_INSUFFICIENCY`, `BLOCKED_ROLE_COLLISION`, `ESCALATE_REVIEW` |
| 2 | `GENERATED_ROLE_PURE`, `GENERATED_WITH_WARNINGS`, `BLOCKED_BY_GUARDRAILS`, `HELD_FOR_REVIEW`, `READY_FOR_PUBLICATION_DECISION` |

## Formulation canonique

Phase 1 protege l'entree.
Phase 1.5 protege l'identite.
Phase 1.6 protege l'usage.
Phase 2 borne la production et transforme seulement ce qui a ete admis.

## Garde-fous G1 a G5 figes

| Garde-fou | Nom canonique | Fonction transverse | Peut bloquer ? | Peut publier ? |
|-----------|--------------|---------------------|----------------|----------------|
| G1 | Purete | garantit qu'un contenu reste dans son role cible et n'empiete pas sur un autre | oui | non |
| G2 | Diversite | evite repetition, duplication, similarite excessive, footprints | oui | non |
| G3 | Anti-cannibalisation | empeche collisions entre surfaces, intentions et clusters | oui | non |
| G4 | Publication Control | decide publish / hold / block / noindex / review gate | oui | oui |
| G5 | Review / Escalation | sort les cas ambigus ou a risque vers arbitrage humain ou workflow de review | oui | non |

## Regles de dependance figees

1. Aucune phase > 1 ne peut ecrire du contenu si la phase 1 n'a pas valide la provenance et la securite d'ecriture.
2. Aucune phase > 1.5 ne peut travailler sur une matiere dont l'identite et la structure canoniques ne sont pas stabilisees.
3. Aucune phase 2 ne peut demarrer sans verdict explicite de phase 1.6.
4. Aucune couche G* ne constitue un role metier ni une destination editoriale.
5. Tout contenu genere cible un role R*, jamais une couche G*.
6. Toute decision publish / hold / block releve de G4, pas de la phase elle-meme.
7. Aucune phase ne peut compenser silencieusement un blocage amont par une logique locale de rattrapage.

## Regles d'implementation canoniques

**Regle A — Aucun saut de phase** : aucune phase aval ne doit compenser une phase amont non validee.

**Regle B — Role unique principal** : toute matiere admise doit cibler un seul role principal.

**Regle C — G* ne produit pas la promesse** : les couches G* controlent, mais ne deviennent jamais la destination metier.

**Regle D — Pas d'ecriture sauvage** : aucune ecriture metier n'est autorisee sans validation Phase 1.

**Regle E — Pas de qualification avant normalisation** : aucune decision de role n'est autorisee avant Phase 1.5.

**Regle F — Pas de generation avant admissibilite** : aucune generation metier n'est autorisee avant Phase 1.6.

**Regle G — Toute publication est une decision G4** : produire n'est pas publier. La publication releve toujours de G4.

**Regle H — Decision tracable** : toute decision de blocage, admissibilite, limitation, hold, review ou publication doit etre attribuable, justifiable, horodatee, persistee et rejouable en audit.

**Regle I — Pas de rattrapage silencieux** : aucune phase ne peut compenser silencieusement une insuffisance ou une ambiguite d'une phase amont par une logique locale de rattrapage.

## Version courte ultra-canonique

| Phase | Verbe canonique | Objet | Resultat |
|-------|----------------|-------|----------|
| 1 | securiser | la source | matiere ingeree sans corruption |
| 1.5 | normaliser | la matiere | matiere canonique |
| 1.6 | admettre | la matiere vers un role R* | verdict metier |
| 2 | generer | la surface R* | artefact metier |

## Raffinements canoniques R1-R4

### R1 — Distinction ecriture / mutation canonique

Avoir le droit d'ecrire ne signifie pas avoir le droit de muter la ressource canonique.
Les phases 1, 1.5, 1.6 et 2 peuvent toutes produire des ecritures, mais seules certaines peuvent modifier directement l'etat canonique de reference, et uniquement dans leur perimetre autorise.

| Phase | Peut ecrire | Peut muter la ressource canonique |
|-------|-------------|-----------------------------------|
| 1 | oui | oui, dans le perimetre d'entree |
| 1.5 | oui | oui, sur identite et mapping |
| 1.6 | oui | non sur le fond, oui sur les verdicts |
| 2 | oui | non sur la source brute, oui sur les derives |

### R2 — Distinction statut / passage

Le statut d'une phase decrit le verdict de cette phase sur son propre contrat.
L'autorisation de passage decrit les actions reellement autorisees pour la phase suivante.
Aucun aval ne doit inferer ses droits uniquement a partir du statut.

Implementation : `phase2Eligible`, `publicationEligible`, `allowedNextPhaseActions[]`

### R3 — Primary generation eligibility (5 niveaux)

Une ressource admissible pour un role n'est pas automatiquement eligible comme base primaire de generation.

| Niveau | Signification |
|--------|--------------|
| `primary_publication_candidate` | source principale + publication directe |
| `primary_generation_allowed` | source principale de generation |
| `primary_generation_limited` | source principale avec limites |
| `support_only` | support/enrichissement uniquement |
| `blocked` | interdit |

Implementation : `primaryGenerationLevel` dans `RoleSufficiencySchema`

### R4 — Decision tracable (Invariant G)

Toute decision structurante prise a partir de la phase 1.5 doit etre attribuable, justifiable, horodatee, persistee et rejouable en audit.

Implementation : `DecisionTrace` (decisionId, decidedBy, decidedAt, pipelineVersion, rulesetVersion) dans `ReadinessRecord`

## Implementation

| Phase | State machine | Types | Service | Migration |
|-------|--------------|-------|---------|-----------|
| 1 | `rag-state.types.ts` (PHASE1_*) | `rag-contracts.types.ts` | `rag-foundation-gate.service.ts` | `20260314_foundation_gate.sql` |
| 1.5 | `rag-state.types.ts` (PHASE15_*) | `rag-contracts.types.ts` | `rag-normalization.service.ts` | `20260315_phase15_normalization.sql` |
| 1.6 | `rag-state.types.ts` (PHASE16_*) | `rag-readiness.types.ts` | `rag-admissibility-gate.service.ts` | `20260316_phase16_admissibility_gate.sql` |
| 2 | `rag-state.types.ts` (PHASE2_*) | `rag-exploitation.types.ts` | (a venir) | `20260317_phase2_exploitation.sql` |
