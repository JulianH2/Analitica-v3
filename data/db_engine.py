from sqlalchemy import create_engine
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCONNECTED_MODE = False


class DBEngine:
    _engine = None

    @classmethod
    def get_engine(cls):
        global DISCONNECTED_MODE

        if cls._engine is None:
            try:
                connection_uri = Config.get_connection_string()

                if not connection_uri:
                    raise ValueError("Cadena de conexión vacía.")

                cls._engine = create_engine(
                    connection_uri,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )

                DISCONNECTED_MODE = False

            except Exception as e:
                logger.error(f"⚠️ Error al conectar a BD: {e}")
                logger.warning("⚠️ Corriendo en modo desconectado.")
                DISCONNECTED_MODE = True
                return None

        return cls._engine


db_engine = DBEngine.get_engine()
