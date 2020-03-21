import redis
from pymongo import MongoClient
from config import Config


def mongo_connect(func):
    """Mongo DB connection fixture.
       (Implicitly passes client instance to function)"""

    client = MongoClient(
        Config.MONGO_HOST,
        Config.MONGO_PORT
    )

    def decorated(*args, **kwargs):
        try:
            return func(client, *args, **kwargs)
        except Exception as e:
            raise Exception(f"DB request error: {e}") from None
        finally:
            client.close()

    return decorated


def redis_connect(func):
    client = redis.StrictRedis(
        Config.REDIS_HOST,
        Config.REDIS_PORT,
    )

    def decorated(*args, **kwargs):
        try:
            return func(client, *args, **kwargs)
        except Exception as e:
            raise Exception(f"Redis request error: {e}") from None
        finally:
            client.close()

    return decorated


@mongo_connect
def get_schema(_client, name):
    """Gets mock schema by name"""
    schema = _client.local.schemas.find_one({"name": name})
    assert schema, f"Schema not found: \"{name}\""
    body = schema.get("body")
    assert body, f"Schema \"{name}\" has no \"body\""
    return body
