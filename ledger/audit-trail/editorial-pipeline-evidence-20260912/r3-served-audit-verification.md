# Audit R3 du HTML servi — 13 septembre 2026

## Scan

Perimetre : audit interne R3, scorer de conseils, validateur de roles, chemin SSR et consigne du planificateur R3. Six fichiers prepares dans le candidat application. Inventaire des 14 fichiers lus, revisions et exclusions : `r3-served-audit-coverage.json`. Reprise de CLAUDE, cartographie ciblee du registre, REPO_MAP et log recent ; regles de domaine et contrat de sortie deja lus, inchanges.

Candidat : `/opt/automecanik/app/.claude/worktrees/editorial-pipeline-20260912`, branche `codex/editorial-pipeline-provenance-20260912`, HEAD `0c31807c8453c251d70c7575eafcc973f04eed14`. Origin/main actualise : `466cc15ce9b385a61503cc0224f40bec700ec41a` ; 13 commits depuis la base, sans difference amont sur les six fichiers de ce lot. Aucun merge/rebase.

## Analysis

Le controleur Remix delegue directement la reponse Express a createRequestHandler. Son retour ne contient pas une chaine HTML : l'intercepteur Nest qui inspecte uniquement les chaines retournees ne couvre donc pas ce flux SSR. La presence du validateur ne prouvait pas son execution sur les pages servies.

L'audit existant pouvait demander de passer une gamme sur la base de ses sections stockees sans verifier le document livre au visiteur. Une section S2_DIAG entierement omise pouvait aussi echapper aux controles HTML qui se declenchaient sur sa presence.

## Correction proposee et preparee avec autorisation utilisateur

L'audit R3 existant lit desormais la route conseils construite depuis l'alias de gamme, sur le BASE_URL explicitement configure. Le score stocke reste distinct du resultat HTML. `storedCanSkip` conserve le resultat stocke ; `canSkip` exige aussi un HTML evalue et valide. `renderedPage` expose URL, date, statut, action, empreinte SHA256 et controles du document. Le statut `evaluated` signifie analyse executee, pas validation reussie. `pageReviewRequired` conserve le travail de rendu a traiter, sans attribuer automatiquement un defaut HTML aux sections a reecrire.

Une section S2_DIAG attendue depuis les sections stockees mais absente du rendu produit R3_DIAGNOSTIC_MISSING. Les autres controles HTML du lot precedent sont reutilises. Les redirections restent visibles avec leur destination et une action de revue ; elles ne sont pas suivies automatiquement.

Lecture GET bornee a 15 secondes et 2 Mio, sans transmission du secret interne ni de cookies ; alias et origine configures verifies. Absence de configuration, erreur HTTP, timeout, corps interrompu, type non HTML ou corps trop grand laissent l'audit indisponible et interdisent canSkip. Aucun fallback implicite sur la production. Aucun nouveau crawler, ordonnanceur ou buffer du flux SSR.

Le commentaire de l'intercepteur est rectifie. La consigne du planificateur documente ces resultats et conserve le diagnostic integre a R3 selon ADR-027, sans recreer les details R5 retires.

## Validation

Avant raccordement : 17 echecs et 17 succes dans la contre-preuve HTTP. Avant controle d'omission complete de S2_DIAG : un echec cible et 38 cas ignores. Apres toutes corrections : 113 tests backend PASS dans six suites, dont 39 tests du parcours HTTP R3. Le serveur HTTP ephemere reel prouve le GET de la route configuree, l'absence du secret et le non-suivi du 301. Les autres cas reseau sont controles par transport de test. Supabase utilise un transport en memoire, sans base partagee.

Quatre tests frontend PASS, dont rendu React SSR vers le vrai validateur et contre-exemple de structure. Ce resultat est reutilise apres modifications du scorer qui n'affectent pas ce perimetre. ESLint : zero erreur, un avertissement any preexistant dans l'intercepteur dont seuls les commentaires changent. Diff checks cibles PASS. Journaux et patches `r3-served-audit-*` dans ce dossier. Les suites plus larges des lots precedents ne sont pas revendiquees comme reexecutees.

## Verdict

VALIDATED_FOR_SCOPE_ONLY pour ce raccordement dans le candidat ; PARTIAL_COVERAGE pour l'objectif global. Aucun commit, push, merge, PR, deploiement, ecriture DB/corpus partage, activation de cron ni notification.

`sourceVersionMatch=not_evaluated` : l'empreinte HTML n'etablit pas que le document correspond a la revision des sections stockees. Ce lot compare la presence de S2_DIAG, pas l'integralite de toutes les sections. Le parseur ne prouve ni visibilite CSS ni exactitude factuelle ni potentiel de classement. Il reste a identifier/verifier l'executant qui appelle cet audit et son environnement avant toute activation autorisee, puis a mesurer la collecte utile et les autres roles.

Aucune nouvelle sonde publique ou DEV dans ce lot. L'observation publique 301/200 avec ancre absente et DEV3000 ECONNREFUSED du lot precedent date du 13 septembre a 15:44 UTC ; elle est historique. Aucune CI, verification TypeScript globale ou installation propre realisee ici.

Lien de contexte : [[ledger/audit-trail/2026-09-12-editorial-pipeline-codex|rapport cumulatif]].
