"""
config.py — Configuración central del pipeline ETL Northwind
Carga variables desde .env en la raíz del repositorio.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Raíz del repo: .../advanced-db-final-project/
_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")

# ── Conexiones (Supabase + MongoDB Atlas) ───────────────────────────────────
SOURCE_DATABASE_URL = os.getenv("SOURCE_DATABASE_URL", "")
STAGING_DATABASE_URL = os.getenv("STAGING_DATABASE_URL", "")
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "northwind_dw")

# ── Rutas de archivos (relativas al directorio northwind_etl/) ──────────────
ETL_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = "logs"
SQL_DIR = str(ETL_ROOT / "sql")
STAGING_DDL_FILE = str(ETL_ROOT / "sql" / "northwind_staging_supabase.sql")

# ── Control de ejecución ────────────────────────────────────────────────────
def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name, str(default)).lower()
    return val in ("1", "true", "yes", "on")


BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TRUNCATE_FIRST = _env_bool("TRUNCATE_FIRST", True)
VALIDATE_DATA = _env_bool("VALIDATE_DATA", True)

# ── Tablas fuente a extraer (orden por dependencias) ────────────────────────
SOURCE_TABLES = [
    "Categories",
    "Suppliers",
    "Shippers",
    "Customers",
    "Employees",
    "Region",
    "Territories",
    "EmployeeTerritories",
    "Products",
    "Orders",
    "Order Details",
]

# ── Mapeo tabla fuente → tabla staging (PostgreSQL: minúsculas) ─────────────
TABLE_MAP = {
    "Categories":          "stg_categories",
    "Suppliers":           "stg_suppliers",
    "Shippers":            "stg_shippers",
    "Customers":           "stg_customers",
    "Employees":           "stg_employees",
    "Region":              "stg_region",
    "Territories":         "stg_territories",
    "EmployeeTerritories": "stg_employee_territories",
    "Products":            "stg_products",
    "Orders":              "stg_orders",
    "Order Details":       "stg_order_details",
}
