'''
This script sets up flask and configures its working with sqlalchemy
'''
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy.inspection import inspect
# from sqlalchemy import create_engine

#initialising flask object
APP = Flask(__name__)

cors=CORS(APP)
APP.config['CORS_HEADERS'] = ["Content-Type"]

# APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://rxxavqzelrynsk:8aec395e670af85437c5c603f01b4c8f608ed7eb2c86e568d2864e53cb1dc3a8@ec2-44-196-223-128.compute-1.amazonaws.com:5432/d96dk3m2laba85'
# consumes lot of memory: set to false
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_ECHO'] = True


#set app secret key
# APP.secret_key = b'\x12\xfc+\xf9\x81\x9d\tU_%\x81\xc2\xb2z\r]'

# Session(APP)
#initialising database with flask object
DB = SQLAlchemy(APP)

engine = DB.create_engine('postgres://rxxavqzelrynsk:8aec395e670af85437c5c603f01b4c8f608ed7eb2c86e568d2864e53cb1dc3a8@ec2-44-196-223-128.compute-1.amazonaws.com:5432/d96dk3m2laba85', engine_opts={
    'pool_recycle': 120,
    'pool_pre_ping': True
    })

#initialising migration extension with flask object
migrate = Migrate(APP, DB)

#initialising onesignal client for notifications
# ONESIGNAL_CLIENT = AsyncClient(app_id="88669c69-3692-49b8-9458-93694b80eeef", rest_api_key="MTBiY2U2YmYtMGJiOS00NTM3LTgzZGMtMDAzMDhjNTQ2NDAx")

class Serializer(object):

    def serialize(self, ignore=[]):
        d = list(instance_state(self).unloaded)
        return {c: None if (c in d or c in ignore) else (getattr(self, c).serialize() if issubclass(type(getattr(self, c)), DB.Model) else getattr(self, c)) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() if m is not None else {} for m in l]