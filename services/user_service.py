from data.db_service import db_service

class UserService:
    def get_user_databases(self, user_email):
        query_user = """
            SELECT u.id_usuario, u.id_tipo_usuario 
            FROM PowerZam.usuario u
            JOIN PowerZam.licencia l ON u.id_licencia = l.id_licencia
            WHERE l.correo_acceso = :email
        """
        user_df = db_service.run_query(query_user, {"email": user_email})
        
        if user_df.empty:
            return [], None

        id_tipo_usuario = int(user_df.iloc[0]["id_tipo_usuario"])
        
        if id_tipo_usuario == 99:
            query_dwh = """
                SELECT c.nombre AS nombre_cliente, dwh.nombre_bd_dwh AS base_de_datos
                FROM PowerZam.cliente c 
                JOIN PowerZam.cliente_bd_dwh dwh ON c.id_cliente = dwh.id_cliente
                WHERE c.id_estatus = 1 
                ORDER BY c.nombre;
            """
            params = {}
        else:
            query_dwh = """
                SELECT c.nombre AS nombre_cliente, dwh.nombre_bd_dwh AS base_de_datos
                FROM PowerZam.usuario u
                JOIN PowerZam.licencia l ON l.id_licencia = u.id_licencia
                JOIN PowerZam.cliente_usuario cu ON u.id_usuario = cu.id_usuario
                JOIN PowerZam.cliente c ON cu.id_cliente = c.id_cliente
                JOIN PowerZam.cliente_bd_dwh dwh ON c.id_cliente = dwh.id_cliente
                WHERE l.correo_acceso = :email AND c.id_estatus = 1;
            """
            params = {"email": user_email}

        dwh_df = db_service.run_query(query_dwh, params)
        databases = dwh_df.to_dict('records')
        
        return databases, id_tipo_usuario

user_service = UserService()