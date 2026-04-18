# Audit Signatures - 2026-04

**Date**: 2026-04-18T12:42:16+02:00
**Vault**: C:\Users\Marwane\nestjs-remix-monorepo\governance-vault
**Total commits**: 70
**Signés**: 50
**Non signés**: 20

---

## Résultat

❌ **COMMITS NON SIGNÉS DÉTECTÉS**

| SHA | Date | Auteur | Message |
|-----|------|--------|---------|
| ada6a8f | 2026-04-18 12:21:41 +0200 | Fafa | docs: cleanup residuals from v2 refactor report |
| 1b8798f | 2026-04-18 12:05:17 +0200 | Fafa | fix(ci): restrictions=null via --input JSON (corrige 422) |
| 0bc0215 | 2026-04-17 18:05:49 +0200 | Fafa | ci(g3): load allowed_signers so %G? returns G instead of N |
| d7ae533 | 2026-04-17 17:32:05 +0200 | Fafa | phase6: enforcement (pre-commit hooks, CI, CLAUDE.md, CRLF fix) |
| e3e432b | 2026-04-17 16:44:21 +0200 | Fafa | phase5: resolve orphans with INDEX.md pattern (177 -> 0) |
| 699dbf5 | 2026-04-17 16:25:17 +0200 | Fafa | refactor(decisions): promote DEC-004 to ADR-014, reclassify 3 non-decisions |
| 74a9676 | 2026-04-17 16:14:59 +0200 | Fafa | refactor(vault): migrate to v2 layout + unify taxonomy T/G/AI/V |
| cc0d10e | 2026-04-17 15:51:44 +0200 | Fafa | chore(vault): remove exact duplicate 03-governance.md |
| 8c1b740 | 2026-04-04 17:31:04 +0200 | auto pieces equipement | fix(adr-013): période observe proportionnée 3j/7j/14j |
| 3cabbd3 | 2026-04-04 16:44:43 +0200 | auto pieces equipement | Merge pull request #1 from ak125/feature/agent-seo-subleads |
| acf3daf | 2026-04-04 14:40:27 +0000 | Claude Code | feat(agents): add 4 SEO sub-leads under IA-SEO Master (G1 process) |
| c12f8ff | 2026-04-04 14:32:33 +0000 | Claude Code | feat(governance): ADR-013 — cycle de vie agents + processus G1/G2/G3 |
| 141b406 | 2026-04-04 13:08:32 +0000 | Claude Code | feat(agents): add 4 QA agents + update REG-001 registry |
| 2240635 | 2026-03-08 23:34:12 +0000 | Claude Code | docs: BUNDLE-REGISTRY — mise à jour REG-001 v1.4.1 → v2.1.0 |
| 5f1d77b | 2026-02-04 00:19:57 +0100 | Deploy Bot | docs(ai-cos): add AI-COS documentation to knowledge base |
| f9b65ad | 2026-02-03 17:45:32 +0100 | Deploy Bot | chore(governance): add ADR-005 + audit-trail for formalization complete |
| e062c3b | 2026-02-03 17:41:54 +0100 | Deploy Bot | docs: add P2 ENFORCE baseline + resolve merge |
| 6cba5ec | 2026-02-03 17:38:57 +0100 | Deploy Bot | docs: add P2 ENFORCE baseline snapshot |
| 42cb376 | 2026-02-02 17:20:27 +0100 | Deploy Bot | fix(moc): link README to MOC-Governance |
| 93162cc | 2026-02-02 15:04:57 +0100 | Deploy Bot | feat(governance): add templates, MOCs, and signing policy |

---

## Interpretation

**Total non signes : 20/70**. Ce resultat est **attendu** sur ce repo (plan GitHub Free + `gh pr merge --rebase`). Les 20 commits se repartissent ainsi :

- **Commits pre-policy (< 2026-02-02)** : bootstrap historique du vault, pas d'action
- **Commits post-rebase** (PRs mergees en rebase-merge) : artefact GitHub Free documente dans [[branch-protection]] section "Artefact Connu : Signature Chain au Merge Rebase"

La chain-of-custody est preservee via :
- CI G3 sur chaque PR (verification au moment du merge)
- GitHub Actions logs (tamper-evident)
- GitHub audit log (identite du merger)

## Actions Requises

1. Classer chaque commit non signe : pre-policy / post-rebase / anomalie vraie
2. Si anomalie vraie (post-policy, pas de PR associee) : investiguer legitimite
3. Documenter dans [[MOC-Incidents]] si compromission suspectee
4. Considerer re-signature si possible (rebase interactif) pour les anomalies

> **Note** : Les commits non signes sur main sont souvent un artefact attendu (merge rebase sans re-signature sur plan Free). Voir [[branch-protection]].

---

## Prochaine Exécution

Planifier l'audit pour le mois suivant.

*Généré automatiquement par audit-signatures.sh*

