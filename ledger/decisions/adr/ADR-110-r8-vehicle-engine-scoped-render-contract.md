---
id: ADR-110
title: "Contrat de rendu de la projection R8 : fiche WIKI par modèle, blocs par motorisation résolus type par type depuis la DB — étend ADR-086 §1/§4, ADR-016 et ADR-059"
status: accepted
date: "2026-10-05"
decision_date: "2026-10-05"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
extends: ["ADR-086", "ADR-016", "ADR-059"]
related_adr: ["ADR-016", "ADR-059", "ADR-062", "ADR-066", "ADR-070", "ADR-086", "ADR-088", "ADR-095", "ADR-099", "ADR-106", "ADR-107"]
related_rules: ["G1", "AI1", "T1"]
related_incidents: []
version: "1.0.0"
---

# ADR-110 : Contrat de rendu de la projection R8

- **Statut** : Accepted (2026-10-05). La fusion par l'owner vaut ratification.
- **Numéro** : dérivé le 2026-10-05 (`main` du vault ∪ PR ouvertes) : `main` porte ADR-105, ADR-112
  et ADR-113 ; aucune PR ouverte ne porte un numéro de 106 à 111. Signé après les ADR-106 à 109, que
  le script owner exige sur `main`. Le script owner re-vérifie le numéro avant le commit.
- **Étend** :
  - [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §1 (surface R8 « écrite par
    motorisation ») et §4 (clés `fuel:` / `fuel_displacement:` / `engine_family:`), sans dire
    comment une page, qui est un type, retrouve le bloc de sa motorisation ;
  - [[ADR-016-vehicle-page-matview-persistence|ADR-016]] (payload de la fiche véhicule) et
    [[ADR-059-seo-runtime-projection|ADR-059]] (rendu depuis la projection).
- **Ordre de signature** : après ADR-106 et ADR-107.

## Périmètre

Rôle **`R8_VEHICLE`**, entités `vehicle`, pages `/constructeurs/<marque>/<modèle>/<type>.html`.
L'entité servie est un **type** (`type_id`) ; l'entité WIKI est un **modèle**.

## Contexte

Constats vérifiés le 2026-10-04 : monorepo `main` `f1c601170`, WIKI `origin/main` `042e566`, base
en lecture seule.
Re-vérifiés le 2026-10-05 : monorepo `main` `658c0a3ce` (aucun fichier cité modifié depuis
`f1c601170`), WIKI épinglé inchangé, base en lecture seule.

1. **Le WIKI écrit par modèle, la page est un type.**
   - `entity-data/vehicle.schema.json` : `make`, `model`, `generation`, `years`, un `type_id`
     optionnel et unique, et deux cartes éditoriales, `known_issues_by_engine` et
     `maintenance_by_engine`.
   - Ces cartes sont indexées par des clés `fuel:…`, `fuel_displacement:…` ou `engine_family:…`.
   - Le schéma ne porte aucun ancrage vers le modèle DB : rattacher une fiche à ses types
     demanderait une correspondance par nom.
2. **Le builder émet un bloc par clé.** `_map_vehicle_to_blocks` produit `R8_VEHICLE/known_issues`
   et `R8_VEHICLE/maintenance`, avec la clé moteur dans `usefulness_target`. Ce champ existe déjà
   dans le contrat d'export et dans les types du module de projection.
3. **Ce que la DB sait d'un type.**
   - `auto_type` porte `type_modele_id` (jamais nul), `type_fuel` et `type_liter`.
   - `type_fuel` : 22 valeurs brutes, avec variantes d'accent et combinaisons (hybrides,
     bicarburation).
   - `type_liter` : texte, 125 valeurs distinctes, 830 types sur 53 959 sans valeur.
   - `auto_type_motor_code` : 63 091 lignes, 50 741 types, 12 061 codes. Un code couvre en
     moyenne 5,2 types (médiane 3, p95 18, maximum 216).
   - `kg_engine_families` : 10 familles, sans lien vers les codes moteur. **Aucune table ne dit à
     quelle famille appartient un code.** Les `engine_family_key` des tables R8 sont des empreintes
     composées (marque::modèle::énergie::motorisation) pour mesurer la duplication, et
     `__seo_keywords.famille_moteur` est un signal de demande : ni l'un ni l'autre n'est une
     correspondance code → famille.
   - ADR-086 §4 dit ce pont « vide » : ce constat est périmé.
4. **Le servi R8 n'a pas de surcouche éditoriale effective.**
   - La page lit `__vehicle_page_cache` (ADR-016) et une surcouche `__seo_r8_pages`. Sur ses 155
     lignes, une seule est `INDEX` (148 `REVIEW_REQUIRED`, 6 `REGENERATE`), et elle ne porte pas de
     `rendered_json.blocks` : aucun véhicule n'est servi avec surcouche.
   - Le cache compte 28 505 lignes. Les 28 017 construites les 24 et 25 avril 2026 n'ont aucun code
     moteur. Le rebuild du 2026-10-03 en a reconstruit 488, dont 446 portent des codes moteur.
5. **Aucune fiche.** `wiki/vehicle/` est vide ; aucun export `vehicle`.

## Décision

### D1 — Une fiche véhicule WIKI est ancrée à ses modèles DB

- `entity-data/vehicle.schema.json` gagne un champ optionnel `modele_ids` (contrat ADR-062 §8,
  MINOR) : liste non vide d'identifiants `auto_modele`, validée contre un manifeste commité, comme
  `related_gammes`. C'est le même principe que `pg_id` pour la gamme.
- Une fiche sans `modele_ids` n'est rattachée à aucune page. Aucun rattachement par nom de marque
  ou de modèle.
- La portée d'un bloc est limitée aux types dont `type_modele_id` figure dans `modele_ids` de sa
  fiche.

### D2 — Un seul résolveur, de la DB source vers les clés moteur

- Pour un `type_id`, le résolveur calcule ses clés depuis les tables source, **jamais** depuis
  `__vehicle_page_cache` ni `__seo_r8_pages` :

  | Clé | Calcul |
  |---|---|
  | `fuel:<carburant>` | `type_fuel` par une table de normalisation déclarée vers l'enum WIKI (`essence`, `diesel`, `hybride`, `electrique`, `gpl`, `ethanol`) |
  | `fuel_displacement:<carburant>:<litres>` | carburant ci-dessus et `type_liter` par une conversion déclarée |
  | `engine_family:<code>` | codes de `auto_type_motor_code` par une correspondance code → famille **explicite et sourcée** en DB |

- La table de normalisation est déclarée, versionnée et testée. Une valeur de `type_fuel` absente
  de la table ne produit aucune clé `fuel:`, et elle est comptée. Une valeur composée n'est
  normalisée que si l'enum a la catégorie exacte.
- **Pas de famille sans correspondance.** Tant qu'aucune correspondance code → famille n'existe en
  DB, les clés `engine_family:` ne résolvent aucun type. Elles sont comptées
  `unresolved_engine_family`. Aucun rapprochement par préfixe de code. Créer cette correspondance
  suit ADR-086 §4 (au moins deux sources, ou backfill DB) et une décision distincte.
- Ce résolveur est **unique**. La composante R8 de R2 (ADR-086 §1, R2 = R1 ⊕ R8) le réutilise ;
  aucun second résolveur.

### D3 — Sélection du bloc : la clé la plus spécifique, sans repli

- Pour chaque section (`known_issues`, `maintenance`), on prend au plus **un** bloc. On garde la
  clé résolue la plus spécifique : `engine_family` d'abord, puis `fuel_displacement`, puis `fuel`.
- Si aucune clé du type ne correspond, la section n'est pas rendue. Aucun repli vers une autre
  motorisation, un autre modèle ou un texte générique.
- Deux blocs de même section et de même clé dans une fiche rendent la section invalide pour cette
  clé : rien n'est rendu, l'erreur est comptée.
- Un bloc dont `usefulness_target` ne respecte pas le motif des clés est classé
  `unmapped / invalid_engine_key`.

### D4 — Table R8 v1

| Section WIKI (`R8_VEHICLE/…`) | Section servie | Titre fixe |
|---|---|---|
| `known_issues` | points de vigilance de la motorisation | Points de vigilance de cette motorisation |
| `maintenance` | repères d'entretien | Repères d'entretien |

- Ces sections s'ajoutent au cadre DB de la page (identité, motorisations, familles de pièces,
  pièces courantes), qui reste inchangé.
- Rendu : prose sûre, et listes selon ADR-107. Titres fixes, provenance non affichée, en-tête
  inchangé (ADR-106 D6, D8).
- La table vit dans le module de projection existant, sur le modèle du mapper R3.

### D5 — Duplication : mesurée, jamais masquée

- Un même bloc sert tous les types de la portée qui résolvent sa clé. La page reste différenciée
  par son cadre DB propre au type.
- Pour chaque bloc, la projection rapporte le nombre de pages qu'il alimente.
- `scripts/qa/r8-diversity-check.py` reste **report-only** sur le chemin projeté.
- Seule la collision exacte de title / H1 bloque (ADR-095). Cet ADR ne touche à aucune balise.

### D6 — Complétude et activation

- Un type est prêt si au moins une section résout un bloc valide. Le cadre DB est toujours rendu ;
  il n'existe aujourd'hui aucune surcouche servie à perdre (constat 4).
- Activation par fiche : `SEO_PROJECTION_READ_V1` et le canary `R8_VEHICLE@vehicle:<slug>`. Seuls
  les types de la portée qui résolvent au moins une section basculent.
- Avant l'ajout au canary : comparaison écrite projeté vs servi, sur un échantillon de types de la
  portée, avec pour chaque bloc le nombre de pages alimentées. Acte owner.
- La comparaison signale aussi les types dont la ligne de cache date d'avant le rebuild du
  2026-10-03 : leur cadre DB n'affiche pas les codes moteur. Le rebuild du cache est un chantier distinct, non bloqué par cet
  ADR.

## Options considérées

- **Écrire le WIKI par type** : rejeté. 53 959 types ; ADR-086 fixe l'écriture par motorisation.
- **Rattacher par nom de modèle** : rejeté. C'est une devinette d'exécution (D1).
- **Déduire la famille du préfixe du code moteur** : rejeté. `K9K 608` ressemble à `K9K`, mais
  rien en base ne l'établit (D2).
- **Lire les codes moteur dans `__vehicle_page_cache`** : rejeté. Ce cache est une projection, et
  28 017 de ses lignes datent d'avril 2026, sans codes moteur.
- **Repli sur la clé `fuel:` d'un autre modèle** : rejeté. Ce serait un texte qui ne concerne pas
  ce véhicule.

## Ce que cet ADR ne fait pas

- Il ne crée aucune fiche, aucune correspondance code → famille, et n'active aucune lecture servie.
- Il ne modifie ni le cache ADR-016, ni `__seo_r8_pages`, ni son producteur.
- Il ne change aucune URL, meta, H1 ou robots, ni l'indexabilité.

## Conséquences

### Positives

- Une fiche WIKI peut enrichir des centaines de pages type, sans texte inventé et avec une portée
  vérifiable.
- R2 dispose du résolveur dont dépend sa composante R8.

### Négatives

- Sans correspondance code → famille, seules les clés `fuel:` et `fuel_displacement:` servent.
  Elles différencient moins.
- Un bloc `fuel:` sert beaucoup de pages : d'où la mesure de D5 et l'activation fiche par fiche.

## Rollback

- Avant activation : revert, sans effet servi.
- Après activation : retrait de la fiche du canary, ou coupure de `SEO_PROJECTION_READ_V1`.

## Anti-patterns interdits

- Rattacher une fiche à un type par similarité de nom.
- Déduire une famille moteur d'un préfixe ou d'une ressemblance de code.
- Servir le bloc d'une autre motorisation, ou d'un autre modèle, faute de bloc propre.
- Lire les clés moteur dans un cache ou dans `__seo_r8_pages`.
- Écrire un second résolveur pour R2.

## Références

- [[ADR-086-encyclopedia-editorial-content-contract|ADR-086]] §1, §4, §7.
- [[ADR-016-vehicle-page-matview-persistence|ADR-016]] — payload de la fiche véhicule.
- [[ADR-059-seo-runtime-projection|ADR-059]] — projection SEO.
- [[ADR-095-balise-anti-duplicate-hard-gate|ADR-095]] — gate anti-duplicata des balises.
- [[ADR-066-r2-content-composition-v2|ADR-066]] /
  [[ADR-070-r8-r1-first-r2-second-active-disambiguation|ADR-070]] — composition R2 et cadre R8.
- [[ADR-099-seo-projection-writer-runtime-placement-and-exports-transport|ADR-099]] D5 — canary par
  paire.
- ADR-106 — contrat de rendu R3 (modèle). ADR-107 — listes structurées.
- [[ADR-062-repository-contract-system-meta-model|ADR-062]] §8 — évolution SemVer du contrat WIKI.
