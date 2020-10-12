from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from flaskaap.instance.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
mail = Mail()


def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    db.init_app(flask_app)
    bcrypt.init_app(flask_app)
    login_manager.init_app(flask_app)
    mail.init_app(flask_app)

    from flaskaap.main.routes import main
    from flaskaap.users.routes import users
    from flaskaap.errors.handlers import errors
    from flaskaap.books.routes import books_app
    from flaskaap.height_collector.routes import height_collector
    flask_app.register_blueprint(main)
    flask_app.register_blueprint(users)
    flask_app.register_blueprint(books_app)
    flask_app.register_blueprint(height_collector)
    flask_app.register_blueprint(errors)

    return flask_app


# app = create_app()
