import secrets
from urllib.parse import urlencode
import requests
from datetime import datetime
from flask import render_template, request, url_for, flash, redirect, Blueprint, session, abort
from flask_login import login_user, logout_user, current_user, login_required

from myApp import db, login_manager
from myApp.models.UserModel import UserModel
from myApp.controllers import MessageController
import config

routes = Blueprint('routes', __name__)
HOME_ROUTE_REDIRECT = 'routes.home'
LOGIN_ROUTE_REDIRECT = 'routes.login'


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def load_user(username):
    return UserModel.query.get(username)


@routes.app_errorhandler(401)
def unauthorized(error):
    MessageController.log.error(f"{error} - {current_user}")
    flash("You do not have permission to view this page.", 'danger')
    return render_template('401.html')


@routes.app_errorhandler(404)
def not_found(error):
    if current_user.is_authenticated:
        MessageController.log.error(error)
        flash("The requested page does not exist.", 'danger')
        return render_template('404.html')
    else:
        return unauthorized("Current user is not authenticated.")


# cache definition @app.after_request def add_header(response): Add headers to both force latest IE rendering engine or Chrome Frame, and also to cache the rendered page for 10 minutes.
@routes.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@routes.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='image/favicon.ico'), code=302)


@routes.route('/')
def index():
    return render_template('home.html')


@routes.route('/home')
def home():
    return render_template('home.html')


@routes.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST' and request.form.get('encodeSubmit') == 'Submit':
        msg = request.form.get('encodeInputMessage')
        offset = int(request.form.get('encodeOffset')) if request.form.get('encodeOffset').isnumeric() else 0
        if msg:
            MessageController.log.info(f"Submitting encode form with msg: {msg}, offset: {offset}")
            encoded_msg = MessageController.encode(msg, offset)
            if encoded_msg[0] != 1:
                flash(encoded_msg[1], 'danger')
            else:
                encode_resp = f"Offset: {offset}\nInput Message: {msg}\nEncoded Message:\n{config.RETURN_SPACER}\n{encoded_msg[1]}"
                return render_template('encode.html', encoded_message=encode_resp)
        else:
            flash("Please enter a message to encode.", 'danger')
    if request.method == 'POST' and request.form.get('encodeClear') == 'Clear':
        MessageController.log.info("Clearing encode form.")
        return redirect(url_for('routes.encode'))
    return render_template('encode.html', encoded_message="")


@routes.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        if request.form.get('decodeSubmit') == 'Submit':
            msg = request.form.get('decodeInputMessage').replace("\r", "")
            if msg:
                MessageController.log.info(f"Submitting decode form with msg:\n{msg}")
                decoded_msg = MessageController.decode(msg)
                if decoded_msg[0] != 1:
                    flash(decoded_msg[1], 'danger')
                else:
                    decode_resp = f"Encoded Message:\n{config.RETURN_SPACER}\n{msg}\n{config.RETURN_SPACER}\nDecoded Message:\n{config.RETURN_SPACER}\n{decoded_msg[1]}"
                    return render_template('decode.html', decoded_message=decode_resp)
            else:
                flash("Please enter a message to decode.", 'danger')
        if request.form.get('decodeClear') == 'Clear':
            MessageController.log.info("Clearing decode form.")
            return redirect(url_for('routes.decode'))
    return render_template('decode.html', decoded_message="")


@routes.route('/about')
def about():
    return render_template('about.html')


'''
@routes.route('/saves/<int:user_id>')
@login_required
def saves(user_id):
    user = UserModel.query.filter_by(id=user_id).first_or_404()

    return render_template('user_saves.html', user=user)
'''


@routes.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = UserModel.query.filter_by(id=user_id).first_or_404()
    MessageController.log.info(f"Getting Info for {user}")
    user.set_empty_properties()
    has_changes = False

    if current_user.username != user.username:
        flash("You do not have permission to visit this page.", 'danger')
        return render_template('401.html')

    if request.method == 'POST':
        form_username = request.form.get('profile_username')
        form_first_name = request.form.get('profile_firstname')
        form_last_name = request.form.get('profile_lastname')
        form_email = request.form.get('profile_email')
        form_password = request.form.get('profile_password')
        if user.validate_new_username(user.username, form_username):
            has_changes = True
            user.username = form_username
        if user.validate_new_password(user.password, form_password):
            has_changes = True
            user.password = user.hash_password(form_password)
        if user.first_name != form_first_name:
            has_changes = True
            user.first_name = form_first_name
        if user.last_name != form_last_name:
            has_changes = True
            user.last_name = form_last_name
        if user.email != form_email:
            has_changes = True
            user.email = form_email

        if has_changes:
            user.last_modified_datetime = datetime.now()
            user.last_modified_userid = form_username
            user.clear_empty_properties()
            MessageController.log.info(f"Saving {user}")
            db.session.commit()
            user = UserModel.query.filter_by(username=user.username).first_or_404()
            user.set_empty_properties()
            flash("Profile Updated", 'success')
            redirect('routes.profile')
        else:
            MessageController.log.info(f"Info not changed {user}")

    return render_template('user_profile.html', user=user)


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(HOME_ROUTE_REDIRECT))
    if request.method == 'POST':
        user = UserModel.query.filter_by(username=request.form.get('username')).first()
        if not user:
            new_user = UserModel(username=request.form.get('username'),
                                 password=UserModel.hash_password(request.form.get('password')))
            db.session.add(new_user)
            db.session.commit()
            MessageController.log.info(f"New user created: {new_user}")
            login_user(new_user)
            flash("Successfully logged in", 'success')
            return redirect(url_for(HOME_ROUTE_REDIRECT))
        else:
            flash(f"Username {user.username} is unavailable. Please choose a new one.", "warning")
    return render_template('sign_up.html')


@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(HOME_ROUTE_REDIRECT))
    # If a post request was made, find the user by filtering for the username
    if request.method == 'POST':
        form_name = request.form.get('username')
        user = UserModel.query.filter_by(username=form_name).first()
        # Check if the password entered is the same as the user's password
        if user is not None:
            try:
                user.check_password(user.password, request.form.get('password'))
                login_user(user)
                MessageController.log.info(f"Login success {user}.")
                return redirect(url_for(HOME_ROUTE_REDIRECT))
            except ValueError:
                MessageController.log.error(f"User <{form_name}> tried logging in with the wrong salt.")
        MessageController.log.info(f"User login failure: <{form_name}>.")
        flash("The username and/or password is incorrect.", 'danger')
        return redirect(url_for(LOGIN_ROUTE_REDIRECT))
    return render_template('login.html')


@routes.route('/authorize/<provider>')
def oauth2_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(HOME_ROUTE_REDIRECT)

    provider_data = config.OAUTH2_PROVIDERS.get(provider)
    if provider_data is None:
        abort(404)

    # generate a random string for the query's state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # create a query string of the parameters for the OAuth2 provider URL.
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('routes.oauth2_callback', provider=provider, _external=True),
        'response_type': provider_data['response_type'],
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state']
    })

    # redirect the user to the OAuth2 provider authorization URL.
    return redirect(provider_data['authorize_url'] + '?' + qs)


@routes.route('/callback/<provider>')
def oauth2_callback(provider):
    if not current_user.is_anonymous:
        return redirect(HOME_ROUTE_REDIRECT)

    provider_data = config.OAUTH2_PROVIDERS.get(provider)
    if provider_data is None:
        abort(404)

    if 'error' in request.args:
        MessageController.log.error(f"Error via sso login request: {request.args.items}")
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f"Error during login attempt: {k} - {v}", 'danger')
        return redirect(HOME_ROUTE_REDIRECT)

    # Ensure the state that was returned by the URL is the same one we sent.
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    if 'code' not in request.args:
        abort(401)

    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('routes.oauth2_callback', provider=provider, _external=True),
    }, headers={'Accept': 'application/json'})

    if response.status_code != 200:
        abort(401)

    # get the OAuth2 token.
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # use the OAuth2 token to get the user info
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Client-Id': provider_data['client_id'],
        'Accept': 'application/json',
    })

    if response.status_code != 200:
        abort(401)

    if not provider_data['userinfo']['email']:
        abort(401)

    email = provider_data['userinfo']['email'](response.json())

    # find or create the requested user.
    user = db.session.scalar(db.select(UserModel).where(UserModel.email == email))
    if user is None:
        name = provider_data['userinfo']['name'](response.json()).split()
        user = UserModel(username=email.split('@')[0],
                         password="",
                         first_name=(name[0] if len(name) > 0 else None),
                         last_name=(name[1] if len(name) > 1 else None),
                         email=email,
                         sso=provider.capitalize())
        db.session.add(user)
        db.session.commit()
        MessageController.log.info(f"New user created via {provider.capitalize()}: {user}")
    else:
        if provider.capitalize() not in user.sso:
            user.sso = user.sso + ',' + provider.capitalize()
            user.last_modified_datetime = datetime.now()
            user.last_modified_userid = user.username
            db.session.commit()
            user = UserModel.query.filter_by(username=user.username).first_or_404()
            user.set_empty_properties()

    # login the user.
    login_user(user)
    MessageController.log.info(f"User logged in: {user}")
    flash(f"Successfully logged in via {provider.capitalize()}", 'success')
    return redirect(url_for(HOME_ROUTE_REDIRECT))


@routes.route('/logout')
def logout():
    if current_user.is_authenticated:
        MessageController.log.info(f"User logged out: {current_user.username}")
        logout_user()
        flash("You have successfully logged out.", 'success')
    return redirect(url_for(HOME_ROUTE_REDIRECT))
