## Message Encoding - A way to encode and decode messages by syllable count.
###### Created by [Adam Bartholomew](https://www.linkedin.com/in/adam-bartholomew/) 
###### Uses [Python](https://www.python.org/), [Flask](https://flask.palletsprojects.com/en/2.3.x/), and [Bootstrap](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
###### Application and Database Hosted on Vercel - [here](https://encode-message.vercel.app/).

Please see the initial design document for in-depth design details: __Message_Coding_Initial_Design.odt__

Syllable dataset downloaded from [Kaggle](https://www.kaggle.com/datasets/schwartstack/english-phonetic-and-syllable-count-dictionary?resource=download)

"Hieroglyph" icon by Jajang Nurrahman from <a href="https://thenounproject.com/browse/icons/term/hieroglyph/" target="_blank" title="Hieroglyph Icons">Noun Project</a>

## File Overview:
__wsgi.py__ - This holds the app and is what's called upon starting.

__config.py__ - Holds all Flask and other configuration settings needed in the application.

__myApp\\\_\_init\_\_.py__ - Creates and initializes the application and modules it depends on.

__myApp\controllers\MessageController.py__ - Controls how messages are encoded and decoded.

__myApp\models\UserModel.py__ - Defines the class for a User.

__myApp\routes.py__ - The Flask application route controller.

__myApp\static__ - Follows Flask standards for static web resources.

__myApp\templates__ - Follows Flask standards for web templates.

__myApp\datasets__ - Contains the word datasets.

__myApp\codex.txt__ - Where the syllable count <--> letter translation scheme is kept.

__myApp\credentials.txt__ - Please keep this file locally only, but any api keys need by a controller can be put in this file:

    words api headers:
    "X-RapidAPI-Key": "your-api-key",
    "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"

__requirements.txt__ - Holds the Python packages and their versions used.

__vercel.json__ - Vercel config properties for hosting.

### Encoding:
- Take an english sentence or phrase and turn it into something that does not make sense.

### Decoding:
- Take a message that has been encoded using this same program and decode it into it's original meaning.

## Running:
Make sure that the environment variable(s) are set on your machine or in the projects **activate.bat** file if using virtual environment. You will need 1 for the flask key and 1 or more for a connection to a database.

    ...
    @set FLASK_APP_KEY="secret-flask-key"
    @set DATABASE_CONNECTION_URL="database-connection-url"
    ...

Prior to starting up please execute the following 2 commands:
    
    $ export FLASK_APP=wsgi
    $ export FLASK_ENV=development

To run app in development:

    flask --app wsgi run --debug
