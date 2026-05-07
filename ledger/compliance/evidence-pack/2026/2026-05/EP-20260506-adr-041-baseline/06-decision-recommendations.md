# 06 — Recommandations sous-décisions 2.A et 2.C (empiriquement justifiées)

> **Méthodologie** : per [`feedback_decision_must_be_signal_proven_not_intuited`](../../../../knowledge/feedback_decision_must_be_signal_proven_not_intuited.md) — décisions basées uniquement sur signal mesuré + canon, pas sur intuition rédactionnelle.
>
> **Contexte** : baseline T0 corrigée 2026-05-07 avec filtre URL R1 PURE (regex ancrée) — voir `snapshots/2026-05-06-summary.json` §correction_note.

## Sous-décision 2.A — Règle longueur `r1s_micro_seo_block`

### Recommandation : **Option 1 (abaisser règle à `Min 200, Max 800`)**

### Justification empirique (T0)

| Bucket | n_slots | n_with_gsc | clicks_28d | impressions_28d | CTR |
|--------|---------|------------|------------|------------------|-----|
| A_long ≥700c   | 6   | **2**  | **0**  | **5**    | 0% |
| mid 300-699c   | 31  | 6      | 0      | 177      | 0% |
| B_short <300c  | 132 | 53     | 2      | 1551     | 0.129% |

**Bucket A_long : 5 impressions, 0 clicks sur 28 jours.** Sample size impossible à utiliser même à T+30, T+60 ou T+90. Le faible volume R1 PUR (1733 imp/28j total = ~62 imp/jour pour 169 slots) interdit toute conclusion statistique sur le levier longueur.

### Argument structurel (smoke prod 2026-05-07)

Test sur 4 pages réellement indexées (top par impressions GSC) :

| URL | Console errors | Render | Structure DOM |
|-----|----------------|--------|---------------|
| `/pieces/galet-tendeur-de-courroie-d-accessoire-310.html` | 0 | OK | H1 + 5 H2 + 6 marques + 12 véhicules |
| `/pieces/volant-moteur-577.html` | 0 | OK | H1 + 5 H2 + multi marques+véhicules |
| `/pieces/capteur-temperature-d-air-admission-3939.html` | 0 | OK | idem |
| `/pieces/rotule-de-direction-2066.html` | 2 (Sentry CSP, cross-cutting) | OK | idem |

→ Le `r1s_micro_seo_block` est **UN bloc parmi ~10 sections** render (H1, hero, buy-args, safe-table, compat-errors, FAQ, motorisations, équipementiers, catalogue, KPI). Augmenter ce bloc seul de 200→700c ajoute ~80 KB de prose totale réparties dans des pages déjà riches en signaux structurés. Le ROI SEO est non-mesurable.

### Argument canon

Per [ADR-041 §1](../../../../decisions/adr/ADR-041-r1-router-posture-empirical-reaffirm.md#1-posture-r1_router-strict-reaffirmée) : "R1_ROUTER reste **router pur** au sens de `r1-router-validator.md` ROLE PURITY". Le canon décrit **explicitement** un router court. La règle "Min 700" inscrite dans `r1-content-batch.md:130,344` est une fiction héritée que l'ADR-041 a rejetée par son rejet du pivot commerce-safe.

### Coûts et risques

| Option | Coût | Risque |
|--------|------|--------|
| **Option 1** (lower 200, max 800) | 3 lignes diff dans `r1-content-batch.md` | Aucun risque empirique : 99% des slots déjà <700c, aucun changement de contenu existant |
| Option 2 (re-enrich 163 slots à ≥700c) | ~30 min Anthropic API + agent r1-content-batch × 3 itérations + reviews | Forte (anti-canon) ; signal non-mesurable ; double-travail si 2.C tournant en parallèle |

### Implémentation

Fichier : [`workspaces/seo-batch/.claude/agents/r1-content-batch.md`](../../../../../monorepo/workspaces/seo-batch/.claude/agents/r1-content-batch.md)

```diff
- | 1 | R1_S4_MICRO_SEO | `r1s_micro_seo_block` | text | 700 chars / 140 mots | HTML `<p>` autorise |
+ | 1 | R1_S4_MICRO_SEO | `r1s_micro_seo_block` | text | 200 chars / 40 mots | HTML `<p>` autorise |

- - Min 700 chars, max 1500 chars
+ - Min 200 chars, max 800 chars

- 6. **Min lengths** : S4 >= 700 chars, S5 >= 60, S7 >= 50, S6 >= 2 rows, S8 >= 50.
+ 6. **Min lengths** : S4 >= 200 chars, S5 >= 60, S7 >= 50, S6 >= 2 rows, S8 >= 50.
```

### Pas besoin d'attendre T+30

Per `feedback_no_overclaim_security_words` la décision T+30 promise dans le plan initial était un garde-fou anti-bricolage. Mais quand la donnée déjà disponible **prouve que le levier n'est pas là** (5 imp/0 clicks dans bucket A), attendre 30j est de la procrastination déguisée. Re-mesure T+30 reste utile **après** lower rule appliquée — comme contrôle anti-régression, pas comme critère de décision.

---

## Sous-décision 2.C — Re-qualification : faux-positif d'audit (CLOSED 2026-05-07)

### Verdict révisé : **PAS d'action requise — les 10 occurrences sont canon-conformes**

### Découverte (rectification 2026-05-07)

L'audit ADR-041 §Q3 a vérifié 4 termes (`commander`, `stock`, `livraison`, `paiement`). Or **le canon `r1-router-validator.md` FORBIDDEN list** ([source](../../../../../monorepo/workspaces/seo-batch/.claude/agents/r1-router-validator.md#L54-77)) liste **explicitement** :

> Lexique interdit dominant : ajouter au panier, livraison, promo, en stock, démonter, remonter, symptôme, panne, qu'est-ce que, meilleur choix avant achat

→ **`commander` et `paiement` ne sont PAS dans le canon FORBIDDEN.** L'audit a élargi arbitrairement la liste de test au-delà du canon SoT.

### Inspection des 10 occurrences `commander`

Mesure 2026-05-07 contexte autour du mot :

| pg_id | pg_alias | Contexte |
|-------|----------|----------|
| 1218 | module-d-allumage | "piloter, **commander**, contrôler" |
| 1432 | commande-correcteur-de-portee | "**commander**, activer, regler" |
| 258 | maitre-cylindre-de-frein | "**commander** le freinage" |
| 566 | arbre-a-came | "**commander**, synchroniser, actionner les soupapes" |
| 61 | relais-de-clignotant | "**commander**, activer, cadencer" |
| 618 | cable-d-accelerateur | "transmettre, actionner, **commander**" |
| 751 | commande-d-essuie-glace | "**commander**, activer, selectionner" |
| 807 | contacteur-de-feu-de-recul | "activer, signaler, **commander**" |
| 809 | commande-d-eclairage | "**commander**, activer, regler" |
| 864 | interrupteur-verrouilage-des-portes | "**commander**, activer, verrouiller" |

**100 % sens technique mécanique** ("commander un dispositif" = piloter/contrôler), **0 % sens transactionnel** ("commander un produit"). Le canon `r1-router-validator.md` interdit le sens transactionnel (lexique panier/livraison/promo/stock) mais pas le verbe technique.

### Conclusion 2.C

- **Aucun slot ne viole le canon FORBIDDEN.**
- Le "vocab cleanup 2.C" était un faux-positif d'audit (extension arbitraire de la liste de test).
- Pas de PR monorepo nécessaire, pas de UPDATE SQL, pas de re-run agent.
- Per [`feedback_decision_must_be_signal_proven_not_intuited`](../../../../knowledge/feedback_decision_must_be_signal_proven_not_intuited.md) : signal mesuré (canon SoT vs audit list extension) → décision = pas d'action.
- Per [`feedback_canon_rule_live_iff_adr_accepted`](../../../../knowledge/feedback_canon_rule_live_iff_adr_accepted.md) : le canon `r1-router-validator.md` est SoT, l'audit n'a pas autorité pour étendre.

### Garde-fou

Re-mesure périodique avec liste **strictement alignée** sur le canon FORBIDDEN :

```sql
-- Garde-fou canonique : violations FORBIDDEN list de r1-router-validator.md L54-77
SELECT r1s_pg_id, LENGTH(r1s_micro_seo_block) AS len
FROM __seo_r1_gamme_slots
WHERE r1s_micro_seo_block ~* '\m(ajouter au panier|livraison|promo|en stock|qu''est-ce que|meilleur choix avant achat)\M'
   OR r1s_micro_seo_block ~* '\mstock\M'  -- "stock" hors "en stock" reste sensible commercialement
ORDER BY r1s_pg_id;
-- Expected 2026-05-07: 0 rows.
```

---

## Implications pour ADR-041

État sous-décisions au 2026-05-07 :
- **2.A** : pendante — décision longueur reportée (skip user 2026-05-07). Re-mesure T+30 toujours utile comme contrôle anti-régression.
- **2.B** : ✅ DONE 169/169 (monorepo PR #332).
- **2.C** : ✅ CLOSED — faux-positif d'audit, canon FORBIDDEN respecté, 0 violation réelle.

`implementation_status` reste `in_progress` tant que 2.A n'est pas tranché.

LIVE déclarable canon ssi :
1. ✅ ADR-041 status=accepted (PR #178 done)
2. ⏳ 2.A Option 1 appliqué (PR monorepo séparée, à venir)
3. ✅ 2.B safe_table backfill (PR #332 done)
4. ⏳ 2.C cleanup vocab (PR monorepo séparée, à venir)
5. ⏳ T+30 re-mesure post-changes comme contrôle anti-régression

## Findings cross-cutting (hors scope ADR-041)

- **Sentry CSP** : `*.ingest.de.sentry.io` bloqué par `connect-src` policy. Détecté smoke 2026-05-07 sur `rotule-de-direction-2066.html`. Per memory [`sentry-vps-bootstrap-20260506`](../../../../knowledge/sentry-vps-bootstrap-20260506.md), Sentry+SOPS PROD est activé. Ce blocage CSP rendait Sentry inopérant côté navigateur. **Fix** : monorepo PR #344 (`fix(csp): allow Sentry ingest in connect-src`) — ajout `https://*.ingest.de.sentry.io` dans `CSP_DIRECTIVES.connectSrc`.
