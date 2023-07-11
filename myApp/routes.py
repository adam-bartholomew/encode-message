from flask import render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from myApp import bcrypt, db, login_manager
from myApp.models.UserModel import UserModel
from myApp.controllers import MessageController
from config import RETURN_SPACER

routes = Blueprint('routes', __name__)


def hash_password(password):
    pw_hash = bcrypt.generate_password_hash(password=password).decode('utf-8')
    return pw_hash


def check_password(pw_hash, password):
    return bcrypt.check_password_hash(pw_hash=pw_hash, password=password)


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def load_user(username):
    return UserModel.query.get(username)


@routes.errorhandler(404)
def page_not_found(error):
    return "This page does not exist", 404, "\n", error


# cache definition @app.after_request def add_header(response): Add headers to both force latest IE rendering engine or Chrome Frame, and also to cache the rendered page for 10 minutes.
@routes.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


# Load Browser Favorite Icon
@routes.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='image/favicon.ico'), code=302)


@routes.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('home.html')
    return redirect(url_for('routes.login'))


@routes.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    return redirect(url_for('routes.login'))


@routes.route('/encode', methods=('GET', 'POST'))
@login_required
def encode():
    page_name = 'encode'
    page_template = f"{page_name}.html"

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
                return render_template(page_template, encoded_message=encode_resp)
        else:
            flash("Please enter a message to encode.")
    if request.method == 'POST' and request.form.get('encodeClear') == 'Clear':
        MessageController.log.info("Clearing encode form.")
        return redirect(url_for('routes.encode'))
    return render_template('encode.html')


@routes.route('/decode', methods=('GET', 'POST'))
@login_required
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
    return render_template('decode.html')


@routes.route('/about')
@login_required
def about():
    return render_template('about.html')


@routes.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html')


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = UserModel(username=request.form.get('username'), password=hash_password(request.form.get('password')))
        db.session.add(new_user)
        db.session.commit()
        MessageController.log.info(f"New user created: {new_user}")
        return redirect(url_for('routes.login'))
    return render_template('sign_up.html')


@routes.route('/login', methods=['GET', 'POST'])
def login():
    # If a post request was made, find the user by filtering for the username
    if request.method == 'POST':
        form_name = request.form.get('username')
        user = UserModel.query.filter_by(username=form_name).first()
        # Check if the password entered is the same as the user's password
        if user is not None:
            if check_password(user.password, request.form.get('password')):
                login_user(user)
                MessageController.log.info(f"User login success: {user}.")
                return redirect(url_for('routes.home'))
        MessageController.log.info(f"User login failure: <{form_name}>.")
        flash(f"Username and/or password is incorrect for {form_name}.")
        return redirect(url_for('routes.login'))
    return render_template('login.html')


@routes.route('/logout')
def logout():
    MessageController.log.info(f"User logout success: {current_user}")
    logout_user()
    return render_template('login.html')
