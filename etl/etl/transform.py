"""
transform.py — Limpieza, validación y transformaciones de negocio
Northwind → Staging Area

Transformaciones implementadas:
    TR-001  Normalización de texto (UPPER + TRIM)
    TR-002  Cast MONEY → DECIMAL(18,2)
    TR-003  Cast DATETIME → DATE (solo parte fecha)
    TR-004  Cast BIT → int (Discontinued)
    TR-005  Cast REAL → DECIMAL(5,2) (Discount)
    TR-006  Cálculo valor neto de venta (columna derivada)
    TR-007  Cálculo días de entrega (columna derivada)
    TR-008  Indicador de puntualidad (columna derivada)
    TR-009  Indicador bajo reorden (columna derivada)
    TR-010  Stock proyectado (columna derivada)
    TR-013  Concatenación nombre completo empleado
    TR-014  Filtro informativo Discontinued (flag, no elimina)
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


# ── Utilidades ─────────────────────────────────────────────────────────────

def _clean_str(series: pd.Series) -> pd.Series:
    """TR-001: UPPER + TRIM para campos de texto."""
    return series.astype(str).str.strip().str.upper().replace("NAN", pd.NA)


def _to_decimal(series: pd.Series, decimals: int = 2) -> pd.Series:
    """TR-002/005: Convierte a float redondeado."""
    return pd.to_numeric(series, errors="coerce").round(decimals)


def _to_date(series: pd.Series) -> pd.Series:
    """TR-003: Convierte DATETIME a solo fecha (date)."""
    return pd.to_datetime(series, errors="coerce").dt.normalize()


# ── Transformaciones por tabla ──────────────────────────────────────────────

def transform_categories(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["CategoryName"] = _clean_str(out["CategoryName"])   # TR-001
    out["Description"]  = out["Description"].astype(str).str.strip()
    logger.debug(f"  Categories transformado: {len(out)} filas")
    return out


def transform_suppliers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["CompanyName", "Country", "City", "ContactName"]:
        if col in out.columns:
            out[col] = _clean_str(out[col])                 # TR-001
    logger.debug(f"  Suppliers transformado: {len(out)} filas")
    return out


def transform_shippers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["CompanyName"] = _clean_str(out["CompanyName"])     # TR-001
    logger.debug(f"  Shippers transformado: {len(out)} filas")
    return out


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["CustomerID", "CompanyName", "Country", "City"]:
        if col in out.columns:
            out[col] = _clean_str(out[col])                 # TR-001
    logger.debug(f"  Customers transformado: {len(out)} filas")
    return out


def transform_employees(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["FirstName", "LastName", "Title", "Country", "City"]:
        if col in out.columns:
            out[col] = _clean_str(out[col])                 # TR-001
    # TR-013: nombre completo para etiquetas de visualización
    out["FullName"] = (
        out["LastName"].fillna("") + ", " + out["FirstName"].fillna("")
    ).str.upper()
    # TR-003: fechas a solo date
    out["BirthDate"] = _to_date(out["BirthDate"])
    out["HireDate"]  = _to_date(out["HireDate"])
    logger.debug(f"  Employees transformado: {len(out)} filas")
    return out


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ProductName"] = _clean_str(out["ProductName"])     # TR-001
    out["UnitPrice"]   = _to_decimal(out["UnitPrice"], 2)   # TR-002
    out["Discontinued"] = out["Discontinued"].astype(int)   # TR-004
    # TR-009: indicador bajo reorden
    out["STG_AlertaBajoReorden"] = np.where(
        (out["UnitsInStock"] < out["ReorderLevel"]) & (out["Discontinued"] == 0),
        "ALERTA", "OK"
    )
    # TR-010: stock proyectado
    out["STG_StockProyectado"] = (
        out["UnitsInStock"].fillna(0) + out["UnitsOnOrder"].fillna(0)
    ).astype(int)
    logger.debug(f"  Products transformado: {len(out)} filas")
    return out


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # TR-003: fechas a solo date
    out["OrderDate"]    = _to_date(out["OrderDate"])
    out["RequiredDate"] = _to_date(out["RequiredDate"])
    out["ShippedDate"]  = _to_date(out["ShippedDate"])
    # TR-002: flete a decimal
    out["Freight"] = _to_decimal(out["Freight"], 2)
    # TR-001: campos texto
    for col in ["ShipCountry", "ShipCity", "ShipName"]:
        if col in out.columns:
            out[col] = _clean_str(out[col])
    # TR-007: días de entrega (solo donde ShippedDate no es NULL)
    # FIX: usar None en lugar de pd.NA y castear a Int32Dtype() nullable
    # para evitar type mismatch al insertar en SQL Server columna INT
    mask_shipped = out["ShippedDate"].notna()
    out["STG_DiasEntrega"] = None
    out.loc[mask_shipped, "STG_DiasEntrega"] = (
        (out.loc[mask_shipped, "ShippedDate"] - out.loc[mask_shipped, "OrderDate"])
        .dt.days
    )
    out["STG_DiasEntrega"] = out["STG_DiasEntrega"].astype(pd.Int32Dtype())

    # TR-008: indicador de puntualidad (1=puntual, 0=tarde, NULL=no enviado)
    # FIX: usar None en lugar de pd.NA y castear a Int8Dtype() nullable
    # para evitar type mismatch al insertar en SQL Server columna BIT/TINYINT
    mask_both = mask_shipped & out["RequiredDate"].notna()
    out["STG_EntregaPuntual"] = None
    out.loc[mask_both, "STG_EntregaPuntual"] = np.where(
        out.loc[mask_both, "ShippedDate"] <= out.loc[mask_both, "RequiredDate"],
        1, 0
    )
    out["STG_EntregaPuntual"] = out["STG_EntregaPuntual"].astype(pd.Int8Dtype())
    logger.debug(f"  Orders transformado: {len(out)} filas")
    return out


def transform_order_details(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["UnitPrice"] = _to_decimal(out["UnitPrice"], 2)     # TR-002
    out["Discount"]  = _to_decimal(out["Discount"], 2)      # TR-005
    # Validación de rango descuento
    invalid_disc = (out["Discount"] < 0) | (out["Discount"] > 1)
    if invalid_disc.any():
        n = invalid_disc.sum()
        logger.warning(f"  [CALIDAD] {n} registros con Discount fuera de [0,1] — forzando a 0")
        out.loc[invalid_disc, "Discount"] = 0.0
    # TR-006: valor neto de venta
    out["STG_ValorNeto"] = (
        out["UnitPrice"] * out["Quantity"] * (1 - out["Discount"])
    ).round(2)
    logger.debug(f"  Order Details transformado: {len(out)} filas")
    return out


# ── Dispatcher ─────────────────────────────────────────────────────────────

_TRANSFORMERS = {
    "Categories":    transform_categories,
    "Suppliers":     transform_suppliers,
    "Shippers":      transform_shippers,
    "Customers":     transform_customers,
    "Employees":     transform_employees,
    "Products":      transform_products,
    "Orders":        transform_orders,
    "Order Details": transform_order_details,
}


def transform_all(raw_data: dict) -> dict:
    """Aplica todas las transformaciones y retorna {tabla: DataFrame limpio}."""
    clean_data = {}
    for table, df in raw_data.items():
        fn = _TRANSFORMERS.get(table)
        if fn:
            logger.info(f"  Transformando: {table}")
            clean_data[table] = fn(df)
        else:
            logger.warning(f"  Sin transformador para '{table}' — pasando sin cambios")
            clean_data[table] = df.copy()
    logger.info(f"Transformación completada: {len(clean_data)} tablas")
    return clean_data
