from flask import Flask, jsonify
from .extensions import db, ma, limiter, cache
from . import models
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config = {
        'app_name' : "Mechanic Shop API"
    }
)

def create_app(config_name):
    app = Flask(__name__)

    if config_name == 'DevelopmentConfig':
        from config import load_development_environment
        load_development_environment()

    # Load configuration from the specified config object
    app.config.from_object(f'config.{config_name}')

    # Verify that DB URL and secret key are available before initializing extensions
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is not configured.")

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError("SECRET_KEY is not configured.")

    # initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)  

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Handle rate limit exceeded errors
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

    return app