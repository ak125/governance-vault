---
id: ADR-030
title: "npm ci --ignore-scripts permanent dans Dockerfile (Alpine musl + @ast-grep/cli)"
status: accepted
date: 2026-04-30
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G3-signed-commits, rules-engineering-quality]
related_incidents: [PR-monorepo-168-2026-04-25]
reviewed_by: ""
---

# ADR-030: `npm ci --ignore-scripts` permanent dans Dockerfile

## Contexte

Le 2026-04-25, 4 déploiements préprod consécutifs ont échoué en boucle sur le step `npm ci` du `Dockerfile`. Cause racine identifiée : le script `postinstall` de `@ast-grep/cli` télécharge un binaire natif lié à musl libc, mais l'image base `node:22-alpine` ne fournit pas certains symboles attendus par le binaire prebuilt. Erreur : `Error loading shared library`.

Mitigation immédiate (PR monorepo #168, mergée 2026-04-25) : ajout de `--ignore-scripts` au step `npm ci` du Dockerfile (ligne 26). Cette ADR formalise la décision et documente les alternatives rejetées.

État au 2026-04-30 :
- Tous les déploiements préprod et production passent depuis #168
- `@ast-grep/cli` est utilisé uniquement par `eslint-plugin-ast-grep` (devDep), pas en runtime — aucun impact fonctionnel
- Aucun autre package du repo n'a un `postinstall` indispensable au runtime (vérifié via grep `package.json` racine + 12 sub-packages)

## Décision

**Conserver `--ignore-scripts` permanent** dans le step `npm ci` du Dockerfile, jusqu'à ce qu'au moins une de ces conditions soit remplie :
- `@ast-grep/cli` retire son `postinstall` natif (ou publie un wheel compatible Alpine musl)
- Le repo migre vers `node:22-bookworm-slim` (passe à debian, ~+150 MB image)
- Une dépendance runtime nécessite réellement un postinstall (à ce moment-là, scope-limit `--ignore-scripts` à un sous-ensemble)

Un check CI doit flagger toute nouvelle dépendance qui ajoute un script `postinstall` afin d'éviter les régressions silencieuses.

## Options Considérées

### Option A: Migration `node:22-bookworm-slim`

**Description**: Quitter Alpine pour debian slim, qui supporte les binaires prebuilt courants.

**Avantages**:
- Aucune restriction sur les postinstall
- Compatible avec la majorité des packages npm

**Inconvénients**:
- +150 MB sur l'image runtime (passe de ~180 MB à ~330 MB)
- Pull time CI/CD augmenté ~+30s
- Surface d'attaque OS plus large (debian = plus de paquets system par défaut)
- Nécessite re-tester la chaîne build/runtime (hors scope timing)

### Option B: `npm rebuild` sélectif post-install

**Description**: Garder `--ignore-scripts` mais ajouter `npm rebuild <pkg1> <pkg2>` pour les packages qui en ont vraiment besoin.

**Avantages**:
- Granularité fine
- Image reste Alpine

**Inconvénients**:
- Liste à maintenir manuellement (drift garanti)
- Aucun package runtime ne nécessite réellement un postinstall (vérifié)
- Complexité Dockerfile sans bénéfice immédiat

### Option C: Switch yarn/pnpm

**Description**: Remplacer npm par yarn (Berry) ou pnpm pour bénéficier de leurs mécanismes de plug-and-play / strict dep resolution.

**Avantages**:
- pnpm a un mode `--ignore-scripts` granular par package
- Performance install meilleure

**Inconvénients**:
- Refactor lourd (lockfile, CI, scripts package.json, monorepo turbo)
- Risque de régressions dans les workspaces turbo
- Aucun gain immédiat sur le problème spécifique (yarn et pnpm ont aussi des soucis postinstall avec @ast-grep/cli)

### Option D (retenue): `--ignore-scripts` permanent + check CI

**Description**: Garder l'état actuel, ajouter un guard CI qui détecte les nouvelles dépendances avec `postinstall` natif.

**Avantages**:
- Zéro changement runtime
- Coût implémentation minimal
- Image Alpine conservée
- Pas de drift à maintenir

**Inconvénients**:
- Si une dep runtime future requiert un postinstall, il faudra revisiter
- Le check CI doit être maintenu

## Justification

Option D est retenue parce que :

1. **Pragmatisme** : la solution actuelle marche depuis 5 jours sans regression. Aucune dep runtime ne requiert de postinstall — investiguer plus loin n'apporte rien.
2. **Coût minimal** : le check CI prévient la classe de bugs sans bloquer le développement.
3. **Reversibilité** : si une dep runtime future requiert un postinstall, on peut basculer vers Option A (debian) en 1 PR.
4. **Cohérence Alpine** : aligne avec le choix Alpine déjà fait pour la taille d'image (cf. ADR antérieurs sur Docker hardening).

## Conséquences

### Positives

- Déploiements préprod/prod stables (4 incidents évités/semaine d'après le pattern de PR #168)
- Image Docker reste compacte (~180 MB)
- Pas de refactor build chain

### Négatives

- Toute nouvelle dep ajoutée doit être checkée pour les postinstall natifs (responsabilité du reviewer + CI guard)
- En cas de besoin runtime postinstall, debt à payer (basculer Option A)

### Neutres

- L'utilisation de `@ast-grep/cli` reste possible en local (les contributeurs ne sont pas en Alpine)
- La doc Dockerfile (lignes 20–25) explique déjà la raison historique — à conserver

## Critères de Succès

- [ ] Métrique 1 : 0 build CI/Docker failed pour cause de postinstall sur 30 jours suivant l'ADR
- [ ] Métrique 2 : check CI `dependency-postinstall-check` ajouté et bloquant sur l'introduction de nouvelles deps avec postinstall natif (P1, après ADR)
- [ ] Métrique 3 : tag de release suivant déploie sans rollback lié à postinstall

## Implémentation

### Code en place (rétroactif)

- `Dockerfile:26` — `RUN --mount=type=cache,target=/root/.npm npm ci --ignore-scripts` (PR #168)
- `Dockerfile:20–25` — commentaire explicatif Alpine + @ast-grep/cli

### Action additionnelle prévue (post-ADR)

- `.github/workflows/dep-postinstall-check.yml` (à créer en P1) — fail PR si nouvelle dep introduit `scripts.postinstall` non-trivial
- Logique : `git diff origin/main...HEAD -- '**/package.json' | grep -A2 '"postinstall"'` → si match alors fail avec lien vers cette ADR

## Revue Planifiée

**Date**: 2026-10-30 (6 mois post-acceptation)

**Critères de revue**:
- Si une dep runtime requiert un postinstall (alors basculer Option A)
- Si la part de packages avec postinstall augmente significativement (>30% de l'arbre dep)
- Si Alpine musl gagne le support natif des prebuilt binaries courants

---

*Proposé le: 2026-04-30*
*Accepté le: 2026-04-30 (confirme PR #168 mergée 2026-04-25)*
*Dernière revue: 2026-04-30*
