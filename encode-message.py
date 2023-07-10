from flask import Flask, render_template, request, url_for, flash, redirect
from flask_login import LoginManager, login_user, UserMixin, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import messaging as messaging
import os

# Create flask application
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_KEY')  # FLASK_KEY stored as system environment variable.
app.debug = True

# Initialize db packages & connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('VERCEL_POSTGRES_URL')
db = SQLAlchemy()
migrate = Migrate(app, db)
return_spacer = "-----------------------"
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)
with app.app_context():
    db.create_all()


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(80), unique=True)
    creation_datetime = db.Column(db.DateTime(timezone=False), nullable=False, server_default=func.now())
    last_modified_datetime = db.Column(db.DateTime(timezone=False), server_default=func.now())
    creation_userid = db.Column(db.String(25), nullable=False, server_default='flask_app')
    last_modified_userid = db.Column(db.String(25), server_default='flask_app')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"


def hash_password(password):
    pw_hash = generate_password_hash(password).decode('utf-8')
    return pw_hash


def check_password(pw_hash, password):
    return check_password_hash(pw_hash, password)


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def load_user(username):
    return UserModel.query.get(username)


# Load Browser Favorite Icon
@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='image/favicon.ico'), code=302)


@app.errorhandler(404)
def page_not_found(error):
    return "This page does not exist", 404, "\n", error


# cache definition @app.after_request def add_header(response): Add headers to both force latest IE rendering engine or Chrome Frame, and also to cache the rendered page for 10 minutes.
@app.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('home.html')
    return redirect(url_for('login'))


@app.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    return redirect(url_for('login'))


@app.route('/encode', methods=('GET', 'POST'))
@login_required
def encode():
    page_name = 'encode'
    page_template = f"{page_name}.html"

    if request.method == 'POST' and request.form.get('encodeSubmit') == 'Submit':
        msg = request.form.get('inputMessage')
        offset = int(request.form.get('encodeOffset')) if request.form.get('encodeOffset').isnumeric() else 0
        if msg:
            messaging.log.info(f"Submitting encode form with msg: {msg}, offset: {offset}")
            encoded_msg = messaging.encode(msg, offset)
            if encoded_msg[0] != 1:
                flash(encoded_msg[1])
            else:
                encode_resp = f"Offset: {offset}\nInput Message: {msg}\nEncoded Message:\n{return_spacer}\n{encoded_msg[1]}"
                return render_template(page_template, encoded_message=encode_resp)
        else:
            flash("Please enter a message to encode.")
    if request.method == 'POST' and request.form.get('encodeClear') == 'Clear':
        messaging.log.info("Clearing encode form.")
        return redirect(url_for(page_name))
    return render_template(page_template)


@app.route('/decode', methods=('GET', 'POST'))
@login_required
def decode():
    page_name = 'decode'
    page_template = f"{page_name}.html"
    if request.method == 'POST':
        if request.form.get('decodeSubmit') == 'Submit':
            msg = request.form.get('inputMessage').replace("\r", "")
            if msg:
                messaging.log.info(f"Submitting decode form with msg:\n{msg}")
                decoded_msg = messaging.decode(msg)
                if decoded_msg[0] != 1:
                    flash(decoded_msg[1])
                else:
                    decode_resp = f"Encoded Message:\n{return_spacer}\n{msg}\n{return_spacer}\nDecoded Message:\n{return_spacer}\n{decoded_msg[1]}"
                    return render_template(page_template, decoded_message=decode_resp)
            else:
                flash("Please enter a message to decode.")
        if request.form.get('decodeClear') == 'Clear':
            messaging.log.info("Clearing decode form.")
            return redirect(url_for(page_name))
    return render_template(page_template)


@app.route('/about')
@login_required
def about():
    return render_template('about.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = UserModel(username=request.form.get('username'), password=hash_password(request.form.get('password')))
        db.session.add(new_user)
        db.session.commit()
        messaging.log.info(f"New user created: {new_user}")
        return redirect(url_for('login'))
    return render_template('sign_up.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If a post request was made, find the user by filtering for the username
    if request.method == 'POST':
        form_name = request.form.get('username')
        user = UserModel.query.filter_by(username=form_name).first()
        # Check if the password entered is the same as the user's password
        if user is not None:
            if check_password(user.password, request.form.get('password')):
                login_user(user)
                messaging.log.info(f"User logged in: {user}.")
                return redirect(url_for('home'))
        messaging.log.info(f"Log in failed for user: <{form_name}>.")
        flash(f"Username and/or password is incorrect for {form_name}.")
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    messaging.log.info(f"User logged out: {current_user}")
    logout_user()
    return render_template('login.html')


if __name__ == "__main__":
    app.run()
