from flask import Flask, render_template, request, url_for, flash, redirect
import messaging as messaging
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_KEY')  # FLASK_KEY stored as system environment variable.
app.debug = True
return_spacer = "-----------------------"


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


@app.route('/encode', methods=('GET', 'POST'))
def encode():
    page_name = "encode"
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
def decode():
    page_name = "decode"
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

    return render_template('decode.html')


@app.route('/about')
def about():
    return render_template('about.html')
