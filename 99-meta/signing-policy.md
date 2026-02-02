# Politique de Signature des Commits

**Statut**: Actif depuis 2026-02-02
**Enforcement**: Obligatoire sur branche `main`

---

## Règle

> **Tous les commits de ce vault DOIVENT être signés cryptographiquement.**
> Un commit non signé invalide la piste d'audit.

---

## Format de Signature

| Paramètre | Valeur |
|-----------|--------|
| Format | SSH (Ed25519) |
| Algorithme | Ed25519 |
| Fichier clé | `~/.ssh/vault_signing_key` |

---

## Vérification

```bash
# Vérifier la signature du dernier commit
git log --show-signature -1

# Vérifier tous les commits depuis une date
git log --show-signature --since="2026-02-02"

# Vérifier un commit spécifique
git verify-commit <sha>
```

**Résultat attendu**: `Good "git" signature for...`

---

## Configuration Requise

```bash
# Configuration globale (une fois par machine)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/vault_signing_key.pub
git config --global commit.gpgsign true

# Ou configuration locale (repo-only)
git config --local gpg.format ssh
git config --local user.signingkey ~/.ssh/vault_signing_key.pub
git config --local commit.gpgsign true
```

---

## Génération de Clé (Nouvelle Machine)

```bash
ssh-keygen -t ed25519 -C "vault-signing@automecanik.com" -f ~/.ssh/vault_signing_key
```

**Important**:
- Utiliser une passphrase forte
- Backup chiffré offline obligatoire
- Ne JAMAIS partager la clé privée

---

## Allowed Signers

Voir [[key-registry]] pour la liste des clés autorisées.

Le fichier `~/.ssh/allowed_signers` doit contenir:

```
vault-signing@automecanik.com ssh-ed25519 AAAA... <fingerprint>
```

---

## Violations

| Violation | Action |
|-----------|--------|
| Commit non signé | Rejet immédiat, investigation |
| Signature invalide | Rejet, vérification clé |
| Clé non enregistrée | Rejet, ajout au registry requis |

---

## Exceptions

Aucune exception autorisée sur `main`.

Pour tests sur branches de développement, utiliser:
```bash
git commit --no-gpg-sign -m "WIP: test only"
```

Ces commits NE DOIVENT PAS être mergés sur `main`.
