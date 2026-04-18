---
type: incidents
---

# Incidents

## Incidents durant la periode (2026-04-17 → 2026-04-18)

**Aucun incident** declare pendant la periode couverte par ce pack.

## Artefact identifie — G3 rebase-merge

**Nature** : Artefact structurel, pas un incident.

**Decouvert** : 2026-04-18 lors de l'audit retroactif `_scripts/audit-signatures.sh`.

**Observation** : 20/70 commits sur `main` retournent "No principal matched" lors de `git verify-commit`. Analyse de l'objet commit (`git cat-file`) confirme l'absence de champ `gpgsig`.

**Cause racine** : Sur plan GitHub Free, `gh pr merge --rebase` (strategie imposee par `required_linear_history: true`) reecrit les commits avec nouveaux SHA sans re-signer. `required_signatures: true` cote GitHub necessite plan Pro.

**Pourquoi ce n'est pas un incident** :

- Aucune compromission de cle
- Aucun commit non signe n'a atteint main sans passer par CI G3 au niveau PR
- CI G3 a valide toutes les PRs recentes (3, 4, 5) avec 4 checks verts avant merge
- La chain-of-custody existe, distribuee sur CI logs + GitHub audit log (tamper-evident)

**Decision** : Option B acte — documenter le gap comme "known artifact", pas de migration vers plan Pro (~4€/mois) pour le moment.

**Documentation associee** : [[branch-protection]] section "Artefact Connu : Signature Chain au Merge Rebase" + [[signing-policy]] section "Niveau d'enforcement".

**Critere de reevaluation** : si exigence compliance externe (audit tiers) demande verification locale sur main, basculer sur Option A (GitHub Pro).

---

## Near-miss / events qu'on a choisi de NE PAS classer comme incidents

Quelques evenements operationnels ont eu lieu durant la phase de hardening. Aucun ne remplit les criteres de severite (cf. [[MOC-Incidents]]) — downtime, perte de donnees, breach, paiements bloques. Ils sont listes pour la transparence :

| Event | Pourquoi pas un incident | Resolution |
|-------|--------------------------|-----------|
| CI job G3 echoue sur PR #3 (status=N) | Erreur de configuration CI (runner sans allowed_signers), pas une compromission. Aucun commit non signe n'a ete accepte. | Etape "Configure SSH signature verification" ajoutee au workflow (PR #4) |
| PR #4 bloquee malgre 4 checks verts | Mismatch configuration branch protection (contexts par job key au lieu de display name). La protection a fait son travail: elle a bloque le merge parce que les contexts declares n'existaient pas. | `setup-branch-protection.sh` re-execute avec les bons display names |
| Pre-commit hook echoue sur Windows (Python) | Windows Store alias empoisonne `python`. Le hook a fait son travail: il a refuse le commit. | `find_python()` ajoute pour detecter proprement |
| HTTP 422 sur `gh api PUT /protection` | `-F restrictions=` passe empty string au lieu de null. Request malformee rejetee par GitHub. Aucune ecriture partielle. | Switch vers `gh api --input -` avec JSON body |

Dans tous les cas: **les controles ont fonctionne comme prevu**. Chaque echec a ete detecte avant impact, corrige, documente dans cette section.

## Incidents historiques toujours references

- [[2026-01-11_critical_rm-module-crash]] — INC-2026-01-11 (Critical, resolu). Reste visible dans MOC-Incidents et a produit [[ADR-001-environment-separation]] + [[ADR-004-rm-module-scope]].

## Kill-switch events

- Aucune activation de `AI_VAULT_WRITE=false` durant la periode
- Aucune activation de `AIRLOCK_DISABLED` (hors perimetre de ce pack, trace dans les EP Airlock)

## Voir aussi

- [[MOC-Incidents]] — Taxonomie severite + RACI + lifecycle
- [[airlock-decisions-reference]] — DEC-004 Kill-Switch + DEC-007 Incident Response
