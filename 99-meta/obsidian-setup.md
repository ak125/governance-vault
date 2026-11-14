---
type: knowledge
status: current
updated: 2026-11-14
audience: [onboarding, obsidian-user]
related_adr: [ADR-015, ADR-102, ADR-126]
related_rules: [G2, G4]
---

# Lire le vault avec Obsidian (usage facultatif)

> **Portée** : note d'usage, sans autorité ([[ADR-126-obsidian-lecteur-facultatif-circuit-ecriture-unique|ADR-126]]).
> Le vault est un dépôt Git de fichiers Markdown reliés par des wikilinks `[[...]]`. Aucune règle ni
> procédure ne demande Obsidian : un éditeur de texte, GitHub ou tout lecteur Markdown suffit. Obsidian
> n'est qu'un moyen commode de **lire** le vault et de suivre ses wikilinks.

---

## Écrire dans le vault : pas depuis Obsidian

Toute écriture suit le circuit unique de [[AGENTS]] (section « Workflow nouveau-document ») : worktree
dédié créé depuis `origin/main`, `_scripts/preflight-write.sh`, commits signés ([[rules-vault|G3]]), PR
vers `main`, fusion par l'owner ([[rules-vault|G4]]). Obsidian ne commite pas, ne pousse pas et n'ouvre
pas de PR.

## Clone de lecture

- Un **clone Git autonome** de `ak125/governance-vault`, avec son propre `.git/`, hors de tout autre
  dépôt (jamais un sous-dossier du monorepo ni d'un autre coffre Obsidian).
- Un seul coffre Obsidian par clone : « Open folder as vault » sur la racine du clone. Ne pas créer de
  coffre dans un sous-dossier : Obsidian y écrirait des fichiers parasites.
- Pas de téléchargement ZIP : sans `.git/`, la copie ne se met plus à jour.
- Ce clone sert à lire. Pour écrire, créer un worktree selon [[AGENTS]] ; ne pas modifier les fichiers
  du clone de lecture.

## Plugins

- **Aucun plugin n'est requis.** Le vault ne contient aucune requête Dataview ni syntaxe Templater ; les
  modèles de documents sont les fichiers Markdown de `_templates/`, copiés à la main.
- **Plugin Git (facultatif)** : *pull* seul, pour garder le clone à jour. Désactiver auto-commit et
  auto-push, et n'utiliser ni « Commit » ni « Push » depuis l'interface.
- **Notes quotidiennes et Canvas** (plugins de base) : les désactiver. Ils créent des fichiers
  (`AAAA-MM-JJ.md`, `*.canvas`) qui n'ont pas leur place dans le vault et que G2 refuse.

## Fichiers locaux d'Obsidian

La configuration `.obsidian/` et les snapshots `_backups/` du plugin Git restent propres au poste :
`.gitignore` les exclut. Le dépôt est public ; rien de cette configuration n'y est versionné.

## Référence croisée

- [[AGENTS]] : circuit d'écriture unique
- [[CLAUDE]] : instructions détaillées des agents
- [[signing-policy]] : configuration de la signature des commits (G3)
- [[ADR-015-vault-single-source-of-truth]] : le vault, source unique de la gouvernance opérationnelle
