"""
pipeline.py — Orquestador principal del pipeline ETL
Northwind (fuente) → Staging Area

Uso:
    python pipeline.py                    # ejecuta ETL completo
    python pipeline.py --only-extract     # solo extracción (modo debug)
    python pipeline.py --skip-validate    # sin validaciones de calidad
    python pipeline.py --dry-run          # extrae y transforma, no carga
"""

import sys
import argparse
import logging
from datetime import datetime

# Módulos del pipeline
from etl.config          import (SOURCE_CONFIG, STAGING_CONFIG,
                                  SOURCE_TABLES, BATCH_SIZE, TRUNCATE_FIRST,
                                  VALIDATE_DATA, LOG_DIR, LOG_LEVEL)
from etl.logger_setup    import setup_logger
from etl.db_connection   import get_source_engine, get_staging_engine, test_connection
from etl.extract         import extract_all
from etl.transform       import transform_all
from etl.validate        import validate_all
from etl.load            import load_all


def parse_args():
    parser = argparse.ArgumentParser(description="ETL Northwind → Staging")
    parser.add_argument("--only-extract",  action="store_true", help="Solo extracción")
    parser.add_argument("--skip-validate", action="store_true", help="Omitir validaciones")
    parser.add_argument("--dry-run",       action="store_true", help="Sin carga al staging")
    return parser.parse_args()


def main():
    args = parse_args()
    logger = setup_logger(LOG_DIR, LOG_LEVEL)
    start  = datetime.now()

    logger.info("=" * 65)
    logger.info("  PIPELINE ETL — NORTHWIND → STAGING AREA")
    logger.info(f"  Inicio: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 65)

    # ── 1. Conexiones ───────────────────────────────────────────────────
    logger.info("\n[1/4] CONEXIONES")
    src_engine = get_source_engine(SOURCE_CONFIG)
    stg_engine = get_staging_engine(STAGING_CONFIG)

    if not test_connection(src_engine, "FUENTE (Northwind)"):
        logger.critical("Conexión a fuente fallida. Abortando.")
        sys.exit(1)

    if not args.dry_run and not test_connection(stg_engine, "DESTINO (Staging)"):
        logger.critical("Conexión a staging fallida. Abortando.")
        sys.exit(1)

    # ── 2. Extracción ───────────────────────────────────────────────────
    logger.info("\n[2/4] EXTRACCIÓN")
    raw_data, extract_errors = extract_all(src_engine, SOURCE_TABLES)

    if args.only_extract:
        for t, df in raw_data.items():
            logger.info(f"  {t}: {len(df):,} filas")
        logger.info("Modo --only-extract: pipeline detenido aquí.")
        return

    # ── 3. Transformación ───────────────────────────────────────────────
    logger.info("\n[3/4] TRANSFORMACIÓN")
    clean_data = transform_all(raw_data)

    # ── 3b. Validación de calidad ───────────────────────────────────────
    if VALIDATE_DATA and not args.skip_validate:
        logger.info("\n[3b] VALIDACIÓN DE CALIDAD")
        quality_report = validate_all(clean_data)
    else:
        quality_report = {}
        logger.info("\n[3b] Validación omitida")

    # ── 4. Carga ────────────────────────────────────────────────────────
    if args.dry_run:
        logger.info("\n[4/4] CARGA — omitida por --dry-run")
        for t, df in clean_data.items():
            logger.info(f"  {t}: {len(df):,} filas listas para cargar")
    else:
        logger.info("\n[4/4] CARGA AL STAGING")
        load_summary, load_errors = load_all(
            stg_engine,
            clean_data,
            table_order=SOURCE_TABLES,
            batch_size=BATCH_SIZE,
            truncate=TRUNCATE_FIRST,
        )

    # ── Resumen final ───────────────────────────────────────────────────
    elapsed = (datetime.now() - start).seconds
    logger.info("\n" + "=" * 65)
    logger.info("  RESUMEN FINAL")
    logger.info("=" * 65)
    logger.info(f"  Tablas extraídas :  {len(raw_data)}/{len(SOURCE_TABLES)}")
    logger.info(f"  Tablas con error :  {len(extract_errors)}")
    if not args.dry_run:
        total_rows = sum(load_summary.values())
        logger.info(f"  Registros cargados: {total_rows:,}")
        logger.info(f"  Tablas fallidas   : {len(load_errors)}")
    logger.info(f"  Duración total    : {elapsed}s")
    logger.info("=" * 65)


if __name__ == "__main__":
    main()
