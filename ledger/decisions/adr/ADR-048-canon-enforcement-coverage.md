---
id: ADR-048
title: "Canon Enforcement Coverage Audit"
status: proposed
date: 2026-05-07
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1]
related_incidents: []
reviewed_by: ""
---

# ADR-048: Canon Enforcement Coverage Audit

## Contexte

Suite à la refondation MOC (PR-1 #185, PR-2 #186, PR-3 #187 mergées 2026-05-07) qui a supprimé les duplications structurelles dans le vault, instauré un glossaire `canon`, et déployé un drift detector mécanique, l'**audit honnête de la robustesse du canon architectural** a révélé un déséquilibre critique :

- Le **vault** (gouvernance opérationnelle, supposé miroir) dispose désormais d'enforcement mécanique solide : hooks signés G2/G3, weekly-lint 9 checks, pre-commit/pre-push, schémas frontmatter validés, drift detector MOC.
- Le **canon architectural** (`.spec/00-canon/` du monorepo, désigné par G1 + ADR-015 §5 comme source-of-truth applicative) dispose d'un enforcement **asymétrique et lacunaire** :
  - `gamme-md-schema.md` → enforced via Zod (ADR-039 LIVE) ✓
  - `role-matrix.md` → enforced via @repo/seo-roles + 4 layers (ADR-040 LIVE) ✓
  - `architecture.md`, `phase2-canon.md`, `pipeline-phases.md`, `prompt-registry.md`, `repo-map.md` → **prose sans enforcement** ✗
  - `db-governance/*` → mixte (récemment modifié 2026-05-06, partiellement enforced)

**Audit factuel des dates de modification au 2026-05-07** :
- `architecture.md` : 2026-02-19 (Q1)
- `gamme-md-schema.md` : 2026-03-11
- `role-matrix.md` : 2026-03-14
- `phase2-canon.md` : 2026-03-14
- `prompt-registry.md` : 2026-03-14
- `pipeline-phases.md` : 2026-03-14

À comparer à : ADR-047 créé le 2026-05-07. **Le canon est plus vieux que la moitié des ADRs qui prétendent y conformer.**

**Risques identifiés** :
1. **Drift silencieux canon → code** : aucun gate ne vérifie qu'un changement de schéma applicatif est répercuté dans `.spec/00-canon/` (ou inversement)
2. **Single-signer SPOF** : Fafa seul signe G1, ADR-015, modifications canon — pas de peer review automatique, pas d'invariant cross-repo
3. **Fraîcheur non vérifiée** : prose-only canon files peuvent rester stales arbitrairement longtemps sans signal
4. **Asymétrie enforcement** : paradoxe où le miroir (vault) est mieux gardé que la source (canon)

Trajectoire saine déjà observable : Zod (ADR-039), seo-roles (ADR-040), dep-cruiser planifié (memory `roadmap-p0-p3-canon-repos-20260501` "P3 dep-cruiser"). Mais **incomplète et non systématisée**.

## Décision (TBD)

À élaborer dans une PR de finalisation. Direction proposée :

1. **Audit fichier-par-fichier** de `.spec/00-canon/*` :
   - Quel artefact downstream consomme ce fichier ?
   - Quelle forme d'enforcement mécanique existe (Zod / TS package / dep-cruiser / runtime guard) ?
   - Date de dernière modification vs ADRs récents qui le citent ?
   - Y a-t-il drift observé entre ce fichier et le code en production ?

2. **Extension d'enforcement aux fichiers prose-only dignes** :
   - `architecture.md` → dependency-cruiser pour invariants module/import
   - `pipeline-phases.md` → tests d'intégration sur les transitions de phase
   - `repo-map.md` → généré automatiquement depuis le filesystem (drift = diff)
   - `prompt-registry.md` → schema YAML/JSON pour les prompts canoniques

3. **Cron `canon-freshness-check`** comparable au weekly-lint vault, dédié au canon :
   - Pour chaque fichier `.spec/00-canon/*`, vérifier `last_mod >= seuil`
   - Pour chaque ADR récent (< 6 mois), vérifier qu'aucun canon file qu'il référence n'est plus vieux que lui de >90j

4. **Considérer un signer secondaire** pour les modifications canon (peer review humaine ou validation cross-repo automatique).

5. **Cross-repo invariant vault ↔ monorepo** : un check qui valide que toute mention de `.spec/00-canon/X` dans un ADR vault correspond à un fichier réel dans le monorepo, et inversement.

## Options Considérées (TBD)

À élaborer dans une PR de finalisation. Au minimum :
- **Option A** : Audit one-shot + ADR-stack par gap → le pattern "9 PRs canon SEO" (memory `seo-roles-canon-shipped-20260505`) appliqué au canon technique global
- **Option B** : Cron `canon-freshness-check` léger + rappels manuels → moins invasif, signal plus que enforcement
- **Option C** : Migration progressive prose → schémas exécutables (Zod / dep-cruiser / runtime guards) → continue la trajectoire ADR-039/ADR-040 sans casser
- **Option D** : Hybride A+C (audit puis migration progressive) → recommandation initiale à challenger

## Conséquences (TBD)

### Positives attendues
- Détection automatique de toute divergence canon ↔ code en production
- Fin du paradoxe "miroir mieux gardé que source"
- Onboarding contributeurs externes facilité (canon vérifiable, pas juste prose à croire)
- Audit-trail mécanique pour les modifications canon (au-delà de la signature Fafa seul)

### Négatives attendues
- Coût initial d'audit fichier-par-fichier (estimé 1-2 semaines)
- Charge récurrente de cron `canon-freshness-check` à maintenir
- Friction sur les modifications canon urgentes (gate supplémentaire)

### Neutres
- Aucun impact sur `governance-vault/` (déjà enforced)
- Aucun impact sur les ADRs qui référencent G1 — leur autorité demeure inchangée

## Critères de Succès (à valider en finalisation)

- [ ] **C1 — Audit complet** : tous les fichiers `.spec/00-canon/*` ont un statut explicite (enforced / prose-only / deprecated)
- [ ] **C2 — Enforcement étendu** : au moins 80% des fichiers prose-only dignes ont un enforcement mécanique ajouté
- [ ] **C3 — Cron freshness** : `canon-freshness-check` LIVE et reporting hebdo
- [ ] **C4 — Cross-repo invariant** : check vault ↔ monorepo en CI

## Implémentation

À planifier dans une PR de finalisation après acceptation de cette ADR (proposed → accepted).

**Trigger** : cette ADR est **proposed** au 2026-05-07. Deadline draft de finalisation = 2026-05-21 (sous 14j). Si non finalisé sous 14j, alerter via issue GitHub.

## Suivi

- **Deadline finalisation décision** : 2026-05-21 (T+14j)
- **Issue GitHub liée** : à créer immédiatement après merge de cette PR (titre : `Canon Enforcement Coverage Audit (ADR-048 draft)`)
- **Owner** : Fafa
- **Reviewers potentiels** : à identifier en finalisation (peer review G3)

---

*Proposé le: 2026-05-07*
*Statut: proposed (cadre, contenu détaillé en finalisation)*
