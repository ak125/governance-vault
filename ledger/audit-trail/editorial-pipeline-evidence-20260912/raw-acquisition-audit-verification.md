# Collecte RAW et richesse WIKI — 14 septembre 2026

## scan

Périmètre ciblé : collecteur HTML natif RAW, transport HTTPS et diagnostic de boucle WIKI. Trois fichiers, extraits ciblés ; chemins, symboles, lignes et SHA256 dans [preuves](raw-acquisition-audit-evidence.json), exclusions dans [manifest](raw-acquisition-audit-coverage.json). Pas de benchmark, de nouvelle capture ou d'inspection exhaustive des autres exécutants.

## analysis

1. `auto-capture-runner.py:main` refuse explicitement la découverte autre que `provided`. Il consomme des URL fournies ; activer `auto` ne crée pas un moteur de recherche et contreviendrait à son contrôle de provenance.
2. `capture_one` vérifie politique, transport, extraction, longueur minimale de 200 caractères, hash et validation d'archive. Aucun de ces contrôles ne démontre que le document comble le besoin éditorial. `main` utilise la première capture réussie pour la transition de disponibilité de la worklist ; cela n'est pas une validation sémantique.
3. `Transport.request` envoie un GET sans If-None-Match/If-Modified-Since et attend 200. Ce chemin ne réutilise pas une archive via 304. Déduplication après téléchargement ; `existing_hashes` relit les captures Markdown à chaque appel. Risque de coût à mesurer, pas de lenteur quantifiée ici.
4. `stage_raw` compte seulement les Markdown de `sources/web-research/<slug>` et un éventuel index. Les captures `sources/auto-captures` ne sont pas comptées par ce contrôle. Son PASS porte sur la présence de fichiers, pas sur leur richesse. La promotion native contrôle séparément les preuves et ne doit pas être remplacée par ce compteur.
5. Le CLI de boucle annonce lui-même que les sources doivent déjà exister : son rôle est diagnostique, sans collecte ni planification. Cette constatation ne prouve pas l'absence d'un autre exécutant ailleurs.

## correction (proposée)

Ordre de construction recommandé, en réutilisant les contrats et points d'entrée natifs :

- Décrire le manque avant recherche : entité, bloc/usage client, question, contexte véhicule/moteur/référence et preuve attendue. Exemple : quel clapet remplit quel rôle, dans quelle architecture, avec quelles exceptions ?
- Rechercher et sélectionner des sources primaires pertinentes, avec provenance de découverte traçable. Les sources concurrentes servent éventuellement à identifier des questions, pas à certifier des faits techniques.
- Capturer les formats nécessaires avec contrôles existants conservés : HTML, puis filière PDF/tableaux lorsqu'elle est justifiée et contractualisée. Pas de contournement des restrictions ni de changement arbitraire de MIME. Mesurer extraction vide, passages manquants et tableaux perdus.
- Conserver archive et versions, URL, date, contexte, passages, unités et restrictions. Regrouper doublons exacts puis examiner les quasi-doublons sans confondre moteurs, millésimes et références.
- Évaluer chaque passage contre la question initiale : preuve directe, conditions applicables, contradiction éventuelle. Un manque reste ouvert si l'information n'est pas obtenue. Une similarité ou un score élevé ne suffit pas à le fermer.
- Relier les faits qualifiés au WIKI, puis adapter leur sélection aux consommateurs R/RAG. Prix, stocks et compatibilités vivantes gardent leur source métier appropriée. Ne pas publier les mêmes paragraphes sur toutes les pages.
- Optimiser ensuite avec suivi par URL, revalidation HTTP conditionnelle, budgets par domaine, reprise contrôlée et index d'empreintes réutilisable. Une réponse 304 exige une archive antérieure encore disponible et intègre ; une source inaccessible reste bloquée, sans boucle de tentatives illimitée.

Mesures à séparer : fiabilité de capture (succès, délais, erreurs), fidélité d'extraction (passages/tableaux conservés), couverture des besoins (ouverts/résolus avec preuve), fraîcheur, contradictions et réutilisation utile. Aucun score global de volume ne remplace ces contrôles. La couverture dépend d'un inventaire de besoins lui-même validé ; les 15 claims du pilote n'établissent pas l'exhaustivité.

Références externes vérifiées : [RFC9110 §13 — requêtes conditionnelles](https://www.rfc-editor.org/rfc/rfc9110.html#section-13), [Google — contenu utile et fiable](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), [Google — fonctionnalités IA et fondamentaux SEO](https://developers.google.com/search/docs/appearance/ai-features). Ces sources justifient les principes, pas la performance de notre code ni une garantie de classement.

## validation

Inspection statique seulement ; empreintes et état des candidats enregistrés. Aucun code RAW/WIKI ni contenu métier changé dans ce lot, aucun test de débit ou de pertinence exécuté. Tests antérieurs non rejoués pour ce diagnostic documentaire. Le défaut de contrat gamme (17 erreurs du lot wiki-consumers) reste ouvert ; ce rapport ne le corrige pas et ne rend pas le WIKI exportable.

## verdict

PARTIAL_COVERAGE. Diagnostic du chemin inspecté étayé ; architecture proposée, non implémentée. Prochain lot : vérifier les contrats natifs de demande/découverte/qualification et leur consommateur, puis corriger la transition mesurable besoin → preuve. Conserver la correction des 17 erreurs de contrat WIKI dans les travaux ouverts. Ni activation, ni publication, ni modification de runtime.
