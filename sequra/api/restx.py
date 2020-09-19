import logging
import traceback

from flask_restx import Api
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

api = Api(version='1.0', title='Disbursement API', description='Using Flask RestPlus with Swagger')


@api.errorhandler
def default_error_handler(exception):
    message = 'An unhandled exception occurred.'
    log.exception(exception)
    return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(error):
    log.warning(traceback.format_exc())
    log.error(error)
    return {'message': 'A database result was required but none was found.'}, 404
