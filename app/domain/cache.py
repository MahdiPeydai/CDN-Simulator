class Cache:
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def has(self, key):
        return key in self._data

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        self._data.pop(key, None)