import os
from random import randint
from models.user import User
from instagram_web import oauth
from authlib.flask.client import OAuth
from authlib.client import OAuth2Session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, render_template, request, redirect, flash, url_for, session, escape

sessions_blueprint = Blueprint('sessions', __name__, template_folder='templates')

@sessions_blueprint.route('/login', methods=['GET'])
def new():
    if 'username' in session:
        flash(f"Logged in as {escape(session['name'])}")
    return render_template('sessions/new.html')


@sessions_blueprint.route('/google/authorize')
def authorize():
    oauth.google.authorize_access_token()
    google_user = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()

    if google_user['email'] in User.select(User.email):
        user = User.get(User.email == google_user['email'])
        login_user(user)
        flash(f"Welcome {user.name}. You are now logged in.")
        return redirect(url_for('users.show', username=user.username))
    else:
        random_pw = os.urandom(8)

        if google_user.get('name'): 
            google_name = google_user['name']
        else:
            index = google_user['email'].index('@')
            google_name = google_user['email'][0:index]
            
        random_username = google_name + str(randint(0, 99))

        hashed_password = generate_password_hash(random_pw)
        u = User(name=google_name, email=google_user['email'],
                 username=random_username, password=hashed_password)
        if u.save():
            flash(f"Account successfully created for {u.name}. You are now logged in.")
            login_user(u)
            return redirect(url_for('users.show', username=u.username))
        else:
            return render_template('users/new.html', errors=u.errors)

@sessions_blueprint.route('/google')
def google():
    redirect_url = url_for('sessions.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_url)

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
