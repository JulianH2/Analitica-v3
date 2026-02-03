import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "llave-secreta-desarrollo")
    
    # --- CONFIGURACIÓN DE SESIONES ---
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_NAME = "analytics_session"
    
    # IMPORTANTE: Esto arregla el problema de "no se guardan"
    # Si estás en Azure (Producción), usa True. En local usa False.
    SESSION_COOKIE_SECURE = False  # <--- CAMBIO CLAVE
    SESSION_COOKIE_SAMESITE = "Lax" # <--- CAMBIO CLAVE
    SESSION_COOKIE_HTTPONLY = True

    ENABLE_LOGIN = True

    MSAL_CLIENT_ID = os.getenv("MSAL_CLIENT_ID")
    MSAL_CLIENT_SECRET = os.getenv("MSAL_CLIENT_SECRET")
    MSAL_AUTHORITY = os.getenv("MSAL_AUTHORITY")
    MSAL_SCOPE = ["openid", "email", "profile", "User.Read"]
    REDIRECT_PATH = "/getAToken"

    SQL_SERVER = os.getenv("AZURE_SQL_SERVER")
    SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
    SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME")
    SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")
    SQL_DRIVER = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 17 for SQL Server")

    @classmethod
    def get_connection_string(cls, target_db=None):
        if not all([cls.SQL_SERVER, cls.SQL_USERNAME, cls.SQL_PASSWORD]):
            return None
        database = target_db if target_db else cls.SQL_DATABASE

        params = (
            f"DRIVER={{{cls.SQL_DRIVER}}};"
            f"SERVER={cls.SQL_SERVER};"
            f"DATABASE={database};"
            f"UID={cls.SQL_USERNAME};"
            f"PWD={cls.SQL_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=30;"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"