"""
db_connection.py — Fábrica de conexiones SQLAlchemy para fuente y staging
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import urllib.parse
import logging

logger = logging.getLogger(__name__)


def _build_url(cfg: dict) -> str:
    engine = cfg["engine"]
    db     = cfg["database"]

    if engine == "mssql_localdb":
        drv  = cfg.get("driver", "ODBC Driver 17 for SQL Server")
        pipe = cfg.get("pipe", "")
        if pipe:
            server = pipe
        else:
            server = r"(localdb)\MSSQLLocalDB"
        conn_str = (
            f"DRIVER={{{drv}}};"
            f"SERVER={server};"
            f"DATABASE={db};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
        return "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(conn_str)

    user = cfg["username"]
    pwd  = cfg["password"]
    host = cfg["host"]
    port = cfg["port"]

    if engine == "mssql":
        drv = cfg.get("driver", "ODBC Driver 17 for SQL Server")
        conn_str = (
            f"DRIVER={{{drv}}};"
            f"SERVER={host},{port};"
            f"DATABASE={db};"
            f"UID={user};PWD={pwd};"
            f"TrustServerCertificate=yes;"
        )
        return "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(conn_str)
    if engine == "mysql":
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"
    if engine == "postgresql":
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    if engine == "sqlite":
        return f"sqlite:///{db}"
    raise ValueError(f"Motor no soportado: {engine}")


def get_source_engine(cfg: dict):
    url = _build_url(cfg)
    return create_engine(url, pool_pre_ping=True, echo=False)


def get_staging_engine(cfg: dict):
    url = _build_url(cfg)
    return create_engine(
        url, pool_pre_ping=True, echo=False,
        pool_size=5, max_overflow=10,
    )


def test_connection(engine, label: str) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"[OK] Conexión {label} establecida.")
        return True
    except OperationalError as e:
        logger.error(f"[ERROR] No se pudo conectar a {label}: {e}")
        return False