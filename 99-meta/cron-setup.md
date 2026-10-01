# Configuration Cron - Governance Vault

**Statut**: Manuel. Aucun des crons décrits ici n'est installé. Seuls crons installés qui touchent le vault : le writer planning (ADR-053, à l'arrêt) et `vault-sync.sh` (hors dépôt) — état détaillé dans [[governance-runtime-map]], Couche D.
**Dernière mise à jour**: 2026-10-01

---

## Principe Fondamental

> **Aucune écriture automatique dans le vault.**
> Les crons servent à NOTIFIER, pas à MODIFIER.

Écarts de fait avec ce principe, non tranchés ici (décision owner) :
- le writer planning (ADR-053) est conçu pour pousser directement sur `main` ;
  la protection de branche le refuse depuis `enforce_admins` (voir [[branch-protection]]) ;
- les wrappers `cron-sync-moc-decisions.sh` et `cron-sync-canon-mirrors.sh`
  (non installés, voir plus bas) ouvrent des auto-PR.

---

## Crons Recommandés (non installés)

### 1. Sync Canon — retiré

`_scripts/sync-canon.sh` copiait `.spec/00-canon/` du monorepo vers le vault,
sous des chemins v1 rejetés par le check requis `No V1 Paths (ADR-015)`. Il est
supprimé par [[ADR-101-vault-decides-canon-authority|ADR-101]] : le vault décide,
aucune synchronisation ne va du monorepo vers le vault. Journal historique :
[[sync-log]] (figé au 2026-02-02).

### 2. Audit Signatures (Mensuel)

Vérifie l'intégrité de la piste d'audit.

```bash
# Premier du mois à 8h (heure de la machine) - génère rapport
0 8 1 * * /opt/automecanik/governance-vault/_scripts/audit-signatures.sh --report >> /var/log/governance-vault/audit.log 2>&1
```

`--report` écrit `99-meta/reports/YYYY-MM-signature-audit.md` dans le checkout,
sans le commiter.

**Action manuelle requise**: Si commits non signés détectés:
1. Lire le rapport dans `99-meta/reports/`
2. Investiguer chaque commit (les commits squash de `main` sont signés par
   GitHub : les vérifier par l'API, voir [[signing-policy]])
3. Documenter si incident

### 3. Check Orphans (Hebdomadaire)

Vérifie que tous les documents sont liés. Déjà couvert à chaque PR par le check
requis `G2: Zero Orphelin` et par les hooks locaux.

```bash
# Dimanche à 7h (heure de la machine)
0 7 * * 0 /opt/automecanik/governance-vault/_scripts/check-orphans.sh /opt/automecanik/governance-vault >> /var/log/governance-vault/orphans.log 2>&1
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

État au 2026-09-30 : le répertoire existe (il ne contient que `planning-sync.log`) ;
`/etc/logrotate.d/governance-vault` n'existe pas, le log n'est pas roté.

Horaires : `cron` interprète les champs dans le fuseau de la machine
(Europe/Paris sur la machine DEV), pas en UTC.

---

## Notifications (Optionnel)

Aucun MTA n'est installé sur la machine DEV : `MAILTO` et `mail` n'envoient rien.
Pour une alerte réelle, utiliser un webhook :

```bash
# Script wrapper avec notification
#!/bin/bash
/opt/automecanik/governance-vault/_scripts/check-orphans.sh /opt/automecanik/governance-vault >/dev/null 2>&1 || \
  curl -X POST "$SLACK_WEBHOOK" -d '{"text": "Governance vault: orphans detected - review required"}'
```

---

## Cron prévus, non installés

### sync-moc-decisions (lundi 01:30 UTC prévu)

Générerait la projection canonique des frontmatters ADR vers la section
`<!-- AUTO-GENERATED:moc-decisions-canonical-index ... -->` de
`ops/moc/MOC-Decisions.md`. Si diff, ouvre une auto-PR signée G3 ; sinon no-op.

```bash
# Crontab deploy@VPS-DEV (non installée)
30 1 * * 1 /opt/automecanik/governance-vault/_scripts/cron-sync-moc-decisions.sh \
  >> /var/log/governance-vault/sync-moc-decisions.log 2>&1
```

**Pattern** (`_scripts/cron-sync-moc-decisions.sh`) :
- `git checkout main` + `git reset --hard origin/main` dans le checkout où il tourne
- Run `sync_moc_decisions.py --write` sur branche temp `govvault/cron-moc-sync-YYYY-MM-DD`
- Si diff : commit signé G3 + push de la branche + auto-PR via `gh pr create --label auto`
- Si no-op : exit 0, branche supprimée

**À installer uniquement sur un clone dédié** : le `reset --hard` détruirait le
travail en cours du checkout runtime partagé.

**Action manuelle requise** : reviewer humain valide ou ferme l'auto-PR.

En attendant, la projection est régénérée à la main (`--write`) dans chaque PR
qui modifie un ADR. Une seule auto-PR a existé (#250, fermée le 2026-05-10).
Les critères de stabilisation prévus (≥3 cycles OK, 0 commit fantôme) n'ont
jamais été mesurés : le cron n'a jamais tourné. La dérive de l'index est
détectée sur chaque PR depuis la PR #360 : `ci-vault-gate.sh pr` (PR-4) exécute
`sync_moc_decisions.py --check` (check `Vault Lint Gate (ADR-020)`), et une PR
qui modifie un ADR sans régénérer l'index a ce check rouge.

### sync-canon-mirrors

`_scripts/cron-sync-canon-mirrors.sh` (vault → monorepo, ADR-061 §3) suit le même
pattern côté monorepo et commence par `git reset --hard origin/main` dans le
checkout principal du monorepo. Même règle : clone dédié uniquement.

---

## Cron installé : writer planning (ADR-053)

```bash
# /etc/cron.d/planning-live
0 8 * * * deploy /opt/automecanik/governance-vault/_scripts/planning/run-cron.sh
```

Tourne à 08:00 heure de Paris (06:00 UTC en été), pas à 08:00 UTC comme
l'indiquent le commentaire du fichier et ADR-053. Rien publié sur `main` depuis
le 2026-08-14, aucune exécution journalisée depuis le 2026-09-14 : diagnostic et
consignes dans [[governance-runtime-map]], Couche D.

---

## Ce qui est INTERDIT

| Action | Raison |
|--------|--------|
| `--commit` en cron | Aucun commit automatique |
| `git push` en cron | Aucun push automatique |
| GitHub Actions write | CI en lecture seule |
| Sync monorepo → vault | Seul sens : vault → monorepo (`sync_canon_mirrors.py`, ADR-061 §3) |

---

## Vérification de la Config

```bash
# Lister les crons actifs
crontab -l
cat /etc/cron.d/planning-live

# Tester manuellement chaque script
/opt/automecanik/governance-vault/_scripts/audit-signatures.sh
/opt/automecanik/governance-vault/_scripts/check-orphans.sh /opt/automecanik/governance-vault
python3 /opt/automecanik/governance-vault/_scripts/sync_moc_decisions.py --check
```

---

*Voir aussi: [[signing-policy]], [[key-registry]], [[governance-runtime-map]], [[branch-protection]]*
