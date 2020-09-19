"""
    Why flask?
    ==========

    Because for an MVP, Flask provides finer granular modularization than Django
"""

import logging.config
from pathlib import Path

from flask import Flask, Blueprint

from sequra import settings
from sequra.api.resource.disbursement import ns as place_namespace
from sequra.api.restx import api
from sequra.database import db, init_db_seed

app = Flask(__name__)
logging.config.fileConfig(Path(__file__).parent / './resources' / 'logging.conf')
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['FLASK_ENV'] = settings.FLASK_ENV
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SQLALCHEMY_ECHO'] = settings.SQLALCHEMY_ECHO


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/')
    api.init_app(blueprint)
    api.add_namespace(place_namespace)
    flask_app.register_blueprint(blueprint)


def initialize_db():
    db.init_app(app)
    with app.app_context():
        db.create_all()
        init_db_seed()


def main():
    initialize_app(app)
    initialize_db()
    app.run(debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()
