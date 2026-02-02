# Configuration Cron - Governance Vault

**Statut**: Manuel (non automatisé)
**Dernière mise à jour**: 2026-02-02

---

## Principe Fondamental

> **Aucune écriture automatique dans le vault.**
> Les crons servent à NOTIFIER, pas à MODIFIER.

---

## Crons Recommandés

### 1. Sync Canon (Dry-Run Quotidien)

Vérifie si des fichiers canon ont changé, sans modifier le vault.

```bash
# Ajouter au crontab de deploy
crontab -e

# Tous les jours à 6h - dry-run uniquement
0 6 * * * /opt/automecanik/governance-vault/scripts/sync-canon.sh --dry-run >> /var/log/governance-vault/sync-canon.log 2>&1
```

**Action manuelle requise**: Si des changements sont détectés:
```bash
cd /opt/automecanik/governance-vault
./scripts/sync-canon.sh --commit  # Applique + commit signé
git push origin main
```

### 2. Audit Signatures (Mensuel)

Vérifie l'intégrité de la piste d'audit.

```bash
# Premier du mois à 8h - génère rapport
0 8 1 * * /opt/automecanik/governance-vault/scripts/audit-signatures.sh --report >> /var/log/governance-vault/audit.log 2>&1
```

**Action manuelle requise**: Si commits non signés détectés:
1. Lire le rapport dans `99-meta/reports/`
2. Investiguer chaque commit
3. Documenter si incident

### 3. Check Orphans (Hebdomadaire)

Vérifie que tous les documents sont liés.

```bash
# Dimanche à 7h
0 7 * * 0 /opt/automecanik/app/.spec/governance/scripts/check-orphans.sh /opt/automecanik/governance-vault >> /var/log/governance-vault/orphans.log 2>&1
```

---

## Setup Initial

```bash
# Créer le répertoire de logs
sudo mkdir -p /var/log/governance-vault
sudo chown deploy:deploy /var/log/governance-vault

# Configurer logrotate
sudo tee /etc/logrotate.d/governance-vault <<EOF
/var/log/governance-vault/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
EOF
```

---

## Notifications (Optionnel)

Pour recevoir des alertes en cas de problème:

```bash
# Ajouter à la fin de chaque cron
# ... | mail -s "Governance Vault Alert" admin@automecanik.com
```

Ou utiliser un webhook Discord/Slack:

```bash
# Script wrapper avec notification
#!/bin/bash
OUTPUT=$(/opt/automecanik/governance-vault/scripts/sync-canon.sh --dry-run 2>&1)
if echo "$OUTPUT" | grep -q "changes detected"; then
  curl -X POST "$SLACK_WEBHOOK" -d "{\"text\": \"Canon changes detected - review required\"}"
fi
```

---

## Ce qui est INTERDIT

| Action | Raison |
|--------|--------|
| `--commit` en cron | Aucun commit automatique |
| `git push` en cron | Aucun push automatique |
| GitHub Actions write | CI en lecture seule |
| Sync bidirectionnel | Canon → Vault uniquement |

---

## Vérification de la Config

```bash
# Lister les crons actifs
crontab -l

# Tester manuellement chaque script
/opt/automecanik/governance-vault/scripts/sync-canon.sh --dry-run
/opt/automecanik/governance-vault/scripts/audit-signatures.sh
/opt/automecanik/app/.spec/governance/scripts/check-orphans.sh /opt/automecanik/governance-vault
```

---

*Voir aussi: [[signing-policy]], [[key-registry]]*
