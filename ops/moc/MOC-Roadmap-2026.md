---
type: moc
status: canon
updated: 2026-05-06
---

# MOC : Roadmap globale 2026

Index canonique des chantiers transverses du projet AutoMecanik. Chaque
chantier porte un identifiant lettre stable (A→I) et un rang de priorité
business (P0→P8). Cette MOC ne décide pas l'ordonnancement d'exécution
hebdomadaire — elle définit la **structure** dans laquelle l'arbitrage est
rendu lisible.

> **Source de vérité** : ce fichier. Tout autre document (plans Claude Code
> locaux, scratch, conversations) référence cette MOC, jamais l'inverse.

---

## Pourquoi cette MOC existe

Constat 2026-05-01 : le plan ADR-033 (raw/wiki/diag) en cours était traité
implicitement comme « la stratégie projet » alors qu'il ne couvre qu'un pilier
sur ~9. Effets observés :

- Risque d'aspirer la bande passante d'exécution sur knowledge canon pendant
  que les chantiers business (paiement, catalogue, indexabilité, sécurité)
  avancent en sous-priorité implicite.
- Pas de matrice partagée pour arbitrer « finir Phase 2 ADR-033 » vs
  « tester le tunnel checkout ».
- Plans existants (ADR-036, ADR-033, ADR-038) se référencent mutuellement
  sans index racine — d'où dérive de scope observée dans plusieurs sessions.

Cette MOC tranche en re-cadrant ADR-033 comme **Chantier C (1/9)**, pas comme
la stratégie globale.

---

## Les 9 chantiers (A→I)

> La lettre est un identifiant stable, **pas un rang**. Le rang business est
> donné en P0→P8 plus bas.

| ID | Chantier | Objectif | ADRs/MOCs |
|----|----------|----------|-----------|
| A  | Runtime e-commerce / business core | Fiabiliser ce qui vend (panier, paiement, commande, emails) | — |
| B  | Catalogue / compatibilité véhicule | Donnée produit exploitable (V-Level, alias, doublons, OEM) | [[ADR-032-diagnostic-maintenance-unification]] |
| C  | Knowledge / Raw / Wiki / Diagnostic Canon | Source canonique unique pour RAG/SEO/chatbot | [[ADR-031-four-layer-content-architecture]], [[ADR-033-wiki-gamme-diagnostic-relations-contract]] |
| D  | SEO / indexation / crawl budget | Sortir du piège « pages explorées non indexées » | [[ADR-040-seo-roles-canon-ts-side-only]] (R0..R8 canon TS-side, accepted 2026-05-05) |
| E  | Performance backend / frontend | Vitesse, stabilité, conversion | [[ADR-016-vehicle-page-matview-persistence]], [[ADR-017-rpc-pieces-cast-cleanup]] |
| F  | Sécurité / DevSecOps / isolation prod | Éviter incidents graves | [[ADR-021-database-rls-hardening-zero-trust]], [[ADR-028-preprod-supabase-isolation]], [[ADR-030-npm-ignore-scripts-alpine-musl]] |
| G  | RAG / support client / assistant | Aider clients, réduire support manuel — RAG = consommateur | [[ADR-022-r8-rag-control-plane]] |
| H  | Marketing / acquisition | Trafic utile + conversion (LOCAL 93 + retention) | [[ADR-036-marketing-operating-layer]], [[ADR-038-marketing-agent-naming-canon]] |
| I  | Agents / gouvernance / Paperclip | Encadrer agents sans complexifier — réduire d'abord | [[ADR-034-aicos-operating-contract]], [[ADR-037-agent-naming-canon]], [[ADR-039-wiki-frontmatter-zod-canon]] |

### Détail des sujets par chantier

Pour chaque chantier, la liste numérotée Ax/Bx/… (jusqu'à 7 sujets max) sert
d'identifiant pour les tickets Paperclip et PRs. Voir le détail dans le plan
local pré-canonisation cité en bas de page.

---

## Priorité business (P0→P8)

> Ordre **indépendant** de l'identifiant alphabétique. Reflète le rendement
> estimé pour le business sur un horizon 3 mois.

| Rang | Chantier | Justification |
|------|----------|---------------|
| **P0** | F — DevSecOps / sécurité prod | Un incident grave annule le bénéfice de tous les autres chantiers. Plancher non négociable. |
| **P1** | A — Runtime e-commerce | Sans paiement/commande/email fiables, SEO et marketing ne convertissent pas. Cœur du revenue. |
| **P2** | D — SEO indexation / crawl budget | Pages explorées non indexées = frein direct. Lever ce frein débloque C, B et G en cascade. |
| **P3** | B — Catalogue / compatibilité véhicule | Donnée produit fiable = base pour SEO (D), RAG (G), marketing local (H). Effet levier multiple. |
| **P4** | E — Performance | Conditions matérielles de P1, P2, P3. Lent = abandon + crawl waste. |
| **P5** | C — Raw/Wiki/Diagnostic canon | Fondationnel mais effet revenue indirect. À finir, pas à étendre prématurément. |
| **P6** | H — Marketing | Acquisition utile **après** que A/D/B soient propres. Sinon on amplifie un funnel cassé. |
| **P7** | G — RAG / support | Dépend de C (wiki validé) + D (pages indexées) + B (compat fiable). À ouvrir une fois ces trois solides. |
| **P8** | I — Agents / Paperclip | Capacité, pas finalité. Réduire d'abord, ajouter ensuite. |

**Note** : ce classement vaut pour **la planification de nouveaux chantiers**.
Il ne dit pas « arrêter ce qui est en cours sur C ou H » — finir le travail en
cours reste rationnel tant qu'il est borné et que le coût d'arrêt > coût de
finition.

---

## Grille d'arbitrage hebdomadaire

Chaque action candidate (PR, ticket, brief agent) est notée sur 5 critères :

| Critère | Question |
|---------|----------|
| **Revenue** | Augmente-t-elle les ventes ou évite-t-elle une perte de ventes ? |
| **Risk** | Réduit-elle un risque prod / sécurité / SEO majeur ? |
| **Blocking** | Plusieurs chantiers dépendent-ils de cette action ? |
| **Effort** | Faisable en petite PR vérifiable (< 1 semaine, tests propres) ? |
| **Evidence** | Basée sur un bug, log, audit ou métrique réelle ? |

**Règle de tri** :

- Prioriser ce qui est **fort** sur Revenue / Risk / Blocking.
- Refuser les actions « jolies » sans métrique, sans bug, sans dépendance
  claire — même si elles sont dans un chantier P0/P1.
- Privilégier petits Effort + forte Evidence quand on hésite : c'est ainsi
  qu'on accumule des wins vérifiables.

Cette grille s'applique **avant** le classement alphabétique (A→I) et **avec**
la priorité P0→P8.

---

## État des plans dédiés

| Chantier | Plan dédié | Statut |
|----------|------------|--------|
| A — Runtime | TBD | À créer |
| B — Catalogue | [[ADR-032-diagnostic-maintenance-unification]] + mémoires monorepo | Existant partiel |
| C — Raw/Wiki/Diag | Plan local Claude Code rev 4 (re-titré « Plan — Chantier C » 2026-05-01) | Actif |
| D — SEO indexation | Pipelines R*/agents `workspaces/seo-batch/` (monorepo) + [[ADR-059-seo-runtime-projection]] (proposed 2026-05-13) | Existant partiel |
| E — Performance | TBD (à consolider depuis ADR-016/017) | À créer |
| F — Sécurité | [[ADR-021-database-rls-hardening-zero-trust]] / [[ADR-028-preprod-supabase-isolation]] / [[ADR-030-npm-ignore-scripts-alpine-musl]] + plan global TBD | Existant partiel |
| G — RAG | [[ADR-022-r8-rag-control-plane]] + mémoires RAG | Existant partiel |
| H — Marketing | Plan local Claude Code (ADR-036 Phase 1 majoritairement mergée 2026-04-30, Phase 2 en cours) | Actif |
| I — Agents/Paperclip | [[ADR-034-aicos-operating-contract]] + [[ADR-037-agent-naming-canon]] / [[ADR-038-marketing-agent-naming-canon]] / [[ADR-039-wiki-frontmatter-zod-canon]] (accepted 2026-05-01) | Existant partiel |

> Les plans listés comme « Plan local Claude Code » vivent actuellement dans
> `/home/deploy/.claude/plans/` sur la VPS DEV. Ils ne sont pas versionnés ni
> partagés. Ils peuvent être canonisés individuellement plus tard si
> stabilité durable et besoin d'historique cross-session le justifient.

---

## Hors scope explicite

Cette MOC **ne fait pas** :

- Trancher l'ordre d'exécution réel des sprints (P0→P8 est une boussole, pas
  un Gantt — l'arbitrage hebdo reste avec l'humain pilote).
- Créer les plans dédiés TBD (Runtime A, Performance E, F global, D global) —
  ils seront écrits à la demande, chantier par chantier.
- Toucher au code, à la DB, ou aux ADRs.

---

## Référence

- [[ADR-031-four-layer-content-architecture]] — raw/wiki/exports/consumers
- [[ADR-033-wiki-gamme-diagnostic-relations-contract]] — diagnostic relations
- [[ADR-036-marketing-operating-layer]] — Marketing Operating Layer
- [[ADR-040-seo-roles-canon-ts-side-only]] — SEO Roles canon R0..R8 TS-side (accepted 2026-05-05)
- [[MOC-Decisions]] — index ADRs vault
- [[MOC-Knowledge]] — index knowledge vault
- [[MOC-Agents]] — index agents (chantier I)
- [[ADR-037-agent-naming-canon]] — agent naming canon (accepted 2026-05-01)
- [[ADR-038-marketing-agent-naming-canon]] — marketing extension (accepted 2026-05-01)
- [[ADR-039-wiki-frontmatter-zod-canon]] — wiki frontmatter Zod canon (accepted 2026-05-01)

---

## Versionnage

| Version | Date | Changements |
|---|---|---|
| 1.0.0 | 2026-05-01 | Création initiale. 9 chantiers A→I, priorité P0→P8, grille d'arbitrage. Source pré-canonisation : `/home/deploy/.claude/plans/plan-directeur-roadmap-globale-automecanik-2026.md` (scratch local DEV, conservé pour traçabilité genèse). |
| 1.0.1 | 2026-05-06 | Self-review pré-merge : (a) Chantier D désormais ancré sur [[ADR-040-seo-roles-canon-ts-side-only]] (accepted 2026-05-05) ; (b) ADR-037/038 promues `accepted 2026-05-01`, ADR-039 ajoutée (chantier I + H) ; (c) wikilinks complétés. Aucune décision changée, mise à jour factuelle pré-merge. |
