import os

# Development Config
class DevelopmentConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"


# Production Config
class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"


def load_development_environment():
    from dotenv import load_dotenv
    load_dotenv()

    DevelopmentConfig.SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI"
    )
    DevelopmentConfig.SECRET_KEY = os.getenv("SECRET_KEY")
