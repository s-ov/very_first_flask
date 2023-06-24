from flask import Blueprint, request, redirect, flash, render_template, url_for, session, g
import sqlite3

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [
    {'url': '.index', 'title': 'Panel'},
    {'url': '.list_users', 'title': 'Users list'},
    {'url': '.list_pubs', 'title': 'Articles list'},
    {'url': '.logout', 'title': 'Logout'},
]

db = None


@admin.before_request
def before_request():
    """Set connection with db before request"""
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request_):
    global db
    db = None
    return request_


# in one app can be only one instance of 'flask_login'
def login_admin():
    session['admin_logged'] = 1


def is_logged():
    return True if session.get('admin_logged') else False


def logout_admin():
    return session.pop('admin_logged', None)


@admin.route('/')
def index():
    if not is_logged():
        return redirect(url_for('.login'))
    return render_template('admin/index.html', menu=menu, title='Admin-panel')


@admin.route('/login', methods=["POST", "GET"])
def login():
    if is_logged():
        return redirect(url_for('.index'))
    if request.method == "POST":
        if request.form['user'] == 'admin' and request.form['psw'] == '12345':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Невірний логін/пароль", "error")
    return render_template('admin/login.html', title="Адмін-панель")


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not is_logged():
        return redirect(url_for('.login'))
    logout_admin()
    return redirect(url_for('.login'))


@admin.route('/list-pubs')
def list_pubs():
    if not is_logged():
        return redirect(url_for('.login'))
    list_ = []
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT title, text, url FROM posts")
            list_ = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Article fetching error from db: {e}")
    return render_template('admin/list_pubs.html', title='Article List', menu=menu, list_=list_)


@admin.route('/list-users')
def list_users():
    if not is_logged():
        return redirect(url_for('.login'))
    list_ = []
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT name, email FROM users ORDER BY time DESC")
            list_ = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Article fetching error from db: {e}")
    return render_template('admin/list_users.html', title='Users List', menu=menu, list_=list_)
