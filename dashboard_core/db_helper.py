import time
import logging
from sqlalchemy import create_engine, text, event
from sqlalchemy.pool import NullPool
from config import Config
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

FAILURES = {}

BLOCK_SECONDS = 30
MAX_FAILS = 2
QUERY_TIMEOUT = 15


def reset_db_failures(db_name: str = None): # type: ignore
    global FAILURES
    if db_name:
        if db_name in FAILURES:
            logger.info(f"🔄 Reseteando fallos para BD: {db_name}")
            del FAILURES[db_name]
    else:
        logger.info("🔄 Reseteando todos los fallos de BD")
        FAILURES.clear()


def get_db_status(db_name: str) -> dict:
    if db_name not in FAILURES:
        return {"status": "ok", "failures": 0, "blocked": False}

    state = FAILURES[db_name]
    now = time.time()
    is_blocked = now < state.get("blocked_until", 0)

    return {
        "status": "blocked" if is_blocked else "warning",
        "failures": state.get("count", 0),
        "blocked": is_blocked,
        "blocked_until": state.get("blocked_until", 0) if is_blocked else None
    }


def validate_db_quick(db_name: str) -> bool:
    if not db_name:
        return False

    conn_str = Config.get_connection_string(target_db=db_name)
    if not conn_str:
        return False

    engine = None
    try:
        engine = create_engine(
            conn_str,
            echo=False,
            poolclass=NullPool,
            connect_args={"timeout": 3}
        )

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info(f"✅ Validación rápida exitosa para: {db_name}")
        return True

    except Exception as e:
        logger.warning(f"⚠️ Validación rápida falló para {db_name}: {str(e)[:100]}")
        return False

    finally:
        if engine:
            engine.dispose()


def _execute_dynamic_query_sync(db_name: str, query: str):
    if not db_name:
        logger.warning("⚠️ Intento de consulta sin nombre de BD")
        return []

    now = time.time()
    state = FAILURES.get(db_name, {"count": 0, "blocked_until": 0})

    if now < state["blocked_until"]:
        seconds_left = int(state["blocked_until"] - now)
        logger.warning(f"🚫 BD {db_name} bloqueada por {seconds_left}s más")
        return []

    conn_str = Config.get_connection_string(target_db=db_name)
    if not conn_str:
        logger.error(f"❌ No se pudo obtener connection string para: {db_name}")
        return []

    engine = None
    start_time = time.time()

    try:
        engine = create_engine(
            conn_str,
            echo=False,
            poolclass=NullPool,
            connect_args={"timeout": QUERY_TIMEOUT}
        )

        @event.listens_for(engine, "before_cursor_execute", retval=True)
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            cursor.execute(f"SET LOCK_TIMEOUT {QUERY_TIMEOUT * 1000};")
            return statement, params

        with engine.connect() as connection:
            result = connection.execute(text(query))
            keys = result.keys()
            rows = [dict(zip(keys, row)) for row in result.fetchall()]

        if db_name in FAILURES:
            FAILURES[db_name] = {"count": 0, "blocked_until": 0}

        elapsed = time.time() - start_time
        logger.debug(f"✅ Consulta exitosa en {db_name} ({elapsed:.2f}s)")
        return rows

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)

        is_schema_error = any(x in error_msg for x in [
            "Invalid object name",
            "Invalid column name",
            "not exist"
        ])

        is_timeout = any(x in error_msg for x in [
            "timeout",
            "Timeout",
            "timed out"
        ])

        if is_schema_error:
            logger.error(f"❌ Error de esquema en {db_name}: {error_msg[:200]}")
        elif is_timeout:
            logger.warning(f"⏱️ Timeout en {db_name} después de {elapsed:.2f}s")
        else:
            logger.error(f"❌ Error SQL en {db_name}: {error_msg[:200]}")

        state["count"] += 1

        if state["count"] >= MAX_FAILS:
            state["blocked_until"] = time.time() + BLOCK_SECONDS
            logger.error(
                f"🚫 BD {db_name} BLOQUEADA por {BLOCK_SECONDS}s "
                f"(fallos consecutivos: {state['count']})"
            )
        else:
            logger.warning(f"⚠️ Fallo {state['count']}/{MAX_FAILS} para {db_name}")

        FAILURES[db_name] = state
        return []

    finally:
        if engine:
            engine.dispose()


execute_dynamic_query = sync_to_async(
    _execute_dynamic_query_sync,
    thread_sensitive=False
)
