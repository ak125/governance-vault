---
type: audit-trail
---

# Audit Trail

## Chronologie (ordre inverse)

### 2026-04-18 (jour 2)

- **Branch protection re-applique** — `setup-branch-protection.sh` execute avec corrections (display names au lieu de job keys). Contexts desormais alignes: PR #4 peut merger.
- **PR #5 ouverte** (cleanup/residuels-v2) — 7 fichiers: airlock-decisions-reference + MOC-Knowledge maj + MOC-Compliance maj + MOC-Incidents rewrite + branch-protection + signing-policy maj + README maj
- **PR #5 mergee** — 4 checks verts, fast-forward, branche supprimee cote serveur et local
- **Task #14 complete** — `99-meta/branch-protection.md` rediger
- **Task #13 complete** — MOC-Incidents enrichi (taxonomie severite + RACI + lifecycle)
- **Task #12 complete** — airlock-decisions-reference cree dans `ledger/knowledge/`
- **EP-20260418-governance-hardening genere** (ce pack)

### 2026-04-17 (jour 1)

- **CI G3 fix applique** — `.github/workflows/vault-governance.yml` etoffe avec step "Configure SSH signature verification" (writes allowed_signers, sets gpg.ssh.allowedSignersFile)
- **`99-meta/key-registry.md` maj** — cle K002 (Fafa-Windows) ajoutee
- **PR #4 mergee** — fix G3 accepte, 4 checks verts
- **Phase 6 complete** — pre-commit hook + CI workflow + README + CLAUDE.md
- **Phase 5 complete** — 0 orphelin (14 → 0), 0 wikilink casse
- **PR #3 mergee** — Phase 5 + 6 combinees sur main

## Artefacts traces

- Historique git complet: `git log --show-signature --since="2026-04-17"`
- Signature audit: `_scripts/audit-signatures.sh --report` → `99-meta/reports/2026-04-signature-audit.md`
- Branch protection verification: `gh api repos/ak125/governance-vault/branches/main/protection`

## Decisions infra prises durant la periode

| Decision | Motivation | Trace |
|----------|------------|-------|
| Hardcoder cles publiques dans workflow | Cles publiques non-sensibles, evite secret Actions | commit workflow |
| `enforce_admins: true` | Personne ne bypasse, meme owner | setup-branch-protection.sh |
| `required_linear_history: true` | Pas de merge commits, rebase obligatoire | setup-branch-protection.sh |
| Display names dans contexts | GitHub matche par `name:`, pas par job key (diagnostique apres PR #4 bloquee) | setup-branch-protection.sh v2 |

## Incidents dans la periode

Aucun.

- Aucun kill-switch AI_VAULT_WRITE active
- Aucune tentative de push direct sur main (protection bloquerait)
- Aucune cle compromise
- Aucun canon modifie depuis CI

## Voir aussi

- [[MOC-AuditTrail]] — Retrospectives de phase (Phase 4 post-hardening deja presente, Phase 5+6 a ajouter)
- [[2026-02-phase4-post-hardening-summary]] — Retro precedente
