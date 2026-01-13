import bcrypt
from flask import session
from data.db_service import db_service

class UserService:
    def get_user_by_email(self, email):
        """
        Busca si el correo existe en PowerZam.licencia y retorna datos básicos.
        Se usa para validar si el usuario que viene de Microsoft/Google tiene permiso.
        """
        query = """
        SELECT 
            L.id_licencia, 
            L.correo_acceso,
            U.nombre, 
            U.apellido_paterno,
            U.id_tipo_usuario -- Necesitamos esto para saber si es Admin (99)
        FROM PowerZam.licencia L
        LEFT JOIN PowerZam.usuario U ON L.id_licencia = U.id_licencia
        WHERE L.correo_acceso = :email AND L.id_estatus = 1
        """

        df = db_service.run_query(query, {"email": email})
        
        if df.empty:
            return None
            
        return df.to_dict('records')[0]

    def validate_local_login(self, email, password_input):
        """Valida usuario y contraseña local (para el formulario manual)."""
        query = """
        SELECT id_licencia, password 
        FROM PowerZam.licencia 
        WHERE correo_acceso = :email AND id_estatus = 1
        """
        df = db_service.run_query(query, {"email": email})
        
        if df.empty:
            return None 
        
        user_record = df.to_dict('records')[0]
        stored_hash = user_record['password']

        if stored_hash and bcrypt.checkpw(password_input.encode('utf-8'), stored_hash):
            return self.get_user_by_email(email)
        
        return None

    def get_user_databases(self, email, id_tipo_usuario):
        if id_tipo_usuario == 99:
            query_dwh = """
            SELECT 
                c.nombre AS nombre_cliente, 
                c.url_logo_cliente AS url_logo, 
                dwh.nombre_bd_dwh AS base_de_datos
            FROM PowerZam.cliente c 
            JOIN PowerZam.cliente_bd_dwh dwh ON c.id_cliente = dwh.id_cliente
            WHERE c.id_estatus = 1 
            ORDER BY c.nombre;
            """
            params = {}
        else:
            query_dwh = """
            SELECT 
                c.nombre AS nombre_cliente, 
                c.url_logo_cliente AS url_logo, 
                dwh.nombre_bd_dwh AS base_de_datos
            FROM PowerZam.usuario u
            JOIN PowerZam.licencia l ON l.id_licencia = u.id_licencia
            JOIN PowerZam.cliente_usuario cu ON u.id_usuario = cu.id_usuario
            JOIN PowerZam.cliente c ON cu.id_cliente = c.id_cliente
            JOIN PowerZam.cliente_bd_dwh dwh ON c.id_cliente = dwh.id_cliente
            WHERE l.correo_acceso = :email AND c.id_estatus = 1;
            """
            params = {"email": email}

        dwh_df = db_service.run_query(query_dwh, params)
        
        if dwh_df.empty:
            return []

        return dwh_df.to_dict('records')

    def load_user_session(self, user_data):
        """Carga toda la información necesaria en la sesión de Flask."""
        email = user_data['correo_acceso']
        id_tipo_usuario = int(user_data.get('id_tipo_usuario') or 0)
        
        databases = self.get_user_databases(email, id_tipo_usuario)
        
        if not databases:
            return "Tu usuario existe, pero no tiene clientes/bases de datos asignadas."
            
        session["user"] = {
            "email": email,
            "name": user_data.get('nombre', 'Usuario'),
            "lastname": user_data.get('apellido_paterno', ''),
            "id_licencia": user_data['id_licencia'],
            "role_id": id_tipo_usuario
        }
        
        session["databases"] = databases
        session["role_id"] = id_tipo_usuario
        
        if databases:
            session["current_db"] = "PowerZAM_tinsadb" #databases[0]["base_de_datos"]
            session["current_client_logo"] = databases[0].get("url_logo") 
        
        session.modified = True 
        return True