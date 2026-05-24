---
# ============================================================
# Empirical Verdict Header — G9 Sunset Clause (ADR-081)
# ============================================================
# Tout fichier verdict empirique (ledger/verdicts/YYYY-MM-DD-<topic>.md)
# DOIT porter ce header YAML.
#
# Verdict expire non-renouvele → DO_NOT_START qu'il bloque deviennent
# OPEN_FOR_REVIEW automatiquement (cron weekly check-verdict-expirations.sh).
#
# Renouvellement = re-instrumentation explicite + nouveau commit verdict
# (ne pas etendre expires_at sans re-mesure).
# ============================================================

id: VERDICT-YYYY-NNN
# Slug stable, jamais reutilise. Format : VERDICT-{year}-{3-digit-counter}.

metric: <metric_slug>
# Slug machine-readable de la metrique mesuree.
# Exemples : conversion_funnel_organic, ai_visibility_gap, cwv_inp_p75_mobile

value: <numeric_value>
# Valeur numerique mesuree (decimal, pas de pourcentage symbole).
# Exemple : 0.0017 (et non "0.17%")

measured_at: YYYY-MM-DD
# Date effective de mesure (pas de date d'ecriture du fichier).

expires_at: YYYY-MM-DD
# OBLIGATOIRE = measured_at + 12 weeks (84 jours).
# Calcul : `date -d "$measured_at + 84 days" +%F`

methodology: |
  <Methodologie courte mais reproductible.>
  <Inclure : source data, fenetre temporelle, segmentation, outils.>
  <Exemple :>
  GA4 events filter ?utm_medium=organic
  + funnel events table (#676) cross-ref
  sur fenetre 28d glissante (2026-04-22 → 2026-05-20).

pr_ref: <pr_number>
# Numero PR ou la mesure a ete livree / documentee.
# Pour la tracabilite GitHub (gh pr view <pr_ref>).

blocks_until_expiry:
  - <do_not_start_slug_1>
  - <do_not_start_slug_2>
# Liste des slugs `DO_NOT_START` (top-priorities.md) que ce verdict justifie.
# Quand le verdict expire, ces slugs passent a OPEN_FOR_REVIEW.
# Laisser vide [] si le verdict justifie un pivot strategique sans bloquer rien.

# (optionnel)
renewed_from: VERDICT-YYYY-NNN
# Si ce verdict renouvelle un verdict precedent, referencer son id ici.
# Sinon omettre.

# (optionnel)
notes: |
  <Notes contextuelles si necessaire.>
  <Exemple : mesure pre-instrumentation funnel, biais possible sur attribution>
---

# Verdict empirique : <Titre humain court>

## Contexte

<Pourquoi cette mesure a ete prise ?>
<Quel debat strategique ou DO_NOT_START elle justifie ?>

## Methodologie detaillee

<Detail reproductible : requetes, fenetres, filtres, outils.>
<Inclure tout assumption non-trivial.>

## Resultats

<Chiffres avec contexte.>
<Sanity checks effectues.>
<Confidence interval ou caveats.>

## Implications strategiques

<Quels DO_NOT_START sont justifies ? Pourquoi ?>
<Quel canal / produit / approche est priorise par ce verdict ?>

## Sunset / renouvellement

<Que faut-il re-mesurer dans 12 semaines pour renouveler ce verdict ?>
<Quelle metrique downstream pourrait l'invalider plus tot ?>
