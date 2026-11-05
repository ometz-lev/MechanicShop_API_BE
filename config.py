class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:SptA53-Pq?@localhost/mechanic_shop_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig:
    pass

class ProductionConfig:
    pass