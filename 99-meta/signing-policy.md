---
type: policy
status: canon
rule: G3
updated: 2026-09-30
---

# Politique de Signature des Commits (G3)

**Statut**: Actif depuis 2026-02-02
**Enforcement**: check requis `G3: Commits signes` (job `g3-signed-commits`, voir [[branch-protection]]) + hook local `.githooks/pre-push`
**Regle canonique**: [[rules-vault]] G3

---

## Regle

> **Tous les commits de ce vault DOIVENT etre signes cryptographiquement au moment de leur push.**
> Un commit non signe dans une PR fait echouer le check requis G3 : la PR ne peut pas etre fusionnee dans `main`.

### Niveau d'enforcement

G3 est enforce **au niveau PR**. Le job `g3-signed-commits` execute `_scripts/check-signatures.sh` (meme script que le hook pre-push) :

| Evenement | Commits verifies |
|-----------|------------------|
| PR vers `main` | chaque commit `base..head` de la PR |
| Push sur `main` ou `refactor/**` | le dernier commit seulement (`HEAD~1..HEAD`) |
| Hook local pre-push | `merge-base(origin/main)..HEAD` |

Le script rejette les statuts `%G?` `N` (non signe) et `B` (signature invalide) ; il accepte tous les autres. Une signature SSH valide par une cle absente d'`allowed_signers` donne `U` et passe : G3 exige une signature, pas une cle du [[key-registry]].

**Note sur main** : les PR sont fusionnees en squash ; le commit cree sur `main` est signe par GitHub (`verification.reason = valid`), pas par K001/K002. `git verify-commit` local echoue sur ces commits (cle GitHub absente d'`allowed_signers`) : verifier par l'API. Les 22 commits non signes issus des merges rebase historiques (avril 2026, PR #336) et les pushes directs sans PR sont detailles dans [[branch-protection]], section « Methode de Merge et Chaine de Signature ».

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
vault-signing@automecanik.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... K001-deploy-vps
```

Une ligne par cle autorisee. Si une cle n'est pas dans ce fichier, `git log --show-signature` affichera "No signature" meme si le commit est bien signe.

---

## Violations

| Violation | Action |
|-----------|--------|
| Commit non signe dans une PR | Check requis G3 en echec, merge bloque ; le hook pre-push (s'il est installe) refuse deja le push |
| Push direct sur `main` | Refuse par la protection (PR requise, `enforce_admins: true`) |
| Signature invalide (`%G? = B`) | Rejet, investigation cle |
| Cle non enregistree dans `allowed_signers` | Statut `U` : `No principal matched` localement, **accepte** par G3 (non bloquant CI) |

### Test local (doit echouer)

```bash
git config commit.gpgsign false
echo "test" > test.md && git add test.md
git commit -m "test unsigned"
# Le hook pre-push refusera le push ; en PR, le check G3 echouera
git reset --hard HEAD~1
git config commit.gpgsign true
```

---

## Exceptions

Aucune exception sur `main`.

Pour les branches de travail (`feature/*`, `refactor/*`):
- La signature reste obligatoire par defaut
- Le hook pre-push verifie les commits de la branche avant chaque push
- Le CI verifie tous les commits de la branche des qu'une PR vers `main` est ouverte ; un push sur `refactor/**` ne verifie que le dernier commit

Pour tests WIP temporaires (a ne pas push):
```bash
git commit --no-gpg-sign -m "WIP: test local only"
# Ces commits DOIVENT etre reecrit ou supprimes avant push
```

---

## Pre-Commit Hook (local)

Le vault fournit deux hooks dans `.githooks/` :

- `pre-commit` : G2 (orphans) et wikilinks casses ; ne verifie **pas** la signature (git signe automatiquement avec `commit.gpgsign true`) ;
- `pre-push` : G2, wikilinks et signatures (`_scripts/check-signatures.sh`, range `merge-base(origin/main)..HEAD`).

Pour les installer :

```bash
git config core.hooksPath .githooks
```

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
- [[branch-protection]] - Protection serveur de main (checks requis, dont G2-G4)
- [[sync-log]] - Journal historique des syncs canon → vault (2026-02-02, plus alimente)

---

_Derniere mise a jour: 2026-09-30_
