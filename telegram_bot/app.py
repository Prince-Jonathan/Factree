'''
This script sets up flask and configures its working with sqlalchemy
'''
import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from sqlalchemy.inspection import inspect
# from sqlalchemy import create_engine

#initialising flask object
APP = Flask(__name__)

cors=CORS(APP)
APP.config['CORS_HEADERS'] = ["Content-Type"]

DATABASE_URI = os.environ.get('DATABASE_URL')

# APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg'
APP.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
# consumes lot of memory: set to false
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_ECHO'] = True
app = APP

# Session(APP)
#initialising database with flask object
DB = SQLAlchemy(APP)

engine = DB.create_engine(os.get('DATABASE_URL'), engine_opts={
    'pool_recycle': 120,
    'pool_pre_ping': True
    })

@app.route('/api')
def api():
    return {"name":"Max"}