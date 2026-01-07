from sqlalchemy import create_engine
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBEngine:
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            try:
                connection_uri = Config.get_connection_string()
                
                if not connection_uri:
                    raise ValueError("La cadena de conexión no pudo ser generada. Revisa el .env")

                cls._engine = create_engine(
                    connection_uri,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True
                )
            except Exception as e:
                logger.error(f"⚠️ Error al conectar a BD: {e}")
                logger.warning("⚠️ Corriendo en modo desconectado (Mock Data).")
                return None
        return cls._engine

db_engine = DBEngine.get_engine()