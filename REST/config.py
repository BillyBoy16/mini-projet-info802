import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    # On récupère la clé dans le .env
    OPENROUTESERVICE_KEY = os.getenv("OPENROUTESERVICE_KEY")