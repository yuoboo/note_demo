
def safe_int(val, default=None):
    if not val:
        return default

    try:
        val = int(val)
    except (ValueError, TypeError):
        return default
    else:
        return val


class ToModel(dict):
    def __getattr__(self, key):
        return self.get(key, None)
