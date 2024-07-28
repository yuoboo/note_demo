# -*- coding: utf-8 -*-
from configs import config
from framework_engine import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host=config['SERVE_HOST'],
        port=config['SERVE_PORT'],
        auto_reload=config['AUTO_RELOAD'],
        debug=config['DEBUG'],
        access_log=config['SERVE_ACCESS_LOG'],
        workers=config['SERVE_WORKERS'],
        # protocol=CustomHttpResponseProtocol   # 这个配置影响日志，暂时取消掉
    )
