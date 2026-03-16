# role-migration-registry.md

> **Version** : 1.0.0
> **Date** : 2026-03-14
> **Source** : legacy-canon-map.md V1.1.0
> **Complement de** : role-implementation-map.md

---

## Registre de migration legacy → canonique

Suivi exhaustif de chaque point de dette legacy dans le code, avec son statut de migration.

### Backend

| Fichier | Type dette | Alias legacy | Canon cible | Statut | Pass | Risque |
|---------|-----------|-------------|-------------|--------|------|--------|
| `role-ids.ts` | enum | R9_GOVERNANCE | @deprecated | deprecate + blocked in output | P1+P5 | R0 |
| `role-ids.ts` | mapping | R3_guide, R3_BLOG, etc. | LEGACY_ROLE_ALIASES (8 entries) | normalizeRoleId() | P1 | R0 |
| `role-ids.ts` | guard | — | assertCanonicalRole() | blocking mode | P3+P5 | R0 |
| `content-refresh.service.ts` | hardcode | R3_guide_howto, R3_conseils | PAGE_TYPE_TO_CANONICAL_ROLE | commente + logged | P1+P3 | R0 |
| `buying-guide-enricher.service.ts` | query | R3_guide | R6_GUIDE_ACHAT | commente + logged | P1+P3 | R0 |
| `content-refresh.types.ts` | union | PageType (7 values) | PAGE_TYPE_TO_CANONICAL_ROLE | bridge mapping | P1 | R0 |

### Frontend

| Fichier | Type dette | Alias legacy | Canon cible | Statut | Pass | Risque |
|---------|-----------|-------------|-------------|--------|------|--------|
| `page-role.types.ts` | enum | R3_BLOG = "R3" | @deprecated, LEGACY_PAGE_ROLE_MAP | deprecate + normalize | P1 | R0 |
| `page-role.types.ts` | mapping | R3_BLOG, R3_guide, R3 | normalizeLegacyPageRole() | legacy-first priority | P1+P3 | R0 |
| `page-role.types.ts` | util | — | getRoleCategory(), ROLE_BADGE_COLORS | canonical UI layer | P4 | R0 |
| `admin.page-role.tsx` | hardcode | bare R1-R6 colors | ROLE_BADGE_COLORS + normalization | migrated | P4 | R0 |
| `admin.rag.cockpit.tsx` | label | R3_guide | R6_guide_achat | fixed | P4 | R0 |
| `admin.content-refresh.tsx` | label | missing R6 | R6_guide_achat added | fixed | P4 | R0 |
| `admin.rag.pipeline.tsx` | label | missing R6 | R6_guide_achat added | fixed | P4 | R0 |

### Documentation / Agents

| Fichier | Type dette | Alias legacy | Canon cible | Statut | Pass | Risque |
|---------|-----------|-------------|-------------|--------|------|--------|
| `page-roles.md` | label | R3/conseils, R3/guide-achat | R3_CONSEILS, R6_GUIDE_ACHAT | updated | P2 | R0 |
| `guide-achat-role.md` | identity | R3_BLOG | R6_GUIDE_ACHAT | updated | P2 | R0 |
| `conseils-role.md` | identity | R3_BLOG | R3_CONSEILS | updated | P2 | R0 |
| `brief-enricher.md` | refs | mixed R3/R6 | canonical | updated | P2 | R0 |
| `blog-hub-planner.md` | routing | R3_BLOG | R3_CONSEILS / R6_GUIDE_ACHAT | updated | P2 | R0 |

### Database (futur)

| Table/Objet | Type dette | Valeur legacy | Canon cible | Statut | Risque |
|-------------|-----------|--------------|-------------|--------|--------|
| DB CHECK constraint | schema | `page_type IN ('R1_pieces','R3_guide_howto','R3_conseils','R4_reference','R5_diagnostic')` | ajouter R6_guide_achat | futur | R2 |
| __seo_gamme_purchase_guide.page_role | data | R3_guide | R6_GUIDE_ACHAT | normalization layer | R1 |
| canonical_role column | schema | — | colonne derivee dans tables SEO | futur | R2 |

---

## Tests anti-regression

| Suite | Fichier | Nb tests | Couverture |
|-------|---------|----------|------------|
| Backend Jest | `role-ids.test.ts` | 30+ | normalizeRoleId, assertCanonicalRole, FORBIDDEN, LEGACY, anti-regression |
| Frontend Vitest | `page-role-normalization.test.ts` | 20+ | normalizeLegacyPageRole, isEditorialRole, getRoleCategory, ROLE_BADGE_COLORS |

---

## 4 Regles canoniques

1. **Entree legacy, sortie canonique** — aliases toleres en entree, interdits en sortie
2. **Mapping central unique** — normalizeRoleId() / normalizeLegacyPageRole()
3. **Ambiguite interdite en sortie** — R3, R6, R3_BLOG, R9 bloques par assertCanonicalRole()
4. **Logging de normalisation** — { canonicalRole, legacyInputRole, normalizationStatus }
