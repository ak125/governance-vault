---
id: ADR-078
title: "pieces_media_img mass corruption recovery — Tier C soft-hide + structural guards, brand-media ingestion deferred"
status: accepted
date: 2026-05-23
decision_date: 2026-05-23
decision_makers: [Fafa]
supersedes: []
superseded_by: []
amends: []
related_adr: [ADR-058]
related_rules: []
related_incidents: [INC-2026-015]
reviewed_by: "@fafa"
---

# ADR-078 : pieces_media_img recovery — Tier C soft-hide + structural guards, brand-media ingestion deferred

## Contexte

Voir [[2026-05-23-pieces-media-img-corruption]] (INC-2026-015) pour la chronologie
et l'évidence empirique. En résumé :

- ~50 % des lignes `pieces_media_img` (≈ 4,76 M) sont malformées
  (`pmi_folder=''`, `pmi_name` sans extension).
- 357 009 pièces **affichées** (103 marques) montrent une icône d'image cassée
  parce que l'URL imgproxy retourne 400 (`Source image is unreachable`) et le
  frontend n'a aucun fallback pour ce cas.
- Les fichiers binaires pour les folders concernés (VALEO `21`, SKF `50`, et
  brand-media nouveau catalogue) **ne sont nulle part dans l'infra actuelle** :
  bucket Supabase `rack-images` (701 K fichiers, scanné), `/opt/automecanik/data/tecdoc/`,
  `automecanik-raw/`, `/opt/automecanik/backups/`, archive `SQL-CONVERTED.7z`
  (pas de table `t216` DOCUMENTS) — tous scannés, **0 binaire trouvé**.
- `IMGPROXY_ALLOWED_SOURCES` restreint au seul bucket Supabase ; pas de serveur
  legacy distinct ni d'origine alternative possible.

Conséquence : aucune récupération automatique des **vraies** images n'est faisable
en interne. Trois options s'offrent :

## Options considérées

### Option A : Recovery automatique « intra-DB » (Tier A relink-par-ref)

**Description** : pour chaque pièce affichée cassée, trouver une ligne bien-formée
de la même marque pour le même `piece_ref` normalisé, et copier `(pmi_folder, pmi_name)`.

**Constat empirique** : 0 yield. Les pièces affichées-cassées sont des **NOUVELLES
références** (`06703…`, `STARTER_4xxxxx`) absentes du catalogue ancien (`063…`,
`VALEO_HEADLAMP_04xxxx`). De plus, même les anciennes refs bien-formées sont des
orphelines (folder `21` = 0 fichier dans le bucket).

→ Rejetée empiriquement.

### Option B : Tier B — extension du pipeline TecDoc pour ingérer les images

**Description** : étendre `scripts/tecdoc-import.py` pour lire `t216 PartDocuments`
de l'archive TecDoc et ré-importer (folder, name) + binaire correspondant.

**Constat empirique** : infaisable depuis l'archive locale.
- `SQL-CONVERTED.7z` ne contient **aucun fichier `216.*.sql`** (table DOCUMENTS).
- Suppliers VALEO/SKF/MAGNETI : seul VALEO (`4820`) a quelques tables (`200`,
  `203`, `211`) ; SKF et MAGNETI n'ont **aucun fichier** dans l'archive.
- `t203` = ARTICLE-LINK-NORMS (cross-references ARTNR/REFNR), **pas** des
  références image.

→ Reportée : nécessite (a) accès aux brand media centers (VALEO Brand Connect /
SKF VSM / TecDoc avec t216), (b) pipeline d'ingestion à construire. Hors scope
sans owner input et sans accès credentials.

### Option C : Tier C — soft-hide + fallback gracieux + gardes structurelles (RETENUE)

**Description** :

1. **Soft-hide** toutes les lignes `pmi_display='1'` malformées attachées à des
   pièces `piece_display=true` (`UPDATE … SET pmi_display='0'`). Pas de DELETE,
   pas de delete-reinsert.
2. **Audit table** `pieces_media_img_tier_c_flipped_20260523` retient la liste
   exacte des lignes flippées → rollback déterministe.
3. **Fallback frontend** : le composant produit utilise déjà `no.png` quand
   `pieces_media_img` ne contient aucune ligne `display='1'` pour la pièce.
   Le soft-hide active naturellement ce fallback. **Pas de modification frontend.**
4. **Gardes structurelles** :
   - Audit nightly `scripts/audit/audit-pieces-media-img-invariants.sh`
     (invariants I1 folder-non-vide / I2 name-avec-extension sur pièces affichées,
     seuil = 0).
   - ast-grep `.ast-grep/rules/supabase-js-bulk-select-paginate.yml` : bloque
     tout `.from(pieces|pieces_price|pieces_media_img).select(...)` sans
     `.range()` / `.limit()` / `.single()`.
   - Brand-folder registry YAML observé promu canon L2 ADR-058
     (`.spec/00-canon/repository-registry/brand-folder-registry.yaml`).
   - Spot-fix `shipping-calculator.service.ts:242` (`.in()` non paginé).

## Décision

**Adopter Option C** comme remédiation immédiate. Tier B (vraie récupération
images) reste **différé** ; il sera scoppé via une ADR séparée quand l'owner
fournit l'accès à une source brand-media (VALEO / SKF / TecDoc t216).

## Conséquences

**Bénéfices** :
- UX immédiate : passage de 357 009 pièces avec icône cassée → 357 009 pièces
  avec placeholder propre (`no.png`).
- Zero data loss : aucune ligne supprimée ; rollback déterministe préservé.
- Régression future bloquée par gardes mécaniques (audit + ast-grep + registry).
- Brand-folder registry devient source canon réutilisable par toute future
  ingestion image.

**Coûts / limitations** :
- Les 357 K pièces concernées n'ont **plus aucune image** sur le site jusqu'à
  Tier B (autrefois elles n'avaient déjà aucune image utilisable — juste un
  lien mort masqué par l'icône cassée).
- Inventaire dormant (`piece_display=false`) : ~3,89 M lignes malformées
  restent en l'état. Pas d'impact UX. Sera flaggé si ces pièces sont
  réactivées (l'audit nightly utilisera alors le scope étendu).
- Le brand-folder registry contient quelques marques multi-folder (MAGNETI =
  95+4723, GATES = 33+4812+6346+6350+6665, etc.) ; l'ingestion future devra
  préserver cette pluralité (set, pas singleton).

## Mises à jour mémoire / canon

- L2 overlay `repository-registry/brand-folder-registry.yaml` (créé).
- Audit ratchet `scripts/audit/audit-pieces-media-img-invariants.sh` (créé).
- ast-grep `.ast-grep/rules/supabase-js-bulk-select-paginate.yml` (créé).
- Mémoire Claude `feedback_supabase_js_1000_row_cap_data_loss` (à enrichir avec
  ce cas réel `pieces_media_img`).
- Nouvelle mémoire `incident-pieces-media-img-corruption-20260523` à créer
  (lien vers cette ADR + INC-2026-015).
