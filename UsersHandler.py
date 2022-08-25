from flask import Flask, request
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, current_user

from uuid import uuid5, NAMESPACE_DNS
import datetime as dt
from BoardHandler import db, User, Board


date = dt.date
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.query.get(user_id)
        return user
    except KeyError:
        return None
        
    return User.query.get(user_id)


def create_user_table(name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Boards.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # user_board = type(name, (Board, db.Model), {'__tablename__': name})
    class UserBoard(Board, db.Model):
        __tablename__ = name

    with app.app_context():
        db.create_all()

    return UserBoard


def current_date():
    today = date.today()
    current_month = today.strftime("%m")
    current_day = today.strftime("%d")
    return f"{current_day}/{current_month}"


def register_user():
    hashed_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

    new_user = User(
        username=request.form.get('username'),
        password=hashed_password,
        date_created=current_date(),
        table_id=str(uuid5(NAMESPACE_DNS, request.form.get('username')))
    )

    create_user_table(new_user.table_id)

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)


def get_user_board():
    db.metadata.reflect(bind=db.engine)
    user_table = db.metadata.tables[current_user.table_id]
    return user_table
