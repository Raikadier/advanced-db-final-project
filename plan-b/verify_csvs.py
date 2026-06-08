import csv, sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
CSV_DIR = Path('csvs')

def read_csv(name):
    with open(CSV_DIR / name, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

fecha=read_csv('dim_fecha.csv'); cliente=read_csv('dim_cliente.csv')
empleado=read_csv('dim_empleado.csv'); producto=read_csv('dim_producto.csv')
shipper=read_csv('dim_shipper.csv'); terr=read_csv('dim_territorio.csv')
metas=read_csv('dim_metas_empleado.csv'); fact=read_csv('fact_ventas.csv')

print('=== dim_fecha ===')
print(f'Rango: {fecha[0]["fecha_id"]} -> {fecha[-1]["fecha_id"]}')
for y,c in sorted(Counter(r['anio'] for r in fecha).items()):
    print(f'  {y}: {c} dias')

print()
print('=== dim_empleado (9 registros) ===')
for r in empleado:
    print(f'  {r["empleado_id"]} | {r["full_name"]:<25} | {r["title"]}')

print()
print('=== dim_cliente top 5 por ventas ===')
top = sorted(cliente, key=lambda x: float(x['total_ventas_usd'] or 0), reverse=True)[:5]
for r in top:
    print(f'  {r["cliente_id"]} | {r["company_name"][:28]:<28} | ${float(r["total_ventas_usd"]):>9,.2f} | {r["segmento_cliente"]}')

print()
print('=== dim_producto top 5 precio ===')
top = sorted(producto, key=lambda x: float(x['unit_price'] or 0), reverse=True)[:5]
for r in top:
    print(f'  {r["producto_id"]:>3} | {r["product_name"][:28]:<28} | ${float(r["unit_price"]):>7,.2f} | {r["categoria"]}')

print()
print('=== dim_shipper ===')
for r in shipper:
    print(f'  {r["shipper_id"]} | {r["company_name"]:<22} | avg={r["avg_delivery_days"]} dias')

print()
print('=== fact_ventas metricas globales ===')
tv = sum(float(r['total_venta'] or 0) for r in fact)
tm = sum(float(r['margen'] or 0) for r in fact)
print(f'  Total ventas   : ${tv:>12,.2f}')
print(f'  Total margen   : ${tm:>12,.2f}')
print(f'  Margen global  : {tm/tv*100:.1f}%')
print(f'  Ordenes unicas : {len(set(r["order_id"] for r in fact))}')
print(f'  Lineas fact    : {len(fact)}')

print()
print('=== CALIDAD fact_ventas ===')
issues = 0
v = sum(1 for r in fact if not r['fecha_id'])
print(f'  fecha_id nulo        : {v}  {"OK" if v==0 else "ERROR"}')
issues += v
v = sum(1 for r in fact if not r['cliente_id'])
print(f'  cliente_id nulo      : {v}  {"OK" if v==0 else "ERROR"}')
issues += v
v = sum(1 for r in fact if float(r['total_venta'] or 0) <= 0)
print(f'  total_venta <= 0     : {v}  {"OK" if v==0 else "ERROR"}')
issues += v
v = sum(1 for r in fact if r['margen'] and float(r['margen']) < 0)
print(f'  margen negativo      : {v}  {"OK" if v==0 else "WARN"}')
v = sum(1 for r in fact if r['descuento'] and (float(r['descuento'])<0 or float(r['descuento'])>1))
print(f'  descuento fuera[0,1] : {v}  {"OK" if v==0 else "ERROR"}')
issues += v
v = sum(1 for r in fact if not r['dias_entrega'])
print(f'  sin dias_entrega     : {v}  (pedidos pendientes de envio - normal)')

print()
print('=== INTEGRIDAD REFERENCIAL ===')
fecha_ids   = {r['fecha_id']    for r in fecha}
cliente_ids = {r['cliente_id']  for r in cliente}
emp_ids     = {str(r['empleado_id']) for r in empleado}
prod_ids    = {str(r['producto_id']) for r in producto}
ship_ids    = {str(r['shipper_id'])  for r in shipper}
terr_ids    = {r['territorio_id']    for r in terr}

checks = [
    ('fact -> dim_fecha',      sum(1 for r in fact if r['fecha_id'] and r['fecha_id'] not in fecha_ids)),
    ('fact -> dim_cliente',    sum(1 for r in fact if r['cliente_id'] and r['cliente_id'] not in cliente_ids)),
    ('fact -> dim_empleado',   sum(1 for r in fact if r['empleado_id'] and str(r['empleado_id']) not in emp_ids)),
    ('fact -> dim_producto',   sum(1 for r in fact if r['producto_id'] and str(r['producto_id']) not in prod_ids)),
    ('fact -> dim_shipper',    sum(1 for r in fact if r['shipper_id'] and str(r['shipper_id']) not in ship_ids)),
    ('fact -> dim_territorio', sum(1 for r in fact if r['territorio_id'] and r['territorio_id'] not in terr_ids)),
]
for label, v in checks:
    print(f'  {label:<28}: {v}  {"OK" if v==0 else "ERROR"}')
    issues += v

print()
print('=== SEGMENTOS clientes ===')
for k, v in sorted(Counter(r['segmento_cliente'] for r in cliente).items()):
    print(f'  {k:<12}: {v} clientes')

print()
print('=== ZONAS territorios ===')
for k, v in sorted(Counter(r['zona'] for r in terr).items()):
    print(f'  {k:<30}: {v}')

print()
print('=== dim_metas_empleado ===')
for k, v in Counter(r['categoria_meta'] for r in metas).items():
    print(f'  {k:<12}: {v} registros (empleados x trimestres x anos)')

print()
if issues == 0:
    print('RESULTADO FINAL: TODOS LOS CSV SON VALIDOS')
else:
    print(f'RESULTADO FINAL: {issues} PROBLEMAS ENCONTRADOS')
