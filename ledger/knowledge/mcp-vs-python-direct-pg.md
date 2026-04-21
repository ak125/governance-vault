---
type: knowledge
scope: backend/db
date: 2026-04-21
owner: Fafa
pr: https://github.com/ak125/nestjs-remix-monorepo/pull/88
tags: [db, supabase, mcp, postgres, python, psycopg2, rule-candidate]
---

# MCP vs Python direct PG — quand utiliser quoi

> **Règle candidate canon issue d'un incident opérationnel.**
> **PR** : #88 nestjs-remix-monorepo — commit `5564f1e5`
> **Incident** : ADR-017 Phase 1, CREATE INDEX CONCURRENTLY bloqué par MCP

---

## TL;DR

**MCP Supabase** (`apply_migration`, `execute_sql`) est l'outil par défaut pour toute DDL/DML courte.
**Python + psycopg2 direct** (port 5432, non poolé) est **obligatoire** pour 3 classes d'opérations :

1. `CREATE INDEX CONCURRENTLY`
2. Toute query > 60 secondes (reindex, maintenance, bulk migration)
3. Tout usage nécessitant une session autocommit sans transaction implicite

---

## Les 2 limitations MCP rencontrées

### 1. `apply_migration` wrappe en `BEGIN...COMMIT`

```
ERROR: CREATE INDEX CONCURRENTLY cannot run inside a transaction block
```

PostgreSQL l'interdit. MCP `apply_migration` **enveloppe automatiquement** toute requête dans une transaction pour garantir l'atomicité.

**Conséquence** : impossible d'exécuter `CREATE INDEX CONCURRENTLY`, `VACUUM`, `REINDEX CONCURRENTLY`, `CLUSTER`, ou tout ordre qui s'oppose à une transaction.

### 2. `execute_sql` passe par le pooler (statement_timeout 60s)

Supabase expose 2 endpoints Postgres :

| Endpoint | Port | `statement_timeout` | Usage |
|---|---|---|---|
| **Pooler Supavisor** | 6543 | 60s (hardcodé) | Connexions courtes, app runtime |
| **Direct** | 5432 | 1min par défaut (surchargeable) | Admin, migrations lourdes |

MCP `execute_sql` utilise le pooler. Au bout de 60s la requête est tuée côté serveur, même si le client attend.

**Conséquence** : impossible d'exécuter une migration lourde (ex: `CREATE INDEX` non-concurrent sur 47 GB, backfill en boucle, refresh matview > 1min).

---

## La solution : Python direct via `psycopg2`

Connexion **directe** (port 5432, **pas** pooler 6543) avec `autocommit=True` et `SET statement_timeout = 0`.

### Extrait canonique

```python
import os, psycopg2
from dotenv import load_dotenv

load_dotenv("backend/.env")
DB_PASSWORD = os.environ["SUPABASE_DB_PASSWORD"]
PROJECT_REF = "cxpojprgwgubzjyqzmoq"

conn = psycopg2.connect(
    host=f"db.{PROJECT_REF}.supabase.co",
    port=5432,                 # DIRECT — PAS 6543 pooler
    dbname="postgres",
    user="postgres",
    password=DB_PASSWORD,
    sslmode="require",
    application_name="my-migration-tool",
)
conn.autocommit = True         # REQUIS pour CONCURRENTLY

with conn.cursor() as cur:
    # Désactive les timeouts au niveau session
    cur.execute("SET statement_timeout = 0")
    cur.execute("SET lock_timeout = 0")
    cur.execute("SET idle_in_transaction_session_timeout = 0")

    # Exécute l'opération longue
    cur.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_foo_bar
          ON public.foo (bar_id, created_at)
    """)
```

### Exemple réel

`scripts/db/adr017-create-index-concurrently.py` (PR #88) :

- Index `idx_prt_pg_id_type_id` sur `pieces_relation_type` (47 GB, 368 M lignes)
- Build en **13 min 24 s** (804 s), zero lock, prod non impactée
- Supervision : `pg_stat_progress_create_index` depuis une 2e connexion (MCP OK pour la lecture courte)

---

## Quand utiliser quoi

| Opération | MCP apply_migration | MCP execute_sql | Python direct |
|---|:---:|:---:|:---:|
| `CREATE TABLE`, `ALTER TABLE`, fonctions courtes | ✅ | | |
| `INSERT/UPDATE/DELETE` < 60 s | ✅ | ✅ | |
| Query read-only monitoring | | ✅ | |
| `CREATE INDEX CONCURRENTLY` | ❌ | ❌ | ✅ |
| `REINDEX CONCURRENTLY` | ❌ | ❌ | ✅ |
| `VACUUM`, `VACUUM FULL`, `CLUSTER` | ❌ | ❌ | ✅ |
| Migration > 60 s (refresh matview, backfill) | ❌ | ❌ | ✅ |
| Supervision long-running (parallèle) | | ✅ | ✅ |

---

## Check-list avant d'écrire un script Python direct

- [ ] Opération vraiment incompatible MCP ? (sinon, rester sur MCP)
- [ ] `SUPABASE_DB_PASSWORD` présent dans `backend/.env` ?
- [ ] Port **5432** (direct) — **pas** 6543 (pooler)
- [ ] `conn.autocommit = True` pour DDL `CONCURRENTLY`
- [ ] `SET statement_timeout = 0` explicite (Supabase impose 1min par défaut)
- [ ] `IF NOT EXISTS` ou `OR REPLACE` pour idempotence
- [ ] Supervision prévue via 2e connexion (ex: `pg_stat_progress_create_index`)
- [ ] `application_name` explicite pour tracer dans `pg_stat_activity`
- [ ] Rollback documenté (ex: `DROP INDEX CONCURRENTLY`)

---

## Risques et garde-fous

1. **Connexion directe = pas de pool sharing.** Une session laissée ouverte retient une connexion au max. Toujours `conn.close()` explicite.
2. **`statement_timeout = 0` = aucune protection.** Une query mal construite tourne indéfiniment. N'activer **que pour l'opération ciblée**, pas en global.
3. **IO prod soutenu pendant CONCURRENTLY.** Construire hors pic si possible. Vérifier que les backups nightly ne chevauchent pas.
4. **`SUPABASE_DB_PASSWORD` sensible.** Ne jamais committer, toujours via `.env` + `dotenv`. Ne jamais logger le DSN complet.

---

## Références

- PR : #88 nestjs-remix-monorepo (ADR-017 Phase 1, fix top 1 CPU consumer)
- Script canon : `scripts/db/adr017-create-index-concurrently.py`
- Related decision : [[ADR-017-rpc-pieces-cast-cleanup]]
- Related incident : [[2026-04-20-gsc-5xx-vehicle-page-cold-rpc]]
- Supabase docs : https://supabase.com/docs/guides/database/connecting-to-postgres
- PostgreSQL docs : https://www.postgresql.org/docs/current/sql-createindex.html (§ CONCURRENTLY restrictions)

---

*Pattern capturé le 2026-04-21, à promouvoir en règle canon après 2 usages confirmés réussis.*
