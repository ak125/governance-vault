# Rules - Vault Governance (G1-G4)

> Regles de gouvernance du vault lui-meme au 2026-10-01 (G1 reecrite par [[ADR-101-vault-decides-canon-authority|ADR-101]])
> **Version**: 3.0.0 | **Status**: CANON
> **Taxonomie**: G = Governance (G1-G4 = vault ici, G5-G8 = processus dans rules-governance-process.md)

---

## Objectif

Les regles **G1-G4** definissent comment le vault Obsidian lui-meme doit etre gouverne. Elles sont **non-negociables** et s'appliquent a toute modification du vault.

---

## G1: Le Vault Decide

**OBLIGATOIRE:** Les decisions de gouvernance vivent dans le vault ; le monorepo
les execute ([[ADR-060-repository-roles-doctrine|ADR-060]], ADR-101).

| Source | Role |
|--------|------|
| `ledger/decisions/adr/` : ADR `accepted` sans `superseded_by` actif | **DECIDE** - normatif |
| `ledger/rules/rules-*.md` | **DECIDE** - normatif ; modifie par PR signee, un changement de decision passe par un ADR |
| `.spec/00-canon/**` (monorepo) consomme par du code, un generateur ou un check CI | **CONTRAT** - fait foi dans son domaine, ne contredit pas un ADR accepte |
| `.spec/00-canon/**` (monorepo) sans consommateur | **PROSE DE REFERENCE** - aucune autorite, quel que soit son en-tete |
| Etat de `main` du monorepo | **FAIT** - dit ce qui est, pas ce qui doit etre |
| `governance-vault/ops/*` | **OPS** - MOC, templates, scripts |

**Consequence:**
- Une decision nait dans un ADR du vault, fusionne **avant** l'execution
- Un ADR qui decrit faussement l'existant se corrige par amendement
- Une divergence entre une decision et le code est un **constat** : la signaler,
  puis la resoudre par une PR de code ou un ADR d'amendement. Jamais appliquee a
  l'aveugle, jamais ignoree
- Aucune synchronisation monorepo → vault : la seule direction est
  vault → monorepo (miroirs d'[[ADR-061-workspace-governance|ADR-061]] §3)

**Verification:**
- [ ] Chaque decision appliquee est portee par un ADR `accepted` ?
- [ ] Les divergences constatees sont signalees et suivies (PR de code ou ADR) ?

---

## G2: Zero Orphelin

**OBLIGATOIRE:** Aucun document ne peut etre orphelin.

> Tout document du vault DOIT etre:
> - lie depuis **au moins 1 MOC** dans `ops/moc/`, OU
> - reference via un wikilink Obsidian depuis un autre document du vault

**Exceptions (whitelist):**
- Fichiers dans `ops/moc/` (les MOC sont des points d'entree)
- Fichiers dans `99-meta/` (gouvernance du vault)
- `README.md`, `CLAUDE.md` (racine)
- Fichiers dans `_assets/`, `_templates/` (ressources)

**Verification:**
```bash
_scripts/check-orphans.sh .
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

**Enforcement:**
- Check requis `G3: Commits signes` (`.github/workflows/vault-governance.yml`) : une PR dont un commit n'est pas signe ne peut pas etre fusionnee
- Hook `pre-push` local : refuse de pousser un commit non signe
- Exigences de protection de `main` : declarees dans `_scripts/setup-branch-protection.sh`, etat reel documente dans [[branch-protection]]

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

- [ ] G1: Une decision nouvelle ou modifiee passe-t-elle par un ADR ?
- [ ] G2: Le nouveau document sera-t-il lie depuis un MOC ?
- [ ] G3: Mon commit sera-t-il signe ?
- [ ] G4: Suis-je autorise (humain) a modifier cette zone ?

### Avant tout merge vers `main`:

- [ ] `_scripts/check-orphans.sh .` passe (G2)
- [ ] Tous les commits de la PR sont signes (G3)
- [ ] Aucune modification automatique sur zones canoniques (G4)
- [ ] Frontmatter YAML valide sur les nouveaux `.md`

---

## Sanctions

| Violation | Severite | Action |
|-----------|----------|--------|
| G1 (decision sans ADR, ou divergence non signalee) | Critique | Revert + Escalade CEO |
| G2 (orphelin non resolu) | Haute | Blocage pre-commit / CI |
| G3 (commit non signe) | Critique | Rejet PR automatique |
| G4 (IA ecrit zone read-only) | Critique | Revert + Kill-switch |

---

## References

- **rules-technical.md** - T1-T7: Regles techniques code
- **rules-governance-process.md** - G5-G8: Regles de gouvernance processus
- **rules-ai-cos.md** - AI1-AI10: Regles d'or agents IA
- **_scripts/check-orphans.sh** - Enforcement G2
- **ADR-101** - Autorite du vault et rang des fichiers `.spec/00-canon/` du monorepo

---

_Derniere mise a jour: 2026-10-01 (ADR-101)_
_Status: CANON - Gouvernance du vault lui-meme_
