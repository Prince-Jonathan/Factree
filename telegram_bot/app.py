'''
This script sets up flask and configures its working with sqlalchemy
'''
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from sqlalchemy.inspection import inspect
# from sqlalchemy import create_engine

#initialising flask object
APP = Flask(__name__)

cors=CORS(APP)
APP.config['CORS_HEADERS'] = ["Content-Type"]

DATABASE_URI = 'postgres://rxxavqzelrynsk:8aec395e670af85437c5c603f01b4c8f608ed7eb2c86e568d2864e53cb1dc3a8@ec2-44-196-223-128.compute-1.amazonaws.com:5432/d96dk3m2laba85'

# APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg'
APP.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
# consumes lot of memory: set to false
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_ECHO'] = True

# Session(APP)
#initialising database with flask object
DB = SQLAlchemy(APP)

engine = DB.create_engine('postgres://rxxavqzelrynsk:8aec395e670af85437c5c603f01b4c8f608ed7eb2c86e568d2864e53cb1dc3a8@ec2-44-196-223-128.compute-1.amazonaws.com:5432/d96dk3m2laba85', engine_opts={
    'pool_recycle': 120,
    'pool_pre_ping': True
    })

@app.route('/')
def index:
    return {"success":True}