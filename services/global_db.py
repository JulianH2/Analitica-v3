import sqlalchemy
from sqlalchemy import text
from config import Config

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        conn_str = Config.get_connection_string()
        if not conn_str:
            return None
        _engine = sqlalchemy.create_engine(conn_str)
    return _engine

def execute_global_query(query_sql, params=None):
    try:
        engine = get_engine()
        if not engine:
            return []
        with engine.connect() as conn:
            result = conn.execute(text(query_sql), params or {})
            if result.returns_rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
            conn.commit()
            return True
    except Exception as e:
        print(f"Error Global DB: {e}")
        return []