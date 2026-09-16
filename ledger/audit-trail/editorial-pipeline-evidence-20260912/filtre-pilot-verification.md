# Pilote filtre a huile : du manque a la preuve

## Scan

Page visee : guide achat existant R6 `blog-pieces-auto/guide-achat/filtre-a-huile`, gamme `pg_id=7`. DEV HTTP200; HTML conserve dans `filtre-pilot-guide-dev.html`, empreinte `fb2d6b2aefec9ee242a42546b99cea89b86bd57baf0dc80238dda62a2297fea8`, ecrit le 2026-09-13T21:38:18.282705+00:00. Les deux lectures publiques guide/conseils ont retourne 403. Ce constat DEV n'est pas une preuve de l'etat public actuel.

## Analysis

Le guide DEV exige « Presence clapet anti-retour (obligatoire moteurs modernes) ». La [page technique FILTRON](https://filtron.eu/en/insights/filter-guide/spin-on-oil-filter-valves.html) indique que l'utilisation des clapets depend de la conception du filtre determinee par le constructeur. Une exigence universelle ne decoule donc pas de ce passage. Le texte cite est maintenant capture par le runner RAW existant.

Le controle des criteres a egalement retrouve [une documentation MANN+HUMMEL pour transmissions](https://oem.mann-hummel.com/en/oem-products/oil-filters/transmission-oil-filters.html) utilisee dans la proposition pour parler du media de filtre moteur. Ses caracteristiques ne prouvent pas, a elles seules, une recommandation moteur ni une hierarchie universelle des medias. Cette seconde affirmation reste a re-sourcer.

Autres constats DEV a traiter separement : criteres marque/modele/motorisation repetes avec variantes d'accents, champs de carte grise a verifier, encart technique portant des chiffres non rattaches a une application precise dans le texte observe. Ce lot ne corrige ni ne valide ces autres passages.

## Correction proposee et preparee

Sous l'autorisation owner de corriger/ameliorer/continuer, un candidat RAW part de l'amont actuel `7565934186fced370f78ea64d7616b912a0c9a6c`. L'ancien candidat et ses changements sont conserves. Une entree native vise WIKI, `pg_id=7`, avec la question precise; domaine FILTRON declare niveau2/licence inconnue. Le controle de secrets initialement absent a bloque avant ecriture. La version 8.18.4 deja fixee par le depot a ete rendue disponible dans un cache propre au pilote apres verification du checksum officiel, sans changement de version du projet.

Une capture immuable est disponible, sans copie quotidienne supplementaire : la repetition renvoie `duplicate_content_hash`. L'extraction contient le passage utile et aussi des recommandations annexes; seule l'introduction sur les clapets est utilisee pour la nouvelle affirmation.

Dans le WIKI candidat, trois fichiers sont modifies : `proposals/filtre-a-huile.md`, sa coverage map et l'entree FILTRON du source-catalog. Le catalogue natif pointe maintenant vers le `manifest_id` reel et le hash du fichier RAW complet. `active` signifie archive disponible, pas faits approuves. La nouvelle affirmation porte `captured`, jamais `verified`.

Texte prepare pour la question visee : **La presence des clapets depend de la conception du filtre et du moteur. Leur presence seule ne prouve pas la compatibilite ; celle-ci reste a verifier dans le catalogue.** La premiere proposition est etayee par l'introduction FILTRON; le renvoi au catalogue applique la separation editoriale/compatibilite du projet.

L'ouverture « 90 a 100 % du debit » et « deux clapets le rendent sur », ainsi que l'association silicone/intervalles longs versus nitrile/intervalles standards, ont ete retirees des deux passages corriges : la source citee n'en fournit pas la justification. Les autres sections ne sont pas validees par cette correction.

## Validation

- Schemas worklist/allowlist : PASS.
- Captures RAW : Gate I et Gate J PASS separement; controle de secrets execute; repetition sans nouveau fichier.
- WIKI : frontmatter PASS; coverage-map strict PASS (14 entrees); lien RAW natif de FILTRON PASS. Fichier et corps ont deux hashes distincts controles, sans les confondre.
- Formule du score : 0.46, controle PASS, valeur inchangee. Ce n'est pas une mesure du gain d'information apporte par cette capture.
- Promotion dry-run : **BLOCKED avant et apres**, motif SUBSTANCE_SCORE 0.46 < 0.85. Le refus intervient avant une validation exhaustive, donc les autres gates ne sont pas declares verts.
- Proposition `proposed`, exports RAG/SEO/support tous `false`; licence de capture `unknown`, statut `CAPTURED_NEEDS_REVIEW`.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour capture/provenance/structure; PARTIAL_COVERAGE global. Le manque est documente et la correction preparee; il n'est pas ferme dans la page servie. Aucun commit Git, push, promotion, export, DB ou deploiement. `--commit` du runner signifie ecriture RAW locale au candidat, pas commit Git.

Suite : re-sourcer les autres affirmations utiles du pilote (en premier le media moteur, puis les criteres de choix), puis reevaluer avec le decideur natif. Corriger les doublons de composition dans leur producteur identifie et verifier les champs de carte grise sur une source officielle. Aucun score gonfle ni promotion forcee.

Retour : [[ledger/audit-trail/2026-09-12-editorial-pipeline-codex|Rapport principal]].
