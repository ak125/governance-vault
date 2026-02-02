---
id: DEPLOY-YYYY-MM-DD-HHmm
date: YYYY-MM-DD HH:mm
environment: preprod|production
commit: ""
image_tag: ""
deployer: "@username"
status: success|failed|rollback
pre_checks_passed: true|false
post_checks_passed: true|false
rollback_commit: ""
---

# Déploiement: [commit message court]

## Pre-Deploy Checklist

- [ ] Import firewall passé
- [ ] Core-build validé
- [ ] TypeScript OK
- [ ] Lint OK
- [ ] Tests manuels effectués
- [ ] Backup vérifié
- [ ] Rollback plan prêt

## Changements Inclus

### Features
- feat: [description]

### Fixes
- fix: [description]

### Other
- chore/refactor/docs: [description]

## Commits

| SHA | Message | Author |
|-----|---------|--------|
| abc123 | feat: ... | @xxx |
| def456 | fix: ... | @xxx |

## Métriques Post-Deploy

| Métrique | Avant | Après | Delta | Status |
|----------|-------|-------|-------|--------|
| LCP (ms) | - | - | - | ✅/⚠️/❌ |
| CLS | - | - | - | ✅/⚠️/❌ |
| Error rate (%) | - | - | - | ✅/⚠️/❌ |
| Response time (ms) | - | - | - | ✅/⚠️/❌ |

## Post-Deploy Checklist

- [ ] Health check OK
- [ ] Smoke tests passés
- [ ] Métriques stables (15 min)
- [ ] Logs vérifiés
- [ ] Alertes configurées

## Incidents Liés

- Aucun

## Rollback (si applicable)

**Raison**: [...]
**Commit rollback**: [sha]
**Durée d'incident**: [X minutes]

---

*Déployé le: YYYY-MM-DD HH:mm*
*Vérifié le: YYYY-MM-DD HH:mm*
