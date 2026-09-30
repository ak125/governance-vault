# R3 — validation du HTML compose, 13 septembre 2026

## Scan

Poursuite autorisee du controle des roles et structures, sans publication. Lectures ciblees du validateur et de l'interceptor Nest, du rendu GuideCard/MiniDiagnosticTable/HtmlContent, des tests et du collecteur synthetic existant. Ce dernier collecte quelques signaux via regex et ne fournit pas une extraction DOM par section ; il n'a pas ete modifie. Manifeste r3-html-coverage.json : 16 fichiers retenus dans le perimetre de lecture ciblee, dont sept modifies. ADR-027 accepted relue, y compris correction du 7 juillet : R3/S2_DIAG reste canonique, RAG n'est pas une autorite de contenu.

## Analysis

validatePageWithHtml deleguait au texte fourni separement et ne regardait le HTML que pour canonical. Le diagnostic integre n'avait pas de borne semantique de section dans le rendu ; l'ancre seule pouvait etre absente ou ambigue. Dix-neuf tests controles reproduisent quinze echecs avant correction. Le monitor Nest n'est pas un crawl exhaustif des SSR : sa presence ne prouve pas que toutes les pages servies lui sont soumises.

## Correction (proposee et preparee dans le candidat autorise)

GuideCard accepte le type de section ; MiniDiagnosticTable emet data-r3-section=S2_DIAG sur le conteneur portant l'ancre, en conservant l'ancien fragment. Le validateur HTML R3/conseils lit desormais le DOM de l'article : un seul article requis, scripts/styles/templates ignores, autres surfaces hors article exclues du contenu editorial. Il refuse l'ambiguite plutot que de choisir un article ou un diagnostic arbitraire.

Pour accorder le traitement diagnostic, un seul marqueur S2_DIAG doit porter l'unique ID diagnostic-rapide a l'interieur de l'article. Le controle verifie un H2 non vide, un tableau et au moins une ligne de donnees avec trois cellules non vides. Une cellule de footer colspan=3 est toleree sans compter comme ligne de donnees. La signification des entetes, le footer DTC et la verite des cellules ne sont pas certifies. Le sous-arbre diagnostic reutilise validateR3Sections ; le reste de l'article conserve ses controles. Une declaration R5 sur une route R3/conseils est refusee. Le controle canonical existant reste applique.

htmlparser2 10.1.0, deja resolu dans le lockfile et utilise dans l'ecosysteme du rendu HTML, est declare directement dans backend/package.json. npm --package-lock-only a ajoute cette seule dependance ; aucune version resolue n'a change, aucun node_modules partage n'a ete installe. Reference API : [documentation officielle htmlparser2](https://github.com/fb55/htmlparser2#usage). Le parseur est tolerant ; cette analyse ne revendique ni conformite a toutes les reparations HTML d'un navigateur ni visibilite CSS.

## Validation

154 tests backend PASS dans huit suites : HTML (19 cas), sections stockees, validateur historique, audit HTTP, doublons, sources, scorer et backfill. Quatre tests frontend PASS, dont un test qui compose le vrai MiniDiagnosticTable avec HtmlContent et sa sanitisation via renderToStaticMarkup, puis transmet ce HTML au vrai validateur backend. Le meme test casse l'ancre et obtient un rejet. Autres cas : contenu commercial encode en entites, procedure dans le diagnostic, pollution ailleurs, mauvais type, double ancre, mauvais emplacement, tableau incomplet, titre manquant, canonical absent et role incoherent. Les fixtures ne modifient aucun contenu partage.

ESLint cible : zero erreur/warning apres rangement d'un import. Diff checks avant/apres staging PASS. La verification JSON du lock confirme que seule la dependance directe change. L'essai npm offline a echoue faute de cache metadata, puis npm package-lock-only normal a reussi. npm ls observe les liens du node_modules partage et affiche extraneous ; cela ne constitue pas une preuve d'installation propre du candidat. HEAD 0c31807c8453c251d70c7575eafcc973f04eed14 ; origin/main 466cc15ce9b385a61503cc0224f40bec700ec41a, 13 commits en avance sur la base. Aucun changement upstream des fichiers de code du lot ; differences Turbo hors lot dans package-lock, preservees pour une integration future.

Sonde distincte a 15:44:41 UTC le 13 septembre : PUBLIC /diagnostic-auto/voyant-disque-de-frein renvoie 301 vers /blog-pieces-auto/conseils/disque-de-frein#diagnostic-rapide ; la destination renvoie 200 avec un article mais zero ID diagnostic-rapide et zero marqueur S2_DIAG. DEV localhost:3000 refuse la connexion (ECONNREFUSED). Ni preuve d'activation du candidat, ni incident d'infrastructure corrige dans ce lot. Details dans r3-html-live.json.

Preuves r3-html-* : patches incremental/candidat, journaux avant/apres, rendu, lint, dependance, sonde et manifeste. Le patch incremental repose sur les snapshots du candidat avant ce lot ; le patch candidat inclut les changements anterieurs des memes fichiers.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour la validation HTML et son contrat avec le rendu testes ; PARTIAL_COVERAGE global. Aucun commit, push, merge, deploiement, modification de base, cron ou contenu partage. Les 154+4 tests ne remplacent pas une installation propre, un typecheck global, la CI, un navigateur sur la page complete ou une preuve de branchement du monitor sur le flux SSR actif. Priorite suivante : etablir ce branchement et le transport de ses constats vers la boucle existante, puis controler les destinations apres livraison autorisee. La collecte de sources utiles et la qualite factuelle du corpus restent ouvertes.
