# Stratégie SEO : Filtre à Huile

> **pg_id** : 7 (famille Filtration)
> **Date** : 2026-01-30
> **Statut** : Validé - Prêt pour implémentation

---

## 1. Stratégie par Intention de Recherche

### 1.1 Intention Informationnelle (Top of Funnel)

**Objectif** : Capter le trafic éducatif et établir l'autorité

| Article | Type | URL Cible | Volume Est. | Priorité |
|---------|------|-----------|-------------|----------|
| Comment changer un filtre à huile | Guide | `/blog/comment-changer-filtre-huile` | 1k-10k | P1 |
| À quoi sert un filtre à huile ? | Reference | `/reference-auto/filtre-a-huile` | 1k-10k | P1 |
| Tous les combien changer son filtre | Guide | `/blog/quand-changer-filtre-huile` | 1k-10k | P1 |
| Tuto vidange Clio 3 1.5 dCi | Advice | `/blog/vidange-clio-3-dci` | 100-1k | P2 |
| Filtre huile voiture sans permis | Advice | `/blog/filtre-huile-vsp-aixam-ligier` | 100-1k | P3 |

### 1.2 Intention Commerciale (Middle of Funnel)

**Objectif** : Guider vers l'achat avec comparatifs et guides

| Article | Type | URL Cible | Volume Est. | Priorité |
|---------|------|-----------|-------------|----------|
| Meilleur filtre Clio 2 : comparatif | Comparatif | `/blog/meilleur-filtre-huile-clio-2` | 100-1k | P1 |
| Purflux vs Mann vs Bosch | Comparatif | `/blog/comparatif-filtres-huile-purflux-mann-bosch` | 100-1k | P1 |
| Filtre huile 1.5 dCi : compatibilité | Guide | `/blog/filtre-huile-1-5-dci-compatibilite` | 100-1k | P2 |
| Diesel vs Essence : même filtre ? | Guide | `/blog/filtre-huile-diesel-essence-difference` | 100-1k | P2 |
| Meilleur filtre huile sportif | Guide | `/blog/filtre-huile-performance-k-n` | 10-100 | P3 |

### 1.3 Intention Transactionnelle (Bottom of Funnel)

**Objectif** : Convertir les recherches produit en ventes

| Page | Pattern URL | Status | Volume Est. |
|------|-------------|--------|-------------|
| Filtre huile Clio 3 | `/pieces/filtre-huile-7/renault-5/clio-iii-*/` | ✅ Existe | 1k-10k |
| Filtre huile Clio 2 | `/pieces/filtre-huile-7/renault-5/clio-ii-*/` | ✅ Existe | 1k-10k |
| Filtre huile Twingo | `/pieces/filtre-huile-7/renault-5/twingo-*/` | ✅ Existe | 100-1k |
| Filtre huile Megane 2 | `/pieces/filtre-huile-7/renault-5/megane-ii-*/` | ✅ Existe | 100-1k |
| Filtre huile Scenic 2 | `/pieces/filtre-huile-7/renault-5/scenic-ii-*/` | ✅ Existe | 100-1k |
| Filtre huile Captur | `/pieces/filtre-huile-7/renault-5/captur-*/` | ✅ Existe | 100-1k |
| Filtre huile 206 | `/pieces/filtre-huile-7/peugeot-6/206-*/` | ✅ Existe | 100-1k |
| Filtre huile Golf 5 | `/pieces/filtre-huile-7/volkswagen-8/golf-v-*/` | ✅ Existe | 100-1k |

---

## 2. Cocon Sémantique

### 2.1 Structure Hiérarchique

```
📄 PAGE PILIER: /reference-auto/filtre-a-huile (R4)
│   Définition, rôle, types, symptômes
│   → Liens vers toutes les branches
│
├── 📁 PAR MARQUE VÉHICULE
│   │
│   ├── 📁 Renault
│   │   ├── Clio (II, III, IV, V)
│   │   ├── Twingo (I, II, III)
│   │   ├── Megane (II, III, IV)
│   │   ├── Scenic (II, III, IV)
│   │   └── Captur (I, II)
│   │
│   ├── 📁 Peugeot
│   │   ├── 206, 207, 208
│   │   ├── 306, 307, 308
│   │   └── 3008, 5008
│   │
│   └── 📁 Volkswagen
│       ├── Golf (IV, V, VI, VII)
│       └── Polo (IV, V, VI)
│
├── 📁 PAR MOTORISATION
│   │
│   ├── 📄 1.5 dCi (K9K) - Renault
│   ├── 📄 2.0 dCi (M9R) - Renault
│   ├── 📄 1.6 HDI (DV6) - PSA
│   ├── 📄 2.0 HDI (DW10) - PSA
│   ├── 📄 1.2 PureTech (EB2) - PSA
│   └── 📄 1.4 TSI (CAXA) - VW
│
├── 📁 PAR MARQUE FILTRE
│   │
│   ├── 📄 Purflux (OE PSA/Renault)
│   ├── 📄 Mann-Filter (Allemagne)
│   ├── 📄 Bosch (Qualité premium)
│   ├── 📄 Mahle (OE Mercedes/BMW)
│   └── 📄 K&N (Performance)
│
└── 📁 GUIDES & TUTORIELS
    │
    ├── 📄 Comment changer son filtre
    ├── 📄 Quand changer son filtre
    ├── 📄 Vidange complète (huile + 3 filtres)
    ├── 📄 Comparatif marques filtres
    └── 📄 Symptômes filtre usé
```

### 2.2 Maillage Interne

| De (Source) | Vers (Cible) | Ancre | Position |
|-------------|--------------|-------|----------|
| R4 Reference | R3 Blog guides | "comment changer" | Intro |
| R4 Reference | R1 Router marques | "filtres par véhicule" | Section compatibilité |
| R3 Blog | R2 Product | "acheter filtre X" | CTA fin article |
| R3 Blog | R4 Reference | "en savoir plus" | Paragraphe intro |
| R2 Product | R3 Blog | "guide installation" | Sidebar |
| R1 Router | R4 Reference | "qu'est-ce qu'un filtre" | Breadcrumb |

---

## 3. Infrastructure Existante

### 3.1 Couverture Actuelle : 85%

| Intention | Status | Action |
|-----------|--------|--------|
| Transactionnelle | ✅ 100% | Rien à faire |
| Informationnelle | ⚠️ 30% | Créer contenu R3/R4 |
| Commerciale | ⚠️ 40% | Créer comparatifs |

### 3.2 Données Existantes (pg_id=7)

**Table `__seo_gamme_purchase_guide` :**
- ✅ `sgpg_intro_title` : "Le filtre à huile"
- ✅ `sgpg_intro_role` : Description complète
- ✅ `sgpg_risk_consequences` : 5 risques
- ✅ `sgpg_timing_km` : "10 000 à 30 000 km"
- ✅ `sgpg_timing_months` : "12 mois max"
- ✅ `sgpg_symptoms` : 5 symptômes
- ✅ `sgpg_faq` : 5 Q/R complètes
- ✅ `sgpg_how_to_choose` : Guide de choix
- ✅ `sgpg_quality_argument` : Mann, Mahle, Bosch, Purflux

### 3.3 Gammes Filtres Connexes

| pg_id | Gamme | Contenu SEO |
|-------|-------|-------------|
| 7 | Filtre à huile | ✅ Complet |
| 8 | Filtre à air | ✅ Complet |
| 9 | Filtre à carburant | ✅ Complet |
| 416 | Filtre boîte auto | ✅ Complet |
| 424 | Filtre habitacle | ✅ Complet |

---

## 4. Plan d'Implémentation

### Phase 1 : Fondations (Semaine 1)

| Tâche | Fichier/Action | Effort | Priorité |
|-------|----------------|--------|----------|
| Créer R4 Reference "filtre-a-huile" | Migration SQL `__seo_reference` | 3h | P1 |
| Ajouter guide frontend JSON | `frontend/app/data/guide-content.json` | 2h | P1 |
| Vérifier indexation pages transactionnelles | Google Search Console | 1h | P1 |

### Phase 2 : Contenu Blog R3 (Semaine 2-3)

| Article | Table | Effort | Priorité |
|---------|-------|--------|----------|
| Comment changer son filtre | `__blog_advice` | 3h | P1 |
| Quand changer son filtre | `__blog_guide` | 3h | P1 |
| Vidange complète huile + filtres | `__blog_guide` | 3h | P1 |
| Comparatif Purflux/Mann/Bosch | `__blog_guide` | 4h | P2 |
| Filtre huile 1.5 dCi compatibilité | `__blog_advice` | 3h | P2 |

### Phase 3 : Pages Agrégées (Mois 2)

| Développement | Fichiers | Effort | Priorité |
|---------------|----------|--------|----------|
| Route `/pieces/filtre-huile-7/motorisation/[family].html` | Nouvelle route Remix | 8h | P2 |
| Service `MotorizationAggregationService` | Backend NestJS | 8h | P2 |
| Pages marque équipementier | Route + Service | 8h | P3 |

---

## 5. Annexes Techniques

### 5.1 SQL : Créer Page R4 Reference

```sql
INSERT INTO __seo_reference (
  sr_slug,
  sr_title,
  sr_meta_description,
  sr_definition,
  sr_role_mecanique,
  sr_composition,
  sr_confusions_courantes,
  sr_symptomes_associes,
  sr_pg_id,
  sr_status
) VALUES (
  'filtre-a-huile',
  'Filtre à huile : définition, rôle et remplacement | Guide Auto',
  'Découvrez tout sur le filtre à huile automobile : fonction dans le moteur, types (à visser, cartouche), fréquence de changement et symptômes d''usure.',
  'Le filtre à huile est un composant essentiel du circuit de lubrification moteur. Il retient les impuretés métalliques, les résidus de combustion et les particules qui circulent dans l''huile moteur.',
  'Dans le système de lubrification, le filtre à huile intercepte les contaminants avant qu''ils n''atteignent les pièces en mouvement (pistons, bielles, arbre à cames). Un filtre colmaté laisse passer les impuretés, causant une usure prématurée.',
  '["Élément filtrant (papier ou synthétique)", "Joint torique d''étanchéité", "Clapet anti-retour (maintien huile au repos)", "Valve de dérivation (by-pass si colmatage)"]'::jsonb,
  '["Filtre à huile ≠ Filtre à air (circuit différent)", "Cartouche ≠ Filtre à visser (même fonction, montage différent)", "Filtre à huile ≠ Crépine de pompe (localisation différente)"]'::jsonb,
  ARRAY['huile-noire-avant-echeance', 'voyant-huile-allume', 'bruit-cliquetis-moteur-froid'],
  7,
  'published'
);
```

### 5.2 JSON : Guide Frontend

```json
{
  "filtre_huile": {
    "name": "Filtre à huile",
    "slug": "filtre-huile",
    "pg_id": 7,
    "title": "Comment choisir votre filtre à huile ?",
    "intro": "Le filtre à huile protège votre moteur en retenant les impuretés. Un filtre de qualité prolonge la durée de vie du moteur.",
    "step1": {
      "title": "Sélectionnez votre véhicule",
      "description": "Marque, modèle et motorisation exacte"
    },
    "step2_ranges": {
      "title": "Comparez les marques",
      "options": [
        { "name": "Purflux", "badge": "OE Renault/PSA", "quality": "premium" },
        { "name": "Mann-Filter", "badge": "Qualité allemande", "quality": "premium" },
        { "name": "Bosch", "badge": "Fiabilité", "quality": "standard" },
        { "name": "Filtron", "badge": "Bon rapport qualité/prix", "quality": "economy" }
      ]
    },
    "step3": {
      "title": "Vérifiez la compatibilité",
      "description": "Dimensions et filetage adaptés"
    },
    "tips": [
      "Changez le filtre à chaque vidange",
      "Préférez les marques OE (Purflux, Mann)",
      "Vérifiez le type : à visser ou cartouche"
    ]
  }
}
```

### 5.3 Motorisations Clés

| Code Moteur | Nom Commercial | Marque | Volume Filtres/an |
|-------------|----------------|--------|-------------------|
| K9K | 1.5 dCi | Renault | Très élevé |
| M9R | 2.0 dCi | Renault | Élevé |
| DW10 | 2.0 HDI | PSA | Élevé |
| DV6 | 1.6 HDI | PSA | Très élevé |
| EB2 | 1.2 PureTech | PSA | Moyen |
| D4F | 1.2 16v | Renault | Moyen |
| F4R | 2.0 16v | Renault | Moyen |
| CAXA | 1.4 TSI | VW | Élevé |

---

## 6. Véhicules Prioritaires

| Véhicule | pg_id | URL Pattern |
|----------|-------|-------------|
| Clio 3 (toutes variantes) | 7 | `/pieces/filtre-huile-7/renault-5/clio-iii-*/` |
| Clio 2 (toutes variantes) | 7 | `/pieces/filtre-huile-7/renault-5/clio-ii-*/` |
| Twingo (1, 2, 3) | 7 | `/pieces/filtre-huile-7/renault-5/twingo-*/` |
| Megane 2 & 3 | 7 | `/pieces/filtre-huile-7/renault-5/megane-*/` |
| Scenic 2, 3, 4 | 7 | `/pieces/filtre-huile-7/renault-5/scenic-*/` |
| Captur | 7 | `/pieces/filtre-huile-7/renault-5/captur-*/` |
| 206 | 7 | `/pieces/filtre-huile-7/peugeot-6/206-*/` |
| Golf 5 | 7 | `/pieces/filtre-huile-7/volkswagen-8/golf-v-*/` |

---

## 7. Estimation Effort vs Impact

| Tâche | Effort | Impact SEO | ROI |
|-------|--------|------------|-----|
| Créer R4 Reference | 3h | Élevé (page pilier) | ⭐⭐⭐⭐⭐ |
| 5 articles blog R3 | 15h | Élevé (long-tail) | ⭐⭐⭐⭐ |
| Guide frontend JSON | 2h | Moyen (UX) | ⭐⭐⭐ |
| Pages par motorisation | 16h dev | Élevé (1.5 dCi) | ⭐⭐⭐⭐ |
| Pages marque équipementier | 8h dev | Moyen | ⭐⭐ |

---

**Prochaines étapes immédiates :**
1. Exécuter SQL pour R4 Reference
2. Ajouter entrée `guide-content.json`
3. Créer premier article blog R3
