from flask import abort, Blueprint, render_template, request, redirect, flash, url_for, session, escape
from werkzeug.security import check_password_hash
from models.user import User
from flask_login import login_user, logout_user, login_required
from urllib.parse import urlparse, urljoin

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

@sessions_blueprint.route('/login', methods=['GET'])
def new():
    if 'username' in session:
        flash(f"Logged in as {escape(session['name'])}")
    return render_template('sessions/new.html')

@sessions_blueprint.route('/', methods=['POST'])
def create():
    user = User.get(User.email == request.form.get('email'))
    if user:
        password_to_check = request.form['password']
        hashed_password = user.password
        result = check_password_hash(hashed_password, password_to_check)
        if result:
            login_user(user)
            flash(f"Welcome {user.name}. You are now logged in.")
            return redirect(url_for('users.show', username=user.username))
        else:
            return render_template('sessions/new.html', errors={'Password': 'Email and password do not match.'})

    return render_template('sessions/new.html', errors={'Email': 'We were not able to find a user with that email.'})

@sessions_blueprint.route('/', methods=["GET"])
def index():
    if 'username' in session:
        flash(f"Logged in as {escape(session['name'])}")
    return redirect(url_for('home'))


@sessions_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f"You are now logged off.")
    return redirect(url_for('sessions.new'))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

