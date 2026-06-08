# Proyecto BI — Northwind Traders

**Base de Datos Avanzadas · Universidad Popular del Cesar · 2026-1**

| | |
|---|---|
| **Asignatura** | Base de Datos Avanzadas |
| **Dataset** | Microsoft Northwind Traders (jul 1996 — may 1998) |
| **Stack objetivo** | Supabase (OLTP + Staging) · MongoDB Atlas · Python ETL · Power BI PBIP |
| **Preguntas de negocio** | 10 (P1–P10) |
| **Repositorio** | [advanced-db-final-project](https://github.com/Raikadier/advanced-db-final-project) |

[![Python](https://img.shields.io/badge/ETL-Python_3.x-3776AB?style=flat&logo=python)](https://python.org)
[![Supabase](https://img.shields.io/badge/OLTP%20%2B%20Staging-Supabase-3FCF8E?style=flat&logo=supabase)](https://supabase.com)
[![MongoDB](https://img.shields.io/badge/DW-MongoDB_Atlas-47A248?style=flat&logo=mongodb)](https://mongodb.com)
[![Power BI](https://img.shields.io/badge/BI-Power_BI_PBIP-F2C811?style=flat&logo=powerbi)](https://powerbi.microsoft.com)

---

## Índice

### General
- [Resumen](#resumen)
- [Equipo y roles](#equipo-y-roles)
- [Preguntas de negocio (P1–P10)](#preguntas-de-negocio-p1p10)

### Arquitectura y decisiones
- [Arquitectura objetivo (cloud)](#arquitectura-objetivo-cloud)
- [Arquitectura legacy (referencia local)](#arquitectura-legacy-referencia-local)
- [Registro de decisiones de diseño](#registro-de-decisiones-de-diseño)
- [Stack tecnológico](#stack-tecnológico)

### Configuración paso a paso
- [Guía de configuración desde cero](#guía-de-configuración-desde-cero) ← **empezar aquí**
- [Supabase — Proyecto fuente (`northwind-oltp`)](#supabase--proyecto-fuente-northwind-oltp)
- [Supabase — Proyecto staging (`northwind-staging`)](#supabase--proyecto-staging-northwind-staging)
- [MongoDB Atlas — Data Warehouse](#mongodb-atlas--data-warehouse)
- [Cursor — MCP Supabase](#cursor--mcp-supabase)
- [Variables de entorno (`.env`)](#variables-de-entorno-env)
- [Programación del ETL en tu PC (Task Scheduler)](#programación-del-etl-en-tu-pc-task-scheduler)

### ETL (guía en profundidad — estudio y sustentación)
- [ETL — Cómo leer esta guía](#etl--cómo-leer-esta-guía)
- [ETL — Visión ejecutiva (30 segundos)](#etl--visión-ejecutiva-30-segundos)
- [ETL — Fundamentos teóricos](#etl--fundamentos-teóricos)
- [ETL — Arquitectura de dos fases](#etl--arquitectura-de-dos-fases)
- [ETL — Diagrama de secuencia](#etl--diagrama-de-secuencia)
- [ETL — Línea de datos (lineage)](#etl--línea-de-datos-lineage)
- [ETL — Flujo en lenguaje simple](#etl--flujo-en-lenguaje-simple)
- [ETL — Catálogo de transformaciones (TR-xxx)](#etl--catálogo-de-transformaciones-tr-xxx)
- [ETL — Catálogo de calidad (RQ-xxx)](#etl--catálogo-de-calidad-rq-xxx)
- [ETL — Esquema staging (`stg_*`)](#etl--esquema-staging-stg_)
- [ETL — Modelo DW (colecciones MongoDB)](#etl--modelo-dw-colecciones-mongodb)
- [ETL — Estructura de archivos](#etl--estructura-de-archivos)
- [ETL — `pipeline.py`](#etl--pipelinepy)
- [ETL — `config.py`](#etl--configpy)
- [ETL — `db_connection.py`](#etl--db_connectionpy)
- [ETL — `bootstrap.py`](#etl--bootstrappy)
- [ETL — `extract.py`](#etl--extractpy)
- [ETL — `transform.py`](#etl--transformpy)
- [ETL — `validate.py`](#etl--validatepy)
- [ETL — `load_staging.py`](#etl--load_stagingpy)
- [ETL — `load_dw.py`](#etl--load_dwpy)
- [ETL — `etl_meta.py`](#etl--etl_metapy)
- [ETL — `logger_setup.py`](#etl--logger_setuppy)
- [ETL — Scripts SQL](#etl--scripts-sql)
- [ETL — Ejecución y automatización](#etl--ejecución-y-automatización)
- [ETL — Métricas verificadas (último run)](#etl--métricas-verificadas-último-run)
- [ETL — Cómo explicarlo en la sustentación](#etl--cómo-explicarlo-en-la-sustentación)
- [ETL — Solución de problemas](#etl--solución-de-problemas)

### Datos y modelo
- [Modelo dimensional (esquema estrella)](#modelo-dimensional-esquema-estrella)
- [Colecciones MongoDB](#colecciones-mongodb)
- [Medidas DAX](#medidas-dax)
- [Diseño de visualizaciones](#diseño-de-visualizaciones)

### Power BI
- [Power BI — Conexión a MongoDB Atlas SQL](#power-bi--conexión-a-mongodb-atlas-sql)
- [Power BI — Validación de vistas y medidas](#power-bi--validación-de-vistas-y-medidas)
- [Proyecto PBIP / TMDL / PBIR](#proyecto-pbip--tmdl--pbir)
- [Páginas del reporte](#páginas-del-reporte)

### Operación y respaldo
- [Plan B — CSV sin infraestructura](#plan-b--csv-sin-infraestructura)
- [Guía de estudio (documento dedicado)](docs/GUIA_ESTUDIO.md) ← **material para sustentación**
- [Estructura del repositorio](#estructura-del-repositorio)
- [Guía de configuración desde cero](#guía-de-configuración-desde-cero)
- [Guía de ejecución rápida](#guía-de-ejecución-rápida)
- [Errores corregidos (auditoría)](#errores-corregidos-auditoría)
- [Punto extra — Tabular SSAS](#punto-extra--tabular-ssas)
- [Estado del proyecto](#estado-del-proyecto)

---

## Resumen

Proyecto de **Business Intelligence** sobre **Northwind Traders**. El pipeline transforma datos operacionales (OLTP) en un **Data Warehouse dimensional** en MongoDB, consumido por **Power BI**, respondiendo **10 preguntas de negocio** con dashboards interactivos.

La **arquitectura objetivo** desacopla las capas en la nube: dos proyectos **Supabase** (fuente y staging), **MongoDB Atlas** como DW, y un **ETL Python ejecutado en el PC del desarrollador** que orquesta todo el ciclo. Power BI se actualiza contra el DW remoto (modo Import con refresh).

> Ver también: [Arquitectura objetivo](#arquitectura-objetivo-cloud) · [Registro de decisiones](#registro-de-decisiones-de-diseño) · [Guía del ETL](#etl--visión-general)

---

## Equipo y roles

| Rol | Responsabilidad |
|-----|-----------------|
| **Análisis funcional** | Modelo dimensional, P1–P10, diccionario de datos |
| **ETL Python** | Pipeline fuente → staging → DW |
| **MongoDB DW** | Colecciones `dim_*` / `fact_*` en Atlas |
| **Power BI** | Modelo TMDL, reporte PBIR, validación |

---

## Preguntas de negocio (P1–P10)

| # | Pregunta | Página del dashboard |
|---|----------|----------------------|
| **P1** | ¿Cómo han evolucionado las ventas por mes y año? | Resumen Ejecutivo |
| **P2** | ¿Top 10 clientes y su comportamiento en el tiempo? | Clientes y Geografía |
| **P3** | ¿Productos con mayor volumen y contribución? | Operaciones y Logística |
| **P4** | ¿Categorías con mayores ingresos y tendencia? | Operaciones y Logística |
| **P5** | ¿Empleados vs. metas de ventas? | Desempeño y Auditoría |
| **P6** | ¿Regiones/países con más ingresos? | Clientes y Geografía |
| **P7** | ¿Tiempos de entrega por región/transportista? | Operaciones y Logística |
| **P8** | ¿Rentabilidad por producto? | Desempeño y Auditoría |
| **P9** | ¿Clientes inactivos e impacto? | Clientes y Geografía |
| **P10** | ¿Patrones estacionales? | Resumen Ejecutivo |

---

## Arquitectura objetivo (cloud)

Arquitectura acordada para el proyecto en producción académica. El ETL corre **en el PC del desarrollador** (no en la nube).

```
┌─────────────────────────┐
│ Supabase Proyecto 1     │  northwind-oltp
│ PostgreSQL — Fuente     │  Tablas Northwind OLTP
│ ref: svrxnmbagwumyogxdlfu
└───────────┬─────────────┘
            │  EXTRACT (Fase A)
            ▼
┌─────────────────────────┐
│ Tu PC — Python ETL      │  pipeline.py (en evolución)
│ transform + validate    │
└───────────┬─────────────┘
            │  LOAD staging
            ▼
┌─────────────────────────┐
│ Supabase Proyecto 2     │  northwind-staging
│ PostgreSQL — Staging    │  STG_* + etl_runs
│ ref: crvyesiaqbqkqaslflya
└───────────┬─────────────┘
            │  LOAD DW (Fase B)
            ▼
┌─────────────────────────┐
│ MongoDB Atlas           │  northwind_dw
│ 8 colecciones dim/fact  │
└───────────┬─────────────┘
            │  Import / Refresh
            ▼
┌─────────────────────────┐
│ Power BI (.pbip)        │  TMDL + PBIR — 4 páginas
└─────────────────────────┘
```

**URLs de API (referencia):**

| Proyecto | Rol | URL |
|----------|-----|-----|
| `svrxnmbagwumyogxdlfu` | Fuente OLTP | `https://svrxnmbagwumyogxdlfu.supabase.co` |
| `crvyesiaqbqkqaslflya` | Staging | `https://crvyesiaqbqkqaslflya.supabase.co` |

---

## Arquitectura legacy (referencia local)

Implementación original del repositorio (SQL Server LocalDB + MongoDB local). Se mantiene como referencia y plan B.

```
Northwind (SQL Server LocalDB)
    → ETL Python (pipeline.py)
    → northwind_staging (LocalDB)
    → northwind_sql_to_mongodb.py
    → MongoDB local (localhost:27017)
    → Power BI (Import / CSV)
```

> La migración a la arquitectura objetivo **reutiliza** el código ETL existente; no requiere reescribirlo desde cero. Ver [ETL — Flujo en lenguaje simple](#etl--flujo-en-lenguaje-simple).

---

## Registro de decisiones de diseño

Documento vivo: cada decisión relevante se registra aquí con fecha y motivo.

| Fecha | Decisión | Motivo | Estado |
|-------|----------|--------|--------|
| 2026-06 | **Dos proyectos Supabase separados** (fuente + staging), no un solo proyecto con schemas | Aislamiento OLTP vs landing zone; narrativa profesional de extracción remota | ✅ Acordado |
| 2026-06 | **ETL en el PC del desarrollador**, no en GitHub Actions | Control local, cron con Task Scheduler, sin exponer fuente | ✅ Acordado |
| 2026-06 | **DW en MongoDB Atlas** (no MongoDB local en producción) | Acceso remoto; Power BI solo necesita internet para refresh | ✅ Verificado E2E |
| 2026-06 | **No reescribir ETL** — extender `pipeline.py` + integrar `load_dw` | ~70–80 % del código actual es reutilizable | ✅ Implementado |
| 2026-06 | **Pipeline unificado** Fase A + B en `pipeline.py` | Un solo comando; full refresh staging + DW | ✅ Implementado |
| 2026-06 | **Bootstrap staging** en primera ejecución | `bootstrap.py` aplica DDL si faltan tablas | ✅ Implementado |
| 2026-06 | **`etl_runs` + Task Scheduler** | Auditoría de ejecuciones periódicas | ✅ Implementado (`etl_meta.py`) |
| 2026-06 | **Carga incremental (`watermark`)** | Optimización futura para volúmenes grandes | 📋 Planeado |
| 2026-06 | **Plan B: `generate_csvs.py`** | Sustentación sin depender de red o servicios cloud | ✅ Disponible |
| 2026-06 | **Power BI en Import Mode** | MongoDB no soporta DirectQuery nativo en PBI; Import + refresh programado | ✅ Acordado |
| 2026-06 | **Power BI vía MongoDB Atlas SQL + ODBC** | Conector integrado actual (no “MongoDB” legacy); requiere Data Federation en Atlas | ✅ Documentado |
| 2026-06 | **MCP Supabase en Cursor** (`supabase-oltp` + `supabase-staging`) | Migraciones y DDL asistidas por IA | 🔄 Configurado en `mcp.json` |
| 2026-06 | **Scripts PBIR para filtros slicer** (`audit_fix_report_filters.py`) | Corrige reporte en blanco por selecciones guardadas en segmentadores | ✅ Implementado |

*Para añadir una decisión: agregar fila a esta tabla en el mismo PR/commit que implemente el cambio.*

---

## Stack tecnológico

### Objetivo (cloud)

| Capa | Tecnología |
|------|------------|
| Fuente OLTP | Supabase PostgreSQL — `northwind-oltp` |
| Staging | Supabase PostgreSQL — `northwind-staging` |
| ETL | Python 3.10+ · pandas · SQLAlchemy · psycopg2 · pymongo |
| DW | MongoDB Atlas — `northwind_dw` |
| BI | Power BI Desktop PBIP · TMDL · PBIR |
| Orquestación local | Windows Task Scheduler |
| IDE / MCP | Cursor + Supabase MCP + Power BI MCP |

### Legacy (local)

| Capa | Tecnología |
|------|------------|
| Fuente / Staging | SQL Server LocalDB |
| DW | MongoDB Community local |
| ETL | Python + pyodbc |

---

## Supabase — Proyecto fuente (`northwind-oltp`)

**Project ref:** `svrxnmbagwumyogxdlfu`

### Qué aloja

- Base de datos operacional **Northwind** (tablas `Categories`, `Customers`, `Orders`, `Order Details`, etc.)
- Simula el ERP / sistema transaccional del que el ETL **extrae** datos

### Pasos de configuración

1. Crear proyecto en [supabase.com/dashboard](https://supabase.com/dashboard) → nombre `northwind-oltp`.
2. Anotar **Project ref** y **Database password**.
3. Aplicar DDL Northwind adaptado a PostgreSQL (vía MCP `apply_migration` o SQL Editor).
4. Verificar tablas: `list_tables` en MCP o `\dt` en SQL Editor.
5. Guardar connection string en `.env` → `SOURCE_DATABASE_URL`.

### Connection string (Session pooler recomendado para ETL)

```
postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:5432/postgres
```

> Obtener la URL exacta en: **Project Settings → Database → Connection string → URI**.

---

## Supabase — Proyecto staging (`northwind-staging`)

**Project ref:** `crvyesiaqbqkqaslflya`

### Qué aloja

- Tablas **`stg_*`** (landing zone del ETL)
- Tabla de control **`etl_runs`** (auditoría del pipeline)
- **No** contiene el modelo dimensional final (eso vive en MongoDB)

### Pasos de configuración

1. Crear proyecto `northwind-staging` en Supabase.
2. Guardar en `.env` → `STAGING_DATABASE_URL`.
3. Ejecutar `python pipeline.py` — `bootstrap.py` aplica `northwind_staging_supabase.sql` automáticamente si faltan tablas.

(Opcional manual: pegar `sql/northwind_staging_supabase.sql` en SQL Editor.)

### Tablas staging esperadas

```
stg_categories, stg_suppliers, stg_shippers, stg_customers,
stg_employees, stg_region, stg_territories, stg_employee_territories,
stg_products, stg_orders, stg_order_details, etl_runs
```

---

## MongoDB Atlas — Data Warehouse

### Qué configuras en Atlas (infraestructura)

Atlas **no define el esquema del DW en la UI**. El ETL crea colecciones al insertar documentos.

| Paso | Acción |
|------|--------|
| 1 | Crear cluster (M0 Free suele bastar para el TF) |
| 2 | **Database Access** → usuario `etl_northwind` (read/write) |
| 3 | **Network Access** → IP actual del PC de desarrollo |
| 4 | **Connect → Drivers → Python** → copiar URI `mongodb+srv://...` |
| 5 | Guardar en `.env` → `MONGO_URI` y `MONGO_DB=northwind_dw` |

### Qué crea el ETL (contenido del DW)

Ver [Colecciones MongoDB](#colecciones-mongodb). Tras la primera carga: `fact_ventas` ≈ **2.155** documentos.

### Verificación rápida

```bash
pip install pymongo
python -c "
from pymongo import MongoClient
import os
c = MongoClient(os.environ['MONGO_URI'])
db = c['northwind_dw']
print('Colecciones:', db.list_collection_names())
print('fact_ventas:', db.fact_ventas.count_documents({}))
"
```

### Power BI y Atlas

Power BI consume el DW en **modo Import** (refresh manual o programado) mediante el conector **MongoDB Atlas SQL** (no el conector legacy “MongoDB” ni `mongosqld` local).

> Guía paso a paso, errores frecuentes y patrón Power Query: [Power BI — Conexión a MongoDB Atlas SQL](#power-bi--conexión-a-mongodb-atlas-sql).

---

## Cursor — MCP Supabase

Configuración en `C:\Users\david\.cursor\mcp.json` (dos entradas, una por proyecto):

```json
"supabase-oltp": {
  "url": "https://mcp.supabase.com/mcp?project_ref=svrxnmbagwumyogxdlfu"
},
"supabase-staging": {
  "url": "https://mcp.supabase.com/mcp?project_ref=crvyesiaqbqkqaslflya"
}
```

### Activación

1. **Cursor → Settings → MCP** → autenticar Supabase (OAuth).
2. **Reload Window** tras editar `mcp.json`.
3. Verificar: pedir al agente `list_tables` en cada proyecto.

### Herramientas MCP útiles para este proyecto

| Herramienta | Uso |
|-------------|-----|
| `list_tables` | Auditar esquema antes/después de migraciones |
| `apply_migration` | DDL: Northwind fuente, `STG_*`, `etl_runs` |
| `execute_sql` | Seeds, consultas de verificación |
| `get_advisors` | Revisar RLS e índices en Supabase |

---

## Variables de entorno (`.env`)

Archivo **local**, nunca en Git. Crear `.env.example` en el repo como plantilla.

```env
# ── Supabase Fuente (northwind-oltp) ──
SOURCE_DATABASE_URL=postgresql://postgres.[ref]:[PASS]@...pooler.supabase.com:5432/postgres

# ── Supabase Staging (northwind-staging) ──
STAGING_DATABASE_URL=postgresql://postgres.[ref]:[PASS]@...pooler.supabase.com:5432/postgres

# ── MongoDB Atlas ──
MONGO_URI=mongodb+srv://etl_northwind:[PASS]@....mongodb.net/?retryWrites=true&w=majority
MONGO_DB=northwind_dw

# ── Control ETL ──
BATCH_SIZE=500
TRUNCATE_FIRST=true
VALIDATE_DATA=true
LOG_LEVEL=INFO
```

El módulo [`etl/config.py`](etl/etl/config.py) carga estas variables automáticamente desde la raíz del repo.

---

## Programación del ETL en tu PC (Task Scheduler)

Para demostrar que el pipeline **se actualiza periódicamente** (aunque Northwind sea estático):

| Elemento | Propósito |
|----------|-----------|
| **Task Scheduler** | Ejecutar `python pipeline.py` cada 15–30 min |
| **Tabla `etl_runs`** | Registro de cada ejecución en Supabase staging |
| **Demo en vivo** | Ejecutar manualmente antes de la sustentación |

### Crear tarea en Windows

1. Abrir **Programador de tareas** → Crear tarea básica.
2. Desencadenador: cada 30 minutos (documentar: *"equivale a ciclo de negocio de 15 días"*).
3. Acción: `python.exe` con argumentos `pipeline.py` y directorio de inicio `etl/`.
4. Verificar en `etl_runs` que el timestamp se actualiza.

> Carga incremental (`watermark.py`) queda como mejora futura; hoy el pipeline usa **full refresh** (ver [ETL — Flujo en lenguaje simple](#etl--flujo-en-lenguaje-simple)).

---

## ETL — Cómo leer esta guía

Esta sección está pensada para que puedas **estudiar el ETL con profundidad** y **explicarlo con lenguaje profesional** en la sustentación. No es solo un manual de ejecución: documenta el *por qué* de cada decisión, el flujo de datos tabla por tabla y el rol de cada módulo Python.

### Orden de estudio recomendado

| Paso | Sección | Objetivo |
|------|---------|----------|
| 1 | [Visión ejecutiva](#etl--visión-ejecutiva-30-segundos) | Elevator pitch de 30 s |
| 2 | [Fundamentos teóricos](#etl--fundamentos-teóricos) | Vocabulario BI/ETL correcto |
| 3 | [Arquitectura de dos fases](#etl--arquitectura-de-dos-fases) | Por qué staging y por qué MongoDB |
| 4 | [Diagrama de secuencia](#etl--diagrama-de-secuencia) | Orden exacto de operaciones |
| 5 | [Línea de datos](#etl--línea-de-datos-lineage) | De dónde sale cada campo del DW |
| 6 | [Catálogo TR / RQ](#etl--catálogo-de-transformaciones-tr-xxx) | Reglas de negocio implementadas |
| 7 | [`pipeline.py`](#etl--pipelinepy) + módulos | Código módulo por módulo |
| 8 | [Cómo explicarlo](#etl--cómo-explicarlo-en-la-sustentación) | Guión oral para el jurado |

### Glosario

| Término | Significado en este proyecto |
|---------|------------------------------|
| **OLTP** | Base operacional Northwind en Supabase (`northwind-oltp`). Simula el ERP transaccional. El ETL **solo lee** — nunca escribe. |
| **Staging** | Zona de aterrizaje en Supabase (`northwind-staging`). Tablas `stg_*` con datos **limpios y enriquecidos** (columnas `STG_*`). |
| **DW** | Data Warehouse analítico en MongoDB Atlas (`northwind_dw`). Modelo **estrella**: 7 dimensiones + 1 hecho. |
| **Full refresh** | Estrategia actual: en cada ejecución se vacía staging/DW y se recarga todo. Simple y auditable. |
| **Fase A** | OLTP → staging: Extract, Transform, Validate, Load. |
| **Fase B** | Staging → MongoDB: lectura SQL, transformación dimensional, carga documental. |
| **batch_id** | Identificador `YYYYMMDDHHMMSS` que une todas las filas de una misma ejecución. |
| **run_id** | Clave autoincremental en `etl_runs` para auditoría de cada ejecución. |

---

## ETL — Visión ejecutiva (30 segundos)

> *"Tenemos un pipeline ETL en Python que extrae datos operacionales de Northwind en Supabase, los limpia y enriquece en una zona staging separada, y luego construye un modelo dimensional en MongoDB Atlas con esquema estrella. Power BI consume ese DW en modo Import. Cada ejecución queda auditada en la tabla `etl_runs`, y el proceso corre en el PC del desarrollador con Task Scheduler para simular actualizaciones periódicas."*

**Números clave del dataset (verificado en producción):**

| Métrica | Valor |
|---------|-------|
| Tablas fuente extraídas | 11 |
| Registros en staging (total) | 3.308 |
| Documentos en DW (total) | 3.184 |
| Granularidad de `fact_ventas` | 1 fila = 1 línea de pedido |
| Líneas de hecho | 2.155 |
| Duración típica del pipeline | ~60–90 s |

---

## ETL — Fundamentos teóricos

### ¿Qué es ETL y qué hace este proyecto?

**ETL** = **E**xtract (extraer) + **T**ransform (transformar) + **L**oad (cargar).

En BI clásico (Kimball), el objetivo es pasar de un modelo **normalizado transaccional** (muchas tablas, optimizado para INSERT/UPDATE) a un modelo **dimensional desnormalizado** (pocas tablas, optimizado para agregaciones y filtros en dashboards).

Este proyecto implementa un patrón **ETL de dos saltos**:

```
OLTP (3FN, transaccional)  →  Staging (limpio, enriquecido)  →  DW (estrella, analítico)
```

No es ELT puro (donde la transformación ocurre dentro del motor del DW), porque:
- La **limpieza de negocio** ocurre en Python (pandas) antes de persistir en staging.
- La **conformación dimensional** (segmentos de cliente, calendario, metas) ocurre en Python antes de MongoDB.

### Tres capas de datos — roles distintos

| Capa | Motor | Rol | ¿Se modifica en el ETL? |
|------|-------|-----|-------------------------|
| **Fuente OLTP** | Supabase PostgreSQL | Sistema operacional simulado | Solo lectura (`SELECT`) |
| **Staging** | Supabase PostgreSQL (proyecto separado) | Landing zone + datos conformados | `TRUNCATE` + `INSERT` cada run |
| **DW** | MongoDB Atlas | Modelo estrella para BI | `drop()` colecciones + `insert_many` cada run |

**¿Por qué dos proyectos Supabase y no un solo schema?**

1. **Aislamiento**: el staging no compite con el OLTP en locks ni espacio.
2. **Narrativa profesional**: demuestra extracción remota entre sistemas distintos.
3. **Seguridad**: credenciales y permisos separables (OLTP read-only vs staging read-write).

**¿Por qué MongoDB como DW y no PostgreSQL otra vez?**

1. Cumple el requisito académico de **motor NoSQL** en la capa analítica.
2. El modelo documental encaja bien con dimensiones desnormalizadas (`dim_cliente` con `segmento_cliente` ya calculado).
3. Power BI puede consumirlo vía conector **MongoDB Atlas SQL** + ODBC en modo Import.

### Estrategia de carga: full refresh

| Alternativa | Ventaja | Por qué no la usamos aún |
|-------------|---------|--------------------------|
| **Full refresh** ✅ | Simple, reproducible, sin duplicados | Northwind es pequeño (~3K filas staging) |
| Incremental (watermark) | Eficiente en volúmenes grandes | Planeado como mejora futura (`watermark.py`) |
| CDC (Change Data Capture) | Tiempo real | Excesivo para dataset estático académico |

En cada ejecución:
- Staging: `TRUNCATE TABLE stg_xxx` → inserta todo de nuevo.
- MongoDB: `db.coleccion.drop()` → inserta todo de nuevo.
- OLTP: **nunca** se toca.

---

## ETL — Arquitectura de dos fases

### Fase A — Ingesta y conformación (`OLTP → Staging`)

**Propósito:** Tomar el modelo relacional fuente y dejarlo **listo para analítica**, con:
- Texto normalizado (TR-001).
- Tipos correctos (fechas, decimales).
- Métricas derivadas de negocio (`STG_ValorNeto`, `STG_DiasEntrega`, etc.).
- Metadatos de linaje (`STG_LOAD_DATE`, `STG_BATCH_ID`).

**Módulos involucrados:** `extract.py` → `transform.py` → `validate.py` → `load_staging.py`

**Salida:** 11 tablas `stg_*` en Supabase staging + registro parcial en `etl_runs`.

### Fase B — Modelado dimensional (`Staging → DW`)

**Propósito:** Leer el staging ya limpio y **materializar el esquema estrella** en MongoDB:
- 7 dimensiones (`dim_fecha`, `dim_cliente`, `dim_empleado`, `dim_producto`, `dim_shipper`, `dim_territorio`, `dim_metas_empleado`).
- 1 tabla de hechos (`fact_ventas`) a nivel línea de pedido.

**Módulo principal:** `load_dw.py` (contiene extract + transform + load de la Fase B en un solo archivo).

**Salida:** 8 colecciones en `northwind_dw` + índices + cierre de `etl_runs` con `status=success`.

### Separación de responsabilidades (principio de diseño)

```
pipeline.py     → Orquesta, no transforma datos
extract.py      → Solo lectura SQL → DataFrame
transform.py    → Solo lógica de limpieza/enriquecimiento en memoria
validate.py     → Solo reglas de calidad (warnings, no bloquea)
load_staging.py → Solo escritura PostgreSQL staging
load_dw.py      → Lectura staging + modelado + escritura MongoDB
etl_meta.py     → Solo auditoría en etl_runs
```

Esto facilita **depurar por etapa**: si falla la Fase B, el staging ya tiene datos válidos para inspeccionar.

---

## ETL — Diagrama de secuencia

```mermaid
sequenceDiagram
    participant U as Usuario / Task Scheduler
    participant P as pipeline.py
    participant O as Supabase OLTP
    participant S as Supabase Staging
    participant M as MongoDB Atlas

    U->>P: python pipeline.py
    P->>O: SELECT 1 (test conexión)
    P->>S: SELECT 1 (test conexión)
    P->>S: ensure_staging_schema() si falta DDL
    P->>S: INSERT etl_runs (status=running)

    loop Fase A — 11 tablas
        P->>O: SELECT * FROM "Tabla"
        Note over P: transform + validate en memoria
        P->>S: TRUNCATE stg_xxx
        P->>S: INSERT stg_xxx (lotes de 500)
    end

    loop Fase B — 8 colecciones
        P->>S: SELECT * FROM stg_*
        Note over P: build_dim_* + build_fact_ventas
        P->>M: drop() colecciones
        P->>M: insert_many (lotes de 500)
        P->>M: create_index()
    end

    P->>S: UPDATE etl_runs (status=success)
    P-->>U: RESUMEN FINAL en log
```

### Estados del pipeline

| Estado | Cuándo | Qué revisar |
|--------|--------|-------------|
| `running` | Pipeline en ejecución | Log en consola / `logs/etl_run_*.log` |
| `success` | Terminó sin excepciones | Conteos en staging + MongoDB |
| `failed` | Excepción no recuperada | `error_message` en `etl_runs` + log CRITICAL |

---

## ETL — Línea de datos (lineage)

Mapa completo: **de dónde sale cada dato** hasta `fact_ventas`.

### Tablas fuente → staging

| Tabla OLTP | Registros | Tabla staging | Transformador | Columnas derivadas clave |
|------------|-----------|---------------|---------------|--------------------------|
| `Categories` | 8 | `stg_categories` | `transform_categories` | — |
| `Suppliers` | 29 | `stg_suppliers` | `transform_suppliers` | — |
| `Shippers` | 3 | `stg_shippers` | `transform_shippers` | — |
| `Customers` | 91 | `stg_customers` | `transform_customers` | — |
| `Employees` | 9 | `stg_employees` | `transform_employees` | `FullName` |
| `Region` | 4 | `stg_region` | *(sin transformador)* | — |
| `Territories` | 53 | `stg_territories` | *(sin transformador)* | — |
| `EmployeeTerritories` | 49 | `stg_employee_territories` | *(sin transformador)* | — |
| `Products` | 77 | `stg_products` | `transform_products` | `STG_AlertaBajoReorden`, `STG_StockProyectado` |
| `Orders` | 830 | `stg_orders` | `transform_orders` | `STG_DiasEntrega`, `STG_EntregaPuntual` |
| `Order Details` | 2.155 | `stg_order_details` | `transform_order_details` | `STG_ValorNeto` |

**Orden de extracción/carga:** definido en `SOURCE_TABLES` de `config.py`. Las dimensiones van antes que los hechos para respetar dependencias lógicas (aunque el staging no tiene FK entre `stg_*`).

### Staging → colecciones DW

| Colección MongoDB | Docs | Función constructora | Fuentes staging | Lógica de negocio |
|-------------------|------|------------------------|-----------------|-------------------|
| `dim_fecha` | 672 | `build_dim_fecha` | `stg_orders` (fechas) | Calendario continuo min→max |
| `dim_cliente` | 91 | `build_dim_cliente` | `stg_customers` + `stg_orders` + `stg_order_details` | Agrega ventas, segmenta cliente |
| `dim_empleado` | 9 | `build_dim_empleado` | `stg_employees` | Copia + `reports_to` |
| `dim_producto` | 77 | `build_dim_producto` | `stg_products` + `stg_categories` + `stg_suppliers` | Join descriptivo + costo 60% |
| `dim_shipper` | 3 | `build_dim_shipper` | `stg_shippers` + `stg_orders` | Promedio días entrega |
| `dim_territorio` | 69 | `build_dim_territorio` | `stg_customers` | País×ciudad → continente/zona |
| `dim_metas_empleado` | 108 | `build_dim_metas_empleado` | `stg_employees` | 9 empleados × 3 años × 4 trimestres |
| `fact_ventas` | 2.155 | `build_fact_ventas` | `stg_order_details` + `stg_orders` + dims | 1 fila por línea de pedido |

### Lineage de campos críticos en `fact_ventas`

| Campo DW | Origen | Cálculo |
|----------|--------|---------|
| `order_detail_id` | `OrderID` + `ProductID` | `"{OrderID}-{ProductID}"` |
| `fecha_id` | `OrderDate` | `YYYYMMDD` como string |
| `total_venta` | `STG_ValorNeto` (staging) | `UnitPrice × Quantity × (1 - Discount)` |
| `costo_total` | `dim_producto.costo_adquisicion` | `costo_adquisicion × cantidad` |
| `margen` | derivado | `total_venta - costo_total` |
| `margen_pct` | derivado | `(margen / total_venta) × 100` |
| `territorio_id` | `dim_cliente.country` | Lookup en mapa país → territorio |
| `dias_entrega` | `STG_DiasEntrega` (staging) | Días entre `OrderDate` y `ShippedDate` |
| `entrega_puntual` | `STG_EntregaPuntual` (staging) | 1 si envió a tiempo, 0 si tarde, NULL si no envió |

---

## ETL — Flujo en lenguaje simple

Cada vez que ejecutas `python pipeline.py` (o Task Scheduler lo hace por ti):

```
Supabase OLTP          Tu PC (Python)              Supabase Staging         MongoDB Atlas
─────────────          ──────────────              ────────────────         ─────────────
"Customers" etc.  →    EXTRACT (leer)         →   (en memoria)
                       TRANSFORM (limpiar)    →   (en memoria)
                       VALIDATE (revisar)     →   (en memoria)
                       LOAD                   →   stg_customers, stg_orders...
                                                →   EXTRACT (leer stg_*)
                                                →   TRANSFORM (armar dims/facts)
                                                →   DROP colecciones + INSERT  →  dim_*, fact_*
```

**Importante:** staging no es una “copia cruda” antes del ETL. Staging **es el resultado** de la Fase A. La Fase B lee ese staging y construye el modelo dimensional en MongoDB.

**Qué se limpia en cada run**

| Capa | Acción |
|------|--------|
| Staging | `TRUNCATE` de cada tabla `stg_*` antes de insertar |
| MongoDB DW | `drop()` de las 8 colecciones antes de insertar |
| OLTP | Nunca se modifica — solo lectura |

---

## ETL — Catálogo de transformaciones (TR-xxx)

Todas las reglas están implementadas en [`etl/etl/transform.py`](etl/etl/transform.py). Son el corazón de la **Fase A**.

| ID | Nombre | Tabla(s) | Descripción | Implementación |
|----|--------|----------|-------------|----------------|
| **TR-001** | Normalización texto | Varias | `UPPER(TRIM(campo))` para consistencia en filtros BI | `_clean_str()` |
| **TR-002** | Cast monetario | Products, Orders, Order Details | Precios y fletes a `NUMERIC(18,2)` | `_to_decimal()` |
| **TR-003** | Fechas sin hora | Employees, Orders | `DATETIME` → solo `DATE` | `_to_date()` |
| **TR-004** | BIT → int | Products | `Discontinued` como 0/1 | `.astype(int)` |
| **TR-005** | Descuento decimal | Order Details | `Discount` a 2 decimales | `_to_decimal(, 2)` |
| **TR-006** | Valor neto venta | Order Details | Métrica base de ingresos | Ver fórmula abajo |
| **TR-007** | Días de entrega | Orders | Logística P7 | Ver fórmula abajo |
| **TR-008** | Entrega puntual | Orders | Indicador binario P7 | Ver fórmula abajo |
| **TR-009** | Alerta reorden | Products | Flag operativo | `ALERTA` si stock < reorder y activo |
| **TR-010** | Stock proyectado | Products | `UnitsInStock + UnitsOnOrder` | Columna `STG_StockProyectado` |
| **TR-013** | Nombre completo | Employees | Etiqueta para reportes | `LASTNAME, FIRSTNAME` en mayúsculas |
| **TR-014** | Filtro discontinued | Products | Flag informativo, no elimina filas | Solo marca, no filtra |

### Fórmulas detalladas

**TR-006 — Valor neto de venta** (base de casi todas las medidas de ingreso):

```
STG_ValorNeto = UnitPrice × Quantity × (1 - Discount)
```

Ejemplo: precio 10, cantidad 5, descuento 0.10 → `10 × 5 × 0.90 = 45.00`

**TR-007 — Días de entrega:**

```
STG_DiasEntrega = ShippedDate - OrderDate   (en días)
                 = NULL si ShippedDate es NULL
```

**TR-008 — Entrega puntual:**

```
STG_EntregaPuntual = 1  si ShippedDate ≤ RequiredDate
                   = 0  si ShippedDate > RequiredDate
                   = NULL si ShippedDate es NULL
```

### Tablas sin transformador dedicado

`Region`, `Territories` y `EmployeeTerritories` pasan **sin cambios** al staging. Se extraen para completitud del modelo fuente y posibles extensiones futuras, pero la Fase B actual no las usa directamente en las dimensiones del DW.

---

## ETL — Catálogo de calidad (RQ-xxx)

Implementado en [`etl/etl/validate.py`](etl/etl/validate.py). Las validaciones **no detienen el pipeline** por defecto: emiten `WARNING` en el log. Esto permite cargar datos con anomalías menores mientras se documentan.

| ID | Tabla | Campo | Regla | Severidad |
|----|-------|-------|-------|-----------|
| **RQ-001** | Order Details | Discount | Debe estar en [0, 1] | ALTA |
| **RQ-002** | Order Details | Quantity | Debe ser > 0 | ALTA |
| **RQ-003** | Order Details | UnitPrice | Debe ser ≥ 0 | ALTA |
| **RQ-004** | Orders | ShippedDate | ShippedDate ≥ OrderDate | ALTA |
| **RQ-005** | Orders | RequiredDate | RequiredDate ≥ OrderDate | MEDIA |
| **RQ-006** | Orders | OrderDate | No puede ser NULL | ALTA |
| **RQ-007** | Products | UnitsInStock | No negativo | ALTA |
| **RQ-009** | Products | UnitPrice | No negativo | ALTA |
| **RQ-010** | Products | Discontinued | Dominio {0, 1} | ALTA |
| **RQ-015** | Customers | CustomerID | Longitud = 5 y único | ALTA |

**Nota:** `transform_order_details` ya corrige descuentos fuera de rango forzándolos a 0 **antes** de la validación, por lo que RQ-001 rara vez reporta issues en la práctica.

**Activar/desactivar:** variable `VALIDATE_DATA=true` en `.env`, o flag `--skip-validate` en CLI.

---

## ETL — Esquema staging (`stg_*`)

DDL completo: [`etl/sql/northwind_staging_supabase.sql`](etl/sql/northwind_staging_supabase.sql)

### Convenciones del esquema

1. **Nombres PascalCase entre comillas** (`"CustomerID"`) — compatibles con el dataset Northwind original y con pandas `to_sql`.
2. **Tres columnas de metadatos** en todas las tablas `stg_*`:
   - `STG_LOAD_DATE` — fecha de carga (sin hora).
   - `STG_SOURCE_NAME` — siempre `"Northwind"`.
   - `STG_BATCH_ID` — timestamp de la ejecución (`YYYYMMDDHHMMSS`).
3. **Columnas derivadas** con prefijo `STG_` para distinguirlas de campos fuente.

### Tablas y claves primarias

| Tabla staging | PK | Columnas derivadas exclusivas |
|---------------|-----|-------------------------------|
| `stg_categories` | CategoryID | — |
| `stg_suppliers` | SupplierID | — |
| `stg_shippers` | ShipperID | — |
| `stg_customers` | CustomerID (CHAR 5) | — |
| `stg_employees` | EmployeeID | FullName |
| `stg_region` | RegionID | — |
| `stg_territories` | TerritoryID | — |
| `stg_employee_territories` | (EmployeeID, TerritoryID) | — |
| `stg_products` | ProductID | STG_AlertaBajoReorden, STG_StockProyectado |
| `stg_orders` | OrderID | STG_DiasEntrega, STG_EntregaPuntual |
| `stg_order_details` | (OrderID, ProductID) | STG_ValorNeto |

### Tabla de auditoría `etl_runs`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `run_id` | BIGSERIAL PK | Identificador único de ejecución |
| `started_at` | TIMESTAMPTZ | Inicio automático (`now()`) |
| `finished_at` | TIMESTAMPTZ | Fin (NULL si aún corre) |
| `status` | VARCHAR | `running` / `success` / `failed` |
| `batch_id` | VARCHAR | Mismo valor que `STG_BATCH_ID` |
| `phase` | VARCHAR | `full` (Fase A + B) |
| `rows_loaded` | JSONB | Conteo por tabla/colección |
| `tables_ok` | TEXT[] | Lista de tablas/colecciones exitosas |
| `tables_failed` | TEXT[] | Lista de fallos |
| `error_message` | TEXT | Mensaje si `status=failed` |
| `duration_sec` | NUMERIC | Duración total en segundos |

### Índices de performance

El DDL crea índices en FKs frecuentes (`CustomerID`, `EmployeeID`, `OrderDate`, `ProductID`, etc.) para acelerar los `SELECT *` de la Fase B.

---

## ETL — Modelo DW (colecciones MongoDB)

Implementado en [`etl/etl/load_dw.py`](etl/etl/load_dw.py). Base de datos: `northwind_dw` (configurable vía `MONGO_DB`).

### Esquema estrella

```
                    dim_fecha (fecha_id)
                        │
                    dim_cliente (cliente_id)
                        │
dim_metas_empleado ─► dim_empleado (empleado_id)
                        │
                    dim_producto (producto_id)
                        │
                    dim_shipper (shipper_id)
                        │
                    dim_territorio (territorio_id)
                        │
                 ┌──────▼ fact_ventas ──────┐
                 │  PK: order_detail_id     │
                 │  FKs → todas las dims    │
                 │  Métricas: venta, margen │
                 └──────────────────────────┘
```

### `dim_fecha` — dimensión calendario

| Campo | Tipo lógico | Descripción |
|-------|-------------|-------------|
| `fecha_id` | string | PK surrogate `YYYYMMDD` |
| `fecha_completa` | datetime | Fecha como objeto |
| `anio`, `trimestre`, `mes` | int | Para agregaciones temporales (P1, P10) |
| `nombre_mes`, `nombre_dia` | string | Etiquetas en español |
| `semana_anio`, `dia` | int | Granularidad semanal/diaria |
| `es_fin_semana` | bool | Filtro para análisis de patrones |

Rango generado: desde la fecha mínima hasta la máxima encontrada en `stg_orders` (típicamente 1996-07-04 → 1998-05-06, **672 días**).

### `dim_cliente` — con segmentación (P2, P6, P9)

| Campo | Origen / cálculo |
|-------|------------------|
| `cliente_id` | `stg_customers.CustomerID` |
| `total_ventas_usd` | SUM(`STG_ValorNeto`) de todos sus pedidos |
| `n_ordenes` | COUNT DISTINCT `OrderID` |
| `segmento_cliente` | Regla de negocio (ver tabla abajo) |

**Reglas de segmentación:**

| Segmento | Condición |
|----------|-----------|
| `Inactivo` | Más de 400 días sin comprar (respecto a la última fecha de pedido del dataset) |
| `Nuevo` | 1 orden o menos |
| `Premium` | `total_ventas_usd` > 10.000 |
| `Regular` | Todo lo demás |

### `dim_producto` — con costo estimado (P3, P4, P8)

| Campo | Cálculo |
|-------|---------|
| `costo_adquisicion` | `UnitPrice × 0.60` (supuesto documentado del 40% de margen bruto) |
| `categoria`, `proveedor` | Lookup desde `stg_categories` y `stg_suppliers` |

### `dim_territorio` — geografía conformada (P6)

Genera un `territorio_id` único por combinación país-ciudad del cliente. Asigna **continente** y **zona** según `ZONA_MAP` (diccionario hardcodeado con ~25 países de Northwind).

Ejemplo: `USA` → continente `América`, zona `Norteamérica`.

### `dim_metas_empleado` — tabla auxiliar para P5

9 empleados × 3 años (1996–1998) × 4 trimestres = **108 documentos**.

| Cargo | Meta trimestral USD | Categoría |
|-------|---------------------|-----------|
| Vice President, Sales | 18.000 | Agresiva |
| Sales Manager | 15.000 | Estándar |
| Sales Representative (default) | 12.000 | Básica |

### `fact_ventas` — tabla de hechos central

**Granularidad:** 1 documento = 1 línea de `stg_order_details` (clave compuesta OrderID + ProductID).

| Grupo | Campos |
|-------|--------|
| **Claves** | `order_detail_id`, `order_id`, `fecha_id`, `fecha_entrega_id` |
| **FKs dimensionales** | `cliente_id`, `empleado_id`, `producto_id`, `shipper_id`, `territorio_id` |
| **Cantidades y precios** | `cantidad`, `unit_price`, `descuento`, `freight` |
| **Métricas calculadas** | `subtotal`, `total_venta`, `costo_total`, `margen`, `margen_pct` |
| **Fechas** | `order_date`, `required_date`, `shipped_date` |
| **Logística** | `dias_entrega`, `entrega_puntual` |

### Índices MongoDB (creados por `setup_indexes`)

| Colección | Índice | Tipo |
|-----------|--------|------|
| `dim_fecha` | `fecha_id` | UNIQUE |
| `dim_cliente` | `cliente_id` | UNIQUE |
| `dim_empleado` | `empleado_id` | UNIQUE |
| `dim_producto` | `producto_id` | UNIQUE |
| `dim_shipper` | `shipper_id` | UNIQUE |
| `dim_territorio` | `territorio_id` | UNIQUE |
| `dim_metas_empleado` | (empleado_id, anio, trimestre) | UNIQUE compuesto |
| `fact_ventas` | `order_detail_id` | UNIQUE |
| `fact_ventas` | `fecha_id`, `cliente_id`, `total_venta`, `margen` | Consulta |

### Utilidad `_safe_int()` — manejo de NULL/NaN

Pandas representa valores SQL `NULL` como `float('nan')`. En Python, `nan is not None` es `True`, lo que causaba errores al hacer `int(nan)`. La función `_safe_int()` usa `pd.isna()` para convertir correctamente a `None` antes de insertar en MongoDB.

---

## ETL — Estructura de archivos

```
etl/
├── pipeline.py                 ← entrada única
├── requirements.txt
├── logs/                       ← generado al ejecutar
├── sql/
│   ├── northwind_oltp_supabase.sql      ← manual, una vez (fuente)
│   └── northwind_staging_supabase.sql   ← bootstrap automático
└── etl/
    ├── config.py
    ├── db_connection.py
    ├── bootstrap.py
    ├── extract.py
    ├── transform.py
    ├── validate.py
    ├── load_staging.py
    ├── load_dw.py
    ├── etl_meta.py
    └── logger_setup.py
```

El `.env` vive en la **raíz del repo** (`advanced-db-final-project/.env`), no dentro de `etl/`.

La Fase B (staging → MongoDB) está integrada en [`etl/etl/load_dw.py`](etl/etl/load_dw.py).

---

## ETL — `pipeline.py`

**Archivo:** [`etl/pipeline.py`](etl/pipeline.py)  
**Rol:** Orquestador central. **No contiene lógica de negocio** — solo coordina módulos, maneja errores y escribe el resumen final.

### Contrato de entrada/salida

| Entrada | Salida |
|---------|--------|
| Variables `.env` vía `config.py` | Logs en consola + `logs/etl_run_*.log` |
| Flags CLI opcionales | Datos en `stg_*` (Fase A) |
| | Colecciones MongoDB (Fase B) |
| | Registro en `etl_runs` |
| | Exit code 0 (éxito) o 1 (fallo) |

### Pasos de `main()` — detalle

| Paso log | Módulo | Acción | ¿Se omite con flags? |
|----------|--------|--------|---------------------|
| `[1/6] CONEXIONES` | `db_connection` | `get_source_engine` + `test_connection` | Nunca |
| `[2/6] BOOTSTRAP` | `bootstrap`, `etl_meta` | DDL si falta + `start_run()` | `--dry-run`, `--only-extract` |
| `[3/6] EXTRACCIÓN` | `extract` | `extract_all()` → dict de DataFrames | Nunca |
| `[4/6] TRANSFORMACIÓN` | `transform` | `transform_all()` | Nunca (salvo `--only-extract` que termina antes) |
| `[4b] VALIDACIÓN` | `validate` | `validate_all()` | `--skip-validate` o `VALIDATE_DATA=false` |
| `[5/6] CARGA STAGING` | `load_staging` | `load_staging_all()` con TRUNCATE | `--dry-run`, `--only-extract` |
| `[6/6] CARGA DW` | `load_dw` | `load_dw()` completo | `--dry-run`, `--skip-dw` |

### Manejo de errores

```python
try:
    # ... flujo completo ...
    etl_meta.finish_run(...)   # status = success
except Exception as e:
    etl_meta.fail_run(...)     # status = failed, guarda error_message
    sys.exit(1)
```

Si la Fase A falla, la Fase B **no se ejecuta**. Si la Fase B falla, el staging **ya tiene datos** de esa ejecución (útil para depurar).

### Flags CLI — casos de uso

| Flag | Cuándo usarlo | Ejemplo |
|------|---------------|---------|
| `--dry-run` | Probar conexión y transformaciones sin escribir nada | Primera vez que configuras `.env` |
| `--only-extract` | Verificar que el OLTP responde y tiene datos | Diagnóstico de red/credenciales |
| `--skip-validate` | Acelerar runs cuando ya confías en los datos | Desarrollo iterativo |
| `--skip-dw` | Cargar solo staging (sin MongoDB) | Cuando Atlas no está disponible |

### Variables en memoria durante la ejecución

| Variable | Contenido |
|----------|-----------|
| `raw_data` | `{tabla: DataFrame}` post-extract |
| `clean_data` | `{tabla: DataFrame}` post-transform |
| `load_summary` | `{tabla: n_registros}` post-staging |
| `dw_counts` | `{coleccion: n_docs}` post-MongoDB |
| `run_id`, `batch_id` | Identificadores de auditoría |

---

## ETL — `config.py`

**Archivo:** [`etl/etl/config.py`](etl/etl/config.py)  
**Rol:** Punto único de configuración. Separa **secretos** (`.env`) de **constantes de código** (tablas, rutas).

### Resolución de rutas

```python
_REPO_ROOT = Path(__file__).resolve().parents[2]   # raíz del repo
load_dotenv(_REPO_ROOT / ".env")                   # carga .env automáticamente
ETL_ROOT = Path(__file__).resolve().parents[1]     # carpeta etl/
```

Por eso el `.env` debe estar en `advanced-db-final-project/.env`, **no** dentro de `etl/`.

### Variables de entorno

| Variable | Default | Uso |
|----------|---------|-----|
| `SOURCE_DATABASE_URL` | *(vacío)* | URI PostgreSQL Supabase OLTP. **Session pooler :5432** recomendado. |
| `STAGING_DATABASE_URL` | *(vacío)* | URI PostgreSQL Supabase staging. |
| `MONGO_URI` | *(vacío)* | URI `mongodb+srv://...` de Atlas. |
| `MONGO_DB` | `northwind_dw` | Nombre de la base DW en Atlas. |
| `BATCH_SIZE` | `500` | Tamaño de lote para `to_sql` y `insert_many`. |
| `TRUNCATE_FIRST` | `true` | Si vaciar staging antes de cada carga. |
| `VALIDATE_DATA` | `true` | Si ejecutar `validate.py`. |
| `LOG_LEVEL` | `INFO` | Verbosidad del log (`DEBUG` muestra cada transformación). |

Valores booleanos aceptan: `1`, `true`, `yes`, `on` (case insensitive).

### Constantes de código (no van en `.env`)

| Constante | Valor | Por qué está en código |
|-----------|-------|------------------------|
| `SOURCE_TABLES` | 11 tablas en orden | Orden de dependencias lógicas; rara vez cambia |
| `TABLE_MAP` | `Categories` → `stg_categories`, etc. | Contrato entre extract y load_staging |
| `STAGING_DDL_FILE` | `etl/sql/northwind_staging_supabase.sql` | Ruta al bootstrap |
| `LOG_DIR` | `logs` | Relativo al directorio de ejecución (`cd etl/`) |

---

## ETL — `db_connection.py`

**Para qué sirve:** Crea conexiones SQLAlchemy a PostgreSQL.

### Funciones

| Función | Qué hace |
|---------|----------|
| `get_engine_from_url(url)` | Crea engine desde `postgresql://...` con `pool_pre_ping` (verifica conexión antes de usarla) |
| `get_source_engine(url)` | Engine para OLTP |
| `get_staging_engine(url)` | Engine para staging (pool de 5 conexiones) |
| `test_connection(engine, label)` | Ejecuta `SELECT 1`; retorna `True`/`False` y loguea resultado |
| `_build_url(cfg)` | Legacy: construye URL desde dict (LocalDB/MySQL) — solo compatibilidad |

---

## ETL — `bootstrap.py`

**Para qué sirve:** En la **primera ejecución**, crea tablas `stg_*` y `etl_runs` si no existen.

### Funciones

| Función | Qué hace |
|---------|----------|
| `staging_schema_exists(engine)` | Consulta `information_schema` buscando `stg_orders` |
| `ensure_staging_schema(engine, ddl_path)` | Si no existe esquema, ejecuta `northwind_staging_supabase.sql` |
| `_split_sql_statements(sql)` | Divide el archivo SQL en sentencias ejecutables |

**No hace en cada run:** no borra proyectos Supabase; no hace `DROP` de tablas si ya existen. El refresco de **datos** lo hace `load_staging.py` con `TRUNCATE`.

---

## ETL — `extract.py`

**Archivo:** [`etl/etl/extract.py`](etl/etl/extract.py)  
**Rol:** Capa **E**xtract de la Fase A. Ejecuta `SELECT` contra el OLTP y materializa todo en memoria como DataFrames pandas.

### Principio de diseño: extracción completa (full table scan)

No hay filtros `WHERE` ni joins en extract. Cada tabla se lee **entera** porque:
1. Northwind es pequeño (~3.300 filas totales).
2. Full refresh requiere el dataset completo cada vez.
3. Los joins y agregaciones ocurren en transform (Fase A) o load_dw (Fase B).

### `EXTRACT_QUERIES` — detalle por tabla

Diccionario con un `SELECT` por tabla. Nombres **entre comillas dobles** (`"Customers"`) porque PostgreSQL convierte identificadores sin comillas a minúsculas, y el DDL de Northwind usa PascalCase.

| Tabla fuente | Registros | Columnas extraídas | Notas |
|--------------|-----------|-------------------|-------|
| `Categories` | 8 | CategoryID, CategoryName, Description | Dimensión producto |
| `Suppliers` | 29 | ID, empresa, contacto, dirección | Dimensión producto |
| `Shippers` | 3 | ShipperID, CompanyName, Phone | Dimensión logística |
| `Customers` | 91 | ID, empresa, contacto, geografía | Dimensión cliente |
| `Employees` | 9 | ID, nombres, cargo, fechas, ReportsTo | Sin foto (BYTEA) |
| `Products` | 77 | ID, nombre, precio, stock, categoría, proveedor | Hecho potencial |
| `Orders` | 830 | ID, cliente, empleado, fechas, envío, flete | Cabecera de pedido |
| `Order Details` | 2.155 | OrderID, ProductID, UnitPrice, Quantity, Discount | **Tabla de hechos fuente** |
| `Region` | 4 | RegionID, RegionDescription (TRIM) | Auxiliar territorial |
| `Territories` | 53 | TerritoryID, descripción, RegionID | Auxiliar territorial |
| `EmployeeTerritories` | 49 | EmployeeID, TerritoryID | Puente M:N |

### Funciones

| Función | Entrada → Salida | Comportamiento ante error |
|---------|------------------|---------------------------|
| `extract_table(engine, table_name)` | nombre → `DataFrame` | Lanza excepción si no hay query |
| `extract_all(engine, table_list)` | lista → `(dict, [errores])` | Continúa con otras tablas; acumula errores |

**Tecnología:** `pd.read_sql(text(query), conn)` vía SQLAlchemy. La conexión se abre y cierra por tabla (no transacción larga).

---

## ETL — `transform.py`

**Archivo:** [`etl/etl/transform.py`](etl/etl/transform.py)  
**Rol:** Capa **T**ransform de la Fase A. Recibe DataFrames crudos y devuelve DataFrames conformados listos para staging.

### Patrón de diseño: transformador por tabla + dispatcher

Cada tabla tiene su función `transform_<tabla>()`. El diccionario `_TRANSFORMERS` mapea nombre de tabla → función. `transform_all()` itera el dict de entrada y aplica el transformador correspondiente.

Tablas sin entrada en `_TRANSFORMERS` pasan con `.copy()` sin cambios (Region, Territories, EmployeeTerritories).

### Utilidades internas

| Función | Regla | Detalle técnico |
|---------|-------|-----------------|
| `_clean_str(series)` | TR-001 | `astype(str).str.strip().str.upper()`; reemplaza `"NAN"` por `pd.NA` |
| `_to_decimal(series, n)` | TR-002/005 | `pd.to_numeric(errors="coerce").round(n)` |
| `_to_date(series)` | TR-003 | `pd.to_datetime().dt.normalize()` — elimina componente hora |

### Transformadores por tabla — resumen

| Función | Columnas afectadas | Columnas nuevas |
|---------|-------------------|-----------------|
| `transform_categories` | CategoryName, Description | — |
| `transform_suppliers` | CompanyName, Country, City, ContactName | — |
| `transform_shippers` | CompanyName | — |
| `transform_customers` | CustomerID, CompanyName, Country, City | — |
| `transform_employees` | FirstName, LastName, Title, fechas | `FullName` |
| `transform_products` | ProductName, UnitPrice, Discontinued | `STG_AlertaBajoReorden`, `STG_StockProyectado` |
| `transform_orders` | Fechas, Freight, ShipCountry/City | `STG_DiasEntrega`, `STG_EntregaPuntual` |
| `transform_order_details` | UnitPrice, Discount | `STG_ValorNeto` |

### Detalle crítico: tipos nullable en `transform_orders`

`STG_DiasEntrega` usa `pd.Int32Dtype()` y `STG_EntregaPuntual` usa `pd.Int8Dtype()`. Esto evita que pandas inserte `pd.NA` en columnas INTEGER de PostgreSQL, que causaba errores de tipo en versiones anteriores del pipeline (bug F2-01).

Ver fórmulas completas en [Catálogo TR-xxx](#etl--catálogo-de-transformaciones-tr-xxx).

---

## ETL — `validate.py`

**Para qué sirve:** Revisa calidad **antes** de escribir en staging. No detiene el pipeline por defecto; emite warnings en el log.

### Validadores

| Función | Reglas |
|---------|--------|
| `validate_order_details` | RQ-001 Discount ∈ [0,1]; RQ-002 Quantity > 0; RQ-003 UnitPrice ≥ 0 |
| `validate_orders` | RQ-004 ShippedDate ≥ OrderDate; RQ-005 RequiredDate ≥ OrderDate; RQ-006 OrderDate not null |
| `validate_products` | RQ-007 stock ≥ 0; RQ-009 precio ≥ 0; RQ-010 Discontinued ∈ {0,1} |
| `validate_customers` | RQ-015 CustomerID longitud 5; unicidad |

| Función | Qué hace |
|---------|----------|
| `validate_all(clean_data)` | Ejecuta todos los validadores aplicables; retorna `{tabla: n_issues}` |

---

## ETL — `load_staging.py`

**Archivo:** [`etl/etl/load_staging.py`](etl/etl/load_staging.py)  
**Rol:** Capa **L**oad de la Fase A. Persiste DataFrames en PostgreSQL staging.

### Estrategia de carga

1. **TRUNCATE** tabla destino (si `TRUNCATE_FIRST=true`).
2. Añadir columnas de metadatos al DataFrame en memoria.
3. **INSERT** por lotes con `df.to_sql(if_exists="append", method="multi")`.

`method="multi"` genera un solo `INSERT` con múltiples valores por lote, más eficiente que fila a fila.

### Funciones

| Función | Qué hace |
|---------|----------|
| `truncate_staging(engine, table_name)` | `TRUNCATE TABLE stg_xxx` dentro de transacción |
| `load_table(engine, source_name, df, ...)` | Trunca + metadatos + insert por lotes; retorna conteo |
| `load_all(engine, clean_data, table_order, ...)` | Itera `SOURCE_TABLES` en orden; retorna `(summary, errors)` |

### Metadatos de linaje (añadidos a cada fila)

| Columna | Valor | Propósito |
|---------|-------|-----------|
| `STG_LOAD_DATE` | `pd.Timestamp.now().normalize()` | Cuándo se cargó |
| `STG_SOURCE_NAME` | `"Northwind"` | De qué sistema viene |
| `STG_BATCH_ID` | `YYYYMMDDHHMMSS` | Agrupa filas de la misma ejecución |

El `STG_BATCH_ID` coincide con `batch_id` en `etl_runs` (mismo formato, generado en momentos cercanos).

### Mapeo fuente → staging (`TABLE_MAP` en config.py)

| Tabla fuente | Tabla staging | Registros típicos |
|--------------|---------------|-------------------|
| Categories | stg_categories | 8 |
| Suppliers | stg_suppliers | 29 |
| Shippers | stg_shippers | 3 |
| Customers | stg_customers | 91 |
| Employees | stg_employees | 9 |
| Region | stg_region | 4 |
| Territories | stg_territories | 53 |
| EmployeeTerritories | stg_employee_territories | 49 |
| Products | stg_products | 77 |
| Orders | stg_orders | 830 |
| Order Details | stg_order_details | 2.155 |

---

## ETL — `load_dw.py`

**Archivo:** [`etl/etl/load_dw.py`](etl/etl/load_dw.py)  
**Rol:** **Todo el pipeline de la Fase B** en un solo módulo (~530 líneas). Es el más complejo del proyecto.

### Flujo interno de `load_dw()`

```
1. read_staging_table() × 8 tablas
2. build_dim_fecha()
3. build_dim_cliente()      ← usa orders + order_details para agregar
4. build_dim_empleado()
5. build_dim_producto()     ← join categories + suppliers en memoria
6. build_dim_shipper()      ← promedia STG_DiasEntrega
7. build_dim_territorio()   ← deduplica país×ciudad
8. build_dim_metas_empleado()
9. build_fact_ventas()      ← usa dims ya construidas para lookups
10. MongoClient → drop() × 8 → insert_col() × 8 → setup_indexes()
```

### Funciones auxiliares

| Función | Propósito |
|---------|-----------|
| `read_staging_table()` | `pd.read_sql("SELECT * FROM ...")` → `list[dict]` |
| `to_dt()` | Normaliza fechas de pandas/SQL/ISO string a `datetime` |
| `fid()` | `datetime` → `"YYYYMMDD"` (surrogate key de fecha) |
| `_safe_int()` | Convierte enteros manejando `None` y `NaN` de pandas |

### Constructores de dimensiones — algoritmos

**`build_dim_cliente`** — el más elaborado:
1. Construye mapa `OrderID → CustomerID` desde `stg_orders`.
2. Itera `stg_order_details` sumando `STG_ValorNeto` por cliente.
3. Calcula `dias_inactivo` respecto a la última fecha de pedido del dataset.
4. Aplica reglas de segmentación (ver [dim_cliente](#etl--modelo-dw-colecciones-mongodb)).

**`build_dim_territorio`** — generación de surrogate key:
1. Itera clientes; clave natural = `country + city`.
2. Genera `territorio_id` = primeros 3 chars del país + primeros 2 de ciudad (`USA-SE` para Seattle, USA).
3. Resuelve colisiones añadiendo sufijo numérico (`USA-SE-1`).

**`build_fact_ventas`** — join en memoria:
1. `order_map = {OrderID: order_dict}` para lookup O(1).
2. Por cada línea de detalle: obtiene cabecera de pedido, calcula métricas, resuelve `territorio_id` vía país del cliente.
3. Prefiere `STG_ValorNeto` del staging sobre recalcular (single source of truth post-Fase A).

### Carga MongoDB

| Función | Detalle |
|---------|---------|
| `insert_col()` | `insert_many(ordered=False)` en lotes; tolera duplicados parciales con warning |
| `setup_indexes()` | 15+ índices: PKs únicos + índices de consulta para Power BI |
| `load_dw()` | Función pública llamada desde `pipeline.py`; retorna `{coleccion: count}` |

### Colecciones que lee vs. que ignora

**Lee:** `stg_customers`, `stg_employees`, `stg_products`, `stg_categories`, `stg_suppliers`, `stg_shippers`, `stg_orders`, `stg_order_details`.

**No lee (por ahora):** `stg_region`, `stg_territories`, `stg_employee_territories`. Están en staging para completitud pero el modelo estrella actual deriva territorio desde la geografía del cliente.

---

## ETL — `etl_meta.py`

**Para qué sirve:** Auditoría en tabla `etl_runs` (Supabase staging).

| Función | Qué hace |
|---------|----------|
| `start_run(engine)` | INSERT con `status='running'`; retorna `(run_id, batch_id)` |
| `finish_run(engine, run_id, rows_loaded, ...)` | UPDATE a `success` con filas, duración, tablas OK |
| `fail_run(engine, run_id, error_message, ...)` | UPDATE a `failed` con mensaje de error |

Consulta de verificación:

```sql
SELECT run_id, started_at, finished_at, status, duration_sec, rows_loaded
FROM etl_runs
ORDER BY started_at DESC
LIMIT 5;
```

---

## ETL — `logger_setup.py`

**Para qué sirve:** Configura logs en consola y archivo.

| Función | Qué hace |
|---------|----------|
| `setup_logger(log_dir, level)` | Crea carpeta `logs/`, archivo `etl_run_YYYYMMDD_HHMMSS.log` rotativo (5 MB × 3 backups), formato con timestamp + nivel + módulo |

---

## ETL — Scripts SQL

| Archivo | Cuándo ejecutarlo | Contenido |
|---------|-------------------|-----------|
| `sql/northwind_oltp_supabase.sql` | **Manual, una vez** en SQL Editor de `northwind-oltp` | 11 tablas OLTP + datos + FK |
| `sql/northwind_staging_supabase.sql` | **Automático** vía `bootstrap.py` en primera ejecución | 11 tablas `stg_*` + `etl_runs` + índices |

---

## ETL — Ejecución y automatización

### Setup inicial (una vez)

1. Crear proyectos Supabase `northwind-oltp` y `northwind-staging`.
2. Ejecutar `northwind_oltp_supabase.sql` en OLTP.
3. Copiar `.env.example` → `.env` en la raíz y completar URLs.
4. `pip install -r requirements.txt`

### Ejecución manual

```bash
cd etl/
pip install -r requirements.txt
python pipeline.py --dry-run      # prueba sin escribir
python pipeline.py                # ciclo completo OLTP → staging → MongoDB
python pipeline.py --skip-dw      # solo Fase A
```

### Verificación post-run

**Staging (Supabase SQL Editor):**

```sql
SELECT 'stg_orders' AS t, COUNT(*) FROM stg_orders
UNION ALL SELECT 'stg_order_details', COUNT(*) FROM stg_order_details;
```

**MongoDB Atlas:** ~2,155 docs en `fact_ventas`, ~91 en `dim_cliente`.

**Task Scheduler:** ver sección [Programación del ETL](#programación-del-etl-en-tu-pc-task-scheduler).

### Dependencias Python

Archivo [`etl/requirements.txt`](etl/requirements.txt):

| Paquete | Rol en el ETL |
|---------|---------------|
| `sqlalchemy` | Engines PostgreSQL, `text()`, `to_sql` |
| `pandas` | DataFrames en memoria (extract, transform, load) |
| `psycopg2-binary` | Driver PostgreSQL para Supabase |
| `numpy` | Cálculos vectorizados en transform |
| `python-dotenv` | Carga `.env` |
| `pymongo` | Cliente MongoDB Atlas (Fase B) |
| `openpyxl` | Export opcional (no usado en pipeline principal) |

---

## ETL — Métricas verificadas (último run)

Resultados de una ejecución exitosa en entorno cloud (junio 2026):

| Etapa | Métrica | Valor |
|-------|---------|-------|
| Extract | Tablas OK | 11/11 |
| Extract | Errores | 0 |
| Staging | Registros totales | 3.308 |
| Staging | `stg_orders` | 830 |
| Staging | `stg_order_details` | 2.155 |
| DW | Documentos totales | 3.184 |
| DW | `fact_ventas` | 2.155 |
| DW | `dim_fecha` | 672 |
| DW | `dim_cliente` | 91 |
| DW | `dim_metas_empleado` | 108 |
| Auditoría | `etl_runs.status` | `success` |
| Performance | Duración | ~72 s |

### Consultas de verificación post-run

**Staging (SQL Editor de `northwind-staging`):**

```sql
-- Conteos por tabla
SELECT 'stg_orders' AS tabla, COUNT(*) FROM stg_orders
UNION ALL SELECT 'stg_order_details', COUNT(*) FROM stg_order_details
UNION ALL SELECT 'stg_customers', COUNT(*) FROM stg_customers;

-- Últimas ejecuciones auditadas
SELECT run_id, started_at, finished_at, status, duration_sec, batch_id
FROM etl_runs
ORDER BY started_at DESC
LIMIT 5;

-- Detalle de la última ejecución exitosa
SELECT run_id, rows_loaded, tables_ok, error_message
FROM etl_runs
WHERE status = 'success'
ORDER BY started_at DESC
LIMIT 1;
```

**MongoDB Atlas (mongosh o script Python):**

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv("../.env")

client = MongoClient(os.environ["MONGO_URI"])
db = client[os.environ.get("MONGO_DB", "northwind_dw")]

for col in sorted(db.list_collection_names()):
    print(f"{col}: {db[col].count_documents({}):,}")

# Sanity check: suma de ventas
total = sum(d["total_venta"] for d in db.fact_ventas.find({}, {"total_venta": 1}))
print(f"Total ventas USD: ${total:,.2f}")
```

**Diagnóstico rápido local:**

```bash
cd etl/
python _check_env.py    # prueba las 3 conexiones sin cargar datos
```

---

## ETL — Cómo explicarlo en la sustentación

Guión estructurado para responder preguntas del jurado con vocabulario profesional.

### Pregunta: "¿Qué hace su ETL?"

> Implementamos un pipeline **batch** en Python que ejecuta un **full refresh** en dos fases. En la Fase A extraemos 11 tablas del OLTP en Supabase, aplicamos reglas de limpieza y enriquecimiento con pandas, validamos calidad, y cargamos el resultado en una zona staging en un segundo proyecto Supabase. En la Fase B leemos ese staging, conformamos un **modelo dimensional estrella** con siete dimensiones y una tabla de hechos, y lo materializamos en MongoDB Atlas como documentos JSON. Cada ejecución queda auditada en `etl_runs` con duración, conteos y estado.

### Pregunta: "¿Por qué staging si ya tienen MongoDB?"

> El staging cumple tres funciones: (1) **desacoplar** la fuente del destino — si falla MongoDB, los datos limpios ya están persistidos; (2) **trazabilidad** — podemos inspeccionar `STG_ValorNeto` y `STG_DiasEntrega` en SQL antes de modelar; (3) **reproducibilidad** — la Fase B puede re-ejecutarse leyendo staging sin volver a tocar el OLTP.

### Pregunta: "¿Por qué full refresh y no incremental?"

> Northwind tiene ~3.300 registros en staging — el full refresh tarda menos de 90 segundos y garantiza **idempotencia**: cada run deja el sistema en un estado conocido sin riesgo de duplicados ni registros huérfanos. Para un dataset estático académico es la estrategia correcta. Dejamos incremental (`watermark`) documentado como mejora futura.

### Pregunta: "¿Dónde ocurren las transformaciones de negocio?"

> En **dos puntos deliberados**: (1) Fase A en `transform.py` — limpieza, tipos, métricas operativas (`STG_ValorNeto`, días de entrega); (2) Fase B en `load_dw.py` — conformación dimensional (segmentación de clientes, calendario, metas de empleado, margen). Separamos *datos limpios* (staging) de *datos analíticos* (DW).

### Pregunta: "¿Cómo garantizan calidad de datos?"

> Tres capas: (1) reglas TR-xxx en transform (corrección activa, ej. descuentos fuera de rango → 0); (2) reglas RQ-xxx en validate (detección con logging); (3) constraints en DDL staging (PKs, tipos `NUMERIC`). Además, `etl_runs` registra cada ejecución para auditoría operativa.

### Pregunta: "¿Qué pasa si falla a mitad del pipeline?"

> El `try/except` de `pipeline.py` captura la excepción, llama a `etl_meta.fail_run()` con el mensaje de error, y termina con exit code 1. Si falla en Fase B, staging ya tiene los datos de esa ejecución. Si falla en Fase A, MongoDB conserva los datos del último run exitoso (no se hace drop hasta que Fase B empieza).

### Diagrama mental para la pizarra

```
[OLTP Supabase] --read--> [Python/pandas] --write--> [Staging Supabase]
                              |
                              +--- validate, log, audit (etl_runs)
                              |
[Staging Supabase] --read--> [Python/load_dw] --write--> [MongoDB Atlas] --> [Power BI]
```

---

## ETL — Solución de problemas

| Error | Causa probable | Solución |
|-------|----------------|----------|
| `SOURCE_DATABASE_URL no configurada` | Falta `.env` en raíz del repo | Copiar `.env.example` → `.env` y completar |
| `DATABASE_URL vacía` | Variable vacía o mal nombrada | Verificar nombres exactos en `.env` |
| `relation "Customers" does not exist` | OLTP sin DDL o tablas en minúsculas | Ejecutar `northwind_oltp_supabase.sql` en Supabase OLTP |
| `relation "customers" does not exist` | Queries sin comillas en PostgreSQL | El ETL usa `"Customers"` con comillas — no modificar |
| `stg_customers vacía` | Fase A no corrió o usaste `--dry-run` | Ejecutar `python pipeline.py` sin flags |
| Error pymongo / `ServerSelectionTimeout` | IP no en whitelist Atlas | Network Access → Add Current IP |
| `cannot convert float NaN to integer` | NULL de SQL leído como `NaN` por pandas | Corregido con `_safe_int()` en `load_dw.py` |
| `pd.NA` / type mismatch en enteros | Bug histórico SQL Server | Corregido con `pd.Int32Dtype()` en `transform_orders` |
| `column "X" does not exist` | Desajuste DDL staging vs DataFrame | Re-aplicar `northwind_staging_supabase.sql` |
| Bootstrap no crea tablas | `stg_orders` ya existe de un run parcial | Borrar tablas manualmente o verificar DDL |
| Pipeline lento (>5 min) | Red o pooler incorrecto | Usar Session pooler `:5432`, no Transaction `:6543` |
| `Modo --only-extract: pipeline detenido` | No es error — es el flag | Quitar `--only-extract` para run completo |

### Árbol de decisión para depurar

```
¿Falla en [1/6] CONEXIONES?
  → Revisar .env, credenciales Supabase, IP en Atlas

¿Falla en [3/6] EXTRACCIÓN?
  → ¿OLTP tiene las 11 tablas? → ejecutar northwind_oltp_supabase.sql

¿Falla en [5/6] CARGA STAGING?
  → ¿Existe DDL staging? → bootstrap o SQL manual
  → Revisar tipos de columnas STG_DiasEntrega (Int32)

¿Falla en [6/6] CARGA DW?
  → ¿Staging tiene datos? → SELECT COUNT(*) FROM stg_order_details
  → ¿MongoDB accesible? → python _check_env.py
  → Revisar _safe_int para campos nullable
```

---

## Modelo dimensional (esquema estrella)

```
                    dim_fecha
                        │
                    dim_cliente
                        │
dim_metas_empleado ─► dim_empleado
                        │
                    dim_producto
                        │
                    dim_shipper
                        │
                    dim_territorio
                        │
                 ┌──────▼ fact_ventas ──────┐
                 │  order_detail_id (PK)    │
                 │  FKs → dimensiones       │
                 │  cantidad, total_venta   │
                 │  margen, dias_entrega    │
                 └──────────────────────────┘
```

### Supuesto de costo (documentado)

```
costo_adquisicion = UnitPrice × 0.60
margen            = total_venta − costo_total
```

### dim_metas_empleado (auxiliar — P5)

| Cargo | Meta trimestral |
|-------|-----------------|
| Vice President, Sales | $18,000 |
| Sales Manager | $15,000 |
| Sales Representative | $12,000 |

---

## Colecciones MongoDB

| Colección | Documentos | Descripción |
|-----------|------------|-------------|
| `fact_ventas` | ~2,155 | Granularidad: línea de pedido |
| `dim_fecha` | ~672 | Calendario jul 1996 — may 1998 |
| `dim_cliente` | 91 | Con segmentación |
| `dim_empleado` | 9 | |
| `dim_producto` | 77 | |
| `dim_shipper` | 3 | |
| `dim_territorio` | ~69 | País × ciudad + zona |
| `dim_metas_empleado` | 108 | Metas trimestrales |

Índices principales los crea el script de carga (`order_detail_id` único, FKs indexadas).

---

## Medidas DAX

Tabla `_Medidas` — 30 medidas organizadas por P1–P10. Ejemplos:

```dax
[Total Ventas]         = SUM(fact_ventas[total_venta])
[Unidades Vendidas]  = SUM(fact_ventas[cantidad])
[% Cumplimiento Meta]= DIVIDE([Total Ventas], [Meta Periodo]) * 100
[Avg Dias Entrega]   = AVERAGEX(FILTER(fact_ventas, NOT ISBLANK([dias_entrega])), fact_ventas[dias_entrega])
[Es Cliente Inactivo] = IF([Días Sin Comprar] > 365, "Inactivo", "Activo")
```

Listado completo en `proyecto-bi/northwind_bi.SemanticModel/definition/model.tmdl`.

---

## Diseño de visualizaciones

4 páginas · canvas 1280×720 · tema BIBB (`#093824`).

| Página | Preguntas | Contenido principal |
|--------|-----------|---------------------|
| Resumen Ejecutivo | P1, P10 | KPIs, línea mensual, matrix calor, barras trimestrales |
| Clientes y Geografía | P2, P6, P9 | Top 10, mapa, tablas, línea comportamiento |
| Operaciones y Logística | P3, P4, P7 | Top productos, donut, área, gauge, logística |
| Desempeño y Auditoría | P5, P8 | Barras vs meta, scatter, tablas |

Wireframes detallados en sección original del README (§13 histórico) — ver commits anteriores si se necesita el ASCII art completo por página.

---

## Power BI — Conexión a MongoDB Atlas SQL

Esta sección documenta cómo llenar las **8 tablas del modelo PBIP** con los datos del DW en MongoDB Atlas (`northwind_dw`), incluyendo problemas reales encontrados en la integración (ODBC, navegación Power Query, claves duplicadas).

### Dos conexiones distintas a Atlas (no confundir)

| Uso | Protocolo | URI típica | ¿Necesita Atlas SQL / Data Federation? |
|-----|-----------|------------|----------------------------------------|
| **ETL Python** (`pymongo`, `_check_env.py`) | Driver nativo MongoDB | `mongodb+srv://...@cluster....mongodb.net/` | **No** |
| **Power BI Desktop** | Atlas SQL + ODBC | `mongodb://atlas-sql-....query.mongodb.net/...` | **Sí** |

Que `_check_env.py` responda `Mongo ping: OK` **no garantiza** que Power BI funcione: son endpoints diferentes.

### Requisitos previos en Atlas

1. Cluster con datos cargados por el ETL (`python pipeline.py`).
2. **Data Federation / Atlas SQL** habilitado:
   - Atlas → **Database → Clusters → Connect → Atlas SQL → Quick Start → Create**
   - Debe aparecer una instancia tipo **Cluster0 Atlas SQL** en **Services → Data Federation**.
3. **Database Access**: usuario con lectura (ej. `etl_northwind`).
4. **Network Access**: IP del PC de desarrollo autorizada.

### Requisitos previos en el PC (Power BI)

| Componente | Obligatorio | Notas |
|------------|-------------|-------|
| **Power BI Desktop** 64 bits | Sí | Conector integrado **MongoDB Atlas SQL** (no “MongoDB” legacy) |
| **MongoDB Atlas SQL ODBC Driver** 64 bits | Sí | [Descarga](https://www.mongodb.com/try/download/odbc-driver). Verificar en `odbcad32.exe` → pestaña Controladores |
| Conector `.pqx` opcional de MongoDB | No | El de Power BI Desktop suele bastar |

### Mapa tabla Power BI ↔ colección Mongo

| Tabla en el modelo | Colección en `northwind_dw` | Filas aprox. |
|--------------------|----------------------------|--------------|
| `dim_fecha` | `dim_fecha` | ~672 |
| `dim_cliente` | `dim_cliente` | ~91 |
| `dim_empleado` | `dim_empleado` | ~9 |
| `dim_producto` | `dim_producto` | ~77 |
| `dim_shipper` | `dim_shipper` | ~3 |
| `dim_territorio` | `dim_territorio` | ~69 |
| `dim_metas_empleado` | `dim_metas_empleado` | ~108 |
| `fact_ventas` | `fact_ventas` | ~2.155 |

Las consultas viven en `proyecto-bi/northwind_bi.SemanticModel/definition/tables/*.tmdl`. Los parámetros de conexión están en `expressions.tmdl`:

- `MongoDB Atlas URI` — endpoint Atlas SQL (**sin** usuario ni contraseña en la URI)
- `MongoDB Database` — `northwind_dw`

Copiar la URI desde Atlas → **Data Federation → Cluster0 Atlas SQL → Connect → Power BI Connector**.

### Flujo correcto con el PBIP existente (recomendado)

El proyecto **ya tiene** las 8 tablas, relaciones y medidas DAX. **No** volver a usar **Obtener datos** para importar tablas nuevas (eso crea duplicados `dim_cliente (2)`, etc.).

```
1. Cerrar Power BI sin guardar (si hay consultas duplicadas o rotas)
2. Abrir proyecto-bi/northwind_bi.pbip
3. Archivo → Opciones → Configuración de origen de datos
   → MongoDB Atlas SQL → credenciales Atlas (etl_northwind + contraseña)
4. Transformar datos → Administrar parámetros
   → verificar MongoDB Atlas URI y MongoDB Database
5. Archivo → Opciones → Carga de datos (archivo actual)
   → desmarcar "Carga en paralelo de tablas" (recomendado con ODBC)
6. Inicio → Actualizar
7. Validar conteos y medidas DAX ([Total Ventas], etc.)
```

**Modo de conectividad:** siempre **Importar** (no DirectQuery).

### Patrón Power Query M (3 pasos de navegación)

Cada tabla debe **bajar hasta su colección**. Solo el paso `Contents` devuelve la lista de bases (`northwind_dw`, `sample_mflix`, `test`) — eso **no** son los datos.

Ejemplo para `dim_cliente` (plantilla para las 8 tablas):

```powerquery
let
  Origen = MongoDBAtlasODBC.Contents(
      "mongodb://atlas-sql-....query.mongodb.net/northwind_dw?ssl=true&authSource=admin",
      "northwind_dw",
      []
  ),
  #"Navegación 1" = Origen{[Name = "northwind_dw", Kind = "Database"]}[Data],
  #"Navegación 2" = #"Navegación 1"{[Name = "dim_cliente", Kind = "Table"]}[Data]
in
  #"Navegación 2"
```

Cambiar solo el nombre en el último paso (`dim_fecha`, `fact_ventas`, etc.).

Equivalente en TMDL (sin pasos renombrados por la UI):

```powerquery
let
    Source   = MongoDBAtlasODBC.Contents(#"MongoDB Atlas URI", #"MongoDB Database"),
    Database = Source{[Name=#"MongoDB Database", Kind="Database"]}[Data],
    Table    = Database{[Name="dim_cliente", Kind="Table"]}[Data]
in
    Table
```

**Si la consulta solo tiene `Origen = Contents(...)`**, verás bases de datos en la vista previa, no filas de clientes — hay que añadir los pasos 2 y 3 (o copiar el M de una consulta que ya funcione).

### Caso especial: `dim_metas_empleado`

En Mongo la granularidad es **`empleado_id + anio + trimestre`** (108 filas: 9 empleados × 3 años × 4 trimestres). `empleado_id` **no es único** (el valor `1` aparece 12 veces).

- **No** marcar `empleado_id` como clave única (`isKey`) en el modelo.
- Las medidas DAX (`[Meta Periodo]`, etc.) filtran por los tres campos vía `CALCULATE`, sin relación directa a esta tabla.

### Qué NO hacer

| Acción | Por qué evitarla |
|--------|------------------|
| **Obtener datos → Mongo** con tablas ya en el modelo | Crea duplicados `(2)` y rompe relaciones |
| Borrar tablas del modelo y renombrar `(2)` | Pierdes jerarquías, formatos y metadatos TMDL |
| Usar URI `mongodb+srv://` del `.env` en Power BI | Es para el ETL, no para Atlas SQL |
| Marcar solo `northwind_dw` en el navegador y Cargar | Carga la base, no cada colección |
| Usar CSV en `csvs/` (raíz) | Ruta incorrecta; el Plan B válido es `plan-b/csvs/` |

### Errores frecuentes y soluciones

| Error | Causa probable | Solución |
|-------|----------------|----------|
| `Missing client library` | ODBC Driver no instalado | Instalar MongoDB Atlas SQL ODBC **64 bits**; reiniciar Power BI |
| `SQL_DRIVER_ODBC_VER: 03.80` | Fallo genérico de conexión ODBC | Reinstalar driver; credenciales; URI de Atlas SQL; IP en Network Access |
| `4 argumentos... espera 2 y 3` | Firma antigua de `Contents` | Usar `Contents(uri, db)` o `Contents(uri, db, [])` según versión |
| Vista previa muestra `northwind_dw`, `test`… | Consulta incompleta (solo paso 1) | Añadir navegación Database → Table |
| Duplicado en `empleado_id` (`dim_metas_empleado`) | `isKey` en columna no única | Quitar clave de `empleado_id` (ya corregido en TMDL) |
| `HRESULT 0x80040E4E` | Timeout ODBC / carga paralela | Desactivar carga en paralelo; actualizar tabla por tabla |
| `La carga se canceló... tabla anterior` | Efecto dominó | Arreglar la primera tabla que falla en la lista |
| Pide LocalDB o CSV | Consultas viejas sin reemplazar | Editor avanzado → patrón M de Atlas SQL en las 8 consultas |

### Checklist de verificación post-refresh

```
□ _check_env.py → Mongo ping OK, 8 colecciones
□ Power Query: 8 consultas sin sufijo (2)
□ Cada consulta termina en Kind = "Table" de su colección
□ fact_ventas ≈ 2.155 filas, dim_cliente ≈ 91
□ [Total Ventas] devuelve valor (~$1.26M)
□ 4 páginas del reporte muestran datos
```

### Plan B — si ODBC no coopera a tiempo

Los CSV en `plan-b/csvs/` tienen la misma estructura dimensional. Editar las consultas existentes para leer CSV (no crear tablas nuevas). Ver [Plan B — CSV sin infraestructura](#plan-b--csv-sin-infraestructura).

---

## Power BI — Validación de vistas y medidas

Las tablas pueden cargar datos correctamente y, aun así, las **páginas del reporte** mostrar `(En blanco)` en KPIs, segmentaciones de `anio` vacías y gráficos sin barras. Eso indica un problema de **modelo semántico** (tipos, relaciones o filtros), no de ausencia de datos en Mongo.

### Síntomas observados (jun 2026)

| Síntoma en el reporte | Páginas afectadas |
|----------------------|-------------------|
| KPIs `[Total Ventas]`, `[Num Ordenes]`, etc. = `(En blanco)` | Resumen Ejecutivo |
| Segmentación `anio` = `(En blanco)` | Todas |
| Tablas con nombres de cliente/producto pero medidas vacías | Clientes, Productos |
| Mapas y gráficos sin datos | Clientes, Operaciones |

### Diagnóstico paso a paso

#### 1. Confirmar que hay filas en las tablas (no solo en Power Query)

**Vista de datos** en Power BI:

| Tabla | Comprobar |
|-------|-----------|
| `fact_ventas` | ~2.155 filas; `total_venta` con números (no texto) |
| `dim_fecha` | ~672 filas; `anio` = 1996, 1997, 1998 |
| `dim_cliente` | ~91 filas |

Si aquí hay datos pero las medidas fallan → seguir con pasos 2–5.

#### 2. Corregir tipos de datos (causa más frecuente con ODBC)

Atlas SQL a veces importa números y fechas como **Texto**. Sin tipos correctos, `SUM()` devuelve blanco.

> **En el repo:** las 8 tablas TMDL ya incluyen `Table.TransformColumnTypes` en la partición M (corrección F4-11). Tras abrir el `.pbip`, **Cerrar y aplicar** debe aplicar esos tipos. Si Power BI conservó M local antiguo, cerrar sin guardar y reabrir el proyecto.

Si aún falla, en **Transformar datos** añadir manualmente **Transformar tipo de columna** (o paso M `Table.TransformColumnTypes`):

**`fact_ventas`** (mínimo):

```powerquery
Table.TransformColumnTypes(#"Navegación 2", {
    {"order_id", Int64.Type}, {"empleado_id", Int64.Type}, {"producto_id", Int64.Type},
    {"shipper_id", Int64.Type}, {"cantidad", Int64.Type},
    {"unit_price", type number}, {"descuento", type number}, {"freight", type number},
    {"subtotal", type number}, {"total_venta", type number},
    {"costo_total", type number}, {"margen", type number}, {"margen_pct", type number},
    {"order_date", type datetime}, {"required_date", type datetime}, {"shipped_date", type datetime},
    {"dias_entrega", Int64.Type}, {"entrega_puntual", type logical}
})
```

**`dim_fecha`** (crítico para segmentaciones `anio` / `trimestre`):

```powerquery
Table.TransformColumnTypes(#"Navegación 2", {
    {"fecha_id", type text},
    {"fecha_completa", type datetime},
    {"anio", Int64.Type},
    {"trimestre", Int64.Type},
    {"mes", Int64.Type},
    {"es_fin_semana", type logical}
})
```

Repetir lógica similar en dimensiones (`cliente_id` = texto, IDs numéricos = Entero, etc.).

#### 3. Verificar relaciones en Vista de modelo

Deben existir **7 relaciones activas** desde `fact_ventas`:

| Desde | Hacia | Columna |
|-------|-------|---------|
| `fact_ventas` | `dim_fecha` | `fecha_id` |
| `fact_ventas` | `dim_cliente` | `cliente_id` |
| `fact_ventas` | `dim_empleado` | `empleado_id` |
| `fact_ventas` | `dim_producto` | `producto_id` |
| `fact_ventas` | `dim_shipper` | `shipper_id` |
| `fact_ventas` | `dim_territorio` | `territorio_id` |

- Sin iconos de advertencia (tipos incompatibles).
- Cardinalidad: muchos a uno (*:1) desde hechos hacia dimensiones.
- `dim_metas_empleado` **no** tiene relación directa (las medidas P5 filtran con DAX).

Si una relación está rota: revisar que `fecha_id` y `cliente_id` sean **mismo tipo** en hechos y dimensiones (texto `YYYYMMDD` y texto respectivamente).

#### 4. Marcar tabla de fechas

**Vista de modelo** → `dim_fecha` → clic derecho → **Marcar como tabla de fechas** → columna `fecha_completa`.

Necesario para `[Ventas YTD]`, `[Ventas Año Anterior]` y segmentaciones temporales.

#### 5. Limpiar filtros del reporte

Las capturas muestran segmentaciones en `(En blanco)` que **filtran todo el reporte**:

1. Pestaña **Vista** → **Limpiar todas las segmentaciones** (o en cada página resetear `anio`, `trimestre`, `zona` a **Todas**).
2. Volver a probar una tarjeta con `[Total Ventas]`.

#### 6. Prueba rápida de medidas

Crear una tarjeta temporal:

```dax
Total Ventas Test = SUM(fact_ventas[total_venta])
```

| Resultado | Interpretación |
|-----------|----------------|
| ~$1.265.793 | Datos y tipos OK; el problema son filtros o campos del visual |
| (En blanco) | `total_venta` no es numérico o `fact_ventas` vacía en el modelo |
| Error DAX | Relación o columna renombrada |

### Resultado esperado por página (cuando el modelo está bien)

| Página | Contenido esperado |
|--------|-------------------|
| **Resumen Ejecutivo** | KPIs con totales; línea mensual; matriz trimestral |
| **Clientes y Geografía** | Top 10 clientes; mapa con países; tabla con ventas por cliente |
| **Operaciones y Logística** | Top productos; donut por categoría; gauges de entrega |
| **Desempeño y Auditoría** | Barras ventas vs meta; scatter rentabilidad |

Métricas de referencia: **2.155** líneas de hecho · **~$1.265.793** ventas totales · **~31,3 %** margen global.

---

## Proyecto PBIP / TMDL / PBIR

```
proyecto-bi/
├── northwind_bi.pbip
├── northwind_bi.SemanticModel/   ← TMDL, compatibilityLevel 1600
│   └── definition/
│       ├── expressions.tmdl      ← parámetros MongoDB Atlas URI / Database
│       ├── relationships.tmdl
│       └── tables/*.tmdl         ← 8 tablas + _Medidas
└── northwind_bi.Report/          ← PBIR, 4 páginas
```

### Abrir en Power BI Desktop

1. **Archivo → Abrir** → `proyecto-bi/northwind_bi.pbip`
2. Configurar credenciales Atlas SQL (primera vez). Ver [guía de conexión](#power-bi--conexión-a-mongodb-atlas-sql).
3. **Inicio → Actualizar** (no volver a **Obtener datos** si las 8 tablas ya existen)
4. Guardar

> **Import Mode:** tras actualizar, los datos quedan embebidos; la sustentación puede funcionar offline si se refrescó antes.

---

## Páginas del reporte

| Página | GUID | Preguntas | Visuales principales |
|--------|------|-----------|----------------------|
| Resumen Ejecutivo | `e3e43335c708953e4407` | P1 + P10 | KPIs, línea mensual, matriz trimestral |
| Clientes y Geografía | `d72257249741148631d0` | P2 + P6 + P9 | Top 10 clientes, mapa Azure, tabla inactivos |
| Operaciones y Logística | `d9ff3d19e960c247b7bd` | P3 + P4 + P7 | Top productos, donut categorías, gauges entrega |
| Desempeño y Auditoría | `ad7a10cd5c1f2cdd218f` | P5 + P8 | Ventas vs meta, scatter rentabilidad |

Tras cargar datos desde Mongo, validar que las páginas no muestren `(En blanco)` en medidas ni segmentaciones `anio`. Ver [Validación de vistas y medidas](#power-bi--validación-de-vistas-y-medidas).

---

## Plan B — CSV sin infraestructura

Si falla la red, los servicios cloud o el **ODBC de Atlas SQL** en la sustentación:

```bash
cd plan-b/
python verify_csvs.py     # valida csvs/ existentes
python generate_csvs.py   # requiere northwind.sql (T-SQL) en plan-b/
```

Conectar Power BI a `plan-b/csvs/*.csv` en lugar de Atlas/Supabase.

**Métricas esperadas:** 2,155 facts · $1,265,793 ventas · 31.3 % margen global.

---

## Estructura del repositorio

```
advanced-db-final-project/
├── Trabajo Final Base de Datos Avanzadas.pdf
├── .env.example                   # Plantilla credenciales (copiar a .env)
├── README.md                      # Documentación central (incl. guía ETL)
├── docs/
│   └── GUIA_ESTUDIO.md            # Guía de estudio y sustentación
├── etl/                           # Pipeline Python (OLTP → staging → DW)
│   ├── pipeline.py
│   ├── sql/                       # DDL Supabase
│   └── etl/                       # Módulos Python del paquete
├── scripts/                       # Mantenimiento PBIR (filtros slicer)
│   ├── audit_fix_report_filters.py
│   └── fix_slicer_null_filters.py
├── plan-b/                        # CSV de respaldo para Power BI
│   ├── csvs/
│   ├── generate_csvs.py
│   └── verify_csvs.py
└── proyecto-bi/                   # Power BI PBIP (ver proyecto-bi/README.md)
```

---

## Guía de configuración desde cero

Guía para que **cualquier persona** clone el repositorio, configure la infraestructura, ejecute el ETL y abra el reporte Power BI con datos del DW.

### Requisitos de software

| Herramienta | Versión | Uso |
|-------------|---------|-----|
| **Python** | 3.10+ | ETL |
| **Git** | Cualquier reciente | Clonar repo |
| **Cuenta Supabase** | 2 proyectos | OLTP + Staging |
| **Cuenta MongoDB Atlas** | Cluster M0+ | Data Warehouse |
| **Power BI Desktop** | 64 bits, actualizado | Reporte `.pbip` |
| **MongoDB Atlas SQL ODBC Driver** | 64 bits | Conexión Power BI → Atlas |

### Paso 0 — Clonar el repositorio

```bash
git clone https://github.com/Raikadier/advanced-db-final-project.git
cd advanced-db-final-project
```

### Paso 1 — Variables de entorno

```bash
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/macOS
```

Completar en `.env` (raíz del repo, **no** dentro de `etl/`):

| Variable | Dónde obtenerla |
|----------|-----------------|
| `SOURCE_DATABASE_URL` | Supabase → northwind-oltp → Connect → URI pooler :5432 |
| `STAGING_DATABASE_URL` | Supabase → northwind-staging → Connect → URI pooler :5432 |
| `MONGO_URI` | Atlas → Connect → Drivers → Python → `mongodb+srv://...` |
| `MONGO_DB` | `northwind_dw` |

Ver [Variables de entorno](#variables-de-entorno-env).

### Paso 2 — Supabase OLTP (fuente Northwind)

1. Crear proyecto `northwind-oltp` en Supabase.
2. SQL Editor → ejecutar `etl/sql/northwind_oltp_supabase.sql`.
3. Verificar ~11 tablas (`Customers`, `Orders`, `Products`, etc.).

Detalle: [Supabase — Proyecto fuente](#supabase--proyecto-fuente-northwind-oltp).

### Paso 3 — Supabase Staging

1. Crear proyecto `northwind-staging`.
2. El DDL de staging se aplica automáticamente en la primera ejecución del ETL (`bootstrap.py`).
3. Guardar `STAGING_DATABASE_URL` en `.env`.

Detalle: [Supabase — Proyecto staging](#supabase--proyecto-staging-northwind-staging).

### Paso 4 — MongoDB Atlas (DW)

1. Crear cluster Atlas (M0 Free suele bastar).
2. **Database Access** → usuario `etl_northwind` (read/write).
3. **Network Access** → IP del PC de desarrollo.
4. Guardar `MONGO_URI` y `MONGO_DB=northwind_dw` en `.env`.

Detalle: [MongoDB Atlas — Data Warehouse](#mongodb-atlas--data-warehouse).

### Paso 5 — Ejecutar el ETL

```bash
cd etl/
pip install -r requirements.txt
python _check_env.py          # diagnóstico: OLTP, Staging, Mongo deben responder OK
python pipeline.py            # ciclo completo → staging + Mongo DW
```

Tras éxito: 8 colecciones en `northwind_dw`, `fact_ventas` ≈ 2.155 documentos.

### Paso 6 — Atlas SQL para Power BI

1. Atlas → **Clusters → Connect → Atlas SQL → Quick Start → Create**.
2. Verificar instancia en **Services → Data Federation** (ej. `Cluster0 Atlas SQL`).
3. **Connect → Power BI Connector** → copiar URI y database `northwind_dw`.

### Paso 7 — ODBC Driver en Windows

1. Descargar [MongoDB Atlas SQL ODBC Driver](https://www.mongodb.com/try/download/odbc-driver) (**Windows x64**).
2. Instalar (PowerShell como administrador si hace falta).
3. Verificar: `Win+R` → `odbcad32.exe` → pestaña **Controladores**.

### Paso 8 — Abrir Power BI y cargar datos

1. Instalar [Power BI Desktop](https://powerbi.microsoft.com/desktop/) si no está instalado.
2. Abrir `proyecto-bi/northwind_bi.pbip`.
3. Seguir [Power BI — Conexión a MongoDB Atlas SQL](#power-bi--conexión-a-mongodb-atlas-sql):
   - Credenciales Atlas en **Configuración de origen de datos**.
   - Parámetros `MongoDB Atlas URI` y `MongoDB Database`.
   - Consultas M con 3 pasos de navegación por tabla.
   - **Importar** (no DirectQuery).
   - Desactivar carga en paralelo (recomendado).
4. **Inicio → Actualizar**.

### Paso 9 — Validar modelo y vistas

1. Comprobar conteos de tablas (ver [checklist post-refresh](#checklist-de-verificación-post-refresh)).
2. Si las páginas muestran `(En blanco)`: seguir [Power BI — Validación de vistas y medidas](#power-bi--validación-de-vistas-y-medidas).
3. Guardar el `.pbip`.

### Paso 10 — Plan B (sin Atlas SQL / ODBC)

Si el paso 8 falla de forma persistente:

```bash
cd plan-b/
python verify_csvs.py
```

Reconfigurar consultas Power Query para leer `plan-b/csvs/*.csv`. Ver [Plan B](#plan-b--csv-sin-infraestructura).

### Diagrama del flujo completo

```
git clone → .env → Supabase OLTP + Staging → Atlas cluster
    → python pipeline.py → northwind_dw (8 colecciones)
    → Atlas SQL + ODBC → northwind_bi.pbip → Actualizar
    → Validar medidas y 4 páginas del reporte
```

---

## Guía de ejecución rápida

Para quien **ya tiene** infraestructura configurada:

```bash
# 1. .env completo en la raíz del repo
# 2. ETL
cd etl/
pip install -r requirements.txt
python pipeline.py

# 3. Power BI
# Abrir proyecto-bi/northwind_bi.pbip → Actualizar
# Si vistas en blanco → ver "Validación de vistas y medidas"
```

Guías completas: [Configuración desde cero](#guía-de-configuración-desde-cero) · [Conexión Atlas SQL](#power-bi--conexión-a-mongodb-atlas-sql) · [Validación vistas](#power-bi--validación-de-vistas-y-medidas).

---

## Errores corregidos (auditoría)

| ID | Fase | Severidad | Corrección |
|----|------|-----------|------------|
| F2-01 | ETL | CRÍTICO | `pd.NA` → `pd.Int32Dtype()` en días de entrega |
| F2-03 | ETL | CRÍTICO | `_safe_int()` para `NaN` de pandas en Fase B (`load_dw.py`) |
| F2-02 | ETL | CRÍTICO | Tablas territoriales añadidas al extract |
| F3-01 | MongoDB | CRÍTICO | Lee staging real, no regex sobre `.sql` |
| F3-02 | MongoDB | CRÍTICO | Eliminados datos sintéticos con `random()` |
| F4-01–08 | TMDL | SINTAXIS | Correcciones de formato TMDL y relaciones |
| F4-09 | Power BI | CRÍTICO | `dim_metas_empleado`: quitado `isKey` de `empleado_id` (granularidad trimestral en Mongo) |
| F4-10 | Power BI | ALTO | Migración fuentes LocalDB/CSV → MongoDB Atlas SQL; patrón M con 3 pasos de navegación |
| F4-11 | Power BI | CRÍTICO | `TransformColumnTypes` en 8 tablas TMDL (ODBC importaba números/fechas como texto) |
| F4-12 | PBIR | CRÍTICO | Slicers con filtros guardados/sincronizados vaciaban el reporte (*flash then blank*); corregido con `scripts/audit_fix_report_filters.py` |

Detalle ampliado en [docs/GUIA_ESTUDIO.md](docs/GUIA_ESTUDIO.md). Referencia histórica: `Reporte_Errores_Corregidos.docx`.

---

## Punto extra — Tabular SSAS

El `northwind_bi.SemanticModel/` es un modelo **Tabular AS** en TMDL (`compatibilityLevel: 1600`). Power BI Desktop usa AS embebido vía `byPath` en `definition.pbir`.

Documentación: [TMDL overview](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview)

---

## Estado del proyecto

| Componente | Estado | Notas |
|------------|--------|-------|
| Análisis funcional | ✅ | Modelo dimensional + diccionario |
| ETL unificado (`pipeline.py`) | ✅ | Fase A + B + bootstrap + `etl_runs` — **verificado E2E** |
| SQL OLTP (`northwind_oltp_supabase.sql`) | ✅ | 11 tablas cargadas en Supabase |
| SQL Staging (`northwind_staging_supabase.sql`) | ✅ | Bootstrap automático |
| Supabase OLTP / Staging | ✅ | Conexiones OK; 3.308 registros en staging |
| MongoDB Atlas | ✅ | 8 colecciones; 3.184 documentos |
| Documentación ETL (README) | ✅ | Guía de estudio y sustentación |
| Documentación onboarding | ✅ | [Guía de configuración desde cero](#guía-de-configuración-desde-cero) |
| Power BI modelo | ✅ | TMDL + ~30 medidas DAX |
| Power BI reporte | ✅ | 4 páginas · ~39 visuals (diseño) |
| Power BI → Atlas SQL | ✅ | 8 tablas cargan datos desde Mongo vía ODBC |
| Power BI vistas / KPIs | ✅ | 4 páginas con datos; filtros slicer corregidos (F4-12); `[Total Ventas]` ≈ $1.265M |
| Plan B CSV | ✅ | `plan-b/csvs/` como respaldo |
| Task Scheduler | 📋 | Opcional para demos periódicas |

### Próximos pasos (opcionales)

1. Programar Task Scheduler para demostrar ejecuciones periódicas del ETL.
2. (Opcional) Implementar carga incremental con `watermark.py`.
3. (Opcional) Refactorizar consultas TMDL para usar parámetros `MongoDB Atlas URI` en lugar de URI hardcodeada por tabla.

---

## Licencia

MIT — ver [LICENSE](LICENSE)

---

*Última actualización documental: junio 2026 — ETL verificado E2E (run_id=4, 67 s), reporte Power BI validado en 4 páginas, [Guía de estudio](docs/GUIA_ESTUDIO.md) y scripts de mantenimiento PBIR. Este README es el índice central del proyecto; las decisiones nuevas se registran en [Registro de decisiones](#registro-de-decisiones-de-diseño).*
