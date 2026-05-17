# Canon Dispatch Setup — GitHub App credentials

**Statut**: Required secrets (CANON_APP_ID + CANON_APP_PRIVATE_KEY)
**Workflow**: `.github/workflows/canon-publish.yml` (job `dispatch`)
**Dernière mise à jour**: 2026-05-17

---

## Pourquoi une GitHub App

Le workflow `canon-publish.yml` publie un `repository_dispatch` (`event_type=canon-updated`) vers chaque consumer repo après ratification d'un canon sur `main`. Chaque consumer écoute cet event et déclenche son check de drift / sa resync auto.

Le `GITHUB_TOKEN` par défaut ne peut pas appeler `repos/<owner>/<repo>/dispatches` sur un repo tiers — il faut une **authentification cross-repo**.

L'approche initiale (PR #287) utilisait un PAT (`CANON_DISPATCH_TOKEN`). Le PR de migration la remplace par une **GitHub App** dédiée pour les raisons suivantes :

| Critère | PAT classique | **GitHub App** |
|---|---|---|
| Token lifetime | Statique (mois → an) | **1h, auto-rotated** |
| Scope | Souvent over-broad (`repo`) | Permission unique : `Repository dispatches: write` |
| Identité audit | "user X did Y" | "App AutoMecanik Canon Dispatch did Y" |
| Survie changement équipe | Cassé si user part | Indépendant de toute identité humaine |
| Rotation | Manuelle, calendaire | Aucune (sauf rotation de la private key, rare) |
| Si compromis | Tous scopes accessibles jusqu'à révocation manuelle | Blast radius ≤ 1h + scope minimal |

Pattern industry-standard utilisé par Renovate, Dependabot, Probot.

## Setup

### Étape 1 — Créer la GitHub App

1. Aller sur https://github.com/settings/apps/new
2. Champs :
   - **GitHub App name** : `AutoMecanik Canon Dispatch`
   - **Homepage URL** : `https://github.com/ak125/governance-vault`
   - **Webhook** → **Active : décocher** (l'App n'écoute pas d'event, elle agit en sortie)
3. **Repository permissions** :
   - **`Metadata`** : Read-only (auto-coché)
   - **`Contents`** : **Read and write** ← le scope requis pour POST `/repos/{owner}/{repo}/dispatches`
   - (tous les autres : No access)
4. **Where can this GitHub App be installed?** → **Only on this account**
5. Bouton **Create GitHub App**.

> **Note sur la permission `Contents`** : contre-intuitif mais documenté côté GitHub —
> POST `/repos/.../dispatches` exige la permission `Contents: write` pour les GitHub Apps,
> *pas* `Repository dispatches: write` (qui n'existe que dans le vocabulaire fine-grained
> PAT UI, jamais exposé dans le manifest GitHub App). Ref :
> https://docs.github.com/rest/repos/repos#create-a-repository-dispatch-event.
> Trade-off accepté : l'App pourrait théoriquement écrire dans le contenu des consumer
> repos, mais le seul appel API utilisé par `canon-publish.yml` est dispatch (no write
> path). Audit log + scope par-repo (`repositories:` input dans le workflow) limitent
> le risque pratique.

GitHub affiche alors :
- **App ID** (entier court, ex. `123456`) — public, peut être en clair
- Bouton **Generate a private key** → télécharge un `.pem` (à protéger comme un mot de passe)

### Étape 2 — Installer l'App sur les consumer repos

1. Sur la page de l'App, onglet **Install App**.
2. Cliquer **Install** sur l'org/user `ak125`.
3. Choisir **Only select repositories** et cocher exactement les 3 consumers :
   - `nestjs-remix-monorepo`
   - `automecanik-wiki`
   - `automecanik-raw`
4. Confirmer.

L'App apparaît ensuite dans les Settings → Integrations → GitHub Apps de chaque repo coché.

### Étape 3 — Stocker les credentials côté vault

```bash
# App ID
gh secret set CANON_APP_ID -R ak125/governance-vault -b "123456"

# Private key — coller le contenu du .pem téléchargé
gh secret set CANON_APP_PRIVATE_KEY -R ak125/governance-vault < ~/Downloads/autobecanik-canon-dispatch.YYYY-MM-DD.private-key.pem
```

Vérification :

```bash
gh secret list -R ak125/governance-vault | grep -E "CANON_APP"
# attendu :
#   CANON_APP_ID           YYYY-MM-DD...
#   CANON_APP_PRIVATE_KEY  YYYY-MM-DD...
```

### Étape 4 — Retirer l'ancien PAT (recommandé une fois App opérationnelle)

```bash
gh secret delete CANON_DISPATCH_TOKEN -R ak125/governance-vault
```

## Vérification post-setup

Au prochain merge canon (AEC ou marketing-voice ou touch `99-meta/canon-hashes.json`) sur `main` :

1. `canon-publish.yml` doit déclencher 3 dispatch jobs (1 par consumer).
2. Chaque job doit logger :
   - `Validate App credentials are configured` → success
   - `Generate scoped App token (1h, repo-scoped to <repo>)` → outputs un token court-lived
   - `Repository dispatch <repo>` → HTTP 204 sans erreur
3. Côté chaque consumer : un run `repository_dispatch[canon-updated]` doit apparaître :

```bash
gh run list --repo ak125/nestjs-remix-monorepo --event repository_dispatch --limit 1
gh run list --repo ak125/automecanik-wiki --event repository_dispatch --limit 1
gh run list --repo ak125/automecanik-raw --event repository_dispatch --limit 1
```

Si l'un des 3 manque → diagnostic via logs du job échoué (App pas installée sur ce repo ? private key invalide ? App ID typo ?).

## Rotation de la private key

La private key d'une GitHub App n'a pas d'expiration par défaut. À rotater uniquement sur compromission soupçonnée ou politique interne.

Procédure :
1. Page de l'App → **Private keys** → **Generate a new private key** → download `.pem`
2. `gh secret set CANON_APP_PRIVATE_KEY -R ak125/governance-vault < new-key.pem`
3. Re-test : déclencher manuellement le workflow (push commit no-op sur path watched ou `workflow_dispatch`)
4. Sur la page App, **Revoke** l'ancienne private key

Aucun temps mort : GitHub accepte les deux clés tant que l'ancienne n'est pas révoquée.

## Référence

- `.github/workflows/canon-publish.yml` — workflow qui consomme ces secrets
- `99-meta/canon-hashes.json` — registre des canons distribués
- `actions/create-github-app-token@v1` — https://github.com/actions/create-github-app-token (action officielle maintenue par GitHub Actions team)
- ADR-015 — vault single source of truth
- ADR-036 — marketing operating layer (canon brand voice consumer)
- ADR-038 — ratification marketing voice v1.0.1
- Incident 2026-05-17 — drift marketing-voice + root cause `CANON_DISPATCH_TOKEN` jamais configuré (graceful-skip silencieux). Fix : PR monorepo #580, PR vault #286 (paths + matrix + consumers guard), PR vault #287 (fail-loud + doc PAT). Migration vers App : PR courante (sécurité + scope minimal).
