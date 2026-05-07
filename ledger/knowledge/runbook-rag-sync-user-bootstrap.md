---
type: knowledge
status: canon
updated: 2026-05-07
---

# Runbook — `rag-sync` User Bootstrap (VPS DEV/PROD)

> Prérequis manuel pour [[ADR-046-r-stack-single-generator-and-layers]] § Layer L3 + [[ADR-050-quality-history-and-drift-detection]]. Doit être exécuté **avant** que `scripts/ops/lock-rag-knowledge.sh` (monorepo PR #356) puisse fonctionner.

## Contexte

[[ADR-046-r-stack-single-generator-and-layers]] § Layer L3 RAG MIRROR pose un schéma 3-tier permissions :

- **owner** = `rag-sync` (write+read pour cron sync)
- **group** = `nestjs` (read-only pour runtime backend)
- **other** = aucun accès

Concrètement : `chown rag-sync:nestjs rag/knowledge/`, `chmod 750/640`.

Le compte `rag-sync` n'existe pas par défaut sur les VPS DEV/PROD. Ce runbook documente sa création comme prérequis manuel à `scripts/ops/lock-rag-knowledge.sh`.

## Pré-requis

- Accès `sudo` sur le VPS cible (DEV `46.224.118.55` ou PROD `49.12.233.2`).
- Connaissance du compte runtime backend (par défaut `deploy` sur le monorepo actuel — à confirmer côté production).

## Procédure

### 1. Créer le compte système `rag-sync`

```bash
sudo useradd -r -m -s /bin/bash -c "RAG sync bot (ADR-046/050)" rag-sync
```

Flags :
- `-r` : compte système (UID < 1000)
- `-m` : crée `/home/rag-sync` (pour SSH key + crontab)
- `-s /bin/bash` : shell pour cron + debug

### 2. Créer le groupe `nestjs` (idempotent)

```bash
sudo groupadd -f nestjs
```

### 3. Membres du groupe `nestjs`

```bash
sudo usermod -aG nestjs rag-sync   # rag-sync membre du groupe pour cohérence
sudo usermod -aG nestjs deploy      # le compte runtime backend lit rag/knowledge en read-only
# Si NestJS tourne sous un autre compte (ex: `nestjs`) : usermod -aG nestjs nestjs
```

### 4. Générer la clé SSH du compte `rag-sync` (cron sync via SSH)

```bash
sudo -u rag-sync ssh-keygen -t ed25519 -N "" \
  -f /home/rag-sync/.ssh/id_ed25519 \
  -C "rag-sync@$(hostname) ADR-046/050"
```

La clé publique (`.ssh/id_ed25519.pub`) doit être ajoutée au repo GitHub pour cloner `automecanik-wiki` (Phase 3B PR-P), si la stratégie sync canon implique un `git pull` côté `rag-sync`.

### 5. Sudoers entry pour `lock-rag-knowledge.sh` (sans password)

```bash
echo "rag-sync ALL=(root) NOPASSWD: /opt/automecanik/app/scripts/ops/lock-rag-knowledge.sh" \
  | sudo tee /etc/sudoers.d/rag-sync
sudo chmod 440 /etc/sudoers.d/rag-sync
sudo visudo -c -f /etc/sudoers.d/rag-sync   # validation syntaxe
```

Restriction explicite : `rag-sync` peut **uniquement** exécuter `lock-rag-knowledge.sh` en root, pas d'autres commandes.

### 6. Vérification finale

```bash
id rag-sync
# uid=999(rag-sync) gid=999(rag-sync) groups=999(rag-sync),101(nestjs)

sudo -u rag-sync sudo /opt/automecanik/app/scripts/ops/lock-rag-knowledge.sh
# Doit s'exécuter sans demander de password
```

## Une fois le bootstrap terminé

Côté monorepo PR #356 (PR-E) :

```bash
# Sur le VPS, après merge PR #356 :
ssh deploy@<vps> "cd /opt/automecanik/app && sudo bash scripts/ops/lock-rag-knowledge.sh"
```

Cela applique le 3-tier permissions (`chown rag-sync:nestjs`, `chmod 750/640`) sur `/opt/automecanik/rag/knowledge/`.

## Rollback emergency

Si le lock 3-tier déclenche un incident bloquant en prod (ex: NestJS backend ne peut plus lire les fichiers à cause d'un bug de groupe) :

```bash
sudo bash /opt/automecanik/app/scripts/ops/unlock-rag-knowledge.sh
```

Cela restaure `0775 deploy:deploy` (état pré-MVP-0). Un incident-postmortem doit être ouvert au vault :

```
ledger/incidents/INC-YYYY-NNN-rag-unlock.md
```

Lié depuis [[MOC-Incidents]] G2.

## Liens

- [[ADR-046-r-stack-single-generator-and-layers]] § Layer L3
- [[ADR-050-quality-history-and-drift-detection]] (Phase 0 baseline)
- Monorepo PR #356 (`scripts/ops/lock-rag-knowledge.sh` + `unlock-rag-knowledge.sh`)
- Monorepo `backend/src/modules/rag-knowledge-bootstrap/` (NestJS bootstrap fail-fast)

## Référence

- Plan détaillé : `/home/deploy/.claude/plans/je-remarque-een-faiblesse-eventual-flamingo.md` (Action 5)
- Memory : `feedback_no_bricolage_clean_layer.md` (3-tier vs `chmod 555` monolithique)
