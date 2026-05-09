---
date: 2026-05-09
type: audit-trail
related: [ADR-057, ADR-036, ADR-038, ADR-039, ADR-047, ADR-054, ADR-055, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-09 — ADR-057 marketingskills adoption pattern

## What

Ouverture ADR-057 dans [[MOC-Decisions]] pour formaliser l'unique pattern admis
d'adoption du repo public `coreyhaines31/marketingskills` (40 skills Agent SDK,
MIT, 27.5k★, v1.10.0 — 2026-05-06) ainsi que de tout repo de skills tiers
analogue à venir.

L'ADR définit :

- **D1** : pattern wrapper canon-bound — upstream read-only via
  `npx skills add --skill <NAME>`, wrapper local mince ≤ 30 lignes sous
  `.claude/skills/<categorie>/auto-<skill>/SKILL.md`, FR + brand-voice + RGPD.
- **D2** : cycle 5 étapes (gouvernance avant code, attente fenêtre branche,
  PR pilote unique, observabilité 30j, gate T+30 explicite).
- **D3** : skill pilote sélectionné = `customer-research` (méthodologie pure,
  zéro génération de copy, comble blocage maturation `marketing-voice.md`).
- **D4** : 17 skills explicitement bannis (4 doublons SEO, 2 conflits
  copywriting canon, 1 social-content doublon, 4 hors modèle SaaS, 1 ASO,
  1 video, 4 hors phase/stratégie).
- **D5** : 6 anti-patterns codifiés (bulk install, fork local, patch upstream,
  skill custom clone, batch multi-skills, adoption skill 🔴).
- **D6** : branchement gouvernance existante (ADR-036, ADR-038, ADR-039, ADR-054).

Auto-application de la convention ADR-054 : tout ADR vault destiné au merge
génère par défaut une entrée audit-trail (méta-application, cf. ADR-054 D2).

## Why

Le repo `marketingskills` propose 40 skills marketing à grande valeur
méthodologique. Sans cadre formel, l'adoption hypothétique génère 4 risques
empiriquement documentés dans le plan source
(`/home/deploy/.claude/plans/verifier-skip-to-jaunty-zebra.md`) :

1. **Pollution canon** par install bulk (17 doublons écraseraient le
   pipeline SEO + brand voice + agents G1 marketing).
2. **Régression FR** : 14 skills sont des générateurs de copy EN — sortie
   EN par défaut violerait `feedback_french_only_for_content.md`.
3. **Bypass brand-compliance** : copywriting / social externes
   court-circuitent `multi-channel-copywriter` + `brand-compliance-gate`
   (chaîne canon ADR-036).
4. **Drift fork** : forker upstream + FR-iser localement crée une dette de
   maintenance permanente sans lien remote.

Sans ADR formalisée, l'adoption — même partielle — du repo n'est pas LIVE
au sens canon (cf. mémoire DEV `feedback_canon_rule_live_iff_adr_accepted.md` :
"Chantier `LIVE` ssi ADR.status=accepted. Code shippé ≠ canon LIVE").

L'ADR fixe également une discipline anti-régression : la liste explicite des
17 skills bannis sert de référence pour les futures revues — toute PR les
introduisant doit être refusée.

## How (process appliqué dans cette session)

1. **Investigation préalable** : 2 agents Explore en parallèle ont cartographié
   (a) les 26 skills locaux + 17 SEO, (b) l'infrastructure backend SEO seo-v9
   + workspace marketing Phase 1 + état CRO/analytics/email/referral.
2. **Plan rédigé** : `/home/deploy/.claude/plans/verifier-skip-to-jaunty-zebra.md`
   avec matrice 40 skills + verdict 🟢🟡🟠🔴 + précautions transversales.
3. **Décision utilisateur** : "meilleure approche, pas de bricolage" → pivot
   vers pattern wrapper canon-bound + 1 skill pilote (vs adoption en bloc ou
   fork-FR).
4. **Worktree vault** : `/tmp/vault-adr-057-marketingskills` depuis
   `origin/main` pour ne pas perturber les 15+ branches concurrentes.
5. **Vérification numérotation** : ADR-057 libre (056 occupé par R7,
   trous 051/052/054 sur drafts ouverts d'autres scopes).
6. **Auto-audit-trail** : présente entrée, conforme convention ADR-054.

## Status post-merge attendu

- ADR-057 passe `proposed` → `accepted` après merge PR vault.
- PR pilote monorepo bloquée jusqu'à :
  (a) merge `feat/seo-v9-r7-router-wire` sur `main` monorepo,
  (b) ADR-057 `accepted`.
- Aucune install upstream avant ces deux conditions.

## References

- Plan source : `/home/deploy/.claude/plans/verifier-skip-to-jaunty-zebra.md`
  (sur poste DEV, non-versionné dans monorepo)
- ADR : `ledger/decisions/adr/ADR-057-marketingskills-adoption-pattern.md`
- Repo upstream : `https://github.com/coreyhaines31/marketingskills` (v1.10.0)
- Branche feature monorepo en cours bloquante : `feat/seo-v9-r7-router-wire`
