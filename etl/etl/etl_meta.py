"""
etl_meta.py — Registro de ejecuciones del pipeline en etl_runs (Supabase staging)
"""

import json
import logging
from datetime import datetime

from sqlalchemy import text

logger = logging.getLogger(__name__)


def _batch_id() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def start_run(engine, phase: str = "full") -> tuple[int, str]:
    """Inserta fila con status=running. Retorna (run_id, batch_id)."""
    batch_id = _batch_id()
    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                INSERT INTO etl_runs (status, batch_id, phase, source_name)
                VALUES ('running', :batch_id, :phase, 'Northwind')
                RETURNING run_id
                """
            ),
            {"batch_id": batch_id, "phase": phase},
        ).fetchone()
    run_id = int(row[0])
    logger.info(f"etl_runs: run_id={run_id} batch_id={batch_id} status=running")
    return run_id, batch_id


def finish_run(
    engine,
    run_id: int,
    rows_loaded: dict,
    tables_ok: list[str],
    tables_failed: list[str],
    duration_sec: float,
    phase: str = "full",
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE etl_runs
                SET finished_at = now(),
                    status = 'success',
                    phase = :phase,
                    rows_loaded = CAST(:rows_loaded AS jsonb),
                    tables_ok = :tables_ok,
                    tables_failed = :tables_failed,
                    duration_sec = :duration_sec
                WHERE run_id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "phase": phase,
                "rows_loaded": json.dumps(rows_loaded),
                "tables_ok": tables_ok,
                "tables_failed": tables_failed or None,
                "duration_sec": round(duration_sec, 2),
            },
        )
    logger.info(f"etl_runs: run_id={run_id} status=success duration={duration_sec:.1f}s")


def fail_run(
    engine,
    run_id: int,
    error_message: str,
    duration_sec: float,
    tables_failed: list[str] | None = None,
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE etl_runs
                SET finished_at = now(),
                    status = 'failed',
                    error_message = :error_message,
                    tables_failed = :tables_failed,
                    duration_sec = :duration_sec
                WHERE run_id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "error_message": error_message[:4000],
                "tables_failed": tables_failed or None,
                "duration_sec": round(duration_sec, 2),
            },
        )
    logger.error(f"etl_runs: run_id={run_id} status=failed")
