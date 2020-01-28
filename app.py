from flask import Flask, request, jsonify
import factory

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


@app.route("/<string:code>/<path:path>", methods=["GET", "POST"])
@app.route("/<string:code>/", defaults={"path": ""})
def handle(code, path):
    """Handles incoming HTTP requests"""
    mock = factory.get_mock(code)
    mock.handle(request)
    return mock.build_response()


if __name__ == '__main__':
    app.debug = True
    app.run()
