"""
logger_setup.py — Configura logging a consola y archivo rotativo
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(log_dir: str = "logs", level: str = "INFO") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)

    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"etl_run_{ts}.log")

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Consola
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # Archivo rotativo (5 MB × 3 backups)
    fh = RotatingFileHandler(log_file, maxBytes=5_242_880, backupCount=3, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    return root
