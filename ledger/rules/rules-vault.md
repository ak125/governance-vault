# Rules - Vault Governance (G1-G4)

> **Source de verite** - Regles de gouvernance du vault lui-meme au 2026-04-17
> **Version**: 2.0.0 | **Status**: CANON
> **Taxonomie**: G = Governance (G1-G4 = vault ici, G5-G8 = processus dans rules-governance-process.md)

---

## Objectif

Les regles **G1-G4** definissent comment le vault Obsidian lui-meme doit etre gouverne. Elles sont **non-negociables** et s'appliquent a toute modification du vault.

---

## G1: Canon Fait Foi

**OBLIGATOIRE:** Le canon architectural reste **exclusivement** dans le monorepo (`.spec/00-canon/`).

| Source | Role |
|--------|------|
| `.spec/00-canon/*` (monorepo) | **CANON** - Source de verite technique |
| `governance-vault/ledger/*` | **LEDGER** - Miroir enrichi operationnel |
| `governance-vault/ops/*` | **OPS** - MOC, templates, scripts |

**En cas de conflit:** `.spec/00-canon/` fait foi.

**Consequence:**
- Une regle technique modifiee dans le vault SANS PR sur le canon = **violation G1**
- Le vault peut enrichir (exemples, post-mortems, ADR) mais ne peut pas contredire le canon

**Verification:**
- [ ] Chaque regle technique du vault a une source dans `.spec/00-canon/` ?
- [ ] Les divergences sont documentees dans un ADR ?

---

## G2: Zero Orphelin

**OBLIGATOIRE:** Aucun document ne peut etre orphelin.

> Tout document du vault DOIT etre:
> - lie depuis **au moins 1 MOC** dans `ops/moc/`, OU
> - reference via `[[wikilink]]` depuis un autre document du vault

**Exceptions (whitelist):**
- Fichiers dans `ops/moc/` (les MOC sont des points d'entree)
- Fichiers dans `99-meta/` (gouvernance du vault)
- `README.md`, `CLAUDE.md` (racine)
- Fichiers dans `_assets/`, `_templates/` (ressources)

**Verification:**
```bash
./scripts/check-orphans.sh .
# Sortie: ❌ Orphans found: N (si violation)
#         ✅ No orphans found (si conforme)
```

**Sanction:** Un orphelin bloque le pre-commit hook. CI refuse le merge.

---

## G3: Commits Signes

**OBLIGATOIRE:** Tous les commits DOIVENT etre signes cryptographiquement (GPG ou SSH).

**Raison:** Un commit non signe invalide la piste d'audit. Sans signature, impossible de prouver qui a modifie une regle canonique.

```bash
# Setup (une fois)
git config --global commit.gpgsign true
git config --global user.signingkey <KEY_ID>

# Verification
git log --show-signature -5
```

**CI enforcement:**
- GitHub Actions refuse les PR avec commits non signes
- Branch protection: `require_signed_commits: true` sur `main`

**Verification:**
- [ ] `git config --get commit.gpgsign` renvoie `true` ?
- [ ] Les 5 derniers commits ont une signature `Good signature` ?

---

## G4: CI Read-Only sur Canon

**OBLIGATOIRE:** La CI et les agents IA sont **read-only** sur les fichiers canoniques.

**Zones read-only pour l'IA:**
- `ledger/rules/*.md` (regles T/G/AI/V)
- `ledger/decisions/ADR-*.md` (decisions architecturales)
- `ledger/knowledge/architecture.md` (architecture canonique)

**Zones write-allowed pour l'IA:**
- `ops/work/*` (brouillons, explorations)
- `ledger/incidents/*` (post-mortems avec validation humaine)
- `99-meta/sync-log.md` (logs automatiques)

**Modification d'un fichier read-only:**
1. IA prepare un draft dans `ops/work/proposals/`
2. Humain (Human CEO) review
3. Humain applique le changement manuellement OU approuve PR signee
4. Commit signe dans la branche dediee

**Kill-switch:**
- `AI_VAULT_WRITE=false` (defaut en prod) bloque toute ecriture IA sur les zones canoniques

**Verification:**
- [ ] Pre-commit hook verifie que l'auteur du commit n'est pas un agent IA pour zones canoniques ?
- [ ] Variable `AI_VAULT_WRITE` est definie a `false` en production ?

---

## Checklist Vault Governance

### Avant toute modification du vault:

- [ ] G1: Modification est-elle cohérente avec `.spec/00-canon/` ?
- [ ] G2: Le nouveau document sera-t-il lie depuis un MOC ?
- [ ] G3: Mon commit sera-t-il signe ?
- [ ] G4: Suis-je autorise (humain) a modifier cette zone ?

### Avant tout merge vers `main`:

- [ ] `./scripts/check-orphans.sh .` passe (G2)
- [ ] Tous les commits de la PR sont signes (G3)
- [ ] Aucune modification automatique sur zones canoniques (G4)
- [ ] Frontmatter YAML valide sur les nouveaux `.md`

---

## Sanctions

| Violation | Severite | Action |
|-----------|----------|--------|
| G1 (divergence canon sans ADR) | Critique | Revert + Escalade CEO |
| G2 (orphelin non resolu) | Haute | Blocage pre-commit / CI |
| G3 (commit non signe) | Critique | Rejet PR automatique |
| G4 (IA ecrit zone read-only) | Critique | Revert + Kill-switch |

---

## References

- **rules-technical.md** - T1-T7: Regles techniques code (canon)
- **rules-governance-process.md** - G5-G8: Regles de gouvernance processus
- **rules-ai-cos.md** - AI1-AI10: Regles d'or agents IA
- **scripts/check-orphans.sh** - Enforcement G2
- `.spec/00-canon/` (monorepo) - Source de verite technique

---

_Derniere mise a jour: 2026-04-17_
_Status: CANON - Gouvernance du vault lui-meme_
