import os

SECRET_KEY = os.environ.get('FLASK_KEY')
DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('VERCEL_POSTGRES_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
RETURN_SPACER = "-----------------------"
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_CONFIG_URL = "https://accounts.google.com/.well-known/openid-configuration"
OAUTH2_PROVIDERS = {
    'google': {
        'client_secret': GOOGLE_CLIENT_SECRET,
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': "https://localhost:5000/home",
        'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'prompt': 'consent',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    }
}
