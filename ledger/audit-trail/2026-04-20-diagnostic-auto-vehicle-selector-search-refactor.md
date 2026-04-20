---
type: retrospective
status: complete
date: 2026-04-20
owner: [Fafa, Claude]
branch: feat/diagnostic-engine-public-surface (PR #85)
related_incident: `INC-2026-003` (post-mortem dans vault PR #9, pending merge to main)
related_adrs: []
tags: [frontend, diagnostic, shadcn, accessibility]
---

# Diagnostic Auto — VehicleSelector + SearchBar shadcn Command + ⌘K

> Suite editoriale UX du plan breezy-eagle (INC-2026-003) : sur la landing `/diagnostic-auto`, ajout d'un VehicleSelector non-redirectif (Marque/Annee/Modele/Motorisation) et migration du sélecteur de recherche vers la primitive shadcn `Command` avec raccourci global `⌘K`.

---

## TL;DR

**Verdict** : feature prete cote code (TypeScript, ESLint, Backend Tests, Frontend Tests, CodeQL, governance gates tous verts). Fails CI residuels `Validate Specifications` et `CWV Performance Check` connus pre-existants (documentes dans INC-2026-003 closure), infra CI non liee au code.

**Effort** : 3 commits, 8 fichiers touches, 0 nouvelle dependance (cmdk + shadcn Command deja installes).

---

## Livrables

### Commit 1 — `722a30c2` : SearchBar → shadcn Command + ⌘K

Migration de `DiagnosticSearchBar` depuis un dropdown maison (161 LoC, logique ARIA/keyboard custom) vers la primitive shadcn `<Command>` (cmdk).

- ARIA combobox + listbox + option natif via cmdk (zero code custom)
- Navigation clavier (Arrow↑↓, Enter, Esc) native
- Groupes de resultats : **Symptomes** / **Entretien** / **Codes OBD-II** + separateurs
- Highlight du substring recherche via `<mark>`
- Badge urgency (rouge critical/high, amber medium, slate low)
- Raccourci global `⌘K` / `Ctrl+K` via `<CommandDialog>` + hint kbd visible
- `min-h-[44px]` sur `CommandItem` (WCAG AA touch target)

**Patch de la primitive** : `CommandDialog` etendu pour forward `shouldFilter` / `filter` / `loop` vers le `<Command>` interne. Requis car on filtre cote serveur (RAG + DB), pas cote client cmdk. 3 lignes de type, rien de breaking.

### Commit 2 — `25447c35` : VehicleSelector sur la landing

Ajout du composant partage `~/components/vehicle/VehicleSelector` (mode `full`) dans le hero `/diagnostic-auto`.

- 4 champs labellises : **Marque → Annee → Modele → Motorisation**
- `redirectOnSelect={false}` → reste sur la page (pas de redirect vers `/constructeurs/...`)
- `onVehicleSelect` callback stocke le vehicule en React state
- Apres selection : le selecteur se replie en **badge contextuel emerald** "Vehicule : Renault Clio 2020 • 1.5 dCi" + bouton `×` pour reset
- Reutilise le composant existant (pas de duplication)

### Commit 3 — `4197a8cc` : vehicleTypeId propage via query param

Le `type_id` du vehicule selectionne est forwarde en `?type=<id>` sur toutes les navigations issues de la SearchBar (inline + CommandDialog).

- Nouveau prop optionnel `vehicleTypeId?: number` sur `DiagnosticSearchBar`
- `routeFor()` construit `/diagnostic-auto/symptome/:slug?type=:id` (idem DTC et entretien)
- Backend search endpoint inchange (ignore les parametres inconnus, pas de rupture)
- Les routes downstream pourront opt-in : `searchParams.get("type")` pour scoper causes/symptomes au vehicule

---

## CI status (PR #85, commit `4197a8cc`)

### PASS (15 checks)

TypeScript · ESLint · Backend Tests · Frontend Tests · CodeQL (×2) · Core Build · Security Audit · Secrets Detection · Migration Safety · Import Firewall · RPC Safety Gate · ADR-010 Governance · DEV Safety (×2)

### FAIL (2 checks — pre-existants infra CI)

- `Validate Specifications` (18s) — attendu `.spec/api` inexistant
- `🔍 CWV Performance Check` (4m9s) — timeout boot en CI

Documentes comme fails infra pre-existants dans `INC-2026-003` (post-mortem dans vault PR #9, pending merge to main) closure (section "Bloqueurs residuels hors scope"). A resoudre par PR infra dediee.

---

## Decisions cles

1. **Pas de nouvelle dependance**. `cmdk` et `@tanstack/react-query` sont deja dans `package.json`. Ajouter un plugin = dette (conforme `.claude/rules/frontend.md` : shadcn/ui uniquement).
2. **Pas de `useQuery`**. Verification grep : `QueryClientProvider` absent du `root.tsx` et de tout l'arbre frontend. Introduire `useQuery` crasherait. Maintien du debounce + AbortController custom (220 ms).
3. **Pas de scope backend pour l'instant**. Le `?type=<id>` est forwarde cote frontend mais le service `diagnostic-engine/search` n'utilise pas encore le parametre. Evolutive : les routes downstream peuvent lire `searchParams.get("type")` sans requerir de modification backend. Le scope backend fera l'objet d'une PR dediee pour eviter de toucher le service RAG stabilise post-INC-2026-003.
4. **Eslint `no-restricted-syntax` disable** sur `command.tsx:44` : le rule flaggait `[hidden]` comme classe Tailwind alors que c'est un selecteur d'attribut CSS cmdk. Disable cible avec commentaire explicatif, pas de relachement de la regle globale.

---

## Audits automatises passes

- `mcp__shadcn__get_item_examples_from_registries` pour `combobox-demo` + `command-dialog` → pattern canonique shadcn applique
- `responsive-audit` skill : 0 critique, 1 haute corrigee (`min-h-[44px]` WCAG), conformes sur les 10 checklists
- `npm run typecheck` : 0 erreur
- `npx eslint` sur 3 fichiers changes : 0 erreur, 0 warning

---

## Fichiers touches

| Fichier | LoC avant | LoC apres | Delta |
|---|---|---|---|
| `frontend/app/components/diagnostic-public/DiagnosticSearchBar.tsx` | 161 | 274 | +113 (cmdk + dialog + groupes + highlight + vehicleTypeId) |
| `frontend/app/components/ui/command.tsx` | 151 | 169 | +18 (CommandDialogProps type) |
| `frontend/app/routes/diagnostic-auto._index.tsx` | ~325 | ~378 | +53 (VehicleSelector + state + badge) |

---

## Reference

- PR : https://github.com/ak125/nestjs-remix-monorepo/pull/85
- Commits : `722a30c2`, `25447c35`, `4197a8cc`
- Related incident : `INC-2026-003` (post-mortem dans vault PR #9, pending merge to main) (breezy-eagle closure)
- UI primitives : shadcn Command (`cmdk` ^1.1.1) + Dialog + Badge

---

## Follow-ups possibles (hors scope)

- [ ] Backend `search(q, limit, vehicleTypeId?)` → scope causes/symptomes au vehicule (PR dediee)
- [ ] Propager `?type=` a `DtcQuickLookup`, `SystemCardsGrid`, `PopularSymptomsGrid` (coherence — a faire APRES le scope backend pour eviter le gold-plating)
- [ ] Fix infra CI `Validate Specifications` + `CWV Performance Check` (PR infra dediee)

---

**Session** : 2026-04-20 — auto mode actif, user `automecanik.seo@gmail.com`.
