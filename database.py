from flask_sqlalchemy import SQLAlchemy
from flask import *
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/tmp'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.String(5000), unique=False, nullable=False)


# Здесь будут храниться логины и пароли пользователей.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    admin = db.Column(db.Boolean, unique=False, nullable=False)


# Данная таблица описывает задачу

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    statement = db.Column(db.String(5000), unique=False, nullable=False)
    time_end = db.Column(db.DateTime, unique=False, nullable=False)


db.create_all()