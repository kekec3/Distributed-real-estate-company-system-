import os
from datetime import timedelta

class Config:
    _user = os.environ.get("MYSQL_USER", "")
    _pass = os.environ.get("MYSQL_PASSWORD", "")
    _host = os.environ.get("MYSQL_HOST", "")
    _port = os.environ.get("MYSQL_PORT", "3306")
    _db = os.environ.get("MYSQL_DATABASE", "")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_user}:{_pass}@{_host}:{_port}/{_db}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours = 1)

    

print("APPPP")
print("MYSQL_URI =", Config.SQLALCHEMY_DATABASE_URI)