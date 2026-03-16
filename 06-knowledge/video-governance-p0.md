# Video Governance P0 — Spec Canonique

> **Version:** 1.0 | **Date:** 2026-02-24 | **Status:** P0 implemente
> **Verticale pilote:** FREINAGE | **Scope:** Gouvernance pure (pas de rendu)

---

## 1. Vue d'ensemble

Le systeme video Media Factory applique une gouvernance editoriale **identique** au pipeline
de contenu texte (hard-gates, evidence pack, claim ledger). P0 formalise les artefacts,
gates et contraintes — sans code de rendu (Remotion/FFmpeg = P1).

**Principe fondamental :** Toute video publiee doit etre factuelle, sourcee, et visuellement
honnete. Aucun visuel IA n'est utilise comme preuve.

---

## 2. Les 5 artefacts obligatoires (NO-GO)

Toute production video necessite ces 5 artefacts. **Sans les 5 → production bloquee.**

| # | Artefact | Description | Type TS |
|---|----------|-------------|---------|
| 1 | **Video Brief** | Type, mode, vertical, gamme, plateformes, duree cible, template | `VideoBrief` |
| 2 | **Claim Table** | Liste des affirmations avec kind, source, status | `VideoClaimEntry[]` |
| 3 | **Evidence Pack** | Preuves RAG (docId, excerpt, confidence) | `VideoEvidenceEntry[]` |
| 4 | **Disclaimer Plan** | Disclaimers requis (type, texte, position) | `DisclaimerPlan` |
| 5 | **Approval Record** | Historique d'approbation par stage | `ApprovalRecord` |

### Claim kinds video-specifiques

| Kind | Description | Validation |
|------|-------------|------------|
| `mileage` | Kilometrage, duree de vie | Evidence RAG |
| `dimension` | Dimensions, poids | Evidence RAG |
| `percentage` | Statistiques, ratios | Evidence RAG |
| `norm` | Normes techniques (ECE R90, etc.) | Evidence RAG |
| `procedure` | Geste technique | **Humain obligatoire** |
| `safety` | Recommandation securite | **Humain obligatoire + disclaimer** |

---

## 3. Les 7 gates video (G1-G7)

Pattern identique a `hard-gates.service.ts` : chaque gate retourne `VideoGateResult`
avec `{gate, verdict, measured, warnThreshold, failThreshold, details, triggerItems}`.

`canPublish = true` ssi **aucun gate FAIL**.

| Gate | Nom | Mesure | Warn | Fail | Bloquant |
|------|-----|--------|------|------|----------|
| **G1** | Truth | Ratio claims non-sources | 0.15 | 0.30 | Oui |
| **G2** | Safety | Nb claims procedure/safety sans validation humaine | 0 | 1 | **STRICT** |
| **G3** | Brand | Nb violations ton/style/interdits | 1 | 3 | Oui |
| **G4** | Platform | Deviation duree vs spec (%) | 0% | 10% | Oui |
| **G5** | Reuse Risk | Score similarite script (cosine) | 0.5 | 0.7 | Oui |
| **G6** | Visual Role | Nb visuels utilises comme preuve | 0 | 1 | **STRICT** |
| **G7** | Final QA | Nb artefacts manquants + approval | 0 | 1 | Oui |

### Gates STRICT (zero tolerance)

- **G2 Safety** : 1 seul claim procedure/safety sans validation humaine = FAIL
- **G6 Visual Role** : 1 seul visuel utilise comme preuve = FAIL

---

## 4. Les 2 modes stricts

### Mode SOCLE (film_socle)

| Contrainte | Valeur |
|-----------|--------|
| CTA commercial | Interdit |
| Promo / prix | Interdit |
| Style narratif | Documentaire |
| Claims par sequence | 1 max |
| Disclaimer requis | Oui (intro + outro) |
| Duree | 7-9 min (420-540s) |

### Mode SHORT

| Contrainte | Valeur |
|-----------|--------|
| CTA commercial | Interdit |
| Faux urgency | Interdit |
| Style narratif | Hook-first |
| Claims par sequence | 1 max |
| Disclaimer | Overlay suffisant |
| Duree | 15-60s |

### Mode GAMME (film_gamme)

| Contrainte | Valeur |
|-----------|--------|
| CTA commercial | Interdit |
| Promo / prix | Interdit |
| Style narratif | Educatif |
| Claims par sequence | 2 max |
| Disclaimer requis | Oui |
| Duree | 3-6 min (180-360s) |

---

## 5. Matrice visuels autorises / interdits

### Autorises (illustration uniquement)

| Type visuel | Usage |
|-------------|-------|
| `schema` | Schema technique stylise |
| `animation` | Animation de principe (liquide, chaleur, usure) |
| `macro` | Macro abstraite d'usure |
| `motion_text` | Texte anime (chiffres, specs) |
| `ambiance` | Ambiance atelier (IA OK) |

### Interdits comme preuve

| Type visuel | Raison |
|-------------|--------|
| `photo_reelle` sans validation | Requiert `truth_dependency = 'proof'` + validation humaine |

**Regle G6 :** Tout visuel avec `truth_dependency != 'illustration'` sans validation humaine
declanche un FAIL.

---

## 6. Patterns de contenu interdits

### Mode socle (FORBIDDEN_PATTERNS_SOCLE)

Mots/expressions bannis du script :
- achetez, commandez, promotion, prix, pas cher, meilleur prix
- livraison, en stock, offre, remise, code promo

### Mode short (FORBIDDEN_PATTERNS_SHORT)

Inclut tous les patterns socle + :
- urgent, depechez, ne ratez pas, dernier(e)(s) chance/jour

---

## 7. Tables Supabase

3 tables creees en migration P0 :

### `__video_productions`

Table maitre des productions video.

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL PK | ID auto |
| brief_id | TEXT UNIQUE | Identifiant du brief |
| video_type | TEXT | film_socle, film_gamme, short |
| vertical | TEXT | Verticale (freinage, etc.) |
| gamme_alias | TEXT | Alias gamme optionnel |
| pg_id | INTEGER | FK vers pieces_gamme |
| status | TEXT | draft → ... → published → archived |
| template_id | TEXT | ID template |
| knowledge_contract | JSONB | Contrat de connaissance |
| claim_table | JSONB | Table de claims |
| evidence_pack | JSONB | Pack de preuves |
| disclaimer_plan | JSONB | Plan disclaimers |
| approval_record | JSONB | Historique approbation |
| quality_score | INTEGER | Score 0-100 |
| quality_flags | TEXT[] | Flags qualite |
| gate_results | JSONB | Resultats des 7 gates |
| created_by | TEXT | Createur |
| created_at | TIMESTAMPTZ | Date creation |
| updated_at | TIMESTAMPTZ | Date modification |

**RLS :** active, politique service_role uniquement.
**Index :** status, vertical, pg_id.

### `__video_templates`

Templates de production versionnes.

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL PK | ID auto |
| template_id | TEXT UNIQUE | Identifiant template |
| version | INTEGER | Numero de version |
| video_type | TEXT | Type de video |
| platform | TEXT | Plateforme cible |
| allowed_use_cases | TEXT[] | Cas d'usage autorises |
| forbidden_use_cases | TEXT[] | Cas d'usage interdits |
| duration_range | JSONB | {min, max} en secondes |
| structure | JSONB | Structure du template |
| created_at | TIMESTAMPTZ | Date creation |

### `__video_assets`

Assets visuels avec validation.

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL PK | ID auto |
| asset_key | TEXT UNIQUE | Cle unique asset |
| visual_type | TEXT | schema, animation, macro, motion_text, ambiance, photo_reelle |
| truth_dependency | TEXT | illustration, proof, reference |
| tags | TEXT[] | Tags de categorisation |
| file_path | TEXT | Chemin fichier optionnel |
| validated | BOOLEAN | Valide par humain |
| validated_by | TEXT | Validateur |
| created_at | TIMESTAMPTZ | Date creation |

**Index :** visual_type, validated.

---

## 8. Fichiers source (SSOT)

| Fichier | Role |
|---------|------|
| `backend/src/config/video-quality.constants.ts` | Constantes, thresholds, enums, patterns interdits |
| `backend/src/modules/media-factory/types/video.types.ts` | Types TypeScript (artefacts, gates, production) |
| `backend/src/modules/media-factory/services/video-gates.service.ts` | Service 7 gates (G1-G7) |

---

## 9. Hors scope P0

| Element | Phase |
|---------|-------|
| Remotion / FFmpeg / rendu | P1 |
| BullMQ queue video | P1 |
| Admin UI / endpoints API | P1 |
| MediaFactoryModule NestJS | P1 |
| Smoke tests (editorial + technique + gouvernance) | P2 |
| Template registry + shot library + prompt registry | P3 |
| Quality score video | P3 |
| Multi-plateforme publish policy | P3 |

---

## 10. Verification P0

```sql
-- Tables creees
SELECT tablename FROM pg_tables WHERE tablename LIKE '__video%';
-- Attendu: __video_productions, __video_templates, __video_assets
```

```bash
# Types compilent
node --max-old-space-size=4096 node_modules/typescript/bin/tsc -p backend/tsconfig.json --noEmit

# Constantes accessibles
grep -n "VIDEO_GATE_THRESHOLDS" backend/src/config/video-quality.constants.ts

# Gates service
grep -n "VideoGatesService" backend/src/modules/media-factory/services/video-gates.service.ts
```
