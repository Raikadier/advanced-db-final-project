# Guía de estudio — Proyecto BI Northwind

Documento de referencia para **entender, reproducir y sustentar** el proyecto completo: ETL, Data Warehouse, modelo semántico y reporte Power BI.

> **Índice maestro:** el [README.md](../README.md) del repositorio contiene la documentación técnica detallada (2.000+ líneas). Esta guía organiza el material en un **orden de estudio** y documenta **qué se hizo, por qué y cómo verificarlo**.

---

## 1. Mapa mental del proyecto

```
Northwind OLTP (Supabase PostgreSQL)
        │  Fase A: Extract → Transform → Validate → Load
        ▼
Staging (Supabase PostgreSQL, tablas stg_*)
        │  Fase B: load_dw.py (modelado dimensional)
        ▼
MongoDB Atlas (northwind_dw, 8 colecciones)
        │  Import Mode + Atlas SQL ODBC
        ▼
Power BI (.pbip: TMDL + PBIR, 4 páginas, P1–P10)
```

**Idea clave:** hay **tres capas de datos** con roles distintos. El ETL no copia crudo: limpia en staging y modela en el DW. Power BI consume el DW, no el OLTP.

---

## 2. Orden de estudio recomendado

| # | Tema | Dónde leer | Tiempo |
|---|------|------------|--------|
| 1 | Contexto y preguntas P1–P10 | README § Resumen, Preguntas de negocio | 15 min |
| 2 | Arquitectura cloud | README § Arquitectura objetivo | 20 min |
| 3 | ETL teoría + dos fases | README § ETL Fundamentos, Fase A/B | 45 min |
| 4 | Código ETL módulo a módulo | `etl/etl/*.py` + README § pipeline.py… | 2 h |
| 5 | Modelo dimensional | README § Modelo estrella, Colecciones MongoDB | 30 min |
| 6 | Power BI conexión ODBC | README § Conexión Atlas SQL | 30 min |
| 7 | Reporte y medidas DAX | README § Proyecto PBIP + `_Medidas.tmdl` | 45 min |
| 8 | Corrección filtros slicer | Esta guía § 5 + `scripts/` | 20 min |
| 9 | Verificación E2E | Esta guía § 4 | 30 min |
| 10 | Guión sustentación | README § Cómo explicarlo en la sustentación | 30 min |

---

## 3. ETL — Qué hace cada etapa

### Pipeline (`etl/pipeline.py`)

| Paso | Nombre | Módulo | Entrada → Salida |
|------|--------|--------|------------------|
| 1/6 | Conexiones | `db_connection.py` | `.env` → engines SQLAlchemy |
| 2/6 | Bootstrap | `bootstrap.py`, `etl_meta.py` | DDL staging si falta + `etl_runs` |
| 3/6 | Extracción | `extract.py` | 11 tablas OLTP → DataFrames |
| 4/6 | Transformación | `transform.py` | DataFrames crudos → limpios (TR-xxx) |
| 4b | Validación | `validate.py` | Reglas RQ-xxx (warnings) |
| 5/6 | Carga staging | `load_staging.py` | DataFrames → `stg_*` (TRUNCATE + INSERT) |
| 6/6 | Carga DW | `load_dw.py` | `stg_*` → 8 colecciones MongoDB |

### Por qué dos fases

1. **Staging** persiste datos limpios aunque falle MongoDB → depuración y trazabilidad.
2. **DW** materializa el esquema estrella optimizado para BI.
3. **OLTP** nunca se modifica (solo `SELECT`).

### Estrategia: full refresh

Cada ejecución vacía staging y DW y recarga todo. Northwind tiene ~3.300 filas; el pipeline tarda **~60–90 s**. Es idempotente y auditable vía `etl_runs`.

---

## 4. Verificación ETL (ejecutada 2026-06-08)

### 4.1 Diagnóstico de conexiones

```bash
cd etl/
python _check_env.py
```

**Resultado:**

| Conexión | Estado |
|----------|--------|
| Supabase OLTP | OK — 11 tablas Northwind |
| Supabase Staging | OK — 12 tablas (`stg_*` + `etl_runs`) |
| MongoDB Atlas | OK — 8 colecciones en `northwind_dw` |

### 4.2 Pipeline completo

```bash
cd etl/
python pipeline.py
```

**Resultado run_id=4 (2026-06-08 13:35–13:36):**

| Etapa | Métrica | Valor |
|-------|---------|-------|
| Extracción | Tablas OK | 11/11 |
| Extracción | Errores | 0 |
| Validación | Problemas RQ | 0 |
| Staging | Registros totales | 3.308 |
| Staging | `stg_order_details` | 2.155 |
| DW | Documentos totales | 3.184 |
| DW | `fact_ventas` | 2.155 |
| DW | `dim_fecha` | 672 |
| DW | `dim_cliente` | 91 |
| DW | `dim_metas_empleado` | 108 |
| Auditoría | `etl_runs.status` | `success` |
| Performance | Duración | 67 s |

### 4.3 Consultas de verificación manual

**Staging (SQL Editor):**

```sql
SELECT run_id, status, duration_sec, rows_loaded
FROM etl_runs ORDER BY started_at DESC LIMIT 3;
```

**MongoDB (Python):**

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv("../.env")
db = MongoClient(os.environ["MONGO_URI"])[os.environ.get("MONGO_DB", "northwind_dw")]
print("fact_ventas:", db.fact_ventas.count_documents({}))
total = sum(d["total_venta"] for d in db.fact_ventas.find({}, {"total_venta": 1}))
print(f"Total ventas: ${total:,.2f}")  # esperado ~$1,265,793
```

### 4.4 Flags útiles para depurar por etapa

| Comando | Uso |
|---------|-----|
| `python pipeline.py --dry-run` | Conexión + extract + transform sin escribir |
| `python pipeline.py --only-extract` | Solo leer OLTP |
| `python pipeline.py --skip-dw` | Solo Fase A (staging) |
| `python pipeline.py --skip-validate` | Omitir RQ-xxx |

---

## 5. Power BI — Corrección del reporte en blanco

### 5.1 Síntoma observado

Patrón **flash then blank**: al abrir el reporte, los KPIs mostraban datos un instante y luego quedaban en `(En blanco)`. Gráficos y tablas vacíos en las 4 páginas.

### 5.2 Causa raíz (no era el modelo ni el ETL)

El **modelo semántico tenía datos** (`[Total Ventas]` ≈ $1.265M cuando no hay filtros). El problema eran **filtros del reporte** guardados en los segmentadores (slicers):

| Problema | Efecto |
|----------|--------|
| `objects.general` con selección guardada (incl. `null`) | Filtraba a cero filas al cargar |
| `syncGroup.filterChanges: true` en Año/Trimestre | Propagaba filtros malos entre páginas |
| `drillFilterOtherVisuals: true` en slicers | Un trimestre en blanco filtraba todos los visuales |
| `strictSingleSelect` en dropdowns Año/Trimestre | Forzaba selección vacía |

### 5.3 Qué se corrigió

Script: [`scripts/audit_fix_report_filters.py`](../scripts/audit_fix_report_filters.py)

| Acción | Alcance |
|--------|---------|
| Eliminar bloques `objects.general` con filtros guardados | 10 slicers |
| `filterChanges` → `false` en grupos sincronizados | 6 slicers (anio, trimestre) |
| `drillFilterOtherVisuals` → `false` en slicers | 10 slicers |
| Quitar `strictSingleSelect` en Año/Trimestre | Resumen Ejecutivo + otras páginas |

Auditoría generada: [`proyecto-bi/northwind_bi.Report/AUDIT-report-filters.json`](../proyecto-bi/northwind_bi.Report/AUDIT-report-filters.json)

Script auxiliar: [`scripts/fix_slicer_null_filters.py`](../scripts/fix_slicer_null_filters.py) — elimina selecciones con `"Value": "null"`.

### 5.4 Por qué funcionó

Power BI aplica el estado guardado del slicer **después** del primer render. Si ese estado filtra `null` o un valor sin datos, el contexto de filtro del reporte queda vacío aunque las medidas DAX sean correctas.

### 5.5 Cómo reproducir la corrección

```bash
python scripts/audit_fix_report_filters.py
```

Luego en Desktop: cerrar → reabrir `proyecto-bi/northwind_bi.pbip` → **Actualizar** → **Limpiar todas las segmentaciones**.

### 5.6 Métricas esperadas tras la corrección

| Medida / visual | Valor esperado |
|-----------------|----------------|
| `[Total Ventas]` | ~$1.265.793 |
| `[Num Ordenes]` | ~830 |
| `[Clientes Activos]` | ~91 |
| `[% Margen Promedio]` | ~31 % |
| Gráfico evolución mensual | Línea 1996–1998 |
| Segmentación `anio` | 1996, 1997, 1998 (no blanco) |

---

## 6. Modelo semántico — Decisiones clave

### Conexión a MongoDB

- **ETL** usa `mongodb+srv://` (driver `pymongo`).
- **Power BI** usa **Atlas SQL + ODBC** (`mongodb://atlas-sql-....query.mongodb.net/...`).
- Son endpoints distintos; `_check_env.py` OK no garantiza refresh en Desktop.

### Tipos de datos (F4-11)

Atlas SQL ODBC a veces importa números como texto. Las 8 tablas TMDL incluyen `Table.TransformColumnTypes` en la partición M. Sin esto, `SUM()` devuelve blanco.

### `dim_metas_empleado` (F4-09)

Granularidad: `empleado_id + anio + trimestre` (108 filas). `empleado_id` **no es único**. Las medidas P5 (`[Meta Periodo]`, `[% Cumplimiento Meta]`) filtran con `CALCULATE`, no con relación directa desde `fact_ventas`.

### Parámetros de conexión

Archivo: `proyecto-bi/northwind_bi.SemanticModel/definition/expressions.tmdl`

- `MongoDB Atlas URI` — endpoint Atlas SQL (sin credenciales en URI)
- `MongoDB Database` — `northwind_dw`

> **Corrección jun 2026:** se unificó el host Atlas SQL (`8l1q1z`) en `expressions.tmdl` para coincidir con las 8 tablas TMDL.

---

## 7. Páginas del reporte y preguntas de negocio

| Página | GUID | Preguntas | Contenido |
|--------|------|-----------|-----------|
| Resumen Ejecutivo | `e3e43335c708953e4407` | P1, P10 | KPIs, línea mensual, matriz trimestral |
| Clientes y Geografía | `d72257249741148631d0` | P2, P6, P9 | Top 10, mapa, inactivos |
| Operaciones y Logística | `d9ff3d19e960c247b7bd` | P3, P4, P7 | Productos, categorías, entregas |
| Desempeño y Auditoría | `ad7a10cd5c1f2cdd218f` | P5, P8 | Ventas vs meta, rentabilidad |

---

## 8. Registro de errores corregidos (resumen)

| ID | Área | Problema | Solución |
|----|------|----------|----------|
| F2-01 | ETL | `pd.NA` en enteros staging | `pd.Int32Dtype()` en `transform_orders` |
| F2-03 | ETL | `NaN` en Fase B | `_safe_int()` en `load_dw.py` |
| F3-01 | MongoDB | Carga desde regex SQL | Lee staging real |
| F4-09 | TMDL | `isKey` en `empleado_id` no único | Quitado en `dim_metas_empleado` |
| F4-10 | Power BI | Fuentes LocalDB/CSV | Migrado a Atlas SQL ODBC |
| F4-11 | Power BI | Tipos texto desde ODBC | `TransformColumnTypes` en 8 tablas |
| **F4-12** | **PBIR** | **Slicers filtran todo (flash then blank)** | **`audit_fix_report_filters.py`** |

---

## 9. Guión rápido para sustentación (5 minutos)

1. **Arquitectura:** OLTP Supabase → ETL Python en PC → Staging → MongoDB DW → Power BI Import.
2. **ETL:** Full refresh en dos fases; 11 tablas fuente, 8 colecciones DW; auditado en `etl_runs`; ~67 s por ejecución.
3. **Modelo:** Esquema estrella; `fact_ventas` a nivel línea de pedido (2.155); segmentación de clientes y calendario en dimensiones.
4. **BI:** 4 páginas responden P1–P10; ~30 medidas DAX; conexión Atlas SQL ODBC.
5. **Problema resuelto:** Reporte en blanco por filtros de slicer, no por datos. Script de auditoría en repo.
6. **Demo:** `_check_env.py` → `pipeline.py` → abrir `.pbip` → Actualizar → mostrar KPIs.

---

## 10. Archivos importantes del repositorio

```
advanced-db-final-project/
├── docs/GUIA_ESTUDIO.md          ← este documento
├── README.md                     ← documentación técnica completa
├── .env.example                  ← plantilla credenciales
├── etl/
│   ├── pipeline.py               ← orquestador
│   ├── _check_env.py             ← diagnóstico conexiones
│   └── etl/                      ← módulos ETL
├── scripts/
│   ├── audit_fix_report_filters.py
│   └── fix_slicer_null_filters.py
└── proyecto-bi/
    ├── README.md                 ← guía específica del PBIP
    ├── northwind_bi.pbip
    ├── northwind_bi.SemanticModel/
    └── northwind_bi.Report/
```

---

*Última actualización: junio 2026 — ETL verificado E2E (run_id=4) y reporte Power BI validado con datos en las 4 páginas.*
