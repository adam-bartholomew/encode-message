from datetime import datetime
from flask import render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from myApp import db, login_manager
from myApp.models.UserModel import UserModel
from myApp.controllers import MessageController
from config import RETURN_SPACER

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
    flash("You do not have permission to view this page.")
    return render_template('401.html')


@routes.app_errorhandler(404)
def not_found(error):
    if current_user.is_authenticated:
        MessageController.log.error(error)
        flash("The requested page does not exist.")
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


@routes.route('/encode', methods=('GET', 'POST'))
def encode():
    if request.method == 'POST' and request.form.get('encodeSubmit') == 'Submit':
        msg = request.form.get('inputMessage')
        offset = int(request.form.get('encodeOffset')) if request.form.get('encodeOffset').isnumeric() else 0
        if msg:
            MessageController.log.info(f"Submitting encode form with msg: {msg}, offset: {offset}")
            encoded_msg = MessageController.encode(msg, offset)
            if encoded_msg[0] != 1:
                flash(encoded_msg[1])
            else:
                encode_resp = f"Offset: {offset}\nInput Message: {msg}\nEncoded Message:\n{RETURN_SPACER}\n{encoded_msg[1]}"
                return render_template('encode.html', encoded_message=encode_resp)
        else:
            flash("Please enter a message to encode.")
    if request.method == 'POST' and request.form.get('encodeClear') == 'Clear':
        MessageController.log.info("Clearing encode form.")
        return redirect(url_for('routes.encode'))
    return render_template('encode.html', encoded_message="")


@routes.route('/decode', methods=('GET', 'POST'))
def decode():
    if request.method == 'POST':
        if request.form.get('decodeSubmit') == 'Submit':
            msg = request.form.get('inputMessage').replace("\r", "")
            if msg:
                MessageController.log.info(f"Submitting decode form with msg:\n{msg}")
                decoded_msg = MessageController.decode(msg)
                if decoded_msg[0] != 1:
                    flash(decoded_msg[1])
                else:
                    decode_resp = f"Encoded Message:\n{RETURN_SPACER}\n{msg}\n{RETURN_SPACER}\nDecoded Message:\n{RETURN_SPACER}\n{decoded_msg[1]}"
                    return render_template('decode.html', decoded_message=decode_resp)
            else:
                flash("Please enter a message to decode.")
        if request.form.get('decodeClear') == 'Clear':
            MessageController.log.info("Clearing decode form.")
            return redirect(url_for('routes.decode'))
    return render_template('decode.html', decoded_message="")


@routes.route('/about')
def about():
    return render_template('about.html')


@routes.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = UserModel.query.filter_by(id=user_id).first_or_404()
    MessageController.log.info(f"Getting Info for {user}")
    user.set_empty_properties()
    has_changes = False

    if current_user.username != user.username:
        flash("You do not have permission to visit this page.")
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
            flash("Profile Updated")
            redirect('routes.profile')
        else:
            MessageController.log.info(f"Info not changed {user}")

    return render_template('user_profile.html', user=user)


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(HOME_ROUTE_REDIRECT))
    if request.method == 'POST':
        new_user = UserModel(username=request.form.get('username'), password=UserModel.hash_password(request.form.get('password')))
        db.session.add(new_user)
        db.session.commit()
        MessageController.log.info(f"New user created: {new_user}")
        return redirect(url_for(LOGIN_ROUTE_REDIRECT))
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
            if user.check_password(user.password, request.form.get('password')):
                login_user(user)
                MessageController.log.info(f"Login success {user}.")
                return redirect(url_for(HOME_ROUTE_REDIRECT))
        MessageController.log.info(f"User login failure: <{form_name}>.")
        flash("The username and/or password is incorrect.")
        return redirect(url_for(LOGIN_ROUTE_REDIRECT))
    return render_template('login.html')


@routes.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for(HOME_ROUTE_REDIRECT))
    MessageController.log.info(f"User logout success: {current_user.username}")
    logout_user()
    return render_template('login.html')
