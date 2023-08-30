from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@db/hospitaldb?auth_plugin=mysql_native_password"
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'we4fh%gC_za:*8G5v=fbv'


app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app=app, session_options={'autoflush': False})
