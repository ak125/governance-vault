---
id: ADR-102
title: "Airlock réduit au RPC gate, canal de bundles retiré, G4 réécrite (écriture par PR, CI en lecture seule) — amende ADR-002, 007 à 013"
status: accepted
date: "2026-10-01"
decision_date: "2026-10-01"
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
amends: ["ADR-002", "ADR-007", "ADR-008", "ADR-009", "ADR-010", "ADR-011", "ADR-012", "ADR-013"]
extends: []
related_adr: ["ADR-003", "ADR-015", "ADR-053", "ADR-060", "ADR-061", "ADR-101"]
related_rules: ["G3", "G4"]
related_incidents: []
version: "1.0.0"
---

# ADR-102 : Airlock réduit au RPC gate, canal de bundles retiré, G4 réécrite

- **Statut** : Accepted (2026-10-01). La fusion par l'owner vaut ratification.
- **Amende** [[ADR-002-airlock-zero-trust|ADR-002]], [[ADR-007-location-independence|ADR-007]],
  [[ADR-008-agent-placement-rules|ADR-008]], [[ADR-009-agents-phase1-activation|ADR-009]],
  [[ADR-010-airlock-enforce-activation|ADR-010]], [[ADR-011-openclaw-claude-api-replacement|ADR-011]],
  [[ADR-012-aicos-vps-architecture|ADR-012]] et [[ADR-013-agent-lifecycle-governance|ADR-013]],
  sur les seuls passages listés en D2. Le reste de ces ADR reste en vigueur.
- **Réécrit** la règle G4 de [[rules-vault]] (v3.1.0).
- **Méthode** : chaque constat ci-dessous a été vérifié le 2026-10-01 sur `main` du vault, sur `main`
  du monorepo et sur la machine DEV.

## Contexte

Le mot « Airlock » désigne dans les ADR deux mécanismes distincts :

| Mécanisme | Où il vit | État au 2026-10-01 |
|---|---|---|
| **RPC gate** : `RpcGateService` filtre les appels RPC Supabase par niveau de risque (P0 à P2), modes `observe` / `enforce` ([[ADR-003-rpc-governance|ADR-003]], ADR-010 §1 à §3) | `backend/src/security/rpc-gate/` du monorepo | Présent. `RPC_GATE_MODE=enforce` est déclaré dans `docker-compose.preprod.yml` (niveau P1) et `docker-compose.prod.yml` (niveau P2). Le mode réellement servi en PROD n'a pas été vérifié au runtime pour cet ADR. |
| **Canal de bundles** : un agent produit un bundle signé HMAC-SHA256, le soumet au dépôt `agent-submissions`, l'Airlock le valide puis ouvre une PR (ADR-002 §2.1, ADR-011) | Dépôt `agent-submissions`, dossier `/opt/automecanik/airlock` de la machine DEV, scripts du monorepo et du vault | Inactif depuis février 2026 (constats 1 à 8). |

Constats :

1. `/opt/automecanik/airlock/audit.log` compte 31 lignes, la dernière datée du 2026-02-06. Les dossiers
   `inbox/`, `processed/` et `rejected/` sont vides.
2. Le dépôt `agent-submissions` n'a reçu aucun push depuis le 2026-03-07.
3. Les scripts du canal côté monorepo (`scripts/airlock.sh`, `scripts/tail-bundle.sh`,
   `scripts/pull-openclaw-bundles.sh`) n'ont pas changé depuis le 2026-02-08.
4. [[ADR-013-agent-lifecycle-governance|ADR-013]] constatait déjà la pause (« Le pipeline
   agent-submissions est pausé depuis le 2026-02-06 ») et prévoyait, en Étape 3.1, de « relancer
   pipeline agent-submissions (ou post-mortem si abandon) ». Ni la relance ni le post-mortem n'ont eu lieu.
5. Les tables annoncées par [[ADR-012-aicos-vps-architecture|ADR-012]] n'existent pas toutes :
   `__airlock_bundles` et `__agent_metrics` sont absentes de la base, seule `__agent_runs` existe.
6. Depuis mars 2026, les agents qui modifient un dépôt le font par branche et PR sur ce dépôt,
   soumises à ses checks requis et fusionnées par un humain. Aucun bundle n'a transité par l'Airlock.
7. `_scripts/gov` ne fonctionne plus : il appelle `./scripts/sync-canon.sh` et
   `./scripts/check-orphans.sh`, chemins inexistants (les scripts du vault sont sous `_scripts/`, et
   `sync-canon.sh` est supprimé par [[ADR-101-vault-decides-canon-authority|ADR-101]]). Il se termine
   par un `git push` de la branche courante.
8. `_scripts/evidence-pack.sh` écrit sous le chemin v1 `06-compliance/evidence-pack/` et lit
   `02-decisions/`, `04-audit-trail/`, `05-incidents/`, que le check requis `No V1 Paths (ADR-015)`
   rejette. Les deux evidence-packs créés depuis le refactor v2 (EP-20260418, EP-20260506) l'ont été
   à la main.
9. **La G4 de [[rules-vault]] décrit des mécanismes qui n'existent pas.** Elle cite `ops/work/*` et
   `ops/work/proposals/` (absents), `ledger/decisions/ADR-*.md` (les ADR sont sous
   `ledger/decisions/adr/`), le kill-switch `AI_VAULT_WRITE=false` (aucun code ne lit cette variable ;
   le job `G4: CI read-only sur canon` se contente d'afficher sa valeur) et un hook pre-commit qui
   vérifierait l'auteur du commit (il n'existe pas). Les barrières réelles sont la protection de
   `main` (PR requise, checks requis, `enforce_admins`, voir [[branch-protection]]), le bloc
   `permissions:` de chaque workflow, la permission par défaut du dépôt (`read`) et l'absence de
   `git push` dans les workflows. Rien ne vérifie ces trois derniers points à chaque PR.
10. L'ordre de réponse à incident de [[MOC-Incidents]] (« Kill-switch `AI_VAULT_WRITE=false` ») est
    inapplicable : la variable ne coupe rien.
11. [[airlock-decisions-reference]] rattache DEC-004 (kill-switch) à une section « Kill-switch »
    d'ADR-002 qui n'existe pas.
12. La règle RULE-H6 de [[GOVERNANCE-HUMAN]], qui décrit le circuit d'une proposition d'agent, est
    tronquée au milieu d'une phrase depuis la création du fichier (commit `607ac42`).

## Décision

### D1 — « Airlock » désigne le RPC gate

Restent normatifs : [[ADR-003-rpc-governance|ADR-003]], ADR-010 §1 à §3 (niveaux et modes du RPC
gate, CI comme autorité finale), ADR-002 §2.2 (modes d'opération) et le principe zero-trust d'ADR-002
(« Tous les agents sont considérés non fiables par défaut […] Aucun agent n'écrit directement dans
les repos critiques »). Dans un ADR, une règle ou une fiche, « Airlock » s'entend désormais du RPC
gate seul.

### D2 — Le canal de bundles est retiré

Le canal unique par lequel un agent modifie un dépôt est : **branche + PR sur le dépôt cible**,
soumise à ses checks requis et à ses règles de fusion. Un agent ne fusionne jamais.

Passages retirés, sans réécriture de leur corps :

| ADR | Passage retiré |
|---|---|
| ADR-002 | §2.1 (pipeline bundle → agent-submissions → Airlock) ; ligne « Validateur » du §2.3 ; ligne « Valider le pipeline agent-submissions » du §4.2. Au §2.4, le vault protégé est le dépôt `ak125/governance-vault`, plus `.local/governance-vault/`. |
| ADR-007 | Principe dérivé 2 (« Airlock est le Sas Unique ») en tant que producteur de bundles ; canal `bundle_only` et cible d'écriture `airlock`. |
| ADR-008 | Flux `External ──[bundle]──► Airlock` ; `bundle_only` dans les règles de placement. |
| ADR-009 | Pipeline agent-submissions (§1) ; actions « Valider pipeline agent-submissions » et « Tester Airlock enforce mode avec Claude API » (§5) ; critère de sortie « Revue des bundles rejetés » (§4). |
| ADR-010 | §4 « Bundle Signatures (HMAC-SHA256) ». |
| ADR-011 | Chaîne bundle → agent-submissions → Airlock (§2.1, §2.2) et lignes « INCHANGÉ » du §3.3 pour agent-submissions, Airlock (canal) et la signature HMAC des bundles. Le remplacement d'OpenClaw par Claude API reste en vigueur. |
| ADR-012 | Section « Airlock Integration » et tables `__agent_metrics`, `__airlock_bundles`. |
| ADR-013 | Niveau G2 : « PR sur le dépôt cible → checks requis → review et fusion humaines » remplace la chaîne bundle. Le niveau G3 perd `output: bundle`. Critère Phase 2 « Stabilité » : la mesure « Logs Airlock » devient le registre des incidents ([[MOC-Incidents]]). Retirés : critère « Pipeline opérationnel », critère « Bundle G2 soumis », critère de succès « Pipeline agent-submissions relancé », Étape 3.1 et Étape 4.1-4.2. Cet ADR tient lieu du post-mortem prévu par l'Étape 3.1. |

**Règle de lecture.** Dans les textes historiques (ADR, evidence-packs, rapports) et dans les fiches
d'agents (`ledger/agents/`), « bundle », « agent-submissions » et « Airlock » au sens du canal se
lisent « PR sur le dépôt cible ». Les fiches ne sont pas réécrites une à une.

### D3 — G4 réécrite : écriture par PR, CI en lecture seule

[[rules-vault]] v3.1.0, G4 :

1. **Aucune écriture directe sur `main`.** Toute modification passe par une PR aux commits signés
   (G3), sous les checks requis.
2. **Un agent prépare, un humain fusionne.** Un agent peut préparer une PR dans toute zone du vault.
   Il ne fusionne jamais. La fusion d'une PR qui modifie un ADR, une règle ou une policy est une
   décision (G1). C'est une **règle de conduite** : la protection n'exige aucune revue, et un jeton
   qui peut ouvrir une PR peut aussi la fusionner. La rendre mécanique (identité GitHub distincte
   pour les agents, revue requise) relève de l'owner et sort du périmètre de cet ADR.
3. **La CI ne produit aucun contenu du vault.** Vérifié à chaque PR par
   `_scripts/check-ci-read-only.py` sur chaque workflow : bloc `permissions:` au niveau racine,
   aucun scope `write` hors liste justifiée (`issues`), aucun `git commit` ni `git push`, aucun jeton
   autre que le `GITHUB_TOKEN` du workflow hors exception nommée (le job `dispatch` de
   `canon-publish.yml`, dont le jeton d'App est limité au dépôt cible). Le test
   `_scripts/test_ci_read_only.py` fait tourner ce contrôle sur les workflows réels dans le check
   requis `Vault Scripts Tests`. Le job du check requis `G4: CI read-only sur canon` l'exécute
   aussi une fois son workflow modifié par l'owner (les fichiers `.github/` lui sont réservés).
4. **`AI_VAULT_WRITE` est retiré.** Aucune règle ne s'y réfère plus.

### D4 — Réponse à incident

Le kill-switch `AI_VAULT_WRITE=false` est retiré (DEC-004 de l'Airlock). Face à un agent qui écrit
hors de son mandat : fermer ses PR ouvertes, puis révoquer son accès en écriture, à savoir sa clé de
signature (« Procédure de Révocation » de [[key-registry]]) et le jeton GitHub de la machine qui l'exécute.

### D5 — Retraits

- `_scripts/gov` et `_scripts/evidence-pack.sh` sont supprimés, avec la ligne `.gitattributes` de
  `gov`. Les evidence-packs restent créés à la main sous `ledger/compliance/evidence-pack/`.
- Les documents du canal sont archivés (`ledger/_archive/`, préfixe `archived-`, bandeau ADR-102,
  entrée dans [[INDEX-archive]]) : `BUNDLE-SPEC`, `PROMPT-bundle-producer.v1`, `BUNDLE-REGISTRY`,
  `bundle.schema.v1.json` et l'exemple `bundle.example.v1/`.
- RULE-H6 de [[GOVERNANCE-HUMAN]] est complétée selon D2. RULE-H3 à H5 y renvoient : le droit
  « bundle generation » devient la préparation d'une PR, le « candidat » de RULE-H4 est une PR, et
  « lecture seule pour les agents » (RULE-H5) signifie aucune écriture sur la branche par défaut,
  la fusion humaine valant commit manuel. Un chemin que le dépôt cible réserve à l'owner le reste.

## Options considérées

- **A — Statu quo.** Rejetée. Huit ADR acceptés prescrivent un canal que personne n'utilise, et G4
  promet un kill-switch qui ne coupe rien. Un agent qui applique ces textes à la lettre chercherait un
  canal mort ; en incident, l'ordre prescrit est sans effet.
- **B — Relancer le canal de bundles.** Rejetée. Il double le circuit PR sans rien y ajouter : la PR
  sur le dépôt cible porte déjà la signature des commits (G3), les checks requis et la fusion humaine.
  Il réintroduirait un dépôt, un secret HMAC et des scripts à maintenir, pour un circuit qui n'a traité
  aucun bundle depuis février.
- **C — Retirer l'Airlock en entier.** Rejetée. Le RPC gate est présent et configuré en `enforce` ;
  le retirer serait une décision de sécurité sans rapport avec la dormance du canal.
- **D — Réduire « Airlock » au RPC gate, retirer le canal, réécrire G4 sur les barrières réelles et
  outiller la seule qui ne l'était pas (lecture seule de la CI).** Retenue.

## Ce que cet ADR NE fait PAS

- **Il ne touche pas au monorepo** : `scripts/airlock.sh`, `scripts/tail-bundle.sh`,
  `scripts/pull-openclaw-bundles.sh`, l'entrée `.gitignore` correspondante, le message « gov
  airlock » du hook `pretool-bash-guard`, le skill `governance-vault-ops` et la mention
  d'`AI_VAULT_WRITE` dans le `CLAUDE.md` du monorepo relèvent d'un suivi monorepo.
- **Il ne supprime pas** le dossier `/opt/automecanik/airlock` de la machine DEV et n'archive pas le
  dépôt `agent-submissions` : actions owner.
- **Il ne modifie pas le workflow `vault-governance.yml`** : le branchement du job G4 sur
  `check-ci-read-only.py` est fourni à l'owner sous forme de patch.
- **Il ne traite pas** l'étape 4 de la procédure d'[[ADR-087-command-center-orchestration|ADR-087]]
  (`proposed`, elle cite `gov`), le writer planning d'[[ADR-053-planning-live-system|ADR-053]]
  (conçu pour pousser sur `main`, refusé par la protection), le texte de G8, la section « Kill
  Switches » de [[rules-technical]] (`AI_PROD_WRITE`, autre périmètre), ni les 121 fiches de
  `ledger/agents/` (sur 130) qui mentionnent le canal : la règle de lecture de D2 s'y applique.
- **Il ne réécrit pas l'histoire** : evidence-packs, rapports et entrées d'audit-trail restent tels
  quels (G8).

## Conséquences

### Positives

- Un seul canal d'écriture, celui qui est effectivement utilisé, sous les protections existantes.
- G4 ne décrit plus que des mécanismes réels, et le seul point non vérifié (ce que peuvent faire les
  workflows) l'est désormais à chaque PR.
- L'ordre de réponse à incident désigne des actions qui coupent réellement l'accès.

### Négatives

- La règle « un agent ne fusionne jamais » reste une règle de conduite tant que l'owner n'a pas donné
  aux agents une identité GitHub distincte et exigé une revue.
- Jusqu'au patch owner, le check requis `G4: CI read-only sur canon` reste un marqueur ; le contrôle
  réel passe par `Vault Scripts Tests`.

### Neutres

- Le RPC gate, ses niveaux et ses modes sont inchangés.

## Mise en œuvre (cette PR)

| Fichier | Changement |
|---|---|
| ADR-002, 007, 008, 009, 010, 011, 012, 013 | `amended_by: ["ADR-102"]` (frontmatter seul, corps inchangé) |
| `ledger/rules/rules-vault.md` | v3.1.0 : G4, checklist, sanctions, références |
| `_scripts/check-ci-read-only.py`, `_scripts/test_ci_read_only.py` | nouveaux (D3.3) |
| `_scripts/gov`, `_scripts/evidence-pack.sh`, `.gitattributes` | supprimés / ligne retirée (D5) |
| `ledger/policies/BUNDLE-SPEC.md`, `ledger/policies/prompts/PROMPT-bundle-producer.v1.md`, `ledger/agents/bundles/BUNDLE-REGISTRY.md`, `ledger/policies/bundle.schema.v1.json`, `ledger/policies/examples/bundle.example.v1/` | archivés sous `ledger/_archive/` (D5) |
| `ledger/_archive/INDEX-archive.md`, `ops/moc/MOC-Policies.md`, `ledger/agents/bundles/INDEX-agents-bundles.md`, `ops/moc/MOC-Agents.md` | liens vers les archives |
| `ops/GOVERNANCE-HUMAN.md` | RULE-H6 complétée, RULE-H3 à H5 alignées (D2, D5) |
| `ops/moc/MOC-Incidents.md`, `ledger/knowledge/airlock-decisions-reference.md` | réponse à incident (D4), DEC-002/004/006 |
| `ledger/policies/PROCESS-G1-design.md` | mention du canal retiré |
| `CLAUDE.md`, `AGENTS.md`, `README.md`, `99-meta/onboarding/claude-desktop-instructions.md`, `99-meta/{ci-policy,deploy-bot,governance-runtime-map,branch-protection}.md`, `ops/moc/{MOC-Governance,MOC-Rules}.md` | G4 et retraits alignés |
| `ops/moc/MOC-Decisions.md` | index régénéré (`sync_moc_decisions.py --write`) |

## Références

- [[ADR-002-airlock-zero-trust]], [[ADR-003-rpc-governance]], [[ADR-010-airlock-enforce-activation]],
  [[ADR-013-agent-lifecycle-governance]], [[ADR-015-vault-single-source-of-truth]],
  [[ADR-060-repository-roles-doctrine]], [[ADR-061-workspace-governance]],
  [[ADR-101-vault-decides-canon-authority]]
- [[rules-vault]], [[branch-protection]], [[key-registry]], [[ci-policy]], [[GOVERNANCE-HUMAN]]
