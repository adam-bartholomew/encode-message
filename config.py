import os

SECRET_KEY = os.environ.get('FLASK_KEY')
DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('VERCEL_POSTGRES_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
RETURN_SPACER = "-----------------------"
GOOGLE_CONFIG_URL = "https://accounts.google.com/.well-known/openid-configuration"
OAUTH2_PROVIDERS = {
    'google': {
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'redirect_uri': "https://localhost:5000/home",
        'prompt': 'consent',
        'response_type': 'code',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
            'name': lambda json: json['name'],
            'profile_pic': lambda json: json['picture'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },
    'github': {
        'client_id': os.environ.get('GITHUB_CLIENT_ID'),
        'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
        'response_type': 'code',
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'redirect_uri': "https://localhost:5000/home",
        'userinfo': {
            'url': 'https://api.github.com/user',
            'email': lambda json: json['email'],
            'name': lambda json: json['name'],
            'profile_pic': lambda json: json['avatar_url'],
        },
        'scopes': ['user'],
    },
    'twitch': {
        'client_secret': os.environ.get('TWITCH_CLIENT_SECRET'),
        'client_id': os.environ.get('TWITCH_CLIENT_ID'),
        'redirect_uri': 'https://localhost:5000/home',
        'authorize_url': 'https://id.twitch.tv/oauth2/authorize',
        'token_url': 'https://id.twitch.tv/oauth2/token',
        'response_type': 'code',
        'userinfo': {
            'url': 'https://api.twitch.tv/helix/users',
            'email': lambda json: json['data'][0]['email'],
            'name': lambda json: json['data'][0]['display_name'],
            'profile_pic': lambda json: json['data'][0]['profile_image_url'],
        },
        'scopes': ['openid', 'user:read:email']
    }
}
