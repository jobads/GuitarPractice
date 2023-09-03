from flask_login import UserMixin
from . import db


class tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    target_bpm = db.Column(db.Integer)
    complete = db.Column(db.Boolean)

class sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    bpm = db.Column(db.Integer)
    duration = db.Column(db.Time)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

db.create_all()