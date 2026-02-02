# Governance Policy - AutoMecanik

> **Source de verite** - Regles de gouvernance processus au 2026-01-07
> **Version**: 1.0.0 | **Status**: CANON
> **Complement de:** rules.md (R1-R7 = technique, R8+ = processus)

---

## R8: Canon-Only Policy

**OBLIGATOIRE:** Seuls les fichiers dans `.spec/00-canon/` font autorite.

| Source | Autorite |
|--------|----------|
| `.spec/00-canon/*` | CANON - Source de verite |
| `.spec/features/*` | Supplementaire - peut etre obsolete |
| `.spec/.archive/*` | Archive - NE JAMAIS REFERENCER |
| `_bmad-output/*` | Artefacts versionnes - read-only |

**Raison:** Prevenir la confusion documentaire et garantir une source de verite unique.

---

## R9: Proof Requirements (Anti-BS Rule)

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

## R10: RAG Corpus Alignment

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

## R11: Obsolete Handling

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

- [ ] Sources = canon uniquement (R8)
- [ ] Claims avec preuves (R9)
- [ ] RAG alignment verifie (R10)
- [ ] Obsolete archive (R11)

Apres chaque deliverable:

- [ ] sha256sum genere
- [ ] git status propre
- [ ] INDEX.md mis a jour si applicable

---

## References

- **rules.md** - R1-R7: Regles techniques code
- **architecture.md** - Architecture NestJS/Remix/Supabase
- **repo-map.md** - Structure monorepo

---

_Derniere mise a jour: 2026-01-07_
_Status: CANON - Complement de rules.md_
