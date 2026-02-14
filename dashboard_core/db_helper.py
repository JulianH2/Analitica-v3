import time
from sqlalchemy import create_engine, text
from config import Config
from asgiref.sync import sync_to_async

FAILURES = {}
BLOCK_SECONDS = 60
MAX_FAILS = 3


def _execute_dynamic_query_sync(db_name: str, query: str):
    if not db_name:
        return []

    now = time.time()
    state = FAILURES.get(db_name, {"count": 0, "blocked_until": 0})

    if now < state["blocked_until"]:
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
            rows = [dict(zip(keys, row)) for row in result.fetchall()]

        FAILURES[db_name] = {"count": 0, "blocked_until": 0}
        return rows

    except Exception as e:
        print(f"❌ Error SQL en {db_name}: {e}")

        state["count"] += 1
        if state["count"] >= MAX_FAILS:
            print(f"🚫 BD {db_name} bloqueada {BLOCK_SECONDS}s por errores repetidos.")
            state["blocked_until"] = time.time() + BLOCK_SECONDS

        FAILURES[db_name] = state
        return []

    finally:
        if engine:
            engine.dispose()


execute_dynamic_query = sync_to_async(_execute_dynamic_query_sync, thread_sensitive=True)
