-- Historial de chats del copilot Zamy (Azure SQL - PowerZAM_AnaliticaDesarrollo)
-- Ejecutar una vez. IDs de conversación = UUID. Por usuario (id_licencia) y empresa (base actual).
-- Si ya ejecutaste una versión anterior con id INT, borra antes: DROP TABLE Analitica.ai_chat_messages; DROP TABLE Analitica.ai_chat_conversations;

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Analitica')
BEGIN
    EXEC('CREATE SCHEMA Analitica');
END
GO

IF OBJECT_ID('Analitica.ai_chat_conversations', 'U') IS NULL
BEGIN
    CREATE TABLE Analitica.ai_chat_conversations (
        id UNIQUEIDENTIFIER NOT NULL PRIMARY KEY DEFAULT NEWID(),
        id_licencia INT NOT NULL,
        empresa NVARCHAR(128) NOT NULL,
        title NVARCHAR(256) NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ai_chat_conversations_user_empresa
        ON Analitica.ai_chat_conversations (id_licencia, empresa);
    CREATE INDEX IX_ai_chat_conversations_updated
        ON Analitica.ai_chat_conversations (updated_at DESC);
END
GO

IF OBJECT_ID('Analitica.ai_chat_messages', 'U') IS NULL
BEGIN
    CREATE TABLE Analitica.ai_chat_messages (
        id INT IDENTITY(1,1) PRIMARY KEY,
        conversation_id UNIQUEIDENTIFIER NOT NULL,
        role NVARCHAR(20) NOT NULL,
        content NVARCHAR(MAX) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_ai_chat_messages_conversation
            FOREIGN KEY (conversation_id) REFERENCES Analitica.ai_chat_conversations(id) ON DELETE CASCADE
    );
    CREATE INDEX IX_ai_chat_messages_conversation
        ON Analitica.ai_chat_messages (conversation_id);
END
GO
