---
type: rules-document
status: canon
scope: agents
updated: 2026-11-01
related_adrs:
  - ADR-031
  - ADR-121
related_incidents: []
related_rules:
  - rules-engineering-quality
  - rules-governance-process
  - rules-ai-antipatterns
---

# Rules — Agent Exit Contract (AEC)

> **Source de vérité canonique** — règles obligatoires de sortie pour tout agent, run, audit ou analyse.
> **Version** : 1.1.0 (amendée par ADR-121, 2026-11-01) | **Status** : CANON
> **Taxonomie** : règle transverse — s'applique avant les règles spécifiques de domaine (T*, G*, Q*, AP*).

La **source canonique** est ce document dans le governance vault. Les copies applicatives sont les dérivées déclarées dans le manifeste de distribution ; leur contrôle repose sur son hash SHA-256 (voir §« Distribution canonique »).

---

## Règles fondamentales

1. **Aucune correction sans mandat humain explicite.** Une demande explicite de correction autorise son exécution et sa vérification dans le périmètre demandé ; cet accord ne se redemande pas à chaque étape. Une demande de scan, d'analyse ou de proposition seule n'autorise pas les modifications. Le mandat ne lève aucune permission, validation spécifique ni restriction de fusion, de publication ou de déploiement ; une action qui le dépasse exige un accord distinct (ADR-121 D1).
2. **Jamais d'overclaim.** Les phrases "tout scanné/vérifié/corrigé", "100% couvert", "aucun problème", "audit complet" (FR/EN) sont **interdites** sans coverage manifest.
3. **Séparation obligatoire** de 5 états dans tout rapport : `scan` | `analysis` | `correction (proposée ou appliquée avec autorisation)` | `validation` | `verdict`.

## Statuts autorisés / interdits

| Autorisés | Interdits |
|-----------|-----------|
| `PARTIAL_COVERAGE` | `PROJECT_FULLY_SCANNED` |
| `SCOPE_SCANNED` | `ALL_FIXED`, `COMPLETE`, `DONE` |
| `REVIEW_REQUIRED` | `NO_ISSUES`, `PATCH_APPLIED` |
| `VALIDATED_FOR_SCOPE_ONLY` | `AUTO_FIXED` |
| `INSUFFICIENT_EVIDENCE` | |

Verdict par défaut = `PARTIAL_COVERAGE` ou `INSUFFICIENT_EVIDENCE`, jamais `COMPLETE`.

Pour déclarer `SCOPE_SCANNED` : fournir nombre exact de fichiers lus, répertoires parcourus, exclusions, et au moins 1 evidence par conclusion.

## Coverage manifest obligatoire

Tout run/audit DOIT produire :

```
scope_requested / scope_actually_scanned / files_read_count
excluded_paths / unscanned_zones (OBLIGATOIRE même si vide)
corrections_proposed / corrections_applied (si autorisées) / validation_executed
remaining_unknowns (OBLIGATOIRE) / final_status (statut autorisé)
```

`corrections_applied` doit être vide/absent sans mandat humain explicite. Si des corrections ont été appliquées, indiquer le mandat, les fichiers ou objets concernés, les vérifications exécutées et leurs limites. Un changement appliqué n'est pas à lui seul un résultat validé.

## Reformulation obligatoire

- "Tout scanné" → "Scan du périmètre X terminé"
- "Tout corrigé" → selon l'état réel : "N recommandations proposées, non appliquées" ou "N corrections autorisées appliquées sur X ; validations Y ; limites Z"
- "100% couvert" → "Couverture estimée à N% sur le périmètre X"

## Decision Dossiers

Inclure Section 13 (Coverage Manifest) + Section 14 (Exit Conditions). Le résultat des conditions de la section 14 peut être `PASS` si elles sont toutes vérifiées ; il ne remplace pas le `final_status` AEC autorisé et borné au périmètre.

---

## Distribution canonique

La source de référence est `ledger/rules/rules-agent-exit-contract.md` dans le vault. Les fichiers applicatifs sont des dérivés ; ils ne s'éditent pas directement.

1. **Manifeste généré** : `99-meta/canon-hashes.json`, clé `aec`, produit par `_scripts/compute-canon-hashes.py --write` et contrôlé par `--check`. Les copies se comparent à `distribution_sha256` (texte privé de son frontmatter). La version et la liste des consommateurs se déclarent dans le générateur.
2. **Révision** : PR signée selon `ledger/rules/rules-vault.md` (G3, G4), ADR pour tout changement de décision, fusion par l'owner, manifeste régénéré dans la même PR.
3. **Notification** : après la fusion, `canon-publish.yml` vérifie les hashes et émet l'événement `canon-updated` vers les dépôts consommateurs. Il ne copie aucun fichier et n'ouvre aucune PR.
4. **Projection monorepo** : `_scripts/sync_canon_mirrors.py` (`--dry-run`, `--check`, `--write`) écrit les copies du monorepo ; `_scripts/cron-sync-canon-mirrors.sh` peut préparer une PR signée, voir `ops/runbooks/sync-canon-mirrors.md`. Côté monorepo, `canon-sync.yml` ouvre ou met à jour la PR `canon-sync/auto`, étiquetée `canon-sync`, sans auto-fusion. Les copies des dépôts wiki et raw se mettent à jour par une PR ordinaire. Toute PR de resynchronisation se fusionne par l'owner, comme toute PR ; aucun label n'autorise une fusion (ADR-121 D5).
5. **Vérification consommateur** : chaque dépôt consommateur exécute `agent-exit-contract-hash.yml`, qui compare ses copies au manifeste du vault. Une notification ne prouve ni la mise à jour d'une copie, ni l'exécution d'un cron, ni un déploiement.

## Versionnage

Bump majeur (X.0) = nouvelle règle ou statut interdit ajouté. Bump mineur (X.Y) = clarification / précision. Bump patch (X.Y.Z) = typo / formatting.

| Version | Date | Changements |
|---|---|---|
| 1.0.0 | 2026-04-28 | Canonisation depuis copies orphelines monorepo + seo-batch (drift constaté empiriquement). Ajout §"Distribution canonique". |
| 1.0.1 | 2026-05-04 | Patch path : copies monorepo relocalisées de `.claude/rules/` vers `.claude/canon-mirrors/` pour ne pas alourdir le contexte projet Claude Code (~2.5K tokens/tour). Aucune règle modifiée, hash recalculé. |
| 1.1.0 | 2026-11-01 | ADR-121 : règle 1, le mandat explicite couvre son exécution dans ses limites ; corrections proposées et appliquées distinguées (règle 3, manifeste, reformulation) ; `PASS` de dossier distinct du `final_status` ; §« Distribution canonique » réécrite selon les mécanismes réels, auto-fusion `canon-sync` retirée ; en-tête aligné sur la version. |

## Référence

- ADR-031 — architecture de contenu à quatre couches (`ledger/decisions/adr/ADR-031-four-layer-content-architecture.md`)
- ADR-121 — mandat, revue, décision et fusion : actes distincts
- `rules-engineering-quality.md` (Q1-Q4 — solution structurelle vs bricolage)
- `rules-ai-antipatterns.md` (AP-* — anti-patterns IA)
- `rules-governance-process.md` (G5-G8 — processus)
