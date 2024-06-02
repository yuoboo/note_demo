from flask import Flask
from flask_redis import FlaskRedis

REDIS_URL = "redis://:@localhost:6379/0"
app = Flask(__name__)
app.config.from_object(__name__)

redis = FlaskRedis(app, True)


@app.route('/index')
def index():
    redis.incr("hit", 1)
    hit = redis.get("hit")
    print(f"hit:{hit}")
    return hit


if __name__ == '__main__':
    app.run()

    # gunicorn -w 4 -b 0.0.0.0:8000 server-redis:app --worker-class gevent
