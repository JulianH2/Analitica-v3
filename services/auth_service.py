from flask import session, url_for, request, redirect
import msal
from config import Config
from services import user_service

class AuthService:
    def __init__(self):
        self.app = msal.ConfidentialClientApplication(
            Config.MSAL_CLIENT_ID,
            authority=Config.MSAL_AUTHORITY,
            client_credential=Config.MSAL_CLIENT_SECRET,
        )

    def build_auth_flow(self, redirect_uri):
        return self.app.initiate_auth_code_flow(
            Config.MSAL_SCOPE,
            redirect_uri=redirect_uri
        )

    def get_token_from_flow(self, flow, auth_response):
        return self.app.acquire_token_by_auth_code_flow(
            flow,
            auth_response
        )

    def login(self):
        """Paso 1: Generar la URL de autenticación de Microsoft"""
        #redirect_uri = url_for("get_token", _external=True)
        redirect_uri = "http://localhost:8000/getAToken"
        
        flow = self.app.initiate_auth_code_flow(
            Config.MSAL_SCOPE,
            redirect_uri=redirect_uri
        )
        
        # Guardamos el 'flow' en la sesión para validarlo en el paso 2
        session["flow"] = flow
        return redirect(flow["auth_uri"])

    def get_token(self, app):
        """Paso 2: Procesar la respuesta de Azure y obtener el Token"""
        try:
            flow = session.get("flow")
            if not flow:
                return redirect(url_for("login"))

            # Validar el código recibido contra el flujo original
            result = self.app.acquire_token_by_auth_code_flow(flow, request.args)
            session.pop("flow", None) # Limpiar flujo usado

            if "error" in result:
                return f"Error de Autenticación: {result.get('error_description')}"

            # Extraer información del usuario (claims)
            claims = result.get("id_token_claims")
            if not claims:
                return "Error: No se pudieron obtener los datos del usuario (claims)."
            user_email = claims.get("preferred_username") or claims.get("email")
            
            # Obtener acceso a bases de datos mediante tu servicio original
            databases, role_id = user_service.UserService().get_user_databases(user_email)
            
            if not databases:
                return "Tu usuario no tiene bases de datos asignadas en el sistema."

            # Guardar todo en la sesión de Flask
            session["user"] = claims
            session["token"] = result.get("access_token")
            session["databases"] = databases
            session["role_id"] = role_id
            session["current_db"] = databases[0]["base_de_datos"]
            session["current_client_name"] = databases[0]["nombre_cliente"]

            return redirect("/") # Regresar al Dashboard principal
            
        except Exception as e:
            session.clear()
            return f"Error crítico: {str(e)} <a href='/login'>Reintentar</a>"
        
auth_service = AuthService()