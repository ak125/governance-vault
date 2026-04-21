---
type: runbook
scope: admin/seo/r7
surface: R7_BRAND
date: 2026-04-21
owner: Fafa
ui_route: /admin/brands-seo?brand={alias}
api_route: PUT /api/admin/r7/editorial/:marqueId
tags: [runbook, r7, admin-ui, editorial, curation, ops]
---

# Runbook — Admin UI éditorial R7 (`/admin/brands-seo`)

> **UI** : `/admin/brands-seo?brand={marque_alias}` (superadmin requis)
> **API** : `PUT /api/admin/r7/editorial/:marqueId`
> **Auto-enrich** : chaque save régénère la page R7 en DB (`__seo_r7_pages`)

---

## À quoi sert cette UI

Curer le contenu éditorial spécifique marque qui différencie les 36 pages R7 constructeur :

- **FAQ** — questions concrètes entretien/panne par marque (ex: "Faut-il décalaminer un Multiair Alfa Romeo ?")
- **Problèmes courants** — symptômes/causes/pistes de résolution (ex: consommation huile 1.4 TBi)
- **Intervalles d'entretien** — pièces avec périodicité km/années par marque

Sans curation : les 36 pages affichent le même boilerplate (FAQ identiques, no issues). Avec curation : chaque marque devient identifiable par Google, le `diversity_score` monte de ~80 à ~88+.

**Hors scope de cette UI** : les champs factuels (country, founded_year, top_models, top_engines, history) sont gérés par le script [[runbook-build-brand-rag]]. Ne pas confondre.

## Pré-requis

| Item | Où | Notes |
|------|-----|------|
| Compte superadmin | `superadmin@autoparts.com` | Mot de passe en 1Password / `MEMORY.md` |
| Session active sur l'admin | `/admin` | Cookie `connect.sid` créé par Passport |
| Marque existante en DB | `auto_marque` | `marque_alias` lisible dans le sélecteur UI |

Le backend applique `AuthenticatedGuard + IsAdminGuard`. Toute PUT anonyme → 401.

## Démarrage

1. Aller sur `/admin/brands-seo` — la page charge par défaut Renault
2. Dans le bloc **"Sélectionner une marque"**, cliquer la carte de la marque à curer
3. Descendre jusqu'à la section **"🏭 Contenu éditorial R7 — {marque}"**
4. Le badge indique l'état :
   - **"Curé par {curated_by}"** (vert) → contenu déjà existant, prêt à éditer
   - **"Non curé (défauts utilisés)"** (gris) → pas de ligne dans `__seo_brand_editorial`, l'enricher tourne sur templates génériques

## Ajouter une FAQ

1. Cliquer **"+ Ajouter une FAQ"** (bouton désactivé si 15 entrées déjà présentes)
2. Remplir le champ **Question** (5–200 caractères)
3. Remplir le champ **Réponse** (20–1000 caractères)
4. Les char counters deviennent **rouges en gras** si la longueur sort des bornes Zod

**Qualité** : les FAQ génériques ("À quoi sert un filtre à air ?") ne servent à rien, elles sont déjà couvertes par R3/R4. Viser du **marque-spécifique** :

- ✅ "Pourquoi la courroie de distribution Multiair Alfa Romeo doit-elle être changée à 120 000 km ?"
- ✅ "Quel est l'intervalle de remplacement du liquide DSG sur VW Golf 7 ?"
- ❌ "Qu'est-ce qu'une plaquette de frein ?" (R4 Référence)
- ❌ "Comment changer un filtre à huile ?" (R3/conseils)

## Ajouter un problème courant

1. **"+ Ajouter un problème"** (max 20)
2. **Symptôme** obligatoire (5–200 car)
3. **Cause** et **Piste de résolution** optionnels (5–300 car chacun)

**Qualité** : un problème utile mentionne un détail reconnaissable de la marque (motorisation, date modèle, technologie propriétaire).

- ✅ "Consommation d'huile anormale 1.4 TBi Alfa Romeo 2010–2015"
- ❌ "Bruit dans le moteur" (trop vague, pas marque-spécifique)

## Ajouter un intervalle d'entretien

1. **"+ Ajouter un intervalle"** (max 20)
2. **Pièce** obligatoire (1–80 car)
3. **Intervalle km** et/ou **Intervalle années** — au moins un des deux recommandé
4. **Note** optionnelle (0–300 car) — bonne place pour préciser une tolérance ou exception

**Qualité** : donner l'intervalle OEM documenté pour la marque, pas une moyenne générique.

- ✅ "Courroie de distribution Multiair — 120 000 km ou 5 ans — incluant galets tendeurs et pompe à eau"
- ❌ "Courroie — à changer régulièrement" (non actionnable, non spécifique)

## Enregistrer

1. Vérifier la section **"🔍 Prévisualisation du payload JSON"** (repliée par défaut — cliquer pour déplier) : elle montre exactement ce qui part au backend
2. Cliquer **"💾 Enregistrer et régénérer R7"**
3. Attendre ~2–4 secondes — le backend fait `upsert + enrichSingle(marqueId)` dans la même requête
4. Un cartouche vert apparaît avec :
   - **Décision SEO** (`PUBLISH` / `REVIEW_REQUIRED` / `REGENERATE` / `REJECT`)
   - **Diversity Score** (sur 100)
   - **Status** (`draft`)

Une décision `PUBLISH` + un score qui monte = curation réussie.

## Interpréter le résultat

### Decision `PUBLISH`

La page R7 en DB est mise à jour, prête à être servie par le frontend au prochain hit (pas de cache applicatif agressif sur R7).

Vérifier visuellement : `https://www.automecanik.com/constructeurs/{alias}-{marque_id}.html` — la section FAQ/S9 doit refléter les nouvelles questions.

### Decision `REVIEW_REQUIRED`

Le score est sous le seuil PUBLISH (typiquement 70). Causes fréquentes :

- Peu de contenu ajouté (1 FAQ n'est pas assez différenciant)
- Questions/réponses trop génériques
- Boilerplate détecté par le risque de boilerplate R7 (voir [[r7-brand-editorial-live-sync]])

Remède : ajouter plus d'entrées spécifiques, ré-enregistrer.

### Decision `REGENERATE` / `REJECT`

Rare. Indique une régression structurelle (payload trop pauvre, RAG `.md` absent, etc.). Vérifier les logs backend :

```bash
ssh 46.224.118.55 "docker compose logs -f --tail=200 | grep -i 'R7 enriched\\|R7 surface-purity\\|marque_id={id}'"
```

## Cas d'erreur courants

### 400 — `Editorial content violates surface purity`

Le backend a détecté une URL R8 profonde collée dans une FAQ, cause, piste de résolution ou note. Exemple :

```json
{
  "violations": [
    {
      "message": "R7: URL R8 \"/constructeurs/bmw-33/serie-3-456/320d-12345.html\" interdite dans le contenu (dérive cross-surface)",
      "details": { "url": "...", "sourceRole": "R7", "foreignRole": "R8" }
    }
  ]
}
```

Remède : retirer l'URL deep et linker à la marque (R7) ou au véhicule via un composant navigationnel dédié côté frontend, pas en dur dans le texte. Cf. [[r7-surface-purity-no-cross-surface-urls]].

### 400 — `Invalid editorial payload` avec liste `issues`

Zod a rejeté une sous-entrée. Exemples typiques :

| `issues[*].path` | `message` | Cause |
|------------------|-----------|-------|
| `faq.0.q` | String must contain at least 5 character(s) | Question trop courte |
| `faq.3.a` | String must contain at most 1000 character(s) | Réponse trop longue |
| `common_issues.2.symptom` | Required | Symptôme laissé vide |
| `maintenance_tips.1.interval_km` | Expected number, received nan | Champ km laissé vide ou non numérique |

Le Alert rouge montre les `issues` en JSON brut sous le message. Corriger les champs flaggés (char counters rouges dans la UI aident à localiser).

### 500 — DB write failed

Rare. Problème Supabase ou RLS. Vérifier `SUPABASE_SERVICE_ROLE_KEY` dans l'env backend et les permissions de la table `__seo_brand_editorial`.

### Pas d'alerte, mais la page R7 n'a pas changé

Vérifier le cartouche vert après save : si `diversity_score` n'a pas bougé, c'est probablement que le contenu ajouté est trop similaire aux templates (sémantique trop proche du boilerplate). Le scoring reste sur l'ancien fingerprint → pas de progrès SEO.

Remède : diversifier le vocabulaire, ajouter des termes techniques propres à la marque.

## Workflows recommandés

### Curation d'une marque pilote (scope : 1 marque, ~20 min)

1. Charger la page avec `?brand={alias}`
2. Ajouter 3–5 FAQ marque-spécifiques (viser > 85 score)
3. Ajouter 2–3 problèmes courants documentés
4. Ajouter 3–5 intervalles d'entretien OEM
5. Enregistrer → viser `PUBLISH` score ≥ 85
6. Vérifier visuellement la page R7 publique

### Batch imports (skip auto-enrich)

Pour importer beaucoup de contenu via script externe sans déclencher 36 enrichissements :

```bash
curl -b cookie.txt -X PUT "https://admin.dev.automecanik.com/api/admin/r7/editorial/13?skipEnrich=true" \
  -H "Content-Type: application/json" \
  -d @alfa-romeo-editorial.json
```

Puis enrich batch dans un second appel :

```bash
curl -b cookie.txt -X POST https://admin.dev.automecanik.com/api/admin/r7/enrich-batch \
  -H "Content-Type: application/json" \
  -d '{"marqueIds":[13, 14, 15, 16]}'
```

### Audit d'une curation existante

```sql
-- Top 10 marques avec contenu éditorial, triées par score R7
SELECT be.marque_id,
       m.marque_name,
       jsonb_array_length(be.faq) AS faq_count,
       jsonb_array_length(be.common_issues) AS issues_count,
       jsonb_array_length(be.maintenance_tips) AS maint_count,
       be.curated_by,
       rp.diversity_score,
       rp.seo_decision
FROM __seo_brand_editorial be
JOIN auto_marque m USING (marque_id)
LEFT JOIN __seo_r7_pages rp ON rp.page_key = 'r7_brand_' || be.marque_id
ORDER BY rp.diversity_score DESC NULLS LAST
LIMIT 10;
```

## Règles dérivées

1. **Curer d'abord la valeur différenciante** — une FAQ générique n'ajoute rien. Viser du marque-spécifique ou ne rien ajouter.
2. **Char counters font loi** — si un champ est rouge, le backend refusera. Corriger avant de perdre du temps à cliquer Enregistrer.
3. **Pas d'URL profonde dans le texte** — le gate surface-purity refuse automatiquement (cf. [[r7-surface-purity-no-cross-surface-urls]]). Laisser le frontend gérer la navigation R8.
4. **Score = signal, pas objectif** — un score à 88 avec contenu pertinent vaut mieux qu'un 92 gonflé artificiellement (le risque de boilerplate est mesuré).
5. **Batch via `skipEnrich=true`** — pour import massif ; l'UI n'est pas conçue pour 100 marques d'affilée.

## Références

- Architecture R7 : [[r7-brand-editorial-live-sync]]
- Règle surface purity : [[r7-surface-purity-no-cross-surface-urls]]
- Build facts RAG (champs stables) : [[runbook-build-brand-rag]]
- PR UI MVP (3 textareas JSON) : https://github.com/ak125/nestjs-remix-monorepo/pull/92
- PR P2 UI v1 (dynamic form) : https://github.com/ak125/nestjs-remix-monorepo/pull/98
- PR P3 surface-purity gate : https://github.com/ak125/nestjs-remix-monorepo/pull/97
- Taxonomie des rôles : [[08-seo-charter]]
