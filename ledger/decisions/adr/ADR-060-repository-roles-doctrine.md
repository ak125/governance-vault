---
id: ADR-060
title: "Doctrine des rôles repositories — 5 acteurs canon (vault / wiki / raw / monorepo / rag)"
status: accepted
date: 2026-05-13
decision_date: 2026-05-13
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: []
related_rules: ["G1", "G2", "G3", "G5"]
related_incidents: []
related_adr: ["ADR-012", "ADR-013", "ADR-015", "ADR-031", "ADR-036", "ADR-058", "ADR-059"]
---

# ADR-060 : Doctrine des rôles repositories — 5 acteurs canon

## Context

L'écosystème AutoMecanik s'appuie sur 5 repositories canoniques distincts :

- `ak125/governance-vault`
- `ak125/automecanik-wiki`
- `ak125/automecanik-raw`
- `ak125/nestjs-remix-monorepo`
- `ak125/automecanik-rag`

Leurs responsabilités opérationnelles sont **canon de fait** depuis [[ADR-015-vault-single-source-of-truth]] (vault SoT) et [[ADR-031-four-layer-content-architecture]] (4-layer content flow), mais **jamais écrites littéralement** comme doctrine inter-repos. Au 2026-05-13, un `grep -rE "vault décide|monorepo exécute" ledger/decisions/adr/` retourne 0 hit.

Conséquences observées :

1. Risque récurrent de créer des sections opérationnelles dans le vault (`growth/`, `marketing/`, `seo/`, `content/`, `infra/`) en partant du principe implicite que « tout ce qui touche la gouvernance vit dans le vault ».
2. Confusion sur l'écriture : qui peut écrire où, sous quelle PR signature, pourquoi le monorepo ne doit jamais écrire dans wiki ou raw.
3. Le rag est parfois traité comme une source secondaire alors qu'il est strictement mirror post-Phase F (D22 d'ADR-031).
4. Memory rule `feedback_canon_rule_live_iff_adr_accepted` : le canon de fait reste fragile sans canon ratifié.

[[ADR-031-four-layer-content-architecture]] (4-layer content) et [[ADR-058-repository-control-plane]] (Repository Control Plane interne au monorepo) ne couvrent pas cette **doctrine inter-repos** — ils couvrent le matériau et la cartographie d'un repo, pas la répartition d'autorité entre les 5.

## Decision

Adopter la **doctrine des rôles repositories à 5 acteurs canon**, orthogonale et complémentaire au flux 4-layer d'[[ADR-031-four-layer-content-architecture]].

### Tableau canon

| Acteur | Rôle canon | Repository | Autorité opérationnelle |
|---|---|---|---|
| **Vault** | *Décide* | `ak125/governance-vault` | ADR, rules T/G/AI/V, policies, MOCs, runbooks. Pas d'écriture métier. |
| **Wiki** | *Valide* | `ak125/automecanik-wiki` | Connaissance sourcée, lintée, validée humainement. Source de vérité métier non-DB. |
| **Raw** | *Collecte* | `ak125/automecanik-raw` | Brut par défaut. Scrapes, CSV, fixtures, generators output, quarantine. |
| **Monorepo** | *Exécute* | `ak125/nestjs-remix-monorepo` | Runtime NestJS + Remix. Lit wiki/exports et bases DB métier. N'écrit ni dans raw, ni dans wiki, ni dans vault. |
| **Rag** | *Indexe et consomme. Jamais source de vérité métier, éditoriale ou canonique.* | `ak125/automecanik-rag` | Consommateur généré (sync-from-wiki). Lecture seule métier post-Phase F (D22 d'ADR-031). |

### Invariants

1. **L'écriture métier dans wiki** passe par PR humaine (Phase E pilote, Phase F batch d'ADR-031).
2. **L'écriture canon dans vault** passe par PR signée G3 (cf. [[ADR-015-vault-single-source-of-truth]]).
3. **Le monorepo n'écrit jamais** dans wiki, raw, ou vault. Il *consomme* via env vars (`AUTOMECANIK_WIKI_PATH`, `AUTOMECANIK_RAW_PATH`) ou via cron sync (cf. memory `feedback_cron_vps_canon_pour_mono_vps_setup`).
4. **Le rag est mirror, jamais source**. Toute modification manuelle de `automecanik-rag/knowledge/<5 catégories>` est bloquée par pre-commit hook (D22).
5. **Aucune section opérationnelle dans le vault**. Le vault contient uniquement : `ledger/decisions/adr/`, `ledger/rules/`, `ops/runbooks/`, `ops/moc/`, et `ledger/knowledge/` *uniquement* pour audit trail, handoff et connaissance gouvernée — **jamais pour contenu métier opérationnel** (catalogue, briefs, guides clients, données marketing). Les contenus métier vont au wiki ; l'exécution va au monorepo ; les runtimes opérationnels vont aux workspaces (`workspaces/marketing/`, `workspaces/wiki/`, `workspaces/seo-batch/`).

### Formule canonique

> **vault décide, wiki valide, raw collecte, monorepo exécute, rag indexe et consomme.**

Cette formule littérale est l'invariant cité par les agents et contributeurs nouveaux. Elle est répétée intentionnellement pour faciliter recherche et grep.

### Articulation avec les ADRs sœurs

- **[[ADR-015-vault-single-source-of-truth]]** : pose le vault comme SoT canonique. ADR-060 précise *vault décide quoi*.
- **[[ADR-031-four-layer-content-architecture]]** : pose le flux raw → wiki → exports → consumers. ADR-060 précise *qui exécute le flux dans chaque repo*.
- **[[ADR-036-marketing-operating-layer]]** : applique la doctrine au domaine marketing (workspace marketing dans monorepo, briefs dans DB, pas de `.md` flottants wiki).
- **[[ADR-058-repository-control-plane]]** : canonise la *manifestation exécutable* du rôle *Exécute* du monorepo. ADR-060 et ADR-058 sont complémentaires : ADR-060 dit *qui exécute* au niveau inter-repos ; ADR-058 dit *comment le monorepo expose sa cartographie*.
- **[[ADR-059-seo-runtime-projection]]** : projection du wiki vers la DB pour pages R0-R8. Conforme à l'invariant ADR-060 « rag/runtime indexe, jamais source ».

## Options considérées

### Option A — Statu quo, doctrine implicite (rejetée)

Continuer sans canon ratifié.

**Inconvénients** : risque récurrent de créer `governance-vault/growth/` ou similaire ; ambiguïté pour les agents et contributeurs nouveaux ; canon de fait fragile (`feedback_canon_rule_live_iff_adr_accepted`).

### Option B — Amendement ADR-031 (rejetée)

Insérer la doctrine 5-layer dans ADR-031 comme nouvelle section.

**Inconvénients** : viole le pattern « une ADR = une décision ». ADR-031 traite du flux de contenu (matériau), pas de la répartition d'autorité entre repositories. Mélanger les deux concerns en une seule ADR rend l'évolution future plus difficile (modifier l'un implique de toucher l'autre) et complique les cross-references depuis d'autres ADRs (« voir ADR-031 §1A » vs « voir ADR-060 »).

### Option C — Méta-ADR « Repository Operating Plane » (rejetée)

Créer une grande ADR qui bundle doctrine + Control Plane + workspace governance.

**Inconvénients** : bundle de décisions = anti-pattern ADR. Duplique ADR-058 (Control Plane). Force ratification couplée de décisions qui devraient évoluer indépendamment.

### Option D — Nouvel ADR-060 doctrine pure (chosen)

Une ADR dédiée à la doctrine des rôles repositories, sans bundle, sans amendement. Pattern aligné avec ADR-058 (Control Plane) et ADR-059 (SEO Runtime Projection) créées sur le même jour 2026-05-13 — chacune avec un concern propre.

**Avantages** :
- Concern unique, ratification atomique légitime
- Cross-références faciles depuis ADR-031, ADR-036, ADR-058, ADR-059, futurs ADRs
- Évolution indépendante possible (futur amendement doctrine sans toucher ADR-031)
- Lecture rapide pour agents et contributeurs (1 page = 1 doctrine)

## Conséquences

### Positives

- Doctrine ratifiée → memory `feedback_canon_rule_live_iff_adr_accepted` satisfaite, canon LIVE
- Anti-bricolage explicite (invariant 5) : verrouille le risque de pollution du vault
- Cross-références ADR claires
- Débloque les sous-projets downstream cohérents (workspace governance, cleanup runtime, CI invariants)

### Négatives / Coûts

- 1 ADR de plus dans le ledger (compensé par lisibilité accrue)
- ADR-060 introduit la mention « workspaces/ » dans le canon — futur ADR (probable ADR-061 « workspace governance ») devra préciser frontière/lifecycle/ownership. Hors scope ici.

### Neutres

- ADR-031, ADR-036, ADR-058, ADR-059 inchangées dans le body
- Aucune modification monorepo, wiki, raw, rag, workspaces

## Conformité règles vault

- **G1 (Canon fait foi)** : ADR-060 ratifiée AVANT toute construction Phase 2 downstream
- **G2 (Zéro orphelin)** : MOC-Decisions ligne ADR-060 ajoutée dans la même PR + MOC-AuditTrail entrée
- **G3 (Signed commits)** : commit signé via clé `vault-signing@automecanik.com`
- **G5 (Canon authoritative)** : ADR-060 référencée par MOC-Decisions post-merge

## Mise en œuvre

ADR-060 créée directement en `status: accepted` (pattern [[ADR-059-seo-runtime-projection]] du 2026-05-13 17:14 → 17:27 même jour). Aucune cascade d'implémentation requise — la doctrine est déclarative, ses conséquences (workspace governance, CI gates anti-pollution vault) sont des sous-projets futurs avec leurs propres ADRs et PRs.

Audit-trail vault créée dans la même PR (`ledger/audit-trail/2026-05-13-adr-060-repository-roles-doctrine.md`) conformément à `feedback_auto_vault_audit_trail_on_adr` (ADR-054 SoT).

## Références

- [[ADR-015-vault-single-source-of-truth]]
- [[ADR-031-four-layer-content-architecture]]
- [[ADR-036-marketing-operating-layer]]
- [[ADR-058-repository-control-plane]]
- [[ADR-059-seo-runtime-projection]]
- [[MOC-Decisions]]
- Memory : `feedback_canon_rule_live_iff_adr_accepted`, `feedback_no_bricolage_align_existing_contract`, `feedback_verify_existing_first`, `cross-repo-and-governance-discipline`
- Brainstorm : `/home/deploy/.claude/plans/verifier-la-meilleure-delightful-kurzweil.md` (session 2026-05-13)
