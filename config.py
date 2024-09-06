import os

class Config:
    SECRET_KEY = os.getenv('JTOKEN_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('WEEKLY_DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JTOKEN_KEY')
    

