import random
import time
from urllib.parse import quote_plus
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__file__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{quote_plus("Bing@107217")}@127.0.0.1:3306/test1'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'DemoUser'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))


@app.route('/index')
def index():
    print("this is server index")
    return "hello world"



