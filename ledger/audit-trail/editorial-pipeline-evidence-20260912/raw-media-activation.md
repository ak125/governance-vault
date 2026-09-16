# Candidat de raccordement RAW — préparation, aucune activation

État : la route admin texte et la route vidéo existantes délèguent au producteur
natif RAW. L'affectation des images/pages et les consommateurs vidéo restent inchangés.
Le reçu `RECEIVED / raw / to_verify / retrievable=false` confirme seulement la réception.
Une vidéo reçue n'apparaît pas automatiquement dans le catalogue vidéo RAG.

## Contrat du déploiement à préparer après revue des candidats

- Livrer le candidat RAW et ses schémas/scripts/manifests dans un checkout de
  réception dédié, accessible à l'identité de l'application, avec Git et LFS.
  Ne jamais pointer le client vers le checkout WIKI du timer ou un miroir RAG.
- `RAW_ACQUISITION_SCRIPT` : chemin absolu du `_scripts/auto-capture-runner.py`
  livré dans ce checkout, pas un chemin fourni par une requête.
- `RAW_GITLEAKS_BIN` : chemin absolu d'un binaire fourni par la chaîne de livraison.
  Le cache pre-commit utilisé en preuve n'est pas une installation de production.
- `RAW_FFPROBE_BIN` : chemin absolu du ffprobe livré pour la vidéo. L'exécution
  nécessite `unshare` avec user namespace et network namespace disponibles.
  Un environnement qui interdit ces namespaces échoue avant stockage vidéo.
- Python3, PyYAML, jsonschema, Git, `/usr/bin/timeout`, `unshare`, le scanner et
  ffprobe doivent être présents dans l'environnement EFFECTIF du backend.
  Les empreintes de la preuve VPS sont consignées dans raw-media-proof-dependencies.json ;
  elles ne prouvent pas leur présence dans le conteneur applicatif ni leur actualité sécurité.
- Le client transmet seulement PATH, LANG et les chemins du scanner/inspecteur.
  Il n'hérite pas des secrets de DB/GitHub de l'application. JSON passe par stdin.
- Limites : réseau 90s (DNS/en-têtes inclus), HTTPS public port443, robots et allowlist
  identiques à la capture HTML, 64MiB, MP4/MOV/WebM/Matroska, durée600s, surface2160p.
  Probe12s sans réseau, scanner15s, manifestes60s ; groupe de processus arrêté à220s,
  force après5s, garde externe Nest240s. Charge concurrente refusée par verrou non bloquant.
- Pas d'extraction ASR/OCR, de téléchargement de pages plateformes, d'extension
  d'allowlist ni de promotion implicite. La détection des secrets textuels ne
  certifie pas l'absence de PII dans les images/sons du média ; qualification ultérieure requise.

## Acceptation avant activation

Les preuves synthétiques passent sur l'hôte avec les composants réels explicités.
Restent : packaging reproductible dans le conteneur de déploiement, droits du checkout,
probe réseau refusé dans ce conteneur, URL vidéo fabricant réellement admissible,
retours HTTP authentifiés et compatibilité des éventuels clients externes.
Les tests de ces propriétés devront s'exécuter sur une instance isolée avant activation.
Aucune modification de service, cron, variables runtime ou corpus partagé dans ce lot.

Retour arrière applicatif : désactiver ces deux acquisitions si le producteur est
indisponible (503, sans fallback RAG). Conserver les reçus et sources RAW déjà écrits.
Un retour à l'ancien téléchargement RAG ne fait pas partie du retour arrière proposé.
