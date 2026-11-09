---
id: ADR-124
title: "Premier périmètre de fusion automatique (ADR-123) : documentation et projections du monorepo vers main"
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
  protection est illisible par le compte des agents (403). Deux PR ouvertes (#1954, #1967) sont
  `CLEAN` sans approbation : aucune revue GitHub ne semble requise.
- `merge-pr.sh` resynchronise toujours la branche avant de fusionner : la tête change après la revue. Il
  ne peut donc pas servir à fusionner la tête revue, et il ne contrôle ni la catégorie ni l'enregistrement
  de revue.
- Une fusion sur `main` n'est pas limitée à DEV : elle lance la chaîne PREPROD (`ci.yml`) et son contenu
  part avec le prochain tag `v*`.
- L'enregistrement de revue DoD2 est du texte dans le corps de la PR. Aucune identité distincte ne peut
  l'attester : les PR des agents viennent du compte `automecanik-agents`, qui ne peut pas approuver ses
  propres PR. Une revue indépendante de niveau B n'est donc pas vérifiable par une machine.
- La classification `ownership.yaml` situe bien les zones STOP du backend, mais `risk` y vaut `low` par
  défaut et `frontend/app/routes/**` ou `frontend/app/components/**` mêlent panier, commande, SEO et
  composants ordinaires. Elle sert donc à refuser, avec une liste fermée de domaines.
- Rejeu du code réel de la porte sur les 40 dernières fusions de `main` (fichiers, diff et niveau de revue ;
  ni assignee, ni contrôles ; classification de `main` au 2026-11-09, pas celle de chaque fusion) :
  **4 admises sur 40, toutes de documentation**. Causes cumulables des refus : niveau de revue insuffisant 33,
  chemin refusé 25, domaine refusé 16, non classé 9, motif de diff 4. Ce périmètre retire donc environ une
  fusion sur dix à l'owner.

## Décisions

### D1 — Périmètre

Dépôt `ak125/nestjs-remix-monorepo`, branche `main`, PR de niveau DoD2 A : documentation Markdown et
projections générées. Le détail machine est dans [merge-perimeter.v1.json](../../policies/merge-perimeter.v1.json),
seule source. Le vault, ses PR et toute décision de gouvernance sont hors périmètre.

Le niveau B n'est pas ouvert : la porte ne saurait pas prouver la revue indépendante qu'il exige, et il
n'admet aucune fusion de plus au rejeu. L'ouvrir suppose une revue attestée par une identité distincte de
l'auteur, puis une modification de la politique par PR du vault.

### D2 — Autorisation par catégorie

L'adoption de cet ADR vaut autorisation préalable (ADR-123 D3) pour les PR qui remplissent toutes les
conditions de D5. Aucune autre autorisation n'est demandée à l'owner pour ces PR.

### D3 — Exclusions

Une PR est hors périmètre, donc fusionnée par l'owner, si un seul fichier ou une seule ligne relève de :

- un fichier autre que Markdown ou projection générée, ou une revue déclarée de niveau B ou C ;
- un domaine absent de la liste fermée, d'après `ownership.yaml` lu à la base de la PR, résolu par le glob
  le plus long : sont ainsi refusés catalogue et prix (D1), SEO (D3), véhicule (D4), blog (D5), routes et
  panier frontend (D8), import fournisseurs (D9), commande et paiement (D11), configuration (D13), gammes
  (D14) et gouvernance (D15). Un chemin sans entrée, sans propriétaire, à risque élevé ou à confiance
  faible est refusé ;
- un chemin de `deny_paths` : `.github/`, hooks, ast-grep, `scripts/`, `.spec/`, `.claude/`, migrations,
  `CLAUDE.md`, `AGENTS.md`, `.env`, Docker, Caddy, manifestes de dépendances ;
- une ligne ajoutée ou retirée portant un motif de `deny_diff_patterns` : meta, H1, canonical, noindex,
  prix, paiement, contrôle d'accès, clé `service_role` ;
- Dependabot et `canon-sync` (ADR-121 C9 et ADR-123 D2 : non décidés ici).

La détection repose sur la classification existante, sans filtre sur le nom des fichiers. Un renommage est
évalué sur ses deux chemins.

### D4 — Mécanisme, compte et acte qui arme

- **Mécanisme** : `scripts/ci/merge-perimeter-gate.mjs`, versionné dans le monorepo. Il lit la politique
  au commit courant de `main` du vault et la classification à la base de la PR : une PR ne peut ni
  s'autoriser ni se reclasser. Il fusionne par `gh pr merge --squash --match-head-commit` sur la tête de
  l'enregistrement de revue. `merge-pr.sh` n'est pas appelé, puisqu'il déplacerait cette tête.
- **Compte qui exécute** : `automecanik-agents[bot]`.
- **Acte qui arme** : le lancement de la porte pour une PR par la session Claude CLI titulaire du mandat,
  après l'enregistrement de revue. La session ne décide pas : la porte applique D5, et tout refus laisse la
  fusion à l'owner.

### D5 — Conditions et refus

Reprend ADR-123 D4 ; une condition manquante ou non concluante empêche la fusion.

| Cas | Effet | Contrôle de la porte |
|---|---|---|
| Politique illisible, ou `status` autre que `active` | pas de fusion | lecture de la politique |
| Fichier de pause présent | pas de fusion | D8 |
| Exclusion de D3 | pas de fusion | fichiers, classification, lignes du diff |
| PR en brouillon, ou titre marqué « NE PAS FUSIONNER » (lot suspendu) | pas de fusion | état et titre |
| Sans assignee humain | pas de fusion | DoD2 point 1 |
| Enregistrement de revue absent, niveau autre que A, autre tête ou autre base | pas de fusion avant réévaluation | DoD2 points 2 à 4 |
| Tête en retard sur `main` ou changée depuis la revue | pas de fusion ; resynchronisation, puis nouvel enregistrement sur la nouvelle tête | état de fusion, retard mesuré, DoD2 point 4 |
| Contrôle requis ou non requis absent, en échec ou non concluant | pas de fusion | contrôles de la tête lus par la porte |
| Protection du dépôt non satisfaite | pas de fusion ; aucun contournement | GitHub, `--match-head-commit` |
| Effet PROD (tag `v*`, déploiement, mutation) | pas de fusion | exclusions de D3 ; la porte ne crée aucun tag |

Une seule fusion automatique à la fois.

### D6 — Trace

Avant la fusion, la porte commente la PR : commit de la politique, tête, niveau, compte. Après
la fusion, elle y consigne le résultat. Aucune trace, identité ni label n'est créé pour cela (ADR-123 D5).

### D7 — Effets couplés

- Chaque fusion lance la chaîne PREPROD, comme aujourd'hui.
- Le contenu fusionné part en PROD avec le prochain tag `v*`, qui reste le geste de l'owner (RULE-H0
  inchangée). L'audit du lot avant tag couvre aussi ces fusions.
- Les fusions automatiques ne portent ni sur le vault, ni sur l'AEC, ni sur `canon-sync`.

### D8 — Activation, pause et arrêt

- **Activation** (ADR-123 D7) : `status: active`, par un commit signé sur une PR du vault fusionnée par
  l'owner, qui cite la recette des cas de D5, chacun démontré par un refus réel de la porte. Le commit
  peut figurer sur la PR de cet ADR si la recette précède la ratification.
- **Pause immédiate** : le fichier `merge-perimeter.pause`, placé à côté de `merge-pr.sh`, arrête toute
  fusion automatique, sans PR.
- **Arrêt** : `status: inactive` ou revert. Une fusion déjà faite se corrige par une PR de revert.

### D9 — Entrée en vigueur sans auto-autorisation

Cet ADR suit le circuit en vigueur, comme ADR-123 D8 : commit de ratification, puis fusion par l'owner de
la tête épinglée (ADR-121 D4 et D7). La PR qui crée la porte touche `scripts/`, donc reste hors périmètre :
l'owner la fusionne. Une fois fusionné, cet ADR n'autorise rien tant que D8 n'a pas activé la politique.

## Limites

- La porte vérifie la forme de l'enregistrement de revue, pas qu'une revue a eu lieu. Au niveau A, DoD2
  admet l'auto-revue, et la porte contrôle elle-même que le contenu relève bien de ce niveau.
- Le champ `risk` vaut `low` par défaut : il ne prouve rien seul. Le frontend reste hors périmètre tant
  que `ownership.yaml` ne le découpe pas ; cette évolution appartient à l'owner.
- Un motif de diff est un filet partiel, pas une détection complète du SEO.
- Les projections générées sont dispensées de classification et de motifs de diff. Leur liste copie
  `GEN_RE` de `resync-pr.sh` sans contrôle automatique ; leur fraîcheur reste vérifiée par la CI.
- La protection complète de `main` n'est pas lisible par le compte des agents, l'option `strict` comprise.
  La porte mesure donc le retard de la tête à l'évaluation. Entre l'évaluation et la fusion, seule la
  protection de GitHub s'applique.

## Options considérées

- **A — Statu quo** : rejetée par l'owner.
- **B — Tout fusionner sans exclusion** : rejetée ; elle lèverait le niveau C qu'ADR-123 D3 maintient.
- **C — Fusion par l'agent via un hook ou un skill modifié** : rejetée ; contournement sans périmètre.
- **D — Niveau B ouvert dès ce périmètre** : rejetée ; la revue indépendante serait déclarative, pour aucune
  fusion de plus au rejeu.
- **E — Périmètre fermé au niveau A, porte déterministe, fusion épinglée à la tête revue** : retenue.

## Conséquences

- **Positives** : plus aucun geste de l'owner sur les PR du périmètre, soit environ une fusion sur dix
  au rejeu ; le tag PROD et les zones STOP restent à lui. Les autres PR restent fusionnables en une ligne
  par `merge-train.sh`.
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
