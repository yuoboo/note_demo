import os

PROJECT_NAME = 'dm.bp.eams'

PROJECT_ENV_VAR_PREFIX = 'DM_BP_EAMS_'

# Directory of runtime data, like logs and uploaded files etc
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Listen host and port of server
HOST = '0.0.0.0'
PORT = 10010

# Whether in debug mode
DEBUG = False

# Whether to auto load modified code
AUTO_RELOAD = False

# Whether log access record
ACCESS_LOG = False

# Number of working processes
WORKERS = 4

# Max size of request in bytes
REQUEST_MAX_SIZE = 100 * 1024 * 1024

# MySQL connection parameters
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DB = 'ucenter'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'TeNn6iuyhvDE'
MYSQL_TIMEOUT = 5
MYSQL_POOL_MIN_SIZE = 3
MYSQL_POOL_MAX_SIZE = 20

# Redis connection parameters
# REDIS_HOST = '10.1.6.114'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
# REDIS_PASSWORD = '123456'
REDIS_PASSWORD = ''
REDIS_DB_INDEX = 0
REDIS_TIMEOUT = 5
REDIS_POOL_MIN_SIZE = 3
REDIS_POOL_MAX_SIZE = 20
REDIS_URI = 'redis://{}@{}:{}/{}'.format(REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, REDIS_DB_INDEX)

CONFIG_CACHE = {
    "default": {
        "cache": "aiocache.RedisCache",
        "endpoint": REDIS_HOST,
        "port": REDIS_PORT,
        "timeout": REDIS_TIMEOUT,
        "namespace": PROJECT_NAME + '.cache',
        "serializer": {
            "class": "aiocache.serializers.JsonSerializer"
        }
    }
}
