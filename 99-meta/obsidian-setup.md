---
type: knowledge
status: canon
updated: 2026-04-24
audience: [onboarding, obsidian-user]
related_adr: [ADR-012, ADR-015]
related_rules: [G1, G2, G3]
---

# Obsidian Setup — Coffre canonique governance-vault

> **Contexte** : ce document documente la **topologie canonique** validée le 2026-04-24 après la Phase W de réconciliation (3 coffres parallèles → 1 coffre unique) sur le poste Windows principal. À lire avant toute installation Obsidian sur un nouveau device (nouveau poste, PROD, AI-COS, nouveau collaborateur).

---

## Principe canonique

**Un coffre Obsidian unique par device**, pointant vers un `git clone` standalone du repo `ak125/governance-vault`. Pas de ZIP téléchargé. Pas de coffre dans un sous-dossier parasite. Pas de coffres multiples parallèles.

Le vault n'est **jamais** un sous-dossier d'un autre repo cloné : il a toujours son propre `.git/`, son propre cycle de vie, sa propre branche.

## Topologie canonique

```
<somewhere>/governance-vault/    <- clone git standalone avec son .git/
├── .git/                        <- remote = git@github.com:ak125/governance-vault.git
├── .obsidian/                   <- config Obsidian locale (plugins, workspace, ...)
├── ledger/
├── ops/
├── 99-meta/
├── _scripts/
├── _templates/
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

**Emplacement recommandé** : `<home>/vaults/governance-vault/` ou `<home>/Documents/governance-vault/`. L'emplacement historique `C:\Users\Marwane\nestjs-remix-monorepo\governance-vault\` (dans un parent monorepo) **fonctionne** mais est un artefact — à ne pas reproduire sur un nouveau device.

**Anti-patterns interdits** :

- Télécharger le repo en ZIP depuis GitHub ("Download ZIP"). Produit `governance-vault-main/` figé, sans `.git/`, sans sync possible, et aggrave silencieusement chaque édition faite dedans.
- Cloner dans un dossier sous-jacent d'un autre vault Obsidian (crée deux coffres parallèles dont Obsidian n'arbitrera pas proprement).
- Créer un "New vault" Obsidian par clic UI dans un sous-dossier du clone (pollue l'arbo avec un `GOVERNANCE VAULT/` fantôme qui viole G2).
- Ouvrir plusieurs coffres Obsidian en parallèle pointant des clones différents du même repo (risque d'écritures divergentes).

## Plugins Obsidian canoniques

| Plugin | Auteur | Version min | Rôle |
|---|---|---|---|
| **Dataview** | blacksmithgu | 0.5.68 | Queries dynamiques dans les notes (auto-index MOCs, listes par frontmatter, etc.) |
| **Templater** | SilentVoid13 | 2.x | Templates avancés pour nouveaux documents (ADR, incidents, règles) — utilisés avec `_templates/` du vault |
| **Git** | Vinzent | 2.38+ | Commit / push / pull depuis l'UI Obsidian (ceinture) |

Les 3 sont **communautaires**. Les installer via Settings → Community plugins → Browse.

Ne pas ajouter d'autres plugins au vault canonique sans en discuter (chaque plugin nouveau peut introduire du drift silencieux).

## Config Obsidian Git recommandée

**Settings → Community plugins → Git → Options** :

| Champ | Valeur | Raison |
|---|---|---|
| Commit Author Name | Ton nom réel (ex : `Fafa`) | Cohérence `git log` avec les commits terminal |
| Commit Author Email | Ton email | Idem |
| Commit message | `docs(vault): {{date:YYYY-MM-DD}} Obsidian edit` ou template court | Conforme convention `docs(vault): ...` |
| Auto pull interval | `10 minutes` | Évite drift local ↔ GitHub, charge réseau minime |
| Auto commit | **désactivé** | Commit manuel via UI = contrôle des messages, pas de WIP poussé par accident |
| Auto push | **désactivé** | Push manuel = tu vois ce que tu pousses |
| Show status bar | activé | Voir branche + nb changes en un coup d'œil |
| List changed files in commit message body | désactivé | Redondant avec diff GitHub |
| Disable notifications | désactivé | Garde les messages d'erreur visibles |

## SSH signing (G3 enforcement)

Le vault applique [[rules-vault|G3]] (Commits signés ed25519). Tout push non signé est rejeté par la CI (`vault-governance.yml` job `G3: Commits signes`).

### Setup Windows

Depuis un terminal PowerShell dans le clone vault :

```powershell
cd <somewhere>\governance-vault

# Verifier la config actuelle
git config --local commit.gpgsign
git config --local user.signingkey
git config --local gpg.format

# Si vide, generer ou reutiliser une cle SSH
# (generer : ssh-keygen -t ed25519 -C "vault-signing@<user>" -f $HOME\.ssh\vault_signing_key)
git config --local user.signingkey "$HOME\.ssh\vault_signing_key.pub"
git config --local gpg.format ssh
git config --local commit.gpgsign true
```

La clé publique doit être enregistrée dans [[key-registry]] du vault (PR dédiée si pas déjà fait) et référencée dans `.github/workflows/vault-governance.yml` job `G3` (`allowed_signers`).

### Vérif post-setup

Créer un commit test dans une branche dédiée :

```powershell
git checkout -b test/signing-smoke
echo "test" > 99-meta/test-signing.md
git add 99-meta/test-signing.md
git commit -S -m "test(signing): smoke test G3"
git log -1 --show-signature
```

Le dernier `git log` doit afficher `Good "git" signature for <key>`. Si non : la clé n'est pas reconnue, vérifier `user.signingkey` et allowed_signers.

Rollback du test : `git reset --hard HEAD~1 && git checkout main && git branch -D test/signing-smoke`.

## Procédure d'installation sur nouveau device

1. Installer Obsidian : https://obsidian.md/download
2. Installer Git for Windows (ou l'équivalent OS) + vérifier accès SSH à `git@github.com:ak125/...`
3. Cloner :
   ```bash
   git clone git@github.com:ak125/governance-vault.git <somewhere>/governance-vault
   cd <somewhere>/governance-vault
   ```
4. Ouvrir Obsidian → "Open folder as vault" → sélectionner `<somewhere>/governance-vault`.
5. Obsidian propose d'activer les plugins communautaires — accepter.
6. Installer les 3 plugins canoniques (Dataview, Templater, Git) depuis Settings → Community plugins → Browse.
7. Config Obsidian Git selon le tableau ci-dessus.
8. Setup SSH signing (section précédente).
9. Test smoke signing (section précédente).
10. C'est opérationnel.

## Ce qui est versionné dans `.obsidian/` (itération future)

Actuellement `.obsidian/` n'est **pas versionné** dans le vault (aucun fichier sous ce chemin dans le repo au 2026-04-24). Chaque device a sa config locale.

Une itération future (ADR dédiée, probablement numérotée ADR-028 ou suivante après les ADR-023/024/025/026/027 planifiés) pourra versionner un sous-ensemble canonique de `.obsidian/` (liste des plugins, hotkeys, snippets) pour cohérence cross-device. Voir backlog Phase W6+ du plan.

## Backup

- **Automatique** : Obsidian Git auto-pull toutes les 10 min + commits manuels = historique git complet sur GitHub = backup distribué.
- **Snapshots locaux** : le plugin Obsidian Git crée des snapshots sous `_backups/` à chaque conflit résolu. Ne **pas** committer ces snapshots (à terme, `.gitignore` du vault les exclura — voir futur Paquet 6 Cleanup).
- **Backup one-shot avant migration majeure** : `Compress-Archive` du dossier vault entier horodaté sur le Bureau (protocole W0 appliqué le 2026-04-24 lors de la Phase W).

## Référence croisée

- [[CLAUDE]] — instructions agents Claude Code / Cowork / Codex
- [[AGENTS]] — guardrails agents + workflow nouveau-document
- [[claude-desktop-instructions]] — condensé pour Claude Desktop (MCP filesystem)
- [[signing-policy]] — policy G3 détaillée
- [[key-registry]] — registre des clés SSH autorisées
- [[ADR-015-vault-single-source-of-truth]] — SoT décision fondatrice
- [[ADR-012-aicos-vps-architecture]] — 3-VPS architecture

## Contact

- Owner : Fafa (`automecanik.seo@gmail.com`)
- Repo : https://github.com/ak125/governance-vault

---

*Document canonisé après la Phase W (2026-04-24) qui a réconcilié une topologie à 3 coffres parallèles vers un coffre unique.*
