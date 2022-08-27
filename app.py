import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, logout_user, login_user, current_user, LoginManager, UserMixin
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import exceptions

from TaskHandler import create_task, create_board, promote_task, demote_task, delete_task, kanban_stats
from FormHandler import LoginForm, RegisterForm
from BoardHandler import db
from UsersHandler import register_user, login_manager



from flask_sqlalchemy import SQLAlchemy, inspect, declarative_base

############################################### APP CONFIGURATION ######################################################
load_dotenv()


app = Flask(__name__)


app.secret_key = os.environ.get('APP_SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)

#Added this line fixed the issue.
login_manager.login_view = 'users.login'
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL1')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_SITE_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_SECRET_KEY')
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}

# db = SQLAlchemy(app)



class Board(db.Model):
    __abstract__ = True
    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.String(50), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.String(50), nullable=False)
    table_id = db.Column(db.String(150), nullable=False)

# db.init_app(app)
# db.create_all()
# db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
        return render_template("index.html", current_user=current_user)


@app.route("/kanban-board/<username>", methods=['GET', 'POST'])
@login_required
def kanban(username):
    my_board = create_board()
    my_stats = kanban_stats()
    if request.method == 'POST':
        create_task()
        return redirect(url_for('kanban', username=current_user.username))
    return render_template("kanban-board.html", my_board=my_board, my_stats=my_stats, username=current_user.username)


@app.route("/login", methods=['GET', 'POST'])
def login():
    username_error = None
    password_error = None
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_exists = User.query.filter_by(username=request.form.get('username')).first()
        if user_exists and check_password_hash(user_exists.password, request.form.get('password')):
            login_user(user_exists)
            return redirect(url_for('home'))
        elif user_exists is None:
            username_error = 'This user does not exist'
        # elif len(request.form['password']) < 8:
        #     password_error = 'Incorrect password. Please try again'
        else:
            password_error = 'Incorrect password. Please try again'
    return render_template("login.html",
                           login_form=login_form,
                           username_error=username_error,
                           password_error=password_error,
                           current_user=current_user)


@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        register_user()
        return redirect(url_for('home'))
    return render_template("signup.html", register_form=register_form)


@app.route("/promote", methods=["GET", "POST"])
def promote():
    promote_task()
    return redirect(url_for('kanban'))


@app.route("/demote", methods=["GET", "POST"])
def demote():
    demote_task()
    return redirect(url_for('kanban'))


@app.route("/delete", methods=["GET", "POST"])
def delete():
    delete_task()
    return redirect(url_for('kanban'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.errorhandler(401)
def unauthorised(e):
    return render_template('error_page.html', error=401), 401


@app.errorhandler(404)
def unauthorised(e):
    return render_template('error_page.html', error=404), 404


if __name__ == '__main__':
#     db.create_all()
    app.run(debug=True)
#     db.create_all()

