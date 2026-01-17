import os
from django.db import connections
from django.conf import settings
from asgiref.sync import sync_to_async


def _execute_dynamic_query_sync(session_db_config: str, sql_query: str):
    base = settings.DATABASES["default"].copy()
    base.update({
        "NAME": session_db_config
    })
    connections.databases["client_db"] = base

    try:
        with connections["client_db"].cursor() as cursor:
            cursor.execute(sql_query)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []
    finally:
        try:
            connections["client_db"].close()
        finally:
            if "client_db" in connections.databases:
                del connections.databases["client_db"]

execute_dynamic_query = sync_to_async(_execute_dynamic_query_sync, thread_sensitive=True)
