"""
db_connection.py — Fábrica de conexiones SQLAlchemy para fuente y staging
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import urllib.parse
import logging

logger = logging.getLogger(__name__)


def get_engine_from_url(url: str, *, pool_size: int | None = None):
    """Crea un engine SQLAlchemy desde una URL (postgresql://...)."""
    if not url or not url.strip():
        raise ValueError("DATABASE_URL vacía — revisa .env en la raíz del repo")

    kwargs = {"pool_pre_ping": True, "echo": False}
    if pool_size is not None:
        kwargs["pool_size"] = pool_size
        kwargs["max_overflow"] = 10

    return create_engine(url, **kwargs)


def _build_url(cfg: dict) -> str:
    """Construye URL desde dict legacy (LocalDB / MySQL). Solo para compatibilidad."""
    engine = cfg["engine"]
    db = cfg["database"]

    if engine == "mssql_localdb":
        drv = cfg.get("driver", "ODBC Driver 17 for SQL Server")
        pipe = cfg.get("pipe", "")
        server = pipe if pipe else r"(localdb)\MSSQLLocalDB"
        conn_str = (
            f"DRIVER={{{drv}}};"
            f"SERVER={server};"
            f"DATABASE={db};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
        return "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(conn_str)

    user = cfg["username"]
    pwd = cfg["password"]
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


def get_source_engine(database_url: str):
    return get_engine_from_url(database_url)


def get_staging_engine(database_url: str):
    return get_engine_from_url(database_url, pool_size=5)


def test_connection(engine, label: str) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"[OK] Conexión {label} establecida.")
        return True
    except OperationalError as e:
        logger.error(f"[ERROR] No se pudo conectar a {label}: {e}")
        return False
