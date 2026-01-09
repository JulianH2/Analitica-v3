import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_NAME = "analytics_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"

    ENABLE_LOGIN = True

    MSAL_CLIENT_ID = os.getenv("MSAL_CLIENT_ID")
    MSAL_CLIENT_SECRET = os.getenv("MSAL_CLIENT_SECRET")
    MSAL_AUTHORITY = os.getenv("MSAL_AUTHORITY")
    MSAL_SCOPE = ["openid", "email", "profile", "User.Read"]
    REDIRECT_PATH = "/getAToken"

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    SQL_SERVER = os.getenv("AZURE_SQL_SERVER")
    SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
    SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME")
    SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")
    SQL_DRIVER = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 18 for SQL Server")

    @classmethod
    def get_connection_string(cls):
        if not all([cls.SQL_SERVER, cls.SQL_DATABASE, cls.SQL_USERNAME, cls.SQL_PASSWORD]):
            return None

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
