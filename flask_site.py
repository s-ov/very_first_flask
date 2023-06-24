import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user_login import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin

# configuration
DATABASE = '/tmp/fl_site.db'
DEBUG = True
SECRET_KEY = 'njh!gh7tf%bs.,.gty43ggsv552@jbjh'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)

# download configuration(DATABASE, DEBUG, SECRET_KEY);
# __name__ - means this module
app.config.from_object(__name__)

# redirect database path(app.root_path): database in the same directory
app.config.update(DATABASE=os.path.join(app.root_path, 'fl_site.db'))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'          # to redirect unauthorized users
login_manager.login_message = "Авторизуйтесь для доступу до закритих сторінок."
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load user")
    return UserLogin().from_db(user_id, dbase)


def connect_db():
    # creates connection with db
    conn = sqlite3.connect(app.config['DATABASE'])
    # for dictionary representation
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Auxiliary function to create DB tables"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Connection with DB, if it is not connected"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()                        # g - global variable of app context
    return g.link_db


@app.route('/')
def index():
    return render_template('index.html', menu=dbase.get_menu(), posts=dbase.get_posts_announce())


@app.route("/add_post", methods=["POST", "GET"])
def add_post():
    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["post"]) > 10:
            result = dbase.add_post(request.form['name'],
                                    request.form['post'],
                                    request.form['url'])
            if not result:
                flash("Article adding error", category='error')
            else:
                flash('Article added successfully.')
        else:
            flash("Article adding error", category='error')
    return render_template('add_post.html', menu=dbase.get_menu(), title="Article adding")


@app.route("/post/<alias>")
@login_required
def show_post(alias):
    title, post = dbase.get_post(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.get_menu(), title=title, post=post)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()

    if form.validate_on_submit():      # THE SAME - if request.method == "POST"
        user = dbase.get_user_by_email(form.email.data)

        if user and check_password_hash(user['psw'], form.psw.data):
            user_login = UserLogin().create(user)
            remain_me = form.remember.data
            login_user(user_login, remember=remain_me)
            return redirect(request.args.get('next') or url_for('profile'))
        flash("Incorrect login or password.", "error")

    return render_template('login.html', menu=dbase.get_menu(), title='Authorization', form=form)


# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('profile'))
    #     if request.method == "POST":
#         user = dbase.get_user_by_email(request.form['email'])
#         if user and check_password_hash(user['psw'], request.form['psw']):
#             user_login = UserLogin().create(user)
#             remain_me = True if request.form.get('remain_me') else False
#             login_user(user_login, remember=remain_me)
#             return redirect(request.args.get('next') or url_for('profile'))
#         flash("Incorrect login or password.", "error")
#
#     return render_template('login.html', menu=dbase.get_menu(), title='Authorization')


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_ = generate_password_hash(form.psw.data)
        result = dbase.add_user(form.name.data, form.email.data, hash_)
        if result:
            flash("You registered successfully.", "success")
            return redirect(url_for('login'))
        else:
            flash("Error while adding to db.", "error")
    return render_template('register.html', menu=dbase.get_menu(), title="Registration", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "success")
    return redirect(url_for('login'))


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', menu=dbase.get_menu(), title='Profile')


@app.route("/user_ava")
@login_required
def user_ava():
    img = current_user.get_avatar(app)
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/jpg'
    return h


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file and current_user.verify_extension(file.filename):
            try:
                img = file.read()
                result = dbase.update_user_avatar(img, current_user.get_id())
                if not result:
                    flash("Avatar update error", "error")
                flash("Avatar updated", "success")
            except FileNotFoundError as e:
                flash("File reading error", "error")
        return redirect(url_for('profile'))



dbase = None


@app.before_request
def before_request():
    """Set connection with db before request."""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Close db connection if it was set"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


if __name__ == '__main__':
    app.run(debug=True)
