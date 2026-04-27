---
type: knowledge
status: draft
domain: seo
created: 2026-04-25
related:
  - ADR-022-r8-rag-control-plane
  - r8-vehicle-enrichment-stage1-honest-debrief-20260425
  - r8-rag-control-plane-design-20260423
tags:
  - r8
  - vehicle
  - duplicate-content
  - scraping
  - frontend
  - propose-before-write
  - session-wrap
---

# R8 distinct render + scraping canon — Session wrap (2026-04-25 → 26)

Document de consigne de fin de session. État réel des deux tracks lancés
pour casser le duplicate content R8 (Jaccard 83 % mesuré sur Clio III
sœurs). À reprendre dans une session future avec la tête fraîche.

---

## TL;DR

- **ADR-022** promu `proposed → accepted` (vault PR #74 mergée).
- **2 PRs draft monorepo** ouvertes en parallèle, scopes orthogonaux.
- **1 row dans `__rag_proposals`** insérée pour test pipeline → **REGRESSION détectée en review** (proposal supprime des fields déjà enrichis au lieu d'enrichir). À ne **PAS** approuver. À DELETE ou investiguer.

---

## Mesure de référence (à conserver pour comparaison post-fix)

```
Jaccard ≥4 chars sur HTML rendu prod (curl) entre 2 motorisations sœurs Clio III 1.5 dCi
URL_A : /constructeurs/renault-140/clio-iii-140004/1-5-dci-26627.html  (64 ch)
URL_B : /constructeurs/renault-140/clio-iii-140004/1-5-dci-19051.html  (68 ch)

  tokens_total_A : 733 | uniques_A : 306
  tokens_total_B : 752 | uniques_B : 337
  communs        : 292
  uniques only A : 14
  uniques only B : 45
  jaccard        : 83.2 %  ← FAIL (seuil cible Google < 40 %)
```

Tokens uniques par page : surtout des codes pièces (mre50…, ure50…) — quasiment **aucun token texte distinctif** côté sémantique. Boilerplate massif partagé.

`r8-diversity-check --modele-id 140004` (côté DB `__seo_r8_pages`) : 3 sib pages, avg_diversity 68.3 %, verdict REVIEW, collisions sur `faq_signature` et `category_signature` (pools 7).

---

## Ce qui a été livré

### 1. Vault canon

- **Vault PR #74** (mergée 2026-04-25, commit `6df8cf6c`) : ADR-022 R8 RAG Control Plane → `status: accepted`, `decision_date: 2026-04-25`, `reviewed_by: @fafa`.

### 2. Monorepo PR #185 — frontend distinct render

Branche `feat/r8-html-distinct-render`. **3 commits, draft, à reviewer.**

| # | Commit | Action |
|---|---|---|
| 1 | `9d9ac41e` | Cut `TrustSection` de la route R8. 100 % boilerplate identique sur 53 959 pages. Composant toujours exporté depuis `r8/index.ts` pour usage ailleurs. |
| 2 | `e7048c22` | Ajout `TechSpecsSection` : table specs depuis `auto_type` (cylindrée, kW, body, période mensuelle, code moteur, CNIT). Filtré si null. |
| 3 | `f8cb914b` | Enrichissement JSON-LD `@type:Car` Schema.org (engineDisplacement cm³, engineType codes, enginePower [HP+kW], CNIT et code moteur en additionalProperty). |

Spec : `docs/superpowers/specs/2026-04-25-r8-html-distinct-render.md`.

**Gain Jaccard estimé** : 83 % → 70-75 % (insuffisant seul, plafonne).

### 3. Monorepo PR #188 — scraping canon

Branche `feat/rag-vehicle-scraping-canon`. **4 commits, draft, smoke test partiel.**

| # | Commit | Action |
|---|---|---|
| 1 | `7642b26f` | Récupération `download-vehicle-motor-corpus.py` (724 LOC) depuis le commit tip 78324b28 de la PR fermée #172, + CSV curated URLs Clio III, + spec. Zéro DB write, zéro RAG write. |
| 2 | `6a7f844f` | NEW `rag-propose-vehicle-from-web.py` (1103 LOC) : enricher mode propose. Lit web-vehicles/, parse engines, compute proposed content, INSERT `__rag_proposals` (status=pending, expires=now+14d). Hashes sha256, input_fingerprint déterministe (idempotence ON CONFLICT DO NOTHING), diff_unified, risk classification ADR-022 L4. |
| 3 | `deb9f985` | fix: `WebDoc.source` → `source_provider` (smoke test crash). |
| 4 | `28d3e95b` | fix: `target_kind` `'vehicle'` → `'vehicle_model'` (constraint `chk_target_kind` allowed values = `vehicle_model | variations | role_map`). |

Spec : `docs/superpowers/specs/2026-04-26-rag-vehicle-scraping-canon.md`.

### 4. Pipeline canon validé end-to-end (avec bémol)

```
$ python3 scripts/rag/rag-propose-vehicle-from-web.py --modele-id 140004 --apply
=== RENAULT CLIO III (modele_id=140004) ===
  web docs=12 engines parsed=14 sources=['fiches-auto', 'wikipedia-fr']
  verdicts : verified=1 partial=13 rejected=4 of 18 types
  proposal clio-iii (vehicles/renault-clio-iii.md):
    base_content_hash : 2d26c6d4d4ab
    proposed_hash     : a4a73b83b1b4
    fingerprint       : 84ecb1fa3a31
    diff              : +36 -109 lines
    risk_level        : high ['removes_many_lines', 'large_diff']
  ✓ INSERT __rag_proposals proposal_uuid=34aa0ff8-40c5-4f84-bf6b-8c41871a9c03
```

Row id=6 dans `__rag_proposals`, status `pending`, expires 2026-05-09.

---

## ⚠️ REGRESSION DÉTECTÉE EN REVIEW (à investiguer)

La proposal `34aa0ff8` **régresse** au lieu d'enrichir. Pour chaque motorisation Clio III (K9K 64ch, 68ch, 86ch, 106ch, etc.), la proposal **retire** :

- `power_rpm`, `couple_nm`, `couple_rpm`, `vitesse_max_kmh`, `zero_a_cent_s`, `boite`, `masse_kg`
- Source `fiches-auto.fr/specs-106-technique-renault-clio-3.php`
- `verification_status: verified` → downgraded en `partial`

**Cause probable** : le fichier RAG `rag/knowledge/vehicles/renault-clio-iii.md` contient déjà ces fields enrichis (sûrement issus de la session bricolage de la PR fermée #3 RAG dont les commits ont été supprimés du repo mais **pas** du disque DEV VPS — les `vehicles/*.md` ne sont pas un repo git séparé, c'est un mount partagé). Le parser maximalist actuel n'arrive pas à reproduire cette richesse depuis les `web-vehicles/*.md` scratch → diff = SUPPRESSION.

**À NE PAS approuver.**

---

## Ce qui reste à faire (priorité)

### P0 — Investiguer la régression proposal

1. **Lire** `/opt/automecanik/rag/knowledge/vehicles/renault-clio-iii.md` actuel (lecture seule) → confirmer ce qu'il contient vraiment
2. **Tracer** d'où viennent les fields enrichis (git log s'il y en a un, sinon suspect : PR RAG #3 fermée mais disk file resté)
3. **Décider** : la source de vérité est-elle ce qui est actuellement sur disque (à conserver) ou doit-elle venir d'un re-scraping propre (à régénérer) ?
4. **DELETE** la row 6 `__rag_proposals` (proposal_uuid=`34aa0ff8-40c5-4f84-bf6b-8c41871a9c03`) :
   ```sql
   DELETE FROM __rag_proposals WHERE proposal_uuid = '34aa0ff8-40c5-4f84-bf6b-8c41871a9c03';
   ```

### P1 — Corriger le parser maximalist du `rag-propose-vehicle-from-web.py`

Le parser doit produire un `motorisations[]` au moins aussi riche que ce qui est actuellement sur disque. Causes possibles à investiguer :

- Le `web-vehicles/*.md` scratch dir actuel a été produit par l'**ancien** scraper (avant le fix `extract_text_generic table-aware` du commit `17644dc5`). Refaire un scraping propre avec le scraper `download-vehicle-motor-corpus.py` actuel pourrait régénérer du scratch plus riche.
- Le matching engine→type_id fait via `match_engine` peut louper sur certains type_ids → à tracer.
- Les regex per-row context (couple/vmax/0-100) peuvent silencieusement échouer.

Test : refaire un scraping fresh sur Clio III (`--apply` sur `download-vehicle-motor-corpus.py`), puis re-run `rag-propose-vehicle-from-web.py --dry-run` et comparer le diff.

### P2 — Vault PR amender ADR-022 ligne 73

ADR-022 ligne 73 dit : *"Stage 2 canary 10 modèles low-profile (PAS Clio/208/Golf)"*. CEO @fafa a directivé que le pilote scraping se fait sur Clio III. Amendement vault PR (5 lignes diff) à rédiger pour ajouter : *"Exception explicite par directive board : un modèle top-trafic peut être inclus en pilote sponsor avec validation board"*. Officialise l'override actuel.

### P3 — Frontend steps 4-7 (PR #185)

Ajouter au frontend R8 (séparément ou en suite de la PR #185 actuelle) :

- **Step 4** `MaintenanceSection` : `__diag_maintenance_operation × __cross_gamme_car_new` (intervalles km/mois par gamme applicable)
- **Step 5** `TopPartsSection` : `__diag_related_parts` triées par `drp_probability`
- **Step 6** `SymptomsSection` : `__diag_symptom` filtrés par `system_id` applicable
- **Step 7** Switches rotation : câbler les 4 tables `__seo_*_switch` (18 430 phrases) sur Howto/AntiErrors/SeoIntro avec rotation déterministe seed=type_id (pattern `brand-bestsellers.service.ts:235-280`)

Ces 4 steps demandent du backend (étendre RPC `build_vehicle_page_payload` ou ajouter un endpoint compagnon `/api/vehicles/types/:typeId/diag-context`) — ~1-2 jours de travail.

### P4 — Writer service

Quand une proposal `__rag_proposals` passe à `status='approved'`, un **writer service NestJS séparé** doit :
1. Lire `proposed_content`
2. Écrire dans `rag/knowledge/<target_path>` via PR signed G3 sur le repo RAG (`ak125/automecanik-rag`)
3. Mettre à jour `status='merged'`, `merged_at`, `merged_commit_sha`

Hors scope cette session. À ouvrir comme PR séparée quand le scraping pipeline sera en confiance (post-P1 fix).

### P5 — Mesure validation finale

Après merge de tous les PRs (frontend + scraping approved + writer), re-mesurer Jaccard sur HTML rendu prod entre 2 motorisations sœurs Clio III :

```bash
# Reproduire la mesure 2026-04-25 (script dans la knowledge)
URL_A="https://www.automecanik.com/constructeurs/renault-140/clio-iii-140004/1-5-dci-26627.html"
URL_B="https://www.automecanik.com/constructeurs/renault-140/clio-iii-140004/1-5-dci-19051.html"
# ... puis tokenize ≥4 chars + jaccard
```

Cible : **Jaccard < 40 %**.

---

## État final session (commit refs)

| Repo | Branche | Statut | Commits | URL |
|---|---|---|---|---|
| `ak125/governance-vault` | `chore/adr-022-accept` | MERGED | `6df8cf6c` | https://github.com/ak125/governance-vault/pull/74 |
| `ak125/nestjs-remix-monorepo` | `feat/r8-html-distinct-render` | OPEN draft | 3 (`9d9ac41e` `e7048c22` `f8cb914b`) | https://github.com/ak125/nestjs-remix-monorepo/pull/185 |
| `ak125/nestjs-remix-monorepo` | `feat/rag-vehicle-scraping-canon` | OPEN draft | 4 (`7642b26f` `6a7f844f` `deb9f985` `28d3e95b`) | https://github.com/ak125/nestjs-remix-monorepo/pull/188 |
| `__rag_proposals` | row id=6 | PENDING — **NE PAS APPROUVER** | proposal_uuid `34aa0ff8-40c5-4f84-bf6b-8c41871a9c03` | DELETE recommandé |

Tag de sécurité créé pendant la session :
- `preserved/adr-027-phase-b-from-r8-branch` → `10e3529a` (commit ADR-027 phase B qui s'était glissé sur la branche R8 par accident multi-agent, préservé pour récupération si besoin)

---

## Antipatterns / leçons à conserver

1. **Le scraping seul ne suffit pas** (ce que la PR fermée #172 prouvait). **Le frontend seul ne suffit pas** (ce que la mesure 70 % estimée prouve). Les deux **ensemble** sont nécessaires pour passer < 40 % Jaccard.

2. **Switches lexicaux ≠ diversité sémantique.** 18 430 phrases en rotation = baisse Jaccard, mais Google fait de la similarité par embeddings — paraphrases d'idées identiques restent détectées comme duplicate. Il faut des **vrais faits différents** par motorisation (couple, vmax, code moteur — pas juste "à changer si cassée" / "à remplacer si défectueuse").

3. **Propose-before-write n'élimine pas les bugs de proposal.** La row 6 inserted est techniquement valide (toutes les contraintes DB respectées, fingerprint OK, diff propre) mais sémantiquement régressive. La review humaine reste indispensable (et aurait été ratée si quelqu'un avait fait UPDATE status='approved' machinalement).

4. **Les fichiers RAG `vehicles/*.md` ne sont pas réversibles via `gh pr close`.** La PR RAG #3 a été fermée + branche supprimée, mais le contenu enrichi écrit sur le disque DEV reste là. Le repo `automecanik-rag` ↔ disque mount n'est pas un git checkout standard. À auditer pour comprendre la sémantique exacte de la sync.

5. **Auto-mode multi-agent peut polluer une branche** (commit ADR-027 phase B s'est glissé dans `feat/r8-html-distinct-render`). Discipline branch-scope reste critique : reset à origin/main au démarrage d'une session, vérifier `git log origin/main..HEAD` avant chaque commit pour repérer les commits orphelins.

---

## Refs

- ADR-022 : `governance-vault/ledger/decisions/adr/ADR-022-r8-rag-control-plane.md`
- Honest debrief Stage 1 : `governance-vault/ledger/knowledge/r8-vehicle-enrichment-stage1-honest-debrief-20260425.md`
- Design spec R8 control plane : `governance-vault/ledger/knowledge/r8-rag-control-plane-design-20260423.md`
- Frontend spec : `nestjs-remix-monorepo/docs/superpowers/specs/2026-04-25-r8-html-distinct-render.md`
- Scraping spec : `nestjs-remix-monorepo/docs/superpowers/specs/2026-04-26-rag-vehicle-scraping-canon.md`

---

_Auteur : session Claude 2026-04-25 → 26, status `draft` — à reviewer par @fafa avant promotion `canon`. Document de fin de session pour reprise sans perte de contexte._
