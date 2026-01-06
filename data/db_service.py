import pandas as pd
from sqlalchemy import create_engine, text
from config import Config

class DBService:
    def __init__(self):
        self.engine = None
        conn_str = Config.get_connection_string()
        
        if conn_str:
            self.engine = create_engine(conn_str, echo=False)
        else:
            print("⚠️ No se pudo crear el Connection String. Revisa tu .env")

    def run_query(self, query, params=None):
        if not self.engine:
            return pd.DataFrame()
        
        try:
            with self.engine.connect() as connection:
                return pd.read_sql(text(query), connection, params=params)
        except Exception as e:
            print(f"❌ Error SQL: {e}")
            return pd.DataFrame()

db_service = DBService()