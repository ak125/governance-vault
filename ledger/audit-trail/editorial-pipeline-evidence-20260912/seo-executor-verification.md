# Executants et lacune de la boucle editoriale — 13 septembre 2026

## Scan

Lecture ciblee du runtime DEV, service utilisateur knowledge-jobs, crontab actif, collecte documentaire et consigne SEO historique. Liste exacte de fichiers et recherches dans `seo-executor-coverage.json` ; mesures et empreintes dans `seo-executor-runtime.json`. SSH Hermes utilise uniquement admin-hermes ; repertoire prive du compte hermes inaccessible, aucune elevation ni modification de droits. Les anciennes mentions de AI-COS ne sont pas une configuration active.

## Analysis

Trois mecanismes distincts sont visibles. DEV repond HTTP200 et son checkout principal est a origin/main ; le controleur compile ne contient pas audit/r3. Le candidat prepare precedemment n'est donc pas prouve servi par DEV.

knowledge-jobs est un service systemd utilisateur quotidien a 08 h Europe/Paris. Son dernier passage du 13 septembre, 08:00:59 a 08:01:34, se termine sans erreur. Il copie les documents de sept depots GitHub et six racines VPS, puis reexecute la decision WIKI native sur les propositions presentes. Le bilan contient 16998 occurrences, 7343 contenus uniques et 9655 occurrences dupliquees, tous projets confondus. Ces doublons de collecte ne sont pas une mesure de duplicate content sur les pages indexees. Quinze propositions WIKI sont bloquees, zero eligible, zero promotion. Le statut validated du rapport decrit une evaluation terminee, pas quinze fiches validees.

Le code de ce service ne lit pas les audits R3 et ne transforme pas une lacune de page en recherche de nouvelles sources automobiles. Sa collecte est documentaire, sans moteur de recherche. La notification vers Hermes en fin de passage ne prouve pas que Hermes pilote une boucle editoriale. D'autres taches privees Hermes ne sont pas exclues par cette inspection.

Un cron utilisateur actif execute aussi auto-enrich-pipeline.sh toutes les trente minutes. Il attend des PDF, puis prevoit l'ingestion et un POST internal/buying-guides/enrich. Les derniers passages observes a 17:30 et 18:00 heure Paris echouent sur INTERNAL_API_KEY not set. Aucun secret n'a ete lu ni fourni. Le script run-phase-f.sh est present mais ne figure pas parmi les entrees actives du crontab inspecte. La route enrich existe dans le code amont ; aucune execution de cette route ni preuve d'ecriture actuelle n'est revendiquee.

## Correction proposee et preparee avec autorisation utilisateur

La consigne agents/seo-content/AGENTS.md conserve le protocole historique mais indique explicitement le retrait AI-COS, la necessite d'identifier l'executant et le suivi autorises, sans inventer un nouveau routage Hermes. Elle distingue maintenant storedCanSkip, renderedPage et pageReviewRequired, ainsi que controle execute et qualite prouvee. Les volumes documentaires ne doivent pas etre presentes comme des preuves nouvelles ; le lien defaut/source/capture/qualification/section doit etre etabli.

Aucune modification du service quotidien, du cron ancien ou de leurs secrets. Remettre une cle au vieux script ne serait pas une correction de la collecte ciblee. Prochaine intervention : definir le passage des lacunes observees aux captures utiles via les capacites RAW/WIKI existantes et identifier le consommateur autorise ; aucune nouvelle boucle parallele.

## Validation

Sondes GET et lectures uniquement. Validateur AGENTS sur le fichier modifie : zero blocage, zero avertissement. Diff checks cibles PASS. Pas de code applicatif change ; les 113 tests backend et quatre tests frontend du lot precedent ne sont pas relances ni presentes comme preuve du runtime. Inventaire cron filtre pour exclure les commentaires. Fraicheur amont reverifiee ; pas de changement amont sur le fichier modifie.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour la correction documentaire ; PARTIAL_COVERAGE global. Le declencheur quotidien et ses limites sont identifies, mais la boucle lacune-vers-preuve utile n'est pas etablie. Aucun commit/push/merge/deploiement, aucun lancement manuel de job, aucune ecriture DB/corpus partage, notification ou modification de droits.

[[ledger/audit-trail/2026-09-12-editorial-pipeline-codex|Rapport cumulatif]].

## Precision demandee par owner : recopie quotidienne

Scan : collect.py (reutilisation GitHub, put, collect) et remote.py ; comparaison des deux derniers manifests, 12 septembre 11:05 UTC et 13 septembre 06:00 UTC. Analysis : pas de nouvelle copie des objets identiques ; GitHub reutilise les sources de revision inchangee (quatre sur ce passage), VPS relit/hash les fichiers mais ne transmet que les empreintes inconnues. Une revision GitHub modifiee provoque encore le telechargement de l'archive complete. Navigation et manifests sont regeneres. Validation : 7325 contenus communs, 18 empreintes ajoutees et sept retirees de l'inventaire, pas du stockage. Les 18 ne prouvent pas 18 nouvelles preuves editoriales. Correction proposee : rendre le bilan incremental explicite et traiter les lacunes utiles via le chemin prevu ; aucune modification runtime. La formulation precedente « copie les documents » etait trop imprecise pour decrire le cout quotidien. Verdict PARTIAL_COVERAGE.
