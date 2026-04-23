---
type: audit-trail
date: 2026-04-23
session: seo-kp-alias-maitre-cylindre-de-frein
related_rules: ["R-SEO-KW-05"]
related_pr: ["ak125/nestjs-remix-monorepo#128"]
status: closed
---

# Audit Trail: R-SEO-KW-05 alias canonicalization — maitre-cylindre-de-frein

## Contexte

Déviation de la session R8 vehicle refactor (PR #126 Phase 1). L'utilisateur
a ouvert `.claude/prompts/R1_ROUTER/Keyword Stats 2026-04-23 at 16_53_56.csv`
dans l'IDE. L'assistant a interprété l'ouverture comme une demande implicite
de traiter le CSV via le pipeline canonique KP Google Ads.

**Correction de cap** : l'utilisateur a signalé la déviation, demandé de
documenter le détour dans le vault et de reprendre R8.

## Travail réalisé sur la déviation

### Pipeline KP exécuté (canon R-SEO-KW)

- CSV source : 314 keywords Google Ads KP pour gamme `maitre-cylindre-de-frein`
  (pg_id=258)
- Script : `scripts/seo/import-gads-kp.py --pg-id 258 --dry-run --suggest-aliases`
- Résultat dry-run initial : 312 dédup → 301 pertinents + 9 `no_core_match`
  candidats (vol cumulé 900/mois = **2.87%** rejection rate)

### Revue des 9 suggestions (R-SEO-KW-05)

Sous le seuil canon de 5%, pas d'obligation de review — mais `--suggest-aliases`
obligatoire. 8 acceptés, 1 rejeté :

| Alias | Vol | Décision | Motif |
|---|---|---|---|
| `cylindre de frein` | 500 | ✅ | Synonyme principal courant |
| `cylindre maitre` | 50 | ✅ | Inversion valide |
| `maitres cylindres` | 50 | ✅ | Pluriel |
| `master cylindre` | 50 | ✅ | Anglicisme FR courant |
| `master cylindre de frein` | 50 | ✅ | Idem |
| `met cylindre` | 50 | ✅ | Normalisation Google Ads « maître »→« met » |
| `met cylindre de frein` | 50 | ✅ | Idem |
| `met cylindre frein` | 50 | ✅ | Idem |
| `maitre frein` | 50 | ❌ | Trop lâche — peut matcher d'autres pièces frein |

### Impact mesuré

- YAML `config/rag-alias-expansions.yaml` : 3 → 11 aliases (commit `1cb3d60b`)
- Post-YAML dry-run : rejection rate **2.87% → 0.96%** (3/312)
- Import réel exécuté : 309 rows UPSERT, 0 erreur
- DB `__seo_keywords` pg_id=258 : 313 rows (inchangé — les 8 aliased KW étaient
  déjà présents depuis imports antérieurs ; le YAML les formalise désormais
  canoniquement pour les futurs imports)

## Evidence

- PR monorepo : https://github.com/ak125/nestjs-remix-monorepo/pull/128
- Commit : `1cb3d60b feat(seo): formalize 8 aliases for maitre-cylindre-de-frein`
- Branche : `seo/kw-import-maitre-cylindre-de-frein`
- Script : `scripts/seo/import-gads-kp.py`

## Leçons et feedback

1. **Ouvrir un fichier dans l'IDE ≠ demande implicite de traitement.** L'agent
   doit demander confirmation avant de pivoter hors de l'objectif en cours,
   même en auto mode, quand le nouveau scope n'est pas nommé explicitement.
2. Règle canon existante confirmée : `feedback_no_autoescalation_after_single_go`
   — un « fais le » couvre uniquement le scope nommé. L'ouverture d'un fichier
   ne constitue pas un scope nommé.

## Statut objectif principal

Session R8 vehicle page refactor :
- Phase 1 **livrée** : PR #126 (extraction types/transform/schema/constants,
  branch `refactor/r8-vehicle-route-split`, 2020 → 1559 lignes)
- Phase 2 **à démarrer** : découpage du composant `VehicleDetailPage`
  (1180 lignes) en sous-composants par `data-section="S_*"` (13 sections)

## Coverage Manifest

- scope_requested: refactor R8 vehicle page (Phase 1 complète, Phase 2 en cours)
- scope_actually_scanned: deviation KP import documentée ci-dessus
- files_read_count: 4 CSV inspectés, 2 scripts, 1 YAML config
- excluded_paths: autres CSV R1_ROUTER (13 CSV non traités dans cette session)
- unscanned_zones: batch KP multi-gammes (178 gammes restantes per memory
  kw-pipeline-status)
- corrections_proposed: 8 aliases → 8 appliqués (validation humaine « ok »)
- validation_executed: dry-run avant + après YAML update, DB verification post-import
- remaining_unknowns: aucune (scope fermé sur cette gamme)
- final_status: SCOPE_SCANNED
