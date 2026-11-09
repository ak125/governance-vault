---
id: ADR-124
title: "Premier périmètre de fusion automatique (ADR-123) : PR ordinaires du monorepo vers main, hors zones STOP"
status: proposed
date: "2026-11-09"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-123"]
related_adr: ["ADR-099", "ADR-102", "ADR-120", "ADR-121", "ADR-123"]
related_rules: ["DoD2", "G4", "RULE-H5", "RULE-H6", "T6"]
related_incidents: []
version: "1.0.0"
---

# ADR-124 : premier périmètre de fusion automatique

- **Statut** : Proposed. Rédigé par un agent (Claude CLI) le 2026-11-09, sur demande de l'owner.
  La décision de l'owner sera consignée par le commit de ratification
  ([[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D7).
- **Étend** [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]], dont il tranche
  les « Points à décider » pour un premier périmètre. N'amende aucune règle.
- **N'active rien à lui seul** : la politique [merge-perimeter.v1.json](../../policies/merge-perimeter.v1.json)
  porte `status: inactive`. Le passage à `active` suit D8.

## Contexte

L'owner, le 2026-11-09 : le processus de validation, fusion, commit et push est « trop compliqué » et
demande son autorisation à chaque fois ; « supprime autorisation owner car trop lourd et simplifie en
gardant la sécurité » ; « prod n'est pas concerné, uniquement dev ». Après exposé des exclusions
proposées et de l'effet réel d'une fusion sur `main`, il a demandé de préparer cette PR.

Constats en lecture seule du 2026-11-09 :

- ADR-123 est `accepted`, aucun périmètre n'est adopté. Toute fusion passe donc par l'owner.
- Sur le monorepo, `main` exige 14 contrôles, appliqués à tous (`enforcement: everyone`). Le reste de la
  protection est illisible par le compte des agents (403). Trois PR ouvertes sont `CLEAN` sans
  approbation : aucune revue GitHub ne semble requise.
- `merge-pr.sh` contrôle déjà brouillon, contrôles requis et non requis, état `CLEAN`, empreinte du
  contenu et fusion épinglée au SHA. Il ne contrôle ni la catégorie ni l'enregistrement de revue.
- Une fusion sur `main` n'est pas limitée à DEV : elle lance la chaîne PREPROD (`ci.yml`) et son contenu
  part avec le prochain tag `v*`.
- Rejeu de la politique sur les 40 dernières fusions de `main` (chemins, statuts de fichiers et lignes
  du diff seulement ; ni revue, ni assignee, ni contrôles) : 6 admises, 34 refusées. Parmi les refusées,
  16 touchent une exclusion nommée et 18 sortent seulement de la liste autorisée (CI, `.spec/`, `scripts/`,
  configuration de build). Ce périmètre retire donc environ une fusion sur sept à l'owner.

## Décisions

### D1 — Périmètre

Dépôt `ak125/nestjs-remix-monorepo`, branche `main`, PR ordinaires de niveau DoD2 A ou B. Le détail
machine est dans [merge-perimeter.v1.json](../../policies/merge-perimeter.v1.json), seule source. Le
vault, ses PR et toute décision de gouvernance sont hors périmètre.

### D2 — Autorisation par catégorie

L'adoption de cet ADR vaut autorisation préalable (ADR-123 D3) pour les PR qui remplissent toutes les
conditions de D5. Aucune autre autorisation n'est demandée à l'owner pour ces PR.

### D3 — Exclusions

Une PR est hors périmètre, donc fusionnée par l'owner, si un seul fichier ou une seule ligne relève de :

- une zone STOP ou le niveau C de DoD2 : paiement, prix et stock servis, panier et commande, RLS,
  migrations, SEO indexé (meta, H1, canonical, noindex, sitemap, robots), déploiement. La détection
  porte sur les chemins, sur le nom des fichiers dans tout le dépôt et sur les lignes du diff ;
- un changement de contrôle d'accès (`@UseGuards`, `@Public`, `@Roles`, `@SkipThrottle`, clé `service_role`) ;
- l'ajout, la suppression ou le renommage d'une route (aucune modification d'URL) ;
- une garde ou sa configuration : `.github/`, hooks, ast-grep, `scripts/`, baselines, `.spec/`,
  miroirs canon, `CLAUDE.md`, `AGENTS.md`, cette porte de périmètre ;
- l'infrastructure : Docker, Caddy, `.env`, manifestes de dépendances ;
- l'avance de pin du sous-module (ADR-099 D2) ;
- Dependabot et `canon-sync` (ADR-121 C9 et ADR-123 D2 : non décidés ici).

La liste autorisée est fermée : un chemin qu'elle ne nomme pas est refusé. Le niveau C déclaré par la
revue est refusé quel que soit le chemin.

### D4 — Mécanisme, compte et acte qui arme

- **Mécanisme** : `merge-pr.sh`, inchangé, appelé par une porte de périmètre versionnée dans le
  monorepo, qui lit la politique sur `origin/main` du vault et refuse si elle est illisible.
- **Compte qui exécute** : `automecanik-agents[bot]`.
- **Acte qui arme** : le lancement de la porte, pour une PR et une empreinte de contenu, par la session
  Claude CLI titulaire du mandat, après l'enregistrement de revue. La session ne décide pas : la porte
  applique D5, et tout refus laisse la fusion à l'owner.

### D5 — Conditions et refus

Reprend ADR-123 D4 ; une condition manquante ou non concluante empêche la fusion.

| Cas | Effet | Contrôle de la porte |
|---|---|---|
| Politique illisible, ou `status` autre que `active` | pas de fusion | lecture de la politique |
| Fichier de pause présent | pas de fusion | D8 |
| Hors liste autorisée, ou exclusion de D3 | pas de fusion | chemins, statuts de fichiers, lignes du diff |
| PR en brouillon, ou titre marqué « NE PAS FUSIONNER » (lot suspendu) | pas de fusion | état et titre |
| Sans assignee humain | pas de fusion | DoD2 point 1 |
| Enregistrement de revue absent, niveau C, ou tête différente | pas de fusion avant réévaluation | DoD2 points 2 à 4 |
| Tête changée depuis la revue | pas de fusion sauf empreinte identique, reportée par un enregistrement sur la nouvelle tête écrit avant la fusion | `--pin`, DoD2 point 4 |
| Contrôle requis ou non requis absent, en échec ou non concluant | pas de fusion | `merge-pr.sh` |
| Protection du dépôt non satisfaite | pas de fusion ; aucun contournement | GitHub, `--match-head-commit` |
| Effet PROD (tag `v*`, déploiement, mutation) | pas de fusion | exclusions de D3 ; la porte ne crée aucun tag |

Une seule fusion automatique à la fois.

### D6 — Trace

Avant la fusion, la porte commente la PR : commit de la politique, tête, empreinte, niveau, compte. Après
la fusion, elle y consigne le résultat. Aucune trace, identité ni label n'est créé pour cela (ADR-123 D5).

### D7 — Effets couplés

- Chaque fusion lance la chaîne PREPROD, comme aujourd'hui.
- Le contenu fusionné part en PROD avec le prochain tag `v*`, qui reste le geste de l'owner (RULE-H0
  inchangée). L'audit du lot avant tag couvre aussi ces fusions.
- Aucun effet sur les consommateurs : le vault, l'AEC et `canon-sync` sont exclus.

### D8 — Activation, pause et arrêt

- **Activation** (ADR-123 D7) : `status: active`, par un commit signé sur une PR du vault fusionnée par
  l'owner, qui cite la recette des cas de D5, chacun démontré par un refus réel de la porte. Le commit
  peut figurer sur la PR de cet ADR si la recette précède la ratification.
- **Pause immédiate** : un fichier de pause placé à côté de `merge-pr.sh` arrête toute fusion
  automatique, sans PR.
- **Arrêt** : `status: inactive` ou revert. Une fusion déjà faite se corrige par une PR de revert.

### D9 — Entrée en vigueur sans auto-autorisation

Cette PR et la PR de la porte sont hors périmètre : l'owner les fusionne (ADR-123 D8).

## Limites

- La porte vérifie la forme de l'enregistrement de revue. Elle ne prouve pas que la revue de niveau B a
  été faite par une session distincte de l'auteur : cela reste une règle de conduite (DoD2).
- La détection du SEO indexé par motif de diff est partielle. Le rejeu admet ainsi #1939, qui modifie
  un composant rendu sur une page R1 (`EquipementiersSection`), et une PR qui modifie la route publique
  `diagnostic-auto._index.tsx`.
  Le classement au niveau C par la revue reste nécessaire.
- Le filtre par nom refuse aussi des fichiers sans rapport avec une zone STOP (`border`, par exemple).
  Ces PR reviennent à l'owner : la seule perte est une fusion manuelle de plus.
- Les projections générées sont dispensées des filtres de contenu. Leur liste doit rester identique à
  `GEN_RE` de `resync-pr.sh` ; un écart est refusé par la porte.
- La protection complète de `main` du monorepo n'a pas pu être lue.

## Options considérées

- **A — Statu quo** : rejetée par l'owner.
- **B — Tout fusionner sans exclusion** : rejetée ; elle lèverait le niveau C qu'ADR-123 D3 maintient.
- **C — Fusion par l'agent via un hook ou un skill modifié** : rejetée ; contournement sans périmètre.
- **D — Périmètre fermé, porte déterministe, mécanisme existant** : retenue.

## Conséquences

- **Positives** : plus aucun geste de l'owner sur les PR du périmètre, soit environ une fusion sur sept
  au rejeu ; le tag PROD et les zones STOP restent à lui.
- **Négatives** : une porte de plus à maintenir ; une erreur fusionnée atteint PREPROD sans regard
  humain et part au prochain tag si elle n'est pas revertée.

## Métriques

- Fusions automatiques hors périmètre : 0.
- Fusions automatiques sans trace complète (D6) : 0.
- Reverts de fusions automatiques : suivis à la revue.

## Retour arrière

Fichier de pause, puis `status: inactive` ou revert de la PR qui porte cet ADR. Aucune protection, aucun
droit ni aucun workflow n'est modifié par cet ADR.

## Revue planifiée

**Date** : 2027-02-09.

**Critères** : une fusion hors périmètre ; un revert dû à un défaut que la porte devait refuser ; une zone
STOP atteinte.

## Références

- [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]]
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]]
- [[ADR-120-dod2-preuve-de-revue-liee-au-sha|ADR-120]]
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4|ADR-102]]
- [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]]
- [[MOC-Decisions]]

---

*Proposé le : 2026-11-09*
