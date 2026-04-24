---
type: meta
status: canon
updated: 2026-04-24
---

# Deploy Bot — Role et Perimetre

**Statut**: Actif
**Nature**: Bot d'automation CI/CD (pas un agent IA, pas un humain)
**Depuis**: 2026-02

---

## Pourquoi cette page existe

Sur les 108 commits du vault au 2026-04-24, **69 (64 %)** sont signes de `Deploy Bot <deploy@automecanik>`. Un lecteur externe du `git log` peut en deduire a tort que le vault est gere par un solo operator ou un single-point-of-failure humain. Cette page documente explicitement le role du bot pour couper cette ambiguite.

---

## Role

Deploy Bot execute les commits automatiques issus des workflows et scripts d'orchestration :

- **Sync canon** : miroir one-way depuis `.spec/00-canon/` du monorepo vers `ledger/` (G1).
- **Reports periodiques** : retrospectives hebdomadaires, sync-log, last-sync-timestamp, rapports `99-meta/reports/`.
- **Bundles evidence-pack** : packaging automatique depuis les resultats de CI monorepo.
- **Housekeeping** : batch ADR-renumbering, archive moves, footer timestamp updates.

Il **n'ecrit jamais** de contenu normatif (ADR, rules, incidents, policies). Tout changement normatif passe par un commit humain (Fafa, auto pieces equipement) ou par Claude Code / Claude Sandbox avec PR review.

---

## Enforcement

Deploy Bot respecte strictement les regles G1-G4 :

| Regle | Respect |
|-------|---------|
| G1 Canon fait foi | Commits sync-canon uniquement, jamais de modification de canon |
| G2 Zero orphelin | Tout fichier cree est link dans un MOC avant commit |
| G3 Commits signes | Cle SSH ed25519 enregistree dans [[key-registry]], chaque commit signe |
| G4 CI read-only | Ne push jamais depuis l'interieur d'un workflow GitHub Actions (voir [[ci-policy]]) |

---

## Infrastructure

- **VPS** : DEV (46.224.118.55), dans `/opt/automecanik/governance-vault/`.
- **User** : `deploy` (non-root).
- **Cle SSH signing** : `/home/deploy/.ssh/vault_signing_key` (ed25519). Pub key dans [[key-registry]].
- **Declencheurs** : cron jobs (voir [[cron-setup]]), hooks post-receive, scripts `_scripts/sync-*.sh`.

---

## Non-SPOF

Malgre sa part de 64 % des commits, Deploy Bot n'est **pas** un SPOF humain :

- C'est un bot automation. Son "absence" (machine down) interrompt juste les syncs automatiques — le vault reste editable par les humains.
- Sa cle privee est isolee (DEV VPS, user non-root, non exportable). Compromission necessite acces root VPS DEV.
- Les commits normatifs (ADR, rules, incidents) viennent d'humains (Fafa, Claude Code avec PR review). Un lecteur peut filtrer par auteur pour distinguer.

Le vrai SPOF est la cle GPG/SSH de Fafa (humain unique auteur de changements canon). Mitigation : voir [[signing-policy]] section "Rotation & Backup".

---

## Distinguer les auteurs

```bash
# Commits normatifs humains (ADR, rules, incidents)
git log --author='Fafa\|auto pieces' --format='%h %s'

# Commits automation
git log --author='Deploy Bot' --format='%h %s'
```

---

## Voir aussi

- [[signing-policy]] — G3 policy SSH ed25519
- [[key-registry]] — registre des cles signataires
- [[ci-policy]] — G4 CI read-only
- [[cron-setup]] — tasks periodiques declencheurs du bot
- [[MOC-Governance]] — master index

---

_Derniere mise a jour: 2026-04-24_
