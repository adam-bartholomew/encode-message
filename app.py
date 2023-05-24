from flask import Flask, render_template, request, url_for, flash, redirect, current_app
from werkzeug.exceptions import abort
import main as main

with open('credentials.txt', 'r') as f:
    for line in f:
        if line.startswith('"flask_key":'):
            flask_app_key = (line.split(":")[1].split('"')[1])

app = Flask(__name__)
app.config['SECRET_KEY'] = flask_app_key
app.debug = True


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


@app.route('/encode', methods=('GET', 'POST'))
def encode():
    page_name = "encode"
    page_template = f"{page_name}.html"

    if request.method == 'POST':
        if request.form.get('encodeSubmit') == 'Submit':
            msg = request.form.get('inputMessage')
            if msg:
                main.log.info(f"submitting encode form with message: {msg}")
                encoded_msg = msg + "\n-----------------------" + main.encode(msg)
                return render_template(page_template, encoded_message=encoded_msg)
            else:
                flash("Please enter a message to encode.")
        if request.form.get('encodeClear') == 'Clear':
            main.log.info("Clearing encode form.")
            return redirect(url_for(page_name))
    return render_template(page_template)


@app.route('/decode', methods=('GET', 'POST'))
def decode():
    page_name = "decode"
    page_template = f"{page_name}.html"
    if request.method == 'POST':
        if request.form.get('decodeSubmit') == 'Submit':
            msg = request.form.get('inputMessage')
            if msg:
                main.log.info(f"Submitting decode form with msg: {msg}")
                decoded_msg = msg + "\n-----------------------\n" + main.decode(msg)
                return render_template(page_template, decoded_message=decoded_msg)
            else:
                flash("Please enter a message to decode.")
        if request.form.get('decodeClear') == 'Clear':
            main.log.info("Clearing decode form.")
            return redirect(url_for(page_name))

    return render_template('decode.html')


@app.route('/about')
def about():
    return render_template('about.html')