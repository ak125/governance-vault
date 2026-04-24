---
type: moc
status: canon
role: master-index
updated: 2026-04-17
---

# MOC: Governance

**Master Index** du vault de gouvernance AutoMecanik. Point d'entree unique.

---

## Navigation Principale

| MOC | Role |
|-----|------|
| [[MOC-Decisions]] | ADR canoniques (14 ADR au 2026-04-17) |
| [[MOC-Rules]] | Taxonomie T/G/AI/V - regles canoniques |
| [[MOC-Compliance]] | Plans d'execution, checklists, evidence-packs |
| [[MOC-Agents]] | 119 agents par categorie |
| [[MOC-Incidents]] | Post-mortems et incidents |
| [[MOC-Knowledge]] | Base de connaissances (specs, guides) |
| [[MOC-AuditTrail]] | Audit-trail, bundles rejetes, audits RPC |
| [[MOC-Policies]] | Bundle specs, prompts systeme, processus |

---

## Regles Vault (G1-G4)

Les 4 regles de gouvernance du vault lui-meme. Voir [[rules-vault]].

| Regle | Description | Enforcement |
|-------|-------------|-------------|
| G1 | Canon fait foi | Sync one-way depuis `.spec/00-canon/` |
| G2 | Zero orphelin | `_scripts/check-orphans.sh` |
| G3 | Commits signes | SSH signing (ed25519) via git config |
| G4 | CI read-only sur canon | `AI_VAULT_WRITE=false` en prod |

---

## Taxonomie Canonique

Voir [[MOC-Rules]] pour les details.

| Prefix | Domaine | Fichier |
|--------|---------|---------|
| `T1-T7` | Technical Rules | [[rules-technical]] |
| `G1-G4` | Vault Governance | [[rules-vault]] |
| `G5-G8` | Governance Process | [[rules-governance-process]] |
| `AI1-AI10` | AI-COS Rules | [[rules-ai-cos]] |
| `V1-V6` | V-Level SEO | [[rules-seo-vlevel]] |
| `PageRole` | SEO PageRole | [[rules-seo-pagerole]] |
| Antipatterns | AI Antipatterns | [[rules-ai-antipatterns]] |

---

## Meta

- [[README]] - Documentation generale du vault
- [[signing-policy]] - Politique de signature (SSH ed25519)
- [[key-registry]] - Registre des cles SSH
- [[sync-log]] - Log de synchronisation canon
- [[ci-policy]] - Politique CI/CD (read-only sur canon)
- [[cron-setup]] - Configuration des tasks cron
- [[deploy-bot]] - Role du bot CI/CD (69/108 commits, non-SPOF)

## Archive

- [[INDEX-archive]] - Documents archives (superseded, OpenClaw, etc.)

---

## Statistiques (2026-04-17)

| Metrique | Valeur |
|----------|--------|
| ADR actifs | 14 |
| Incidents formalises | 0 |
| Retrospectives | 4 |
| Evidence-packs | 4 (fevrier 2026) |
| Agents | 119 (11 categories) |
| Regles canoniques | 7 fichiers (T1-T7, G1-G8, AI1-AI10, V1-V6, + R-SEO, AP) |
| Bundles rejetes (Airlock) | 8 |

---

## Cycle de Vie

```
Probleme/Incident -> [[MOC-Incidents]]
        |
        v
Decision prise  -> [[MOC-Decisions]] (nouveau ADR)
        |
        v
Plan execute    -> [[MOC-Compliance]] (plan + checklist)
        |
        v
Preuves         -> [[MOC-Compliance]] (evidence-pack)
        |
        v
Audit-trail     -> [[MOC-AuditTrail]] (retrospective, rejects)
```

---

_Derniere mise a jour: 2026-04-17_
