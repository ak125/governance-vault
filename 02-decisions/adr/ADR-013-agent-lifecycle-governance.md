---
id: ADR-013
title: "Cycle de vie des agents : gouvernance création, activation et restructuration"
status: accepted
date: 2026-04-04
decision_makers: [Human CEO]
supersedes: []
superseded_by: []
related_rules: [RULE-H0, RULE-H4, RULE-H5, RULE-H6]
related_incidents: []
reviewed_by: ""
---

# ADR-013: Cycle de vie des agents — gouvernance création, activation et restructuration

## Contexte

### Problème 1 — Pas de processus pour les agents planifiés

ADR-002 et ADR-009 définissent un pipeline rigoureux (bundle HMAC → agent-submissions → Airlock → PR → merge humain) pour l'activation des agents. Ce pipeline est adapté aux agents qui s'exécutent en production.

Mais il n'existe **aucun processus défini** pour :
- Créer une fiche agent planifié (`status: planned`, `verdict: NOT_APPROVED`)
- Restructurer la hiérarchie organisationnelle (ajout de leads, sous-leads)
- Modifier REG-001 pour documenter de nouveaux agents non-activés

En l'absence de processus, deux dérives sont possibles :
1. **Contournement** : les fiches sont créées en direct, sans review (violation RULE-H4/H5)
2. **Blocage** : rien n'est créé car le pipeline HMAC est disproportionné pour un markdown

Les deux sont arrivés. Le pipeline agent-submissions est pausé depuis le 2026-02-06. Des modifications récentes du governance-vault ont été poussées directement sur main sans review.

### Problème 2 — Pas de critères Phase 2

ADR-009 définit Phase 1 (activation des agents APPROVED/APPROVED_WITH_CONDITIONS). Mais les critères de passage en Phase 2 (activation des Leads L2, Sub-Leads L2.5, Executive L1) ne sont pas définis. 31 agents NOT_APPROVED sont bloqués sans chemin d'approbation.

### Problème 3 — Span of control

Certains orchestrateurs (ex: IA-SEO Master) ont trop de reports directs (~30 agents SEO). La création de sous-leads est nécessaire mais bloquée par l'absence de processus.

## Décision

### 1. Trois niveaux de gouvernance selon le risque

| Niveau | S'applique à | Processus |
|--------|-------------|-----------|
| **G1 — Design** | Fiches `planned` + `NOT_APPROVED`, modifications orgchart/catalog | PR → review humaine → merge |
| **G2 — Activation** | Passage `planned` → `active`, changement de verdict | Bundle signé → agent-submissions → Airlock → PR → review humaine → merge |
| **G3 — Production** | Agents avec `output: rpc` ou `output: bundle` en mode actif, accès write | G2 + tests d'intégration + période observe 14j + audit trail |

**Principe** : le niveau de sécurité est proportionnel au niveau de risque. Un document de design n'a pas besoin du même pipeline qu'un déploiement production.

### 2. Processus G1 — Design (fiches agents planifiés)

**Conditions d'éligibilité** (toutes requises) :

- Agent `status: planned`
- Agent `governance_verdict: NOT_APPROVED`
- Aucune activation (pas de runtime, pas d'exécution)
- Changements limités à : fiches `.md`, REG-001, catalog, orgchart

**Processus** :

```
1. Rédiger la fiche agent (AGENT-*.md) selon template standard
   - Sections obligatoires : Identity, Rattachement, Execution Environment,
     Trust & Risk, Access Rights, Governance, Placement Decision
   - Si sub-lead : section Agents Managed avec liste complète

2. Mettre à jour REG-001
   - Nouvelle ligne dans la table appropriée
   - Version bump (patch)
   - Mise à jour des compteurs Quick Stats et Domain Coverage

3. Mettre à jour les documents de référence
   - 11-agent-catalog.md (si agent AI-COS)
   - company-orgchart.md (si modification hiérarchie)

4. Soumettre PR vers governance-vault (branche feature/agent-*)
   - Titre : "feat(agents): add <agent_id> — <justification courte>"
   - Description : lien vers la fiche, justification, impact

5. Review humaine (Human CEO ou délégué explicitement nommé)
   - Vérifie la cohérence hiérarchique (Golden Rule R5)
   - Vérifie le ratio CREATE/DELETE (Golden Rule R6)
   - Vérifie la complétude de la fiche

6. Merge manuel après approbation
```

**Ce qui est interdit en G1** :
- Modifier du code applicatif
- Changer un verdict vers APPROVED ou APPROVED_WITH_CONDITIONS
- Activer un agent (`status: active`)
- Modifier des règles, ADRs, ou politiques de gouvernance

### 3. Critères Phase 2 — Activation des Leads et Sub-Leads

**Prérequis globaux** (Phase 1 → Phase 2) :

| Critère | Exigence | Mesure |
|---------|----------|--------|
| Stabilité Phase 1 | 14 jours consécutifs sans incident | Logs Airlock |
| Airlock enforce actif | Mode enforce sur toutes les fonctions P0 | Config RpcGate |
| Pipeline opérationnel | agent-submissions traite au moins 1 bundle/semaine | Audit trail |
| Signed commits | Tous les commits governance-vault sont signés | audit-signatures.sh |
| Branch protection | main protégé, PR obligatoire | GitHub settings |

**Critères par agent** (chaque lead/sub-lead doit satisfaire) :

| Critère | Exigence |
|---------|----------|
| Fiche complète | Toutes les sections remplies, approuvée via G1 |
| agents_managed | Liste complète des reports directs, chacun documenté |
| KPIs définis | Au moins 2 métriques mesurables avec targets |
| Rollback plan | Procédure de désactivation documentée |
| Sponsor identifié | Un agent Level 1 ou Level 2 comme sponsor |
| Budget validé | IA-CFO a approuvé le budget (ou budget = 0 pour orchestration pure) |
| Bundle G2 soumis | Bundle signé passé par Airlock avec succès |
| Période observe | 14 jours en mode observe sans violation |

**Ordre d'activation Phase 2** :

```
Vague 2a — Sub-Leads (Level 2.5) sous un Lead existant
  → Risque faible : orchestration locale, pas d'accès production
  → Premier test : sous-leads SEO sous IA-SEO Master

Vague 2b — Leads (Level 2) avec agents_managed actifs
  → Risque moyen : coordination inter-agents
  → Prérequis : sub-leads de la vague 2a stables

Vague 2c — Executive (Level 1) avec authority.proposes
  → Risque élevé : propositions stratégiques
  → Prérequis : nouvel ADR spécifique par agent L1
```

### 4. Restructuration hiérarchique

Toute modification de la hiérarchie (ajout de leads, sub-leads, réaffectation d'agents) suit le processus G1 avec des vérifications supplémentaires :

| Vérification | Description |
|-------------|-------------|
| Span of control | Le parent ne doit pas dépasser 10 reports directs |
| Couverture complète | Chaque agent du domaine est assigné à exactement 1 lead/sub-lead |
| Pas d'orphelins | Aucun agent sans `reports_to` (Golden Rule R5) |
| Ratio R6 respecté | Si N agents créés, au moins N/2 agents fusionnés ou supprimés (sauf première structuration d'un domaine) |

## Options Considérées

### Option A : Pipeline unique HMAC pour tout (statu quo)

**Description** : Garder le pipeline ADR-002 tel quel pour toute modification, y compris les fiches planifiées.

**Avantages** :
- Sécurité maximale, processus unique
- Pas de nouveau processus à maintenir

**Inconvénients** :
- Pipeline agent-submissions pausé depuis 2 mois — bloque toute évolution
- Disproportionné pour des documents markdown sans impact opérationnel
- Pousse au contournement (modifications directes observées)

### Option B : Trois niveaux de gouvernance G1/G2/G3 (retenue)

**Description** : Processus proportionné au risque. G1 léger pour le design, G2 complet pour l'activation, G3 renforcé pour la production.

**Avantages** :
- Proportionné : le niveau de contrôle correspond au niveau de risque
- Débloque l'évolution organisationnelle (G1) sans affaiblir la sécurité (G2/G3)
- Le pipeline HMAC reste obligatoire dès qu'un agent s'active
- Critères Phase 2 explicites et mesurables

**Inconvénients** :
- Trois processus à maintenir au lieu d'un
- Risque de confusion sur quel niveau s'applique (mitigé par les conditions d'éligibilité claires)

### Option C : Approbation directe Human CEO sans processus

**Description** : RULE-H0 permet au Human CEO d'approuver tout directement.

**Avantages** :
- Rapide, pas de processus

**Inconvénients** :
- Pas de traçabilité structurée
- Pas reproductible, dépend d'une seule personne
- Contredit l'esprit de "governance as code"

## Justification

L'option B est retenue car elle résout les trois problèmes identifiés :

1. **Processus pour les agents planifiés** : G1 permet de créer des fiches sans contourner la gouvernance
2. **Critères Phase 2** : Explicites, mesurables, par vagues de risque croissant
3. **Restructuration** : Possible via G1 avec vérifications de cohérence hiérarchique

Le principe directeur est la **proportionnalité** : un markdown ne nécessite pas un bundle HMAC, mais un agent actif en production, si.

## Conséquences

### Positives

- Déblocage de l'évolution organisationnelle (création de leads, sub-leads)
- Chemin clair de Phase 1 → Phase 2 → Phase 2a/2b/2c
- La gouvernance s'applique à elle-même (PR obligatoire même pour G1)
- Fin des contournements : un processus existe pour chaque cas

### Négatives

- Trois niveaux de processus à documenter et maintenir
- G1 est plus léger que le pipeline actuel — acceptation d'un risque résiduel faible sur les fiches planifiées

### Neutres

- Le pipeline HMAC (ADR-002) n'est pas modifié — G2 et G3 l'utilisent tel quel
- REG-001 continue d'être la source de vérité

## Critères de Succès

- [ ] Premier agent créé via processus G1 (PR + review + merge)
- [ ] Prérequis globaux Phase 2 atteints (Airlock enforce, signed commits, branch protection)
- [ ] Premier sub-lead activé via G2 (vague 2a)
- [ ] Zéro contournement du processus pendant 30 jours
- [ ] Pipeline agent-submissions relancé et traite au moins 1 bundle/semaine

## Implémentation

### Étape 1 — Prérequis (avant toute création G1)

1. Activer branch protection sur `governance-vault` main (PR obligatoire)
2. Configurer signed commits SSH (allowed signers)
3. Documenter le processus G1 dans `03-policies/PROCESS-G1-design.md`

### Étape 2 — Premier cas d'usage G1 : sous-leads SEO

1. Créer branche `feature/agent-seo-subleads`
2. Rédiger 4 fiches : `agent.seo.kp.lead`, `agent.seo.content.lead`, `agent.seo.qa.lead`, `agent.seo.exec.lead`
3. Mettre à jour REG-001 v2.3.0, catalog, orgchart
4. PR + review Human CEO
5. Merge

### Étape 3 — Prérequis Phase 2

1. Relancer pipeline agent-submissions (ou post-mortem si abandon)
2. Passer RpcGate en enforce mode (P0)
3. 14 jours de stabilité mesurée

### Étape 4 — Vague 2a : activation sous-leads SEO

1. Bundle G2 pour chaque sous-lead
2. Soumission agent-submissions → Airlock
3. Période observe 14 jours
4. Verdict APPROVED_WITH_CONDITIONS

## Revue Planifiée

**Date** : 2026-05-04 (30 jours après proposition)
**Critères de revue** : Évaluer si les trois niveaux G1/G2/G3 fonctionnent en pratique, ajuster si nécessaire.

---

*Proposé le : 2026-04-04*
*Accepté le : 2026-04-04*
*Dernière revue : —*
