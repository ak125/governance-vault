---
id: PLAN-DEC-001
decision: "[[DEC-001-hardening-dev-preprod-prod]]"
status: P0-P1 done, P2 pending
created: 2026-02-02
updated: 2026-02-02
---

# Plan d'Exécution: DEC-001 Hardening

## Phase P0 — Stop risques critiques

| # | Action | Fichier | Critère de Succès | Statut |
|---|--------|---------|-------------------|--------|
| P0.1 | Commenter imports RmModule | `app.module.ts:50-53,172-175` | grep "RmModule" = commenté | ✅ |
| P0.2 | Commenter imports AI modules | `app.module.ts:48-50,169-175` | grep "AiContent\|KnowledgeGraph\|RagProxy" = commenté | ✅ |
| P0.3 | Compléter .dockerignore | `.dockerignore` | +25 lignes exclusions | ✅ |
| P0.4 | Compléter .gitignore | `.gitignore` | CSV patterns ajoutés | ✅ |
| P0.5 | Kill-switch scripts OPS | 5 scripts backend/*.js | Bloc KILL-SWITCH en tête | ✅ |

### Vérifications P0

```bash
# V1: RmModule non importé
grep -n "RmModule" backend/src/app.module.ts | grep -v "//"
# Attendu: aucune ligne

# V2: AI modules non importés
grep -n "AiContentModule\|KnowledgeGraphModule\|RagProxyModule" backend/src/app.module.ts | grep -v "//"
# Attendu: aucune ligne

# V3: .dockerignore complet
grep -c "backend/\*.js\|backend/\*.csv\|packages/ai-orchestrator" .dockerignore
# Attendu: >= 3

# V4: Build TypeScript OK
cd backend && npm run build 2>&1 | tail -3
# Attendu: "Successfully compiled"
```

### Preuves P0
- Commit: `7551ea3c`
- Date: 2026-02-02

---

## Phase P1 — Rendre DEV incassable

| # | Action | Fichier | Critère de Succès | Statut |
|---|--------|---------|-------------------|--------|
| P1.1 | Script `npm run dev:core` | `package.json` | Commande fonctionne | ✅ |
| P1.2 | Script `npm run dev:full:all` | `package.json` | Commande fonctionne | ✅ |
| P1.3 | ESLint import-firewall | `backend/.eslintrc.js` | Règle no-restricted-imports | ✅ |
| P1.4 | CI check core-build | `.github/workflows/ci.yml` | Job ajouté | ✅ |
| P1.5 | CI check import-firewall | `.github/workflows/ci.yml` | Job ajouté | ✅ |

### Vérifications P1

```bash
# V1: dev:core existe
grep -c "dev:core" package.json
# Attendu: 1

# V2: import-firewall ESLint
grep -c "no-restricted-imports" backend/.eslintrc.js
# Attendu: >= 1

# V3: CI jobs ajoutés
grep -c "core-build\|import-firewall" .github/workflows/ci.yml
# Attendu: >= 2

# V4: Lint passe
cd backend && npm run lint 2>&1 | tail -3
# Attendu: pas d'erreur
```

### Preuves P1
- Commit P1.1-P1.3: `b1ce836b`
- Commit P1.4-P1.5: `397df387`
- Date: 2026-02-02

---

## Phase P2 — Industrialiser OPS (TODO)

| # | Action | Fichier | Critère de Succès | Statut |
|---|--------|---------|-------------------|--------|
| P2.1 | Déplacer scripts vers tools/ | `tools/scripts/` | 75+ fichiers migrés | ⏳ |
| P2.2 | Créer inventaire scripts | `tools/README.md` | Liste complète | ⏳ |
| P2.3 | Externaliser CSV vers S3 | - | Aucun CSV en git | ⏳ |
| P2.4 | Convertir scripts en migrations | `supabase/migrations/` | Top 10 convertis | ⏳ |

### Prérequis P2
- P0 et P1 validés
- Bucket S3 configuré
- Revue des scripts par équipe

---

## Rollback Procedure

En cas de problème, rollback par phase :

### Rollback P0
```bash
git revert 7551ea3c
```

### Rollback P1
```bash
git revert 397df387
git revert b1ce836b
```

---

## Checklist de Conformité

Voir [[pre-deploy-hardening]] pour la checklist à valider avant chaque déploiement.

---

*Dernière mise à jour: 2026-02-02*
