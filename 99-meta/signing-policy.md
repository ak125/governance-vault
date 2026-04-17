---
type: policy
status: canon
rule: G3
updated: 2026-04-17
---

# Politique de Signature des Commits (G3)

**Statut**: Actif depuis 2026-02-02
**Enforcement**: Obligatoire sur `main` (CI job `g3-signed-commits`)
**Regle canonique**: [[rules-vault]] G3

---

## Regle

> **Tous les commits de ce vault DOIVENT etre signes cryptographiquement.**
> Un commit non signe invalide la piste d'audit et sera rejete par le CI.

---

## Format de Signature

| Parametre | Valeur |
|-----------|--------|
| Format | SSH (preferred) ou GPG |
| Algorithme | Ed25519 |
| Cle par defaut | `~/.ssh/id_ed25519` |
| Cle dediee optionnelle | `~/.ssh/vault_signing_key` |

SSH signing est **prefere** a GPG car:
- Plus simple (pas de gpg-agent, pas de keyring)
- Reutilise la cle SSH deja utilisee pour GitHub
- Moderne (introduit dans Git 2.34, OpenSSH 8.0+)

---

## Verification

```bash
# Verifier la signature du dernier commit
git log --show-signature -1

# Resultat attendu:
# Good "git" signature for <email> with ED25519 key SHA256:<fingerprint>

# Verifier tous les commits depuis une date
git log --show-signature --since="2026-02-02"

# Verifier un commit specifique
git verify-commit <sha>
```

---

## Configuration

### Linux / macOS

```bash
# 1. Generer la cle (si pas deja fait)
ssh-keygen -t ed25519 -C "$(git config user.email)" -f ~/.ssh/id_ed25519

# 2. Configurer git pour signer avec SSH
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true

# 3. Creer le fichier allowed_signers
echo "$(git config user.email) $(cat ~/.ssh/id_ed25519.pub)" >> ~/.ssh/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers

# 4. (Optionnel) Ajouter la cle a GitHub comme "Signing Key"
#    https://github.com/settings/keys -> New SSH key -> type "Signing Key"
```

### Windows

Config supplementaire requise car Git for Windows embarque une version de OpenSSH qui ne gere pas la signature:

```powershell
# Diriger git vers OpenSSH de Windows
git config --global gpg.ssh.program "C:/Windows/System32/OpenSSH/ssh-keygen.exe"

# Le reste est identique a Linux/macOS
git config --global gpg.format ssh
git config --global user.signingkey "$HOME\.ssh\id_ed25519.pub"
git config --global commit.gpgsign true
git config --global gpg.ssh.allowedSignersFile "$HOME\.ssh\allowed_signers"
```

---

## Allowed Signers

Voir [[key-registry]] pour la liste des cles autorisees.

Format de `~/.ssh/allowed_signers`:

```
<email> <algo> <public-key>
automecanik.seo@gmail.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...
```

Une ligne par cle autorisee. Si une cle n'est pas dans ce fichier, `git log --show-signature` affichera "No signature" meme si le commit est bien signe.

---

## Violations

| Violation | Action |
|-----------|--------|
| Commit non signe push sur `main` | Rejet par CI `g3-signed-commits` |
| Signature invalide (`%G? = B`) | Rejet, investigation cle |
| Cle non enregistree dans `allowed_signers` | Affiche "No signature" localement (non bloquant CI) |

### Test local (doit echouer)

```bash
git config commit.gpgsign false
echo "test" > test.md && git add test.md
git commit -m "test unsigned"
# Le CI bloquera le push suivant sur main
git reset --hard HEAD~1
git config commit.gpgsign true
```

---

## Exceptions

Aucune exception sur `main`.

Pour les branches de travail (`feature/*`, `refactor/*`):
- La signature reste obligatoire par defaut
- Le CI verifie uniquement les commits merges dans `main`

Pour tests WIP temporaires (a ne pas push):
```bash
git commit --no-gpg-sign -m "WIP: test local only"
# Ces commits DOIVENT etre reecrit ou supprimes avant push
```

---

## Pre-Commit Hook (local)

Le vault fournit un hook `pre-commit` dans `.githooks/pre-commit` qui verifie G2 (orphans) et les wikilinks casses. Pour l'installer:

```bash
git config core.hooksPath .githooks
```

Le hook ne verifie **pas** la signature (git s'en charge automatiquement apres `commit.gpgsign true`).

---

## Rotation de Cle

Quand une cle est compromise ou perimee:

1. Retirer la cle de `~/.ssh/allowed_signers` sur toutes les machines autorisees
2. Marquer "Revoquee" dans [[key-registry]]
3. Generer nouvelle cle et ajouter a `allowed_signers`
4. Si compromission: documenter dans [[MOC-Incidents]]
5. Commit signe avec la nouvelle cle pour acter la rotation

---

## Voir aussi

- [[rules-vault]] - Regle G3 (canonique)
- [[key-registry]] - Registre des cles autorisees
- [[ci-policy]] - Politique CI/CD (G4)
- [[sync-log]] - Journal des syncs signes

---

_Derniere mise a jour: 2026-04-17_
