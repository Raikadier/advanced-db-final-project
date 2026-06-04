# Proyecto BI — Northwind Traders
### Base de Datos Avanzadas · Universidad Popular del Cesar

[![Python](https://img.shields.io/badge/ETL-Python_3.x-3776AB?style=flat&logo=python)](https://python.org)
[![MongoDB](https://img.shields.io/badge/DW-MongoDB-47A248?style=flat&logo=mongodb)](https://mongodb.com)
[![Power BI](https://img.shields.io/badge/BI-Power_BI_PBIP-F2C811?style=flat&logo=powerbi)](https://powerbi.microsoft.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Tabla de Contenidos

1. [Resumen del Proyecto](#1-resumen-del-proyecto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Estructura del Repositorio](#4-estructura-del-repositorio)
5. [Preguntas de Negocio](#5-preguntas-de-negocio)
6. [Fase 1 — Análisis Funcional](#6-fase-1--análisis-funcional)
7. [Fase 2 — ETL Python](#7-fase-2--etl-python)
8. [Fase 3 — Data Warehouse MongoDB](#8-fase-3--data-warehouse-mongodb)
9. [Fase 4 — Power BI (TMDL/PBIR)](#9-fase-4--power-bi-tmdlpbir)
10. [Generación de CSV sin infraestructura](#10-generación-de-csv-sin-infraestructura)
11. [Modelo Dimensional (Esquema Estrella)](#11-modelo-dimensional-esquema-estrella)
12. [Medidas DAX implementadas](#12-medidas-dax-implementadas)
13. [Diseño de las Visualizaciones](#13-diseño-de-las-visualizaciones)
14. [Errores Corregidos (Auditoría)](#14-errores-corregidos-auditoría)
15. [Prerrequisitos e Instalación](#15-prerrequisitos-e-instalación)
16. [Guía de Ejecución por Fase](#16-guía-de-ejecución-por-fase)
17. [Independencia entre Fases](#17-independencia-entre-fases)
18. [Punto Extra — Tabular SSAS](#18-punto-extra--tabular-ssas)
19. [Estado del Proyecto](#19-estado-del-proyecto)

---

## 1. Resumen del Proyecto

Proyecto de Business Intelligence sobre la base de datos **Northwind Traders** de Microsoft, con datos históricos de ventas del período **julio 1996 — mayo 1998**.

El pipeline completo transforma datos relacionales de un sistema OLTP en un **Data Warehouse dimensional** accesible desde Power BI, respondiendo 10 preguntas de negocio con dashboards interactivos.

### Equipo y Roles

| Rol | Responsabilidad |
|-----|-----------------|
| **Análisis Funcional** | Diseño del modelo dimensional, 10 preguntas de negocio, diccionario de datos |
| **ETL Python** | Pipeline de extracción, transformación y carga desde Northwind → Staging |
| **MongoDB DW** | Diseño e implementación del Data Warehouse NoSQL |
| **Power BI** | Modelo semántico TMDL, dashboards PBIR, validación y control de calidad |

---

## 2. Arquitectura del Sistema

```
┌──────────────┐     FASE 2          ┌──────────────┐     FASE 3          ┌──────────────┐
│  Northwind   │  ─────────────────► │   Staging    │  ─────────────────► │  MongoDB DW  │
│  SQL Server  │   ETL Python        │  SQL Server  │  northwind_sql_to   │  northwind_dw│
│  (fuente)    │   pipeline.py       │  northwind_  │  _mongodb.py        │  7 colecciones│
│  ~830 orders │                     │  staging     │                      │  ~2155 facts  │
└──────────────┘                     └──────────────┘                      └──────┬───────┘
                                                                                  │
                                                                         FASE 4   │ Import Mode
                                                                                  ▼
                                                                         ┌──────────────┐
                                                                         │  Power BI    │
                                                                         │  .pbip       │
                                                                         │  TMDL + PBIR │
                                                                         │  4 páginas   │
                                                                         │  22 medidas  │
                                                                         └──────────────┘
```

> **Nota importante:** Con **Import Mode** en Power BI, los datos se embeben en el `.pbip` tras una sola actualización. Después de eso, **no es necesario que ningún servidor esté corriendo** para ver los dashboards. El reporte es autocontenido.

### Alternativa sin infraestructura

Si no tienes MongoDB ni SQL Server disponibles, el script `generate_csvs.py` (incluido en este repositorio) lee directamente el archivo `northwind.sql` y genera los 8 CSV necesarios para Power BI en segundos, **sin instalar ningún servidor**.

---

## 3. Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Fuente de datos | Microsoft Northwind (SQL Server LocalDB) | SQL Server 2019+ |
| ETL | Python + pandas + SQLAlchemy + pyodbc | Python 3.x |
| Staging | SQL Server LocalDB | `northwind_staging` |
| Data Warehouse | MongoDB Community | `northwind_dw` |
| Visualización | Power BI Desktop (PBIP format) | Mayo 2026 |
| Modelo semántico | TMDL (Tabular Model Definition Language) | v1600 |
| Formato reporte | PBIR (Power BI Enhanced Report Format) | v3.3.0 |
| Control de versiones | Git + GitHub | — |

---

## 4. Estructura del Repositorio

```
advanced-db-final-project/
│
├── 📁 ETL_Base_ded_datos/                    # FASE 2 — Pipeline ETL
│   ├── northwind_etl_python/
│   │   └── northwind_etl/
│   │       ├── etl/
│   │       │   ├── config.py                 # Configuración conexiones y tablas
│   │       │   ├── extract.py                # Queries SQL de extracción (11 tablas)
│   │       │   ├── transform.py              # 14 transformaciones TR-001 a TR-014
│   │       │   ├── validate.py               # Reglas de calidad RQ-001 a RQ-022
│   │       │   ├── load.py                   # Carga por batch al staging
│   │       │   ├── db_connection.py          # Factory de conexiones SQLAlchemy
│   │       │   └── logger_setup.py           # Logging rotativo a archivo + consola
│   │       ├── pipeline.py                   # Orquestador principal del ETL
│   │       ├── requirements.txt              # Dependencias Python
│   │       └── sql/
│   │           └── create_staging.sql        # DDL del staging (MySQL/SQL Server)
│   └── scripteado/
│       ├── northwind.sql                     # Base de datos fuente completa (2MB)
│       └── Northwind_staging.sql             # Script staging para SQL Server
│
├── 📁 entreega preeparada/                   # FASE 3 — MongoDB DW
│   └── entreega preeparada/
│       ├── northwind_sql_to_mongodb.py       # Cargador del DW (lee del staging)
│       ├── northwind_dw_mongodb.js           # Schema mongosh + queries de validación
│       ├── Modelo_Dimensional_MongoDB_Northwind.docx
│       └── read me.txt                       # Instrucciones de ejecución
│
├── 📁 proyecto-bi/                           # FASE 4 — Power BI PBIP
│   ├── northwind_bi.pbip                     # Punto de entrada del proyecto
│   ├── northwind_bi.Report/                  # Definición del reporte (PBIR)
│   │   ├── definition.pbir                   # Referencia al SemanticModel
│   │   ├── StaticResources/SharedResources/
│   │   │   ├── BaseThemes/CY26SU05.json      # Tema base Microsoft
│   │   │   └── CustomThemes/BIBB.json        # Tema corporativo BIBB.PRO v2.05
│   │   └── definition/
│   │       ├── report.json                   # Config global + tema inyectado
│   │       ├── version.json
│   │       └── pages/
│   │           ├── pages.json                # Orden de las 4 páginas
│   │           ├── e3e43335c708953e4407/     # Página 1: Resumen Ejecutivo
│   │           ├── d72257249741148631d0/     # Página 2: Clientes y Geografía
│   │           ├── d9ff3d19e960c247b7bd/     # Página 3: Operaciones y Logística
│   │           └── ad7a10cd5c1f2cdd218f/     # Página 4: Desempeño y Auditoría
│   └── northwind_bi.SemanticModel/           # Modelo semántico (TMDL)
│       ├── definition.pbism
│       └── definition/
│           ├── database.tmdl                 # compatibilityLevel: 1600
│           ├── model.tmdl                    # 8 tablas + 22 medidas + 7 relaciones
│           └── cultures/es-CO.tmdl
│
├── 📁 csvs/                                  # CSV del DW (generados automáticamente)
│   ├── fact_ventas.csv                       # 2155 filas — tabla de hechos principal
│   ├── dim_fecha.csv                         # 672 filas — 1996-07-04 → 1998-05-06
│   ├── dim_cliente.csv                       # 91 filas
│   ├── dim_empleado.csv                      # 9 filas
│   ├── dim_producto.csv                      # 77 filas
│   ├── dim_shipper.csv                       # 3 filas
│   ├── dim_territorio.csv                    # 69 filas
│   └── dim_metas_empleado.csv                # 108 filas (9 emp × 3 años × 4 trim)
│
├── generate_csvs.py                          # ⚡ Genera todos los CSV desde northwind.sql
├── verify_csvs.py                            # ✅ Valida integridad de los CSV
├── Diccionario_Datos_Northwind_BI.xlsx       # Diccionario de campos y reglas de calidad
├── Entregable1_Analisis_Northwind.docx       # Análisis funcional Fase 1
├── Reporte_Errores_Corregidos.docx           # Auditoría técnica del proyecto
├── Power BI Theme by BIBB.json               # Tema visual corporativo
├── prompt_fase1_analisis.txt                 # Guía de correcciones para Fase 1
├── prompt_fase2_etl.txt                      # Guía de correcciones para Fase 2
├── prompt_fase3_mongodb.txt                  # Guía de correcciones para Fase 3
├── prompt_fase4_powerbi.txt                  # Guía de desarrollo para Fase 4
├── .gitignore
└── README.md
```

---

## 5. Preguntas de Negocio

El proyecto responde las siguientes 10 preguntas, cada una implementada como medidas DAX y visualizaciones específicas:

| # | Pregunta | Página del Dashboard |
|---|---|---|
| **P1** | ¿Cómo han evolucionado las ventas por mes y año? | Resumen Ejecutivo |
| **P2** | ¿Cuáles son los 10 clientes que más ingresos generan y cómo ha variado su comportamiento? | Clientes y Geografía |
| **P3** | ¿Cuáles son los productos con mayor volumen y su contribución al total de ingresos? | Productos y Categorías |
| **P4** | ¿Qué categorías generan mayores ingresos y cuál es su tendencia histórica? | Productos y Categorías |
| **P5** | ¿Qué empleados logran mayor facturación y cuál es su tasa de cumplimiento vs. metas? | Desempeño y Auditoría |
| **P6** | ¿Qué regiones/países generan más ingresos y cuáles tienen oportunidades de crecimiento? | Clientes y Geografía |
| **P7** | ¿Cuál es el tiempo promedio de entrega y cómo varía por región o transportista? | Operaciones y Logística |
| **P8** | ¿Cuál es la rentabilidad por producto y cómo contribuye a la utilidad total? | Desempeño y Auditoría |
| **P9** | ¿Qué clientes han dejado de comprar y qué impacto tiene en las ventas? | Clientes y Geografía |
| **P10** | ¿Existen patrones estacionales en las ventas y cómo afectan el inventario? | Resumen Ejecutivo |

---

## 6. Fase 1 — Análisis Funcional

### Modelo Dimensional — Esquema Estrella

El diseño sigue el patrón **Star Schema** con una tabla de hechos central y 7 dimensiones:

```
                    dim_fecha ◄───────────────────────────────────────┐
                        │                                              │
                    dim_cliente ◄─────────────────────────────────┐   │
                        │                                          │   │
dim_metas_empleado ─► dim_empleado ◄───────────────────────────┐  │   │
                        │                                       │  │   │
                    dim_producto ◄──────────────────────────┐   │  │   │
                        │                                   │   │  │   │
                    dim_shipper ◄───────────────────────┐   │   │  │   │
                        │                               │   │   │  │   │
                    dim_territorio ◄─────────────────┐  │   │   │  │   │
                                                     │  │   │   │  │   │
                                              ┌──────▼──▼───▼───▼──▼───▼──────┐
                                              │         fact_ventas            │
                                              │  order_detail_id  (PK)        │
                                              │  order_id                     │
                                              │  fecha_id         (FK)        │
                                              │  fecha_entrega_id (FK, inact) │
                                              │  cliente_id       (FK)        │
                                              │  empleado_id      (FK)        │
                                              │  producto_id      (FK)        │
                                              │  shipper_id       (FK)        │
                                              │  territorio_id    (FK)        │
                                              │  cantidad, unit_price         │
                                              │  descuento, freight           │
                                              │  subtotal, total_venta        │
                                              │  costo_total, margen          │
                                              │  margen_pct                   │
                                              │  dias_entrega                 │
                                              │  entrega_puntual              │
                                              └────────────────────────────────┘
```

### Supuesto de negocio documentado

> **Northwind no tiene costos de adquisición reales.** Se utiliza la siguiente aproximación documentada:
> ```
> costo_adquisicion = UnitPrice_historico × 0.60
> costo_total       = cantidad × costo_adquisicion
> margen            = total_venta − costo_total
> margen_pct        = (margen / total_venta) × 100
> ```

### dim_metas_empleado (tabla auxiliar — no existe en Northwind)

Para responder P5, se creó una tabla de metas trimestrales por cargo:

| Cargo | Meta por trimestre |
|---|---|
| Vice President, Sales | $18,000 |
| Sales Manager | $15,000 |
| Sales Representative | $12,000 |

---

## 7. Fase 2 — ETL Python

### Tablas extraídas (11 tablas)

```
Categories → STG_CATEGORIES
Suppliers  → STG_SUPPLIERS
Shippers   → STG_SHIPPERS
Customers  → STG_CUSTOMERS
Employees  → STG_EMPLOYEES
Region              → STG_REGION              ← análisis territorial (P6)
Territories         → STG_TERRITORIES
EmployeeTerritories → STG_EMPLOYEE_TERRITORIES
Products   → STG_PRODUCTS
Orders     → STG_ORDERS
Order Details → STG_ORDER_DETAILS
```

### Transformaciones aplicadas (TR-001 a TR-014)

| ID | Transformación | Campo/Tabla |
|---|---|---|
| TR-001 | Normalización texto (UPPER + TRIM) | Todos los campos de texto |
| TR-002 | MONEY → DECIMAL(18,2) | UnitPrice, Freight |
| TR-003 | DATETIME → DATE (solo fecha) | OrderDate, ShippedDate, HireDate |
| TR-004 | BIT → int | Products.Discontinued |
| TR-005 | REAL → DECIMAL(5,2) | Order Details.Discount |
| TR-006 | Valor neto de venta (columna derivada) | `STG_ValorNeto = UnitPrice × Qty × (1 - Discount)` |
| TR-007 | Días de entrega (columna derivada) | `STG_DiasEntrega = ShippedDate − OrderDate` |
| TR-008 | Indicador de puntualidad | `STG_EntregaPuntual = 1 si ShippedDate ≤ RequiredDate` |
| TR-009 | Alerta bajo reorden | `STG_AlertaBajoReorden = ALERTA/OK` |
| TR-010 | Stock proyectado | `STG_StockProyectado = UnitsInStock + UnitsOnOrder` |
| TR-013 | Nombre completo empleado | `FullName = LastName + ", " + FirstName` |
| TR-014 | Flag Discontinued | Filtro informativo (no elimina) |

### Reglas de calidad (RQ-001 a RQ-022)

- **RQ-001–004**: Integridad referencial (OrderID, ProductID, CustomerID, CategoryID)
- **RQ-005–007**: Completitud (OrderDate, UnitPrice, Quantity no nulos)
- **RQ-008**: Discount en rango [0.0, 1.0]
- **RQ-009–010**: Consistencia temporal (ShippedDate ≥ OrderDate)
- **RQ-012–014**: Unicidad de PKs

### Ejecución

```bash
cd ETL_Base_ded_datos/northwind_etl_python/northwind_etl/

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pipeline completo
python pipeline.py

# Modos alternativos
python pipeline.py --only-extract    # solo extracción (debug)
python pipeline.py --skip-validate   # sin validaciones
python pipeline.py --dry-run         # sin carga al staging
```

### Resultado esperado

```
[1/4] CONEXIONES     ✅ Northwind + Staging
[2/4] EXTRACCIÓN     ✅ 11/11 tablas
[3/4] TRANSFORMACIÓN ✅ 11 tablas procesadas
[3b] VALIDACIÓN      ✅ 0 problemas detectados
[4/4] CARGA          ✅ ~3,600 registros totales al staging
```

### Bug crítico corregido — Type mismatch pd.NA

**Problema:** `transform.py` inicializaba `STG_DiasEntrega` y `STG_EntregaPuntual` con `pd.NA`, que mezclado con `numpy.int64` generaba `dtype=object`. SQL Server rechazaba el INSERT en columnas `INT/BIT`.

**Corrección:**
```python
# ANTES (incorrecto):
out["STG_DiasEntrega"] = pd.NA

# DESPUÉS (correcto):
out["STG_DiasEntrega"] = None
out.loc[mask, "STG_DiasEntrega"] = (ShippedDate - OrderDate).dt.days
out["STG_DiasEntrega"] = out["STG_DiasEntrega"].astype(pd.Int32Dtype())
```

---

## 8. Fase 3 — Data Warehouse MongoDB

### Colecciones del DW

| Colección | Documentos | Descripción |
|---|---|---|
| `fact_ventas` | ~2,155 | Tabla de hechos — granularidad: línea de pedido |
| `dim_fecha` | ~672 | Calendario diario Jul 1996 → May 1998 |
| `dim_cliente` | 91 | Clientes + segmentación Premium/Regular/Inactivo/Nuevo |
| `dim_empleado` | 9 | Empleados de Northwind |
| `dim_producto` | 77 | Catálogo con costo estimado (60% del precio) |
| `dim_shipper` | 3 | Transportistas + promedio de días de entrega |
| `dim_territorio` | ~69 | País × Ciudad + zona geográfica |
| `dim_metas_empleado` | 108 | Metas trimestrales por cargo (auxiliar) |

### Ejecución

```bash
# Prerrequisito: MongoDB corriendo en localhost:27017
pip install pymongo pyodbc pandas

# Cargar DW desde staging (requiere ETL ejecutado antes)
cd "entreega preeparada/entreega preeparada/"
python northwind_sql_to_mongodb.py

# Verificar en MongoDB Compass: mongodb://localhost:27017
```

### Índices principales

- `fact_ventas`: índice único en `order_detail_id`, índices en todas las FKs
- `dim_fecha`: índice único en `fecha_id`, índice compuesto `(anio, mes)`
- `dim_metas_empleado`: índice único compuesto `(empleado_id, anio, trimestre)`

### Bugs críticos corregidos

1. **Bypass del Staging con regex:** el script original leía `northwind.sql` con regex en lugar del staging — corregido para usar `pyodbc` sobre `northwind_staging`.
2. **Datos sintéticos con `random()`:** `generar_orders()` inventaba 830 órdenes — eliminado, ahora lee `STG_ORDERS` real.
3. **Segmentación por Freight:** usaba el flete en lugar de ventas reales para clasificar clientes — corregido para usar `STG_ValorNeto`.

---

## 9. Fase 4 — Power BI (TMDL/PBIR)

### Formato del proyecto

El proyecto está guardado como **Power BI Project (PBIP)** con:
- **SemanticModel en TMDL** (Tabular Model Definition Language) — `model.tmdl`
- **Report en PBIR** (Power BI Enhanced Report Format) — `definition/pages/`

Esto permite control de versiones con Git, edición de texto plano y colaboración.

### Tema visual

Se aplica el tema **BIBB.PRO v2.05** con paleta corporativa:
- Colores primarios: `#093824` (verde oscuro), `#001f54` (navy), `#4c956c` (verde)
- Fuente global: Arial
- Fondo de página: `#F1F3F6`

### Páginas del reporte

| Página | GUID | Preguntas |
|---|---|---|
| **Resumen Ejecutivo** | `e3e43335c708953e4407` | P1 + P10 |
| **Análisis de Clientes y Geografía** | `d72257249741148631d0` | P2 + P6 + P9 |
| **Operaciones y Logística** | `d9ff3d19e960c247b7bd` | P3 + P4 + P7 |
| **Desempeño y Auditoría** | `ad7a10cd5c1f2cdd218f` | P5 + P8 |

### Cómo abrir el proyecto

```
1. Abrir Power BI Desktop (May 2026 o superior)
2. File > Open > Browse > seleccionar proyecto-bi/northwind_bi.pbip
3. Si hay aviso de actualización de datos → Actualizar ahora
4. El reporte carga con datos del modelo semántico
```

> **Prerrequisito:** Las queries M del `model.tmdl` apuntan a `(localdb)\MSSQLLocalDB` base de datos `Northwind`, **O** se pueden redirigir a los CSV de la carpeta `csvs/` (ver sección 10).

---

## 10. Generación de CSV sin infraestructura

### ¿Para qué sirve?

Si **no tienes** SQL Server, MongoDB, ni el ETL corriendo, el script `generate_csvs.py` genera todos los CSV del DW directamente desde `northwind.sql` usando solo Python.

```bash
# Desde la raíz del repositorio
python generate_csvs.py
```

**Salida:** carpeta `csvs/` con 8 archivos listos para importar en Power BI.

### Verificación de los CSV

```bash
python verify_csvs.py
```

**Resultado esperado:**
```
RESULTADO FINAL: TODOS LOS CSV SON VALIDOS

Métricas verificadas:
  ✅ 0 errores de integridad referencial (6 relaciones FK)
  ✅ 0 valores nulos en campos críticos
  ✅ 0 descuentos fuera del rango [0,1]
  ⚠️ 11 márgenes negativos (normal — descuentos altos en algunos productos)
  ℹ️ 73 pedidos sin fecha de envío (histórico: pedidos nunca enviados)
```

### Métricas de los datos Northwind 1996-1998

| Métrica | Valor |
|---|---|
| Total ventas | **$1,265,793** |
| Total margen | **$396,177** |
| Margen global | **31.3%** |
| Órdenes únicas | **830** |
| Líneas de detalle | **2,155** |
| Rango temporal | Jul 4, 1996 → May 6, 1998 |
| Top cliente | QUICK-Stop — $110,277 |
| Empleados | 9 (6 Sales Rep, 1 Manager, 1 VP, 1 Coordinator) |

---

## 11. Modelo Dimensional (Esquema Estrella)

### fact_ventas — Granularidad: 1 fila = 1 línea de pedido

| Campo | Tipo | Descripción |
|---|---|---|
| `order_detail_id` | string PK | `OrderID-ProductID` |
| `order_id` | int | Número de orden |
| `fecha_id` | string FK | YYYYMMDD → dim_fecha |
| `fecha_entrega_id` | string FK | YYYYMMDD → dim_fecha (relación inactiva) |
| `cliente_id` | string FK | → dim_cliente |
| `empleado_id` | int FK | → dim_empleado |
| `producto_id` | int FK | → dim_producto |
| `shipper_id` | int FK | → dim_shipper |
| `territorio_id` | string FK | → dim_territorio |
| `cantidad` | int | Unidades vendidas |
| `unit_price` | float | Precio facturado (≠ precio catálogo) |
| `descuento` | float | Descuento en [0,1] |
| `freight` | float | Costo de flete |
| `subtotal` | float | `unit_price × cantidad` |
| `total_venta` | float | `subtotal × (1 - descuento)` |
| `costo_total` | float | `unit_price × 0.60 × cantidad` |
| `margen` | float | `total_venta - costo_total` |
| `margen_pct` | float | `(margen / total_venta) × 100` |
| `dias_entrega` | int | `ShippedDate - OrderDate` |
| `entrega_puntual` | bool | `1 si ShippedDate ≤ RequiredDate` |

### Relaciones activas

```
fact_ventas.fecha_id       → dim_fecha.fecha_id        (Many-to-One)
fact_ventas.cliente_id     → dim_cliente.cliente_id    (Many-to-One)
fact_ventas.empleado_id    → dim_empleado.empleado_id  (Many-to-One)
fact_ventas.producto_id    → dim_producto.producto_id  (Many-to-One)
fact_ventas.shipper_id     → dim_shipper.shipper_id    (Many-to-One)
fact_ventas.territorio_id  → dim_territorio.territorio_id (Many-to-One)
```

### Relación inactiva

```
fact_ventas.fecha_entrega_id → dim_fecha.fecha_id   (inactiva — se activa con USERELATIONSHIP en DAX)
```

---

## 12. Medidas DAX implementadas

Todas las medidas están en la tabla `_Medidas`, organizadas por pregunta de negocio:

### P1 — Ventas por periodo
```dax
[Total Ventas]         = SUM(fact_ventas[total_venta])
[Num Ordenes]          = DISTINCTCOUNT(fact_ventas[order_id])
[Ventas YTD]           = CALCULATE([Total Ventas], DATESYTD(dim_fecha[fecha_completa]))
[Ventas Año Anterior]  = CALCULATE([Total Ventas], SAMEPERIODLASTYEAR(dim_fecha[fecha_completa]))
[Variación YoY %]      = DIVIDE([Total Ventas] - [Ventas Año Anterior], [Ventas Año Anterior]) × 100
```

### P2 — Clientes rentables
```dax
[Clientes Activos]     = DISTINCTCOUNT(fact_ventas[cliente_id])
[Ventas por Cliente]   = DIVIDE([Total Ventas], [Clientes Activos])
[Ranking Cliente]      = RANKX(ALL(dim_cliente[company_name]), [Total Ventas], , DESC, DENSE)
```

### P3 — Productos más vendidos
```dax
[Unidades Vendidas]        = SUM(fact_ventas[cantidad])
[% Contribución Ventas]    = DIVIDE([Total Ventas], CALCULATE([Total Ventas], ALL(dim_producto))) × 100
```

### P5 — Eficiencia empleados
```dax
[Meta Periodo]         = SUMX(FILTER(dim_metas_empleado, ...), dim_metas_empleado[meta_ventas_usd])
[% Cumplimiento Meta]  = DIVIDE([Total Ventas], [Meta Periodo]) × 100
[Ranking Empleado]     = RANKX(ALL(dim_empleado[full_name]), [Total Ventas], , DESC, DENSE)
```

### P7 — Tiempos de entrega
```dax
[Avg Dias Entrega]     = AVERAGEX(FILTER(fact_ventas, NOT ISBLANK([dias_entrega])), fact_ventas[dias_entrega])
[% Entregas Puntuales] = DIVIDE(COUNTROWS(FILTER(fact_ventas, [entrega_puntual] = TRUE())), [Pedidos Entregados]) × 100
[Pedidos Entregados]   = COUNTROWS(FILTER(fact_ventas, NOT ISBLANK(fact_ventas[shipped_date])))
[Pedidos Pendientes]   = COUNTROWS(FILTER(fact_ventas, ISBLANK(fact_ventas[shipped_date])))
```

### P8 — Margen de rentabilidad
```dax
[Total Margen]             = SUM(fact_ventas[margen])
[Total Costo]              = SUM(fact_ventas[costo_total])
[% Margen Promedio]        = DIVIDE([Total Margen], [Total Ventas]) × 100
[Ranking Margen Producto]  = RANKX(ALL(dim_producto[product_name]), [Total Margen], , DESC, DENSE)
```

### P9 — Clientes inactivos
```dax
[Última Compra Cliente] = CALCULATE(MAX(fact_ventas[order_date]), ALLEXCEPT(dim_cliente, dim_cliente[cliente_id]))
[Días Sin Comprar]      = DATEDIFF([Última Compra Cliente], MAX(fact_ventas[order_date]), DAY)
[Es Cliente Inactivo]   = IF([Días Sin Comprar] > 365, "Inactivo", "Activo")
```

### P10 — Estacionalidad
```dax
[Ventas por Trimestre]           = CALCULATE([Total Ventas], ALLEXCEPT(dim_fecha, dim_fecha[anio], dim_fecha[trimestre]))
[Variación vs Trimestre Anterior] = DIVIDE([Total Ventas] - CALCULATE([Total Ventas], DATEADD(dim_fecha[fecha_completa], -1, QUARTER)), ...) × 100
[Índice Estacionalidad]           = DIVIDE([Total Ventas], AVERAGEX(ALL(dim_fecha[trimestre]), CALCULATE([Total Ventas])))
```

---

## 13. Diseño de las Visualizaciones

### Página 1 — Resumen Ejecutivo (P1 + P10)

```
┌─────────────────────────────────────────────────────────────┐
│  BANNER: "Northwind BI · Resumen Ejecutivo"    [Año][Trim]  │
├────────────┬────────────┬────────────┬────────────────────── │
│ Total       │ Órdenes    │ % Margen   │ Clientes Activos      │
│ Ventas      │ Únicas     │ Promedio   │                       │
├────────────┴────────────┴────────────┴──────────────────────┤
│  P1 → Gráfico de Líneas: "Evolución Ventas Mensuales"        │
│       Eje X: nombre_mes | Eje Y: Total Ventas                │
│       Leyenda: año (3 líneas: 1996, 1997, 1998)              │
├────────────────────────────┬────────────────────────────────┤
│ P10 → Matrix (mapa calor)  │ P10 → Barras Agrupadas          │
│ "Ventas por Trim × Año"    │ "Ventas Trimestrales"           │
│ Filas: Trimestre 1-4       │ Eje X: nombre_mes               │
│ Cols: anio                 │ Eje Y: Total Ventas             │
└────────────────────────────┴────────────────────────────────┘
```

### Página 2 — Clientes y Geografía (P2 + P6 + P9)

```
┌─────────────────────────────────────────────────────────────┐
│  BANNER: "Clientes y Territorios"   [País][Segmento][Año]   │
├─────────────────────────┬────────────────────────────────── │
│ P2 → Barras Horiz.      │ P6 → Mapa Coroplético             │
│ "Top 10 Clientes"       │ "Ingresos por País"               │
│ Color: segmento_cliente │ Tamaño/Color: Total Ventas        │
├─────────────────────────┼────────────────────────────────── │
│ P2 → Tabla Detallada    │ P6 → Barras: Ventas por Zona      │
│ Cliente│Ventas│Segmento │                                   │
├─────────────────────────┴────────────────────────────────── │
│ P9 → Tabla: "Clientes con Actividad en Declive"              │
│ Cliente │ Última Compra │ Días Sin Comprar │ Ventas Hist.    │
└─────────────────────────────────────────────────────────────┘
```

### Página 3 — Operaciones y Logística (P3 + P4 + P7)

```
┌─────────────────────────────────────────────────────────────┐
│  BANNER: "Productos y Logística"        [Categoría][Año]    │
├─────────────────────────┬────────────────────────────────── │
│ P3 → Barras Horiz.      │ P4 → Donut                        │
│ "Top 10 Productos"      │ "Ingresos por Categoría"          │
│ Eje Y: product_name     │ Etiquetas: nombre + %             │
├─────────────────────────┴────────────────────────────────── │
│ P4 → Área Apilada: "Tendencia Histórica por Categoría"       │
├─────────────────────────┬────────────────────────────────── │
│ P7 → KPI Cards          │ P7 → Barras Horiz.                │
│ Avg Días / % Puntuales  │ "Días Entrega por Transportista"  │
└─────────────────────────┴────────────────────────────────── │
```

### Página 4 — Desempeño y Auditoría (P5 + P8)

```
┌─────────────────────────────────────────────────────────────┐
│  BANNER: "Desempeño y Rentabilidad"    [Empleado][Año][Trim]│
├─────────────────────────┬────────────────────────────────── │
│ P5 → Barras Agrupadas   │ P8 → Dispersión (Scatter)         │
│ Ventas Reales vs Meta   │ Eje X: Total Ventas               │
│ Color: full_name        │ Eje Y: % Margen                   │
│                         │ Tamaño: Unidades Vendidas         │
├─────────────────────────┼────────────────────────────────── │
│ P5 → Tabla              │ P8 → Tabla                        │
│ Empleado│Ventas│%Cumpl  │ Producto│Ventas│Margen│%Margen    │
└─────────────────────────┴────────────────────────────────── │
```

---

## 14. Errores Corregidos (Auditoría)

Durante el desarrollo se realizó una auditoría técnica completa. Los hallazgos y correcciones se documentan en `Reporte_Errores_Corregidos.docx`.

### Resumen de correcciones

| ID | Fase | Severidad | Error | Corrección |
|---|---|---|---|---|
| F2-01 | ETL Python | **CRÍTICO** | `pd.NA` type mismatch en `STG_DiasEntrega` → INSERT fallaba | `None` + `pd.Int32Dtype()` |
| F2-02 | ETL Python | **CRÍTICO** | Tablas territoriales (Region, Territories, EmployeeTerritories) no extraídas | Añadidas a `SOURCE_TABLES` y `TABLE_MAP` |
| F2-03 | ETL Python | MENOR | `DELETE FROM` en lugar de `TRUNCATE TABLE` | Reemplazado por `TRUNCATE TABLE` (O(1)) |
| F3-01 | MongoDB | **CRÍTICO** | Script leía `northwind.sql` con regex en lugar del staging | Reemplazado por `read_staging()` con `pyodbc` |
| F3-02 | MongoDB | **CRÍTICO** | Función `generar_orders()` con `random()` creaba datos falsos | Eliminada — lee `STG_ORDERS` real |
| F3-03 | MongoDB | MEDIO | Segmentación de clientes usaba `Freight` en lugar de ventas reales | Usa `STG_ValorNeto` con cruce de details |
| F3-04 | MongoDB | MEDIO | `dim_metas_empleado` no existía | Nueva función `build_dim_metas_empleado()` |
| F4-01 | TMDL | SINTAXIS | `ref cultureInfo` indentado dentro del bloque `model` | Movido al nivel top-level |
| F4-02 | TMDL | SINTAXIS | `annotation:` con dos puntos (sintaxis YAML incorrecta) | Eliminado, reemplazado por comentario `///` |
| F4-03 | TMDL | SINTAXIS | Línea vacía entre bloque `///` y declaración | Eliminada |
| F4-04 | TMDL | SINTAXIS | `fromTable`/`toTable` no existen en TMDL | `fromColumn: tabla.columna` |
| F4-05 | TMDL | SINTAXIS | `relationship` sin nombre (objeto nombrado obligatorio) | Añadido nombre a cada relación |
| F4-06 | TMDL | SEMÁNTICO | `sourceColumn: [fecha_id]` con brackets (sintaxis DAX, no TMDL) | `sourceColumn: fecha_id` |
| F4-07 | TMDL | M Engine | `\MSSQLLocalDB` en string M → secuencia de escape inválida | `\\MSSQLLocalDB` (backslash doble) |
| F4-08 | TMDL | SEMÁNTICO | Relación desde tabla calculada → column ID inválido | Relación eliminada (la medida usa FILTER explícito) |

---

## 15. Prerrequisitos e Instalación

### Opción A — Pipeline completo (ETL + MongoDB)

```
✅ Python 3.9+
✅ SQL Server LocalDB (viene con Visual Studio)
✅ MongoDB Community Server 6+
✅ Power BI Desktop (Mayo 2026+)
✅ ODBC Driver 17 for SQL Server
```

```bash
# Python
pip install sqlalchemy pandas pyodbc pymongo numpy openpyxl

# Crear base de datos Northwind en LocalDB
sqlcmd -S "(localdb)\MSSQLLocalDB" -i ETL_Base_ded_datos/scripteado/northwind.sql

# Crear staging en LocalDB
sqlcmd -S "(localdb)\MSSQLLocalDB" -i ETL_Base_ded_datos/northwind_etl_python/northwind_etl/sql/create_staging.sql
```

### Opción B — Solo CSV para Power BI (mínimo)

```
✅ Python 3.9+ (solo librería estándar + csv)
✅ Power BI Desktop (Mayo 2026+)
```

```bash
python generate_csvs.py   # genera csvs/ desde northwind.sql
python verify_csvs.py     # verifica integridad
# Luego conectar Power BI a los CSV
```

---

## 16. Guía de Ejecución por Fase

```bash
# ── FASE 2: ETL Python ───────────────────────────────────────────────
cd ETL_Base_ded_datos/northwind_etl_python/northwind_etl/
python pipeline.py
# Resultado: northwind_staging con 11 tablas pobladas

# ── FASE 3: MongoDB DW ───────────────────────────────────────────────
cd "entreega preeparada/entreega preeparada/"
python northwind_sql_to_mongodb.py
# Resultado: northwind_dw con 8 colecciones (2155 fact_ventas)

# ── OPCIÓN SIN SERVIDORES ────────────────────────────────────────────
python generate_csvs.py    # desde la raíz del repo
python verify_csvs.py      # verificar integridad

# ── FASE 4: Power BI ─────────────────────────────────────────────────
# Abrir proyecto-bi/northwind_bi.pbip en Power BI Desktop
# Actualizar datos → Import Mode embebe todo en el .pbip
# Guardar → el reporte funciona sin servidores
```

---

## 17. Independencia entre Fases

Una pregunta frecuente: **¿necesito que todos los servicios estén corriendo?**

```
ETL Python  ─────── Corre UNA VEZ ──────► datos en Staging
                                                │
MongoDB     ─────── Corre UNA VEZ ──────► datos en northwind_dw
                                                │
Power BI    ─────── Import UNA VEZ ─────► datos en .pbip
                                                │
Sustentación ───────────────────────────► Solo abrir .pbip
                                          (sin servidores)
```

> **Para la sustentación:** con Import Mode activo, el archivo `.pbip` tiene los datos embebidos. Solo necesitas abrir Power BI Desktop con el archivo. No se necesita ningún servidor corriendo.

---

## 18. Punto Extra — Tabular SSAS

El proyecto implementa el **modelo semántico con Tabular SSAS** mencionado en la actividad como punto extra.

> *"Se reconocerá un punto adicional si los grupos pasan de un modelo dimensional a un modelo semántico con Tabular SASS y el Visualizador se conecta al modelo semántico para realizar los dashboards."*

### Evidencia técnica

El `northwind_bi.SemanticModel/` es un modelo tabular Analysis Services serializado en **TMDL (Tabular Model Definition Language)**:

```tmdl
# database.tmdl
database
    compatibilityLevel: 1600    ← Analysis Services Tabular

# model.tmdl
model Model
    culture: es-CO
    defaultPowerBIDataSourceVersion: powerBI_V3
    ...
    table fact_ventas   ← tabla de hechos
    table dim_fecha     ← dimensión calculada (DAX CALENDAR)
    table dim_cliente   ← dimensión M (Power Query)
    ...
    measure 'Total Ventas' = SUM(fact_ventas[total_venta])
    ...
    relationship 'fv_fecha'
        fromColumn: fact_ventas.fecha_id
        toColumn:   dim_fecha.fecha_id
```

**TMDL** es el lenguaje oficial del **Tabular Object Model (TOM)** de Analysis Services. Power BI Desktop se conecta al modelo a través de su instancia interna de Analysis Services (`byPath` en `definition.pbir`).

Documentación oficial: [learn.microsoft.com/analysis-services/tmdl](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview)

---

## 19. Estado del Proyecto

### Progreso general

| Fase | Estado | Notas |
|---|---|---|
| **Fase 1 — Análisis Funcional** | ✅ Completa | Modelo dimensional, diccionario, reglas de calidad |
| **Fase 2 — ETL Python** | ✅ Completa | 11 tablas, 14 transformaciones, bugs corregidos |
| **Fase 3 — MongoDB DW** | ✅ Completa | 8 colecciones, validación, bugs corregidos |
| **Fase 4 — Modelo Semántico** | ✅ Completa | TMDL con 8 tablas, 22 medidas, 7 relaciones |
| **Fase 4 — Páginas vacías** | ✅ Listas | 4 páginas PBIR creadas |
| **Fase 4 — Visuals** | 🔄 Pendiente | Construcción en Power BI Desktop |
| **CSV sin infraestructura** | ✅ Validado | `generate_csvs.py` + 0 errores de integridad |
| **Repositorio Git** | ✅ Publicado | github.com/Raikadier/advanced-db-final-project |

### Validación de datos (última ejecución)

```
✅ dim_fecha          :    672 filas  (1996-07-04 → 1998-05-06)
✅ dim_cliente        :     91 filas  (38 Premium, 50 Regular, 3 Inactivo)
✅ dim_empleado       :      9 filas  (todos los nombres correctos)
✅ dim_producto       :     77 filas
✅ dim_shipper        :      3 filas  (avg entrega: 5.9, 7.8, 6.1 días)
✅ dim_territorio     :     69 filas  (6 zonas geográficas)
✅ dim_metas_empleado :    108 filas  (9 × 3 años × 4 trimestres)
✅ fact_ventas        :  2,155 filas

Integridad referencial: 0 errores en 6 relaciones FK
Total ventas: $1,265,793 | Margen global: 31.3%
```

---

## Licencia

MIT — ver archivo [LICENSE](LICENSE)

---

*Proyecto desarrollado para la asignatura Base de Datos Avanzadas — Universidad Popular del Cesar (UPC), 2026.*
