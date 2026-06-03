"""
extract.py — Extracción de datos desde la base de datos fuente Northwind
"""

import pandas as pd
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

# SQL de extracción por tabla (proyección explícita de columnas necesarias)
EXTRACT_QUERIES = {
    "Categories": """
        SELECT
            CategoryID,
            CategoryName,
            Description
        FROM Categories
    """,

    "Suppliers": """
        SELECT
            SupplierID,
            CompanyName,
            ContactName,
            ContactTitle,
            Address,
            City,
            Region,
            PostalCode,
            Country,
            Phone,
            Fax
        FROM Suppliers
    """,

    "Shippers": """
        SELECT
            ShipperID,
            CompanyName,
            Phone
        FROM Shippers
    """,

    "Customers": """
        SELECT
            CustomerID,
            CompanyName,
            ContactName,
            ContactTitle,
            Address,
            City,
            Region,
            PostalCode,
            Country,
            Phone,
            Fax
        FROM Customers
    """,

    "Employees": """
        SELECT
            EmployeeID,
            LastName,
            FirstName,
            Title,
            TitleOfCourtesy,
            BirthDate,
            HireDate,
            City,
            Region,
            Country,
            ReportsTo
        FROM Employees
    """,

    "Products": """
        SELECT
            ProductID,
            ProductName,
            SupplierID,
            CategoryID,
            QuantityPerUnit,
            UnitPrice,
            UnitsInStock,
            UnitsOnOrder,
            ReorderLevel,
            Discontinued
        FROM Products
    """,

    "Orders": """
        SELECT
            OrderID,
            CustomerID,
            EmployeeID,
            OrderDate,
            RequiredDate,
            ShippedDate,
            ShipVia,
            Freight,
            ShipName,
            ShipAddress,
            ShipCity,
            ShipRegion,
            ShipPostalCode,
            ShipCountry
        FROM Orders
    """,

    "Order Details": """
        SELECT
            OrderID,
            ProductID,
            UnitPrice,
            Quantity,
            Discount
        FROM [Order Details]
    """,

    # ── Tablas territoriales — necesarias para P6 (Análisis de territorios) ──
    "Region": """
        SELECT
            RegionID,
            RTRIM(RegionDescription) AS RegionDescription
        FROM Region
    """,

    "Territories": """
        SELECT
            TerritoryID,
            RTRIM(TerritoryDescription) AS TerritoryDescription,
            RegionID
        FROM Territories
    """,

    "EmployeeTerritories": """
        SELECT
            EmployeeID,
            TerritoryID
        FROM EmployeeTerritories
    """,
}


def extract_table(engine, table_name: str) -> pd.DataFrame:
    """Extrae una tabla completa desde la fuente y retorna un DataFrame."""
    query = EXTRACT_QUERIES.get(table_name)
    if not query:
        raise ValueError(f"No hay query definida para la tabla: {table_name}")

    logger.info(f"  Extrayendo: {table_name}")
    with engine.connect() as conn:
        df = pd.read_sql(text(query.strip()), conn)

    logger.info(f"    → {len(df):,} registros extraídos")
    return df


def extract_all(engine, table_list: list) -> dict:
    """Extrae todas las tablas y devuelve un diccionario {tabla: DataFrame}."""
    raw_data = {}
    errors = []

    for table in table_list:
        try:
            raw_data[table] = extract_table(engine, table)
        except Exception as e:
            logger.error(f"  [ERROR] Extracción fallida en '{table}': {e}")
            errors.append(table)

    if errors:
        logger.warning(f"Tablas con error en extracción: {errors}")

    logger.info(f"Extracción completada: {len(raw_data)}/{len(table_list)} tablas")
    return raw_data, errors
