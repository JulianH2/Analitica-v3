# Scripts

## Historial de chats del copilot (Azure SQL)

Para que el historial de chats de Zamy se guarde en la base de datos, ejecuta **una vez** el script SQL en tu base `PowerZAM_AnaliticaDesarrollo`:

```bash
# Con sqlcmd (o desde Azure Data Studio / SSMS):
sqlcmd -S powerzamsql.database.windows.net -d PowerZAM_AnaliticaDesarrollo -U <usuario> -P <contraseña> -i init_ai_chat_history.sql
```

Crea el esquema `Analitica` y las tablas:

- **Analitica.ai_chat_conversations**: una fila por conversación; `id` es **UUID** (UNIQUEIDENTIFIER). Por `id_licencia` y `empresa` (base actual).
- **Analitica.ai_chat_messages**: mensajes de cada conversación (`conversation_id` = UUID).

**Si ya tenías una versión anterior del script** (con `id` INT en conversaciones), borra las tablas y vuelve a ejecutar:

```sql
IF OBJECT_ID('Analitica.ai_chat_messages', 'U') IS NOT NULL DROP TABLE Analitica.ai_chat_messages;
IF OBJECT_ID('Analitica.ai_chat_conversations', 'U') IS NOT NULL DROP TABLE Analitica.ai_chat_conversations;
-- Luego ejecuta init_ai_chat_history.sql
```

El resto lo hace la aplicación al usar el botón de historial y al enviar mensajes.
