import factory
import storage
from flask import Flask, jsonify
from cache import MockCache
from config import Config, App

app = Flask(__name__)


@app.errorhandler(Exception)
def handle_exception(error):
    """Renders all raised exceptions with HTTP codes"""
    try:
        message, status_code = error.args
    except:
        message = str(error)
        status_code = 500
    response = {
        'error': {
            'code': status_code,
            'message': message
        }
    }

    return jsonify(response), status_code


@app.route("/<string:code>/<path:path>", methods=Config.ACCEPTED_METHODS)
@app.route("/<string:code>/", methods=Config.ACCEPTED_METHODS)
def handle(code, path=""):
    """Handles incoming HTTP requests"""
    mock = factory.get_mock(code)
    mock.cache = cache
    mock.handle()
    return mock.build_response()


if __name__ == '__main__':

    # create app config
    app.config.from_object("config.App")

    # create server cache object
    cache = MockCache(app)

    # init storage client
    storage = storage.Storage()

    # init schemas storage
    storage.run(
        Config.MONGO_CONTAINER_NAME,
        Config.MONGO_IMAGE,
        Config.MONGO_PORT
    )

    # init session cache storage
    storage.run(
        Config.REDIS_CONTAINER_NAME,
        Config.REDIS_IMAGE,
        Config.REDIS_PORT
    )

    # run application
    try:
        app.run(
            App.HOST,
            App.PORT
        )
    finally:
        cache.clear()
        storage.stop_all()
        
