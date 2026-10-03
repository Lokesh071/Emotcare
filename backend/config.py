import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this')
    SQLALCHEMY_DATABASE_URI = 'url'
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.environ.get('REDIS_URL')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'mail'
    MAIL_PASSWORD = 'passcode'
