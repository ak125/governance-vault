---
category: knowledge
doc_family: knowledge
source_type: lessons-learned
title: Vault PR — self-review workflow obligatoire avant admin merge
slug: vault-self-review-workflow
schema_version: "1.0.0"
lang: fr
updated_at: "2026-05-04"
updated_by: "@fafa"
related_adr: []
related_prs:
  - "ak125/governance-vault#146"
related_knowledge:
  - "single-maintainer-merge-pattern"
  - "sandbox-merge-auto-rule-20260428"
  - "claude-code-plugin-enablement-policy-20260504"
status: current
tags:
  - governance
  - vault
  - merge
  - review
  - self-review
  - canon
---

# Vault PR — self-review workflow obligatoire avant admin merge

> Session 2026-05-04. Formalisation d'un filtre **sémantique** pré-merge sur
> les PRs `governance-vault` ouvertes par Claude, en complément des 5 gates CI
> structurels (G2/G3/G4/Wikilinks/V1). Pattern éprouvé sur PR #146 où la
> self-review a détecté 2 erreurs factuelles qu'aucun gate CI ne pouvait voir.
> Étend `single-maintainer-merge-pattern` (admin-merge solo) et
> `sandbox-merge-auto-rule-20260428` (5 conditions auto-merge).

## 1. Contexte / problème

La branch protection `main` du vault est strictement configurée (PR #91,
ADR-015) :

- 5 status checks requis : G2 (Zero Orphelin), G3 (Commits Signés), G4 (CI
  read-only), Broken Wikilinks, No V1 Paths (ADR-015)
- `require_code_owner_reviews: true`
- `enforce_admins: true` (depuis 2026-05-02)
- Solo maintainer `@ak125` ne peut pas s'auto-approver (limite GitHub)

Le merge nominal d'une PR Claude-ouvert est donc :

```bash
git push  # → CI 5 gates → BLOCKED par REVIEW_REQUIRED
gh pr merge <N> --admin --squash  # bypass review-gate (status checks restent)
```

**Gap** : `--admin` retire la review humaine sans la remplacer. Or les 5 gates
CI couvrent l'**intégrité structurelle** (orphelins, signatures, paths
interdits) mais **pas** la qualité **sémantique** :

- Slug typo, frontmatter incomplet/incohérent
- Chiffres faux (« 27 plugins » alors que le settings.json en montre 24/28)
- Math incohérent (« 1500–3800 » quand 8×3×80 = 1920)
- Overclaim (« 100 % couvert », « tout scanné », « complet »)
- Contradiction silencieuse avec un ADR/rule existant
- Wikilink pointant à un fichier qui existe mais ne traite pas du sujet
- Précédent oublié → cross-refs cassés

Sans filtre sémantique, ces erreurs deviennent canon et propagent vers PROD
(read-only mirror) + AI-COS (lecture HTTPS GitHub).

**Précédent éprouvé (PR #146, 2026-05-04)** : self-review pré-merge a flag
2 erreurs factuelles :
- Décompte plugins « 27 » → réalité 24 actifs sur 28 listés
- Math estimation tokens « 1500–3800 » → corrigé à 1920–3840

Les deux corrigées par commit `9a1c063` AVANT merge — évitant un revert ou
un patch correctif post-merge.

## 2. Pattern canon

```
1. Claude push branche → CI 5 gates
2. CI green
3. ⚠️ AVANT `gh pr merge --admin` :
   → Claude exécute la 8-item checklist (§3) sur la PR diff
   → Output : verdict APPROVE | FIX_NEEDED + liste issues
4. Si FIX_NEEDED :
   → fix dans commit séparé (pas --amend, pas force-push)
   → push, re-CI, re-checklist
5. Si APPROVE :
   → reporter le verdict explicitement à l'utilisateur
   → attendre confirmation user (« go », « merge », « fusionne »)
   → `gh pr merge <N> --admin --squash`
```

Le self-review n'est **pas** un substitut à la review humaine — c'est une
**couche additionnelle** qui rattrape les erreurs sémantiques avant que le
user ne les voie. L'utilisateur garde le dernier mot via le `go` final.

## 3. Checklist 8 items (canon)

Source unique de la checklist. Tout déclencheur (memory rule, futur skill,
hook, doc) doit pointer ici, pas dupliquer.

### 3.1 Frontmatter

- `slug` cohérent avec filename sans suffixe date
- `schema_version`, `lang`, `status`, `category`, `doc_family` alignés sur
  les précédents de même type (knowledge ↔ knowledge, ADR ↔ ADR)
- `updated_at` = date du dernier edit (pas de la création initiale)
- `related_adr`, `related_prs`, `related_knowledge` à jour
- `tags` minimum 3, pertinents

### 3.2 Factuel

Tout chiffre cité doit être vérifiable par grep/count en une commande :

- Compter les entrées d'un settings.json, d'une migration, d'une table
- Vérifier un nombre de PRs/commits/lignes
- Confirmer une date par `git log` ou métadonnée externe

Anti-pattern : reprendre un chiffre vu dans la conversation sans le
revérifier au moment du commit.

### 3.3 Math

Toute estimation chiffrée doit être recalculable et bornée correctement :

- Bornes basse et haute alignées avec la formule (ex : `8×3×80 = 1920`,
  pas 1500)
- Pas de précision factice (`~1923,7 tokens` est faux ; `~1900` honnête)
- Si l'estimation est ouverte, dire « ordre de grandeur » plutôt que donner
  des bornes précises

### 3.4 Wikilinks

- Chaque `[[ref]]` cible un fichier réel (G2 le force structurellement)
- La référence est **sémantiquement pertinente** (un wikilink valide vers
  un fichier hors-sujet passe G2 mais est mauvais)
- Pas de wikilink vers une page deprecated/superseded sans le signaler

### 3.5 Anti-patterns de formulation

Bannir (ou justifier explicitement) :

- « 100 % », « tout », « complet », « aucun », « jamais », « toujours »,
  « impossible » sans coverage manifest (cf. AEC `rules-agent-exit-contract`)
- « Auto-corrigé », « auto-fixé », « auto-validé » → utiliser
  `PARTIAL_COVERAGE`, `REVIEW_REQUIRED`, `VALIDATED_FOR_SCOPE_ONLY`
- Présenter contournable comme impossible (false security)

### 3.6 Cohérence canon

Avant d'affirmer une règle/décision/contrainte, grep les ADR + rules
existants pour absence de contradiction :

```bash
grep -r "<keyword>" /opt/automecanik/governance-vault/ledger/decisions/adr/ \
                   /opt/automecanik/governance-vault/ops/rules/
```

Si contradiction → soit la note est fausse, soit elle supersède un canon
existant et doit le marquer explicitement (deprecate/supersede pattern).

### 3.7 Précédent

Si la note est suite logique d'une autre :

- `related_knowledge` ou `related_adr` frontmatter renseigné
- §Références cross-link bilatéral (la précédente devra peut-être être
  amendée pour pointer vers la nouvelle)

### 3.8 MOC

Lien ajouté dans le bon MOC (G2 zero-orphelin force la présence d'un lien) :

- `MOC-Knowledge.md` pour knowledge
- `MOC-Decisions.md` pour ADR
- `MOC-Rules.md` pour rule
- `MOC-Incidents.md` pour incident
- `MOC-Policies.md` pour policy

Vérifier la **section** dans le MOC (Architecture / Patterns / Gouvernance /
SEO / etc.) — le placement détermine la trouvabilité future.

## 4. Anti-patterns du workflow lui-même

- ❌ « C'est un petit changement, on skip le self-review » → si le diff vaut
  un commit, il vaut une checklist 5-min.
- ❌ Self-review en parallèle de la rédaction (biais de confirmation).
  Faire la review **après** que le commit est figé sur la branche.
- ❌ Auto-trigger merge sur verdict APPROVE sans le `go` user. Le user reste
  le dernier oeil — la self-review réduit son coût d'attention, ne le
  remplace pas.
- ❌ Étendre la checklist en ad-hoc dans une PR (« je rajoute item 9 pour
  cette PR »). Toute extension passe par une nouvelle PR vault qui amende
  ce canon.
- ❌ Skip la checklist parce que « Claude vient de relire en écrivant ».
  L'écriture et la review ont des biais inverses — ne pas mélanger.

## 5. Hors scope (intentionnel)

- **Branch protection** : non touchée. CODEOWNERS strict + 5 gates +
  enforce_admins restent l'arbitrage forçant la review.
- **Bot auto-approve** (CodeRabbit, Optibot, ou GitHub App custom) : non
  intégré. Hors contexte vault-specific (factuel sur settings.json, etc.).
- **Hook PreToolUse `gh pr merge`** : non créé. Bricolage qui patche le
  harness pour forcer un comportement déjà couvert par memory + canon.
- **Skill `vault-self-review/SKILL.md`** : non créé. Wrapper inutile sur ce
  canon qui sert de source unique. Claude lit ce fichier et applique.

## 6. Métrique

Mesure empirique : sur les 5 prochaines PRs vault Claude-ouvertes,
journaliser dans la PR description :

- Verdict initial self-review : `APPROVE` | `FIX_NEEDED:N`
- Erreurs détectées (catégorie : factuel / math / cohérence / etc.)
- Temps self-review (min)

Objectif : ≥ 1 erreur sémantique détectée toutes les 3 PRs (sinon la
checklist est sur-engineered ou le rédacteur est trop conservateur ; à
revoir).

## 7. Références

- `single-maintainer-merge-pattern.md` — le pattern admin-merge solo qu'on
  étend
- `sandbox-merge-auto-rule-20260428.md` — les 5 conditions auto-merge ;
  ce workflow ajoute la condition « 6. self-review APPROVE » pour scope vault
- `claude-code-plugin-enablement-policy-20260504.md` — précédent PR #146
  (les 2 erreurs détectées et fixées avant merge)
- `branch-protection-main-20260502` (memory) — `enforce_admins: true`
- `rules-agent-exit-contract` — AEC v1.0.0 (statuts autorisés, anti-overclaim)
- ADR-015 — vault SoT canonique
- Memory associée : `feedback_vault_self_review_before_admin_merge.md`
  (path : `~/.claude/projects/-opt-automecanik-app/memory/`)
