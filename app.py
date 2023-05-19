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

# cache defintion @app.after_request def add_header(response):     """     Add headers to both force latest IE rendering engine or Chrome Frame,     and also to cache the rendered page for 10 minutes.     """
@app.after_request
def add_header(response):
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response

@app.route('/', methods=('GET', 'POST'))
def encode():
    template = 'index.html'
    if request.method == 'POST':
        if request.form.get('encodeSubmit') == 'Submit':
            msg = request.form.get('inputMessage')
            if msg:
                encoded_msg = msg + "\n-----------------------" + main.encode(msg)
                return render_template(template, encoded_message=encoded_msg)
        if request.form.get('encodeClear') == 'Clear':
            return render_template(template)

    return render_template(template)


@app.route('/decode', methods=('GET', 'POST'))
def decode():
    template = 'decode.html'
    if request.method == 'POST':
        if request.form.get('decodeSubmit') == 'Submit':
            msg = request.form.get('inputMessage')
            print(f"message:\n{msg}")
            if msg:
                decoded_msg = msg + "\n-----------------------\n" + main.decode(msg)
                return render_template(template, decoded_message=decoded_msg)
        if request.form.get('decodeClear') == 'Clear':
            return render_template(template)

    return render_template('decode.html')


@app.route('/about')
def about():
    return render_template('about.html')
