---
id: ADR-096
title: Dérogation schemaVersion DepEntry — correction in-place de provenance (occurrences[])
status: Accepted
date: 2026-07-04
deciders: [Fafa]
supersedes: []
amends: []
tags: [registry, control-plane, schema-version, depentry, derogation, ADR-058]
---

# ADR-096 — Dérogation schemaVersion DepEntry (correction in-place de provenance)

## Statut

Proposed — dérogation **ponctuelle et single-use** à la Schema Evolution Policy d'**ADR-058 §4**
(retrait de champ obligatoire / restructuration de schéma = évolution *major* exigeant un ADR dédié +
sunset + migration). Ne prend effet qu'après commit **G3 signé** + merge vault. Débloque le merge de
`ak125/nestjs-remix-monorepo#1225` (`fix/deps-l1-occurrences-fidelity`, head technique `f906ea48c`).
Relation à ADR-058 : **exception bornée**, sans affaiblir ni amender la politique (voir NON AUTORISÉ).

## INCIDENT

#1223 a livré une provenance `DepEntry` déterministe mais **fausse** :
`workspaces[]` et `declaredIn[]` triés séparément puis re-zippés par index → paires
`(workspace, declaredIn)` erronées. `git diff --exit-code` ne peut pas l'attraper
(il rejoue le même producteur faux).

## DÉROGATION AUTORISÉE

`DepEntry` **uniquement** :

```
workspaces[] + declaredIn[]
        →
occurrences[{ workspace, declaredIn, bucket, specifier }]
```

Correction **in-place sous `schemaVersion: "1.0.0"`** — c.-à-d. **sans** le bump *major* d'ADR-058 §4 —
autorisée **pour `DepEntry` seul**.

## MOTIF

L'ancien modèle **ne peut pas représenter fidèlement ses propres sources**.
Laisser la forme infidèle en place pour préserver un numéro de version perpétuerait
un contrat *vert-mais-faux*.

## CONDITIONS

1. #1225 apporte une **preuve de fidélité indépendante** du producteur.
2. **Aucun autre breaking change silencieux** sous `schemaVersion 1.0.0`.
3. **PR-E ferme immédiatement** la chaîne L1 → L3 → REPO_MAP avec **I6 PASS**.
4. L'architecture future de **versionnage / migration reste gouvernée séparément**.

## NON AUTORISÉ

- aucun changement des **quatre autres schémas L1** ;
- aucun **précédent général** pour contourner SemVer ;
- aucun **affaiblissement d'ADR-058** ;
- aucune **extension de scope de #1225** ;
- aucune **absorption de PR-E**.

## ÉPUISEMENT

La dérogation est **consommée** une fois **#1225 mergé et PR-E fermé**.
Elle **n'est pas réutilisable**.
