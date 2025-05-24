import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.environ.get('REDIS_URL')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
