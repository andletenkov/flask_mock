from uuid import uuid4
from flask_caching import Cache


class MockCache(Cache):
    """
    Custom cache implementation for managing redis data
    """

    @property
    def all_data(self):
        """Returns list of all cached items"""
        keys = [k.decode() for k in self.cache._read_clients.keys()]
        return [self.get(k.replace(self.cache.key_prefix, "")) for k in keys]

    def find(self, key, **rules):
        """Finds item in cache by specified conditions"""
        def try_int(v):
            try:
                return int(v)
            except ValueError:
                return v
        r = filter(
            lambda item: item["_key"] == key and
            all([item[k] == v or item[k] == try_int(v) for k, v in rules.items()]),
            self.all_data
        )
        try:
            return next(r)
        except StopIteration:
            return None

    def add_new(self, key, data):
        """Adds new unique item in cache storage"""

        if not self.find(key, **data):
            body = {
                "_key": key,
                **data
        }
            return self.set(str(uuid4()), body)
