import math
from aiomysql.sa import SAConnection


class ServiceException(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)

        self.message = message
        self.code = code


class BaseService(object):

    def __init__(self, app):
        self.app = app

    @property
    def cache(self):
        return self.app.cache

    @property
    def redis(self):
        return self.app.redis

    @property
    def conn(self):
        return self.app.db.acquire()

    async def execute(self, sm):
        conn: SAConnection
        async with self.conn as conn:
            result = await conn.execute(sm)

        return result

    @staticmethod
    def calc_offset(page=1, per_page=10):
        offset = (page - 1) * per_page
        return offset

    @staticmethod
    def calc_limit(per_page=10, per_page_max=100):
        limit = min(per_page, per_page_max)
        return limit

    @staticmethod
    def calc_total_pages(total=0, per_page=10):
        return math.ceil(total / float(per_page))
