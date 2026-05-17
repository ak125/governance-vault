# Canon Dispatch Setup — `CANON_DISPATCH_TOKEN`

**Statut**: Required secret
**Workflow**: `.github/workflows/canon-publish.yml` (job `dispatch`)
**Dernière mise à jour**: 2026-05-17

---

## Pourquoi ce secret existe

Le workflow `canon-publish.yml` publie une notification `repository_dispatch`
(`event_type=canon-updated`) vers chaque consumer repo listé dans la matrix
`dispatch` quand un canon est ratifié sur `main`. Chaque consumer écoute cet
event et déclenche son propre check de drift (ex. `marketing-voice-hash.yml`,
`agent-exit-contract-hash.yml`).

Le `GITHUB_TOKEN` par défaut ne peut pas appeler `repos/<owner>/<repo>/dispatches`
sur un repo tiers — il faut un PAT (Personal Access Token) dédié, stocké comme
secret `CANON_DISPATCH_TOKEN`.

Sans ce secret, le job `dispatch` **échoue** (fail-loud) : pas de notification,
pas de propagation. Volontairement bloquant : un canon ratifié mais non
distribué = drift garanti côté consumer (cf. incident marketing-voice
v1.0.1 du 2026-05-17, fixé par PR #286 + PR-monorepo #580).

## Scopes requis

PAT avec `repo` scope sur **chaque** consumer listé dans la matrix de
`canon-publish.yml`. Au 2026-05-17 :

| Consumer repo | Pourquoi |
|---|---|
| `ak125/nestjs-remix-monorepo` | 3 mirrors AEC + 2 mirrors marketing-voice |
| `ak125/automecanik-wiki` | 1 mirror AEC dans `_meta/` |
| `ak125/automecanik-raw` | 1 mirror AEC à la racine |

Quand un consumer est ajouté à la matrix, le PAT doit être étendu (ou
remplacé) avec le scope sur le nouveau repo.

## Setup

### Option 1 — Fine-grained PAT (recommandé)

1. https://github.com/settings/personal-access-tokens → "Generate new token"
2. **Resource owner**: `ak125`
3. **Repository access**: "Only select repositories" → cocher chaque consumer
   ci-dessus
4. **Repository permissions** :
   - `Contents` : Read
   - `Metadata` : Read (auto)
   - `Custom properties` : pas nécessaire
   - **`Repository dispatches`** : **Read and write** ← le scope critique
5. Expiration : ≤ 1 an, rotation au calendrier (cf. `99-meta/key-registry.md`).

### Option 2 — Classic PAT

1. https://github.com/settings/tokens → "Generate new token (classic)"
2. Scope **`repo`** (Full control of private repositories)
3. Idem expiration ≤ 1 an

### Installation du secret

```bash
gh secret set CANON_DISPATCH_TOKEN -R ak125/governance-vault
# Coller le PAT à l'invite, puis ENTER
```

Vérification :

```bash
gh secret list -R ak125/governance-vault | grep CANON_DISPATCH_TOKEN
```

## Vérification post-setup

Au prochain merge canon (AEC ou marketing-voice ou touch
`99-meta/canon-hashes.json`) sur `main` :

1. `canon-publish.yml` doit déclencher 3 dispatch jobs (1 par consumer)
2. Chaque job doit logger un appel `gh api repos/<consumer>/dispatches` réussi
   (HTTP 204), **sans** message `CANON_DISPATCH_TOKEN secret not set`
3. Côté chaque consumer : un run `repository_dispatch[canon-updated]` doit
   apparaître dans `gh run list --event repository_dispatch`

Si l'un des 3 n'est pas vérifié → incident token (scope manquant, token
expiré, mauvais owner) — diagnostic via les logs du job échoué.

## Rotation

PAT à rotation manuelle ≤ 1 an. Procédure :

1. Générer un nouveau PAT avec les mêmes scopes
2. `gh secret set CANON_DISPATCH_TOKEN -R ak125/governance-vault` (overwrite)
3. Forcer un re-run `canon-publish.yml` via `workflow_dispatch` pour valider
4. Révoquer l'ancien PAT sur https://github.com/settings/tokens

Inscrire la rotation dans `99-meta/key-registry.md`.

## Référence

- `.github/workflows/canon-publish.yml` — le workflow qui consomme ce secret
- `99-meta/canon-hashes.json` — registre des canons distribués
- ADR-015 — vault single source of truth
- ADR-036 — marketing operating layer (canon brand voice consumer)
- ADR-038 — ratification marketing voice v1.0.1
- Incident 2026-05-17 — drift marketing-voice détecté, root cause = ce
  secret manquant (graceful-skip silencieux). Fix : PR monorepo #580,
  PR vault #286 (paths + matrix + consumers guard), PR vault courante
  (fail-loud + ce doc).
