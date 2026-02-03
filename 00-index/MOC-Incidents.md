# MOC: Incidents

Index des incidents et post-mortems.

---

## Incidents Récents

| ID | Date | Sévérité | Titre | Status |
|----|------|----------|-------|--------|
| INC-2026-01-11 | 2026-01-11 | Critical | rm/ Module Crash Production | Closed |

---

## Par Sévérité

### Critical
- [[2026-01-11_critical_rm-module-crash]] - Crash production module rm/ (~15min downtime)

### High
- (aucun)

### Medium
- (aucun)

### Low
- (aucun)

---

## Par Année

### 2026
- [[2026-01-11_critical_rm-module-crash]] - rm/ module import error

### 2025
- (aucun incident documenté)

---

## Statistiques

| Métrique | Valeur |
|----------|--------|
| Total incidents documentés | 1 |
| Incidents critiques | 1 |
| MTTR moyen (incidents critiques) | ~15 minutes |

---

## Actions Correctives Issues d'Incidents

| Incident | Action | Status |
|----------|--------|--------|
| INC-2026-01-11 | Créer ADR-001 (Environment Separation) | Complété |
| INC-2026-01-11 | Créer ADR-004 (rm/ Module Scope) | Complété |
| INC-2026-01-11 | Ajouter verification CI imports | Planifié |

---

## Template

Voir `01-incidents/_templates/incident-template.md`

---

## Processus Incident

1. Détection incident
2. Investigation (max 4h)
3. Résolution
4. Post-mortem (max 48h)
5. Actions correctives identifiées
6. Mise à jour MOC
7. Revue trimestrielle

---

_Dernière mise à jour: 2026-02-03_
