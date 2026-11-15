#this file is used to initialize the extensions used in the application
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

ma = Marshmallow()             #creating an instance of Marshmallow for serialization and deserialization of data
db = SQLAlchemy()

# creating an instance of Limiter with default limits of 200 requests per day and 50 requests per hour, using the client's IP address as the key for rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day","50 per hour"])

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})                 #creating an instance of Cache