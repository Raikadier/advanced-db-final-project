"""
bootstrap.py — Asegura que el esquema staging exista antes de cargar datos
"""

import logging
import re
from pathlib import Path

from sqlalchemy import text

logger = logging.getLogger(__name__)


def staging_schema_exists(engine) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'stg_orders'
                """
            )
        ).fetchone()
    return row is not None


def _split_sql_statements(sql: str) -> list[str]:
    """Divide un script DDL en sentencias individuales (sin datos INSERT)."""
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    parts = []
    current = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(current).strip()
            if stmt and stmt != ";":
                parts.append(stmt.rstrip(";").strip())
            current = []
    if current:
        tail = "\n".join(current).strip()
        if tail:
            parts.append(tail.rstrip(";").strip())
    return parts


def ensure_staging_schema(engine, ddl_path: str) -> None:
    """
    Crea tablas stg_* y etl_runs si no existen.
    Idempotente: no borra ni recrea en cada ejecución.
    """
    if staging_schema_exists(engine):
        logger.info("Esquema staging ya existe — bootstrap omitido.")
        return

    path = Path(ddl_path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró DDL staging: {ddl_path}")

    logger.info("Esquema staging no detectado — aplicando %s", path.name)
    sql = path.read_text(encoding="utf-8")
    statements = _split_sql_statements(sql)

    with engine.begin() as conn:
        for stmt in statements:
            upper = stmt.upper()
            if upper.startswith("SET "):
                conn.execute(text(stmt))
                continue
            if upper.startswith("SELECT ") and "INFORMATION_SCHEMA" in upper:
                continue
            conn.execute(text(stmt))

    logger.info("Bootstrap staging completado (stg_* + etl_runs).")
