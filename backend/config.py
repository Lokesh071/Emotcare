import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this')
    SQLALCHEMY_DATABASE_URI = 'postgresql://neondb_owner:npg_xjCwiJ2t9pLq@ep-orange-cake-a1jy3myz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.environ.get('REDIS_URL')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'faceauth1@gmail.com'
    MAIL_PASSWORD = 'kvik axuf aeqy yhex'
