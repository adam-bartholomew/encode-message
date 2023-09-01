import os

SECRET_KEY = os.environ.get('FLASK_KEY')
DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('VERCEL_POSTGRES_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
RETURN_SPACER = "-----------------------"
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_CONFIG_URL = "https://accounts.google.com/.well-known/openid-configuration"
TWITTER_CLIENT_SECRET = os.environ.get('TWITTER_CLIENT_SECRET')
TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
OAUTH2_PROVIDERS = {
    'google': {
        'client_secret': GOOGLE_CLIENT_SECRET,
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': "https://localhost:5000/home",
        'prompt': 'consent',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
            'name': lambda json: json['name'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },
    'github': {
        'client_id': os.environ.get('GITHUB_CLIENT_ID'),
        'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'redirect_uri': "https://localhost:5000/home",
        'userinfo': {
            'url': 'https://api.github.com/user',
            'email': lambda json: json['email'],
            'name': lambda json: json['name'],
            'avatar_url': lambda json: json['avatar_url'],
        },
        'scopes': ['user'],
    },
    'twitter': {
        'client_secret': TWITTER_CLIENT_SECRET,
        'client_id': TWITTER_CLIENT_ID,
        'redirect_uri': 'https://localhost:5000/home',
        #'prompt': 'consent',
        'authorize_url': 'https://api.twitter.com/oauth2/authorize',
        'token_url': 'https://api.twitter.com/oauth2/token',
        'userinfo': {

        },
        'scopes': []
    }
}
