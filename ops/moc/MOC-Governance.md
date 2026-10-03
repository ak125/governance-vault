---
type: moc
status: canon
role: master-index
updated: 2026-10-03
---

# MOC: Governance

**Master Index** du vault de gouvernance AutoMecanik. Point d'entree unique de navigation.

> Ce MOC ne contient pas de statistiques numeriques. Chaque metrique vit dans sa source canonique unique (voir la section "Single Source of Truth" ci-dessous). Cette discipline garantit qu'aucun chiffre ne peut deriver entre l'index et la realite.

---

## Navigation Principale

| MOC | Role |
|-----|------|
| [[MOC-Decisions]] | Index des ADR (statuts a jour, source canonique = frontmatter de chaque ADR) |
| [[MOC-Rules]] | Taxonomie T / G / AI / V / R-SEO / R-SEO-KW / AP / D / Q / AEC — regles canoniques |
| [[MOC-Compliance]] | Plans d'execution, checklists, evidence-packs |
| [[MOC-Agents]] | Catalogue agents par categorie (registry SoT : [[REG-001-agents]]) |
| [[MOC-Incidents]] | Post-mortems et incidents |
| [[MOC-Knowledge]] | Base de connaissances (specs, guides) |
| [[MOC-AuditTrail]] | Audit-trail, bundles rejetes, audits RPC |
| [[MOC-Policies]] | Specifications, processus, templates |
| [[MOC-Repository-Control-Plane]] | Repository Control Plane du monorepo (ADR-058) : registry en couches, gates CI progressifs |
| [[MOC-Roadmap-2026]] | Chantiers transverses 2026 (identifiants et rangs de priorite ; n'ordonne pas l'execution hebdomadaire) |
| [[MOC-Planning-Live]] | Planning vivant, section auto-generee par le moteur de sync (ADR-053) |

---

## Regles Vault (G1-G4)

Les regles G1-G4 de gouvernance du vault lui-meme. Voir [[rules-vault]].

| Regle | Description | Enforcement |
|-------|-------------|-------------|
| G1 | Le vault decide (ADR-101) | Decision = ADR `accepted` ; divergence decision/code signalee |
| G2 | Zero orphelin | `_scripts/check-orphans.sh` |
| G3 | Commits signes | Check requis `G3: Commits signes` + hook `pre-push` |
| G4 | Ecriture par PR, CI en lecture seule (ADR-102) | Protection de `main` + `_scripts/check-ci-read-only.py` (checks requis `G4: CI read-only sur canon` et `Vault Scripts Tests`) ; fusion par un humain (regle de conduite) |

---

## Taxonomie Canonique

Voir [[MOC-Rules]] pour la taxonomie complete (T / G / AI / V / R-SEO / R-SEO-KW / AP / D / Q / AEC). Aucune duplication ici — la taxonomie a une source unique.

---

## Single Source of Truth

> Le `governance-vault` est la **source de verite unique des documents de gouvernance operationnelle** (ADR, rules, MOCs, audit-trail, evidence-packs, runbooks, registry agents — formalise par [[ADR-015-vault-single-source-of-truth]]). Le **canon architectural** (contrats de schemas, code patterns figes) reste dans `.spec/00-canon/` du monorepo ; son rang est fixe par [[rules-vault]] G1 (contrat consomme = fait foi dans son domaine, prose sans consommateur = aucune autorite).

### Glossaire `canon` (polysemie levee)

Le mot `canon` apparait sous plusieurs sens distincts dans le vault et ses fichiers d'instructions. **Ce glossaire definit les termes (semantique linguistique) ; il n'etablit aucune autorite.** L'autorite pour chaque acception reste dans son document canonique (regles, ADR, registries) qui est cite plutot que duplique.

| Terme | Definition (semantique) | Source d'autorite |
|-------|--------------------------|-------------------|
| **canon architectural** | Contrats de schemas, code patterns figes, source-of-truth applicative. Concept distinct du contenu de gouvernance. | [[rules-vault]] G1 designe la SoT actuellement en vigueur. Toute revision passe par un ADR. |
| **document canonique** | Document avec autorite editoriale dans le vault (`type: moc` ou ADR `status: accepted`). C'est ce que designe `status: canon` dans un frontmatter MOC. **N'implique pas "canon architectural"**. | Schema de frontmatter `_scripts/schemas/moc.schema.json` + ADR du document concerne. |
| **canonical registry** | Registry designe SoT pour son domaine (autorite par domaine, pas statut editorial). | Le registry lui-meme + son frontmatter (ex. [[REG-001-agents]] frontmatter `id: REG-001`). |
| **canonical source** | Endroit unique ou une information donnee vit ; tout le reste est derive (index, miroir, projection). Principe DRY applique a la gouvernance. | Concept architectural — voir PR-1 (refactor MOC-Governance) pour application concrete. |

Lorsque le mot `canon` est utilise sans qualificatif, il faut preferer l'interpretation `document canonique` (sens editorial), sauf si le contexte rend explicite qu'il s'agit de canon architectural (mots-cles : "code", "schemas", "patterns figes", reference explicite a une regle de la famille G).

---

## Meta

- [[README]] - Documentation generale du vault
- [[signing-policy]] - Politique de signature (SSH ed25519)
- [[key-registry]] - Registre des cles SSH
- [[sync-log]] - Log de synchronisation canon
- [[ci-policy]] - Politique CI/CD (read-only sur canon)
- [[cron-setup]] - Configuration des tasks cron
- [[deploy-bot]] - Role du bot CI/CD (non-SPOF)
- [[claude-desktop-instructions]] - Onboarding Claude Desktop (MCP filesystem, condense CLAUDE.md + AGENTS.md)
- [[obsidian-setup]] - Topologie canonique coffre Obsidian (1 clone = 1 vault, plugins Dataview/Templater/Git, SSH signing G3)
- [[branch-protection]] - Politique de protection de la branche main
- [[canon-dispatch-setup]] - Identifiants GitHub App du workflow canon-publish (dispatch vers les depots consommateurs)
- [[governance-runtime-map]] - Carte des scripts et chemins d'ecriture/lecture du vault (instantane du 2026-05-10)

## Archive

- [[INDEX-archive]] - Documents archives (superseded, OpenClaw, etc.)

---

## Cycle de Vie

```
Probleme/Incident -> [[MOC-Incidents]]
        |
        v
Decision prise  -> [[MOC-Decisions]] (nouveau ADR)
        |
        v
Plan execute    -> [[MOC-Compliance]] (plan + checklist)
        |
        v
Preuves         -> [[MOC-Compliance]] (evidence-pack)
        |
        v
Audit-trail     -> [[MOC-AuditTrail]] (retrospective, rejects)
```
