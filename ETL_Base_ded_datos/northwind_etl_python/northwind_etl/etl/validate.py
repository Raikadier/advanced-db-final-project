"""
validate.py — Validaciones de calidad de datos antes de la carga al staging
Implementa las reglas de la sección Reglas_Calidad del Diccionario de Datos
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def _log_issue(table, field, rule, count, severity="ALTA"):
    icon = "🔴" if severity == "ALTA" else "🟡"
    logger.warning(f"  {icon} [{severity}] {table}.{field} | {rule} | {count} registros afectados")


def validate_order_details(df: pd.DataFrame) -> int:
    issues = 0
    # RQ-001: Discount en [0, 1]
    bad = ((df["Discount"] < 0) | (df["Discount"] > 1)).sum()
    if bad:
        _log_issue("Order Details", "Discount", "Fuera de rango [0,1]", bad)
        issues += bad
    # RQ-002: Quantity > 0
    bad = (df["Quantity"] <= 0).sum()
    if bad:
        _log_issue("Order Details", "Quantity", "Debe ser > 0", bad)
        issues += bad
    # RQ-003: UnitPrice >= 0
    bad = (df["UnitPrice"] < 0).sum()
    if bad:
        _log_issue("Order Details", "UnitPrice", "Debe ser >= 0", bad)
        issues += bad
    return issues


def validate_orders(df: pd.DataFrame) -> int:
    issues = 0
    # RQ-004: ShippedDate >= OrderDate
    mask = df["ShippedDate"].notna() & df["OrderDate"].notna()
    bad = (df.loc[mask, "ShippedDate"] < df.loc[mask, "OrderDate"]).sum()
    if bad:
        _log_issue("Orders", "ShippedDate", "ShippedDate < OrderDate", bad)
        issues += bad
    # RQ-005: RequiredDate >= OrderDate
    mask = df["RequiredDate"].notna() & df["OrderDate"].notna()
    bad = (df.loc[mask, "RequiredDate"] < df.loc[mask, "OrderDate"]).sum()
    if bad:
        _log_issue("Orders", "RequiredDate", "RequiredDate < OrderDate", bad, "MEDIA")
        issues += bad
    # RQ-006: OrderDate NOT NULL
    bad = df["OrderDate"].isna().sum()
    if bad:
        _log_issue("Orders", "OrderDate", "OrderDate es NULL", bad)
        issues += bad
    return issues


def validate_products(df: pd.DataFrame) -> int:
    issues = 0
    # RQ-007: UnitsInStock >= 0
    bad = (df["UnitsInStock"] < 0).sum()
    if bad:
        _log_issue("Products", "UnitsInStock", "Valor negativo", bad)
        issues += bad
    # RQ-009: UnitPrice >= 0
    bad = (df["UnitPrice"] < 0).sum()
    if bad:
        _log_issue("Products", "UnitPrice", "Precio negativo", bad)
        issues += bad
    # RQ-010: Discontinued en {0, 1}
    bad = (~df["Discontinued"].isin([0, 1])).sum()
    if bad:
        _log_issue("Products", "Discontinued", "Valor fuera de dominio {0,1}", bad)
        issues += bad
    return issues


def validate_customers(df: pd.DataFrame) -> int:
    issues = 0
    # RQ-015: CustomerID 5 chars y único
    bad_len = (df["CustomerID"].str.len() != 5).sum()
    if bad_len:
        _log_issue("Customers", "CustomerID", "Longitud diferente a 5 chars", bad_len)
        issues += bad_len
    dups = df["CustomerID"].duplicated().sum()
    if dups:
        _log_issue("Customers", "CustomerID", "Valores duplicados (violación PK)", dups)
        issues += dups
    return issues


_VALIDATORS = {
    "Order Details": validate_order_details,
    "Orders":        validate_orders,
    "Products":      validate_products,
    "Customers":     validate_customers,
}


def validate_all(clean_data: dict) -> dict:
    """Ejecuta todas las validaciones. Retorna {tabla: n_issues}."""
    report = {}
    total_issues = 0
    for table, df in clean_data.items():
        fn = _VALIDATORS.get(table)
        if fn:
            logger.info(f"  Validando: {table}")
            n = fn(df)
            report[table] = n
            total_issues += n
    if total_issues == 0:
        logger.info("✅ Validación completada: sin problemas de calidad detectados")
    else:
        logger.warning(f"⚠️  Validación completada: {total_issues} problemas detectados")
    return report
