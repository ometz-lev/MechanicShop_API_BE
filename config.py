import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False