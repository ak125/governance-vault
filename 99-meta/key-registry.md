# Registre des Clés de Signature

**Dernière mise à jour**: 2026-02-02
**Gestionnaire**: @admin

---

## Clés Actives

| ID | Propriétaire | Email | Fingerprint | Ajouté | Statut |
|----|--------------|-------|-------------|--------|--------|
| K001 | Deploy VPS | vault-signing@automecanik.com | `SHA256:qBBgd1ZloPXm0MkTd7L1fWe8OCAs8BjDfw6h7pxQCow` | 2026-02-02 | Actif |

---

## Format d'Enregistrement

Pour ajouter une nouvelle clé:

1. Générer la clé (voir [[signing-policy]])
2. Extraire le fingerprint: `ssh-keygen -lf ~/.ssh/vault_signing_key.pub`
3. Ajouter une ligne dans le tableau ci-dessus
4. Mettre à jour `~/.ssh/allowed_signers` sur toutes les machines
5. Commit signé de cette modification

---

## Allowed Signers File

Contenu du fichier `~/.ssh/allowed_signers`:

```
# governance-vault allowed signers
# Format: email key-type public-key comment

vault-signing@automecanik.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICjDduq8ifx/Uesw0qemXsLjrgPNzZju+zEQnmGAX4wa K001-deploy-vps
```

---

## Procédure de Révocation

1. Marquer la clé comme "Révoqué" dans ce registre
2. Retirer de `~/.ssh/allowed_signers`
3. Documenter la raison dans [[../01-incidents/]] si compromission
4. Générer nouvelle clé si nécessaire
5. Commit signé avec nouvelle clé

---

## Clés Révoquées

| ID | Propriétaire | Révoqué le | Raison |
|----|--------------|------------|--------|
| - | - | - | Aucune clé révoquée |

---

## Audit Trail

Toute modification de ce fichier doit être:
- Signée
- Justifiée dans le message de commit
- Tracée dans [[sync-log]]
