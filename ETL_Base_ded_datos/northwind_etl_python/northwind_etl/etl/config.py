"""
config.py — Configuración central del pipeline ETL Northwind → Staging
Proyecto BI - Base de Datos Avanzadas
"""

# ── Conexión fuente (Northwind) ─────────────────────────────────────────────
# Ajustar según el motor que use el equipo
SOURCE_CONFIG = {
    "engine":   "mssql_localdb",
    "database": "Northwind",
    "driver":   "ODBC Driver 17 for SQL Server",
    "pipe":     r"np:\\.\pipe\LOCALDB#F3EE2E3A\tsql\query",
}

# ── Conexión destino (Staging) ──────────────────────────────────────────────
STAGING_CONFIG = {
    "engine":   "mssql_localdb",
    "database": "northwind_staging",
    "driver":   "ODBC Driver 17 for SQL Server",
    "pipe":     r"np:\\.\pipe\LOCALDB#F3EE2E3A\tsql\query",
}

# ── Rutas de archivos ───────────────────────────────────────────────────────
LOG_DIR   = "logs"
SQL_DIR   = "sql"
DOCS_DIR  = "docs"

# ── Control de ejecución ────────────────────────────────────────────────────
BATCH_SIZE     = 500          # filas por batch en inserciones
LOG_LEVEL      = "INFO"       # DEBUG | INFO | WARNING | ERROR
TRUNCATE_FIRST = True         # Truncar staging antes de cada carga
VALIDATE_DATA  = True         # Ejecutar validaciones de calidad

# ── Tablas fuente a extraer (en orden por dependencias FK) ─────────────────
SOURCE_TABLES = [
    "Categories",
    "Suppliers",
    "Shippers",
    "Customers",
    "Employees",
    "Region",               # debe ir antes de Territories (FK)
    "Territories",          # debe ir antes de EmployeeTerritories (FK)
    "EmployeeTerritories",  # necesita Employees + Territories ya cargadas
    "Products",
    "Orders",
    "Order Details",
]

# ── Mapeo tabla fuente → tabla staging ─────────────────────────────────────
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
