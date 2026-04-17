# MOC: Compliance

Index des plans d'exécution, checklists et rapports de conformité.

---

## Plans d'Exécution Actifs

| Plan | Décision | Status |
|------|----------|--------|
| [[DEC-001-execution-plan]] | [[DEC-001-hardening-dev-preprod-prod]] | P0-P1 done, P2 pending |

---

## Checklists

### Pre-Deploy
| Checklist | Usage | Décision |
|-----------|-------|----------|
| [[pre-deploy-hardening]] | Avant deploy PREPROD/PROD | [[DEC-001-hardening-dev-preprod-prod]] |

### Post-Incident
- (à créer)

### Quarterly Review
- (à créer)

---

## Rapports

*Aucun rapport généré*

---

## Structure 05-compliance/

```
05-compliance/
├── plans/
│   └── DEC-001-execution-plan.md
├── checklists/
│   └── pre-deploy-hardening.md
└── reports/
    └── (à venir)
```

---

## Processus

1. **Décision** créée dans `02-decisions/`
2. **Plan d'exécution** créé dans `05-compliance/plans/`
3. **Checklist** créée si actions répétables
4. **Exécution** avec preuves (commits, logs)
5. **Rapport** si audit requis

---

*Dernière mise à jour: 2026-02-02*
