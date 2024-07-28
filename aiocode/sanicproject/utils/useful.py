import random
import string
import hashlib
import uuid


def random_string(length=8, letters=None):
    if letters is None:
        letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def sha256_hash(s, salt=''):
    return hashlib.sha256((s + salt).encode()).hexdigest()


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def generate_uuid(with_hex=True):
    uuid_obj = uuid.uuid4()
    return str(uuid_obj.hex) if with_hex else uuid_obj
