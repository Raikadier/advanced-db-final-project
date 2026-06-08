"""
load_dw.py — Fase B: Staging (Supabase) → Data Warehouse (MongoDB Atlas)
"""

import logging
from collections import defaultdict
from datetime import date, datetime, timedelta

import pandas as pd
from pymongo import ASCENDING, DESCENDING, MongoClient
from sqlalchemy import text

logger = logging.getLogger(__name__)

DW_COLLECTIONS = [
    "dim_fecha",
    "dim_cliente",
    "dim_empleado",
    "dim_producto",
    "dim_shipper",
    "dim_territorio",
    "dim_metas_empleado",
    "fact_ventas",
]

STAGING_READ_ORDER = [
    "stg_customers",
    "stg_employees",
    "stg_products",
    "stg_categories",
    "stg_suppliers",
    "stg_shippers",
    "stg_orders",
    "stg_order_details",
]

ZONA_MAP = {
    "USA": ("América", "Norteamérica"),
    "CANADA": ("América", "Norteamérica"),
    "MEXICO": ("América", "Latinoamérica"),
    "BRAZIL": ("América", "Latinoamérica"),
    "ARGENTINA": ("América", "Latinoamérica"),
    "VENEZUELA": ("América", "Latinoamérica"),
    "GERMANY": ("Europa", "Europa Occidental"),
    "UK": ("Europa", "Europa Occidental"),
    "FRANCE": ("Europa", "Europa Occidental"),
    "SPAIN": ("Europa", "Europa Occidental"),
    "ITALY": ("Europa", "Europa Occidental"),
    "PORTUGAL": ("Europa", "Europa Occidental"),
    "AUSTRIA": ("Europa", "Europa Central"),
    "SWITZERLAND": ("Europa", "Europa Central"),
    "BELGIUM": ("Europa", "Europa Occidental"),
    "NETHERLANDS": ("Europa", "Europa Occidental"),
    "DENMARK": ("Europa", "Europa del Norte"),
    "SWEDEN": ("Europa", "Europa del Norte"),
    "NORWAY": ("Europa", "Europa del Norte"),
    "FINLAND": ("Europa", "Europa del Norte"),
    "POLAND": ("Europa", "Europa del Este"),
    "IRELAND": ("Europa", "Europa Occidental"),
    "JAPAN": ("Asia", "Asia Oriental"),
    "SINGAPORE": ("Asia", "Asia Oriental"),
    "AUSTRALIA": ("Oceanía", "Oceanía"),
}

NOMBRES_MES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
NOMBRES_DIA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def read_staging_table(engine, table_name: str) -> list[dict]:
    with engine.connect() as conn:
        df = pd.read_sql(text(f"SELECT * FROM {table_name}"), conn)
    records = df.to_dict("records")
    logger.info(f"  {table_name}: {len(records):,} registros leídos del staging")
    return records


def _safe_int(val, default: int | None = None) -> int | None:
    if val is None:
        return default
    try:
        if pd.isna(val):
            return default
    except (TypeError, ValueError):
        pass
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def to_dt(val) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, float) and pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime()
    if isinstance(val, date):
        return datetime(val.year, val.month, val.day)
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val[:10])
        except ValueError:
            return None
    return None


def fid(val) -> str | None:
    dt = to_dt(val)
    return None if dt is None else dt.strftime("%Y%m%d")


def build_dim_fecha(orders: list[dict]) -> list[dict]:
    fechas = set()
    for o in orders:
        od = to_dt(o.get("OrderDate"))
        if od:
            fechas.add(od.date())
        shipped = to_dt(o.get("ShippedDate"))
        if shipped:
            fechas.add(shipped.date())

    if not fechas:
        logger.warning("  Sin fechas — usando rango Northwind por defecto")
        mn, mx = date(1996, 7, 4), date(1998, 5, 6)
    else:
        mn, mx = min(fechas), max(fechas)

    docs, cur = [], mn
    while cur <= mx:
        dt = datetime(cur.year, cur.month, cur.day)
        docs.append({
            "fecha_id": cur.strftime("%Y%m%d"),
            "fecha_completa": dt,
            "anio": cur.year,
            "trimestre": (cur.month - 1) // 3 + 1,
            "mes": cur.month,
            "nombre_mes": NOMBRES_MES[cur.month],
            "semana_anio": cur.isocalendar()[1],
            "dia": cur.day,
            "nombre_dia": NOMBRES_DIA[cur.weekday()],
            "es_fin_semana": cur.weekday() >= 5,
        })
        cur += timedelta(days=1)
    logger.info(f"  dim_fecha: {len(docs):,} docs ({mn} → {mx})")
    return docs


def build_dim_cliente(customers: list[dict], orders: list[dict], details: list[dict]) -> list[dict]:
    order_to_customer = {o["OrderID"]: o["CustomerID"] for o in orders}
    order_fecha = {o["OrderID"]: to_dt(o.get("OrderDate")) for o in orders}

    stats = defaultdict(
        lambda: {"total_ventas": 0.0, "n_ordenes": 0, "ultima_compra": datetime(1990, 1, 1)}
    )
    for d in details:
        oid = d.get("OrderID")
        cid = order_to_customer.get(oid)
        if not cid:
            continue
        valor = float(d.get("STG_ValorNeto") or 0)
        stats[cid]["total_ventas"] += valor
        stats[cid]["n_ordenes"] += 1
        fecha = order_fecha.get(oid)
        if fecha and isinstance(fecha, datetime) and fecha > stats[cid]["ultima_compra"]:
            stats[cid]["ultima_compra"] = fecha

    fechas_validas = [to_dt(o.get("OrderDate")) for o in orders if to_dt(o.get("OrderDate"))]
    hoy = max(fechas_validas) if fechas_validas else datetime(1998, 5, 6)

    docs = []
    for c in customers:
        cid = c.get("CustomerID")
        s = stats[cid]
        dias_inactivo = (
            (hoy - s["ultima_compra"]).days
            if s["ultima_compra"] > datetime(1990, 1, 1)
            else 9999
        )
        if dias_inactivo > 400:
            segmento = "Inactivo"
        elif s["n_ordenes"] <= 1:
            segmento = "Nuevo"
        elif s["total_ventas"] > 10000:
            segmento = "Premium"
        else:
            segmento = "Regular"

        docs.append({
            "cliente_id": cid,
            "company_name": c.get("CompanyName"),
            "contact_name": c.get("ContactName"),
            "contact_title": c.get("ContactTitle"),
            "address": c.get("Address"),
            "city": c.get("City"),
            "region": c.get("Region"),
            "postal_code": c.get("PostalCode"),
            "country": c.get("Country"),
            "phone": c.get("Phone"),
            "fax": c.get("Fax"),
            "total_ventas_usd": round(s["total_ventas"], 2),
            "n_ordenes": s["n_ordenes"],
            "segmento_cliente": segmento,
        })
    logger.info(f"  dim_cliente: {len(docs):,} docs")
    return docs


def build_dim_empleado(employees: list[dict]) -> list[dict]:
    docs = []
    for e in employees:
        docs.append({
            "empleado_id": int(e["EmployeeID"]),
            "last_name": e.get("LastName"),
            "first_name": e.get("FirstName"),
            "full_name": e.get("FullName")
            or f"{e.get('FirstName', '')} {e.get('LastName', '')}".strip(),
            "title": e.get("Title"),
            "hire_date": to_dt(e.get("HireDate")),
            "city": e.get("City"),
            "country": e.get("Country"),
            "region": e.get("Region"),
            "reports_to": _safe_int(e.get("ReportsTo")),
        })
    logger.info(f"  dim_empleado: {len(docs):,} docs")
    return docs


def build_dim_producto(
    products: list[dict], categories: list[dict], suppliers: list[dict]
) -> list[dict]:
    cat_map = {c["CategoryID"]: c["CategoryName"] for c in categories}
    sup_map = {s["SupplierID"]: s["CompanyName"] for s in suppliers}
    docs = []
    for p in products:
        up = float(p.get("UnitPrice") or 0)
        docs.append({
            "producto_id": int(p["ProductID"]),
            "product_name": p.get("ProductName"),
            "categoria_id": int(p["CategoryID"]) if p.get("CategoryID") else None,
            "categoria": cat_map.get(p.get("CategoryID"), "Sin categoría"),
            "proveedor_id": int(p["SupplierID"]) if p.get("SupplierID") else None,
            "proveedor": sup_map.get(p.get("SupplierID"), "Desconocido"),
            "unit_price": up,
            "units_in_stock": int(p.get("UnitsInStock") or 0),
            "units_on_order": int(p.get("UnitsOnOrder") or 0),
            "reorder_level": int(p.get("ReorderLevel") or 0),
            "discontinued": bool(p.get("Discontinued")),
            "costo_adquisicion": round(up * 0.60, 2),
        })
    logger.info(f"  dim_producto: {len(docs):,} docs")
    return docs


def build_dim_shipper(shippers: list[dict], orders: list[dict]) -> list[dict]:
    dias = defaultdict(list)
    for o in orders:
        dias_entrega = o.get("STG_DiasEntrega")
        if dias_entrega is not None:
            try:
                dias[o["ShipVia"]].append(int(dias_entrega))
            except (TypeError, ValueError):
                pass
    docs = []
    for s in shippers:
        sid = s["ShipperID"]
        avg = round(sum(dias[sid]) / len(dias[sid]), 1) if dias[sid] else 0.0
        docs.append({
            "shipper_id": int(sid),
            "company_name": s.get("CompanyName"),
            "phone": s.get("Phone"),
            "avg_delivery_days": avg,
        })
    logger.info(f"  dim_shipper: {len(docs):,} docs")
    return docs


def build_dim_territorio(customers: list[dict]) -> list[dict]:
    seen, docs = {}, []
    for c in customers:
        country = (c.get("Country") or "").strip()
        city = (c.get("City") or "").strip()
        key = f"{country}-{city}"
        if key in seen:
            continue
        seen[key] = True
        cu = country.upper()
        cont, zona = ZONA_MAP.get(cu, ("Otro", "Otro"))
        cc = cu[:3] if cu else "OTR"
        ck = city[:2].upper() if city else "XX"
        tid = f"{cc}-{ck}"
        base, n = tid, 1
        existing = {d["territorio_id"] for d in docs}
        while tid in existing:
            tid = f"{base}-{n}"
            n += 1
        docs.append({
            "territorio_id": tid,
            "city": city or None,
            "region": c.get("Region"),
            "country": country,
            "continente": cont,
            "zona": zona,
        })
    logger.info(f"  dim_territorio: {len(docs):,} docs")
    return docs


def build_dim_metas_empleado(employees: list[dict]) -> list[dict]:
    meta_por_titulo = {
        "Vice President, Sales": 18000.0,
        "Sales Manager": 15000.0,
    }
    categoria_por_titulo = {
        "Vice President, Sales": "Agresiva",
        "Sales Manager": "Estándar",
    }
    docs = []
    for e in employees:
        eid = int(e["EmployeeID"])
        title = (e.get("Title") or "").strip()
        meta = meta_por_titulo.get(title, 12000.0)
        cat = categoria_por_titulo.get(title, "Básica")
        for anio in [1996, 1997, 1998]:
            for trimestre in [1, 2, 3, 4]:
                docs.append({
                    "empleado_id": eid,
                    "anio": anio,
                    "trimestre": trimestre,
                    "meta_ventas_usd": meta,
                    "categoria_meta": cat,
                })
    logger.info(f"  dim_metas_empleado: {len(docs):,} docs")
    return docs


def build_fact_ventas(
    orders: list[dict],
    details: list[dict],
    dim_producto: list[dict],
    dim_cliente: list[dict],
    dim_territorio: list[dict],
) -> list[dict]:
    costo_map = {p["producto_id"]: p["costo_adquisicion"] for p in dim_producto}
    terr_map = {}
    for t in dim_territorio:
        c = (t.get("country") or "").strip().upper()
        if c not in terr_map:
            terr_map[c] = t["territorio_id"]
    cli_country = {
        d["cliente_id"]: (d.get("country") or "").strip().upper() for d in dim_cliente
    }
    order_map = {o["OrderID"]: o for o in orders}

    docs = []
    for d in details:
        oid = d["OrderID"]
        pid = _safe_int(d.get("ProductID"))
        o = order_map.get(oid, {})
        cid = o.get("CustomerID", "")

        up = float(d.get("UnitPrice") or 0)
        qty = _safe_int(d.get("Quantity"), 0) or 0
        disc = float(d.get("Discount") or 0)

        stg_valor = d.get("STG_ValorNeto")
        total = (
            round(float(stg_valor), 2)
            if stg_valor is not None
            else round(up * qty * (1 - disc), 2)
        )

        sub = round(up * qty, 2)
        cu = costo_map.get(pid, round(up * 0.60, 2))
        ct = round(cu * qty, 2)
        mg = round(total - ct, 2)
        mgp = round((mg / total * 100) if total else 0, 2)

        country_key = cli_country.get(cid, "")
        terr_id = terr_map.get(country_key, "OTR-XX")

        dias_entrega = _safe_int(o.get("STG_DiasEntrega"))
        entrega_puntual_etl = o.get("STG_EntregaPuntual")
        entrega_puntual = (
            bool(entrega_puntual_etl) if entrega_puntual_etl is not None else None
        )

        docs.append({
            "order_id": oid,
            "order_detail_id": f"{oid}-{pid}",
            "fecha_id": fid(o.get("OrderDate")),
            "fecha_entrega_id": fid(o.get("ShippedDate")),
            "cliente_id": cid,
            "empleado_id": _safe_int(o.get("EmployeeID")),
            "producto_id": pid,
            "shipper_id": _safe_int(o.get("ShipVia")),
            "territorio_id": terr_id,
            "cantidad": qty,
            "unit_price": up,
            "descuento": disc,
            "freight": round(float(o.get("Freight") or 0), 2),
            "subtotal": sub,
            "total_venta": total,
            "costo_total": ct,
            "margen": mg,
            "margen_pct": mgp,
            "order_date": to_dt(o.get("OrderDate")),
            "required_date": to_dt(o.get("RequiredDate")),
            "shipped_date": to_dt(o.get("ShippedDate")),
            "dias_entrega": dias_entrega,
            "entrega_puntual": entrega_puntual,
        })
    logger.info(f"  fact_ventas: {len(docs):,} docs")
    return docs


def setup_indexes(db) -> None:
    db.dim_fecha.create_index([("fecha_id", ASCENDING)], unique=True, name="idx_fecha_id")
    db.dim_fecha.create_index([("anio", ASCENDING), ("mes", ASCENDING)], name="idx_anio_mes")
    db.dim_fecha.create_index([("trimestre", ASCENDING)], name="idx_trimestre")

    db.dim_cliente.create_index([("cliente_id", ASCENDING)], unique=True, name="idx_cliente_id")
    db.dim_cliente.create_index([("country", ASCENDING)], name="idx_country")

    db.dim_empleado.create_index([("empleado_id", ASCENDING)], unique=True, name="idx_empleado_id")

    db.dim_producto.create_index([("producto_id", ASCENDING)], unique=True, name="idx_producto_id")
    db.dim_producto.create_index([("categoria_id", ASCENDING)], name="idx_cat_id")

    db.dim_shipper.create_index([("shipper_id", ASCENDING)], unique=True, name="idx_shipper_id")

    db.dim_territorio.create_index([("territorio_id", ASCENDING)], unique=True, name="idx_terr_id")
    db.dim_territorio.create_index([("zona", ASCENDING)], name="idx_terr_zona")

    db.dim_metas_empleado.create_index(
        [("empleado_id", ASCENDING), ("anio", ASCENDING), ("trimestre", ASCENDING)],
        unique=True,
        name="idx_metas_emp_periodo",
    )

    db.fact_ventas.create_index([("order_detail_id", ASCENDING)], unique=True, name="idx_pk_fact")
    db.fact_ventas.create_index([("fecha_id", ASCENDING)], name="idx_fv_fecha")
    db.fact_ventas.create_index([("cliente_id", ASCENDING)], name="idx_fv_cliente")
    db.fact_ventas.create_index([("empleado_id", ASCENDING)], name="idx_fv_empleado")
    db.fact_ventas.create_index([("producto_id", ASCENDING)], name="idx_fv_producto")
    db.fact_ventas.create_index([("shipper_id", ASCENDING)], name="idx_fv_shipper")
    db.fact_ventas.create_index([("territorio_id", ASCENDING)], name="idx_fv_territorio")
    db.fact_ventas.create_index(
        [("fecha_id", ASCENDING), ("cliente_id", ASCENDING)],
        name="idx_fv_fecha_cliente",
    )
    db.fact_ventas.create_index([("total_venta", DESCENDING)], name="idx_fv_total_desc")
    db.fact_ventas.create_index([("margen", DESCENDING)], name="idx_fv_margen_desc")
    logger.info("  Índices MongoDB creados")


def insert_col(col, docs: list, name: str, batch_size: int = 500) -> int:
    inserted = 0
    for i in range(0, len(docs), batch_size):
        try:
            r = col.insert_many(docs[i : i + batch_size], ordered=False)
            inserted += len(r.inserted_ids)
        except Exception as e:
            logger.warning(f"  {name} lote {i // batch_size}: {e}")
    logger.info(f"  OK {name}: {inserted:,} docs insertados")
    return inserted


def load_dw(staging_engine, mongo_uri: str, mongo_db: str, batch_size: int = 500) -> dict:
    """
    Lee staging, construye modelo estrella, limpia colecciones DW y recarga MongoDB.
    Retorna conteo de documentos por colección.
    """
    logger.info("Leyendo tablas staging para Fase B...")
    customers = read_staging_table(staging_engine, "stg_customers")
    employees = read_staging_table(staging_engine, "stg_employees")
    products = read_staging_table(staging_engine, "stg_products")
    categories = read_staging_table(staging_engine, "stg_categories")
    suppliers = read_staging_table(staging_engine, "stg_suppliers")
    shippers = read_staging_table(staging_engine, "stg_shippers")
    orders = read_staging_table(staging_engine, "stg_orders")
    details = read_staging_table(staging_engine, "stg_order_details")

    if not customers:
        raise RuntimeError("stg_customers vacía — ejecuta Fase A primero.")
    if not orders:
        raise RuntimeError("stg_orders vacía — ejecuta Fase A primero.")

    logger.info("Construyendo dimensiones...")
    dim_fecha = build_dim_fecha(orders)
    dim_cliente = build_dim_cliente(customers, orders, details)
    dim_empleado = build_dim_empleado(employees)
    dim_producto = build_dim_producto(products, categories, suppliers)
    dim_shipper = build_dim_shipper(shippers, orders)
    dim_territorio = build_dim_territorio(customers)
    dim_metas = build_dim_metas_empleado(employees)

    logger.info("Construyendo fact_ventas...")
    fact_ventas = build_fact_ventas(orders, details, dim_producto, dim_cliente, dim_territorio)

    if not mongo_uri:
        raise ValueError("MONGO_URI vacía — revisa .env")

    logger.info("Limpiando y cargando MongoDB (%s)...", mongo_db)
    client = MongoClient(mongo_uri)
    db = client[mongo_db]

    for col_name in DW_COLLECTIONS:
        db[col_name].drop()
        logger.info(f"  Colección {col_name} limpiada")

    counts = {
        "dim_fecha": insert_col(db.dim_fecha, dim_fecha, "dim_fecha", batch_size),
        "dim_cliente": insert_col(db.dim_cliente, dim_cliente, "dim_cliente", batch_size),
        "dim_empleado": insert_col(db.dim_empleado, dim_empleado, "dim_empleado", batch_size),
        "dim_producto": insert_col(db.dim_producto, dim_producto, "dim_producto", batch_size),
        "dim_shipper": insert_col(db.dim_shipper, dim_shipper, "dim_shipper", batch_size),
        "dim_territorio": insert_col(db.dim_territorio, dim_territorio, "dim_territorio", batch_size),
        "dim_metas_empleado": insert_col(db.dim_metas_empleado, dim_metas, "dim_metas_empleado", batch_size),
        "fact_ventas": insert_col(db.fact_ventas, fact_ventas, "fact_ventas", batch_size),
    }

    setup_indexes(db)
    client.close()

    logger.info("Fase B completada — DW recargado en %s", mongo_db)
    return counts
