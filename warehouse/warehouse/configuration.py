from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"];

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/warehouse"
    REDIS_URI = "redis"
    REDIS_PRODUCTS_LIST = "products"
    JWT_SECRET_KEY = "IEP_PROJEKAT"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours = 1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days = 30)
