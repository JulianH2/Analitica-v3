"""
Persistencia del historial de chats del copilot en Azure SQL.
Conversaciones por usuario (id_licencia) y empresa (base de datos actual).
IDs de conversación = UUID. Tablas: Analitica.ai_chat_conversations, Analitica.ai_chat_messages.
"""
import logging
import uuid
from typing import Any, Dict, List, Optional, Union

from services.global_db import execute_global_query

logger = logging.getLogger(__name__)


def list_conversations(id_licencia: int, empresa: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Lista conversaciones del usuario en la empresa, más recientes primero."""
    if not id_licencia or not empresa:
        return []
    q = """
    SELECT id, id_licencia, empresa, title, created_at, updated_at
    FROM Analitica.ai_chat_conversations
    WHERE id_licencia = :id_licencia AND empresa = :empresa
    ORDER BY updated_at DESC
    OFFSET 0 ROWS FETCH NEXT :limit ROWS ONLY
    """
    try:
        result = execute_global_query(q, {"id_licencia": id_licencia, "empresa": empresa, "limit": limit})
        rows = result if isinstance(result, list) else []
        if not rows:
            return []
        for r in rows:
            if r.get("id") is not None and hasattr(r["id"], "hex"):
                r["id"] = str(r["id"])
            if r.get("created_at"):
                r["created_at"] = r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"])
            if r.get("updated_at"):
                r["updated_at"] = r["updated_at"].isoformat() if hasattr(r["updated_at"], "isoformat") else str(r["updated_at"])
        return rows
    except Exception as e:
        logger.exception("list_conversations failed: %s", e)
        return []


def get_conversation_with_messages(conversation_id: Union[str, uuid.UUID]) -> Optional[Dict[str, Any]]:
    """Obtiene una conversación y sus mensajes. conversation_id = UUID (str o UUID)."""
    if not conversation_id:
        return None
    cid = str(conversation_id) if not isinstance(conversation_id, str) else conversation_id
    try:
        conv_q = """
        SELECT id, id_licencia, empresa, title, created_at, updated_at
        FROM Analitica.ai_chat_conversations WHERE id = :id
        """
        convs = execute_global_query(conv_q, {"id": cid})
        convs = convs if isinstance(convs, list) else []
        if not convs:
            return None
        conv = convs[0]
        if conv.get("id") is not None and hasattr(conv["id"], "hex"):
            conv["id"] = str(conv["id"])
        msg_q = """
        SELECT id, conversation_id, role, content, created_at
        FROM Analitica.ai_chat_messages
        WHERE conversation_id = :cid ORDER BY id ASC
        """
        messages = execute_global_query(msg_q, {"cid": cid})
        messages = messages if isinstance(messages, list) else []
        for m in messages:
            if m.get("created_at") and hasattr(m["created_at"], "strftime"):
                m["timestamp"] = m["created_at"].strftime("%H:%M")
            else:
                m["timestamp"] = ""
        conv["messages"] = [
            {"role": m["role"], "content": m["content"], "timestamp": m.get("timestamp", "")}
            for m in messages
        ]
        return conv
    except Exception as e:
        logger.exception("get_conversation_with_messages failed: %s", e)
        return None


def create_conversation(id_licencia: int, empresa: str, title: Optional[str] = None) -> Optional[str]:
    """Crea una conversación (id = UUID) y devuelve su id como string."""
    if not id_licencia or not empresa:
        return None
    title = (title or "Nueva conversación")[:256]
    new_id = str(uuid.uuid4())
    q = """
    INSERT INTO Analitica.ai_chat_conversations (id, id_licencia, empresa, title, created_at, updated_at)
    VALUES (:id, :id_licencia, :empresa, :title, SYSUTCDATETIME(), SYSUTCDATETIME())
    """
    try:
        result = execute_global_query(q, {"id": new_id, "id_licencia": id_licencia, "empresa": empresa, "title": title})
        if result is True:
            return new_id
        return None
    except Exception as e:
        logger.exception("create_conversation failed: %s", e)
        return None


def add_message(conversation_id: Union[str, uuid.UUID], role: str, content: str) -> bool:
    """Añade un mensaje a una conversación (conversation_id = UUID) y actualiza updated_at."""
    if not conversation_id or not role or content is None:
        return False
    cid = str(conversation_id) if not isinstance(conversation_id, str) else conversation_id
    role = (role or "user").strip()[:20]
    try:
        execute_global_query(
            """
            INSERT INTO Analitica.ai_chat_messages (conversation_id, role, content, created_at)
            VALUES (:conversation_id, :role, :content, SYSUTCDATETIME())
            """,
            {"conversation_id": cid, "role": role, "content": (content or "")[:4000]},
        )
        execute_global_query(
            """
            UPDATE Analitica.ai_chat_conversations
            SET updated_at = SYSUTCDATETIME(), title = CASE
                WHEN title IS NULL OR title = 'Nueva conversación' THEN LEFT(:snippet, 256)
                ELSE title
            END
            WHERE id = :id
            """,
            {"id": cid, "snippet": (content or "").strip()[:256]},
        )
        return True
    except Exception as e:
        logger.exception("add_message failed: %s", e)
        return False


def delete_conversation(conversation_id: Union[str, uuid.UUID]) -> bool:
    """Elimina una conversación y todos sus mensajes (ON DELETE CASCADE)."""
    if not conversation_id:
        return False
    cid = str(conversation_id) if not isinstance(conversation_id, str) else conversation_id
    try:
        execute_global_query(
            "DELETE FROM Analitica.ai_chat_conversations WHERE id = :id",
            {"id": cid},
        )
        return True
    except Exception as e:
        logger.exception("delete_conversation failed: %s", e)
        return False


def update_conversation_title(conversation_id: Union[str, uuid.UUID], title: str) -> bool:
    """Actualiza el título de una conversación (conversation_id = UUID)."""
    if not conversation_id:
        return False
    cid = str(conversation_id) if not isinstance(conversation_id, str) else conversation_id
    try:
        execute_global_query(
            "UPDATE Analitica.ai_chat_conversations SET title = :title, updated_at = SYSUTCDATETIME() WHERE id = :id",
            {"id": cid, "title": (title or "")[:256]},
        )
        return True
    except Exception as e:
        logger.exception("update_conversation_title failed: %s", e)
        return False
