# This file allows you to control how your application behaves depending on where it is running, without having to rewrite your application code.
import os

# Create the Development
class DevelopmentConfig:
    from dotenv import load_dotenv    # Only used locally for development & testing
    load_dotenv()

    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"

# Create the Test Config
class TestingConfig:
    from dotenv import load_dotenv
    load_dotenv()

    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    DEBUG = True

    CACHE_TYPE = 'SimpleCache'
    RATELIMIT_STORAGE_URI = 'memory://'

# Create the Production Config
class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"