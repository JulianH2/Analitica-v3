import logging
from authlib.integrations.flask_client import OAuth
from flask import url_for, redirect, session
from config import Config
from services.user_service import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, server=None):
        self.oauth = OAuth()
        if server:
            self.init_app(server)
            
    def init_app(self, server):
        self.oauth.init_app(server)
        
        self.oauth.register(
            name='azure',
            client_id=Config.MSAL_CLIENT_ID,
            client_secret=Config.MSAL_CLIENT_SECRET,
            server_metadata_url=f'{Config.MSAL_AUTHORITY}/v2.0/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile User.Read'}
        )

        self.oauth.register(
            name='google',
            client_id=Config.GOOGLE_CLIENT_ID,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

    def login_local(self, email, password):
        """Valida usuario y contraseña contra base de datos local"""
        user_service = UserService()
        user = user_service.validate_local_login(email, password)
        if user:
            return user_service.load_user_session(user)
        return "Correo o contraseña incorrectos."

    def login_social(self, provider_name):
        if provider_name == 'azure':
            redirect_uri = "http://localhost:8000/getAToken"
        else:
            redirect_uri = url_for('auth_callback', provider=provider_name, _external=True)
            if "127.0.0.1" in redirect_uri:
                redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")

        client = self.oauth.create_client(provider_name)
        if not client:
            return f"Proveedor de autenticación '{provider_name}' no configurado."
        return client.authorize_redirect(redirect_uri)

    def handle_social_callback(self, provider_name):
        try:
            client = self.oauth.create_client(provider_name)
            if not client:
                return f"Proveedor de autenticación '{provider_name}' no configurado."
            
            token = client.authorize_access_token()
            
        except Exception as e:
            return f"Error de conexión con {provider_name}: {e}"
        
        email = None
        
        if provider_name == 'azure':
            user_info = token.get('userinfo')

            if user_info:
                email = user_info.get('preferred_username') or user_info.get('email')
        
        elif provider_name == 'google':
            user_info = token.get('userinfo')
            email = user_info.get('email')

        if not email:
            return f"No pudimos identificar tu correo con {provider_name}."

        user_service = UserService()
        user = user_service.get_user_by_email(email)
        
        if user:
            return user_service.load_user_session(user)
        else:
            return f"El correo {email} no tiene permisos en este sistema."

auth_service = AuthService()