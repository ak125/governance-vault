# sql-governance-policy.md

> **Version** : 1.0.0
> **Date** : 2026-03-14
> **Statut** : ACTIVE
> **Projet Supabase** : `cxpojprgwgubzjyqzmoq`
> **Pre-requis** : Phase 1 close (change-control-plan.md V1.3.0)

---

## Objectif

6 regles minimales pour eviter la regression des gains Phase 1 (-24 GB indexes, F4 x3600, 7 tables DROP) et maintenir la sante de la base de donnees dans le temps.

Ces regles s'appliquent a **toute modification de schema** : migration SQL, creation de table/index/vue/RPC, suppression d'objet.

---

## Regle 1 — Owner fonctionnel obligatoire

**Toute nouvelle table doit etre rattachee a un domaine fonctionnel (D1-D15).**

| Champ | Valeur attendue |
|-------|----------------|
| Domaine | D1-D15 (cf. domain-map.md V1.4.3) |
| Owner | Service backend ou module responsable |
| Tiering | CRITICAL / HIGH / MEDIUM / LOW |

**Application** :
- Avant toute migration `CREATE TABLE` : identifier le domaine et l'owner
- Mettre a jour `domain-map.md` avec la nouvelle table
- Si aucun domaine ne correspond : creer un nouveau domaine ou justifier l'exception

**Pourquoi** : 7 tables orphelines (0 consumers, 0 refs) ont ete decouvertes en Phase 1 car aucune n'avait d'owner documente.

---

## Regle 2 — Justification index documentee

**Tout nouvel index doit avoir une justification avant creation.**

| Champ | Valeur attendue |
|-------|----------------|
| Table cible | nom qualifie (`public.table`) |
| Colonne(s) | colonnes indexees |
| Query justificative | la requete qui beneficie de l'index |
| EXPLAIN avant | plan sans l'index (Seq Scan attendu) |
| EXPLAIN apres | plan avec l'index (Index Scan attendu) |

**Application** :
- Avant toute migration `CREATE INDEX` : fournir la query justificative
- Verifier l'absence de doublon (index existant couvrant les memes colonnes)
- Apres creation : confirmer `idx_scan > 0` dans les 2 semaines

**Pourquoi** : 25 indexes 0-scan (~23.5 GB) ont ete decouverts en Phase 1, dont des doublons structurels et des indexes supersedes.

---

## Regle 3 — Classification des objets vides

**Tout objet vide (table, vue, RPC) doit etre classe.**

| Classification | Definition | Action |
|---------------|-----------|--------|
| `staging` | Table de transit temporaire (import, migration) | Documenter la date de fin prevue |
| `design-intent` | Table creee pour un futur feature | Documenter le feature et la date cible |
| `orphan` | Objet sans consumer ni plan d'usage | Candidat DROP apres validation |
| `active` | Objet utilise en production | Aucune action |

**Application** :
- Toute table avec `n_live_tup = 0` depuis > 3 mois : classifier
- Objets `orphan` : planifier DROP dans le prochain cycle de maintenance
- Objets `design-intent` sans activite > 6 mois : reclasser en `orphan`

**Pourquoi** : 2 vues phantom et 3 tables vides (products, categories, messages) ont persiste pendant des mois sans que personne ne sache si elles etaient prevues ou abandonnees.

---

## Regle 4 — Controle periodique ANALYZE / VACUUM

**Les tables critiques doivent avoir des stats planner a jour.**

| Seuil | Action |
|-------|--------|
| `last_autoanalyze > 3 mois` sur table > 100 MB | `ANALYZE public.<table>` immediat |
| `dead_pct > 20%` ou `n_dead_tup > 1M` | Evaluer `VACUUM (ANALYZE)` |
| `seq_tup_read` en croissance > 50% sur 1 mois | Investiguer (nouveau query pattern ou index manquant) |

**Application** :
- Executer les requetes M3 et M4 de `phase-2-monitoring-rpc.md` selon le calendrier (hebdomadaire S1-S2, puis mensuel)
- Tables CRITICAL (pieces_*, ___xtr_msg) : verifier `last_autoanalyze` a chaque cycle

**Pourquoi** : F4 etait a 5884ms uniquement parce que les stats planner de `pieces_relation_criteria` (36 GB) etaient obsoletes depuis 6 mois. Un simple ANALYZE a corrige le probleme (→ 1.6ms, x3600).

---

## Regle 5 — Revue trimestrielle des vues et RPC

**Toute vue ou RPC non utilisee doit etre revue trimestriellement.**

| Verification | Methode |
|-------------|---------|
| Vue : consumers actifs | `grep -r "v_<nom>" backend/src/` + verification SDK/RPC |
| RPC : appels recents | `grep -r "rpc('<nom>'" backend/src/` + verification frontend |
| Index : scans recents | Requete M6 (`idx_scan = 0` sur > 1 MB) |

**Application** :
- Trimestre : lister vues avec 0 consumers, RPC avec 0 appels code, indexes avec 0 scans
- Pour chaque candidat : validation multi-couche (grep + SQL dependencies + schema constraints)
- Ne jamais DROP sur la seule base de `idx_scan = 0` ou `grep = 0 results`

**Pourquoi** : `idx____xtr_msg_msg_parent_id` avait 0 scans sur la fenetre de stats mais etait utilise par `contact.service.ts` (discovery par grep). Le 0-scan seul n'autorise jamais un DROP.

---

## Regle 6 — Doublons structurels traces

**Les doublons structurels (tables, indexes, colonnes) doivent etre documentes et arbitres.**

| Type de doublon | Exemple Phase 1 | Action |
|----------------|----------------|--------|
| Table doublon | `__cross_gamme_car_new2` vs `__cross_gamme_car_new` | Comparer les contenus, DROP le subset |
| Index doublon | `idx_prt_piece_id` vs `idx_prt_piece_id_v2` | Verifier lequel est actif, DROP l'autre |
| Index supersede | Index (A) couvert par index (A, B) | Verifier les queries single-column, DROP si couvert |
| Backup table | `__rag_knowledge_backup_20260222` | Supprimer apres 30 jours si original intact |

**Application** :
- Avant toute creation d'index : verifier les indexes existants sur la meme table
- Nommer les indexes de maniere explicite : `idx_<table>_<colonnes>` (pas de suffixes arbitraires `_v2`, `_new`)
- Les tables `_backup_*` et `_old` doivent avoir une date d'expiration

**Pourquoi** : 9 des 25 indexes 0-scan supprimes en Phase 1 etaient des doublons ou des supersedes (~8 GB recuperes).

---

## Synthese

| # | Regle | Frequence | Document de reference |
|---|-------|-----------|----------------------|
| R1 | Owner fonctionnel | A chaque CREATE TABLE | domain-map.md |
| R2 | Justification index | A chaque CREATE INDEX | change-control-plan.md (principes) |
| R3 | Classification vide | Mensuelle | table-remediation-matrix.md |
| R4 | ANALYZE / VACUUM | Mensuelle (S1-S2 hebdo) | phase-2-monitoring-rpc.md (M3, M4) |
| R5 | Revue vues/RPC | Trimestrielle | phase-2-monitoring-rpc.md (M6) |
| R6 | Doublons traces | A chaque CREATE INDEX | schema-governance-matrix.md |

---

## Refs croisees

| Document | Version | Role |
|----------|---------|------|
| domain-map.md | V1.4.3 | 15 domaines, rattachement tables |
| schema-governance-matrix.md | V1.2.0 | Matrice objet-par-objet |
| change-control-plan.md | V1.3.0 (gele) | Principes d'execution Phase 1 |
| phase-2-monitoring-rpc.md | V1.0.0 | 6 requetes monitoring + audit RPC |
| final-exec-summary.md | V1.4.0 | Bilan Phase 1 + risques + baseline T0 |
