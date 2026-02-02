---
id: CHK-HARDENING
decision: "[[DEC-001-hardening-dev-preprod-prod]]"
plan: "[[DEC-001-execution-plan]]"
type: pre-deploy
---

# Checklist: Pre-Deploy Hardening

Cette checklist doit être validée avant tout déploiement en PREPROD ou PROD.

---

## Informations d'Exécution

| Champ | Valeur |
|-------|--------|
| Date | __________ |
| Validateur | @__________ |
| Commit | __________ |
| Environnement | ☐ PREPROD ☐ PROD |

---

## Vérifications Obligatoires

### 1. Imports PROD-safe

- [ ] `grep -n "RmModule" backend/src/app.module.ts | grep -v "//"` → **aucune ligne**
- [ ] `grep -n "AiContentModule" backend/src/app.module.ts | grep -v "//"` → **aucune ligne**
- [ ] `grep -n "KnowledgeGraphModule" backend/src/app.module.ts | grep -v "//"` → **aucune ligne**
- [ ] `grep -n "RagProxyModule" backend/src/app.module.ts | grep -v "//"` → **aucune ligne**

### 2. Exclusions Packaging

- [ ] `.dockerignore` contient `backend/*.js`
- [ ] `.dockerignore` contient `backend/*.csv`
- [ ] `.dockerignore` contient `packages/ai-orchestrator/`
- [ ] `.dockerignore` contient `scripts/`

### 3. Kill-switch Scripts OPS

- [ ] `head -15 backend/generate_all_seo_switches.js | grep "KILL-SWITCH"` → **présent**
- [ ] `head -15 backend/recalculate-vlevel.js | grep "KILL-SWITCH"` → **présent**

### 4. Build & Lint

- [ ] `npm run build` → **0 erreur**
- [ ] `npm run lint` → **0 erreur**
- [ ] `npm run typecheck` → **0 erreur**

### 5. CI Checks

- [ ] Job `core-build` → **✅ passed**
- [ ] Job `import-firewall` → **✅ passed**

---

## Vérifications Post-Deploy

- [ ] `curl https://automecanik.com/health` → `{"status":"ok"}`
- [ ] Logs sans erreur d'import
- [ ] Aucune alerte Cloudflare

---

## Signature

| Rôle | Nom | Date | Signature |
|------|-----|------|-----------|
| Exécutant | __________ | __________ | __________ |
| Validateur | __________ | __________ | __________ |

---

## Référence

- Décision: [[DEC-001-hardening-dev-preprod-prod]]
- Plan: [[DEC-001-execution-plan]]
- Incident origine: INC-2026-001 (Crash prod RmModule)

---

*Template v1.0 — 2026-02-02*
