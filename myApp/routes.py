import secrets
import requests
import webbrowser
from urllib.parse import urlencode
from datetime import datetime
from typing import Union, Any
from flask import render_template, request, url_for, flash, redirect, Blueprint, session, abort, Response
from flask_login import login_user, logout_user, current_user, login_required

from myApp import db, login_manager, User, SavedMessage, encode as encode_message, decode as decode_message, log, utils
from config import OAUTH2_PROVIDERS, RETURN_SPACER, AVAILABLE_PAGES

# Define route constants
routes = Blueprint('routes', __name__)


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def load_user(username: Any) -> Any:
    return User.query.get(username)


@routes.app_errorhandler(401)
def unauthorized(error: Any) -> str:
    log.error(f"{error} - {current_user}")
    flash("You do not have permission to view this page.", 'danger')
    return render_template(AVAILABLE_PAGES['unauthorized']['direct'])


@routes.app_errorhandler(404)
def not_found(error: Any) -> str:
    if current_user.is_authenticated:
        log.error(error)
        flash("The requested page does not exist.", 'danger')
        return render_template(AVAILABLE_PAGES['not_found']['direct'])
    else:
        return unauthorized("Current user is not authenticated.")


# cache definition @app.after_request def add_header(response): Add headers to both force latest IE rendering engine or Chrome Frame, and also to cache the rendered page for 10 minutes.
@routes.after_request
def add_header(response) -> Response:
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@routes.route('/favicon.ico')
def favicon() -> Response:
    return redirect(url_for('static', filename='image/favicon.ico'), code=302)


@routes.route('/')
def index() -> str:
    return render_template(AVAILABLE_PAGES['home']['direct'])


@routes.route('/home')
def home() -> str:
    return render_template(AVAILABLE_PAGES['home']['direct'])


@routes.route('/encode', methods=['GET', 'POST'])
def encode() -> Union[str, Response]:
    if request.method == 'POST':
        input_message = request.form.get('encodeInputMessage')
        encoded_message = request.form.get('encodedMessage')
        offset = int(request.form.get('encodeOffset')) if request.form.get('encodeOffset').isnumeric() else 0
        if request.form.get('encodeSubmit') == 'Submit':
            log.info(f"Submitting encode form with msg: {input_message}, offset: {offset}")
            encoded_msg = encode_message(input_message, offset)
            if encoded_msg[0] != 1:
                flash(encoded_msg[1], 'danger')
            else:
                encoded_message = f"Offset: {offset}\nInput Message: {input_message}\nEncoded Message:\n{RETURN_SPACER}\n{encoded_msg[1]}"
                return render_template(AVAILABLE_PAGES['encode']['direct'], encoded_message=encoded_message)
        elif request.form.get('encodeClear') == 'Clear':
            log.info("Clearing encode form.")
            return redirect(url_for(AVAILABLE_PAGES['encode']['redirect']))
        elif request.form.get('saveButton') == 'Save':
            message = encoded_message.split(RETURN_SPACER)[1].lstrip("\r\n").replace("\r", "")
            log.info(f"Saving encoded message:\n{message}")
            message, category = utils.save_message(current_user, message)
            flash(message, category)
            return render_template(AVAILABLE_PAGES['encode']['direct'], encoded_message=encoded_message)
        else:
            flash("Request was sent and nothing happened", 'warning')
    return render_template(AVAILABLE_PAGES['encode']['direct'], encoded_message="")


@routes.route('/decode', methods=['GET', 'POST'])
def decode() -> Union[str, Response]:
    if request.method == 'POST':
        if request.form.get('decodeSubmit') == 'Submit':
            msg = request.form.get('decodeInputMessage').replace("\r", "")
            if msg:
                log.info(f"Submitting decode form with msg:\n{msg}")
                decoded_msg = decode_message(msg)
                if decoded_msg[0] != 1:
                    flash(decoded_msg[1], 'danger')
                else:
                    decode_resp = f"Encoded Message:\n{RETURN_SPACER}\n{msg}\n{RETURN_SPACER}\nDecoded Message:\n{RETURN_SPACER}\n{decoded_msg[1]}"
                    return render_template(AVAILABLE_PAGES['decode']['direct'], decoded_message=decode_resp)
            else:
                flash("Please enter a message to decode.", 'danger')
        if request.form.get('decodeClear') == 'Clear':
            log.info("Clearing decode form.")
            return redirect(url_for(AVAILABLE_PAGES['decode']['redirect']))
    return render_template(AVAILABLE_PAGES['decode']['direct'], decoded_message="")


@routes.route('/about')
def about() -> str:
    return render_template(AVAILABLE_PAGES['about']['direct'])


@routes.route('/saved_messages/<string:username>')
@login_required
def saved_messages(username: str) -> str:
    user = User.query.filter_by(username=username).first_or_404()
    messages_list = utils.get_user_saved_messages(user)
    log.info(f"User {user.username}'s saved messages: {messages_list}")
    return render_template(AVAILABLE_PAGES['saved_messages']['direct'], user=user, saved_messages=messages_list)


@routes.route('/delete_saved_message/<int:message_id>', methods=['POST'])
@login_required
def delete_saved_message(message_id: int):
    if request.method == 'POST':
        log.info(f"Requesting to delete saved message id {message_id} for {current_user.username}")
        message, category = utils.delete_saved_message(message_id)
        flash(message, category)
    return redirect(url_for(AVAILABLE_PAGES['saved_messages']['redirect'], username=current_user.username))


@routes.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id: int) -> str:
    user = User.query.filter_by(id=user_id).first_or_404()
    log.info(f"Getting info for {user.username}")
    user.set_empty_properties()
    has_changes = False

    if current_user.username != user.username:
        flash("You do not have permission to visit this page.", 'danger')
        return render_template(AVAILABLE_PAGES['unauthorized']['direct'])

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
            log.info(f"Saving {user.username}")
            db.session.commit()
            user = User.query.filter_by(username=user.username).first_or_404()
            user.set_empty_properties()
            flash("Profile Updated", 'success')
            redirect(url_for(AVAILABLE_PAGES['profile']['redirect'], oauth2_providers=OAUTH2_PROVIDERS))
        else:
            log.info(f"Info not changed {user.username}")

    return render_template(AVAILABLE_PAGES['profile']['direct'], user=user, oauth2_providers=OAUTH2_PROVIDERS)


@routes.route('/register', methods=['GET', 'POST'])
def register() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for(AVAILABLE_PAGES['home']['redirect']))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if not user:
            new_user = User(username=request.form.get('username'),
                            password=User.hash_password(request.form.get('password')))
            db.session.add(new_user)
            db.session.commit()
            log.info(f"New user created: {new_user.username}")
            login_user(new_user)
            flash("Successfully logged in", 'success')
            return redirect(url_for(AVAILABLE_PAGES['home']['redirect']))
        else:
            flash(f"Username {user.username} is unavailable. Please choose a new one.", "warning")
    return render_template(AVAILABLE_PAGES['register']['direct'])


@routes.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for(AVAILABLE_PAGES['home']['redirect']))
    # If a post request was made, find the user by filtering for the username
    if request.method == 'POST':
        form_name = request.form.get('username')
        user = User.query.filter_by(username=form_name).first()
        # Check if the password entered is the same as the user's password
        if user is not None:
            try:
                user.check_password(user.password, request.form.get('password'))
                login_user(user)
                log.info(f"Login success {user.username}.")
                return redirect(url_for(AVAILABLE_PAGES['home']['redirect']))
            except ValueError:
                log.error(f"User <{form_name}> tried logging in with the wrong salt.")
        log.info(f"User login failure: <{form_name}>.")
        flash("The username and/or password is incorrect.", 'danger')
        return redirect(url_for(AVAILABLE_PAGES['login']['redirect']))
    return render_template(AVAILABLE_PAGES['login']['direct'])


@routes.route('/authorize/<provider>')
def oauth2_authorize(provider: str) -> Response:
    if not current_user.is_anonymous:
        return redirect(AVAILABLE_PAGES['home']['redirect'])

    provider_data = OAUTH2_PROVIDERS.get(provider)
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
def oauth2_callback(provider: str) -> Response:
    if not current_user.is_anonymous:
        return redirect(AVAILABLE_PAGES['home']['redirect'])

    provider_data = OAUTH2_PROVIDERS.get(provider)
    if provider_data is None:
        abort(404)

    if 'error' in request.args:
        log.error(f"Error via sso login request: {request.args.items}")
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f"Error during login attempt: {k} - {v}", 'danger')
        return redirect(AVAILABLE_PAGES['home']['redirect'])

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

    session['oauth2_token'] = oauth2_token
    session['current_oauth_provider'] = provider
    email = provider_data['userinfo']['email'](response.json())

    # find or create the requested user.
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        name = provider_data['userinfo']['name'](response.json()).split()
        user = User(username=email.split('@')[0],
                    password="",
                    first_name=(name[0] if len(name) > 0 else None),
                    last_name=(name[1] if len(name) > 1 else None),
                    email=email,
                    sso=provider.capitalize())
        db.session.add(user)
        db.session.commit()
        log.info(f"New user created via {provider.capitalize()}: {user.username}")
    else:
        if provider.capitalize() not in user.sso:
            user.sso = user.sso + ',' + provider.capitalize()
            user.last_modified_datetime = datetime.now()
            user.last_modified_userid = user.username
            db.session.commit()
            user = User.query.filter_by(username=user.username).first_or_404()
            user.set_empty_properties()

    # login the user.
    login_user(user)
    log.info(f"User logged in: {user.username}")
    flash(f"Successfully logged in via {provider.capitalize()}", 'success')
    return redirect(url_for(AVAILABLE_PAGES['home']['redirect']))


@routes.route('/revoke/<provider>')
def oauth2_revoke(provider: str) -> Union[str, Response]:
    if current_user.is_anonymous:
        return redirect(url_for(AVAILABLE_PAGES['home']['redirect']))

    provider_data = OAUTH2_PROVIDERS.get(provider)

    if provider_data is None or 'revoke_info' not in provider_data.keys():
        abort(404)

    # Get the current user model
    user = User.query.filter_by(id=current_user.id).first_or_404()

    if user:
        if provider == 'google':
            # Build the HTTP request
            req_params = {}
            for param in provider_data['revoke_info']['params']:
                if "token" in param:
                    req_params[param] = session['oauth2_token']
                if param == "client_id":
                    req_params[param] = provider_data['client_id']
            response = requests.post(provider_data['revoke_info']['revoke_url'],
                                    params=req_params,
                                    headers={'content-type': 'application/x-www-form-urlencoded'})

            # Error response code
            if response.status_code != 200:
                log.error(f"Response status code of {response.status_code} returned from oauth_revoke request for {user.username} and {provider}")
                abort(401)

        # Update user profile
        user.last_modified_datetime = datetime.now()
        user.last_modified_userid = current_user.username
        user.sso = user.sso.replace(provider.capitalize(), '').replace(',,', ',').strip(',')
        user.clear_empty_properties()
        log.info(f"Saving User {user.username}")
        db.session.commit()

        session['oauth2_token'] = None
        session['oauth2_state'] = None
        session['current_oauth_provider'] = None
        log.info(f"Revoked {provider.capitalize()} access from User {user.username}")
        if provider in ["github", "twitch"]:
            flash(f"Please see the opened tab to revoke the {provider.capitalize()} account connection, then logout.", 'info')
            return render_template(AVAILABLE_PAGES['profile']['direct'], user=user, oauth2_providers=OAUTH2_PROVIDERS)
        flash(f"Please review your {provider.capitalize()} account connections page to verify the connection is removed.", 'info')
        return redirect(url_for(AVAILABLE_PAGES['profile']['redirect'], user_id=current_user.id, oauth2_providers=OAUTH2_PROVIDERS))
    else:
        abort(404)


@routes.route('/logout')
def logout() -> Response:
    if current_user.is_authenticated:
        log.info(f"User logged out: {current_user.username}")
        logout_user()
        flash("You have successfully logged out.", 'success')
    return redirect(url_for(AVAILABLE_PAGES['home']['redirect']))
