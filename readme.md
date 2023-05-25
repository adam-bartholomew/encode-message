## Message Encoding - A way to encode and decode messages.
###### Created by [Adam Bartholomew](https://www.linkedin.com/in/adam-bartholomew/) using [Python](https://www.python.org/) and [Flask](https://flask.palletsprojects.com/en/2.3.x/)

Please see the initial design document for in-depth design details: __Message_Coding_Initial_Design.odt__

Syllable dataset downloaded from [Kaggle](https://www.kaggle.com/datasets/schwartstack/english-phonetic-and-syllable-count-dictionary?resource=download)

### File Overview:
__main.py__ - Contains the encryption and decryption functionality used by the flask app.

__app.py__ - The Flask application controller.

__\static__ - Follows Flask standards.

__\templates__ - Follows Flask standards.

__\datasets__ - Contains the datasets of words with their syllable counts.

__codex.txt__ - Where the letter - syllable translation scheme is kept. The line number that each letter is on equals the number of syllables that letter corresponds to.

__credentials.txt__ - Please keep this file locally only, but any api keys should be put in this file:

    words api headers:
    "X-RapidAPI-Key": "your-api-key",
    "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"

### Encoding:
- Take an english sentence or phrase and turn it into something that does not make sense.

### Decoding:
- Take a message that has been encrypted using this same program and decrypt it into it's original meaning.

## Running:
Make sure that the FLASK_KEY environment variable is set on your machine or in the projects **activate.bat** file if using virtual environment.

    ...
    @set FLASK_KEY="secret-flask-key"
    ...

Prior to starting up please execute the following 2 commands:
    
    $ export FLASK_APP=app
    $ export FLASK_ENV=development

To run app in development:

    flask --app app run --debug
