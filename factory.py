import json
from json import JSONDecodeError
from handler import RequestHandler


def get_mock(code):
    """Gets concrete mock client instance"""
    try:
        with open(f"schemas/{code}.json", "r") as f:
            schema = json.loads(f.read())
    except FileNotFoundError:
        raise Exception(f"Can't find schema for specified mock: {code}", 500)
    except JSONDecodeError:
        raise Exception("Invalid schema file", 500)

    return RequestHandler(schema)
