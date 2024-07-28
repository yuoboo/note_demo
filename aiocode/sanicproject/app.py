# coding: utf-8
from sanic import Sanic
from config import config, log_config
from libs.exception import customer_exception_handler
from libs.init import init_db, init_redis, init_cache, close_db, close_redis, close_cache
from utils import client
from blueprints import register_blueprint

app = Sanic(config['PROJECT_NAME'], log_config=log_config)
app.config.update(config)

app.error_handler.add(Exception, customer_exception_handler)
register_blueprint(app)


@app.listener('before_server_start')
async def server_init(app, loop):
    app.db = await init_db(config)
    app.redis = await init_redis(config)
    app.cache = init_cache(config)
    app.client = client.Client(app)


@app.listener('after_server_stop')
async def server_clean(app, loop):
    await close_db(app.db)
    await close_redis(app.redis)
    await close_cache(app.cache)
    app.client.close()


if __name__ == '__main__':
    app.run(
        host=config['HOST'],
        port=config['PORT'],
        debug=config['DEBUG'],
        auto_reload=config['AUTO_RELOAD'],
        access_log=config['ACCESS_LOG'],
        workers=config['WORKERS']
    )
