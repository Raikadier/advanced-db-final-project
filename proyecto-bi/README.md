# Proyecto Power BI — Northwind BI

Proyecto **PBIP** (Power BI Project) con modelo semántico **TMDL** y reporte **PBIR**. Consume el Data Warehouse `northwind_dw` en MongoDB Atlas vía **Atlas SQL + ODBC** (modo Import).

## Abrir el proyecto

1. Instalar [Power BI Desktop](https://powerbi.microsoft.com/desktop/) 64 bits.
2. Instalar [MongoDB Atlas SQL ODBC Driver](https://www.mongodb.com/try/download/odbc-driver) 64 bits.
3. Abrir `northwind_bi.pbip`.
4. Configurar credenciales Atlas en **Archivo → Opciones → Configuración de origen de datos**.
5. **Inicio → Actualizar**.

> Guía completa: [README principal § Power BI](../README.md#power-bi--conexión-a-mongodb-atlas-sql) y [Guía de estudio](../docs/GUIA_ESTUDIO.md).

## Estructura

```
proyecto-bi/
├── northwind_bi.pbip                    ← punto de entrada
├── northwind_bi.SemanticModel/
│   └── definition/
│       ├── expressions.tmdl             ← parámetros URI Atlas SQL
│       ├── relationships.tmdl           ← 7 relaciones activas desde fact_ventas
│       ├── model.tmdl
│       └── tables/
│           ├── fact_ventas.tmdl
│           ├── dim_*.tmdl               ← 7 dimensiones
│           └── _Medidas.tmdl            ← ~30 medidas DAX (P1–P10)
└── northwind_bi.Report/
    ├── definition/
    │   ├── report.json
    │   └── pages/                       ← 4 páginas
    └── AUDIT-report-filters.json        ← auditoría slicers (jun 2026)
```

## Modelo semántico

### Tablas (9)

| Tabla | Origen MongoDB | Filas aprox. |
|-------|----------------|--------------|
| `fact_ventas` | `fact_ventas` | 2.155 |
| `dim_fecha` | `dim_fecha` | 672 |
| `dim_cliente` | `dim_cliente` | 91 |
| `dim_empleado` | `dim_empleado` | 9 |
| `dim_producto` | `dim_producto` | 77 |
| `dim_shipper` | `dim_shipper` | 3 |
| `dim_territorio` | `dim_territorio` | 69 |
| `dim_metas_empleado` | `dim_metas_empleado` | 108 |
| `_Medidas` | Calculada | ~30 medidas |

### Relaciones activas

`fact_ventas` se relaciona con 6 dimensiones por FK (`fecha_id`, `cliente_id`, `empleado_id`, `producto_id`, `shipper_id`, `territorio_id`). `dim_metas_empleado` se relaciona con `dim_empleado` para contexto de metas (P5).

### Medidas clave

```dax
[Total Ventas]         = SUM(fact_ventas[total_venta])      -- ~$1.265M
[Num Ordenes]          = DISTINCTCOUNT(fact_ventas[order_id])
[Clientes Activos]     = DISTINCTCOUNT(fact_ventas[cliente_id])
[% Margen Promedio]    = DIVIDE([Total Margen], [Total Ventas]) * 100
[% Cumplimiento Meta]  = DIVIDE([Total Ventas], [Meta Periodo]) * 100
```

## Páginas del reporte

| Página | GUID | Preguntas |
|--------|------|-----------|
| Resumen Ejecutivo | `e3e43335c708953e4407` | P1, P10 |
| Clientes y Geografía | `d72257249741148631d0` | P2, P6, P9 |
| Operaciones y Logística | `d9ff3d19e960c247b7bd` | P3, P4, P7 |
| Desempeño y Auditoría | `ad7a10cd5c1f2cdd218f` | P5, P8 |

## Mantenimiento de filtros (slicers)

Si el reporte muestra `(En blanco)` tras cargar datos:

```bash
# Desde la raíz del repo
python scripts/audit_fix_report_filters.py
```

Cierra y reabre el `.pbip`, **Actualizar** y **Limpiar todas las segmentaciones**.

Ver [Guía de estudio § 5](../docs/GUIA_ESTUDIO.md#5-power-bi--corrección-del-reporte-en-blanco).

## Prerrequisitos de datos

El ETL debe haber cargado MongoDB antes del refresh:

```bash
cd ../etl/
python _check_env.py    # 8 colecciones OK
python pipeline.py      # recarga DW
```

## Plan B (sin ODBC)

Usar CSV en `../plan-b/csvs/` y reconfigurar consultas M. Ver [Plan B](../README.md#plan-b--csv-sin-infraestructura).
