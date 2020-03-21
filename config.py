import redis
from datetime import timedelta


class Config(object):
    """Flask application config object"""

    ACCEPTED_METHODS = [
        "GET",
        "POST",
        "HEAD",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "PATCH",
        "TRACE"
    ]

    # Mongo DB config
    MONGO_CONTAINER_NAME = "mock_schemas"
    MONGO_IMAGE = "mongo:latest"
    MONGO_HOST = "localhost"
    MONGO_PORT = 27017

    # Redis cache storage config
    REDIS_CONTAINER_NAME = "cache_storage"
    REDIS_IMAGE = "redis:latest"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379

    # Placeholder for matching any possible request body
    ANY = {"__any__": "__any__"}

    # Default mime type for rendering responses
    JSON_MIME_TYPE = "application/json"


class App(object):
    """Flask session config"""

    HOST = "0.0.0.0"
    PORT = 5001

    SECRET_KEY = '123456789012345678901234'
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}"
    CACHE_DEFAULT_TIMEOUT = 3_800
