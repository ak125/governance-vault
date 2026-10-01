# Rules - Vault Governance (G1-G4)

> Regles de gouvernance du vault lui-meme au 2026-10-01 (G1 reecrite par [[ADR-101-vault-decides-canon-authority|ADR-101]], G4 par [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]])
> **Version**: 3.1.0 | **Status**: CANON
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

## G4: Ecriture par PR, CI en Lecture Seule

**OBLIGATOIRE:** Le vault ne se modifie que par PR. Un agent prepare, un humain fusionne. La CI
ne produit aucun contenu du vault ([[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]] D3).

1. **Aucune ecriture directe sur `main`.** Toute modification passe par une PR aux commits signes
   (G3), sous les checks requis.
2. **Un agent prepare, un humain fusionne.** Un agent peut preparer une PR dans toute zone du
   vault ; il ne fusionne jamais. La fusion d'une PR qui modifie un ADR, une regle ou une policy
   est une decision (G1).
3. **La CI ne produit aucun contenu du vault.** Chaque workflow declare un bloc `permissions:` au
   niveau racine, n'obtient aucun scope `write` hors liste justifiee (`issues`), ne lance ni
   `git commit` ni `git push`, et n'utilise aucun jeton autre que son `GITHUB_TOKEN` hors exception
   nommee dans le script de verification.

**Enforcement:**
- Point 1 : protection de `main` (PR requise, checks requis, `enforce_admins`), voir [[branch-protection]]
- Point 2 : **regle de conduite**. La protection n'exige aucune revue, et un jeton qui peut ouvrir
  une PR peut la fusionner. La rendre mecanique (identite GitHub distincte pour les agents, revue
  requise) est une decision owner
- Point 3 : `_scripts/check-ci-read-only.py`, execute sur les workflows reels par
  `_scripts/test_ci_read_only.py` dans le check requis `Vault Scripts Tests`

**Reponse a incident:** fermer les PR de l'agent, puis revoquer son acces en ecriture (cle de
signature, voir [[key-registry]] « Procédure de Révocation », et jeton GitHub de la machine qui
l'execute). Il n'y a pas de kill-switch : `AI_VAULT_WRITE` est retire (ADR-102 D4).

**Verification:**
- [ ] La modification passe par une PR, et non par un push direct ?
- [ ] Un agent n'a fusionne aucune PR ?
- [ ] `python3 _scripts/check-ci-read-only.py .` renvoie 0 violation ?

---

## Checklist Vault Governance

### Avant toute modification du vault:

- [ ] G1: Une decision nouvelle ou modifiee passe-t-elle par un ADR ?
- [ ] G2: Le nouveau document sera-t-il lie depuis un MOC ?
- [ ] G3: Mon commit sera-t-il signe ?
- [ ] G4: Ma modification passe-t-elle par une PR, sans fusion par un agent ?

### Avant tout merge vers `main`:

- [ ] `_scripts/check-orphans.sh .` passe (G2)
- [ ] Tous les commits de la PR sont signes (G3)
- [ ] La PR n'est pas fusionnee par un agent, et `_scripts/check-ci-read-only.py .` passe (G4)
- [ ] Frontmatter YAML valide sur les nouveaux `.md`

---

## Sanctions

| Violation | Severite | Action |
|-----------|----------|--------|
| G1 (decision sans ADR, ou divergence non signalee) | Critique | Revert + Escalade CEO |
| G2 (orphelin non resolu) | Haute | Blocage pre-commit / CI |
| G3 (commit non signe) | Critique | Rejet PR automatique |
| G4 (push direct, fusion par un agent, CI qui ecrit) | Critique | Revert + fermeture des PR de l'agent + revocation de son acces |

---

## References

- **rules-technical.md** - T1-T7: Regles techniques code
- **rules-governance-process.md** - G5-G8: Regles de gouvernance processus
- **rules-ai-cos.md** - AI1-AI10: Regles d'or agents IA
- **_scripts/check-orphans.sh** - Enforcement G2
- **_scripts/check-ci-read-only.py** - Enforcement G4 (point 3)
- **ADR-101** - Autorite du vault et rang des fichiers `.spec/00-canon/` du monorepo
- **ADR-102** - Airlock reduit au RPC gate, canal de bundles retire, G4 reecrite

---

_Derniere mise a jour: 2026-10-01 (ADR-101, ADR-102)_
_Status: CANON - Gouvernance du vault lui-meme_
