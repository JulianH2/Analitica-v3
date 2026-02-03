import pandas as pd
from sqlalchemy import create_engine, text
from config import Config
from asgiref.sync import sync_to_async

def _execute_dynamic_query_sync(db_name: str, query: str):
    if not db_name:
        return []
    conn_str = Config.get_connection_string(target_db=db_name)
    
    if not conn_str:
        return []

    engine = None
    try:
        engine = create_engine(conn_str, echo=False)
        with engine.connect() as connection:
            result = connection.execute(text(query))
            keys = result.keys()
            return [dict(zip(keys, row)) for row in result.fetchall()]
            
    except Exception as e:
        print(f"❌ Error SQL en {db_name}: {e}") 
        return [] 
        
    finally:
        if engine:
            engine.dispose()

execute_dynamic_query = sync_to_async(_execute_dynamic_query_sync, thread_sensitive=True)