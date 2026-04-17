# Registre des Clés de Signature

**Dernière mise à jour**: 2026-04-17
**Gestionnaire**: @Fafa

---

## Clés Actives

| ID | Propriétaire | Email | Clé publique (ssh-ed25519) | Ajouté | Statut |
|----|--------------|-------|----------------------------|--------|--------|
| K001 | Deploy VPS | vault-signing@automecanik.com | `AAAAC3NzaC1lZDI1NTE5AAAAICjDduq8ifx/Uesw0qemXsLjrgPNzZju+zEQnmGAX4wa` | 2026-02-02 | Actif |
| K002 | Fafa (Windows) | automecanik.seo@gmail.com | `AAAAC3NzaC1lZDI1NTE5AAAAIGzlu+W6fcbvbqo1wXVaI/sGqitm/HOYvWA2uovt/blS` | 2026-04-17 | Actif |

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
automecanik.seo@gmail.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGzlu+W6fcbvbqo1wXVaI/sGqitm/HOYvWA2uovt/blS K002-fafa-windows
```

Le meme contenu est embarque dans `.github/workflows/vault-governance.yml` (job `g3-signed-commits`) pour que `%G?` retourne `G` sur le runner CI.

---

## Procédure de Révocation

1. Marquer la clé comme "Révoqué" dans ce registre
2. Retirer de `~/.ssh/allowed_signers`
3. Documenter la raison dans [[MOC-Incidents]] si compromission
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
