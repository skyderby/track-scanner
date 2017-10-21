import logging
from flask import request
from time import strftime
from tracksegmenter import app

logger = logging.getLogger('__name__')


@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.after_request
def after_request(response):
    # This IF avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        logger.error(
            '%s %s %s %s %s %s',
            strftime('[%Y-%m-%d %H:%M:%S %z]'),
            request.remote_addr,
            request.method,
            request.scheme,
            request.full_path,
            response.status
        )
    return response
