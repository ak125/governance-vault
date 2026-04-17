# Rules - Governance Process (G5-G8)

> **Source de verite** - Regles de gouvernance processus au 2026-04-17
> **Version**: 2.0.0 | **Status**: CANON
> **Taxonomie**: G = Governance (G1-G4 = vault dans rules-vault.md, G5-G8 = processus ici)
> **Complement de:** rules-technical.md (T1-T7 = technique, G5+ = processus)

---

## G5: Canon-Only Policy

**OBLIGATOIRE:** Seuls les fichiers dans `.spec/00-canon/` font autorite.

| Source | Autorite |
|--------|----------|
| `.spec/00-canon/*` | CANON - Source de verite |
| `.spec/features/*` | Supplementaire - peut etre obsolete |
| `.spec/.archive/*` | Archive - NE JAMAIS REFERENCER |
| `_bmad-output/*` | Artefacts versionnes - read-only |

**Raison:** Prevenir la confusion documentaire et garantir une source de verite unique.

---

## G6: Proof Requirements (Anti-BS Rule)

**OBLIGATOIRE:** Chaque claim "fait" doit inclure preuves.

```bash
# Preuves requises pour tout deliverable
ls -lah <fichier>           # Existence + taille
sha256sum <fichier>         # Hash integrite
head -n 25 <fichier>        # Apercu contenu
git status --porcelain      # Etat git
```

| Claim | Preuve requise |
|-------|---------------|
| "Fichier cree" | ls -lah + sha256sum |
| "Contenu modifie" | git diff |
| "Migration appliquee" | psql query result |
| "Test passe" | curl output |

**Raison:** Eliminer les claims sans verification. "Trust but verify" → "Verify first".

---

## G7: RAG Corpus Alignment

**OBLIGATOIRE:** RAG corpus reference UNIQUEMENT documents valides.

| Regle | Valeur |
|-------|--------|
| PROD Namespace | `knowledge:faq` UNIQUEMENT |
| truth_level requis | L1 ou L2 obligatoire |
| RAG status | **OFF jusqu'a golden tests 100%** |
| Gating | Score < 0.70 = REFUSE |

**Kill Switches actifs:**
- `AI_PROD_WRITE=false` - Bloque ecriture IA en prod
- `NAMESPACE_GUARD=knowledge:faq` - Limite namespace PROD
- `MIN_SCORE_THRESHOLD=0.70` - Refuse reponses incertaines

**Raison:** Prevenir hallucinations et reponses hors-sujet du RAG.

---

## G8: Obsolete Handling

**OBLIGATOIRE:** Documents obsoletes doivent etre explicitement archives.

```
Document identifie comme obsolete
      ↓
Deplacement vers .spec/.archive/
      ↓
Entry dans deprecation_ledger.md
      ↓
Retrait de tout INDEX
      ↓
Exclusion du corpus RAG
```

| Action | Commandes |
|--------|-----------|
| Archiver | `mv .spec/features/xxx.md .spec/.archive/` |
| Logger | Ajouter entry dans `deprecation_ledger.md` |
| Verifier | `grep -r "xxx.md" .spec/` doit retourner 0 resultats |

**Raison:** Prevenir l'empoisonnement du contexte par documents perimes.

---

## Checklist Governance

Avant tout workflow BMAD:

- [ ] Sources = canon uniquement (G5)
- [ ] Claims avec preuves (G6)
- [ ] RAG alignment verifie (G7)
- [ ] Obsolete archive (G8)

Apres chaque deliverable:

- [ ] sha256sum genere
- [ ] git status propre
- [ ] INDEX.md mis a jour si applicable

---

## References

- **rules-technical.md** - T1-T7: Regles techniques code
- **rules-ai-cos.md** - AI1-AI10: Regles d'or agents IA
- **rules-vault.md** - G1-G4: Regles de gouvernance du vault
- **architecture.md** - Architecture NestJS/Remix/Supabase
- **repo-map.md** - Structure monorepo

---

_Derniere mise a jour: 2026-04-17_
_Status: CANON - Complement de rules-technical.md_
