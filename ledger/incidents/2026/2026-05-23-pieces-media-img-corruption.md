---
id: INC-2026-015
title: "pieces_media_img mass corruption — ~50 % rows malformed, ~357K displayed pieces broken"
date: 2026-05-23
detected_by: Fafa (visual report : « images VALEO cassées »)
severity: P2 (UX-only, no revenue blocker, no PII)
status: contained
related_adr: [ADR-078]
related_rules: []
runtime_impact: degraded UX (broken-image icons on listings/details)
data_loss: none (referenced files were already absent ; rows were dangling pointers)
---

# INC-2026-015 — `pieces_media_img` mass corruption

## TL;DR

~4,76 M lignes (≈ 50 %) de `pieces_media_img` ont `pmi_folder=''` et un `pmi_name`
sans extension (valeurs type `STARTER_406502_01`, `VALEO_HEADLAMP_046741_02` ou des
identifiants TecDoc bruts). Conséquence runtime : l'URL imgproxy résolue est
`rack-images//<name>@webp` → upstream 400 → imgproxy renvoie un placeholder texte
de 27 octets `Source image is unreachable` avec HTTP 200 (trompeur). Le frontend
n'a aucun fallback pour ce cas (le `no.png` n'est utilisé que si **aucune** ligne
`pmi_display='1'` n'existe pour la pièce). Résultat visible : icône d'image cassée
sur **357 009 pièces affichées** (103 marques).

## Timeline

- **Date inconnue antérieure** : import TecDoc/brand-media a écrit dans
  `pieces_media_img` des lignes orphelines pour des refs nouvelles, sans résoudre
  les chemins rack (folder vide, name = identifiant brut TecDoc/VALEO).
- **2026-05-23** : owner signale "images VALEO cassées" + identifie le pattern
  `supabase-js caps at 1000 rows`. Investigation Claude révèle :
  - VALEO 2 538 affichées / 100 % cassées ; SKF 1 122 / 100 % ; MAGNETI 4 523 / 82 %.
  - Bucket `rack-images` : 707 948 fichiers (688K jpg, 18K bmp, 0 webp).
  - VALEO folder `21` = 0 fichier dans le bucket (vrai pour anciennes ET nouvelles refs).
  - Vérification : aucune origine alternative possible — `IMGPROXY_ALLOWED_SOURCES`
    restreint au seul bucket Supabase ; pas de serveur legacy distinct ;
    `/opt/automecanik/data/tecdoc`, `automecanik-raw/`, `/opt/automecanik/backups/`,
    `/var`, `/home`, `/srv` scannés → 0 fichier image binaire trouvé.
- **2026-05-23 (h+4)** : Tier C appliqué = soft-hide (`pmi_display '1'→'0'`)
  de toutes les lignes malformées attachées à pièces affichées (1 107 390 lignes /
  357 009 pièces / 103 marques). Audit table `pieces_media_img_tier_c_flipped_20260523`
  préserve la liste pour rollback.

## Cause racine

Trois sous-causes cumulées :

1. **Bad import** : un script (non identifié à ce stade ; n'est PAS le canonique
   `scripts/tecdoc-import.py` — celui-ci utilise psycopg2 sans cap 1000 et fait
   `INSERT ... ON CONFLICT DO NOTHING` purement additif) a écrit dans
   `pieces_media_img` un mix de :
   - identifiants TecDoc bruts dans `pmi_name` au lieu de filename résolu ;
   - folder vide ;
   - parfois la valeur folder (21/50/95) écrite dans la mauvaise colonne (`pmi_pm_id`).
   Pattern compatible avec un read PostgREST capé à 1 000 lignes silencieux qui
   pilote ensuite un delete-reinsert (cf. mémoire interne `feedback_supabase_js_1000_row_cap_data_loss`).

2. **Fichiers jamais migrés** : les fichiers images pour les folders concernés
   (VALEO `21`, SKF `50`, et brand media pour les nouveaux produits) **n'ont
   jamais été présents** dans le bucket `rack-images`. Probablement, la migration
   PHP→Supabase n'a copié qu'un sous-ensemble (folders `30, 95, 141, 260, …`).
   Le bug est resté invisible tant que les pièces concernées étaient `display=false`.

3. **Fallback frontend insuffisant** : le composant produit utilise `no.png`
   uniquement si **aucune** ligne `pmi_display='1'` n'existe — il ne détecte
   pas le 400 imgproxy au runtime. Le soft-hide Tier C remet la condition
   "aucune ligne" → fallback `no.png` s'active.

## Mesures prises

- **Tier C soft-hide** (DB UPDATE par chunks transactionnels, 4 batches piece_id ranges).
- **Audit table** `pieces_media_img_tier_c_flipped_20260523` conservée
  (1 107 390 entrées) avec rollback prêt
  (`scripts/recovery/tier-c-softhide-malformed-p1.rollback.sql`).
- **Brand-folder registry** YAML observé écrit comme source canon
  (`.spec/00-canon/repository-registry/brand-folder-registry.yaml`).
- **Audit ratchet nightly** (`scripts/audit/audit-pieces-media-img-invariants.sh`),
  invariants I1/I2 sur pièces affichées (seuil = 0).
- **ast-grep rule** (`.ast-grep/rules/supabase-js-bulk-select-paginate.yml`) :
  bloque tout `.from(<pieces|pieces_price|pieces_media_img>).select(...)` sans
  `.range()` / `.limit()` / `.single()`.
- **Spot fix** : `shipping-calculator.service.ts:242` (`.in()` sur `pieces_price`)
  batché en chunks de 1 000.

## Mesures **non** prises (différées, décision ADR-078)

- **Vraie récupération images** (Tier B-rev) : nécessite l'accès aux brand media
  archives (VALEO Brand Connect / SKF VSM / TecDoc t216 documents). Aucun de ces
  flux n'est actuellement câblé. Non scopé sans owner input.
- **Soft-hide inventaire hidden** (~3,89 M lignes malformées sur pièces
  `display=false`) : pas d'impact UX courant — flag potentiel si ces pièces
  sont un jour réactivées. À traiter alors.

## Vérification post-fix

- `audit-pieces-media-img-invariants.sh` → I1=0, I2=0 sur pièces affichées.
- Re-comptage par marque : 0 pièce affichée avec ligne `pmi_display='1'`
  malformée (VALEO/SKF passent de 100 % cassées à 100 % `no.png` ;
  MAGNETI passe de 82 % cassées à 18 % avec image réelle + 82 % `no.png`).
- Cache Redis `pieces:detail:*` scanné : 0 clé (TTL court, pas d'invalidation
  nécessaire).

## Apprentissages → règles canon

1. Tout import bulk supabase-js qui driveune write DOIT paginer `.range()`.
   Garde mécanique ast-grep installée.
2. Tout flag `pmi_display='1'` doit garantir que `(pmi_folder, pmi_name)`
   résout effectivement vers un fichier storage. Garde nightly installée.
3. Le composant produit doit aussi détecter le 400 imgproxy au runtime
   (HEAD probe ou `<img onError>`) — **TODO** non urgent vu le soft-hide.
4. Brand→folder registry promu canon L2 (ADR-058) ; toute future ingestion
   image valide `(pmi_pm_id, pmi_folder)` contre ce registre.
