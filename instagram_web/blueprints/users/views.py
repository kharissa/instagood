from flask import Blueprint, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from models.user import User

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')

@users_blueprint.route('/', methods=['POST'])
def create():
    hashed_password = generate_password_hash(request.form.get('password'))
    u = User(name=request.form.get('name'), email=request.form.get('email'), username=request.form.get('username'), password=hashed_password)
    if u.save():
        flash(f"Account successfully created.")
        return redirect(url_for('users.new'))
    else:
        return render_template('users/new.html', errors=u.errors)

@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass

@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"

@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass

@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
