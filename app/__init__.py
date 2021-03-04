import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object('settings')

route = '/api'

db = SQLAlchemy(app)
migrate  = Migrate(app=app, db=db)

manager = Manager(app=app)
manager.add_command('db', MigrateCommand)

from app.models import models
from app.controllers import monopoly_api