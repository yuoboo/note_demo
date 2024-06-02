import random
import time

from flask import Flask

app = Flask(__file__)


@app.route('/index')
def index():
    print("this is server index")
    return "hello world"



