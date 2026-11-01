---
type: meta
status: canon
updated: 2026-10-01
---

# Deploy Bot — Role et Perimetre

**Statut**: Actif comme identite git ; le writer planning qui committait sous ce nom est retire (ADR-104)
**Nature**: identite git partagee de la machine DEV (ni un service distinct, ni un agent IA, ni une personne)
**Depuis**: 2026-02

---

## Pourquoi cette page existe

`Deploy Bot` est le `user.name` git de la machine DEV : configuration globale de l'utilisateur `deploy`, reprise par le checkout du monorepo et par celui du vault. Toute session qui committe depuis cette machine (humaine, Claude Code ou script) le fait sous ce nom. Le nom d'auteur dit donc **d'ou** un commit a ete cree, pas **qui** l'a ecrit.

Au 2026-09-30 (`619a690`), `main` compte 419 commits. Par auteur : `auto pieces equipement` 256, `Deploy Bot` 148, `Fafa` 10, `Claude Code` 4, `Claude Sandbox` 1.

---

## Ce que recouvrent les 148 commits `Deploy Bot`

| Origine | Commits | Periode | Reconnaissable a |
|---------|---------|---------|------------------|
| Writer planning (cron `/etc/cron.d/planning-live`, ADR-053) | 63 | 2026-05-08 → 2026-08-14 | sujet `chore(planning): …` |
| Tail des bundles Airlock | 11 | 2026-02 | sujet `tail(bundle): …` |
| Sessions de travail sur la machine DEV (ADR, regles, docs, scripts) | 74 | 2026-02-02 → 2026-07-04 | tout le reste |

Des commits normatifs (ADR, regles) existent donc sous ce nom : ils viennent des sessions de travail, pas d'un automate.

Le writer planning poussait directement sur `main` ; il n'y a plus rien publie depuis le 2026-08-14 (diagnostic dans [[governance-runtime-map]], Couche D) ; il est retire par [[ADR-104-planning-live-writer-retired|ADR-104]]. `sync-canon.sh` n'a plus tourne depuis le 2026-02-02 ([[sync-log]]) ; il est retire par [[ADR-101-vault-decides-canon-authority|ADR-101]].

Les commits fusionnes par GitHub (committer `GitHub`, du 2026-04-04 au 2026-09-30) ont tous `auto pieces equipement` pour auteur, meme quand la branche a ete ecrite sous `Deploy Bot`. Apres le 2026-07-04, les seuls commits `Deploy Bot` de `main` sont ceux du writer planning.

---

## Regles applicables

| Regle | Etat reel |
|-------|-----------|
| G1 Le vault decide | Reecrite par ADR-101 ([[rules-vault]]). Aucune synchronisation monorepo → vault ; dernier sync consigne : 2026-02-02 ([[sync-log]]) |
| G2 Zero orphelin | Check requis en PR. Les pushes directs du writer planning (jusqu'au 2026-08-14) n'etaient verifies qu'apres coup, par le run de CI sur `main` |
| G3 Commits signes | Signature K001 (`/home/deploy/.ssh/vault_signing_key`) via `commit.gpgsign true`, voir [[key-registry]] |
| G4 ecriture par PR, CI en lecture seule | Aucun commit de `main` n'a pour auteur un bot GitHub Actions ; `_scripts/check-ci-read-only.py` verifie a chaque PR qu'aucun workflow ne peut ecrire dans le vault (voir [[ci-policy]]) |

---

## Infrastructure

- **Machine** : DEV, checkout `/opt/automecanik/governance-vault/`.
- **User** : `deploy` (non-root).
- **Cle SSH signing** : `/home/deploy/.ssh/vault_signing_key` (ed25519, K001). Pub key dans [[key-registry]].
- **Declencheurs automatiques** : aucun cron ne committe dans le vault depuis le retrait du writer planning ([[ADR-104-planning-live-writer-retired|ADR-104]], voir [[cron-setup]]) ; son fichier cron reste installé jusqu'à sa suppression par l'owner mais s'arrête avant toute operation git. Aucun hook post-receive n'existe.

---

## Non-SPOF

- L'absence de la machine DEV arrete `vault-sync.sh`. Le vault reste modifiable par PR depuis tout clone disposant d'une cle de signature (K002, voir [[key-registry]]).
- La cle K001 est sur la machine DEV, sous un user non-root. Sa compromission permettrait de signer sous K001. G3 accepte aussi une signature par une cle absente d'`allowed_signers` (statut `U`, voir [[signing-policy]]).
- Rotation ou compromission de cle : voir [[signing-policy]] section « Rotation de Cle ».

---

## Distinguer les auteurs

Le nom d'auteur ne distingue ni humain et agent, ni travail manuel et automate. Filtrer plutot par sujet ou par committer :

```bash
# Automatismes (writer planning, tail Airlock)
git log --format='%h %ad %s' --date=short | grep -E ' (chore\(planning\)|tail\(bundle\)):'

# Commits de main fusionnes par PR (committer GitHub)
git log --committer='GitHub' --format='%h %an %s'
```

---

## Voir aussi

- [[signing-policy]] — G3 policy SSH ed25519
- [[key-registry]] — registre des cles signataires
- [[ci-policy]] — G4, CI en lecture seule
- [[cron-setup]] — crons
- [[governance-runtime-map]] — historique du writer planning
- [[MOC-Governance]] — master index

---

_Derniere mise a jour: 2026-09-30_
