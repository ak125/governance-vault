---
type: retrospective
status: complete
date: 2026-04-18
owner: [Fafa, Claude]
branch: main (via PRs #3, #4, #5, chore/evidence-pack-20260418)
phase: "Phase 7"
related_plan: [[2026-04-17-governance-vault-v2-refactor]]
related_adrs: []
---

# Phase 7 — Residuels v2 + Evidence-Pack + Option B

> Retrospective de la phase de cloture du refactor v2 : resolution des residuels identifies dans le rapport final v2, production du premier evidence-pack meta-vault, et decision officielle sur l'artefact G3 rebase-merge.

**Predecesseur** : [[2026-04-17-governance-vault-v2-refactor]] (couvre Phases 1-6)

---

## TL;DR

**Verdict** : PASS. La phase 7 complete proprement le refactor v2. Le vault passe d'un etat "fonctionnel" (Phases 1-6) a un etat "documente et auditable" (Phase 7). L'artefact G3 rebase-merge, decouvert par l'audit retroactif des signatures, est officiellement documente et accepte comme gap connu (Option B) plutot que masque ou ignore.

**Effort** : ~1 session continue (2026-04-17 → 2026-04-18), 3 PRs mergees (#3 refactor, #4 allowed_signers, #5 residuels) + 1 PR en cours (chore/evidence-pack-20260418).

---

## Livrables

### Tasks #12-#14 (residuels du rapport v2)

| Task | Livrable | Fichier |
|------|----------|---------|
| #12 | Mapping Airlock DEC → ADR | `ledger/knowledge/airlock-decisions-reference.md` |
| #13 | MOC-Incidents enrichi (taxonomie severite + RACI + lifecycle 8 etapes) | `ops/moc/MOC-Incidents.md` |
| #14 | Policy branch-protection (config + procedure d'urgence + verification) | `99-meta/branch-protection.md` |

### Infrastructure

- `_scripts/setup-branch-protection.sh` — idempotent, JSON body via `--input -`
- `_scripts/check-orphans.sh` + `check-broken-links.sh` — detection Python robuste (`find_python()`) pour Windows
- `.githooks/pre-commit` — distingue exit 2 (Python manquant) vs exit 1 (violation)
- `.github/workflows/vault-governance.yml` — step "Configure SSH signature verification" ajoutee

### Evidence-Pack

- Premier EP meta-vault : `EP-20260418-governance-hardening`
- 9 documents canoniques + INDEX + manifest.sha256
- Distinct des 4 EP Airlock (EP-20260205-*) — scope = vault documentaire

### Documentation Option B

- `99-meta/branch-protection.md` — section "Artefact Connu : Signature Chain au Merge Rebase"
- `99-meta/signing-policy.md` — clarification "G3 enforced au PR level"
- EP `05-ci-proof.md` + `07-incidents.md` — documentation distribuee

---

## Pieges rencontres et resolutions

Les apprentissages de cette session meritent d'etre documentes pour eviter que la prochaine phase retombe dedans.

### Python introuvable sur Windows

**Symptome** : `python` sur Windows appelle le Microsoft Store alias qui exit 9009 sans rien faire → pre-commit hook plante.

**Cause** : Git Bash fait confiance a `command -v python` sans verifier que c'est un vrai interpreteur.

**Fix** : `find_python()` teste chaque candidate avec `sys.version_info` et `py -3`. Elimine les stubs.

### CI G3 status=N malgre commits signes

**Symptome** : PR #3 CI job `g3-signed-commits` echoue, alors que `git log --show-signature` en local dit "Good signature".

**Cause** : Le runner CI n'a pas de `~/.ssh/allowed_signers` et pas de `gpg.ssh.allowedSignersFile` configure → `%G?` retourne `N` au lieu de `G`.

**Fix** : Step "Configure SSH signature verification" dans le workflow. Les cles publiques (non-sensibles) sont hardcodees.

### HTTP 422 sur `gh api PUT /protection`

**Symptome** : `setup-branch-protection.sh` echoue avec HTTP 422 "restrictions must be object or null".

**Cause** : `-F restrictions=` en ligne de commande passe une chaine vide `""` au lieu de `null`.

**Fix** : Switch vers `gh api --input -` avec JSON body complet. `"restrictions": null` explicite.

### PR #4 bloquee malgre 4 checks verts

**Symptome** : Tous les checks CI sont SUCCESS, mais la PR affiche "blocked by required status checks" et le merge est refuse.

**Cause** : `required_status_checks.contexts` utilisait les **job keys** (`g2-orphans`, etc.) alors que GitHub matche par **display name** (`G2: Zero Orphelin`, etc. — le `name:` field du YAML).

**Fix** : Re-executer `setup-branch-protection.sh` avec les bons display names.

### git verify-commit retourne "No principal matched" localement

**Symptome** : Audit retroactif signale 20/70 commits non signes sur main, dont des commits Fafa tres recents qui ont pourtant passe CI G3.

**Cause** : Sur plan GitHub Free, `gh pr merge --rebase` (strategie imposee par `required_linear_history: true`) reecrit les commits sans re-signer. Le champ `gpgsig` de l'objet commit disparait.

**Fix** : Non-technique — documentation de l'artefact comme "known gap" (Option B). Compensating control = CI G3 enforce au PR level + GitHub audit log tamper-evident.

### `jq` absent sur Windows

**Symptome** : Commande de verification integrite branch-protection echoue sur "jq n'est pas reconnu".

**Fix** : Alternative PowerShell native avec `ConvertFrom-Json` + `PSCustomObject`. Documente pour futures verifications.

---

## Metriques avant/apres

| Metrique | Avant Phase 7 | Apres Phase 7 |
|----------|---------------|---------------|
| Residuels flaggues rapport v2 | 3 | 0 |
| Documents meta-vault (99-meta + MOCs) | ~14 | ~16 |
| Evidence-packs meta-vault | 0 | 1 |
| Gap G3 documente | Non | Oui (Option B) |
| PRs avec 4 checks verts | 2 | 5 |
| Branch protection verifiee | Initial | Verifiee 2x (JSON match a 100%) |

---

## Decisions prises durant la phase

| Decision | Rationale |
|----------|-----------|
| Option B pour G3 rebase-merge | Plan Free suffit si on documente honnetement le gap. Le CI au PR level + GitHub audit log sont compensating controls suffisants pour un repo de gouvernance documentaire. |
| EP meta-vault separe des EP Airlock | Les perimetres sont distincts (vault documentaire vs runtime Airlock). Un EP unique aurait brouille les responsabilites. |
| `required_signatures: false` cote GitHub | Plan Free ne le supporte pas de toute facon. Mais si on migrait un jour vers Pro, cet EP sert de baseline pour mesurer l'ameliotion (0 → N commits signes sur main). |
| Hardcoder les cles publiques dans workflow YAML | Cles publiques = non-sensibles. Eviter un secret Actions pour quelque chose de verifiable publiquement. |

---

## Pattern reutilisables

Pour les futures phases de hardening :

1. **Audit retroactif systematique** : apres toute phase d'enforcement, lancer `audit-signatures.sh --report` pour detecter les artefacts. Interpreter en 3 categories : pre-policy / post-rebase / anomalie vraie.
2. **Verification integrite via `jq` ou `ConvertFrom-Json`** : a chaque modif de branch protection, exporter le JSON attendu et le comparer a la reference documentee.
3. **Evidence-pack meta apres 10+ commits de gouvernance** : rend l'audit externe possible, structure la memoire institutionnelle.
4. **Retrospective systematique** : chaque phase produit une retro, meme courte. Les apprentissages se perdent autrement.

---

## Links

- [[2026-04-17-governance-vault-v2-refactor]] — Retro predecesseur (Phases 1-6)
- [[INDEX-EP-20260418-governance-hardening]] — Evidence-pack officiel de cette phase
- [[branch-protection]] — Policy complete (section "Artefact Connu")
- [[signing-policy]] — G3 enforce au PR level
- [[airlock-decisions-reference]] — Cree en task #12
- [[MOC-Incidents]] — Enrichi en task #13

---

_Generated: 2026-04-18_
