import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-12345")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    ENABLE_LOGIN = False