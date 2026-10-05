---
id: INC-2026-017
date: 2026-08-14
severity: critical
status: investigating
impact_duration: "2025-11-12 → en cours (rotation partielle 2026-08-14)"
affected_systems: [monorepo-public-repo, backend-session-auth, systempay-prod, systempay-test, supabase-massdoc]
root_cause: "Un fichier d'environnement de production committé sous une identité de template de test (backend/.env.test.template), donc invisible aux contrôles ciblant les .env"
related_rules: ["G1", "G3"]
related_adr: []
owner: "@ak125"
reviewed_by: ""
---

# Incident: secrets de production publiés via un faux template de test

> **Cet incident RÉTRACTE une conclusion antérieure.** L'audit SEC-03 (2026-08-13) avait
> conclu « aucun secret exposé n'est encore en service ». **Ce verdict est FAUX et retiré.**
> Voir §Rétractation.

## Résumé

`backend/.env.test.template` est **tracké au HEAD** du dépôt **public**
`ak125/nestjs-remix-monorepo`. Malgré son nom, ce n'est pas un gabarit : c'est une **copie d'un
environnement réel**, valeurs comprises.

Quatre de ces secrets étaient, au 2026-08-14, **identiques au runtime vivant** :

| secret | statut au 2026-08-14 |
|---|---|
| `SESSION_SECRET` | VIVANT → tourné sur DEV le jour même ; PROD/PREPROD à vérifier |
| `SYSTEMPAY_HMAC_KEY_PROD` | VIVANT → rotation Back Office requise |
| `SYSTEMPAY_HMAC_KEY_TEST` | VIVANT → rotation requise |
| `SYSTEMPAY_CERTIFICATE_PROD` | VIVANT → renouvellement requis |
| `PAYBOX_HMAC_KEY` | différent du runtime — `EXPOSED / NOT_CURRENT / REVOCATION_TO_PROVE` |
| `RESEND_API_KEY` | aucune contrepartie runtime → **indéterminé**, à prouver |
| `SUPABASE_SERVICE_ROLE_KEY` | RÉVOQUÉ — voir §Famille JWT legacy |

Le fichier porte en outre en clair, non masqués parce que numériques :
`SYSTEMPAY_SITE_ID`, `SYSTEMPAY_CERTIFICATE_PROD`, `SYSTEMPAY_MODE=PRODUCTION`.

**Aucune valeur de secret n'apparaît dans ce document.** Les constats reposent sur des
comparaisons d'empreintes SHA-256, jamais sur l'affichage des valeurs.

## Rétractation du verdict SEC-03

```
SEC-03, verdict du 2026-08-13
  « aucun secret exposé n'est encore en service »
        ↓
  RETRACTED le 2026-08-14
```

**Cause de l'erreur : périmètre de scan incomplet.** SEC-03 examinait les fichiers `.env`
présents dans l'**historique** git. Le fichier en cause est au **HEAD**, et son nom
(`.env.test.template`) ne correspond ni au motif `.env` recherché, ni à ce que son identité
promet. Il a donc été classé comme gabarit inoffensif.

**Corollaire à ne pas perdre** : SEC-03 notait que `SYSTEMPAY_HMAC_KEY_PROD` « n'a pas de
contrepartie courante », et en déduisait qu'aucune inférence de révocation ne s'y appliquait.
La contrepartie existe et elle est **identique**. Cette clé n'est pas non-inférable : elle est
compromise.

Sans cette rétractation, un audit ultérieur retrouverait le verdict SEC-03 et **innocenterait à
tort les secrets PSP**.

## Cause racine

Le défaut n'est pas « un secret committé ». C'est :

> **un fichier de production copié sous une identité de template de test.**

C'est ce qui explique que les contrôles précédents l'aient mal classé — humains comme
automatiques. Un `*.template` est présumé porter des placeholders ; celui-ci portait des
credentials. La preuve de provenance est locale et non publiée :
`backend/.env.production` (untracked, couvert par `.gitignore:64`) porte **les mêmes valeurs**
pour `SESSION_SECRET`, les trois variables SystemPay et `SUPABASE_SERVICE_ROLE_KEY`.

## Timeline

| Date | Événement |
|------|-----------|
| 2025-11-12 | `cf5fd8953` — introduction de literals `service_role` dans `backend/scripts/*.js` |
| 2026-08-13 | Audit SEC-03 — conclut à tort « aucun secret encore en service » |
| 2026-08-14 | Découverte incidente pendant un inventaire d'ownership : 6 fichiers portent un JWT `service_role` |
| 2026-08-14 | Élargissement du scan → 8 fichiers, dont `backend/.env.test.template` |
| 2026-08-14 | Comparaison par empreinte : 4 secrets identiques au runtime vivant |
| 2026-08-14 | Preuve control-plane : famille JWT legacy massdoc désactivée |
| 2026-08-14 | **Rotation `SESSION_SECRET` sur DEV**, process recréé, `/health` 200 |
| — | PROD / PREPROD / SystemPay / Resend / Paybox : ouverts |

## Famille JWT legacy Supabase — révocation prouvée

```
GET /v1/projects/cxpojprgwgubzjyqzmoq/api-keys/legacy
{"enabled":false}      HTTP 200
```

Lecture **control-plane**, obtenue sans jamais présenter la clé exposée au projet. La famille
JWT legacy (`anon` + `service_role`) est désactivée sur `massdoc`. Le `service_role` publié
n'ouvre donc plus d'accès, RLS compris.

Méthode retenue et à rejouer : le discriminant est l'endpoint de management, **jamais un appel
authentifié avec la clé compromise**.

## Rotation effectuée — SESSION_SECRET, DEV uniquement

Preuve structurelle, sans exposition de valeur :

```
backend/.env modifié     2026-08-14 18:02:59
process 1114450 démarré  2026-08-14 18:04:16     ← postérieur
/health                  HTTP 200
empreinte publiée        absente du runtime
```

Le contrôle porte sur l'**existence** de l'ancienne configuration et sur la **recréation** du
process, jamais sur l'affichage d'une valeur. Aucun `env`, aucun `/proc/*/environ`, aucun
`docker inspect` exploratoire.

Conséquence acceptée : invalidation de toutes les sessions DEV. Aucun maintien ancien+nouveau en
parallèle — cela prolongerait volontairement la validité du secret compromis.

## Chaîne PROD — ce qu'il reste à faire

```
~/production/.env
   ├── SESSION_SECRET
   ├── SYSTEMPAY_HMAC_KEY_PROD
   ├── SYSTEMPAY_HMAC_KEY_TEST
   └── SYSTEMPAY_CERTIFICATE_PROD
          ↓  env_file
docker-compose.prod.yml
          ↓
nestjs-remix-monorepo-prod
```

Le workflow de déploiement PROD substitue explicitement les clés Supabase et `JWT_SECRET` depuis
des secrets GitHub, **mais pas ces quatre valeurs**. Elles proviennent donc du `.env` persistant
du runner. Conséquence directe : **si `~/production/.env` porte encore les valeurs publiées, un
redéploiement les réinjecte.** La rotation doit modifier ce fichier, pas seulement le container.

### Sonde de contrôle — hash-only, lecture seule

Sortie acceptable : `COMPROMISED_MATCH` ou `DIFFERENT`. Aucune valeur, aucune empreinte runtime.

```
empreinte SHA-256 du SESSION_SECRET publié :
9553b86a04fca15cb30cddfb51a8d1f9b47664443fce28b99a55955ba6559dd4
```

### Interdits pendant la vérification

- **Ne pas** utiliser `workflow_dispatch` de `deploy-prod.yml` comme sonde : ce workflow n'est
  pas read-only, il retague `:production` et redéploie.
- **Ne pas** modifier `backend/.env.production` sur DEV : il ne pilote pas PROD et constitue
  désormais une **preuve de provenance**.
- **Ne jamais** présenter une clé compromise au prestataire « pour voir si elle marche ».

## Séquence restante

```
P0-1  SESSION_SECRET   DEV      CLOSED
                       PREPROD  secret GitHub distinct — à vérifier
                       PROD     à vérifier (sonde hash-only) puis tourner
P0-2  SystemPay PROD            Back Office marchand → ~/production/.env → recréation container
P0-3  SystemPay TEST            après PROD
P0-4  RESEND                    prouver l'état côté fournisseur, sinon rotation
P0-5  Paybox                    prouver la révocation de l'ancienne valeur
P1    nettoyer le HEAD          placeholders CHANGE_ME, jamais de credential dans un .template
P1    scan historique + baseline de secrets révoqués + fingerprints exacts
```

L'ordre est non négociable sur un point : **la rotation précède le nettoyage**. Supprimer le
fichier d'abord retirerait la preuve sans fermer l'accès.

## Ce que cet incident change pour la dette Gitleaks

Les 394 findings historiques ne peuvent plus être traités comme une dette homogène : au moins une
famille correspond à des secrets **vivants**, pas historiques. Le triage doit être ordonné par
**type de secret × système × statut de révocation**, jamais par volume.

## Prévention

- Aucun credential réel dans un fichier `*.template` — placeholders explicites uniquement.
- Un contrôle de secrets ne doit pas cibler un **nom de fichier** (`.env`) mais un **contenu**.
  C'est précisément l'écart qui a rendu SEC-03 aveugle.
- Le modèle de preuve reste celui de SEC-01 : baseline de secrets révoqués + fingerprints
  commit-spécifiques, **jamais d'allowlist par valeur**.
