# ETL Northwind → Staging Area
**Proyecto BI — Base de Datos Avanzadas**
Herramienta ETL: **Python + SQLAlchemy + Pandas**

---

## 1. Arquitectura del Pipeline

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   FUENTE         │    │   EXTRACCIÓN     │    │  TRANSFORMACIÓN  │    │    STAGING       │
│                  │    │                  │    │                  │    │                  │
│  Northwind DB    │───▶│  extract.py      │───▶│  transform.py    │───▶│  MySQL/PG/MSSQL  │
│  (SQL Server /   │    │  SQL explícito   │    │  14 reglas TR    │    │  8 tablas STG_*  │
│   MS Access)     │    │  por tabla       │    │  validate.py     │    │  + campos deriv. │
└──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
```

**Módulos:**
| Archivo | Responsabilidad |
|---|---|
| `pipeline.py` | Orquestador principal |
| `etl/config.py` | Parámetros de conexión y configuración |
| `etl/db_connection.py` | Fábrica de engines SQLAlchemy |
| `etl/extract.py` | Extracción por tabla con SQL explícito |
| `etl/transform.py` | 14 transformaciones de limpieza y derivación |
| `etl/validate.py` | Validaciones de calidad (reglas RQ-*) |
| `etl/load.py` | Carga por batches al staging |
| `etl/logger_setup.py` | Logging a consola y archivo |
| `sql/create_staging.sql` | DDL completo de la staging area |

---

## 2. Requisitos del Sistema

- Python **3.10+**
- Base de datos **MySQL 8+** (o PostgreSQL / SQL Server)
- Acceso de red a la BD Northwind fuente
- 50 MB de espacio en disco para logs

### Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 3. Instalación y Configuración

### Paso 1 — Crear la Staging Area
```sql
-- En MySQL Workbench / DBeaver / consola mysql:
source sql/create_staging.sql;
```

### Paso 2 — Configurar conexiones
Editar `etl/config.py`:

```python
# Fuente (Northwind)
SOURCE_CONFIG = {
    "engine":   "mssql",           # mssql | mysql | postgresql
    "host":     "localhost",
    "port":     1433,
    "database": "Northwind",
    "username": "sa",
    "password": "TuPassword",
    "driver":   "ODBC Driver 17 for SQL Server",
}

# Destino (Staging)
STAGING_CONFIG = {
    "engine":   "mysql",
    "host":     "localhost",
    "port":     3306,
    "database": "northwind_staging",
    "username": "etl_user",
    "password": "etl_password",
}
```

### Paso 3 — Crear usuario MySQL de staging (opcional)
```sql
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'etl_password';
GRANT ALL PRIVILEGES ON northwind_staging.* TO 'etl_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 4. Ejecución

### Ejecución completa (extracción + transformación + carga)
```bash
python pipeline.py
```

### Modos de operación
```bash
python pipeline.py --only-extract    # Solo extrae datos (diagnóstico)
python pipeline.py --dry-run         # Extrae y transforma, pero NO carga
python pipeline.py --skip-validate   # Omite validaciones de calidad
```

### Salida esperada (consola)
```
=================================================================
  PIPELINE ETL — NORTHWIND → STAGING AREA
  Inicio: 2026-05-30 10:00:00
=================================================================

[1/4] CONEXIONES
[OK] Conexión FUENTE (Northwind) establecida.
[OK] Conexión DESTINO (Staging) establecida.

[2/4] EXTRACCIÓN
  Extrayendo: Categories → 8 registros
  Extrayendo: Suppliers  → 29 registros
  ...
  Extrayendo: Order Details → 2155 registros

[3/4] TRANSFORMACIÓN
  Transformando: Products...
  Transformando: Orders...
  ...

[3b] VALIDACIÓN DE CALIDAD
✅ Validación completada: sin problemas de calidad detectados

[4/4] CARGA AL STAGING
  ✅ Categories    → STG_CATEGORIES:    8 registros
  ✅ Suppliers     → STG_SUPPLIERS:    29 registros
  ✅ Orders        → STG_ORDERS:      830 registros
  ✅ Order Details → STG_ORDER_DETAILS: 2,155 registros
  ...

=================================================================
  RESUMEN FINAL
=================================================================
  Tablas extraídas :  8/8
  Registros cargados: 3,282
  Duración total    : 12s
=================================================================
```

---

## 5. Transformaciones Aplicadas

| Código | Nombre | Tablas Afectadas |
|---|---|---|
| TR-001 | Normalización texto (UPPER+TRIM) | Todas |
| TR-002 | Cast MONEY → DECIMAL(18,2) | Products, Orders, Order Details |
| TR-003 | Cast DATETIME → DATE | Orders, Employees |
| TR-004 | Cast BIT → TINYINT | Products (Discontinued) |
| TR-005 | Cast REAL → DECIMAL(5,2) | Order Details (Discount) |
| TR-006 | Valor neto de venta | Order Details → STG_ValorNeto |
| TR-007 | Días de entrega | Orders → STG_DiasEntrega |
| TR-008 | Indicador puntualidad | Orders → STG_EntregaPuntual |
| TR-009 | Alerta bajo reorden | Products → STG_AlertaBajoReorden |
| TR-010 | Stock proyectado | Products → STG_StockProyectado |
| TR-013 | Nombre completo empleado | Employees → FullName |
| TR-014 | Filtro Discontinued | Products (conserva ambos para P08) |

---

## 6. Logs

Los logs se guardan en `logs/etl_run_YYYYMMDD_HHMMSS.log`.
Cada ejecución genera un archivo nuevo (rotativo, máx. 5 MB × 3 backups).

---

## 7. Verificar la Carga

```sql
-- Contar registros en staging
SELECT 'STG_CATEGORIES'    AS Tabla, COUNT(*) AS Registros FROM stg_categories
UNION ALL SELECT 'STG_SUPPLIERS',   COUNT(*) FROM stg_suppliers
UNION ALL SELECT 'STG_SHIPPERS',    COUNT(*) FROM stg_shippers
UNION ALL SELECT 'STG_CUSTOMERS',   COUNT(*) FROM stg_customers
UNION ALL SELECT 'STG_EMPLOYEES',   COUNT(*) FROM stg_employees
UNION ALL SELECT 'STG_PRODUCTS',    COUNT(*) FROM stg_products
UNION ALL SELECT 'STG_ORDERS',      COUNT(*) FROM stg_orders
UNION ALL SELECT 'STG_ORDER_DETAILS', COUNT(*) FROM stg_order_details;

-- Verificar campos derivados
SELECT ProductName, UnitsInStock, ReorderLevel,
       STG_AlertaBajoReorden, STG_StockProyectado
FROM stg_products WHERE STG_AlertaBajoReorden = 'ALERTA';

SELECT OrderID, OrderDate, ShippedDate,
       STG_DiasEntrega, STG_EntregaPuntual
FROM stg_orders WHERE STG_DiasEntrega IS NOT NULL
LIMIT 10;
```

---

## 8. Preguntas de Negocio Cubiertas

| P# | Pregunta | Tablas Staging |
|---|---|---|
| P1 | Ventas por periodo | STG_ORDERS + STG_ORDER_DETAILS |
| P2 | Clientes rentables Top 10 | + STG_CUSTOMERS |
| P3 | Productos más vendidos | + STG_PRODUCTS |
| P4 | Análisis por categorías | + STG_CATEGORIES |
| P5 | Eficiencia empleados | STG_ORDERS + STG_EMPLOYEES |
| P6 | Análisis de territorios | STG_ORDERS (ShipCountry) |
| P7 | Tiempos de entrega | STG_ORDERS (STG_DiasEntrega) |
| P8 | Margen rentabilidad | STG_ORDER_DETAILS (STG_ValorNeto) |
| P9 | Clientes inactivos | STG_ORDERS + STG_CUSTOMERS |
| P10 | Estacionalidad ventas | STG_ORDERS (OrderDate por mes/trim) |
