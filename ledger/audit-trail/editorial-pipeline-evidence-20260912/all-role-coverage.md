# Édition éditoriale — couverture de tous les rôles demandés

Date : 12 septembre 2026. Extension de périmètre reçue de Marwane : R1, R2, R3,
R6, R7, R8, R9. Cette matrice est une preuve de travail, pas un nouveau canon.

## Scan

Base applicative et `origin/main` vérifiés : `0c31807c8453c251d70c7575eafcc973f04eed14`.
Références d'autorité : `.spec/00-canon/role-matrix.md` v5 ;
`packages/seo-roles/src/canonical.ts` ; contrats `packages/seo-role-contracts/src/contracts/` ;
WIKI `_meta/schema/exports-seo.schema.json` et `_scripts/build_exports_seo.py` ;
Vault ADR-031, ADR-090. Lectures ciblées ; périmètre exact dans `coverage.json`.

**Écart de nomenclature R9** : la demande mentionne R9, mais le canon et le code
marquent `R9_GOVERNANCE` déprécié et renvoient à G1–G5. Aucun contrat de page R9
n'est enregistré. La consigne complémentaire confirme l'audit de la dépréciation
et des appels résiduels vers G*, sans réactivation. La ligne R9 demeure dans le
périmètre ; aucune nouvelle page publique ni clarification bloquante.

## Analysis — matrice de couverture

« Présent » désigne du code lu. « Testé » désigne des fixtures hors runtime.
« Activé » exige une preuve de configuration courante, qui n'a pas été collectée
pour ces parcours publics. Les tests du writer ne prouvent ni l'admission en amont,
ni la qualité du contenu, ni sa publication. Le pipeline RAG chatbot est un
consommateur parallèle : aucune édition SEO ne doit dépendre de son index.

| Rôle / intention | Sources admissibles selon contrat | Édition et validation examinées | Projection / indexation | Rendu final repéré | Fraîcheur / retraits | Duplication / interactions | Preuves et statut |
|---|---|---|---|---|---|---|---|
| R1 — trouver la gamme compatible | Gamme canonique, taxonomie, familles, variantes et critères de compatibilité | Contrat router ; slots existants lus via RPC. Contrat indique producteur WIKI→R1 encore à construire. Gate de texte et sélection véhicule examinées. | Writer générique testé pour R1. R1 absent des rôles gamme par défaut du builder et du feeder : pas de raccordement automatique démontré. | `pieces.$slug.tsx` : hero, sélecteur, blocs éditoriaux et ressources associées depuis API/DB. | Garde miroir commune testée ; invalidation des slots/cache depuis source retirée non raccordée par ce lot. | Séparer navigation R1, transaction R2, choix R6 et intervention R3. Signature catalogue conservée. | E1/E2/E3/E4 ; parcours code repéré, projection mécanique testée ; édition WIKI et rendu du candidat non couverts, activation non vérifiée. |
| R2 — acheter la référence exacte compatible | Catalogue, compatibilité exacte, références OEM/OES, prix/stock/shipping réels | Contrat R2, signature catalogue, éligibilité structurelle. `r2-enricher.service.ts` lit encore le miroir RAG : dette de raccordement à la connaissance qualifiée. Aucune donnée commerciale runtime modifiée. | Writer générique R2 testé ; R2 absent de l'admission gamme par défaut. Conditions d'indexabilité produit distinctes de R8 testées. | Route `pieces.$gamme.$marque.$modele.$type[.]html.tsx` → `piecesVehicleLoader` → grille/liste compatible. | Historique de projection et absence de nouvelles versions au rejeu testés ; retrait source jusqu'au catalogue, cache et rendu non démontré. | R2/R8 n'est qu'une paire : contrôler aussi R1/R2 et R2/R6. Même catalogue doit conserver sa signature malgré les variations de texte. | E1/E2/E3/E5 ; preuve structurelle isolée, aucun parcours transactionnel live exécuté ; raccordement éditorial et activation non vérifiés. |
| R3 — intervenir correctement | Procédure validée, sécurité, outils, étapes, anti-erreurs et contrôles post-intervention | Qualification WIKI et garde projection ; candidat #86 non promu. Aucun contenu de sécurité n'est fabriqué pour satisfaire le score. | Export gamme/diagnostic S2_DIAG prévu ; writer et canary role-scoped. Tables SEO vides dans l'inventaire lu. | `blog-pieces-auto.conseils.$pg_alias.tsx` ; les 44 tests antérieurs prouvent encore `legacy`, même READY_FOR_RENDER. Renderer P2-R3-E manquant. | Anciennes versions conservées ; retrait causal et caches non raccordés. | R3/R6 : intervenir vs choisir ; R3/R5 : agir vs orienter un symptôme ; maillage sans absorption de la promesse voisine. | E1/E2/E3/E6 ; frontière de rendu testée, bout en bout WIKI→navigateur non couvert. |
| R6 — choisir avant achat | Critères, références/compatibilité, niveaux de qualité, comparaisons et pièges d'achat sourcés | Contrat guide et quality gates présents. Le fetcher legacy lit encore RAG et fichiers supplémentaires et assigne confidence=1.0 : présence du texte ne prouve pas son autorité. Pas de seuil remplacé arbitrairement. | Blocks R6 `selection_criteria`, `quality_tiers`, `selection` dans le builder. Writer et admission testés ; connexion au lecteur public R6 non démontrée. | `blog-pieces-auto.guide-achat.$pg_alias.tsx` → R6 API → `__seo_gamme_purchase_guide` ; probe de redirection R6→R3 sous flag, testé sans activation. | Rejeu mécanique testé ; retrait de source jusqu'au guide et aux caches non couvert. | Guide d'achat ≠ listing R2 ; procédure R3 ne remplace pas le guide. Redirection flaggée n'est pas une preuve d'identité éditoriale. | E1/E2/E3/E7 ; mapping export présent/testé ; sources legacy et rendu du candidat restent à raccorder. |
| R7 — entrer par la marque | Entité marque, modèles, familles, accès véhicules, faits et FAQ curés | `BrandEditorialService` DB → composeur R7 → score/gates. Correctif candidat : aucune FAQ inventée ; un score élevé ne lève plus un hard gate. Autres textes génériques du composeur restent à qualifier. | Export constructeur accepte les blocks structurés explicites ; pas de mapper automatique de la FAQ DB vers le WIKI observé. Writer R7 et admission testés. | `constructeurs.$brand[.]html.tsx` → `brandApi.getR7Content` → blocs DB optionnels. | Aucun graphe source→FAQ/blocks/cache actif vérifié. La correction ne retire pas les anciennes FAQ déjà persistées. | R7/R8 : navigation marque vs identité véhicule ; cross-surface URLs contrôlées par validateur existant ; variantes de marque à comparer sur preuves propres. | E1/E2/E3/E8 ; composition et gate testés, aucun contenu existant republié, activation non vérifiée. |
| R8 — entrer par un véhicule précis | Identité véhicule, générations/motorisations, catalogue compatible, usure et entretien sourcés par moteur | Composeur owned editorial existant, 30 tests antérieurs réutilisables. Enricher legacy peut encore appeler `VehicleRagGeneratorService` : chemin producteur RAG à re-sourcer, pas à réactiver. | Builder véhicule projette les blocs par moteur ; writer/admission R8 testés. Aucune généralisation du consommateur R3. | Wrapper `.html` → `constructeurs.$brand.$model.$type.tsx` → données véhicule et blocs R8. | Rejeu testé ; source moteur retirée → blocks DB/cache/rendu non démontré. | R7/R8, moteurs frères, R1/R8, R2/R8 ; fiche véhicule sans absorber une liste transactionnelle ni une procédure. | E1/E2/E3/E7 + 30 tests R8 antérieurs ; contenu candidat au navigateur et activation non vérifiés. |
| R9 — dépréciation vers G* | Canon actuel : données QA, fingerprints, versioning, voisinages, décisions de gates G* | Pas de contrat public R9 ; `getContract(R9_GOVERNANCE)` rejeté. G1 pureté, G2 diversité, G3 collisions, G4 publication, G5 revue traversent tous les rôles. | Page/index R9 non applicable au canon actuel. Aucun nouvel identifiant ni moteur ajouté. | Sorties internes PASS/REVIEW/BLOCK ; aucun renderer public R9 à inventer. | Traces de décision et versions ; couvrir les retraits transversalement. | Une collision ne se résout pas en créant un rôle public « gouvernance ». | E1 + deux suites rôles/matrice74 PASS ; dépréciation et compatibilité examinées. Couverture G* partielle, sans réactivation R9. |

### Autres identifiants rencontrés en vérifiant « tous les R »

| Identifiant | Statut vérifié et limite |
|---|---|
| R0_HOME | Rôle public canonique, contrat présent ; couvert par les tests partagés d'indexabilité, pas par une preuve d'édition/rendu de home dans ce lot. |
| R4_REFERENCE | Contrat présent ; export gamme et writer existants. Ne pas absorber sa définition dans R3/R6. Pas de preuve navigateur dédiée dans ce lot. |
| R5_DIAGNOSTIC | Matrice métier conserve la promesse d'orientation ; contrat de page indexable absent/sunset dans le package courant. Builder refuse R5 public et n'admet diagnostic qu'en R3/S2_DIAG selon ADR-027. Ce n'est pas une permission de supprimer une page. |

## Parcours représentatifs et contre-exemples

Ces parcours désignent les points d'exécution réels ; leurs contenus sont des
fixtures, pas des affirmations mécaniques validées ni des pages publiées.

- **R1** : gamme → sélection véhicule → lien R2. Cache miss/hit et erreur RPC testés ;
  contenu symptom-first refusé. Familles insuffisantes déclenchent le verdict
  d'indexabilité existant. L'édition WIKI→slots demeure manquante.
- **R2** : fixture de références OEM compatibles → signature déterministe →
  éligibilité. Permuter les entrées conserve le hash ; références différentes le
  changent ; jeux vides ne produisent pas un faux chevauchement. Produit incomplet
  ou variante dupliquée refusé par la politique existante.
- **R3** : projection disponible → décision de service → corps legacy. Contre-exemple :
  READY_FOR_RENDER ne signifie pas « rendu projeté ». Procédure non sourcée et texte
  contradictoire restent des problèmes de qualification, même avec un score élevé.
- **R6** : section de choix structurée WIKI → bloc R6 → writer R6 isolé ; API guide
  publique encore séparée. Redirection activable seulement si cible R3 vivante,
  flag OFF = zéro requête du probe. Un guide ne peut être certifié par la seule
  lecture de son texte depuis le miroir RAG.
- **R7** : une FAQ curée → même Q/R dans le bloc, sans complément inventé. Source
  absente → pas de FAQ, MISSING_FAQ conduit à REVIEW_REQUIRED ; score 100 ne la
  rend pas publiable. Candidat complet et gates satisfaits conserve PUBLISH ;
  candidat structurellement cassé conserve REJECT. Cela teste une décision, pas
  une action de publication.
- **R8** : connaissance par moteur → bloc R8 ; absence de données structurées ne
  crée pas de filler. Les fixtures owned-editorial couvrent le choix des ancrages,
  la FAQ et les variations moteur. Le writer R8 ne réécrit pas le bloc R2 voisin.
- **R9/G*** : un rôle public déprécié ne reçoit pas de contrat par défaut. Source
  inconnue, collision d'intention et guard échoué doivent rester des décisions
  de revue/blocage ; leur assimilation à un contenu R9 reste interdite.

### Interactions à conserver dans le raccordement

Une source partagée peut impacter plusieurs rôles, mais chacun garde sa promesse.
ADR-090 C1 désigne `__rag_change_events` et `rce_impacted_roles[]` comme outbox
canonique, avec coalescing et dédup par entité×rôle. Ne pas créer un second moteur.
La preuve du writer vérifie l'isolation des blocs pour R1/R2/R3/R6/R7/R8 et le
no-op des versions identiques ; elle ne prouve pas que les événements de retrait
sont émis ou consommés. L'absence de nouveaux blocs dans un export n'est pas,
à elle seule, une instruction de retrait de tous les blocs historiques.

## Correction autorisée, proposée à la livraison

1. **Sync** : préflight complet avant copie ; exports retirés/fichiers historiques
   non réconciliés → UNRECONCILED, exit 1, fichiers conservés, ancien synced_at
   conservé. Refus des sous-dossiers source qui aplatiraient les topics et des
   symlinks miroir. Pas de suppression ni de prétendue invalidation de l'index.
2. **R7** : FAQ limitée aux entrées DB curées ; garde de présence/boilerplate/qualité
   échouée ne devient plus PUBLISH grâce au score. Aucun seuil, metadata SEO,
   URL, ligne DB ou statut de page existante modifié.
3. **Exports SEO WIKI** : préflight du lot avant écriture ; ancien export sans source
   éligible → UNRECONCILED et erreur, preuve conservée. Scope single-entity borné ;
   le dry-run expose aussi le retrait. Aucun tombstone ni retrait aval exécuté.
4. **Tests de projection** : extension des tests du writer existant aux six rôles
   publics demandés ; aucune nouvelle architecture de projection.

Ces correctifs sont dans le worktree applicatif, sans commit/push/activation.

## Validation

- **E1** `all-role-contract-tests.log` : 73 tests (conformance, cascade d'indexabilité,
  frontières lexicales). R9 rejeté ; tests de structure, pas jugement factuel.
- **E2** `all-role-projection-tests.log` : 20 tests, dont 12 nouveaux cas d'isolation
  et de rejeu couvrant R1/R2/R3/R6/R7/R8 ; DB simulée, admission amont séparée.
- **E3** `all-role-targeted-tests.log` : 69 tests dans cinq suites (R7 initial 4,
  validateur de rôle, R1 cache/RPC, R6 redirection, gate projection). Complément
  `r7-and-role-admission-tests.log` : 21 tests (R7 final 6 + feeder 15).
  Les comptes se recouvrent ; ne pas les additionner comme des tests uniques.
- **E4** `sync-withdrawal-baseline.log` : 4 nouveaux cas échouent avant le correctif ;
  `sync-withdrawal-tests.log` : 14 tests passent après. Corpus temporaire uniquement.
- **E5** `r2-structure-tests.log` : 14 tests signature/éligibilité ; aucune commande,
  écriture catalogue ou opération commerciale exécutée.
- **E6** `r3-serving-proof.log` : 44 tests antérieurs inchangés, réutilisés.
- **E7** `wiki-withdrawal-tests.log` : 68 tests du builder natif, dont 13 nouveaux cas
  couvrant les six rôles explicites et le refus de R9, puis 5 cas CLI de retrait/rejeu.
  Quatre échecs avant correction dans `wiki-withdrawal-baseline.log`. Le passage
  intermédiaire à 63 tests est conservé dans `all-role-wiki-export-tests.log`.
  Mapping, schéma, source et absence de filler testés sans corpus réel.
  Hooks WIKI sur les trois fichiers modifiés PASS (`wiki-all-role-hooks.log`).
- **E8** `r7-editorial-baseline.log` : 4 échecs reproductibles avant correction.
  R7 final : 6 PASS dans E3. Lint des trois fichiers TS et typage backend complet
  PASS (`all-role-lint.log`, `all-role-typecheck.log`, sorties vides avec exit 0).

RAW 296, acquisitions Nest 25, RAG 25, scorer 96 et owned-editorial R8 30 : preuves
antérieures réutilisées uniquement sur les périmètres inchangés. L'inventaire live
précédent reste daté : v2 absent, tables de projection vides ; pas de nouveau sondage
identique ni de conclusion sur des flags publics non lus.

## Verdict et suite

**PARTIAL_COVERAGE**. Corrections sync/exports SEO/R7 **VALIDATED_FOR_SCOPE_ONLY**. Tous les rôles
demandés ont une ligne explicite ; aucun n'est déclaré activé sur la base d'un test.

Ordre de raccordement étayé : (1) contrat de retrait/tombstone→outbox et dépendances
exactes ; (2) resourcer les producteurs legacy R2/R6/R8, préparer WIKI→R1 et
WIKI→R7 sans source concurrente ; (3) compléter le renderer/consumer propre à chaque
rôle ; (4) preuve représentative WIKI qualifiée→page visible en environnement
isolé, puis activation/publication séparément autorisées. R9 reste un alias déprécié
vers G* ; le score ou le gabarit ne peut pas en inventer un nouveau rôle public.

Le schéma de manifest RAG annonce `tombstone`, mais `scripts/tools/wiki_ingester.py`
consomme un ancien format content/source_path et n'en implémente pas le retrait.
Le nouvel importeur F5 ne réconcilie pas les anciennes versions et sa collection
cible est absente. Ces contrats et états doivent être alignés avant une migration ;
ce lot n'exécute aucune suppression, migration, publication ni activation.

### Contrat de retrait proposé à revue, sans autorité normative

Le raccordement destructif n'est pas déduit d'un diff de fichiers. Proposition
concrète pour le prochain lot, à faire ratifier dans le canon existant :

1. Utiliser le tombstone du manifest existant avec l'identité et le hash exact de
   la version retirée ; provenance du commit WIKI et snapshot complet vérifiables.
   Une source absente, illisible ou non approuvée bloque le run sans inventer ce signal.
2. Résoudre ses dépendances à partir des source_ids enregistrés et des versions
   actives ; si une dépendance ou une identité d'index manque, HOLD observable.
   Ne pas assimiler les 619 lignes SQL aux 9945 objets Weaviate legacy.
3. Passer par le writer versionné et l'outbox `__rag_change_events` désignés par
   ADR-090. Émettre seulement les rôles impactés ; rejouer le même retrait doit être
   un no-op. Conserver les snapshots et anciennes versions comme preuve de rollback.
4. Tester source partagée R1/R6, R2/R8, R3/R6 et marque/véhicule : retirer une
   source n'invalide ni un rôle sans dépendance ni une autre version autorisée.
   Refuser un tombstone visant le mauvais hash, une source inconnue, une projection
   hors allowlist, une ingestion partielle et un événement rejoué hors ordre.
5. Raccordement aux index/caches/public : définir la décision de serving dans le
   contrat de chaque consommateur avant activation. Ne pas laisser un fallback
   legacy réintroduire automatiquement le contenu retiré, et ne pas modifier les
   URLs, HEAD optimisés ou indexabilité publique sans l'accord SEO requis.

ADR-090 §A impose « review @fafa + ADR amendment si comportement change » pour
l'évolution de signature du writer. CLAUDE invariant 9 réserve « SEO indexé » à
l'accord nominatif. Le lot présent ne modifie donc ni cette signature, ni une
allowlist, ni l'index réel : il apporte les corrections isolées et le dossier
nécessaire pour examiner ce prochain changement sans prétendre l'avoir activé.

## Complément consolidation et R9

[[ledger/audit-trail/editorial-pipeline-evidence-20260912/method-consolidation|Matrice des méthodes]] :
retraits index ciblés désormais testés, invalidation WIKI/SEO toujours absente. R9 doit être
couvert comme dépréciation vers G*, sans réactivation : la clarification antérieure n'est plus
bloquante. Enum legacy, affichages et matrice sont des consommateurs de compatibilité ; les
sorties canoniques rejettent R9. Deux suites de rôles/matrice :74 PASS.
