# Pattern : Single-maintainer merge avec CI gates comme enforcement

**Domaine :** Governance, vault operations
**Date :** 2026-04-27
**Décision :** session 2026-04-27, audit-trail [PR #91](https://github.com/ak125/governance-vault/pull/91)
**Status :** canon (mode opérationnel actuel)

---

## Contexte

Le `governance-vault` est aujourd'hui maintenu par un humain unique (`@ak125`,
Fafa). Cette réalité produit un blocage structurel sur la branch protection
`main` :

- `required_approving_review_count: 1` exige 1 reviewer
- GitHub interdit à un auteur d'approuver sa propre PR
- Aucun 2ᵉ collaborateur write-access dans le repo
- → toutes les PRs vault sont mergées en `BLOCKED / REVIEW_REQUIRED`

L'antipattern serait d'inventer une 2ᵉ identité fictive dans CODEOWNERS (un
bot non-installé, un compte fantôme) sans qu'elle puisse réellement
reviewer. CODEOWNERS deviendrait du bruit.

## Le pattern canon

Tant qu'un 2ᵉ reviewer humain ou bot installé n'est pas onboardé, le vault
opère en **single-maintainer + admin-merge + CI-gates-as-enforcement** :

### Étapes pour merger une PR canon

1. **Ouvrir la PR** avec un commit signé G3 et une description explicite
   (motivation, scope, hors-scope, test plan)
2. **Attendre les 5 gates CI au vert** :
   - `G2: Zero Orphelin` — chaque .md lié depuis un MOC ou archivé
   - `G3: Commits signes` — clé `vault-signing@automecanik.com` (SSH ou GPG)
   - `G4: CI read-only sur canon` — pas d'écriture LLM dans `ledger/decisions/**`
     ni `ops/rules/**` depuis le CI
   - `Broken Wikilinks` — tous les `[[…]]` résolvent vers un .md du vault
   - `No V1 Paths (ADR-015)` — aucun chemin `.local/governance-vault/`
3. **Admin merge** : `gh pr merge <N> --admin --squash`
   - Autorisé parce que `enforce_admins: false` côté branch protection
   - Le squash préserve `required_linear_history: true`
4. **Audit-trail** : ajouter un bullet dans la PR de session récap (#91 ou
   équivalent en cours) :
   ```markdown
   - PR #<N> ("<title>"), commit `<sha>`, mergée <date> via admin merge.
     Rationale : single-maintainer mode (cf. CODEOWNERS comment).
   ```

### Conditions d'utilisation

| Critère | Comportement |
|---|---|
| 5/5 CI gates verts | ✅ admin-merge autorisé |
| Au moins 1 CI gate rouge | ❌ fix requis avant merge (admin-merge bypasserait le gate) |
| PR touche `ledger/decisions/**` ou `ops/rules/**` | ⚠️ bullet audit-trail obligatoire (CODEOWNERS l'aurait normalement gate) |
| PR auteur ≠ ak125 | ✅ flow normal, ak125 review et merge sans admin override |

## Ce que ce pattern préserve

- **G3 commits signés** — chaque merge garde une chaîne de signatures
  cryptographique. La provenance est auditée même sans review humaine.
- **CI gates** — G2/G4 + Wikilinks + V1Paths restent enforcement réel.
  Aucune PR ne merge avec un gate rouge.
- **Audit-trail** — chaque admin-merge est listé dans une PR de session
  récap, signée, archivée. Recherchable via `git log --grep "admin merge"`.
- **Réversibilité** — quand un 2ᵉ reviewer arrive, ce pattern devient
  obsolète sans rien casser : il suffit d'arrêter d'utiliser `--admin`.

## Ce que ce pattern n'élimine pas

- **Single point of failure humain** — si Fafa a un blocage, le vault est
  gelé. ADR follow-up envisageable pour onboarder un 2ᵉ humain ou installer
  une GitHub App de gouvernance.
- **Self-review qualité** — pas de "quatre yeux" sur les ADRs et rules
  canon. Mitigé par : drafts longs en cours, audit-trail réguliers, possibilité
  de re-review post-merge via reverts/amendements.

## Procédure de revert vers le mode bi-maintainer

Quand un 2ᵉ reviewer humain ou bot est onboardé :

1. **Inviter** le compte/bot avec write access au repo (`Settings → Manage
   access`)
2. **Ajouter** son handle à `.github/CODEOWNERS` aux côtés de `@ak125`
3. **Retirer** le bloc commentaire "MODE OPÉRATIONNEL ACTUEL" du même fichier
4. **Cesser** d'utiliser `gh pr merge --admin` — le flow normal review-then-merge
   reprend automatiquement (la branch protection est inchangée)

Aucune modification de l'API branch protection requise — la config actuelle
(`required_approving_review_count: 1`, `require_code_owner_reviews: true`)
est compatible avec les 2 modes.

## Évidence d'application

Sessions où ce pattern a été appliqué :

- 2026-04-27 — PR #94 (fix wikilinks INC-2026-012), commit `8ed6184`,
  admin-merged après 5/5 CI verts
- _(à compléter par audit-trail #91)_

## Références

- [[ADR-015-vault-single-source-of-truth]] — vault SoT, principes G1-G4
- [[rules-governance-process]] — règles G1, G2, G3, G4
- `.github/CODEOWNERS` — bloc commentaire qui pointe vers ce document
