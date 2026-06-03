"""
load.py — Carga de datos transformados a la Staging Area
"""

import pandas as pd
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Mapeo tabla fuente → nombre tabla staging
TABLE_MAP = {
    "Categories":          "STG_CATEGORIES",
    "Suppliers":           "STG_SUPPLIERS",
    "Shippers":            "STG_SHIPPERS",
    "Customers":           "STG_CUSTOMERS",
    "Employees":           "STG_EMPLOYEES",
    "Region":              "STG_REGION",
    "Territories":         "STG_TERRITORIES",
    "EmployeeTerritories": "STG_EMPLOYEE_TERRITORIES",
    "Products":            "STG_PRODUCTS",
    "Orders":              "STG_ORDERS",
    "Order Details":       "STG_ORDER_DETAILS",
}


def truncate_staging(engine, table_name: str):
    # FIX: TRUNCATE TABLE es O(1) y no genera log por fila, a diferencia de DELETE
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_name}"))
    logger.debug(f"  Truncated {table_name}")


def load_table(
    engine,
    source_name: str,
    df: pd.DataFrame,
    batch_size: int = 500,
    truncate: bool = True,
) -> int:
    stg_table = TABLE_MAP.get(source_name)
    if not stg_table:
        raise ValueError(f"Sin mapeo staging para: {source_name}")

    if truncate:
        truncate_staging(engine, stg_table)

    # Añadir metadatos de carga
    df = df.copy()
    df["STG_LOAD_DATE"]   = pd.Timestamp.now().normalize()
    df["STG_SOURCE_NAME"] = "Northwind"
    df["STG_BATCH_ID"]    = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")

    total = 0
    for start in range(0, len(df), batch_size):
        chunk = df.iloc[start : start + batch_size]
        chunk.to_sql(
            name=stg_table.lower(),
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
        )
        total += len(chunk)
        logger.debug(f"    Cargados {total}/{len(df)} → {stg_table}")

    logger.info(f"  ✅ {source_name} → {stg_table}: {total:,} registros")
    return total


def load_all(
    engine,
    clean_data: dict,
    table_order: list,
    batch_size: int = 500,
    truncate: bool = True,
) -> dict:
    """Carga todas las tablas en el orden definido (respetando FKs)."""
    summary = {}
    errors  = []

    for table in table_order:
        df = clean_data.get(table)
        if df is None:
            logger.warning(f"  Sin datos para cargar: {table}")
            continue
        try:
            logger.info(f"  Cargando: {table} ({len(df):,} filas)")
            n = load_table(engine, table, df, batch_size, truncate)
            summary[table] = n
        except Exception as e:
            logger.error(f"  [ERROR] Carga fallida en '{table}': {e}")
            errors.append(table)
            summary[table] = 0

    total = sum(summary.values())
    logger.info(
        f"Carga completada: {len(summary) - len(errors)} tablas OK | "
        f"{total:,} registros totales"
    )
    if errors:
        logger.error(f"Tablas con error en carga: {errors}")

    return summary, errors
