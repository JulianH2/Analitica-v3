import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- Claves Secretas y Sesión ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-12345")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_COOKIE_SECURE = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "analytics_v3_"
    
    # Control de autenticación
    ENABLE_LOGIN = True

    # --- MSAL / Azure AD (Configuración Original) ---
    MSAL_CLIENT_ID = os.getenv("MSAL_CLIENT_ID")
    MSAL_CLIENT_SECRET = os.getenv("MSAL_CLIENT_SECRET")
    MSAL_AUTHORITY = os.getenv("MSAL_AUTHORITY")
    MSAL_SCOPE = ["User.Read"]
    REDIRECT_PATH = "/getAToken"
    
    # --- GOOGLE OAuth2 (Nueva Configuración) ---
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # --- Base de Datos (Azure SQL con Driver 18) ---
    SQL_SERVER = os.getenv("AZURE_SQL_SERVER")
    SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
    SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME")
    SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")
    # Usamos el Driver 18 como solicitaste
    SQL_DRIVER = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 18 for SQL Server")

    @classmethod
    def get_connection_string(cls):
        """Genera la cadena de conexión compatible con Driver 18"""
        if not all([cls.SQL_SERVER, cls.SQL_DATABASE, cls.SQL_USERNAME, cls.SQL_PASSWORD]):
            return None
            
        # IMPORTANTE: Driver 18 requiere TrustServerCertificate=yes si no tienes certificados SSL configurados
        params = (
            f"DRIVER={{{cls.SQL_DRIVER}}};"
            f"SERVER={cls.SQL_SERVER};"
            f"DATABASE={cls.SQL_DATABASE};"
            f"UID={cls.SQL_USERNAME};"
            f"PWD={cls.SQL_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=30;"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"