import os

class Config:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") #isti kao u auth
    MONGO_URI = os.environ.get("MONGO_URI")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME") or ""
    REDIS_HOST = os.environ.get("REDIS_HOST") or ""
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    GANACHE_URL = os.environ.get("GANACHE_URL") or ""
