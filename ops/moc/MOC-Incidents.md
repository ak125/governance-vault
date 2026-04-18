---
type: moc
status: canon
updated: 2026-04-18
---

# MOC: Incidents

Index des incidents et post-mortems. Cette MOC est la porte d'entree pour tout evenement qui a impacte la production, la securite, ou l'integrite des donnees.

> Les **retrospectives** (non-incident) sont dans [[MOC-AuditTrail]].
> Les **decisions** issues d'incidents deviennent des [[MOC-Decisions|ADRs]].

---

## Incidents Recents

| ID | Date | Severite | Titre | Status |
|----|------|----------|-------|--------|
| INC-2026-003 | 2026-04-18 | High | Diagnostic Engine — Seeding contenu metier sans validation RAG/vault | Resolved |
| INC-2026-01-11 | 2026-01-11 | Critical | rm/ Module Crash Production | Closed |

---

## Par Severite

### Critical

- [[2026-01-11_critical_rm-module-crash]] — Crash production module rm/ (~15min downtime)

### High

- [[2026-04-18_high_diag-engine-rag-seeding]] — Agent a fabrique 350 entrees contenu metier en DB sans consulter RAG + vault (rollback OK, pivot delegation RAG pure)

### Medium

- (aucun)

### Low

- (aucun)

---

## Par Annee

### 2026

- [[2026-04-18_high_diag-engine-rag-seeding]] — Diagnostic engine : violation gouvernance contenu (RAG ignore, ~350 entrees fabriquees, rollback)
- [[2026-01-11_critical_rm-module-crash]] — rm/ module import error

### 2025

- (aucun incident documente)

---

## Taxonomie de Severite

| Severite | Criteres | SLA detection | SLA post-mortem |
|----------|----------|----------------|------------------|
| **Critical** | Downtime PROD, perte de donnees, breach securite, paiements bloques | Immediate | < 48h |
| **High** | Degradation majeure, SLO viole sur service critique, fuite non-sensible | < 1h | < 72h |
| **Medium** | Bug user-visible contournable, performance degradee, regression sur feature secondaire | < 4h | < 7j |
| **Low** | Defauts cosmetiques, warnings, issues de devex | < 24h | Optionnel |

Un incident de severite `Critical` ou `High` **DOIT** declencher une activation du kill-switch Airlock (`AI_VAULT_WRITE=false`) si une action IA/agent est suspectee dans la chaine causale.

---

## Processus Incident (lifecycle)

| Etape | Duree max | Responsable | Artefact produit |
|-------|-----------|-------------|------------------|
| 1. **Detection** | N/A | Monitoring / utilisateur | Ticket ou alerte |
| 2. **Triage** | 15 min (Critical) / 1h (High) | On-call engineer | Assignation severite |
| 3. **Mitigation** | < 1h (Critical) | Engineer + tech lead | Rollback / hotfix / kill-switch |
| 4. **Investigation** | < 4h | Engineer assigne | Timeline + root cause preliminaire |
| 5. **Resolution** | Variable | Engineer assigne | Fix deploye et verifie |
| 6. **Post-mortem** | Voir SLA severite | Engineer + owner | Document dans `ledger/incidents/YYYY/` |
| 7. **Actions correctives** | Tracees jusqu'a closure | Tech lead | ADR(s), nouvelles rules, tests ajoutes |
| 8. **Revue trimestrielle** | T+90j apres incident | Governance team | Update de cette MOC |

---

## RACI

| Activite | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| Detection | Monitoring / Any | On-call | — | Team |
| Triage | On-call | Tech lead | Engineer concerne | Team |
| Mitigation | On-call + Engineer | Tech lead | Architecture team | Fafa |
| Post-mortem redaction | Engineer assigne | Tech lead | Team, Governance | Fafa |
| Decision architecturale issue de l'incident | Architecture team | Fafa | Engineer, Governance | Team |
| Closure formelle | Governance team | Fafa | — | Team |

---

## Comment declarer un nouvel incident

1. **Copier** le template : `_templates/incident-template.md`
2. **Creer** le fichier dans `ledger/incidents/YYYY/` avec le pattern de nom :
   ```
   YYYY-MM-DD_<severity>_<short-title>.md
   ```
   Exemple : `2026-01-11_critical_rm-module-crash.md`
3. **Remplir** le frontmatter YAML :
   ```yaml
   ---
   type: incident
   status: investigating | mitigated | resolved | closed
   severity: critical | high | medium | low
   date: YYYY-MM-DD
   detected_at: YYYY-MM-DDTHH:MM:SSZ
   resolved_at: YYYY-MM-DDTHH:MM:SSZ
   owner: <nom>
   related_adrs: []
   ---
   ```
4. **Linker** l'incident depuis cette MOC (sections "Incidents Recents", "Par Severite", "Par Annee")
5. Si le post-mortem produit une decision architecturale, **creer une ADR** via `_templates/adr-template.md`
6. Commit **signe** avec message clair : `docs(incident): INC-YYYY-MM-DD <short-title>`

---

## Actions Correctives Issues d'Incidents

| Incident | Action | Status |
|----------|--------|--------|
| INC-2026-01-11 | Creer [[ADR-001-environment-separation]] (Environment Separation) | Complete |
| INC-2026-01-11 | Creer [[ADR-004-rm-module-scope]] (rm/ Module Scope) | Complete |
| INC-2026-01-11 | Ajouter verification CI imports | Planifie |

---

## Statistiques

| Metrique | Valeur |
|----------|--------|
| Total incidents documentes | 1 |
| Incidents critiques | 1 |
| MTTR moyen (incidents critiques) | ~15 minutes |
| Incidents ayant produit une ADR | 1 (2 ADRs) |
| Incidents ayant declenche un kill-switch | 0 |

---

## Template

Voir [[_templates/incident-template|_templates/incident-template.md]]

---

## Voir aussi

- [[MOC-AuditTrail]] — Retrospectives de phase, bundles rejetes, audits ponctuels
- [[MOC-Decisions]] — ADRs canoniques (souvent produites par des post-mortems)
- [[MOC-Rules]] — Regles T/G/AI/V (peuvent evoluer suite a incident)
- [[airlock-decisions-reference]] — DEC-004 Kill-Switch Global + DEC-007 Incident Response

---

_Derniere mise a jour: 2026-04-18_
