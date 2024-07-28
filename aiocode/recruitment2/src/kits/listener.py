# -*- coding: utf-8 -*-
import aiotask_context as context
from drivers.mysql import db


async def setup_serve(app, loop):
    # 服务启动之前处理
    loop.set_task_factory(context.task_factory)

    # 初始化mysql
    await db.init_mysql_db()


async def teardown_serve(app, loop):
    # 服务结束之前处理
    ...
