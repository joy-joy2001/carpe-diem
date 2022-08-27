from flask import Flask
from flask_sqlalchemy import SQLAlchemy, inspect, declarative_base

from flask_login import UserMixin

db = SQLAlchemy()
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL1')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Board(db.Model):
    __abstract__ = True
    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.String(50), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.String(50), nullable=False)
    table_id = db.Column(db.String(80), nullable=False)

# with app.app_context():
#     db.create_all()

