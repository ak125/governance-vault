# Matrice canonique des phases — Foundation Gate durci

> Date : 2026-03-14
> Version : 1.0.0

## Principe directeur

Le pipeline ne doit jamais confondre : **stocker**, **rendre admissible**, **synthétiser**, **produire**, **publier**.

La chaîne canonique :

| Phase | Fonction |
|-------|----------|
| Phase 1 | Sécuriser et filtrer l'admissibilité documentaire |
| Phase 1.5 | Normaliser et stabiliser la structure / l'identité documentaire |
| Phase 1.6 | Décider l'admissibilité métier d'usage vers un rôle R* |
| Phase 2 | Fusionner, générer, assembler et préparer une surface métier |
| G* | Contrôler, bloquer, limiter, scorer, escalader, publier ou retenir |

---

## Phase 1 — Ingestion sécurisée et admissibilité documentaire

### Fonction

Faire entrer une doc dans le système, garantir sécurité/traçabilité/non-destruction, décider si admissible au pool métier.

### Ce que valide Phase 1

- doc stockable, lisible, auditable, comparable/scorable
- admissible ou non à l'exploitation métier

### Ce que Phase 1 ne fait pas

- ne fusionne pas les docs
- ne choisit pas un document gagnant
- ne synthétise pas la vérité métier
- ne génère aucun contenu final
- ne publie rien

### Pools canoniques

| Pool | Contenu | Usages |
|------|---------|--------|
| **Pool brut** | Toutes docs (admissibles + non admissibles, legacy, partial, failed) | Stockage, audit, scoring, comparaison, diagnostic |
| **Pool admissible métier** | `foundation_gate_passed = true` + sécurité validée + provenance acceptable | Retrieval, enrichissement, refresh, génération, écriture aval |

### Règle de non-blocage global

Une doc non admissible n'entraîne pas un blocage global de gamme. Blocage seulement si le pool admissible utile est vide ou insuffisant.

### États recommandés

`INGESTED_ADMISSIBLE` · `INGESTED_NON_ADMISSIBLE` · `BLOCKED_PROVENANCE` · `BLOCKED_WRITE_SAFETY` · `BLOCKED_SYNC` · `QUARANTINED` · `NO_RAG_DOCS_PRESENT` · `HOLD_FOUNDATION_POOL_EMPTY`

---

## Phase 1.5 — Normalisation canonique documentaire

### Fonction

Transformer une doc stockée en doc structurée, comparable, normalisée, stable, identifiée, gouvernable.

### Ce qu'elle verrouille

- identité canonique
- structure minimale commune
- nomenclature stabilisée
- taxonomie homogène
- séparation couches : source / enrichissement / contrat / rendu / gouvernance

### Ce qu'elle ne fait pas

- ne produit pas de vérité métier finale
- ne fusionne pas les meilleures informations
- ne publie pas

### Règle clé

Une doc peut être admissible en Phase 1 mais non exploitable tant que 1.5 n'a pas stabilisé sa structure/identité/taxonomie.

### États recommandés

`NORMALIZED` · `NORMALIZED_WITH_WARNINGS` · `BLOCKED_SCHEMA_DRIFT` · `BLOCKED_TAXONOMY_CONFLICT` · `BLOCKED_SEMANTIC_COLLISION`

---

## Phase 1.6 — Admissibilité métier d'usage

### Fonction

Décider si une matière (stockée + filtrée + normalisée) est admissible à l'usage métier pour un rôle R*.

### Ce qu'elle valide

- rôle principal unique R*
- suffisance minimale d'usage
- compatibilité intentionnelle
- absence de collision inter-rôles non résolue

### Ce qu'elle ne fait pas

- ne génère pas le contenu final
- ne fusionne pas les fragments
- ne publie pas

### Règle clé

Phase 1.6 ne juge pas "la meilleure doc". Elle juge si une matière issue du pool admissible peut servir un rôle métier.

### États recommandés

`ADMISSIBLE_R0` · `ADMISSIBLE_R1` · `ADMISSIBLE_R2` · `ADMISSIBLE_R3` · `ADMISSIBLE_R4` · `ADMISSIBLE_R5` · `ADMISSIBLE_R6` · `ADMISSIBLE_R7` · `ADMISSIBLE_R8` · `BLOCKED_ROLE_AMBIGUITY` · `BLOCKED_INPUT_INSUFFICIENCY` · `BLOCKED_ROLE_COLLISION` · `ESCALATE_G5`

---

## Phase 2 — Synthèse métier, génération et assemblage contrôlés

### Fonction

Première phase qui peut exploiter, fusionner, générer et assembler une surface métier.

### Règle centrale

Les phases aval ne fusionnent jamais des documents. Elles fusionnent des **fragments/signaux/informations admissibles** issus du pool admissible métier.

### Politique de fusion (ordre de priorité)

1. admissibilité documentaire
2. truth_level
3. verification_status
4. fraîcheur
5. coverage utile
6. résolution de conflit
7. qualité documentaire
8. confiance de provenance

### Ce que fait Phase 2

- retrieval métier sur pool admissible
- distillation evidence-first
- sélection fragments exploitables
- fusion meilleures informations admissibles
- génération sous contrat
- assemblage de surface
- QA profonde
- écriture versionnée et contrôlée
- préparation publication

### Cas de blocage

Écriture aval interdite si : pool admissible vide/insuffisant, rôle non admissible, structure non stabilisée, evidence pack insuffisant, collision critique non résolue, QA en échec, G4 en hold/block.

### États recommandés

`READY_FOR_PUBLICATION` · `READY_BUT_HOLD_G4` · `BLOCKED_G1` · `BLOCKED_G2` · `BLOCKED_G3` · `BLOCKED_UPSTREAM` · `ESCALATE_G5`

---

## Couche G* — Gouvernance transverse

G* ne produit pas de surface métier. G* juge, bloque, limite, score et décide.

| Couche | Fonction |
|--------|----------|
| G1 | Pureté de rôle |
| G2 | Diversité |
| G3 | Anti-cannibalisation |
| G4 | Publication control |
| G5 | Review / escalation |

### Règle canonique

Les couches G* ne sont jamais des destinations métier, ne remplacent jamais les rôles R*, ne définissent jamais la promesse centrale d'une surface, contrôlent la promotion — jamais la nature éditoriale cible.

---

## Table compacte finale

| Phase | Fonction | Objet traité | Résultat | Ce qu'elle décide | Ce qu'elle ne décide pas |
|-------|----------|-------------|----------|-------------------|--------------------------|
| 1 | Ingestion + filtre admissibilité | doc/source | doc stockée + admissible/non | sécurité, traçabilité, admissibilité doc | vérité métier, doc gagnante |
| 1.5 | Normalisation canonique | doc admissible/brute | doc structurée, identifiée | identité, structure, taxonomie | vérité métier, synthèse |
| 1.6 | Admissibilité métier | matière canonisée | rôle principal admissible/blocage | usage métier vers R* | meilleure synthèse finale |
| 2 | Synthèse + génération + assemblage | fragments admissibles | surface métier structurée | fusion, génération, QA, écriture | publication autonome |
| G* | Contrôle transverse | surfaces, flux | hold/block/score/escalation/publish | qualité, pureté, promotion | rôle métier cible |

---

## 6 Règles suprêmes

1. **Foundation** — Phase 1 filtre les docs ; elle ne choisit pas la vérité métier finale.
2. **Non-blocage global** — Une doc non admissible n'entraîne pas un blocage global de gamme.
3. **Pool admissible** — Seul le pool admissible alimente retrieval, synthèse, enrichissement, refresh et écriture aval.
4. **Fusion aval** — Les phases aval fusionnent les meilleures informations admissibles, pas des docs entières.
5. **Écriture protégée** — Aucune écriture métier aval ne peut utiliser une doc/evidence non admissible.
6. **Publication** — Produire n'est pas publier ; la publication relève toujours de G4.

---

## Formulation ultra-courte

F1 filtre les docs. F1.5 stabilise les docs. F1.6 autorise l'usage métier. F2 fusionne les meilleures informations admissibles pour produire une surface métier. G* juge, bloque et publie.
