import os

SECRET_KEY = os.environ.get('FLASK_KEY')
DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('VERCEL_POSTGRES_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
RETURN_SPACER = "-----------------------"
