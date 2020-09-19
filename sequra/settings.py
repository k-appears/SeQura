# Flask settings
FLASK_SERVER_NAME = 'localhost:8888'
FLASK_DEBUG = True  # Do not use debug mode in production
FLASK_ENV = 'development'

# Flask-Restplus settings
RESTPLUS_VALIDATE = True
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_TRACK_MODIFICATIONS = True  # https://docs.sqlalchemy.org/en/13/core/event.html
SQLALCHEMY_ECHO = False

MAX_POOL_WORKERS = 4
