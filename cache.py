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
        for k in keys:
            k_ = k.replace(self.cache.key_prefix, "")
            yield k_, self.get(k_)

    def find(self, key, **rules):
        """Finds item in cache by specified conditions"""
        def try_int(v):
            try:
                return int(v)
            except ValueError:
                return v
        r = iter(
            item for item in self.all_data if item[1]["_key"] == key and
            all([item[1][k] == v or item[1][k] == try_int(v) for k, v in rules.items()])
        )
        try:
            found = next(r)
            self.delete(found[0])
            return found
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
