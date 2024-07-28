import json
import datetime
import sqlalchemy.sql as sasql
from . import BaseService
from utils.useful import random_string, sha256_hash, safe_cast
from models.user import users_table, UserSchema


class UserService(BaseService):

    def __init__(self, app):
        super().__init__(app)
        self.table = users_table
        self.schema = UserSchema()

    async def create(self, **data):
        data['salt'] = random_string(64)
        data['password'] = sha256_hash(data['password'], data['salt'])
        data['created_at'] = datetime.datetime.now()

        async with self.app.db.acquire() as conn:
            result = await conn.execute(sasql.insert(self.table).values(**data))
            user_id = result.lastrowid

        return await self.info(user_id)

    async def info(self, user_id):
        if not user_id:
            return None

        # cache_key = 'user:info:{}'.format(user_id)
        # if await self.cache.exists(cache_key):
        #     user = await self.cache.get(cache_key)
        # else:
        #     result = await self.execute(self.table.select().where(self.table.c.id == user_id))
        #     user = await result.first()
        #     user = self.schema.dump(user)
        #
        #     await self.cache.set(cache_key, user)

        result = await self.execute(self.table.select().where(self.table.c.id == user_id))
        user = await result.first()
        user = self.schema.dump(user)

        return user

    async def infos(self):
        result = await self.execute(self.table.select())
        user_list = await result.fetchall()
        users = self.schema.dump(user_list, many=True)

        return users

    async def list(self, *, from_=None, where=None, order_by=None, page=1, per_page=10):
        page = safe_cast(page, int, 1)
        per_page = safe_cast(per_page, int, 10)

        select_sm = self.table.select()
        count_sm = sasql.select([sasql.func.count()]).select_from(self.table)

        if from_ is not None:
            select_sm = select_sm.select_from(from_)
            count_sm = count_sm.select_from(from_)

        if where is not None:
            select_sm = select_sm.where(where)
            count_sm = count_sm.where(where)

        if order_by is not None:
            select_sm = select_sm.order_by(order_by)

        count_result = await self.execute(count_sm)
        total = await count_result.scalar()

        total_pages = self.calc_total_pages(total, per_page)

        if page > total_pages:
            page = total_pages

        offset = self.calc_offset(page, per_page)
        limit = self.calc_limit(per_page, per_page)

        select_sm = select_sm.offset(offset)
        select_sm = select_sm.limit(limit)

        result = await self.execute(select_sm)
        rows = self.schema.dump(await result.fetchall(), many=True)

        return {
            'rows': rows,
            'page': page,
            'per_page': per_page,
            'total_count': total,
            'total_pages': total_pages,
        }

    async def count(self, where=None):
        sm = sasql.select([sasql.func.count()]).select_from(self.table)
        if where is not None:
            sm = sm.where(where)
        result = await self.execute(sm)

        return await result.scalar()

    async def user_cache(self, user_id):
        cache_key = 'user:info:{}'.format(user_id)
        user = await self.redis.get(cache_key)

        return json.loads(user)

    async def set_user_cache(self, user_id, user_data):
        cache_key = 'user:info:{}'.format(user_id)

        await self.redis.set(cache_key, user_data)
