"""
pipeline.py — Orquestador ETL Northwind
Fase A: OLTP (Supabase) → Staging (Supabase)
Fase B: Staging → DW (MongoDB Atlas)

Uso:
    python pipeline.py
    python pipeline.py --dry-run
    python pipeline.py --only-extract
    python pipeline.py --skip-validate
    python pipeline.py --skip-dw
"""

import sys
import argparse
import logging
from datetime import datetime

from etl.config import (
    SOURCE_DATABASE_URL,
    STAGING_DATABASE_URL,
    MONGO_URI,
    MONGO_DB,
    SOURCE_TABLES,
    BATCH_SIZE,
    TRUNCATE_FIRST,
    VALIDATE_DATA,
    LOG_DIR,
    LOG_LEVEL,
    STAGING_DDL_FILE,
)
from etl.logger_setup import setup_logger
from etl.db_connection import get_source_engine, get_staging_engine, test_connection
from etl.bootstrap import ensure_staging_schema
from etl.extract import extract_all
from etl.transform import transform_all
from etl.validate import validate_all
from etl.load_staging import load_all as load_staging_all
from etl.load_dw import load_dw
from etl import etl_meta


def parse_args():
    parser = argparse.ArgumentParser(description="ETL Northwind — OLTP → Staging → DW")
    parser.add_argument("--only-extract", action="store_true", help="Solo extracción")
    parser.add_argument("--skip-validate", action="store_true", help="Omitir validaciones")
    parser.add_argument("--dry-run", action="store_true", help="Sin carga a staging ni DW")
    parser.add_argument("--skip-dw", action="store_true", help="Solo Fase A (staging)")
    return parser.parse_args()


def main():
    args = parse_args()
    logger = setup_logger(LOG_DIR, LOG_LEVEL)
    start = datetime.now()
    run_id = None
    stg_engine = None

    logger.info("=" * 65)
    logger.info("  PIPELINE ETL — NORTHWIND (OLTP → STAGING → DW)")
    logger.info(f"  Inicio: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 65)

    load_summary = {}
    load_errors = []
    dw_counts = {}
    extract_errors = []

    try:
        # ── 1. Conexiones ─────────────────────────────────────────────────
        logger.info("\n[1/6] CONEXIONES")
        if not SOURCE_DATABASE_URL:
            raise ValueError("SOURCE_DATABASE_URL no configurada en .env")

        src_engine = get_source_engine(SOURCE_DATABASE_URL)
        if not test_connection(src_engine, "FUENTE (OLTP)"):
            raise RuntimeError("Conexión a fuente fallida")

        if not args.dry_run and not args.only_extract:
            if not STAGING_DATABASE_URL:
                raise ValueError("STAGING_DATABASE_URL no configurada en .env")
            stg_engine = get_staging_engine(STAGING_DATABASE_URL)
            if not test_connection(stg_engine, "DESTINO (Staging)"):
                raise RuntimeError("Conexión a staging fallida")

            # ── 2. Bootstrap staging ──────────────────────────────────────
            logger.info("\n[2/6] BOOTSTRAP STAGING")
            ensure_staging_schema(stg_engine, STAGING_DDL_FILE)

            run_id, batch_id = etl_meta.start_run(stg_engine, phase="full")
            logger.info(f"  batch_id={batch_id}")
        else:
            logger.info("\n[2/6] BOOTSTRAP — omitido (dry-run / only-extract)")

        # ── 3. Extracción ─────────────────────────────────────────────────
        logger.info("\n[3/6] EXTRACCIÓN (Fase A)")
        raw_data, extract_errors = extract_all(src_engine, SOURCE_TABLES)

        if args.only_extract:
            for t, df in raw_data.items():
                logger.info(f"  {t}: {len(df):,} filas")
            logger.info("Modo --only-extract: pipeline detenido.")
            return

        # ── 4. Transformación + validación ────────────────────────────────
        logger.info("\n[4/6] TRANSFORMACIÓN (Fase A)")
        clean_data = transform_all(raw_data)

        if VALIDATE_DATA and not args.skip_validate:
            logger.info("\n[4b] VALIDACIÓN DE CALIDAD")
            validate_all(clean_data)
        else:
            logger.info("\n[4b] Validación omitida")

        # ── 5. Carga staging ──────────────────────────────────────────────
        if args.dry_run:
            logger.info("\n[5/6] CARGA STAGING — omitida (--dry-run)")
            for t, df in clean_data.items():
                logger.info(f"  {t}: {len(df):,} filas listas")
        else:
            logger.info("\n[5/6] CARGA STAGING (Fase A)")
            load_summary, load_errors = load_staging_all(
                stg_engine,
                clean_data,
                table_order=SOURCE_TABLES,
                batch_size=BATCH_SIZE,
                truncate=TRUNCATE_FIRST,
            )
            if load_errors:
                raise RuntimeError(f"Errores en carga staging: {load_errors}")

        # ── 6. Carga DW ───────────────────────────────────────────────────
        if args.dry_run or args.skip_dw:
            logger.info("\n[6/6] CARGA DW — omitida")
        else:
            logger.info("\n[6/6] CARGA DW (Fase B)")
            dw_counts = load_dw(stg_engine, MONGO_URI, MONGO_DB, BATCH_SIZE)

        # ── Auditoría éxito ───────────────────────────────────────────────
        elapsed = (datetime.now() - start).total_seconds()
        rows_loaded = {**load_summary, **{f"dw_{k}": v for k, v in dw_counts.items()}}
        tables_ok = list(load_summary.keys()) + list(dw_counts.keys())

        if run_id and stg_engine:
            etl_meta.finish_run(
                stg_engine,
                run_id,
                rows_loaded=rows_loaded,
                tables_ok=tables_ok,
                tables_failed=[],
                duration_sec=elapsed,
            )

        logger.info("\n" + "=" * 65)
        logger.info("  RESUMEN FINAL")
        logger.info("=" * 65)
        logger.info(f"  Tablas extraídas   : {len(raw_data)}/{len(SOURCE_TABLES)}")
        logger.info(f"  Errores extract    : {len(extract_errors)}")
        if not args.dry_run:
            logger.info(f"  Registros staging  : {sum(load_summary.values()):,}")
            logger.info(f"  Docs DW            : {sum(dw_counts.values()):,}")
        logger.info(f"  Duración total     : {elapsed:.0f}s")
        logger.info("=" * 65)

    except Exception as e:
        elapsed = (datetime.now() - start).total_seconds()
        logger.critical(f"Pipeline abortado: {e}")
        if run_id and stg_engine:
            etl_meta.fail_run(
                stg_engine,
                run_id,
                str(e),
                elapsed,
                tables_failed=load_errors or extract_errors,
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
