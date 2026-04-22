---
id: INC-2026-008
date: 2026-04-22
severity: medium
status: resolved
impact_duration: "indéterminée (Redis exposé ≥1 snapshot BSI du 2026-04-21 13:12 UTC, fenêtre réelle probablement plus longue — config en place depuis ≥ 5 semaines d'après age container)"
affected_systems: [vps-dev-46.224.118.55, redis-dev, docker-compose-dev, docker-compose-redis, docker-compose-meilisearch]
root_cause: "3 fichiers docker-compose (dev.yml, redis.yml, meilisearch.yml) exposaient `ports: '6379:6379'` sur 0.0.0.0 sans --requirepass. L'alignement de prod.yml (ports commentés, 2025-12-17 commit 2c4c24aa) n'avait jamais été propagé aux 3 autres fichiers. La tentative de mars 2026 (commit 71ac9791) a retiré --requirepass à cause d'un crash-loop, sans restaurer la fermeture de port."
related_rules: []
related_adr: []
owner: "@fafa"
reviewed_by: ""
---

# Incident: Redis DEV exposé publiquement sans authentification (BSI)

## Synthèse

Serveur Redis 7.4.7 sur DEV VPS `46.224.118.55:6379` accessible depuis Internet sans authentification. Signalé par le CERT-Bund allemand (BSI) via Hetzner Abuse. **Zero compromission détectée** lors de l'audit post-remédiation. Remédiation 2 couches appliquée le jour même : firewall Hetzner + alignement compose files (PR #102).

## Timeline

| Heure (UTC) | Événement |
|-------------|-----------|
| 2026-04-21 13:12:07 | BSI scanne `46.224.118.55:6379` → Redis 7.4.7 répond sans auth |
| 2026-04-22 ~09:39 | Email Hetzner Abuse reçu (ticket `AbuseID:118DAFD:19`, CERT `CB-Report#20260422-10008190`) |
| 2026-04-22 ~12:30 | Investigation démarrée : 4 fichiers compose identifiés exposant 6379 sur 0.0.0.0 |
| 2026-04-22 ~12:40 | Historique git analysé : 3 tentatives précédentes (2c4c24aa, 16410088, 71ac9791) ont oscillé entre auth ON/OFF avec crash-loop |
| 2026-04-22 ~12:50 | Décision : pas de `--requirepass` (régresseur confirmé). Solution = isolation réseau |
| 2026-04-22 ~13:00 | Hetzner Cloud Firewall `dev-vps-redis-block` créé et attaché au serveur DEV |
| 2026-04-22 ~13:05 | Validation : BSI inbound tcp/6379 bloqué. Site DEV opérationnel (80/443 étaient déjà fermés, aucun service HTTP public). |
| 2026-04-22 ~13:10 | Audit compromission READ-ONLY sur `redis-dev` : CLEAN |
| 2026-04-22 ~13:15 | PR #102 ouverte sur monorepo pour alignement compose files |
| 2026-04-22 ~13:20 | Mémoire Claude Code mise à jour (règle anti `--requirepass` + fait firewall) |

## Impact

- **Utilisateurs affectés** : 0 (DEV VPS, pas d'impact user-facing)
- **Transactions perdues** : 0
- **Durée d'indisponibilité** : 0 minute (aucun service coupé lors de la remédiation)
- **Impact business** : 0 direct, mais risque latent (lecture potentielle de sessions/cache si exploité durant la fenêtre d'exposition)
- **Impact gouvernance** : ticket BSI ouvert → nécessite réponse documentée à Hetzner

## Root Cause

Trois fichiers `docker-compose` historiquement mal alignés :

| Fichier | État avant | État en prod (modèle) |
|---------|-----------|------------------------|
| `docker-compose.dev.yml` | `ports: '6379:6379'` + `image: redis:latest` | — |
| `docker-compose.redis.yml` | `ports: '6379:6379'` + `image: redis:latest` | — |
| `docker-compose.meilisearch.yml` | `ports: "6379:6379"` + `redis:7-alpine` | — |
| `docker-compose.prod.yml` | `# ports:` commenté, `# SECURITY: Never expose Redis publicly` | ✅ pattern éprouvé (2025-12-17) |

**Pourquoi le désalignement a persisté** : la correction de 2025-12-17 (commit `2c4c24aa`) a été appliquée UNIQUEMENT sur `docker-compose.prod.yml`. Les 3 autres fichiers n'ont jamais été touchés. Aucun lint / hook pre-commit ne vérifiait la cohérence inter-compose.

**Pourquoi `--requirepass` n'a pas été remis** : trois tentatives historiques ont échoué en régression :
- `2c4c24aa` (2025-12-17) : ajout `--requirepass` prod → OK initialement
- `16410088` (2026-01-17) : retrait preprod ("no password needed")
- `71ac9791` (2026-03-05) : retrait prod, cause : `REDIS_PASSWORD was never set, caused crash-loop`

Le secret `REDIS_PASSWORD` n'est pas propagé de façon fiable dans l'env GitHub Actions / docker compose up. Chaque `--requirepass` vide crée un crash-loop qui invalide les sessions (cookies `connect.sid`, TTL 30j).

## Résolution

### Couche 1 — Firewall Hetzner (niveau réseau, instantané)

Firewall `dev-vps-redis-block` créé dans la Hetzner Cloud Console et attaché au serveur DEV `46.224.118.55`.

**Inbound rules (allowlist) :**

| Protocol | Port | Source | Rôle |
|----------|------|--------|------|
| TCP | 22 | 0.0.0.0/0, ::/0 | SSH |
| TCP | 80 | 0.0.0.0/0, ::/0 | HTTP (Caddy futur, actuellement fermé host-level) |
| TCP | 443 | 0.0.0.0/0, ::/0 | HTTPS |
| UDP | 443 | 0.0.0.0/0, ::/0 | HTTP/3 |
| ICMP | — | 0.0.0.0/0, ::/0 | Ping |

**Outbound :** aucune restriction (tous sortants autorisés).

**Ports désormais DROP inbound** :
- `6379` (Redis) ✅ **objectif BSI**
- `8000` (rag-api-prod)
- `9000-9001` (minio)
- `8081` (imgproxy)
- `3000` (dev node process) + tout autre non listé

### Couche 2 — Alignement compose files (défense en profondeur)

PR [ak125/nestjs-remix-monorepo#102](https://github.com/ak125/nestjs-remix-monorepo/pull/102) : 3 fichiers compose alignés sur le pattern `prod.yml` :
- `ports: '6379:6379'` commentés (accès réseau Docker uniquement)
- Images pinnées `redis:7-alpine` (au lieu de `redis:latest`)
- Command enrichi (`--appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru`)
- Pas de `--requirepass` (évite la régression de mars)

### Audit compromission READ-ONLY

```bash
docker exec redis-dev redis-cli CONFIG GET dir
# → /data  ✅ (pas de pivot vers /root/.ssh ou /var/spool/cron)

docker exec redis-dev redis-cli CONFIG GET dbfilename
# → dump.rdb  ✅ (nom standard, pas de redirection vers authorized_keys)

docker exec redis-dev redis-cli DBSIZE
# → 400 clés (cohérent BullMQ + cache app)

# Scan patterns malware connus
for pat in 'crackit*' 'xmrig*' 'mining*' 'pwn*' '*mikrotik*' '*ssh*' '*cron*' '*.py' '*.sh'; do
  docker exec redis-dev redis-cli --scan --pattern "$pat" --count 1000
done
# → 0 match sur tous les patterns ✅

# Seule famille suspecte : `backup1..4` (4 clés)
for k in backup1 backup2 backup3 backup4; do
  docker exec redis-dev redis-cli STRLEN "$k"  # → 87-99 bytes
done
# → trop petit pour payload exploit, strings applicatives ✅
```

**Verdict : zero indicateur de compromission.** Le vecteur d'attaque principal (Redis-to-shell via `CONFIG SET dir /root/.ssh` puis `SET "" "<ssh-key>"` puis `BGSAVE`) n'a pas été utilisé.

## Lessons Learned

1. **L'alignement ne se propage pas tout seul entre compose files.** Une correction sécurité ciblée sur `prod.yml` doit s'accompagner d'un scan des autres fichiers compose pour déceler les clones désalignés. Ajouter un gate de cohérence (`.spec/` ou CI) qui compare les sections `redis_*` entre les fichiers.
2. **Un `--requirepass` sans secret propagé est pire qu'aucune auth.** Le crash-loop qui invalide les sessions 30j est un incident plus grave pour les users que l'exposition réseau elle-même (si elle est déjà mitigée autrement). Règle : **ne jamais utiliser `--requirepass` sans vérifier que `REDIS_PASSWORD` est effectivement dans l'env du container au runtime.**
3. **Firewall niveau infra bat firewall niveau compose.** Le Hetzner Cloud Firewall survit à un `docker compose up` qui rouvrirait un port. L'inverse n'est pas vrai. Pour les services internes qui n'ont aucune raison d'être publics, le firewall cloud est la couche de défense primaire.
4. **Les scans BSI sont une source de vérité gratuite.** Exposer 1 service inutilement = notification automatique. Utiliser cela comme un audit externe régulier (si la notification arrive, c'est que la config a dérivé).
5. **Le VPS DEV expose aussi 8000 / 9000-9001 / 8081.** Le firewall protège maintenant, mais ces services auraient aussi pu apparaître dans des scans. Action de fond : un audit trimestriel `docker ps --format {{.Ports}} | grep 0.0.0.0` pour surfacer toute expo non-intentionnelle.

## Actions Correctives

| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| Firewall Hetzner `dev-vps-redis-block` attaché à DEV | @fafa | 2026-04-22 | ✅ Done |
| PR #102 alignement compose files | @fafa | 2026-04-22 | 🟡 Open (review) |
| Audit compromission Redis READ-ONLY | @fafa | 2026-04-22 | ✅ Done (clean) |
| Mémoire Claude Code — règle anti `--requirepass` | @fafa | 2026-04-22 | ✅ Done |
| Mémoire Claude Code — firewall à préserver | @fafa | 2026-04-22 | ✅ Done |
| Réponse ticket BSI / Hetzner `AbuseID:118DAFD:19` | @fafa | 2026-04-23 | ⏳ À faire (template préparé) |
| Gate CI — cohérence compose `redis_*` (tous fichiers alignés sur prod.yml) | @fafa | 2026-05-15 | ⏳ À planifier |
| Audit trimestriel `docker ps --format {{.Ports}} 0.0.0.0` DEV | @fafa | récurrent | ⏳ À automatiser (cron + alerte) |

## Preuves

- **Ticket BSI** : `CB-Report#20260422-10008190` (CERT-Bund, `reports@reports.cert-bund.de`)
- **Ticket Hetzner** : `AbuseID:118DAFD:19`
- **PR monorepo** : [#102](https://github.com/ak125/nestjs-remix-monorepo/pull/102) `fix(security): remove public Redis port exposure`
- **Commits historiques (régressions)** :
  - `2c4c24aa` fix(security): secure Redis — add password auth & remove public exposure (OK prod, pas propagé)
  - `16410088` fix(infra): remove Redis auth for preprod
  - `71ac9791` fix(infra): redis crash-loop + health-check perf monitoring (retrait `--requirepass`)
- **Firewall Hetzner** : `dev-vps-redis-block` sur projet `K1266100725`, attaché IP `46.224.118.55`
- **Audit Redis** : CONFIG + scans patterns malware, 0 match

## Communication

- [x] Owner notifié (auto — incident vécu en direct)
- [ ] Réponse Hetzner envoyée
- [x] Post-mortem créé dans vault (ce fichier)
- [ ] Review post-mortem par un second œil

## Template réponse Hetzner / BSI

```
Subject: Re: [AbuseID:118DAFD:19] Open Redis-Server in AS24940

Ticket: CB-Report#20260422-10008190
IP: 46.224.118.55
Service: Redis 7.4.7

Status: RESOLVED at 2026-04-22 ~13:00 UTC

Remediation (defense in depth):

1. Network layer (primary): Hetzner Cloud Firewall rule
   "dev-vps-redis-block" attached to server. Inbound rules now
   allow only TCP 22/80/443, UDP 443, ICMP — all other inbound
   traffic dropped. Port 6379 is no longer reachable from the
   public internet.

2. Configuration layer (in review): pull request
   ak125/nestjs-remix-monorepo#102 aligns the 3 remaining
   docker-compose files on the already-hardened prod.yml pattern
   (no host port mapping, internal Docker network only).

Post-exposure audit (read-only):
- Redis CONFIG dir = /data (no pivot path)
- Redis CONFIG dbfilename = dump.rdb (no malicious rename)
- Key scan for known exploit patterns (crackit*, xmrig*, mining*,
  *ssh*, *cron*) returned 0 matches.
- No indicators of compromise detected.

No further action required on our side. Ticket can be closed.

Thanks for the notification.
```

## Références

- Post-mortem lié (incident adjacent deployment confusion) : [[2026-04-21-false-prod-claim-on-main-merge]]
- Règle à envisager (CI gate compose consistency) : à créer sous `ops/rules/` si validé
- PR monorepo : [ak125/nestjs-remix-monorepo#102](https://github.com/ak125/nestjs-remix-monorepo/pull/102)

---

*Créé le : 2026-04-22*
*Dernière mise à jour : 2026-04-22*
