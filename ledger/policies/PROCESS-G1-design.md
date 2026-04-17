---
id: PROCESS-G1
title: Processus G1 — Création de fiches agents planifiés
status: active
date: 2026-04-04
related_adr: ADR-013
---

# Processus G1 — Design (fiches agents planifiés)

> Défini par ADR-013. Ce processus s'applique aux modifications documentaires
> sans impact opérationnel (pas d'activation, pas de code, pas de runtime).

## Conditions d'éligibilité

Toutes les conditions suivantes doivent être remplies :

| Condition | Valeur requise |
|-----------|---------------|
| `status` | `planned` |
| `governance_verdict` | `NOT_APPROVED` |
| Agent activé ? | Non (pas de runtime, pas d'exécution) |
| Nature des changements | Fiches `.md` + REG-001 + catalog + orgchart uniquement |

**Si une seule condition n'est pas remplie → processus G2 ou G3 obligatoire (ADR-002).**

## Processus

### 1. Préparer la branche

```bash
git checkout main && git pull
git checkout -b feature/agent-<description>
```

### 2. Rédiger la fiche agent

Créer `05-agents/ai-cos/AGENT-<agent-id>.md` avec les sections obligatoires :

- **Frontmatter** : agent_id, agent_name, status, owner, governance_verdict, last_audit, zone
- **Identity** : ID, Name, Status, Owner, Description
- **Rattachement** : reports_to, sponsor, squad, level
- **Agents Managed** (si lead/sub-lead) : liste complète des reports directs
- **Execution Environment** : zone, runtime, output
- **Trust & Risk** : trust level, risk class, risk factors
- **Access Rights** : read, write, secrets
- **Governance** : verdict, related ADR, airlock required, audit trail
- **Placement Decision** : statut d'activation

### 3. Mettre à jour REG-001

Dans `05-agents/registry/REG-001-agents.md` :

- Ajouter la ligne dans la table appropriée
- Version bump (patch : x.y.z → x.y.z+1)
- Mettre à jour Quick Stats (total, NOT_APPROVED count)
- Mettre à jour Domain Coverage (planned count, total)
- Mettre à jour last_audit

### 4. Mettre à jour les documents de référence

- `06-knowledge/11-agent-catalog.md` — si agent AI-COS Level 2+
- `ai-cos-system/docs/company-orgchart.md` — si modification de hiérarchie

### 5. Vérifications avant PR

| Vérification | Comment |
|-------------|---------|
| Golden Rule R5 | Chaque agent a un `reports_to`, un `sponsor`, un `squad` |
| Golden Rule R6 | Documenter le ratio create/delete dans la PR |
| Span of control | Aucun parent ne dépasse 10 reports directs |
| Couverture | Chaque agent du domaine assigné à exactement 1 lead |
| Pas d'orphelins | Pas d'agent sans hiérarchie |
| Compteurs REG-001 | Les totaux sont cohérents |

### 6. Soumettre la PR

```bash
git add <fichiers modifiés>
git commit -m "feat(agents): add <agent_id> — <justification courte>"
git push -u origin feature/agent-<description>
gh pr create --title "feat(agents): ..." --body "..."
```

Format PR :

```markdown
## Contexte
[Pourquoi cette création/modification]

## Changements
- Fiches créées : [liste]
- REG-001 : v[old] → v[new] (+N agents)
- Catalog/orgchart : [modifications]

## Vérifications G1
- [ ] R5 : reports_to, sponsor, squad définis
- [ ] R6 : ratio create/delete documenté
- [ ] Span of control ≤ 10
- [ ] Compteurs REG-001 cohérents
- [ ] Pas d'activation (status=planned, verdict=NOT_APPROVED)
```

### 7. Review et merge

- **Reviewer** : Human CEO ou délégué explicitement nommé
- **Merge** : Manuel uniquement, après approbation

## Ce qui est interdit en G1

- Modifier du code applicatif
- Changer un verdict vers APPROVED ou APPROVED_WITH_CONDITIONS
- Activer un agent (`status: planned` → `status: active`)
- Modifier des règles, ADRs, ou politiques de gouvernance
- Créer des bundles signés ou soumettre via agent-submissions

## Audit

Chaque PR G1 mergée constitue son propre audit trail (auteur, reviewer, date, changements).

---

_Créé le : 2026-04-04_
_Référence : ADR-013_
