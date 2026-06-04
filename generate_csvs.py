"""
generate_csvs.py
Lee northwind.sql (ya en el repositorio) y genera los CSV del DW
sin necesitar MongoDB, SQL Server, ni ningún servidor externo.

Uso:
    python generate_csvs.py

Salida: carpeta csvs/ con 8 archivos listos para Power BI
"""

import re, csv, os
from datetime import datetime, timedelta
from pathlib import Path

SQL_PATH = Path(__file__).parent / "ETL_Base_ded_datos" / "scripteado" / "northwind.sql"
OUT_DIR  = Path(__file__).parent / "csvs"

NOMBRES_MES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
               "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
NOMBRES_DIA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
ZONA_MAP = {
    "USA":("América","Norteamérica"),"CANADA":("América","Norteamérica"),
    "MEXICO":("América","Latinoamérica"),"BRAZIL":("América","Latinoamérica"),
    "ARGENTINA":("América","Latinoamérica"),"VENEZUELA":("América","Latinoamérica"),
    "GERMANY":("Europa","Europa Occidental"),"UK":("Europa","Europa Occidental"),
    "FRANCE":("Europa","Europa Occidental"),"SPAIN":("Europa","Europa Occidental"),
    "ITALY":("Europa","Europa Occidental"),"PORTUGAL":("Europa","Europa Occidental"),
    "AUSTRIA":("Europa","Europa Central"),"SWITZERLAND":("Europa","Europa Central"),
    "BELGIUM":("Europa","Europa Occidental"),"NETHERLANDS":("Europa","Europa Occidental"),
    "DENMARK":("Europa","Europa del Norte"),"SWEDEN":("Europa","Europa del Norte"),
    "NORWAY":("Europa","Europa del Norte"),"FINLAND":("Europa","Europa del Norte"),
    "POLAND":("Europa","Europa del Este"),"IRELAND":("Europa","Europa Occidental"),
    "SINGAPORE":("Asia","Asia Oriental"),"JAPAN":("Asia","Asia Oriental"),
    "AUSTRALIA":("Oceanía","Oceanía"),
}

# ── Lector ────────────────────────────────────────────────────────────────────

def leer_sql():
    data = open(SQL_PATH, 'rb').read()
    return data.decode('utf-16', errors='ignore')

# ── Helper: parsear valores SQL ───────────────────────────────────────────────

def sql_val(v):
    """Convierte un token SQL a valor Python."""
    v = v.strip()
    if v.upper() == 'NULL': return None
    if v.startswith("N'") or v.startswith("n'"): v = v[1:]
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1].replace("''", "'")
    try: return int(v)
    except ValueError: pass
    try: return float(v)
    except ValueError: pass
    return v

def parse_values_line(line):
    """
    Extrae la lista de valores de una línea SQL VALUES (...).
    Maneja strings con comillas escapadas '' y prefijo N'.
    """
    # Eliminar el "VALUES (" o "VALUES(" del inicio
    m = re.search(r'VALUES\s*\((.+)\)\s*$', line, re.IGNORECASE | re.DOTALL)
    if not m: return []
    content = m.group(1)

    tokens = []
    i = 0
    while i < len(content):
        c = content[i]
        if c in (' ', '\t', '\n', '\r'):
            i += 1
        elif c == ',':
            i += 1
        elif content[i:i+2].upper() == "N'" or c == "'":
            # string literal
            start = i + (2 if content[i:i+2].upper() == "N'" else 1)
            val = []
            j = start
            while j < len(content):
                if content[j] == "'" and j+1 < len(content) and content[j+1] == "'":
                    val.append("'"); j += 2
                elif content[j] == "'":
                    j += 1; break
                else:
                    val.append(content[j]); j += 1
            tokens.append("'" + "".join(val) + "'")
            i = j
        elif content[i:i+2] == '0x' or content[i:i+2] == '0X':
            # hex blob — ignorar
            j = i + 2
            while j < len(content) and content[j] in '0123456789abcdefABCDEF':
                j += 1
            tokens.append('NULL')
            i = j
        else:
            # número o NULL
            j = i
            while j < len(content) and content[j] not in (',',):
                j += 1
            tokens.append(content[i:j].strip())
            i = j
    return [sql_val(t) for t in tokens]

def to_date(v):
    """Convierte string de fecha SQL a datetime. Intenta múltiples formatos."""
    if v is None: return None
    s = str(v).strip("'").strip()
    # Intentar con el string completo primero
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try: return datetime.strptime(s, fmt)
        except: pass
    # Si falla, intentar solo los primeros 10 caracteres (parte de fecha)
    for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
        try: return datetime.strptime(s[:10], fmt)
        except: pass
    return None

# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_simple(text, table_name, columns):
    """
    Parsea INSERTs de la forma:
      INSERT "Table"(col1,...) VALUES(v1,...)
      INSERT "Table" VALUES(v1,...)
    """
    pat = re.compile(
        r'INSERT\s+(?:INTO\s+)?["\[]?' + re.escape(table_name) + r'["\]]?\s*'
        r'(?:\([^)]+\)\s*)?VALUES\s*\(([^;]+?)\)',
        re.IGNORECASE | re.DOTALL
    )
    rows = []
    for m in pat.finditer(text):
        raw_vals = m.group(0)
        vals = parse_values_line(raw_vals)
        if len(vals) >= len(columns):
            rows.append(dict(zip(columns, vals[:len(columns)])))
    return rows

def parse_customers(text):
    cols = ["CustomerID","CompanyName","ContactName","ContactTitle",
            "Address","City","Region","PostalCode","Country","Phone","Fax"]
    rows = []
    for line in text.splitlines():
        if 'INSERT' in line and '"Customers"' in line and 'VALUES' in line:
            vals = parse_values_line(line)
            if len(vals) >= len(cols):
                rows.append(dict(zip(cols, vals[:len(cols)])))
    print(f"  Customers : {len(rows)}")
    return rows

def extract_balanced_parens(text, start):
    """
    Dado el índice del '(' de apertura, extrae el contenido hasta el ')' de cierre
    respetando strings y sin entrar en blobs hex.
    Retorna el contenido interno (sin los parens exteriores).
    """
    depth = 0; in_str = False; i = start
    result = []
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "'" and i+1 < len(text) and text[i+1] == "'":
                result.append("''"); i += 2; continue
            elif c == "'":
                in_str = False; result.append(c); i += 1; continue
            else:
                result.append(c); i += 1; continue
        if c == "'":
            in_str = True; result.append(c); i += 1; continue
        if c == '(':
            depth += 1
            if depth == 1: i += 1; continue
            result.append(c); i += 1; continue
        if c == ')':
            depth -= 1
            if depth == 0: break
            result.append(c); i += 1; continue
        result.append(c); i += 1
    return ''.join(result)

def parse_employees(text):
    """
    Employees: blobs hex + algunas direcciones con saltos de linea embebidos.
    Usamos extraccion posicional con balanceo de parentesis.
    """
    clean = re.sub(r'0x[0-9A-Fa-f]+', 'NULL', text)
    rows = []
    for m in re.finditer(r'INSERT\s+"Employees"\s*\([^)]+\)\s*VALUES\s*\(', clean, re.IGNORECASE):
        start  = m.end() - 1          # posicion del '(' de apertura del VALUES
        content = extract_balanced_parens(clean, start)
        content = ' '.join(content.splitlines())   # eliminar saltos internos
        vals = parse_values_line("VALUES (" + content + ")")
        if len(vals) >= 17:
            rows.append({
                "EmployeeID": int(vals[0]) if vals[0] is not None else 0,
                "LastName":   str(vals[1]) if vals[1] else "",
                "FirstName":  str(vals[2]) if vals[2] else "",
                "Title":      str(vals[3]) if vals[3] else "",
                "HireDate":   str(vals[6]) if vals[6] else "",
                "City":       str(vals[8]) if vals[8] else "",
                "Region":     str(vals[9]) if vals[9] else "",
                "Country":    str(vals[11]) if vals[11] else "",
                "ReportsTo":  int(vals[16]) if vals[16] is not None else None,
            })
    print(f"  Employees : {len(rows)}")
    return rows

def parse_categories(text):
    # Categories tiene blob Picture — tomar solo los 3 primeros
    pat = re.compile(
        r'INSERT\s+["\[]?Categories["\]]?\s*\([^)]+\)\s*VALUES\s*\(([^;]+?)\)',
        re.IGNORECASE | re.DOTALL
    )
    rows = []
    for m in pat.finditer(text):
        vals = parse_values_line(m.group(0))
        if len(vals) >= 2:
            rows.append({"CategoryID": vals[0], "CategoryName": vals[1]})
    print(f"  Categories: {len(rows)}")
    return rows

def parse_suppliers(text):
    cols = ["SupplierID","CompanyName","ContactName","ContactTitle",
            "Address","City","Region","PostalCode","Country","Phone","Fax","HomePage"]
    rows = parse_simple(text, "Suppliers", cols)
    print(f"  Suppliers : {len(rows)}")
    return rows

def parse_shippers(text):
    cols = ["ShipperID","CompanyName","Phone"]
    rows = parse_simple(text, "Shippers", cols)
    print(f"  Shippers  : {len(rows)}")
    return rows

def parse_products(text):
    cols = ["ProductID","ProductName","SupplierID","CategoryID","QuantityPerUnit",
            "UnitPrice","UnitsInStock","UnitsOnOrder","ReorderLevel","Discontinued"]
    rows = parse_simple(text, "Products", cols)
    # Convertir tipos
    for r in rows:
        r["ProductID"]    = int(r["ProductID"]) if r["ProductID"] else 0
        r["CategoryID"]   = int(r["CategoryID"]) if r["CategoryID"] else 0
        r["SupplierID"]   = int(r["SupplierID"]) if r["SupplierID"] else 0
        r["UnitPrice"]    = float(r["UnitPrice"]) if r["UnitPrice"] else 0.0
        r["UnitsInStock"] = int(r["UnitsInStock"]) if r["UnitsInStock"] else 0
        r["UnitsOnOrder"] = int(r["UnitsOnOrder"]) if r["UnitsOnOrder"] else 0
        r["ReorderLevel"] = int(r["ReorderLevel"]) if r["ReorderLevel"] else 0
        r["Discontinued"] = bool(int(r["Discontinued"])) if r["Discontinued"] else False
    print(f"  Products  : {len(rows)}")
    return rows

def parse_orders(text):
    """
    Orders usa formato multi-linea:
      INSERT INTO "Orders"
      ("col1","col2",...)
      VALUES (10248, N'VINET', ...)
    """
    # Normalizar: unir cada bloque INSERT INTO "Orders" + columnas + VALUES en una sola linea
    normalized = re.sub(
        r'INSERT\s+INTO\s+"Orders"\s*\([^)]+\)\s*VALUES\s*',
        'INSERT_ORDERS_VALUES ',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )
    pat = re.compile(r'INSERT_ORDERS_VALUES\s*\((.+?)\)\s*(?=INSERT|$)', re.DOTALL)
    cols_order = ["OrderID","CustomerID","EmployeeID","OrderDate","RequiredDate",
                  "ShippedDate","ShipVia","Freight","ShipName","ShipAddress",
                  "ShipCity","ShipRegion","ShipPostalCode","ShipCountry"]
    rows = []
    for m in pat.finditer(normalized):
        raw = "VALUES (" + m.group(1).replace('\n',' ').replace('\t',' ') + ")"
        vals = parse_values_line(raw)
        if len(vals) < 14: continue
        od = to_date(vals[3]); sd = to_date(vals[5]); rd = to_date(vals[4])
        dias = int((sd - od).days) if sd and od else None
        puntual = (1 if sd <= rd else 0) if (sd and rd) else None
        rows.append({
            "OrderID":       int(vals[0]),
            "CustomerID":    str(vals[1]) if vals[1] else "",
            "EmployeeID":    int(vals[2]) if vals[2] is not None else None,
            "OrderDate":     od.strftime('%Y-%m-%d') if od else None,
            "RequiredDate":  rd.strftime('%Y-%m-%d') if rd else None,
            "ShippedDate":   sd.strftime('%Y-%m-%d') if sd else None,
            "ShipVia":       int(vals[6]) if vals[6] is not None else None,
            "Freight":       float(vals[7]) if vals[7] else 0.0,
            "ShipCity":      str(vals[10]) if vals[10] else "",
            "ShipCountry":   str(vals[13]) if vals[13] else "",
            "STG_DiasEntrega":   dias,
            "STG_EntregaPuntual": puntual,
            "fecha_id":          od.strftime('%Y%m%d') if od else None,
            "fecha_entrega_id":  sd.strftime('%Y%m%d') if sd else None,
        })
    print(f"  Orders    : {len(rows)}")
    return rows

def parse_order_details(text):
    pat = re.compile(
        r'INSERT\s+["\[]?Order Details["\]]?\s*(?:\([^)]+\)\s*)?VALUES\s*\('
        r'(\d+),(\d+),([\d.]+),(\d+),([\d.]+)\)',
        re.IGNORECASE
    )
    rows = []
    for m in pat.finditer(text):
        up = float(m.group(3)); qty = int(m.group(4)); disc = float(m.group(5))
        rows.append({
            "OrderID":      int(m.group(1)),
            "ProductID":    int(m.group(2)),
            "UnitPrice":    up, "Quantity": qty, "Discount": disc,
            "STG_ValorNeto": round(up * qty * (1 - disc), 2),
        })
    print(f"  OrdDetails: {len(rows)}")
    return rows

# ── Constructores del modelo dimensional ─────────────────────────────────────

def build_dim_fecha(orders):
    fechas = set()
    for o in orders:
        if o["OrderDate"]:   fechas.add(datetime.strptime(o["OrderDate"],  '%Y-%m-%d').date())
        if o["ShippedDate"]: fechas.add(datetime.strptime(o["ShippedDate"],'%Y-%m-%d').date())
    mn, mx = min(fechas), max(fechas)
    docs, cur = [], mn
    while cur <= mx:
        docs.append({
            "fecha_id":       cur.strftime("%Y%m%d"),
            "fecha_completa": cur.strftime("%Y-%m-%d"),
            "anio":           cur.year,
            "trimestre":      (cur.month - 1) // 3 + 1,
            "mes":            cur.month,
            "nombre_mes":     NOMBRES_MES[cur.month],
            "semana_anio":    cur.isocalendar()[1],
            "dia":            cur.day,
            "nombre_dia":     NOMBRES_DIA[cur.weekday()],
            "es_fin_semana":  cur.weekday() >= 5,
        })
        cur += timedelta(days=1)
    print(f"  dim_fecha : {len(docs)} ({mn} -> {mx})")
    return docs

def build_dim_cliente(customers, orders, details):
    from collections import defaultdict
    o_cid  = {o["OrderID"]: o["CustomerID"] for o in orders}
    o_date = {o["OrderID"]: o["OrderDate"]  for o in orders}
    stats  = defaultdict(lambda: {"total":0.0,"n":0,"ultima":"1990-01-01"})
    for d in details:
        cid = o_cid.get(d["OrderID"])
        if not cid: continue
        stats[cid]["total"] += d["STG_ValorNeto"]
        stats[cid]["n"]     += 1
        f = o_date.get(d["OrderID"]) or "1990-01-01"
        if f and f > stats[cid]["ultima"]: stats[cid]["ultima"] = f
    fechas = [o["OrderDate"] for o in orders if o["OrderDate"]]
    hoy    = max(fechas) if fechas else "1998-05-06"
    docs = []
    for c in customers:
        cid = str(c["CustomerID"])
        s   = stats[cid]
        dias = (datetime.strptime(hoy,'%Y-%m-%d') -
                datetime.strptime(s["ultima"],'%Y-%m-%d')).days if s["ultima"] != "1990-01-01" else 9999
        seg = ("Inactivo" if dias > 400 else
               "Nuevo"    if s["n"] <= 1 else
               "Premium"  if s["total"] > 10000 else "Regular")
        docs.append({
            "cliente_id":       cid,
            "company_name":     c.get("CompanyName",""),
            "contact_name":     c.get("ContactName",""),
            "city":             c.get("City",""),
            "region":           c.get("Region","") or "",
            "country":          c.get("Country",""),
            "phone":            c.get("Phone",""),
            "total_ventas_usd": round(s["total"],2),
            "n_ordenes":        s["n"],
            "segmento_cliente": seg,
        })
    print(f"  dim_cliente: {len(docs)}")
    return docs

def build_dim_empleado(employees):
    docs = []
    for e in employees:
        hd = None
        for fmt in ('%m/%d/%Y','%Y-%m-%d %H:%M:%S','%Y-%m-%d'):
            try: hd = datetime.strptime(str(e.get("HireDate",""))[:10],fmt).strftime('%Y-%m-%d'); break
            except: pass
        docs.append({
            "empleado_id": int(e["EmployeeID"]),
            "last_name":   e.get("LastName",""),
            "first_name":  e.get("FirstName",""),
            "full_name":   f"{e.get('FirstName','')} {e.get('LastName','')}".strip(),
            "title":       e.get("Title",""),
            "hire_date":   hd or "",
            "city":        e.get("City",""),
            "country":     e.get("Country",""),
            "region":      e.get("Region","") or "",
            "reports_to":  e.get("ReportsTo","") or "",
        })
    print(f"  dim_empleado: {len(docs)}")
    return docs

def build_dim_producto(products, categories, suppliers):
    cat_map = {c["CategoryID"]: c["CategoryName"] for c in categories}
    sup_map = {s["SupplierID"]: s["CompanyName"]  for s in suppliers}
    docs = []
    for p in products:
        up = float(p["UnitPrice"])
        docs.append({
            "producto_id":     p["ProductID"],
            "product_name":    p["ProductName"],
            "categoria_id":    p["CategoryID"],
            "categoria":       cat_map.get(p["CategoryID"],"Sin categoría"),
            "proveedor_id":    p["SupplierID"],
            "proveedor":       sup_map.get(p["SupplierID"],"Desconocido"),
            "unit_price":      up,
            "units_in_stock":  p["UnitsInStock"],
            "discontinued":    p["Discontinued"],
            "costo_adquisicion": round(up * 0.60, 2),
        })
    print(f"  dim_producto: {len(docs)}")
    return docs

def build_dim_shipper(shippers, orders):
    from collections import defaultdict
    dias = defaultdict(list)
    for o in orders:
        if o.get("STG_DiasEntrega") is not None and o.get("ShipVia"):
            dias[o["ShipVia"]].append(o["STG_DiasEntrega"])
    docs = []
    for s in shippers:
        sid = s["ShipperID"]
        avg = round(sum(dias[sid])/len(dias[sid]),1) if dias[sid] else 0.0
        docs.append({
            "shipper_id":        int(sid),
            "company_name":      s["CompanyName"],
            "phone":             s["Phone"],
            "avg_delivery_days": avg,
        })
    print(f"  dim_shipper: {len(docs)}")
    return docs

def build_dim_territorio(customers):
    seen, docs = {}, []
    for c in customers:
        country = (c.get("Country") or "").strip()
        city    = (c.get("City")    or "").strip()
        key = f"{country}-{city}"
        if key in seen: continue
        seen[key] = True
        cu = country.upper()
        cont, zona = ZONA_MAP.get(cu, ("Otro","Otro"))
        cc = cu[:3] if cu else "OTR"
        ck = city[:2].upper() if city else "XX"
        tid = f"{cc}-{ck}"; base=tid; n=1
        existing = {d["territorio_id"] for d in docs}
        while tid in existing: tid=f"{base}-{n}"; n+=1
        docs.append({
            "territorio_id": tid, "city": city,
            "region": c.get("Region","") or "",
            "country": country, "continente": cont, "zona": zona,
        })
    print(f"  dim_territorio: {len(docs)}")
    return docs

def build_dim_metas(employees):
    meta_map = {"Vice President, Sales":18000.0,"Sales Manager":15000.0}
    cat_map  = {"Vice President, Sales":"Agresiva","Sales Manager":"Estándar"}
    docs = []
    for e in employees:
        t = (e.get("Title") or "").strip()
        meta = meta_map.get(t, 12000.0); cat = cat_map.get(t,"Básica")
        for y in [1996,1997,1998]:
            for q in [1,2,3,4]:
                docs.append({"empleado_id":int(e["EmployeeID"]),"anio":y,
                             "trimestre":q,"meta_ventas_usd":meta,"categoria_meta":cat})
    print(f"  dim_metas  : {len(docs)}")
    return docs

def build_fact_ventas(orders, details, dim_producto, dim_cliente, dim_territorio):
    costo_map = {p["producto_id"]: p["costo_adquisicion"] for p in dim_producto}
    terr_map  = {}
    for t in dim_territorio:
        c = (t.get("country") or "").strip().upper()
        if c not in terr_map: terr_map[c] = t["territorio_id"]
    cli_country = {d["cliente_id"]: (d.get("country") or "").strip().upper()
                   for d in dim_cliente}
    order_map = {o["OrderID"]: o for o in orders}
    docs = []
    for d in details:
        oid=d["OrderID"]; pid=d["ProductID"]; o=order_map.get(oid,{})
        cid=o.get("CustomerID","")
        up=float(d["UnitPrice"]); qty=int(d["Quantity"]); disc=float(d["Discount"])
        cu=costo_map.get(pid, round(up*0.60,2))
        sub=round(up*qty,2); total=round(sub*(1-disc),2)
        ct=round(cu*qty,2);  mg=round(total-ct,2)
        mgp=round((mg/total*100) if total else 0, 2)
        tid=terr_map.get(cli_country.get(cid,""),"OTR-XX")
        docs.append({
            "order_id":         oid,
            "order_detail_id":  f"{oid}-{pid}",
            "fecha_id":         o.get("fecha_id","") or "",
            "fecha_entrega_id": o.get("fecha_entrega_id","") or "",
            "cliente_id":       cid,
            "empleado_id":      o.get("EmployeeID","") or "",
            "producto_id":      pid,
            "shipper_id":       o.get("ShipVia","") or "",
            "territorio_id":    tid,
            "cantidad":         qty,
            "unit_price":       up,
            "descuento":        disc,
            "freight":          float(o.get("Freight",0)),
            "subtotal":         sub,
            "total_venta":      total,
            "costo_total":      ct,
            "margen":           mg,
            "margen_pct":       mgp,
            "order_date":       o.get("OrderDate","") or "",
            "required_date":    o.get("RequiredDate","") or "",
            "shipped_date":     o.get("ShippedDate","") or "",
            "dias_entrega":     o.get("STG_DiasEntrega","") if o.get("STG_DiasEntrega") is not None else "",
            "entrega_puntual":  o.get("STG_EntregaPuntual","") if o.get("STG_EntregaPuntual") is not None else "",
        })
    print(f"  fact_ventas: {len(docs)}")
    return docs

# ── Guardar CSV ───────────────────────────────────────────────────────────────

def save_csv(docs, filename):
    if not docs: print(f"  ⚠️  {filename} — sin datos"); return
    path = OUT_DIR / filename
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=docs[0].keys())
        writer.writeheader(); writer.writerows(docs)
    size = os.path.getsize(path)
    print(f"  ✅ {filename:<30} {len(docs):>6} filas  ({size/1024:.1f} KB)")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUT_DIR.mkdir(exist_ok=True)
    print(f"Leyendo {SQL_PATH.name} ...")
    text = leer_sql()
    print(f"  {len(text):,} caracteres\n")

    print("Parseando tablas fuente...")
    customers  = parse_customers(text)
    employees  = parse_employees(text)
    products   = parse_products(text)
    categories = parse_categories(text)
    suppliers  = parse_suppliers(text)
    shippers   = parse_shippers(text)
    orders     = parse_orders(text)
    details    = parse_order_details(text)

    if not customers: print("\nERROR: No se encontraron Customers."); return
    if not orders:    print("\nERROR: No se encontraron Orders."); return

    print(f"\nConstruyendo modelo dimensional...")
    df = build_dim_fecha(orders)
    dc = build_dim_cliente(customers, orders, details)
    de = build_dim_empleado(employees)
    dp = build_dim_producto(products, categories, suppliers)
    ds = build_dim_shipper(shippers, orders)
    dt = build_dim_territorio(customers)
    dm = build_dim_metas(employees)
    fv = build_fact_ventas(orders, details, dp, dc, dt)

    print(f"\nGuardando CSV en {OUT_DIR}/...")
    save_csv(df, "dim_fecha.csv")
    save_csv(dc, "dim_cliente.csv")
    save_csv(de, "dim_empleado.csv")
    save_csv(dp, "dim_producto.csv")
    save_csv(ds, "dim_shipper.csv")
    save_csv(dt, "dim_territorio.csv")
    save_csv(dm, "dim_metas_empleado.csv")
    save_csv(fv, "fact_ventas.csv")

    print(f"\n{'='*55}")
    print(f"  Listo. CSVs en: {OUT_DIR.resolve()}")
    print(f"{'='*55}")

if __name__ == "__main__":
    main()
