---
id: INC-2026-016
date: "2026-05-27"
date_detected: "2026-05-27"
severity: high
status: open
impact_duration: "ongoing since 2026-05-26 23:01 UTC (PR #765 merge)"
affected_systems:
  - "ak125/nestjs-remix-monorepo .claude/skills/continuous-improvement-global/SKILL.md"
  - "ak125/nestjs-remix-monorepo .spec/00-canon/improvement-report.schema.json"
  - "ak125/nestjs-remix-monorepo .github/PULL_REQUEST_TEMPLATE.md"
root_cause: "Monorepo PR #765 (merge SHA d2cc2dbba4eaf5e1cfe461727805874500761fa7, mergée 2026-05-26 23:01 UTC) a mergé 3 artefacts revendiquant 'Doctrine canon = ADR-082 vault' alors qu'ADR-082 n'existe qu'en branche draft non-ratifiée du vault (adr/082-continuous-improvement-doctrine). Inversion du flux d'autorité ADR-060 (vault décide → monorepo exécute) + violation Invariant G3 (écriture canon vault = PR signée G3). Le monorepo a posé une doctrine que le vault n'a pas encore décidée."
related_rules: ["G3"]
related_adr: ["ADR-060", "ADR-015"]
owner: "@fafa"
reviewed_by: ""
---

# Incident: Monorepo PR #765 — Authority drift "canon ADR-082" déclaré avant ratification vault

## Timeline

| Heure (UTC) | Événement |
|-------------|-----------|
| 2026-05-26 23:01:59 | PR #765 mergée dans `ak125/nestjs-remix-monorepo` (merge commit `d2cc2dbba4eaf5e1cfe461727805874500761fa7`). Ajoute 9 fichiers dont 3 artefacts revendiquant "canon ADR-082 vault". |
| 2026-05-27 | Audit gouvernance assistant (3 explorations parallèles). Détection : ADR-082 absent vault `main`, seule branche draft `adr/082-continuous-improvement-doctrine`. |
| 2026-05-27 | Cross-vérification ADR-060 §Decision + Invariant 2 : violation confirmée (`vault décide → monorepo exécute` + G3 signed PR pour écriture canon vault). |
| 2026-05-27 | Audit élargi : pattern systémique détecté — 4 ADR-08X orphelins + ~20 fichiers `.spec/00-canon/` sans backing vault. |
| 2026-05-27 | Incident ouvert. Branche vault `incident/INC-2026-016-monorepo-pr765-authority-drift`. |

## Impact

- **Utilisateurs affectés** : 0 (gouvernance interne, pas de runtime utilisateur)
- **Transactions perdues** : 0
- **Durée d'indisponibilité** : N/A (pas un outage)
- **Impact business** : drift d'autorité gouvernance. Le vault perd son rôle de **décideur effectif** au profit d'une autorité **déclarative**. Si le pattern continue : chaque PR monorepo peut créer sa mini-doctrine, le vault devient bibliothèque de références, plus organe de décision. Risque de cascade sur d'autres bounded contexts.

## Root Cause

ADR-060 énonce clairement (§Decision, table canon 5 acteurs + Invariants 2-3) :

> **Vault** : *Décide*. ADR, rules T/G/AI/V, policies, MOCs, runbooks. **Pas d'écriture métier**.
>
> **Monorepo** : *Exécute*. Runtime NestJS + Remix. Lit wiki/exports et bases DB métier. **N'écrit ni dans raw, ni dans wiki, ni dans vault**.
>
> **Invariant 2** : L'écriture canon dans vault passe par **PR signée G3** (cf. [[ADR-015-vault-single-source-of-truth]]).

CLAUDE.md du monorepo réaffirme : « ce fichier est un contrat d'exécution + pointer, et il ne contient aucune règle canonique de gouvernance, car les ADR/rules/policies vivent dans le vault ».

PR #765 a livré 3 artefacts qui **revendiquent explicitement** un statut "canon ADR-082" :

1. **`.claude/skills/continuous-improvement-global/SKILL.md`** (171 lignes ajoutées)
   - Ligne 3 (description frontmatter) : `Doctrine canon = ADR-082 vault (Global Continuous Improvement Doctrine).`
   - Ligne 14 (banner) : `> **Filtre** opérationnel — pas un nouveau système. Doctrine canon = ADR-082 vault.`
   - Ligne 62 : `**Schema canonique (SoT unique)** : .spec/00-canon/improvement-report.schema.json`
   - Ligne 155-156 : référence directe à `governance-vault/ledger/decisions/adr/ADR-082-global-continuous-improvement-doctrine.md` — fichier qui **n'existe pas**

2. **`.spec/00-canon/improvement-report.schema.json`** (417 lignes ajoutées)
   - Ligne 4 : `"title": "Improvement Report v1 (canon ADR-082)"`
   - Ligne 5 : `"description": "...Conforme à la doctrine d'amélioration continue globale (ADR-082 vault)..."`

3. **`.github/PULL_REQUEST_TEMPLATE.md`** (43 lignes ajoutées)
   - Ligne 1 : commentaire fichier `(ADR-082 vault)`
   - Ligne 21 : marqueur `IMPROVEMENT_GATE_BEGIN — canon ADR-082 vault, marqueurs requis pour validation auto Phase 2 (improvement-gate.yml)`
   - Ligne 23 : section obligatoire `## Improvement Gate (canon ADR-082)`

**Vérification vault** (2026-05-27) :
- `ls /opt/automecanik/governance-vault/ledger/decisions/adr/ADR-082-*.md` → `No such file or directory`
- Numérotation s'arrête à ADR-081 en `main`
- Branche `adr/082-continuous-improvement-doctrine` existe (local + remote) mais **non mergée, pas de commit signé G3, pas de PR review/approval**

**Conclusion** : le monorepo a pu poser une "doctrine canon" sans aucun gate mécanique pour bloquer une revendication d'ADR vault inexistant. ADR-060 est lettre morte tant qu'aucun mécanisme CI ne vérifie le couplage référence-canon ↔ fichier-vault.

## Résolution

### Décision owner @fafa (2026-05-27) — Voie 3 : Amender ADR-082 en lightweight advisory perpétuel

**Décision actée** : ADR-082 ratifié vault uniquement en **mode lightweight advisory perpétuel**. Aucun blocking gate par défaut. Toute promotion future vers blocking gate exigera un **amendement vault séparé** (PR vault G3-signed), pas owner GO seul. C'est la leçon directe de cet incident encodée dans la doctrine elle-même.

Draft amendée prête : `/tmp/adr-draft-ADR-082-amended-voie3.md` (validée contre `adr.schema.json` vault). Frontmatter conformé, contenu enrichi d'une section "Amendement Voie 3" explicite (verrou A1-A5), Phase 4 originelle (adoption obligatoire) **supprimée**, Phase 3 (ratchet bloquant) gated par amendement vault séparé.

### État durable post-amendement Voie 3

- Skill `.claude/skills/continuous-improvement-global/SKILL.md` : reste advisory (`status: experimental` actuel acceptable, ou promotion `stable` post-amendement vault à la discrétion owner — dans les 2 cas, description + banner conservent "advisory only, never default-blocking per ADR-082 amended Voie 3").
- Schema `.spec/00-canon/improvement-report.schema.json` : `$comment` conservé pour signaler statut advisory ; `title` peut perdre "(proposed)" post-amendement vault.
- PR template `Improvement Gate` : reste `[OPTIONAL]` dans `<details>` collapsé **perpétuellement**.
- CI gate `vault-canon-exists.yml` : reste **warn-only** (`continue-on-error: true`). Promotion vers blocking = amendement vault séparé.

### Voies alternatives rejetées (pour archive)

**Voie 1 (ratification brute, blocking dès Phase 3 sur owner GO seul)** : rejetée car laisse owner GO comme verrou unique. Insuffisant après cet incident.

**Voie 2 (rejet total)** : rejetée car le travail de doctrine v15.4 a une valeur réelle (filtre 6 questions, hiérarchie P1-P6, anti-complexité, SAFE intégré) ; perdre ça serait jeter le bébé avec l'eau du bain. La doctrine est utile en mode advisory.

### Actions immédiates monorepo (assistant-executable, indépendantes de la décision owner)

Ces actions **respectent ADR-060** dans tous les cas (downgrade pas revendication) et sont compatibles avec les 3 voies :

- **Phase B** (assistant, ~80 lignes net, 3 fichiers) : downgrade des 3 artefacts de "canon ADR-082" → "experimental, advisory only". Inclut bannière `⚠️ EXPERIMENTAL — DO NOT TREAT AS CANON`, frontmatter `status: experimental` + `metadata: { vault_ratification: pending, vault_adr_ref, vault_incident_ref: INC-2026-016 }`, schema `$comment` warning + title/description nettoyés (`$id` intact, 9 verdicts enum intacts), PR template section encapsulée `<details>` + préfixe `[OPTIONAL — EXPERIMENTAL]`. Réversible en 1 PR de promotion ~10 lignes si Voie 1 retenue.

- **Phase C1** (assistant, 1 fichier workflow) : nouveau gate CI `vault-canon-exists.yml` warn-only V1. Détecte toute référence "canon ADR-XXX" dans `.claude/`, `.spec/`, `.github/`, `CLAUDE.md` sans backing vault `main`. Vault checkout sparse (~50ms, vault public confirmé `gh api repos/ak125/governance-vault --jq .private` → `false`). Output `$GITHUB_STEP_SUMMARY` only (0 supply chain risk). Promotion vers blocking = 2-line PR follow-up après ratification du premier ADR via ce mécanisme (preuve de fonctionnement).

## Lessons Learned

1. **ADR-060 reste lettre morte sans CI gate mécanique**. Une doctrine d'autorité non vérifiée par la CI est déclarative, pas opérante. Phase C1 (gate `vault-canon-exists.yml`) restaure la vérifiabilité.

2. **`.spec/00-canon/` agit comme vault parallèle**. ~20 fichiers `.md/.json` se présentent comme "source de vérité" sans pointeur ADR vault. Pattern à auditer (cf. Annexe — Systemic finding). **Owner-action requise séparée**, pas dans cet incident.

3. **Le processus de review PR n'a pas attrapé "canon ADR-082" sur un ADR inexistant en vault**. La review humaine seule est insuffisante pour des claims qui demandent une vérification cross-repo. Le gate mécanique (Phase C1) comble ce gap.

4. **Les disclaimers internes (`soft signal pas hard gate`) n'effacent pas un claim "canon"**. Une seule mention "canon ADR-XXX" suffit à inverser le flux d'autorité, indépendamment des nuances internes. Doctrine v15.4 du skill (`soft signal pas hard gate`) ne suffit pas si le PR template revendique normativement "canon ADR-082".

## Actions Correctives

- [x] **Owner @fafa** : décide Voie 3 (lightweight advisory perpétuel) sur ADR-082 — **2026-05-27** ✅
- [x] **Assistant** : PR monorepo Phase B downgrade des 3 artefacts — **PR #771 MERGED 2026-05-27 21:42 UTC SHA `97af9f667a`** ✅
- [x] **Assistant** : PR monorepo Phase C1 gate `vault-canon-exists.yml` warn-only — **PR #772 auto-merge SQUASH queued 2026-05-27 21:43 UTC** ⏳ (auto-merge handled)
- [x] **Assistant** : draft ADR-082 amendée Voie 3 prête + validée — **`/tmp/adr-draft-ADR-082-amended-voie3.md`** ✅
- [ ] **Owner** : push incident vault G3 (commandes paste-ready livrées Phase A3) — **deadline 2026-05-28**
- [ ] **Owner** : push PR vault ADR-082 amendée Voie 3 G3-signed (draft prête `/tmp/adr-draft-ADR-082-amended-voie3.md`) — **deadline 2026-06-03**
- [ ] **Owner** : audit séparé des 3 autres ADR-08X orphelins (ADR-075 / ADR-073 / ADR-054) — **pas de deadline (hors scope incident)**
- [ ] **Owner** : audit séparé `.spec/00-canon/` (~20 fichiers sans backing) — **pas de deadline (hors scope incident)**
- [ ] **PERMANENT (Voie 3)** : gate `vault-canon-exists.yml` reste warn-only **perpétuellement**. Toute promotion vers blocking exige amendement vault séparé (PR G3, owner GO seul insuffisant).

## Preuves

- PR monorepo originelle : <https://github.com/ak125/nestjs-remix-monorepo/pull/765>
- Merge commit SHA : `d2cc2dbba4eaf5e1cfe461727805874500761fa7`
- Vérification ADR-082 absent vault main : `ls /opt/automecanik/governance-vault/ledger/decisions/adr/ADR-082-*.md` retourne `No such file or directory` (2026-05-27)
- Branche draft vault : `adr/082-continuous-improvement-doctrine` (local + `remotes/origin/`)
- Citations exactes monorepo : SKILL.md L3+L14+L62, schema.json L4-5, PR_TEMPLATE.md L1+L21+L23
- Schema `$id` actuel intact : `"improvement-report.schema.json"` (relatif, à ne pas changer en downgrade)

---

## Annexe A — Systemic finding (drift plus large que #765)

**Owner-action requise séparée, hors scope de cet incident.**

### A.1 — 4 ADR-08X référencés par le monorepo mais absents vault `main`

État fresh re-vérifié 2026-05-27 :

| ADR | Présent vault `main` ? | Branche vault | Référence(s) monorepo |
|-----|---|---|---|
| ADR-082 | ❌ Absent | `adr/082-continuous-improvement-doctrine` (draft) | SKILL.md, schema, PR template (cet incident) |
| ADR-075 | ❌ Absent | `adr/075-deployment-topology-clarification` (draft, PR vault #294 stagnante 8j au 2026-05-27) | `.claude/rules/deployment.md` (2 refs), `CLAUDE.md` (2 refs) |
| ADR-073 | ❌ Absent | aucune branche détectée | `.claude/skills/runtime-truth-audit/checks/attribution-write-gap.md` (3 refs) |
| ADR-054 | ❌ Absent | aucune branche détectée | `backend/src/modules/seo-shadow-observatory/README.md` (2 refs), `CLAUDE.md` (2 refs) |

### A.2 — Pattern `.spec/00-canon/`

~20 fichiers `.md/.json` se présentent comme "source de vérité" ou "canon" sans pointeur ADR vault explicite (audit assistant 2026-05-27). Bottleneck à arbitrer : ces fichiers sont-ils "source de vérité" canon (devraient avoir backing ADR vault) ou "implementation detail" (statut clarifié) ?

**Pas d'action immédiate dans cet incident.** Ratification 1:1 dans vault ou re-qualification = décision owner distincte.

---

## Annexe B — Garde-fou explicite : Allowlist PR monorepo pendant draft vault

Cette section est **doctrinale** et invariant opérationnel pendant que ADR-082 (ou tout ADR référencé "canon" dans le monorepo) reste en draft non-ratifié vault.

Les seules PR monorepo autorisées qui touchent à `.claude/`, `.spec/`, `.github/`, `CLAUDE.md` (ou contenu à poids normatif) :

✅ **Autorisé** :
- Downgrade canon → experimental / advisory / proposed
- Neutralisation d'un gate (warn-only, optional, collapsible)
- Détection warn-only (CI gate qui prévient sans bloquer)
- Mise à jour purement éditoriale (typo, lien)
- Documentation explicite du statut draft / pending

❌ **Interdit** :
- Promotion d'un statut experimental → canon
- Activation d'un gate bloquant
- Extension de la doctrine ADR-XXX (nouveaux verdicts, nouveaux critères, nouveaux templates)
- Référence à un nouvel ADR-XXX inexistant en vault
- Ajout d'un nouveau fichier dans `.spec/00-canon/` se présentant comme "source de vérité" sans backing vault

Toute PR violant cette allowlist doit être bloquée (en attendant que le gate Phase C1 soit actif, le contrôle reste humain via review).
