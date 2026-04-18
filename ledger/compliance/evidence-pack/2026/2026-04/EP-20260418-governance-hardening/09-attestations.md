---
type: attestations
---

# Attestations

## Compliance Attestation

Je, soussigne, atteste que :

1. Toutes les modifications durant la periode 2026-04-17 → 2026-04-18 ont ete appliquees via PR sur `main` avec branch protection active (G1, G2, G3, G4)
2. Toutes les PRs ont passe les 4 required status checks (G2 orphelins, broken wikilinks, G3 signed commits, G4 CI read-only)
3. Tous les commits sont **signes** avec la cle K002 (Fafa Windows, `~/.ssh/id_ed25519`), verifiables via `git log --show-signature`
4. Aucun document `status: canon` n'a ete modifie sans ADR associee (G1 respecte)
5. Le canon architectural reste exclusivement dans `.spec/00-canon/` du monorepo (G1)
6. Aucun incident de securite ou de compromission de cle n'a ete detecte
7. Le kill-switch `AI_VAULT_WRITE=false` n'a pas eu besoin d'etre active (aucune violation de CI detectee)

**Date:** 2026-04-18

**Name:** Fafa

**Role:** Owner / Governance Lead

**Email:** automecanik.seo@gmail.com

**Signing Key:** K002 (ssh-ed25519, fingerprint voir [[key-registry]])

**Signature:** _______________ *(attestation actee par commit signe avec K002 de ce document)*

---

## Pack Integrity

- **Pack ID:** EP-20260418-governance-hardening
- **Generated:** 2026-04-18
- **Generator:** manual curation (scope meta-vault hors perimetre `evidence-pack.sh` qui cible l'Airlock)
- **Hash manifest:** `manifest.sha256` (calcule via `sha256sum *.md > manifest.sha256` apres finalisation)

## Verification d'Integrite

```bash
# Depuis le repertoire du pack
cd ledger/compliance/evidence-pack/2026/2026-04/EP-20260418-governance-hardening
sha256sum -c manifest.sha256
```

Resultat attendu: `OK` pour chacun des 9 fichiers canoniques.

## Voir aussi

- [[rules-governance-process]] — G6 (Proof Requirements), G8 (Obsolete Handling)
- [[MOC-Compliance]] — Index evidence-packs
