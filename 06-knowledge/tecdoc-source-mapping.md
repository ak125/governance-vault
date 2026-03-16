# TecDoc Source Mapping — Document A

> **Version** : 1.0.0
> **Date** : 2026-03-15
> **Source** : `CreateTablesTAF24.sql` (TAF 2.7)
> **Scope** : Phase 1 (t001, t100, t200, t209, t210)

---

## Convention

- **DLNR** = Data Supplier Number (identifie le fournisseur, ex: 730 = Bosch)
- **ARTNR** = Article Number (reference article chez le fournisseur)
- **SA** = constante table (toujours = numero de table)
- **LOSCH_FLAG** = 1 = marque pour suppression (delta delivery)
- **BEZNR** = numero de description (jointure vers table 030 pour textes multilingues)
- **LKZ** = Country Code
- **PK source** = cle primaire dans le schema TecDoc MySQL

---

## t001 — Header (version fournisseur)

| Colonne | Type MySQL | Sens metier | PK | Nullable |
|---------|-----------|-------------|-----|----------|
| DLNR | smallint(4) | Fournisseur ID | **PK** | NOT NULL |
| SA | smallint(3) | Constante = 1 | — | NOT NULL |
| DATA_RELEASE | smallint(4) | Version (format xxyy) | — | NOT NULL |
| DATUM | int(8) | Date version YYYYMMDD | — | NOT NULL |
| KZVOLL | tinyint(1) | 1 = livraison complete | — | NOT NULL |
| KHERNR | mediumint(6) | Numero constructeur vehicule | — | NOT NULL |
| MARKE | varchar(20) | Marque (TecDoc) | — | NOT NULL |
| REFERENZDATEN | mediumint(4) | Version reference data (xxyy) | — | NOT NULL |
| VORVERSION | mediumint(4) | Version precedente (delta) | — | NULL |
| FORMAT | varchar(3) | Version format (2.x) | — | NOT NULL |
| LOSCH_FLAG | tinyint(1) | 1 = supprimer tous les articles de la marque | — | NOT NULL |

**Role** : 1 ligne par fournisseur. Indique la version de ses donnees et si c'est un envoi complet ou delta.

---

## t100 — Manufacturers (fournisseurs)

| Colonne | Type MySQL | Sens metier | PK | Nullable |
|---------|-----------|-------------|-----|----------|
| DLNR | smallint(4) | Constante = 9999 | — | NOT NULL |
| SA | smallint(3) | Constante = 100 | — | NOT NULL |
| HERNR | mediumint(6) | Numero fabricant unique | **PK** | NOT NULL |
| HKZ | varchar(10) | Code court fabricant | — | NOT NULL |
| LBEZNR | int(9) | Description (→ 012) | — | NOT NULL |
| PKW | tinyint(1) | Fabricant auto | — | NOT NULL |
| NKW | tinyint(1) | Fabricant poids lourd | — | NOT NULL |
| VGL | tinyint(1) | Fabricant comparatif | — | NOT NULL |
| ACHSE | tinyint(1) | Fabricant essieux | — | NOT NULL |
| MOTOR | tinyint(1) | Fabricant moteurs | — | NOT NULL |
| GETRIEBE | tinyint(1) | Fabricant transmissions | — | NOT NULL |
| TRANSPORTER | tinyint(1) | Fabricant utilitaires | — | NOT NULL |
| DELETE | tinyint(1) | 1 = propose pour suppression | — | NOT NULL |

**Role** : referentiel des fabricants (Bosch, Valeo, TRW, etc.). HERNR = cle unique.

---

## t200 — Main Articles

| Colonne | Type MySQL | Sens metier | PK | Nullable |
|---------|-----------|-------------|-----|----------|
| ARTNR | varchar(22) | Reference article fournisseur | **PK** | NOT NULL |
| DLNR | smallint(4) | Fournisseur ID | **PK** | NOT NULL |
| SA | smallint(3) | Constante = 200 | — | NOT NULL |
| BEZNR | int(9) | Description (→ 030) | — | NULL |
| KZSB | tinyint(1) | Self-service packing | — | NULL |
| KZMAT | tinyint(1) | Certification materiau obligatoire | — | NULL |
| KZAT | tinyint(1) | Piece remanufacturee | — | NULL |
| KZZUB | tinyint(1) | Accessoire | — | NULL |
| LOSGR1 | mediumint(5) | Taille lot 1 | — | NULL |
| LOSGR2 | mediumint(5) | Taille lot 2 | — | NULL |
| LOSCH_FLAG | tinyint(1) | 1 = supprimer | — | NOT NULL |

**Role** : table principale des articles. PK = (ARTNR, DLNR).
**Mapping AutoMecanik** : `piece_ref` = ARTNR, `piece_pm_id` = DLNR.

---

## t209 — EAN List

| Colonne | Type MySQL | Sens metier | PK | Nullable |
|---------|-----------|-------------|-----|----------|
| ARTNR | varchar(22) | Reference article | **PK** | NOT NULL |
| DLNR | smallint(4) | Fournisseur ID | **PK** | NOT NULL |
| SA | smallint(3) | Constante = 209 | — | NOT NULL |
| LKZ | varchar(3) | Country Code | — | NULL |
| EANNR | varchar(14) | Code EAN | **PK** | NOT NULL |
| EXCLUDE | tinyint(1) | 1 = exclusion pays | — | NULL |
| LOSCH_FLAG | tinyint(1) | 1 = supprimer | — | NOT NULL |

**Role** : codes barres EAN par article. PK = (ARTNR, DLNR, EANNR).
**Mapping AutoMecanik** : `pieces_ref_ean.pre_piece_id` (via ARTNR+DLNR), `pre_code_ean` = EANNR.

---

## t210 — Fixed Article Criteria

| Colonne | Type MySQL | Sens metier | PK | Nullable |
|---------|-----------|-------------|-----|----------|
| ARTNR | varchar(22) | Reference article | **PK** | NOT NULL |
| DLNR | smallint(4) | Fournisseur ID | **PK** | NOT NULL |
| SA | smallint(3) | Constante = 210 | — | NOT NULL |
| RESERVIERT | varchar(5) | Ancien GenArtNr (obsolete) | — | NULL |
| LKZ | varchar(3) | Country Code | — | NULL |
| SORTNR | smallint(3) | Ordre affichage | **PK** | NOT NULL |
| KRITNR | smallint(4) | Numero critere (KT 050) | — | NOT NULL |
| KRITWERT | varchar(20) | Valeur critere | — | NOT NULL |
| ANZSOFORT1 | tinyint(1) | Afficher = 1 | — | NULL |
| EXCLUDE | tinyint(1) | 1 = exclusion pays | — | NULL |
| LOSCH_FLAG | tinyint(1) | 1 = supprimer | — | NOT NULL |

**Role** : criteres techniques fixes par article (dimensions, specifications). PK = (ARTNR, DLNR, SORTNR).
**Mapping AutoMecanik** : `pieces_criteria.pc_piece_id` (via ARTNR+DLNR), `pc_cri_id` = KRITNR.
