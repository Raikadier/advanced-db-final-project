"""Diagnóstico rápido de conexiones — no commitear si se modifica con secretos."""
from etl.config import SOURCE_DATABASE_URL, STAGING_DATABASE_URL, MONGO_URI, MONGO_DB, _REPO_ROOT
from etl.db_connection import get_source_engine, get_staging_engine, test_connection
from sqlalchemy import text

print("ENV root:", _REPO_ROOT)
print("SOURCE set:", bool(SOURCE_DATABASE_URL))
print("STAGING set:", bool(STAGING_DATABASE_URL))
print("MONGO set:", bool(MONGO_URI))
print("MONGO_DB:", MONGO_DB)

src = get_source_engine(SOURCE_DATABASE_URL)
print("OLTP:", "OK" if test_connection(src, "OLTP") else "FAIL")
with src.connect() as c:
    rows = c.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' ORDER BY table_name LIMIT 15"
        )
    ).fetchall()
    print("OLTP tablas (max 15):", [r[0] for r in rows] or "(ninguna)")

stg = get_staging_engine(STAGING_DATABASE_URL)
print("Staging:", "OK" if test_connection(stg, "Staging") else "FAIL")
with stg.connect() as c:
    rows = c.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' ORDER BY table_name"
        )
    ).fetchall()
    print("Staging tablas:", [r[0] for r in rows] or "(ninguna)")

try:
    from pymongo import MongoClient

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")
    db = client[MONGO_DB]
    cols = db.list_collection_names()
    print("Mongo ping: OK")
    print("Mongo collections:", cols or "(ninguna)")
    client.close()
except Exception as e:
    print("Mongo FAIL:", type(e).__name__, str(e)[:200])
