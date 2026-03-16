# Phase 2 — Canon final durci

> **Version** : 1.1.0
> **Date** : 2026-03-14
> **Statut** : CANONIQUE
> **Pre-requis** : Phase 1 + Phase 1.5 + Phase 1.6 + Phase 2A

---

## Definition canonique

Phase 2 = systeme gouverne de production d'une surface R* unique, qui orchestre l'execution, distille la preuve, genere sous contrat, assemble proprement, rafraichit sans degrader, structure URL et maillage, audite en profondeur, puis n'ecrit qu'en etat versionne, tracable et publiable uniquement sous controle de G4.

Elle ne commence que si l'amont a deja garanti :

- **Phase 1** : provenance sure, stockage sur, sync sure, non-destruction
- **Phase 1.5** : normalisation canonique, separation R* / G*
- **Phase 1.6** : admissibilite metier vers un role unique
- **Phase 2A** : projection legacy → canon stabilisee

La Phase 2 ne "redige" donc pas seulement. Elle :

- orchestre
- genere
- assemble
- rafraichit
- distille le RAG
- structure les URLs / liens
- controle
- prepare
- ecrit sous conditions

---

## Axiome de la Phase 2

Toute sortie Phase 2 doit viser une promesse centrale unique portee par un role R*.
Aucune couche G* ne peut devenir une cible de production.

- **R* = ce qu'on produit**
- **G* = ce qui juge, bloque, limite, score, escalade**

---

## Regle supreme

La Phase 2 ne peut jamais compenser un amont non fiabilise.
Si un defaut structurel vient de 1 / 1.5 / 1.6 / 2A, elle doit rebloquer en amont.

---

## Invariants globaux de la Phase 2

### I1 — Contrat actif unique

Toute execution Phase 2 doit etre rattachee a un seul role R* principal et a un seul contrat actif principal. Cela evite la double lecture du contrat, le mix de section packs et la contamination entre modeles voisins.

### I2 — No raw-to-final

Aucune donnee brute, normalisee seule, ou evidence pack non valide ne peut etre promue directement en sortie finale de surface. Tout doit passer par la chaine P2.2 → P2.3 → P2.7 → P2.8.

### I3 — Best-version protection

Aucune regeneration ou refresh ne peut remplacer une version jugee meilleure sans decision explicite de gouvernance. Le score guard empeche la regression automatique.

### I4 — Decision tracabilite

Toute decision Phase 2 de generation, skip, refresh, hold, block, write, publication candidate ou escalation doit etre :
- attribuable (quel acteur / service / agent)
- horodatee
- persistee
- justifiable (raison explicite)
- rejouable en audit

---

## Architecture interne canonique — 8 sous-blocs obligatoires

### P2.1 — Orchestration d'execution

**Mission** : definir quelle chaine concrete doit etre executee pour une surface R* donnee.

**Verbe canonique** : orchestrer

**Ce que ce bloc decide** : quel prompt, quel skill, quel agent, quel service, quel planner, quel validator, quel assembler, quel ordre, quelle granularite, quelle politique d'arret.

**Modes d'execution canoniques** (liste fermee) :

| Mode | Description |
|------|-------------|
| `create` | Creation initiale d'une surface |
| `regenerate` | Regeneration complete d'une surface existante |
| `refresh_partial` | Refresh cible sur sections faibles |
| `refresh_full` | Refresh complet de toutes les sections |
| `repair` | Correction ciblee d'un defaut identifie |
| `qa_only` | Audit QA sans generation |
| `hold_only` | Mise en hold explicite sans action |

Tout `execution_mode` doit appartenir a cette liste. Les modes implicites sont interdits.

**Entrees minimales** :
- role canonique cible R*
- contrat cible actif
- artefact cible
- sorties 2A
- policy d'execution
- policy de write
- etat actuel de la surface

**Traitements** :
- selectionner le pipeline adapte au role
- determiner le mode d'execution (liste fermee ci-dessus)
- decouper les responsabilites : planner, generator, validator, assembler
- interdire les executions non alignees au role

**Sorties** : execution_plan, execution_mode, contract_version, write_mode, role_lock_status, selected_agents, selected_prompts, selected_skills, stop_policy, escalation_policy

**Blocages** : role non unique, contrat absent ou multiple, repo reel contradictoire, moteur d'execution non aligne, legacy non resolu, mode non canonique

**G dominants** : G1, G4, G5

**Interdit central** : lancer une generation "a la volee" sans contrat ni role

---

### P2.2 — Generation structuree

**Mission** : produire les blocs metier admissibles pour la surface R*, et rien d'autre.

**Verbe canonique** : generer

**Ce que ce bloc couvre** : titres, H2/H3, sections, rich text, CTA, FAQ, anchors, meta title / meta desc, internal link candidates, media briefs textuels, variantes sectionnelles controlees.

**Section eligibility** (etat par section) :

| Etat | Description |
|------|-------------|
| `ELIGIBLE` | Section autorisee, evidence suffisante |
| `ELIGIBLE_WITH_LIMITS` | Section autorisee avec contraintes lexicales ou de profondeur |
| `BLOCKED` | Section explicitement interdite pour ce role |
| `MISSING_EVIDENCE` | Evidence insuffisante pour generer |
| `OUT_OF_ROLE` | Section hors perimetre du role cible |

**Entrees minimales** :
- brief admissible
- contrat de role
- evidence pack admissible
- limites lexicales
- sections autorisees / interdites
- seuils de refus

**Traitements** :
- evaluer l'eligibilite de chaque section
- produire par section ou sous-section (uniquement ELIGIBLE ou ELIGIBLE_WITH_LIMITS)
- respecter la structure attendue et les interdits du role
- produire seulement si l'evidence est suffisante
- generer en mode : full, partial, targeted, repair
- stopper si glissement de role

**Sorties** : structured_content, section_outputs, section_eligibility_map, claim_limit_map, generation_scope, meta_outputs, anchor_candidates, cta_candidates, link_candidates, generation_warnings

**Blocages** : evidence insuffisante, section non admissible, sortie hors contrat, contamination inter-roles, hallucination probable

**G dominants** : G1, G2, G3

**Interdit central** : texte libre non borne, ajout opportuniste de blocs hors contrat, invention hors preuve

---

### P2.3 — Assemblage de surface

**Mission** : transformer les elements generes en surface complete, coherente et consommable.

**Verbe canonique** : assembler

**Ce que ce bloc couvre** : ordre des sections, inclusion/exclusion des blocs, coherence globale, construction finale, preparation au rendu frontend/backend, mapping vers structure finale attendue.

**Distinction assembled_surface / renderable_surface** :
- `assembled_surface` : surface techniquement complete, toutes sections ordonnees
- `renderable_surface` : surface validee par QA et prete au rendu final. Une surface assemblee n'est pas automatiquement renderable.

**Entrees minimales** :
- structured_content
- contrat/schema
- regles d'ordre
- slots attendus
- contraintes de rendu

**Traitements** :
- ordonner les sections
- ajouter les blocs obligatoires
- retirer les blocs illegitimes (OUT_OF_ROLE, BLOCKED)
- verifier la couverture minimale (mandatory_slots_report)
- creer une version assemblee coherente
- preparer une structure stable pour QA

**Sorties** : assembled_surface, assembled_sections, mandatory_slots_report, out_of_role_sections_removed, structure_report, assembly_warnings

**Blocages** : bloc obligatoire manquant, structure illegale, incoherence d'ordre, incompatibilite frontend/backend

**G dominants** : G1, G4

**Interdit central** : publier directement apres generation brute

---

### P2.4 — Exploitation RAG avancee

**Mission** : transformer le RAG en evidence operationnelle filtree par role, au lieu d'un simple contexte brut.

**Verbe canonique** : distiller

**Ce que ce bloc couvre** : retrieval cible, sufficiency check, provenance check, distillation par role, mapping evidence → section, exclusion des preuves non admissibles, evidence pack final, safe extraction.

**Evidence grading** (niveaux de preuve) :

| Grade | Description | Usage autorise |
|-------|-------------|----------------|
| `strong` | Preuve verifiee, source fiable, provenance claire | Claims, faits, recommandations |
| `support-only` | Preuve correcte mais insuffisante pour un claim autonome | Contexte, support d'un claim fort |
| `weak-support` | Preuve faible ou source non ideale | Mention prudente uniquement |
| `forbidden-for-claim` | Preuve interdite (provenance douteuse, verite trop basse) | Exclusion totale |

**Entrees minimales** :
- fichiers RAG / DB RAG
- metadata de provenance
- truth level
- verification status
- role cible
- section cible
- regles de distillation

**Traitements** :
- recuperer les bons blocs
- filtrer selon le role
- grader chaque preuve (strong → forbidden-for-claim)
- attribuer chaque preuve a une section cible
- construire un evidence pack avec grades
- renvoyer les insuffisances et les conflits

**Sorties** : evidence_pack, section_evidence_map, evidence_grade_map, claim_eligibility_map, forbidden_evidence_items, rag_sufficiency_report, provenance_report, rag_conflict_report

**Blocages** : provenance non claire, verite trop faible, conflit entre sources, absence d'evidence pour sections critiques, evidence incompatible avec le role

**G dominants** : G1, G3, G5

**Interdit central** : traiter le RAG comme une verite implicite sans filtrage ni tracabilite

---

### P2.5 — Refresh intelligent

**Mission** : regenerer seulement ce qui doit etre regenere, sans ecrasement destructif.

**Verbe canonique** : rafraichir

**Ce que ce bloc couvre** : stale detection, trigger detection, refresh partiel, refresh cible, skip intelligent, comparaison avant/apres, score guard, protection du meilleur contenu, version-aware refresh.

**Entrees minimales** :
- version actuelle
- score actuel
- date/etat de fraicheur
- changements amont
- evidence update
- policy de refresh

**Traitements** :
- decider : skip, refresh_partial, refresh_full, hold
- cibler les sections faibles
- empecher les rewrites inutiles
- comparer candidate vs current (delta de score)
- appliquer best-version protection (invariant I3)
- conserver la meilleure version

**Sorties** : refresh_plan, refresh_targets, refresh_mode, current_vs_candidate_score_delta, best_version_protection_status, comparison_report, refresh_decision

**Blocages** : nouvelle version inferieure, refresh sans declencheur legitime, refresh integral alors qu'un patch suffit, rewrite destructif

**G dominants** : G2, G4, G5

**Interdit central** : full rewrite automatique par defaut

---

### P2.6 — URL / canonical / maillage

**Mission** : faire en sorte que la surface produite soit structurellement coherente, indexable et correctement reliee.

**Verbe canonique** : structurer

**Ce que ce bloc couvre** : URL pattern, slug policy, canonical policy, coherence route ↔ role, maillage interne, ancres internes, compatibilite legacy, coherence sitemaps / indexation.

**Entrees minimales** :
- role cible
- route model
- slug model
- contrat
- regles de linking
- legacy map

**Traitements** :
- generer ou valider l'URL
- verifier la canonical policy
- produire les ancres internes
- determiner les liens inter-roles admissibles
- eviter les liens interdits
- verifier la coherence SEO structurelle

**Sorties** : canonical_url, canonical_policy_status, indexability_status, cross_role_link_guard_status, route_validation_report, internal_link_map, anchor_map, legacy_compat_report

**Blocages** : URL incoherente avec le role, canonical absente, slug contradictoire, lien interdit inter-role, incoherence avec le mapping legacy

**G dominants** : G1, G3, G4

**Interdit central** : surface publiable sans coherence d'URL ni maillage

---

### P2.7 — QA editoriale profonde

**Mission** : controler la qualite reelle de la surface au-dela des simples checks techniques.

**Verbe canonique** : auditer

**Ce que ce bloc couvre** : purete de role, conformite au contrat, diversite, anti-cannibalisation, profondeur utile, genericity, claims non prouves, qualite du maillage, qualite des CTA, qualite des headings, qualite meta, qualite refresh, admissibilite publication.

**Entrees minimales** :
- surface assemblee
- contrat de role
- evidence pack
- contenu voisin / corpus voisin
- scores existants
- regles G1-G5

**Traitements** :
- auditer profondement
- scorer
- flagger
- bloquer
- mettre en hold
- escalader
- produire un verdict publication

**Sorties** : qa_report, qa_score, qa_decision (PASS | HOLD | BLOCK | ESCALATE), claim_risk_flags, genericity_score, blocking_flags, warning_flags, publication_decision, escalation_decision

**Blocages** : promesse centrale cassee, duplication trop forte, cannibalisation, manque de preuve, contenu trop generique, claims a risque, refresh degradant

**G dominants** : G1, G2, G3, G4, G5

**Interdit central** : promotion d'une surface non auditee en profondeur

---

### P2.8 — Ecriture controlee et preparation publication

**Mission** : persister uniquement ce qui a franchi la chaine complete, avec etat, version et tracabilite.

**Verbe canonique** : persister

**Ce que ce bloc couvre** : write controle, versioning, hold state, ready state, blocked state, tracabilite finale, stockage structure, preparation publication.

**Write modes canoniques** (liste fermee) :

| Mode | Description |
|------|-------------|
| `shadow_write` | Ecriture shadow (audit trail uniquement, pas de persistence visible) |
| `draft_write` | Ecriture en mode brouillon, non publie |
| `versioned_replace` | Remplacement versionne avec archivage de la version precedente |
| `hold_write` | Ecriture en etat hold (persiste mais bloque pour publication) |
| `blocked_no_write` | Ecriture refusee, rien n'est persiste |

**Distinction publication_candidate / publication_decision** :
- `publication_candidate` : booleen — la surface remplit-elle les conditions techniques ? (QA passee, version complete)
- `publication_decision` : verdict G4 — `HOLD | BLOCK | APPROVED | REVIEW`. Seul G4 peut promouvoir un candidat en decision APPROVED.

**Entrees minimales** :
- surface validee
- decision QA (qa_decision)
- write policy / write mode
- version precedente
- target storage
- publication policy

**Traitements** :
- ecrire dans le bon format selon le write mode
- versionner (increment content_version)
- archiver la version precedente si versioned_replace
- marquer l'etat final : draft, ready, hold, blocked
- separer publication_candidate (technique) de publication_decision (G4)
- preparer l'objet pour publication sans le promouvoir implicitement

**Sorties** : persisted_surface, new_version, write_mode, write_result, version_relation, final_state, publication_candidate_status, write_trace, publication_candidate

**Blocages** : ecriture sans QA, ecriture sans versionnement, tentative de publication implicite, etat final incoherent

**G dominants** : G4, G5

**Interdit central** : overwrite sauvage ou publication implicite

---

## Table compacte canonique — version durcie

| Sous-bloc | Verbe | Mission | Sortie cle | Blocage majeur | G dominants | Interdit central |
|-----------|-------|---------|------------|----------------|-------------|------------------|
| P2.1 Orchestration | orchestrer | choisir la chaine d'execution gouvernee | execution_plan | role flou, contrat absent, mode non canonique | G1 G4 G5 | execution sans role ni contrat |
| P2.2 Generation | generer | produire les blocs metier admissibles | structured_content | evidence insuffisante, hors contrat, derive de role | G1 G2 G3 | texte libre hors preuve |
| P2.3 Assemblage | assembler | composer une surface coherente | assembled_surface | bloc obligatoire manquant, structure illegale | G1 G4 | publication apres generation brute |
| P2.4 RAG avance | distiller | transformer le RAG en evidence exploitable par role | evidence_pack | provenance faible, conflit, manque de preuve critique | G1 G3 G5 | RAG brut = verite |
| P2.5 Refresh | rafraichir | regenerer sans degrader | refresh_decision | rewrite destructif, version candidate inferieure | G2 G4 G5 | full rewrite par defaut |
| P2.6 URL/maillage | structurer | assurer URL, canonical et maillage coherents | canonical_url, link_map | URL incoherente, canonical absente, lien interdit | G1 G3 G4 | surface publiable sans structure SEO |
| P2.7 QA profonde | auditer | juger profondement la surface avant promotion | qa_report, qa_decision | purete cassee, duplication, claims faibles, cannibalisation | G1 G2 G3 G4 G5 | promotion sans audit profond |
| P2.8 Ecriture | persister | ecrire sous etat/version/tracabilite | persisted_surface, final_state | write sans QA, overwrite, promo implicite | G4 G5 | ecriture sauvage |

---

## Entrees globales obligatoires

La Phase 2 complete exige au minimum :

1. `canonical_role` — role R* unique
2. `target_contract` — contrat cible actif unique (invariant I1)
3. `phase16_admissibility` = PASS
4. `phase2A_projection` = STABLE or ESCALATED
5. `provenance_status` = SAFE
6. `write_safety_status` = SAFE
7. `evidence_pack` or `rag_sufficiency` = PASS
8. `execution_policy` (avec execution_mode dans la liste fermee)
9. `refresh_policy`
10. `publication_policy`

---

## Sorties globales canoniques

La Phase 2 ne peut sortir que sous une forme strictement controlee :

- `READY_FOR_PUBLICATION`
- `READY_BUT_HOLD_G4`
- `BLOCKED_G1`
- `BLOCKED_G2`
- `BLOCKED_G3`
- `BLOCKED_UPSTREAM`
- `ESCALATE_G5`

---

## Matrice des dependances internes

| Bloc | Depend de | Ne peut pas court-circuiter |
|------|-----------|----------------------------|
| P2.1 | role + contrat + readiness | P2.7 / P2.8 |
| P2.2 | P2.1 + evidence admissible | P2.4 / P2.7 |
| P2.3 | P2.2 | P2.7 |
| P2.4 | provenance + role + section target | P2.1 |
| P2.5 | version actuelle + score + changements | P2.7 |
| P2.6 | role + route model + linking rules | P2.7 |
| P2.7 | P2.2 + P2.3 + P2.4 + P2.5 + P2.6 | aucun |
| P2.8 | P2.7 PASS ou HOLD explicite | aucun |

---

## 12 regles canoniques finales

1. Aucune execution sans role R* principal unique.
2. Aucune execution sans contrat actif principal unique (invariant I1).
3. Aucune generation sans evidence admissible et tracable.
4. Aucune section hors role ne doit survivre a la chaine P2.2 → P2.3.
5. Aucune donnee brute ou simplement normalisee ne peut etre promue directement en surface finale (invariant I2).
6. Aucun refresh destructif ou full rewrite automatique par defaut.
7. Aucune URL ou canonical incoherente avec le role.
8. Aucune promotion sans QA profonde explicite.
9. Aucune publication sans decision explicite de G4.
10. Toute ambiguite non tranchable part en G5.
11. Toute faiblesse amont rebloque en amont.
12. Toute sortie Phase 2 doit etre tracable, versionnee, reversible et auditable (invariant I4).
