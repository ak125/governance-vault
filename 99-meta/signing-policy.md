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

---

## Point d'Écriture Unique (R-Vault-03)

> **Le vault ne peut être modifié que depuis ce VPS** (`/opt/automecanik/governance-vault`).

### Mécanismes d'Enforcement

| Niveau | Mécanisme | Statut |
|--------|-----------|--------|
| Local | Hook `pre-push` vérifie signatures | ✅ Actif |
| GitHub | Branch protection (signed commits) | ⚠️ Non enforcé (plan gratuit) |

### Hook Pre-Push

Installé à `.git/hooks/pre-push`, ce hook :
1. Intercepte chaque `git push`
2. Vérifie que TOUS les commits à pousser sont signés
3. Bloque le push si un commit non signé est détecté

```bash
# Test du hook
git config commit.gpgsign false
echo "test" > test.md && git add test.md
git commit -m "test unsigned"
git push  # ❌ PUSH BLOCKED: unsigned commit detected
git reset --hard HEAD~1
git config commit.gpgsign true
```

### Pourquoi Ce Modèle ?

1. **Contrôle centralisé**: Une seule machine autorisée = audit simplifié
2. **Pas de drift**: Pas de risque de modifications depuis d'autres sources
3. **Clé unique**: Une seule clé de signature (`K001`) = traçabilité maximale
4. **Backup sûr**: La clé est sur le VPS avec passphrase + backup offline

### Ajout d'une Nouvelle Machine (Procédure)

1. Générer nouvelle clé sur la machine
2. Enregistrer dans [[key-registry]]
3. Ajouter au fichier `~/.ssh/allowed_signers` sur TOUTES les machines
4. Commit signé de la modification (depuis machine existante)
5. Tester la signature depuis nouvelle machine

---

## Audit Trail

Chaque modification de cette politique doit être:
- Signée
- Justifiée dans le message de commit
- Tracée dans [[sync-log]]

*Dernière mise à jour: 2026-02-02*
