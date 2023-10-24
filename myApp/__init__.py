from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    """Initialize the modules and packages then create the flask app.
    """

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    from myApp.routes import routes
    app.register_blueprint(routes)
    login_manager.login_view = "routes.login"

    return app


from myApp.models.User import User  # ignore PEP 8: E402
from myApp.models.SavedMessage import SavedMessage  # ignore PEP 8: E402
from myApp.controllers.MessageController import encode, decode, log  # ignore PEP 8: E402
from myApp import routes, utils  # ignore PEP 8: E402
