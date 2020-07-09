import json
import os

import db
from json import JSONDecodeError
from handler import RequestHandler, SkrillRequestHandler

HANDLERS = {
    # "example": ExampleRequestHandler
    # implement your own handler if needed!
}


def get_mock(code):
    """Gets concrete mock client instance"""
    try:
        with open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas", f"{code}.json"), "r"
        ) as f:
            schema = json.loads(f.read())
    except FileNotFoundError:
        schema = db.get_schema(code)
    except JSONDecodeError:
        raise Exception("Invalid schema file", 500)

    handler = HANDLERS.get(code, RequestHandler)
    return handler(schema)
