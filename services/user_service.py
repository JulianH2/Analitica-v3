import bcrypt
from flask import session
from data.db_service import db_service
import logging

logger = logging.getLogger(__name__)

class UserService:
    def get_user_by_email(self, email):
        query = """
        SELECT 
            L.id_licencia, 
            L.correo_acceso,
            U.nombre, 
            U.apellido_paterno,
            U.id_tipo_usuario
        FROM PowerZam.licencia L
        LEFT JOIN PowerZam.usuario U ON L.id_licencia = U.id_licencia
        WHERE L.correo_acceso = :email AND L.id_estatus = 1
        """

        df = db_service.run_query(query, {"email": email})
        
        if df.empty:
            return None
            
        return df.to_dict('records')[0]

    def validate_local_login(self, email, password_input):
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
        email = user_data['correo_acceso']
        id_tipo_usuario = int(user_data.get('id_tipo_usuario') or 0)
        
        databases = self.get_user_databases(email, id_tipo_usuario)
        
        if not databases:
            logger.error(f"Usuario {email} no tiene bases de datos asignadas")
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
        
        tinsa_db = None
        first_db = None
        
        for db in databases:
            db_name = db.get("base_de_datos", "")
            client_name = db.get("nombre_cliente", "")
            
            logger.info(f"Base disponible: {db_name} - Cliente: {client_name}")
            
            if db_name == "PowerZAM_tinsadb":
                tinsa_db = db
                logger.info(f"✅ Encontrada base TINSA: {db_name}")
            
            if first_db is None:
                first_db = db
        
        if tinsa_db:
            selected_db = tinsa_db
            logger.info(f"🔧 Usando TINSA como base por defecto")
        elif first_db:
            selected_db = first_db
            logger.warning(f"⚠️ TINSA no encontrada. Usando primera disponible: {first_db.get('base_de_datos')}")
        else:
            selected_db = None
            logger.error(f"No hay bases de datos disponibles")
        
        if selected_db:
            session["current_db"] = selected_db.get("base_de_datos")
            session["current_client_logo"] = selected_db.get("url_logo")
            
            logger.info(f"""
            📊 RESUMEN DE CONEXIÓN:
            - Usuario: {email}
            - Bases disponibles: {len(databases)}
            - Base seleccionada: {session['current_db']}
            - Cliente: {selected_db.get('nombre_cliente')}
            - Logo: {session.get('current_client_logo', 'No disponible')}
            """)
        else:
            session["current_db"] = None
            session["current_client_logo"] = None
            logger.error(f"❌ No se pudo seleccionar ninguna base de datos")
        
        session.modified = True 
        return True