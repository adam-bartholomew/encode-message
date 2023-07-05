from flask import Flask, render_template, request, url_for, flash, redirect
from flask_login import LoginManager, login_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import messaging as messaging
import os
import func_timeout

# Create flask application
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_KEY')  # FLASK_KEY stored as system environment variable.
app.debug = True

# Tells flask-sqlalchemy what database to connect to
db_basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_basedir, 'encodeMessage.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize flask-sqlalchemy extension
db = SQLAlchemy()

return_spacer = "-----------------------"
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(80), unique=True)
    #creation_datetime = db.Column(db.Datetime(timezone=False), nullable=False, server_default=func.now())
    #last_modified_datetime = db.Column(db.Datetime(timezone=False))
    #creation_userid = db.Column(db.Integer, nullable=False, server_default='admin')
    #last_modified_userid = db.Column(db.Integer)

    def __repr__(self):
        return f"<User {self.user_id}>"


db.init_app(app)
with app.app_context():
    db.create_all()


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)


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
    template = 'index.html'
    return render_template(template)


@app.route('/home')
def home():
    template = 'home.html'
    return render_template(template)


@app.route('/encode', methods=('GET', 'POST'))
def encode():
    page_name = "encode"
    page_template = f"{page_name}.html"

    if request.method == 'POST' and request.form.get('encodeSubmit') == 'Submit':
        msg = request.form.get('inputMessage')
        offset = int(request.form.get('encodeOffset')) if request.form.get('encodeOffset').isnumeric() else 0
        if msg:
            messaging.log.info(f"Submitting encode form with msg: {msg}, offset: {offset}")
            try:
                encoded_msg = func_timeout.func_timeout(9.99, messaging.encode, args=[msg, offset])
            except func_timeout.FunctionTimedOut:
                messaging.log.info("The call to messaging.encode took more than 10 seconds.")
                flash("Aborted encoding due to timeout. Try shortening the message or reducing the complexity.")
            else:
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
def decode():
    page_name = "decode"
    page_template = f"{page_name}.html"
    if request.method == 'POST':
        if request.form.get('decodeSubmit') == 'Submit':
            msg = request.form.get('inputMessage').replace("\r", "")
            if msg:
                messaging.log.info(f"Submitting decode form with msg:\n{msg}")
                try:
                    decoded_msg = func_timeout.func_timeout(9.99, messaging.decode, args=[msg])
                except func_timeout.FunctionTimedOut:
                    messaging.log.info("The call to messaging.decode took more than 10 seconds.")
                    flash("Aborted decoding due to timeout. Try shortening the message or reducing the complexity.")
                else:
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

    return render_template('decode.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile')
def profile():
    return render_template('user_profile.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(user_id=request.form.get("username"), password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If a post request was made, find the user by filtering for the username
    if request.method == 'POST':
        user = User.query.filter_by(
            user_id=request.form.get("username")).first()
        # Check if the password entered is the same as the user's password
        if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            return redirect(url_for("home"))
        # Redirect the user back to the home
        # (we'll create the home route in a moment)
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
