import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('HEIGHT_COLLECTOR_DATABASE_URI')
    # ENV is by default production so we are not setting it here
    # DEBUG = False debug is by default false
    # SQLALCHEMY_ECHO: When set to 'True', Flask-SQLAlchemy will log all database
    # activity to Python's stderr for debugging purposes.
    SQLALCHEMY_ECHO = False
    #  To suppress the warning "this option takes a lot of system resources" set
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_FOLDER = 'static/images'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')

    # Flask-User settings
    USER_APP_NAME = "Flask Basic App"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

    # Configure email setting
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')


