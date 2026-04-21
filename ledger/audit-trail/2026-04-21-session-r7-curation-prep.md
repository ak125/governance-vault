---
type: retrospective
date: 2026-04-21
owner: Fafa
duration: ~3h
session_id: r7-curation-prep-p1-p4
related_prs:
  monorepo: [97, 98, 99]
  vault: [26, 27, 28]
tags: [r7, retrospective, session-log, curation, oem, rappel-conso, r7-vs-r8]
supersedes: none
builds_on: [2026-04-21-session-r7-brand-complete]
---

# Session Retrospective — R7 Curation Preparation (P1 → P4)

> **Date** : 2026-04-21 (après-midi, suite de la session matin `r7-brand-live-sync-complete`)
> **Scope** : préparer les conditions d'une curation éditoriale R7 scalable — gate runtime, admin UI v1, corpus support, documentation ops

---

## TL;DR

La session du matin avait livré l'architecture R7 (36/36 pages PUBLISH, admin UI MVP avec 3 textareas JSON). Mais la **valeur SEO restait bloquée** sur la curation humaine, difficile à lancer tant que :
- le backend ne protégeait pas contre la pollution cross-surface R8
- l'UI exposait du JSON brut aux admins non-techs
- aucun corpus structuré n'existait pour alimenter la rédaction
- aucune documentation n'expliquait quoi curer et comment

Cette session a livré les 4 éléments de préparation, dans l'ordre `P3 → P2 → P4 → P1` : 3 PRs monorepo + 3 PRs vault. Une erreur cadrage R7/R8 a été rattrapée en live et documentée.

## Scope couvert

4 priorités issues du prompt de continuation `r7-session-continuation-20260421.md` :

| Priorité | Livré par | Durée estimée vs réelle |
|---|---|---|
| P3 — Gate CI surface purity runtime | PR monorepo #97 | 1-2h → ~1h30 |
| P2 — Admin UI v1 formulaire dynamique | PR monorepo #98 | 2-3h → ~2h |
| P4 — Runbook admin éditorial | PR vault #26 | 30-60min → ~45min |
| P1 — Corpus OEM support | PR monorepo #99 + PR vault #27 | emergent → ~1h30 |

Ordre choisi (prep → valeur débloquée) au lieu de l'ordre numérique des priorités. Justification : P3 sécurise, P2 rend utilisable, P4 documente, P1 alimente.

## Livrables

### Monorepo (ak125/nestjs-remix-monorepo) — 3 PRs OPEN

| PR | Titre | Impact |
|----|-------|--------|
| [#97](https://github.com/ak125/nestjs-remix-monorepo/pull/97) | feat(seo): surface-purity gate — forbid cross-surface URLs in editorial content | Protection contenu R7 (BadRequest 400 sur URL R8 deep dans FAQ/issues/maintenance) + 50/50 unit tests + extension pour R4/R5/R8 |
| [#98](https://github.com/ak125/nestjs-remix-monorepo/pull/98) | feat(admin-brand): P2 dynamic form for R7 editorial | Remplacement 3 textareas JSON par liste editors (Add/Remove/char counters/JSON preview), +481 lignes frontend, shadcn/ui + lucide |
| [#99](https://github.com/ak125/nestjs-remix-monorepo/pull/99) | feat(rag): multi-source brand oem corpus downloader | `download-brand-oem-corpus.py` multi-source (Wikipedia FR + Wikidata SPARQL + Rappel Conso FR v2.1, opt-in Wikipedia EN + NHTSA), 667 lignes, 0-LLM, testé sur 5 marques pilotes |

### Governance Vault (ak125/governance-vault) — 3 PRs OPEN

| PR | Titre | Type |
|----|-------|------|
| [#26](https://github.com/ak125/governance-vault/pull/26) | runbook: admin UI curation éditorial R7 | Runbook ops + amendement R7 vs R8 |
| [#27](https://github.com/ak125/governance-vault/pull/27) | runbook: download-brand-oem-corpus.py | Runbook ops script PR #99 |
| #28 (cette PR) | retro: session r7 curation prep | Traçabilité |

## Décisions prises

### 1. Gate surface purity en runtime, pas uniquement agent

`r7-brand-validator` existe comme agent Claude (audit). Ajouter la gate en runtime (`PageRoleValidatorService.validateSurfacePurity`) garantit qu'elle s'applique à **chaque PUT éditorial et chaque enrichissement**, pas seulement aux audits ponctuels. Les deux couches stackent.

### 2. Admin UI v1 sans framework de form lourd

Pas de react-hook-form ni conform.js pour ce cas : la logique est simple (3 listes d'objets, validation au submit par Zod côté backend). State React vanilla + hidden inputs sérialisés = minimal et maintenable. Ajouter un form framework aurait été du bricolage.

### 3. Corpus support avec provenance, pas synthèse LLM

Option rejetée : faire synthétiser les FAQ/issues/maintenance_tips par Claude à partir des sources.
Option retenue : télécharger le corpus brut avec `source_uri` + `fetched_at` dans chaque fichier, et laisser l'humain rédiger.

Raison : `feedback_rag_vault_always_first.md` interdit de seed du contenu métier depuis LLM. Une synthèse LLM sur un corpus brut reste une synthèse LLM — donc interdite.

### 4. Wikipedia EN opt-in strict

Feedback utilisateur explicite : « contenu en anglais pas bon pour le contenu ». Site et SEO sont FR. Avoir Wikipedia EN par défaut créait le risque qu'un admin y pioche des formulations EN à coller dans l'UI FR → pollution SEO. Moved to `--source wikipedia-en` avec warning CLI « cross-ref technique seulement, NE PAS coller en direct dans l'UI FR ».

### 5. NHTSA opt-in (pas de triplet = pas d'énumération modèles)

L'endpoint `recallsByVehicle` exige le triplet `(make, model, modelYear)`. Le script lit `wikidata-models.json` s'il est présent pour énumérer. Sinon warning + skip. 36 marques × ~10 modèles × 26 années ≈ 9 000 requêtes → opt-in par défaut, trop agressif pour un flux quotidien.

## Erreurs et apprentissages

### Erreur cadrage R7 vs R8 (rattrapée en live)

En proposant des candidats `common_issues` à partir du corpus Rappel Conso FR, j'ai suggéré :
- ❌ « Peugeot Boxer NG — tuyau retour carburant »
- ❌ « BMW Série 5/7 2026 — faisceau câbles microfiltre »
- ❌ « Citroën Berlingo / C5 Aircross — moteur DV5R fuite »

Les 3 sont **modèle-spécifique ou motorisation-spécifique** = R8 (page véhicule), pas R7 (hub marque). Violation de la règle canon R7 « hub marque, pas de fiche véhicule ».

L'utilisateur l'a signalé immédiatement. Correction : amendement PR vault #26 avec nouvelle section « ⚠️ Règle critique — R7 = marque, pas modèle », 3 tableaux ✅/❌ (FAQ/issues/maintenance) avec exemples marque-transversaux réels, section « Que faire si tu trouves un signal R8 ? », règle dérivée ajoutée.

**Apprentissage** : un corpus utile (Rappel Conso 100 fiches Peugeot avec défauts structurés) ne garantit pas qu'il soit utilisable dans la surface cible. Le filtrage marque-level vs modèle-level est un travail d'humain informé, pas d'IA filtrant statistiquement. Le runbook doit rendre ce filtre explicite, pas le supposer acquis.

### Bug titre Wikipedia sur marques uppercase

`auto_marque.marque_name` stocke en MAJUSCULES (`PEUGEOT`, `CITROËN`). Wikipedia exige la casse normale. Le script initial passait `marque_name` tel quel → 404 sur Peugeot et Citroën. Fix : `name.title()` par défaut, overrides manuels conservés pour les cas spéciaux (Alfa Romeo, DS, MG).

### Collision nom de branche

Branche `feat/p3-surface-purity-gate` déjà utilisée et mergée (mais avec un scope différent : PREV-2 monitoring 5xx — réutilisation confuse par la session précédente). Renommée en local vers `feat/p3-r7-surface-purity-gate` avant push. Apprentissage : vérifier `gh pr list` pour les collisions de nom avant de push.

### Rappel Conso API v1.0 dépréciée

Premier essai sur `data.economie.gouv.fr/api/records/1.0/search/` avec dataset `rappelconso0` → 0 résultats silencieux. L'API a été migrée vers v2.1 `/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/records` avec ODSQL et schéma différent. Fix : migration vers v2.1 + re-test = 100 rappels Peugeot.

## Règles dérivées candidates (à promouvoir en canon)

1. **R7 ≠ R8 côté contenu** — un `common_issue` vrai pour un seul modèle/moteur n'est pas R7. Règle déjà canon pour les URLs (gate purity) ; elle mérite d'être explicitée pour le **texte** (gate ne détecte pas les mentions textuelles).
2. **Corpus avec provenance, pas synthèse** — un helper pour l'humain télécharge du brut avec `source_uri`. La synthèse reste une responsabilité humaine.
3. **SEO FR = FR-first** — toute source EN/US est opt-in strict avec warning explicite « NE PAS coller en direct ».
4. **Gate runtime + agent Claude = complémentaires** — une seule des deux couches laisse un trou. Gate runtime s'applique à chaque écriture ; agent Claude audite ponctuellement.
5. **Scope discipline : branche dédiée depuis main par plan** — déjà connue. Rappelée au cours de la session (stash initial des modifs hors-scope, rename de branche sur collision). Ne pas hériter de branche fourre-tout.

## Dette résiduelle (post-session)

### Mergeable maintenant (5 PRs OPEN)

Monorepo #97, #98, #99 + Vault #26, #27, #28. Aucune dépendance inter-PR bloquante. Ordre de merge suggéré :
1. Vault #28 (retro — read-only)
2. Vault #26 (runbook admin — pas de dépendance)
3. Vault #27 (runbook OEM corpus — URL vers #26, stable après merge)
4. Monorepo #97 (gate — pas de dépendance)
5. Monorepo #98 (UI — compatible avec ou sans gate mergé)
6. Monorepo #99 (script corpus — autonome)

### Non abordé, à faire ultérieurement

- **P1 curation réelle** — scope humain, pas IA. Commencer par 2-3 marques pilotes (Peugeot/BMW/Renault ont les meilleurs corpus Rappel Conso).
- **Gate texte pour mentions modèles R8 dans R7** — difficile à automatiser sans dictionnaire de modèles par marque. Rester en revue humaine pour l'instant.
- **Extracteur de candidats éditoriaux depuis le corpus** — un second script `extract-brand-editorial-candidates.py` pourrait proposer 3-5 FAQ marque-level à partir du corpus, l'admin valide/édite. Scope V2.
- **Édition UI R8** — pas d'équivalent `__seo_vehicle_editorial` aujourd'hui. Les signaux R8 identifiés via Rappel Conso vont en backlog externe.
- **Wikipedia `Liste des modèles {marque}`** — page n'existe pas pour toutes les marques. Fallback sur `Catégorie:Modèle de {marque}` non implémenté, laissé comme follow-up.

## Stats session

- Durée : ~3h (après-midi 2026-04-21)
- Commits : 9 (6 monorepo + 3 vault)
- Lignes ajoutées : ~1800 (script 667 + validator 200 + tests 153 + UI 481 + runbooks 2×230)
- Tests ajoutés : 13 (50/50 pass sur page-role-validator)
- PRs ouvertes : 6 (3 monorepo + 3 vault)
- Bugs identifiés et fixés en live : 3 (wikipedia-en default, titlecase DB uppercase, Rappel Conso v1.0 dépréciée)
- Erreur cadrage rattrapée : 1 (R7 vs R8 — runbook amendé)

## Références

### Session antérieure du jour
- [[2026-04-21-session-r7-brand-complete]] — session matin, architecture R7 de base

### PRs livrées (liens)
- Monorepo : https://github.com/ak125/nestjs-remix-monorepo/pull/97 · /98 · /99
- Vault : https://github.com/ak125/governance-vault/pull/26 · /27

### Knowledge base liée
- [[r7-brand-editorial-live-sync]] — architecture (déjà canon)
- [[r7-surface-purity-no-cross-surface-urls]] — règle canon que le gate runtime implémente
- [[r7-brand-route-refactoring]] — patterns frontend
- [[runbook-build-brand-rag]] — runbook sibling (facts stables)

### Règles rappelées
- `feedback_rag_vault_always_first.md` (Claude Code memory) — source canon > LLM synthesis
- `feedback_branch_scope_discipline.md` (Claude Code memory) — branche dédiée depuis main
