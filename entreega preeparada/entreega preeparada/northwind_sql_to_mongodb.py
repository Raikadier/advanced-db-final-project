"""
northwind_sql_to_mongodb.py
Lee datos REALES desde la Staging Area (SQL Server) y carga el DW en MongoDB.

Arquitectura corregida:
    Northwind → [ETL Python] → northwind_staging (SQL Server) → MongoDB DW

Fixes aplicados:
    - FIX-1: Eliminados todos los parsers de regex (leer_sql, parse_xxx)
    - FIX-2: Eliminada función generar_orders() con random()
    - FIX-3: Lee datos reales desde STG_ORDERS y STG_ORDER_DETAILS
    - FIX-4: segmento_cliente basado en total_venta real (STG_ValorNeto)
    - FIX-5: Agregada dim_metas_empleado (diseño Fase 1)

Uso:
    python northwind_sql_to_mongodb.py

Requisitos:
    pip install pymongo pyodbc pandas
"""

import pyodbc
import pandas as pd
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# ── Configuración ──────────────────────────────────────────────────────────────
STAGING_CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=northwind_staging;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB  = "northwind_dw"

ZONA_MAP = {
    "USA":         ("América",  "Norteamérica"),
    "CANADA":      ("América",  "Norteamérica"),
    "MEXICO":      ("América",  "Latinoamérica"),
    "BRAZIL":      ("América",  "Latinoamérica"),
    "ARGENTINA":   ("América",  "Latinoamérica"),
    "VENEZUELA":   ("América",  "Latinoamérica"),
    "GERMANY":     ("Europa",   "Europa Occidental"),
    "UK":          ("Europa",   "Europa Occidental"),
    "FRANCE":      ("Europa",   "Europa Occidental"),
    "SPAIN":       ("Europa",   "Europa Occidental"),
    "ITALY":       ("Europa",   "Europa Occidental"),
    "PORTUGAL":    ("Europa",   "Europa Occidental"),
    "AUSTRIA":     ("Europa",   "Europa Central"),
    "SWITZERLAND": ("Europa",   "Europa Central"),
    "BELGIUM":     ("Europa",   "Europa Occidental"),
    "NETHERLANDS": ("Europa",   "Europa Occidental"),
    "DENMARK":     ("Europa",   "Europa del Norte"),
    "SWEDEN":      ("Europa",   "Europa del Norte"),
    "NORWAY":      ("Europa",   "Europa del Norte"),
    "FINLAND":     ("Europa",   "Europa del Norte"),
    "POLAND":      ("Europa",   "Europa del Este"),
    "IRELAND":     ("Europa",   "Europa Occidental"),
    "JAPAN":       ("Asia",     "Asia Oriental"),
    "SINGAPORE":   ("Asia",     "Asia Oriental"),
    "AUSTRALIA":   ("Oceanía",  "Oceanía"),
}
NOMBRES_MES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
NOMBRES_DIA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# ── FIX-1: Lector del Staging (reemplaza todos los parsers de regex) ──────────

def read_staging(table_name: str) -> list[dict]:
    """
    Lee una tabla del Staging Area (SQL Server) y retorna lista de dicts.
    Reemplaza: leer_sql(), parse_customers(), parse_employees(), etc.
    """
    conn = pyodbc.connect(STAGING_CONN_STR)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    records = df.to_dict("records")
    log.info(f"  {table_name}: {len(records):,} registros leídos del staging")
    return records


def to_dt(val) -> datetime | None:
    """Convierte cualquier tipo de fecha a datetime de Python para pymongo."""
    if val is None:
        return None
    if isinstance(val, float) and pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime()
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val[:10])
        except ValueError:
            return None
    return None


# ── Constructores de dimensiones ───────────────────────────────────────────────

def fid(val) -> str | None:
    """Convierte fecha a string YYYYMMDD para usar como fecha_id."""
    dt = to_dt(val)
    return None if dt is None else dt.strftime("%Y%m%d")


def build_dim_fecha(orders: list[dict]) -> list[dict]:
    """Genera la dimensión de fechas cubriendo todo el rango de OrderDate y ShippedDate."""
    fechas = set()
    for o in orders:
        od = to_dt(o.get("OrderDate"))
        sd = to_dt(o.get("ShippedDate") or o.get("STG_DiasEntrega") and o.get("OrderDate"))
        if od:
            fechas.add(od.date())
        shipped = to_dt(o.get("ShippedDate"))
        if shipped:
            fechas.add(shipped.date())

    if not fechas:
        log.warning("  Sin fechas disponibles — usando rango Northwind por defecto")
        from datetime import date
        mn, mx = date(1996, 7, 4), date(1998, 5, 6)
    else:
        mn, mx = min(fechas), max(fechas)

    docs, cur = [], mn
    while cur <= mx:
        dt = datetime(cur.year, cur.month, cur.day)
        docs.append({
            "fecha_id":    cur.strftime("%Y%m%d"),
            "fecha_completa": dt,
            "anio":        cur.year,
            "trimestre":   (cur.month - 1) // 3 + 1,
            "mes":         cur.month,
            "nombre_mes":  NOMBRES_MES[cur.month],
            "semana_anio": cur.isocalendar()[1],
            "dia":         cur.day,
            "nombre_dia":  NOMBRES_DIA[cur.weekday()],
            "es_fin_semana": cur.weekday() >= 5,
        })
        cur += timedelta(days=1)
    log.info(f"  dim_fecha: {len(docs):,} docs ({mn} → {mx})")
    return docs


def build_dim_cliente(customers: list[dict], orders: list[dict], details: list[dict]) -> list[dict]:
    """
    FIX-4: segmento_cliente basado en total_venta real (STG_ValorNeto),
    NO en Freight como estaba antes.
    """
    from collections import defaultdict

    # Cruzar orders → customers para sumar ventas reales por cliente
    order_to_customer = {o["OrderID"]: o["CustomerID"] for o in orders}
    order_fecha       = {o["OrderID"]: to_dt(o.get("OrderDate")) for o in orders}

    stats = defaultdict(lambda: {"total_ventas": 0.0, "n_ordenes": 0,
                                  "ultima_compra": datetime(1990, 1, 1)})
    # Acumular ventas desde STG_ValorNeto (valor neto real calculado en ETL)
    for d in details:
        oid  = d.get("OrderID")
        cid  = order_to_customer.get(oid)
        if not cid:
            continue
        valor = float(d.get("STG_ValorNeto") or 0)
        stats[cid]["total_ventas"] += valor
        stats[cid]["n_ordenes"]    += 1
        fecha = order_fecha.get(oid)
        if fecha and isinstance(fecha, datetime) and fecha > stats[cid]["ultima_compra"]:
            stats[cid]["ultima_compra"] = fecha

    fechas_validas = [to_dt(o.get("OrderDate")) for o in orders
                      if to_dt(o.get("OrderDate")) is not None]
    hoy = max(fechas_validas) if fechas_validas else datetime(1998, 5, 6)

    docs = []
    for c in customers:
        cid = c.get("CustomerID")
        s   = stats[cid]
        dias_inactivo = (hoy - s["ultima_compra"]).days \
            if s["ultima_compra"] > datetime(1990, 1, 1) else 9999

        # Segmentación por ventas reales
        if   dias_inactivo > 400:          segmento = "Inactivo"
        elif s["n_ordenes"] <= 1:          segmento = "Nuevo"
        elif s["total_ventas"] > 10000:    segmento = "Premium"
        else:                              segmento = "Regular"

        docs.append({
            "cliente_id":       cid,
            "company_name":     c.get("CompanyName"),
            "contact_name":     c.get("ContactName"),
            "contact_title":    c.get("ContactTitle"),
            "address":          c.get("Address"),
            "city":             c.get("City"),
            "region":           c.get("Region"),
            "postal_code":      c.get("PostalCode"),
            "country":          c.get("Country"),
            "phone":            c.get("Phone"),
            "fax":              c.get("Fax"),
            "total_ventas_usd": round(s["total_ventas"], 2),
            "n_ordenes":        s["n_ordenes"],
            "segmento_cliente": segmento,
        })
    log.info(f"  dim_cliente: {len(docs):,} docs")
    return docs


def build_dim_empleado(employees: list[dict]) -> list[dict]:
    """
    Lee empleados del staging. Los campos ya vienen transformados (UPPER/TRIM)
    y la fecha HireDate ya viene como DATE desde el staging.
    """
    docs = []
    for e in employees:
        docs.append({
            "empleado_id": int(e["EmployeeID"]),
            "last_name":   e.get("LastName"),
            "first_name":  e.get("FirstName"),
            "full_name":   e.get("FullName") or
                           f"{e.get('FirstName','')} {e.get('LastName','')}".strip(),
            "title":       e.get("Title"),
            "hire_date":   to_dt(e.get("HireDate")),
            "city":        e.get("City"),
            "country":     e.get("Country"),
            "region":      e.get("Region"),
            "reports_to":  int(e["ReportsTo"]) if e.get("ReportsTo") is not None else None,
        })
    log.info(f"  dim_empleado: {len(docs):,} docs")
    return docs


def build_dim_producto(products: list[dict], categories: list[dict],
                       suppliers: list[dict]) -> list[dict]:
    cat_map = {c["CategoryID"]: c["CategoryName"] for c in categories}
    sup_map = {s["SupplierID"]: s["CompanyName"]  for s in suppliers}
    docs = []
    for p in products:
        up = float(p.get("UnitPrice") or 0)
        docs.append({
            "producto_id":      int(p["ProductID"]),
            "product_name":     p.get("ProductName"),
            "categoria_id":     int(p["CategoryID"]) if p.get("CategoryID") else None,
            "categoria":        cat_map.get(p.get("CategoryID"), "Sin categoría"),
            "proveedor_id":     int(p["SupplierID"]) if p.get("SupplierID") else None,
            "proveedor":        sup_map.get(p.get("SupplierID"), "Desconocido"),
            "unit_price":       up,
            "units_in_stock":   int(p.get("UnitsInStock") or 0),
            "units_on_order":   int(p.get("UnitsOnOrder") or 0),
            "reorder_level":    int(p.get("ReorderLevel") or 0),
            "discontinued":     bool(p.get("Discontinued")),
            # Costo estimado = 60% del precio histórico (supuesto documentado Fase 1)
            "costo_adquisicion": round(up * 0.60, 2),
        })
    log.info(f"  dim_producto: {len(docs):,} docs")
    return docs


def build_dim_shipper(shippers: list[dict], orders: list[dict]) -> list[dict]:
    from collections import defaultdict
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
            "shipper_id":       int(sid),
            "company_name":     s.get("CompanyName"),
            "phone":            s.get("Phone"),
            "avg_delivery_days": avg,
        })
    log.info(f"  dim_shipper: {len(docs):,} docs")
    return docs


def build_dim_territorio(customers: list[dict]) -> list[dict]:
    seen, docs = {}, []
    for c in customers:
        country = (c.get("Country") or "").strip()
        city    = (c.get("City")    or "").strip()
        key     = f"{country}-{city}"
        if key in seen:
            continue
        seen[key] = True
        cu       = country.upper()
        cont, zona = ZONA_MAP.get(cu, ("Otro", "Otro"))
        cc  = cu[:3]  if cu   else "OTR"
        ck  = city[:2].upper() if city else "XX"
        tid = f"{cc}-{ck}"
        base, n = tid, 1
        existing = {d["territorio_id"] for d in docs}
        while tid in existing:
            tid = f"{base}-{n}"
            n  += 1
        docs.append({
            "territorio_id": tid,
            "city":          city    or None,
            "region":        c.get("Region"),
            "country":       country,
            "continente":    cont,
            "zona":          zona,
        })
    log.info(f"  dim_territorio: {len(docs):,} docs")
    return docs


def build_dim_metas_empleado(employees: list[dict]) -> list[dict]:
    """
    FIX-5: Nueva dimensión según diseño de Fase 1.
    Metas trimestrales por empleado según cargo (1996-1998).
    """
    # Meta base según cargo
    meta_por_titulo = {
        "Vice President, Sales": 18000.0,
        "Sales Manager":         15000.0,
    }
    categoria_por_titulo = {
        "Vice President, Sales": "Agresiva",
        "Sales Manager":         "Estándar",
    }
    docs = []
    for e in employees:
        eid   = int(e["EmployeeID"])
        title = (e.get("Title") or "").strip()
        meta  = meta_por_titulo.get(title, 12000.0)
        cat   = categoria_por_titulo.get(title, "Básica")
        for anio in [1996, 1997, 1998]:
            for trimestre in [1, 2, 3, 4]:
                docs.append({
                    "empleado_id":    eid,
                    "anio":           anio,
                    "trimestre":      trimestre,
                    "meta_ventas_usd": meta,
                    "categoria_meta": cat,
                })
    log.info(f"  dim_metas_empleado: {len(docs):,} docs "
             f"({len(employees)} emp × 3 años × 4 trim)")
    return docs


def build_fact_ventas(orders: list[dict], details: list[dict],
                      dim_producto: list[dict], dim_cliente: list[dict],
                      dim_territorio: list[dict]) -> list[dict]:
    """
    FIX-2/3: Usa datos REALES del staging.
    - orders  ← STG_ORDERS  (campos reales con STG_DiasEntrega calculado por ETL)
    - details ← STG_ORDER_DETAILS (STG_ValorNeto calculado por ETL)
    """
    costo_map  = {p["producto_id"]: p["costo_adquisicion"] for p in dim_producto}
    terr_map   = {}
    for t in dim_territorio:
        c = (t.get("country") or "").strip().upper()
        if c not in terr_map:
            terr_map[c] = t["territorio_id"]
    cli_country = {d["cliente_id"]: (d.get("country") or "").strip().upper()
                   for d in dim_cliente}
    order_map   = {o["OrderID"]: o for o in orders}

    docs = []
    for d in details:
        oid  = d["OrderID"]
        pid  = d["ProductID"]
        o    = order_map.get(oid, {})
        cid  = o.get("CustomerID", "")

        up   = float(d.get("UnitPrice") or 0)
        qty  = int(d.get("Quantity")    or 0)
        disc = float(d.get("Discount")  or 0)

        # Usar STG_ValorNeto calculado por el ETL cuando esté disponible
        stg_valor = d.get("STG_ValorNeto")
        total = round(float(stg_valor), 2) if stg_valor is not None \
            else round(up * qty * (1 - disc), 2)

        sub  = round(up * qty, 2)
        cu   = costo_map.get(pid, round(up * 0.60, 2))
        ct   = round(cu * qty, 2)
        mg   = round(total - ct, 2)
        mgp  = round((mg / total * 100) if total else 0, 2)

        country_key = cli_country.get(cid, "")
        terr_id     = terr_map.get(country_key, "OTR-XX")

        # Dias entrega y puntualidad ya calculados por el ETL
        dias_etl = o.get("STG_DiasEntrega")
        dias_entrega = int(dias_etl) if dias_etl is not None else None
        entrega_puntual_etl = o.get("STG_EntregaPuntual")
        entrega_puntual = bool(entrega_puntual_etl) \
            if entrega_puntual_etl is not None else None

        docs.append({
            "order_id":         oid,
            "order_detail_id":  f"{oid}-{pid}",
            "fecha_id":         fid(o.get("OrderDate")),
            "fecha_entrega_id": fid(o.get("ShippedDate")),
            "cliente_id":       cid,
            "empleado_id":      int(o["EmployeeID"]) if o.get("EmployeeID") else None,
            "producto_id":      pid,
            "shipper_id":       int(o["ShipVia"])    if o.get("ShipVia")    else None,
            "territorio_id":    terr_id,
            "cantidad":         qty,
            "unit_price":       up,
            "descuento":        disc,
            "freight":          round(float(o.get("Freight") or 0), 2),
            "subtotal":         sub,
            "total_venta":      total,
            "costo_total":      ct,
            "margen":           mg,
            "margen_pct":       mgp,
            "order_date":       to_dt(o.get("OrderDate")),
            "required_date":    to_dt(o.get("RequiredDate")),
            "shipped_date":     to_dt(o.get("ShippedDate")),
            "dias_entrega":     dias_entrega,
            "entrega_puntual":  entrega_puntual,
        })
    log.info(f"  fact_ventas: {len(docs):,} docs")
    return docs


# ── Índices ────────────────────────────────────────────────────────────────────

def setup_indexes(db):
    db.dim_fecha.create_index([("fecha_id", ASCENDING)],
                              unique=True, name="idx_fecha_id")
    db.dim_fecha.create_index([("anio", ASCENDING), ("mes", ASCENDING)],
                              name="idx_anio_mes")
    db.dim_fecha.create_index([("trimestre", ASCENDING)], name="idx_trimestre")

    db.dim_cliente.create_index([("cliente_id", ASCENDING)],
                                unique=True, name="idx_cliente_id")
    db.dim_cliente.create_index([("country", ASCENDING)], name="idx_country")

    db.dim_empleado.create_index([("empleado_id", ASCENDING)],
                                 unique=True, name="idx_empleado_id")

    db.dim_producto.create_index([("producto_id", ASCENDING)],
                                 unique=True, name="idx_producto_id")
    db.dim_producto.create_index([("categoria_id", ASCENDING)], name="idx_cat_id")

    db.dim_shipper.create_index([("shipper_id", ASCENDING)],
                                unique=True, name="idx_shipper_id")

    db.dim_territorio.create_index([("territorio_id", ASCENDING)],
                                   unique=True, name="idx_terr_id")
    db.dim_territorio.create_index([("zona", ASCENDING)], name="idx_terr_zona")

    db.dim_metas_empleado.create_index(
        [("empleado_id", ASCENDING), ("anio", ASCENDING), ("trimestre", ASCENDING)],
        unique=True, name="idx_metas_emp_periodo"
    )

    db.fact_ventas.create_index([("order_detail_id", ASCENDING)],
                                unique=True, name="idx_pk_fact")
    db.fact_ventas.create_index([("fecha_id", ASCENDING)],   name="idx_fv_fecha")
    db.fact_ventas.create_index([("cliente_id", ASCENDING)], name="idx_fv_cliente")
    db.fact_ventas.create_index([("empleado_id", ASCENDING)],name="idx_fv_empleado")
    db.fact_ventas.create_index([("producto_id", ASCENDING)],name="idx_fv_producto")
    db.fact_ventas.create_index([("shipper_id", ASCENDING)], name="idx_fv_shipper")
    db.fact_ventas.create_index([("territorio_id", ASCENDING)], name="idx_fv_territorio")
    db.fact_ventas.create_index(
        [("fecha_id", ASCENDING), ("cliente_id", ASCENDING)],
        name="idx_fv_fecha_cliente"
    )
    db.fact_ventas.create_index([("total_venta", DESCENDING)],  name="idx_fv_total_desc")
    db.fact_ventas.create_index([("margen", DESCENDING)],       name="idx_fv_margen_desc")
    log.info("  Índices creados OK")


def insert_col(col, docs: list, name: str):
    inserted = 0
    for i in range(0, len(docs), 500):
        try:
            r = col.insert_many(docs[i:i + 500], ordered=False)
            inserted += len(r.inserted_ids)
        except Exception as e:
            log.warning(f"  {name} lote {i // 500}: {e}")
    log.info(f"  OK {name}: {inserted:,} docs insertados")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    start = datetime.now()
    log.info("=" * 60)
    log.info("  NORTHWIND STAGING → MONGODB DW  (datos reales)")
    log.info(f"  Inicio: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    # ── [1/4] Leer desde el Staging (FIX-1: reemplaza regex parsers) ──────────
    log.info("\n[1/4] Leyendo desde northwind_staging (SQL Server)...")
    customers  = read_staging("STG_CUSTOMERS")
    employees  = read_staging("STG_EMPLOYEES")
    products   = read_staging("STG_PRODUCTS")
    categories = read_staging("STG_CATEGORIES")
    suppliers  = read_staging("STG_SUPPLIERS")
    shippers   = read_staging("STG_SHIPPERS")

    # FIX-2/3: Orders y Details REALES, sin random()
    orders  = read_staging("STG_ORDERS")
    details = read_staging("STG_ORDER_DETAILS")

    if not customers:
        log.error("STG_CUSTOMERS vacía — asegúrate de ejecutar el ETL Python primero.")
        return
    if not orders:
        log.error("STG_ORDERS vacía — el ETL debe ejecutarse y cargar Orders primero.")
        return

    # ── [2/4] Construir dimensiones ────────────────────────────────────────────
    log.info("\n[2/4] Construyendo dimensiones...")
    df = build_dim_fecha(orders)
    dc = build_dim_cliente(customers, orders, details)     # FIX-4: usa ventas reales
    de = build_dim_empleado(employees)
    dp = build_dim_producto(products, categories, suppliers)
    ds = build_dim_shipper(shippers, orders)
    dt = build_dim_territorio(customers)
    dm = build_dim_metas_empleado(employees)               # FIX-5: nueva dimensión

    # ── [3/4] Construir tabla de hechos ────────────────────────────────────────
    log.info("\n[3/4] Construyendo fact_ventas con datos reales...")
    fv = build_fact_ventas(orders, details, dp, dc, dt)

    # ── [4/4] Cargar a MongoDB ─────────────────────────────────────────────────
    log.info("\n[4/4] Cargando a MongoDB...")
    client = MongoClient(MONGO_URI)
    db     = client[MONGO_DB]

    colecciones = ["dim_fecha", "dim_cliente", "dim_empleado", "dim_producto",
                   "dim_shipper", "dim_territorio", "dim_metas_empleado", "fact_ventas"]
    for col in colecciones:
        db[col].drop()
        log.info(f"  Colección {col} limpiada")

    insert_col(db.dim_fecha,          df, "dim_fecha")
    insert_col(db.dim_cliente,        dc, "dim_cliente")
    insert_col(db.dim_empleado,       de, "dim_empleado")
    insert_col(db.dim_producto,       dp, "dim_producto")
    insert_col(db.dim_shipper,        ds, "dim_shipper")
    insert_col(db.dim_territorio,     dt, "dim_territorio")
    insert_col(db.dim_metas_empleado, dm, "dim_metas_empleado")
    insert_col(db.fact_ventas,        fv, "fact_ventas")

    setup_indexes(db)
    client.close()

    # ── Resumen ────────────────────────────────────────────────────────────────
    elapsed = (datetime.now() - start).seconds
    log.info("\n" + "=" * 60)
    log.info("  RESUMEN FINAL")
    log.info("=" * 60)
    log.info(f"  dim_fecha           : {len(df):>6,} docs")
    log.info(f"  dim_cliente         : {len(dc):>6,} docs")
    log.info(f"  dim_empleado        : {len(de):>6,} docs")
    log.info(f"  dim_producto        : {len(dp):>6,} docs")
    log.info(f"  dim_shipper         : {len(ds):>6,} docs")
    log.info(f"  dim_territorio      : {len(dt):>6,} docs")
    log.info(f"  dim_metas_empleado  : {len(dm):>6,} docs")
    log.info(f"  fact_ventas         : {len(fv):>6,} docs")
    log.info(f"  Duración            : {elapsed}s")
    log.info("  MongoDB DW listo en northwind_dw")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
