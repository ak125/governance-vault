# Matrice canonique des roles R0-R8 + Couche de gouvernance G*

> Version figee : 2026-03-14 v5

## Statut de ce document

Ce document est la norme de classification canonique. Il gouverne :
la qualification des surfaces, les frontieres metier entre pages, les contracts,
les gates de purete, la generation, la validation, le maillage,
la prevention de cannibalisation, la gouvernance QA.

Aucun prompt, agent, script, pipeline, assembler, brief ou contract
ne doit redefinir librement un role hors de cette matrice.

Cette matrice est amont de la Phase 2.

## Regle mere de qualification

Un role canonique est attribue selon la promesse centrale dominante et non selon :
le nom historique du fichier, le template utilise, l'URL seule,
la densite du contenu, ou la presence de blocs secondaires.

## Lois canoniques globales

### Loi 1 — Unicite de promesse centrale
Chaque role repond a une promesse centrale unique.
Si une surface repond simultanement a deux promesses centrales, elle est mal qualifiee.

### Loi 2 — Un artefact = un role principal
Tout artefact porte un seul role principal. Les autres roles ne peuvent exister que comme maillage, renvoi, CTA secondaire ou support de comprehension.

### Loi 3 — Separation surface / intention / execution
Un role est defini par 3 axes : surface (ce que l'utilisateur voit), intention dominante (besoin a satisfaire), mode d'execution (navigation, information, decision, transaction, diagnostic, gouvernance).

### Loi 4 — Purete avant richesse
Une page moins riche mais pure est meilleure qu'une page plus riche mais hybride.

### Loi 5 — Aucun role aval ne corrige un role amont
La matrice est respectee dans l'ordre : Phase 1 (securite matiere) → Phase 1.5 (identite canonique) → Phase 1.6 (admissibilite metier) → Phase 2 (generation de role).

## Modele canonique d'un role R*

Ce modele s'applique aux roles metier/surface R0-R8.
La couche de gouvernance G* a son propre modele (voir section dediee).

Chaque role R* definit obligatoirement :
role_id, canonical_name, promise_core, central_question,
intent_dominant, primary_decision_mode, role_scope_level,
vehicle_dependency_level, commerciality_level, surface_type,
surface_visibility, admissible_sources, authorized_outputs,
forbidden_outputs, forbidden_dominant_signals,
authorized_linking, purity_gates, handoff_targets,
handoff_conditions, blocking_conditions.

## Table compacte

| Role | Nom | Promesse centrale | Intent | Decision mode | Dep. vehicule | Nature | Visibilite | Risque derive |
|------|-----|-------------------|--------|---------------|---------------|--------|------------|---------------|
| R0 | Home | orienter globalement | orientation | navigate | faible | hub global | public | hybridation excessive |
| R1 | Router gamme | trouver la bonne gamme pour le bon vehicule | navigation compatibilite | navigate | forte | navigation | public | glissement vers R2/R6 |
| R2 | Product | acheter la bonne reference compatible | transaction | buy | tres forte | listing commercial | public | derive editoriale |
| R3 | Conseils | intervenir correctement | agir | act | faible/moyenne | how-to | public | glissement vers R6/R5 |
| R4 | Reference | comprendre ce que c'est | comprendre | understand | faible | glossaire | public | glissement vers R3/R5 |
| R5 | Diagnostic | orienter un symptome | orienter | triage | faible/moyenne | diagnostic | public | glissement vers R3 |
| R6 | Guide d'achat | choisir sans erreur | choisir | choose | moyenne | pre-achat | public | glissement vers R2/R3/R4 |
| R7 | Brand | explorer une marque | navigation marque | navigate | moyenne | hub marque | public | glissement vers R8 |
| R8 | Vehicle | contextualiser un vehicule | contextualiser | contextualize | tres forte | fiche vehicule | public | glissement vers R1/R5 |

La serie R* est ouverte : R9, R10, R11... peuvent etre ajoutes pour de futurs roles metier.

## Definitions detaillees

### R0 — HOME / HUB GLOBAL

- **Promesse** : orienter l'utilisateur vers le bon parcours
- **Scope** : global
- **Question** : "Par ou commencer selon mon besoin ?"
- **Est** : porte d'entree, repartiteur de parcours, hub de decouverte
- **N'est pas** : page gamme, page produit, page symptome, guide d'achat detaille
- **Sources admissibles** : navigation globale, hubs metier, categories majeures, constructeurs
- **Sorties autorisees** : hero d'orientation, acces catalogue/marque/diagnostic/blog/recherche
- **Sorties interdites** : procedure detaillee, diagnostic detaille, transaction fine, definition technique profonde
- **forbidden_dominant_signals** : `["detailed_procedure", "symptom_tree", "transactional_listing", "deep_glossary", "buying_checklist"]`
- **Bascule** : besoin gamme → R1, besoin marque → R7, besoin vehicule → R8, besoin symptome → R5, besoin achat guide → R6
- **handoff_targets** : `[{target: R1, condition: "besoin gamme"}, {target: R7, condition: "besoin marque"}, {target: R8, condition: "besoin vehicule"}, {target: R5, condition: "besoin symptome"}, {target: R6, condition: "besoin guide achat"}]`

### R1 — ROUTER GAMME / NAVIGATION COMPATIBILITE

- **Promesse** : aider a trouver la bonne gamme pour le bon vehicule
- **Scope** : gamme
- **Question** : "Ou trouver la bonne piece pour mon vehicule ?"
- **Est** : page gamme, orientation vers compatibilite, selection, anti-erreur de filtrage, transition vers R2
- **N'est pas** : page produit, page achat guide, page how-to, page definition, page diagnostic
- **Sources admissibles** : gamme canonique, criteres de compatibilite, variantes, familles, taxonomie produit
- **Sorties autorisees** : hero gamme, selector, compat reminders, variantes, FAQ selection, safe table legere, renvois R3/R4/R5/R6
- **Sorties interdites** : prix detailles, stock, panier, procedure, symptomes, glossaire profond
- **forbidden_dominant_signals** : `["detailed_pricing", "basket_cta", "procedure_steps", "symptom_tree", "deep_glossary"]`
- **Gates de purete** : zero procedure, zero symptom-first, zero definition-first, zero conversion produit directe dominante
- **Bascule** : besoin transactionnel exact → R2, besoin definition → R4, besoin symptome → R5, besoin comment remplacer → R3, besoin comment choisir → R6
- **handoff_targets** : `[{target: R2, condition: "besoin transactionnel exact"}, {target: R4, condition: "besoin definition"}, {target: R5, condition: "besoin symptome"}, {target: R3, condition: "besoin comment remplacer"}, {target: R6, condition: "besoin comment choisir"}]`

### R2 — PRODUCT / LISTING TRANSACTIONNEL

- **Promesse** : permettre de consulter et acheter les references compatibles
- **Scope** : reference
- **Question** : "Quelles references puis-je acheter maintenant pour ce vehicule exact ?"
- **Est** : listing compatible, comparaison produit, prix, disponibilite, conversion
- **N'est pas** : routeur, guide d'achat editorial, tutoriel, diagnostic, fiche encyclopedique
- **Sources admissibles** : catalogue, compatibilite exacte, prix, stock, shipping, OEM/OES/equivalences, scoring produit
- **Sorties autorisees** : cartes produit, prix, stock, CTA panier, micro specs, badges, FAQ achat, reassurance
- **Sorties interdites** : tutoriel complet, arbre diagnostic, definition pure, guide editorial long, navigation large gamme
- **forbidden_dominant_signals** : `["procedure_flow", "symptom_tree", "deep_glossary", "editorial_guide", "gamme_navigation"]`
- **Gates de purete** : presence transactionnelle obligatoire, pas de langage R3/R4/R5 dominant
- **handoff_targets** : `[{target: R1, condition: "besoin navigation gamme"}, {target: R3, condition: "besoin tutoriel"}, {target: R4, condition: "besoin definition"}, {target: R6, condition: "besoin guide achat"}]`

### R3 — CONSEILS / HOW-TO / ENTRETIEN / REMPLACEMENT

- **Promesse** : aider a intervenir correctement sur une piece
- **Scope** : gamme
- **Question** : "Comment intervenir correctement, en securite, sur cette piece ?"
- **Est** : how-to, conseil pratique, entretien, remplacement, controle simple, post-intervention
- **N'est pas** : guide d'achat, definition, diagnostic profond, page produit
- **Sources admissibles** : procedure validee, securite, outils, etapes, anti-erreurs, controles post-montage, FAQ maintenance
- **Sorties autorisees** : sections procedurales, checklists, tables de controle, FAQ maintenance, CTA soft vers R1, liens R4/R5/R6
- **Sorties interdites** : prix/stock/panier, comparatif achat dominant, symptome-first dominant, definition-first dominante
- **forbidden_dominant_signals** : `["buying_checklist", "symptom_tree", "deep_glossary", "transactional_listing", "quality_tiers"]`
- **Gates de purete** : si besoin = "choisir quoi acheter" → sortie R3, si besoin = "comprendre ce que c'est" → sortie R3, si besoin = "identifier une panne" → sortie R3
- **handoff_targets** : `[{target: R6, condition: "besoin principal = choix avant achat"}, {target: R5, condition: "besoin principal = interpretation symptome"}, {target: R4, condition: "besoin principal = comprehension definitionnelle"}]`

### R4 — REFERENCE / DEFINITION / GLOSSAIRE

- **Promesse** : expliquer ce qu'est un terme ou un organe et eviter les confusions
- **Scope** : reference
- **Question** : "Qu'est-ce que c'est exactement ?"
- **Est** : definition, role mecanique, composition, limites, terminologie, confusions frequentes
- **N'est pas** : achat guide, how-to, diagnostic, page produit, page vehicule exacte
- **Sources admissibles** : definitions validees, composition, role, nomenclature, distinctions OEM/OES/IAM, confusions, FAQ encyclopedique
- **Sorties autorisees** : definition, composition, role, confusions, glossaire, FAQ encyclopedique, renvois R1/R3/R5/R6
- **Sorties interdites** : prix, stock, tutoriel, arbre de symptomes, checklist achat dominante
- **forbidden_dominant_signals** : `["procedure_flow", "symptom_orientation", "basket_cta", "buying_checklist", "transactional_listing"]`
- **Gates de purete** : zero procedure dominante, zero diagnostic dominant, zero transactionnel dominant
- **handoff_targets** : `[{target: R3, condition: "besoin = comment intervenir"}, {target: R5, condition: "besoin = interpreter un symptome"}, {target: R1, condition: "besoin = trouver la bonne gamme"}, {target: R6, condition: "besoin = choisir avant achat"}]`

### R5 — DIAGNOSTIC / SYMPTOMES / ORIENTATION PANNE

- **Promesse** : aider a orienter un symptome et prioriser les verifications
- **Scope** : symptom
- **Question** : "Que peut signifier ce symptome et que verifier d'abord ?"
- **Est** : symptome-first, orientation prudente, tri d'hypotheses, quick checks, risque/securite, decision d'escalade
- **N'est pas** : tutoriel, definition, guide d'achat, page produit, diagnostic atelier individualise complet
- **Sources admissibles** : symptomes, hypotheses, quick checks, safety gates, niveaux d'urgence, causes plausibles
- **Sorties autorisees** : symptomes, hypotheses, verifications rapides, actions immediates prudentes, signaux d'arret, renvois R3/R4/R1
- **Sorties interdites** : depose/repose detaillee, glossaire dominant, choix qualite/budget, conversion transactionnelle
- **forbidden_dominant_signals** : `["procedure_steps", "glossary_dominant", "quality_tiers", "basket_cta", "buying_checklist"]`
- **Gates de purete** : zero pas-a-pas dominant, zero definition dominante, zero guide achat dominant
- **handoff_targets** : `[{target: R3, condition: "besoin = comment intervenir"}, {target: R4, condition: "besoin = comprendre ce que c'est"}, {target: R1, condition: "besoin = trouver la bonne gamme"}]`

### R6 — GUIDE D'ACHAT

- **Promesse** : aider a choisir la bonne piece sans erreur avant commande
- **Scope** : gamme
- **Question** : "Comment choisir et commander la bonne piece sans me tromper ?"
- **Est** : guide d'achat, aide a la decision, compatibilite pre-achat, niveaux de qualite, pieges d'achat, criteres de comparaison, checklists avant commande
- **N'est pas** : tutoriel, diagnostic, definition, page produit listing, FAQ support generique
- **Sources admissibles** : selection.criteria, checklist achat, quality tiers, anti_mistakes, cross_gammes, budgets editoriaux, FAQ achat
- **Sorties autorisees** : decision blocks, quality tables, compatibility checklist, pitfalls, brands guide, when pro, FAQ achat, CTA vers R1
- **Sorties interdites** : pas a pas, symptomes/causes, glossaire dominant, panier/stock detaille
- **forbidden_dominant_signals** : `["procedure_steps", "symptom_tree", "deep_glossary", "transactional_listing", "stock_pricing"]`
- **Gates de purete** : zero R3 dominant, zero R5 dominant, zero R4 dominant, zero R2 dominant
- **handoff_targets** : `[{target: R2, condition: "decision prise, pret a acheter"}, {target: R3, condition: "besoin = comment remplacer"}, {target: R5, condition: "besoin = comprendre un symptome"}, {target: R4, condition: "besoin = definition technique"}]`

### R7 — BRAND / CONSTRUCTEUR / HUB MARQUE

- **Promesse** : aider a naviguer dans l'univers pieces d'une marque
- **Scope** : brand
- **Question** : "Comment explorer les pieces et vehicules lies a cette marque ?"
- **Est** : page constructeur, porte d'entree marque, hub de navigation, regroupement modeles/pieces/recherches
- **N'est pas** : fiche vehicule, page produit, how-to, guide d'achat, diagnostic
- **Sources admissibles** : marque, modeles, pieces populaires, top recherches, hubs compatibilite, blocs about brand
- **Sorties autorisees** : hero marque, top pieces, top vehicules, top recherches, raccourcis, compat guide leger, FAQ marque
- **Sorties interdites** : procedure, symptomes, listing transactionnel detaille, fiche vehicule profonde
- **forbidden_dominant_signals** : `["procedure_steps", "symptom_tree", "transactional_listing", "vehicle_deep_sheet", "buying_checklist"]`
- **handoff_targets** : `[{target: R8, condition: "besoin = fiche vehicule precise"}, {target: R1, condition: "besoin = trouver gamme compatible"}, {target: R2, condition: "besoin = acheter reference"}]`

### R8 — VEHICLE / FICHE VEHICULE

- **Promesse** : donner la fiche contexte d'un vehicule pour guider entretien, recherche et compatibilite
- **Scope** : vehicle
- **Question** : "Quelles sont les caracteristiques utiles de ce vehicule ?"
- **Est** : identite vehicule, motorisations, periodes, specificites, reperes entretien, points de vigilance, contexte de compatibilite
- **N'est pas** : produit, guide d'achat, tutoriel detaille, diagnostic complet, hub marque
- **Sources admissibles** : donnees vehicule, motorisations, periodes, known issues bornes, usure courante, reperes entretien, liaisons gammes
- **Sorties autorisees** : identite, versions, motorisations, reperes entretien, pieces courantes, liens R1/R3/R5/R6
- **Sorties interdites** : panier, prix, procedure longue, symptome-first dominant, brand hub
- **forbidden_dominant_signals** : `["basket_cta", "stock_pricing", "procedure_flow", "symptom_tree", "brand_hub_navigation"]`
- **handoff_targets** : `[{target: R1, condition: "besoin = trouver gamme"}, {target: R3, condition: "besoin = comment intervenir"}, {target: R5, condition: "besoin = interpreter symptome"}, {target: R7, condition: "besoin = explorer marque"}]`

## Tableau canonique — R0 a R8 entrees / sorties / interdits / G*

| Role | Promesse centrale exclusive | Entrees minimales | Sorties attendues | Interdits majeurs | Garde-fous G* | Bascule prioritaire | Contexte |
|------|---------------------------|-------------------|-------------------|-------------------|---------------|--------------------|----|
| R0 Home | orienter rapidement l'utilisateur vers les grandes portes d'entree du systeme | taxonomie principale, acces catalogue, acces marques, acces blog, acces diagnostic, signaux de reassurance, priorites business | page d'accueil de cadrage, navigation primaire, raccourcis de parcours, preuves de confiance, liens vers surfaces pivots | devenir page catalogue detaillee, article profond, page diagnostic, guide d'achat detaille | G1, G3, G4 | R1 / R7 / R8 / R5 / R6 | global |
| R1 Router gamme | aider a trouver la bonne gamme pour le bon vehicule | gamme identifiee, criteres de compatibilite, logique de selection vehicule, variantes principales, wording de selection | page de routage gamme, orientation vers selection vehicule, acces vers R2, maillage vers R3/R4/R5/R6 | prix/stock pousses comme R2, diagnostic comme R5, definition encyclopedique comme R4, procedure de montage comme R3, guide d'achat complet comme R6 | G1, G3, G4 | R2 / R3 / R4 / R5 / R6 | vehicule/gamme |
| R2 Product | permettre d'acheter la bonne reference compatible | vehicule ou contexte compatible, donnees produit, prix, stock, specs, equivalences, preuves transactionnelles | page produit ou listing transactionnel, CTA d'achat, prix, stock, compatibilite, attributs produit, cross-sell encadre | devenir routeur R1, faire du how-to R3, faire de la definition R4, faire du diagnostic R5 | G1, G3, G4 | R1 / R3 / R4 / R6 | transaction compatible |
| R3 Conseils | expliquer comment agir, remplacer, controler ou entretenir correctement | matiere procedurale fiable, etapes, outils, securite, erreurs frequentes, verifications finales, compatibilite minimale | contenu how-to, procedure structuree, checklist, FAQ maintenance, CTA doux vers gamme | definition pure R4, diagnostic oriente causes R5, page achat R6, push commercial R2, dependance forte au vehicule individuel non justifiee | G1, G2, G3, G4 | R4 / R5 / R6 | operation |
| R4 Reference | definir clairement un terme, une piece, un concept ou une notion technique | definition, role mecanique, composition, distinctions, confusions, limites, vocabulaire normalise | page de reference ou glossaire, contenu intemporel, distinctions semantiques, FAQ de comprehension, liens vers R1/R3/R5 | montage detaille R3, diagnostic R5, achat comparatif R6, transaction R2, dependance a un vehicule specifique | G1, G2, G3, G4 | R3 / R5 | notion |
| R5 Diagnostic | orienter l'utilisateur face a un symptome ou un signal anormal | symptome observable, signaux, quick checks, causes probables, niveaux de risque, actions prudentes, limites de certitude | page d'orientation diagnostic, hypotheses, signaux, drapeaux de risque, redirection vers R3/R4/R1 selon besoin | procedure detaillee R3, definition pure R4, vente directe R2, guide achat R6, personnalisation forte necessitant un outil | G1, G3, G4, G5 | R3 / R4 / outil | symptome |
| R6 Guide d'achat | aider a choisir et acheter la bonne piece sans se tromper | criteres de choix, compatibilite, references, niveaux de qualite, pieges d'achat, checklist avant commande, logique de pack | guide d'achat, arbre de choix, tableaux comparatifs, checklist achat, FAQ achat, CTA vers R1 | montage/how-to R3, diagnostic R5, definition pure R4, fiche transactionnelle R2, promesse de support generique R0 | G1, G2, G3, G4 | R2 / R3 / R4 | pre-achat |
| R7 Brand | orienter et structurer l'entree par constructeur ou marque | entite marque, modeles cles, gammes populaires, acces vehicules, shortcuts de navigation, contenus d'orientation marque | page marque/constructeur, hub navigationnel, acces vers R8, R1 et univers de pieces, raccourcis recherches | devenir home R0, devenir R1 de gamme, devenir article R3, devenir reference R4, devenir page transactionnelle R2 | G1, G3, G4 | R8 / R1 | marque |
| R8 Vehicle | orienter a partir d'un vehicule precis vers les bonnes familles de pieces et contenus associes | identite vehicule, generation, motorisations, points d'usure, familles de pieces, specificites vehicule, acces catalogue | fiche vehicule, hub vehicule, acces gammes compatibles, acces R1/R2/R3/R4/R5 contextualises | devenir page marque R7, devenir diagnostic personnalise outil, devenir produit R2, devenir procedure detaillee R3, devenir glossaire R4 | G1, G2, G3, G4 | R1 / R2 / R5 / outil | vehicule |

## Lecture canonique par role

**R0** : orienter dans l'ecosysteme.
**R1** : trouver la bonne gamme pour le bon vehicule.
**R2** : acheter la bonne reference compatible.
**R3** : agir correctement sur la piece.
**R4** : comprendre ce qu'est la chose.
**R5** : orienter un symptome.
**R6** : choisir la bonne piece avant achat.
**R7** : entrer par la marque.
**R8** : entrer par le vehicule.

## Interdits structurants globaux

1. Un role R* ne porte qu'une promesse centrale exclusive.
2. Si le besoin principal derive vers une autre promesse, le contenu doit changer de role R*.
3. Un role R* peut mailler vers d'autres roles, mais ne doit jamais absorber leur fonction dominante.
4. Plus un contenu est ambigu entre plusieurs roles, plus G1, G3 et G5 deviennent bloquants.

## Garde-fous G* appliques aux roles

| Garde-fou | Fonction sur les roles |
|-----------|----------------------|
| G1 — Purete | verifie qu'un role reste dans sa promesse centrale exclusive |
| G2 — Diversite | evite duplication, similarite excessive, repetition structurelle ou semantique |
| G3 — Anti-cannibalisation | empeche deux roles de se battre pour la meme intention utilisateur |
| G4 — Publication Control | autorise, bloque, met en hold, ou degrade publication / indexation |
| G5 — Review / Escalation | sort les cas ambigus, dangereux ou non tranchables vers revue |

## Regle de separation role / gouvernance

Les roles R* decrivent des surfaces ou usages metier a promesse centrale exclusive.
La gouvernance n'est pas un role editorial ni un role de surface : elle constitue
une couche transversale de controle, de QA, de purete, de diversite et de decision
de publication.
Les identifiants R* sont reserves aux roles canoniques de contenu, surface ou usage metier.
La serie R* reste ouverte : R9, R10, R11... peuvent etre ajoutes pour de futurs roles metier.

## Couche de gouvernance transverse (G*)

La gouvernance garantit qu'un contenu est distinct, pur, tracable et publiable.
Question centrale : "Ce contenu peut-il exister sans collision ni derive de role ?"
Visibilite : internal — PAS un role editorial public.

| Gate | Nom | Fonction |
|------|-----|----------|
| G1 | Purete | Verifier qu'un artefact respecte un seul role R* dominant |
| G2 | Diversite | Verifier qu'un artefact n'est pas un doublon d'un autre |
| G3 | Anti-cannibalisation | Verifier qu'un artefact ne cannibalise pas une surface existante |
| G4 | Publication gate | Decider si un artefact est publiable (PASS/REVIEW/BLOCK) |
| G5 | Review / escalation | Aiguiller vers review humaine si score insuffisant |

**Sources admissibles** : fingerprints, versioning, neighbors, overlap scores, forbidden vocab, gates, decisions QA.
**Sorties autorisees** : PASS/REVIEW/BLOCK, score diversite, score purete, exclusions sitemap, file de review, logs QA.
**Sorties interdites** : contenu public metier principal.
**forbidden_dominant_signals** : `["editorial_content", "public_page", "transactional_listing", "procedure_steps", "user_facing_navigation"]`

### Regles d'implementation G*

**Regle G-1** : Un agent, script, brief, contract ou pipeline ne doit jamais traiter G* comme un role metier.
**Regle G-2** : Tout contenu genere doit cibler un role R0 a R8, jamais une couche G*.
**Regle G-3** : Toute decision de validation, blocage, score, review ou publication releve de G*, jamais d'un role R*.
**Regle G-4** : Les collisions entre surfaces se reglent par les controles G*, pas en creant un faux role supplementaire.

## Matrice de frontieres fortes

| Paire | Distinction |
|-------|------------|
| R3 vs R6 | R3 = comment intervenir / R6 = comment choisir avant achat |
| R4 vs R5 | R4 = qu'est-ce que c'est / R5 = que signifie ce symptome |
| R1 vs R2 | R1 = trouver la bonne gamme / R2 = acheter les references exactes |
| R7 vs R8 | R7 = univers marque / R8 = identite d'un vehicule precis |
| R5 vs outil | R5 = orientation generique / si vehicule+km+historique+contexte croise → hors role editorial, vers outil |

## Table de migration legacy → canonique

| Legacy / ancien nom | Canonique |
|---------------------|-----------|
| R3_guide_achat | R6 |
| R3 guide achat | R6 |
| guide achat R3 | R6 |
| purchase guide R3 | R6 |
| blog guide achat semantiquement pre-achat | R6 |
| R3_conseils | R3 |
| howto / conseil / remplacement | R3 |
| glossary / reference | R4 |
| diagnostic / observable / symptome | R5 |
| brand / constructeur | R7 |
| vehicle sheet / fiche vehicule | R8 |
| diversity / fingerprint / anti duplicate | G* (couche transverse) |
| R9 gouvernance | G* (R9 n'est plus un role canonique) |

**Regle dure** : le systeme ne doit plus produire de nouvelle ambiguite du type R3_guide_achat, R6_support, R5_conseil.

## Correspondance code actuelle

| Canonique | RoleId enum | PageType (legacy) | Notes |
|-----------|------------|-------------------|-------|
| R0 Home | R0_HOME | — | Pas de PageType |
| R1 Router | R1_ROUTER | R1_pieces | OK |
| R2 Product | R2_PRODUCT | — | OK |
| R3 Conseils | R3_CONSEILS | R3_conseils | OK |
| R3 Guide (how-to) | R3_GUIDE | R3_guide_howto | Renomme 2026-03-13 (ex R3_guide_achat) |
| R4 Reference | R4_REFERENCE | R4_reference | OK |
| R5 Diagnostic | R5_DIAGNOSTIC | R5_diagnostic | OK |
| R6 Guide achat | R6_GUIDE_ACHAT | R6_guide_achat | OK |
| R7 Brand | R7_BRAND | — | Ajout 2026-03-11 |
| R8 Vehicle | R8_VEHICLE | — | Ajout 2026-03 |
| ~~R9 Gouvernance~~ | R9_GOVERNANCE | — | DEPRECIE — remplace par couche G* (voir section dediee) |

## Formulation normative

La matrice R0-R8 est la norme canonique de qualification des roles metier.
La couche G* est la norme canonique de gouvernance transverse.
Ensemble, elles gouvernent la classification des surfaces, les frontieres metier,
les contracts, les gates de purete, la generation, la QA et la prevention
de cannibalisation.
Aucun systeme aval ne peut redefinir librement un role ou une gate
en dehors de ces deux referentiels.
Le critere principal de qualification est la promesse centrale exclusive du role.

## Lien avec les phases pipeline

Phase 1 garantit la matiere sure.
Phase 1.5 normalise et qualifie la matiere vers un role R*.
Phase 1.6 valide l'admissibilite metier d'ecriture vers un role R*.
Phase 2 genere une surface R* a partir de matiere validee.
G* = couche de controle appliquee autour et apres ces phases — pas une destination.

**Loi de verrouillage** : aucune phase > 1 ne peut ecrire du contenu si la provenance, l'identite canonique et l'admissibilite metier ne sont pas validees.

Detail complet : `.spec/00-canon/pipeline-phases.md` (matrice G* par phase, contrats de passage, statuts, invariants).
