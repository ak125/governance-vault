---
id: ADR-128
title: "Départements autonomes et coordonnés : file de travail GitHub unique, remise de mandat par issue, bascule par étapes"
status: proposed
date: "2026-11-14"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-034"]
extends: []
related_adr: ["ADR-012", "ADR-020", "ADR-034", "ADR-102", "ADR-121", "ADR-123", "ADR-124"]
related_rules: ["AI1", "AI2", "AI5", "AI6", "AI9", "AI10", "AP-12", "G1", "G3", "G4"]
related_incidents: []
reviewed_by: ""
version: "0.1.0"
---

# ADR-128 : départements autonomes et coordonnés sur le contrat ADR-034

- **Statut** : Proposed (2026-11-14). Rédigé par un agent (Claude CLI) sur le mandat M de l'owner,
  décideur humain : Marwane. Aucune ratification sans instruction explicite de l'owner
  ([[rules-vault|G1]] ; [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]] D7). Tant que
  ce statut reste `proposed`, ce document est du contexte : il ne modifie ni le canon de `main` ni
  [[ADR-034-aicos-operating-contract|ADR-034]].
- **Amende (à la ratification)** [[ADR-034-aicos-operating-contract|ADR-034]] sur deux points : l'axe
  Exécution et la génération de MOC-Routines (D7). Le champ `amended_by` d'ADR-034 ne sera posé que
  par le commit de ratification.
- **N'active rien.** Aucun runner, workflow, label, secret ni variable n'est créé par cet ADR ou par
  sa PR. Chaque activation est une étape du plan D8, déclenchée par l'owner.

## Contexte

L'owner veut que les départements d'AutoMecanik avancent seuls et se coordonnent sans qu'il
recopie les mandats d'un chat vers une session. Aujourd'hui, l'état du travail est dispersé :

- les mandats sont rédigés dans le pilotage (Space ChatGPT, doc Départements) puis collés à la main
  dans une session Claude Code sur le DEV ;
- la mémoire de session, les handoffs (`.claude/handoffs/`) et le doc Départements servent de
  file de fait, sans source unique ;
- les 24 départements de `.spec/00-canon/ai-registry/agent-operating-map.yaml` ont tous
  `accountable_owner: null`.

[[ADR-034-aicos-operating-contract|ADR-034]] fixe déjà le cadre (3 axes Trigger / Exécution / Preuve,
un déclencheur par routine, six composants maison interdits, [[rules-ai-antipatterns#AP-12|AP-12]]).
[[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]] et
[[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]] ont ouvert un premier périmètre de
fusion automatique (documentation Markdown du monorepo, niveau A). Il manque la file, les rôles
actifs, les déclencheurs et la remise de mandat.

### Constats relevés le 2026-11-14 (lecture seule)

| Constat | Preuve | Portée |
|---|---|---|
| Aucun runner auto-hébergé ne tourne sur le DEV | pas d'unité systemd `actions.runner*`, pas de processus `Runner.Listener` (22:37:02Z) | l'axe Exécution d'ADR-034 n'est pas servi |
| L'API des runners est fermée au jeton agent | `gh api repos/ak125/nestjs-remix-monorepo/actions/runners` → HTTP 403 | l'enregistrement du runner n'est pas vérifiable par l'agent |
| 5 workflows du monorepo ciblent `[self-hosted, Linux, X64]` | `ci.yml`, `deploy-monitoring-scripts.yml`, `prod-smoke-tests.yml`, `release-prod.yml`, `visual-gate.yml` | ils attendent un runner absent |
| 254 exécutions en file (`queued`) | `gh run list --status queued` ; la file contient aussi des workflows `ubuntu-latest` (Dependabot Auto-merge, CodeQL) | cause non établie : l'absence de runner ne l'explique pas seule |
| Aucun label de département, de statut ou de niveau | `gh label list` du monorepo | la file D1 est à créer à l'étape 1 |
| 180 issues ouvertes ; 107 PR créées et 93 fusionnées depuis le 2026-11-01 | `gh issue list`, `gh pr list` | volume d'entrée de la file et des déclencheurs |
| Contexte mesuré d'une session racine | carte des départements (2026-11-09) : premier appel, médiane 71 020 jetons d'entrée, 90e centile 77 366 | base d'estimation du coût D3 ; coût monétaire non établi |

## Décision

### D1 — Une file de travail unique : les issues GitHub du monorepo

1. **Lieu.** La file est l'ensemble des issues de `ak125/nestjs-remix-monorepo`. Une issue = un
   mandat. Les PR (monorepo, vault, wiki) se rattachent à leur issue par `Refs #N` ou `Closes #N`
   dans leur corps ; une PR du vault cite l'issue par son URL complète.
2. **Labels** (à créer à l'étape 1, pas par cet ADR) :
   - département : `dept:NN-<slug>`, avec le slug de `agent-operating-map.yaml` (ex.
     `dept:07-seo`, `dept:21-runtime`) ; un seul label de département par issue ;
   - statut : un des cinq statuts de pilotage — `statut:implémenté`, `statut:intégré`,
     `statut:vérifié`, `statut:opérationnel`, `statut:bloqué` (directive owner du 2026-10-23). Une
     issue sans label de statut n'est pas commencée ;
   - niveau : `niveau:L0` à `niveau:L4` (échelle du skill `capability-acceptance`) ;
   - remise : `mandat-prêt` (D4). Le label existant `needs-human` reste celui de l'escalade.
3. **Ce que deviennent les documents Claude.** Le doc Départements, les handoffs
   `.claude/handoffs/`, `MEMORY.md` et la mémoire de session deviennent une **vue et une mémoire** :
   ils peuvent résumer ou citer la file, ils ne la remplacent pas. En cas d'écart, l'issue fait foi
   pour l'état d'un mandat ; le code et le runtime font foi pour l'état servi.
4. **Visibilité.** Le monorepo est public. Une issue ne contient ni secret, ni adresse IP, ni donnée
   personnelle, ni détail exploitable d'un incident de sécurité ouvert ; elle renvoie à
   l'emplacement privé sans en recopier le contenu.

### D2 — Rôles actifs, missions et KPI

Sont actifs : 02, 06, 07, 08, 10, 21, 22 (demande de l'owner) et 23 comme pilote (D6). Les 16
autres départements restent **dormants** : aucune routine, aucune session. Une issue labellisée
`dept:NN-…` pour un département dormant le réveille pour ce seul mandat, par la voie D4.

Le KPI vient de `kpi_primary` dans `agent-operating-map.yaml`. Le producteur est cherché dans
`backend/src/modules/admin/services/command-center-kpi.service.ts` : « présent » veut dire présent
dans le code (L1 au plus), la valeur servie n'est pas vérifiée.

| Rôle | Mission | Entrées | Sorties | KPI | Producteur |
|---|---|---|---|---|---|
| 02 Gouvernance | faire respecter les limites | mandat + règles du vault | autorisation ou refus motivé | `limits_respected` | **absent** |
| 06 Éditorial | contenu réutilisable et validé | WIKI validée + brief | contenu proposé (PR) | `reusable_validated_content` | **absent** |
| 07 SEO | servir des pages utiles | contenu + catalogue | page, événement ATC | `pages_generating_atc` | présent (L1) |
| 08 Vidéo | relier média et demande | brief approuvé | média + attribution | `demands_from_video` | **absent** |
| 10 Catalogue | la bonne pièce pour le bon véhicule | véhicule + pièce + vérité fournisseur | compatibilité, dispo affichée | `compat_and_displayed_availability` | **absent** |
| 21 Runtime | un service fiable | code/config + télémétrie | service, preuve de santé | `runtime_health` | **absent** (le digest `morning-health-digest.yml` produit une preuve, pas ce KPI) |
| 22 Data | des mesures fiables | événements + paiements | verdict `tracking-integrity-verdict.v1` | `metric_reliability` | présent (L1) |
| 23 IA & agents (pilote) | des capacités utiles, pas de complexité | la file D1 | arbitrages proposés, doublons, blocages | `useful_capabilities_not_complexity` | **absent** |

**Conséquence d'[[rules-ai-cos|AI1]].** Seuls 07 et 22 ont un producteur. Pour les six autres rôles,
la routine *agent* du rôle ne s'active pas tant que son producteur n'existe pas : c'est un critère
de sortie de l'étape qui l'active (D8). Les routines déterministes déjà en service (02 : lint hebdo
du vault ; 21 : digest du matin) restent ce qu'elles sont et ne deviennent pas des agents.

### D3 — Déclencheurs, cadence, coût et charge

Une routine = un déclencheur, déclaré dans le bloc `routine:` de son workflow (ADR-034). Aucune
routine n'est créée par cet ADR.

| Routine (proposée) | Rôle | Déclencheur unique (natif) | Runner | Cadence attendue |
|---|---|---|---|---|
| `pilote-file` | 23 | `schedule` cron `0 6-19 * * *` (horaire, journée Europe/Paris) | `ubuntu-latest` | 14 exécutions/jour |
| `mandat-remise` | tous | `issues: labeled` (`mandat-prêt`, D4) | DEV auto-hébergé | bornée par les approbations de l'owner |
| `seo-sur-fusion` | 07 | `pull_request: closed` (fusionnée) + filtre `paths:` SEO | `ubuntu-latest` | ≤ 6,6/jour (93 fusions en 14 jours, avant filtre) |
| `editorial-sur-wiki` | 06 | `repository_dispatch` émis par le dépôt wiki à la fusion d'une page validée | `ubuntu-latest` | bornée par les validations WIKI |
| `video-sur-brief` | 08 | `issues: labeled` (`brief-approuvé` sur `dept:08-media`) | `ubuntu-latest` | bornée par les briefs approuvés |
| `vault-weekly-lint` (existante) | 02 | `schedule` `0 2 * * 1` (ADR-020) | `ubuntu-latest` | hebdomadaire |
| `morning-health-digest` (existante) | 21 | `schedule` `0 5 * * 1-5` | `ubuntu-latest` | quotidienne, jours ouvrés |
| `data-verdict` | 22 | `schedule` quotidien | DEV auto-hébergé (lecture base) | quotidienne |
| `catalogue-audit` | 10 | `schedule` hebdomadaire | DEV auto-hébergé (lecture base) | hebdomadaire |

**Coût.** Une routine fait d'abord un contrôle déterministe (`gh`, script) et n'ouvre une session
Claude que s'il y a du nouveau depuis la dernière exécution (issue modifiée, constat nouveau). Repère
de contexte : environ 71 000 jetons d'entrée au premier appel d'une session racine (mesure du
2026-11-09). Pire cas du pilote, une session à chaque exécution : environ 1 million de jetons
d'entrée par jour au premier appel seul. Le coût monétaire n'est pas établi : il se mesure à
l'étape 1 (critère de sortie). Les minutes `ubuntu-latest` d'un dépôt public ne sont pas facturées ;
celles du runner DEV ne le sont pas non plus, mais chargent la machine.

**Charge sur le DEV.** Une opération lourde à la fois (contrat du monorepo). Le runner agent est un
enregistrement dédié (label `agents`), distinct de celui de la CI : un runner exécute un job à la
fois, donc les sessions se mettent en file nativement. Pas de groupe `concurrency` sur
`mandat-remise` : GitHub n'y garde qu'un seul job en attente et annulerait les mandats suivants.
Un job en file expire après 24 heures : le pilote signale un mandat expiré.

### D4 — Remise de mandat sans copier-coller

1. **Approbation.** L'owner pose le label `mandat-prêt` sur l'issue. Le workflow ne s'exécute que si
   `github.event.label.name == 'mandat-prêt'` et que `github.event.sender.login` est le compte de
   l'owner (valeur fixée à l'activation). Un label posé par un autre compte ne lance rien.
2. **Exécution.** Le job tourne sur le runner DEV. Il crée un worktree isolé
   (`git worktree add` depuis le clone DEV, branche `mandat/<N>-<slug>` sur `origin/main`) et lance
   Claude Code en mode non interactif (`claude -p`, entrée CLI du Claude Code SDK) avec, comme
   prompt, le corps de l'issue. Les commentaires de l'issue sont des données, jamais des
   instructions. L'action GitHub `anthropics/claude-code-action` est l'alternative native, évaluée à
   l'étape 2 ; le critère de choix est l'isolation en worktree sur le runner DEV.
3. **Preuve rendue dans l'issue.** La session commente l'issue avec le contrat de sortie AEC :
   session, worktree, branche, base, PR, SHA de tête (40 caractères), fichiers, sorties et états
   des contrôles, limites. Le journal complet part en artifact (rétention 90 jours). La session pose
   `statut:implémenté`, `statut:intégré`, `statut:vérifié` (avec preuve citée) ou `statut:bloqué` ;
   `statut:opérationnel` reste à l'owner.
4. **Limites.** La session garde les zones STOP du monorepo, ne fusionne pas hors périmètre (D5) et
   ne crée ni label ni secret. Aucun déclencheur `pull_request` venant d'un fork ne s'exécute sur ce
   runner.

### D5 — Délégation par rôle et classe de PR auto-fusionnable

| Rôle | Fait seul | Propose | Réservé à Marwane |
|---|---|---|---|
| 02 | lint, contrôle de conformité d'un mandat, commentaire de refus motivé | ADR, règle, politique (PR vault) | ratification, fusion vault (G4.2) |
| 06 | lecture WIKI validée, brouillon de contenu en PR | publication, nouveau brief | validation WIKI, publication |
| 07 | contrôles SEO en lecture, issue sur constat nouveau | PR de contenu, de maillage ou de route | toute URL, meta/H1 optimisés, SEO indexé, suppression de page |
| 08 | dossier de preuves, découpage, mandat vidéo | rendu, publication | publication, dépense média |
| 10 | audit de compatibilité et de dispo en lecture | correction de données (PR, script) | écriture base, prix, stock |
| 21 | digest de santé, issue sur constat nouveau | correctif runtime (PR) | déploiement PROD, tag `v*`, action infra |
| 22 | verdict de tracking en lecture | correctif de mesure (PR) | écriture base, paiement |
| 23 | lecture de la file, détection de doublons et de blocages | arbitrage, fusion d'issues, relance | arrêt d'urgence, décision d'arbitrage |

Tous les rôles peuvent, dans leur mandat : créer une branche, committer, pousser et ouvrir une PR.
Aucun ne fusionne hors du périmètre ci-dessous.

**Classe candidate « faible risque » (non activée).** Extension proposée du périmètre
d'[[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]], même porte
(`scripts/ci/merge-perimeter-gate.mjs`), même politique (`ledger/policies/merge-perimeter.v1.json`),
même compte exécutant, même fichier de pause. Ce n'est pas un nouveau mécanisme.

- **Condition** : CI requise verte sur la tête **et** revue de niveau B, c'est-à-dire une approbation
  sur ce SHA par une identité distincte de l'auteur, vérifiable par la porte.
- **Liste fermée de chemins** :
  1. Markdown hors chemins refusés de la politique (déjà couvert au niveau A par ADR-124) ;
  2. `audit/**/*.md` (rapports d'audit) ;
  3. `backend/tests/unit/**` et `frontend/tests/unit/**`, en ajout ou modification de tests
     seulement (aucun fichier source, aucune suppression de test ; motifs refusés `\.skip\(` et
     `\.only\(`).
- **Exclus dans tous les cas** : les `deny_paths` de la politique, `.github/**`,
  `.spec/00-canon/**`, les projections générées, `packages/seo-role-contracts/**`, toutes les zones
  STOP, et tout le dépôt du vault.
- **Prérequis bloquant** : l'identité de revue distincte n'existe pas. Le compte
  `automecanik-agents[bot]` ne peut pas approuver ses propres PR. Tant qu'elle n'existe pas, le
  niveau B reste fermé et tout le reste demeure sous [[rules-vault|G4]]. L'ouverture du niveau B se
  fait par une PR vault sur la politique, fusionnée par l'owner.

### D6 — Un pilote unique : le rôle 23

Le rôle 23 (IA, agents et automatisation) pilote la file ; le rôle 01 Direction reste humain.

- Le pilote lit la file (`gh issue list`, `gh pr list`), repère les doublons, les mandats sans
  département, les blocages (issue `statut:bloqué` ou sans mouvement), les mandats expirés (D3) et
  les PR sans issue.
- Il **propose** : un commentaire sur l'issue concernée et un récapitulatif dans une issue de pilotage
  unique, mise à jour à chaque exécution. Il ne ferme, ne fusionne, ne relabellise et ne décide rien
  ([[rules-ai-cos|AI2]]). L'arbitrage est l'acte de l'owner, posé par label ou commentaire.
- Il n'ajoute pas d'agent : il active une mission déjà déclarée du rôle 23
  ([[rules-ai-cos|AI6]]).

**Arrêt d'urgence ([[rules-ai-cos|AI9]]), réservé à l'owner** :

| Niveau | Geste natif | Effet |
|---|---|---|
| N1 | arrêter le service du runner DEV | plus aucune exécution sur le DEV |
| N2 | `gh workflow disable <routine>` | une routine coupée |
| N3 | retirer `mandat-prêt`, poser `statut:bloqué` | un mandat gelé |

Le pilote peut demander un arrêt (label `needs-human`), jamais l'exécuter.

### D7 — Amendement d'ADR-034 (pris à la ratification)

1. **Axe Exécution.** Le texte devient : « Runner auto-hébergé DEV → Claude Code SDK (dont les
   sessions lancées depuis une issue `mandat-prêt` dans un worktree isolé, ADR-128 D4) / scripts /
   MCP / `gh api` ». « AI-COS » désigne le contrat d'exploitation, pas une machine : aucune routine ni
   session ne s'exécute sur la machine AI-COS. Le retrait de cette machine et la zone `aicos_vps`
   d'[[ADR-012-aicos-vps-architecture|ADR-012]] relèvent de l'ADR du mandat K, que cet ADR ne
   duplique pas.
2. **MOC-Routines.** Le texte « régénérée automatiquement à chaque merge » est remplacé : la page
   `ops/moc/MOC-Routines.md` est **générée** par un script du vault à partir des blocs `routine:` des
   workflows (vault et monorepo, lus par `gh api`), lancé en local, et committée par PR signée. La CI
   n'exécute que le mode `--check` (G4.3), sur le modèle de `_scripts/sync_moc_decisions.py`. Le
   script fait l'objet d'une PR séparée.
3. **Bloc `routine:`.** Aux champs existants (`id`, `owner`, `trigger`, `evidence`, `escalation`,
   `secret`) s'ajoutent `departement` (`NN-<slug>`) et `kpi` (identifiant ou `absent`).

### D8 — Plan de bascule

Chaque étape s'active par un acte de l'owner et se défait par le geste N1 ou N2 de D6.

| Étape | Contenu | Critère de sortie |
|---|---|---|
| 0 | ratification de cet ADR | commit de ratification fusionné par l'owner |
| 1 (mandat N) | runner DEV agent enregistré ; labels D1 créés ; routine `pilote-file` | runner `online` vu par l'API avec un jeton de l'owner ; 10 exécutions de journée consécutives vertes ; issue de pilotage à jour ; coût réel d'une journée mesuré ; cause des exécutions en file établie ou traitée à part |
| 2 | remise de mandat par issue (`mandat-remise`) | 3 mandats menés du label `mandat-prêt` à la PR avec preuve AEC dans l'issue, sans copier-coller ; refus prouvé d'un label posé par un autre compte ; geste N2 testé |
| 3 | routines SEO (07), éditorial (06), vidéo (08) | chaque routine a tourné sur un événement réel avec preuve ; valeur servie de `pages_generating_atc` vérifiée ; producteurs de `reusable_validated_content` et `demands_from_video` présents avant toute routine agent de 06 et 08 |

Les routines 10 et 22 et le rattachement des routines existantes 02 et 21 à leur label suivent
l'étape 3, chacune avec son producteur de KPI comme condition.

## Briques, outil natif et owner

L'owner humain de chaque brique est Marwane : `accountable_owner` est vide pour les 24 départements.

| Brique | Outil natif ([[rules-ai-antipatterns#AP-12|AP-12]]) | Département porteur |
|---|---|---|
| File de travail | GitHub Issues + labels | 23 |
| Lien mandat ↔ PR | `Refs #N` / `Closes #N` | rôle du mandat |
| Déclencheurs | GitHub Actions (`schedule`, `issues`, `pull_request`, `repository_dispatch`) | rôle de la routine |
| Exécution | runner auto-hébergé GitHub Actions sur le DEV | 21 |
| Session agent | Claude Code SDK (`claude -p`) | 23 |
| Preuve | commentaire d'issue + artifact GitHub (90 jours) | rôle du mandat |
| Fusion auto (candidate) | porte ADR-124 + `gh pr merge --match-head-commit` | 02 |
| Cockpit | Paperclip + interface GitHub Actions | 23 |
| Arrêt d'urgence | service du runner, `gh workflow disable`, labels | owner seul |
| Matrice des routines | MOC-Routines générée (D7) | 02 |

## Options considérées

### Option A : statu quo (mandats collés à la main)

Pas de nouvelle brique. L'owner reste le transporteur de chaque mandat ; l'état reste dispersé entre
chat, mémoires et handoffs. Rejetée : c'est le problème posé.

### Option B : orchestrateur ou file maison (machine AI-COS, base, bus)

Rejetée : six composants interdits par AP-12 et ADR-034 ; la vision d'[[ADR-006-ai-orchestrator-architecture|ADR-006]]
est remplacée.

### Option C : issues GitHub + Actions + runner DEV + Claude Code SDK (retenue)

Tout est natif, déjà payé et déjà audité par GitHub ; chaque brique se coupe par un geste natif.

## Justification

L'option C reprend le contrat d'ADR-034 sans rien y ajouter de maison. La file est là où vivent déjà
les PR. La remise de mandat garde l'approbation humaine en un seul geste (un label). La fusion
automatique reste dans le mécanisme d'ADR-123/124, avec son prérequis de revue distincte.

## Conséquences

### Positives

- Un seul endroit pour l'état d'un mandat ; plus de copier-coller entre chat et session.
- Chaque routine a un déclencheur, un owner, une preuve et un geste d'arrêt.
- Les rôles sans KPI produit sont visibles comme tels (AI1) au lieu d'être tenus pour actifs.

### Négatives

- Les issues sont publiques : le contexte sensible reste ailleurs (D1.4).
- Un runner auto-hébergé sur un dépôt public exige de n'y exécuter aucun code de fork (D4.4).
- Six producteurs de KPI manquent ; sans eux, la moitié des rôles actifs restent sans routine agent.

### Neutres

- Les documents Claude existants restent, comme vue.
- Le numéro ADR-128 est pris à la date de rédaction ; si l'ADR du mandat K s'ouvre avant avec ce
  numéro, l'un des deux est renuméroté avant fusion.

## Ce que cet ADR ne fait pas

- Il n'active ni runner, ni workflow, ni label, ni secret, ni variable.
- Il ne touche ni la PROD, ni la base, ni le code applicatif, ni les PR ouvertes du vault.
- Il ne décide pas du retrait de la machine AI-COS (mandat K).
- Il n'ouvre pas le niveau B de fusion automatique.

## Critères de succès

- [ ] C1 — Étape 1 sortie selon D8.
- [ ] C2 — Étape 2 sortie : aucun mandat collé à la main pendant 2 semaines.
- [ ] C3 — Étape 3 sortie.
- [ ] C4 — Chaque rôle actif a un producteur de KPI présent, ou son absence reste inscrite ici.

## Inconnues

- Les valeurs exactes des cinq statuts vivent dans le Space de pilotage : à confirmer par l'owner à
  l'étape 1.
- Cause des 254 exécutions en file : non établie.
- Enregistrement réel du runner : non vérifiable par le jeton agent (403).
- Coût monétaire d'une session : non établi.
- Disponibilité d'une identité de revue distincte (niveau B) : à décider par l'owner.

## Retour arrière

Avant ratification : fermer la PR. Après : un ADR qui remplace celui-ci ; chaque étape activée se
défait par N1 ou N2 (D6).

## Revue planifiée

À la sortie de l'étape 2, et au plus tard le 2027-02-14.

## Références

- [[ADR-034-aicos-operating-contract|ADR-034]], [[ADR-012-aicos-vps-architecture|ADR-012]],
  [[ADR-020-weekly-vault-lint|ADR-020]]
- [[ADR-121-mandat-revue-decision-fusion-actes-distincts|ADR-121]],
  [[ADR-123-fusion-automatique-conditionnelle-perimetre-adopte|ADR-123]],
  [[ADR-124-premier-perimetre-fusion-automatique-monorepo|ADR-124]]
- [[rules-ai-cos]], [[rules-ai-antipatterns]], [[rules-vault]]
- [[MOC-Decisions]], [[MOC-Agents]]

---

*Proposé le : 2026-11-14*
*Accepté le : —*
*Dernière revue : 2026-11-14*
