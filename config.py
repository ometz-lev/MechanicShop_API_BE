import os

# Development Config
class DevelopmentConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"


# Testing Config
class TestingConfig:
    SECRET_KEY = 'test-secret-key'
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    DEBUG = True

    CACHE_TYPE = 'SimpleCache'
    RATELIMIT_STORAGE_URI = 'memory://'


# Production Config
class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    if SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1
        )
        
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"


# Load development environment variables
def load_development_environment():
    from dotenv import load_dotenv
    load_dotenv()

    DevelopmentConfig.SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI"
    )
    DevelopmentConfig.SECRET_KEY = os.getenv("SECRET_KEY")
