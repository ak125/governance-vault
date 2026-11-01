---
type: index
status: canon
category: archive
updated: 2026-10-01
---

# INDEX: Archive

> Documents **archives** : contenu obsolete, superseded, ou historique. Conserves pour tracabilite mais non maintenus.

**Parent MOC**: [[MOC-Governance]]

---

## Raisons d'Archivage (G8)

Voir [[rules-governance-process]] G8 (Obsolete Handling). Un document est archive quand :

1. Il est **superseded** par un autre document (decision remplacee)
2. Il decrit un **composant supprime** ou retire (ex: OpenClaw, voir [[ADR-011-openclaw-claude-api-replacement]] ; canal de bundles, voir [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]])
3. Il represente une **phase terminee** non-pertinente au present

L'archivage ne supprime pas le document : il le retire de la circulation active.

---

## Contenu

| Document | Raison | Remplace par |
|----------|--------|--------------|
| [[archived-2026-02-05-openclaw-security-fix]] | OpenClaw supprime du monorepo | [[ADR-011-openclaw-claude-api-replacement]] |
| [[archived-DEC-OPENCLAW-CHROMIUM-NO-SANDBOX]] | OpenClaw supprime du monorepo | [[ADR-011-openclaw-claude-api-replacement]] |
| [[archived-BUNDLE-SPEC]] | Canal de bundles retire | [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] |
| [[archived-PROMPT-bundle-producer.v1]] | Canal de bundles retire | [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] |
| [[archived-BUNDLE-REGISTRY]] | Canal de bundles retire | [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] |
| `archived-bundle.schema.v1.json` | Canal de bundles retire | [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] |
| `archived-bundle.example.v1/` (manifest, constraints, evidence, patch) et son [[report]] | Canal de bundles retire | [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] |

---

## Voir aussi

- [[MOC-Governance]] - Index maitre
- [[rules-governance-process]] - G8 Obsolete Handling
- [[ADR-011-openclaw-claude-api-replacement]] - ADR superseding (OpenClaw)
- [[ADR-102-airlock-rpc-gate-bundle-channel-retired-g4]] - Retrait du canal de bundles

---

_Derniere mise a jour: 2026-10-01 (ADR-102)_
