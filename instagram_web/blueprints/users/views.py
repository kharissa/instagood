from app import app
from flask import Blueprint, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from models.user import User
from models.image import Image
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import helpers

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

@users_blueprint.route('/profile/<username>', methods=["GET"])
def show(username):
        user = User.get(User.username == username)
        photos = Image.select().where(Image.user_id==user.id)
        return render_template('users/show.html', user=user, photos=photos)

@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"

@users_blueprint.route('/<user_id>/edit', methods=['GET'])
@login_required
def edit(user_id):
        user = User.get_by_id(user_id)
        if current_user == user:
                return render_template('users/edit.html', user=user)
        else:
                return render_template('users/show.html', errors={'Access': 'You do not have access to this page.'})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(
               ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@users_blueprint.route('/<user_id>/edit/profile/submit', methods=['POST'])
@login_required
def update(user_id):
        user = User.get_by_id(user_id)

        if current_user == user:
                if request.form.get('email'):
                        user.email = request.form.get('email')
                if request.form.get('name'):
                        user.name = request.form.get('name')
                if request.form.get('username'):
                        user.username = request.form.get('username')
                if request.form.get('password'):
                        user.password = generate_password_hash(
                            request.form.get('password'))
                if 'file' in request.files:
                        file = request.files["user-photo"]

                        if file and allowed_file(file.filename):
                                file.filename = secure_filename(file.filename)
                                user.profile_image_path = file.filename
                                helpers.upload_images_to_s3(
                                file, app.config["S3_BUCKET"], user.id)
                if request.form.get('public-profile') and user.is_public == False:
                                user.is_public = True
                if not request.form.get('public-profile') and user.is_public == True:
                        user.is_public = False
                if user.save():
                        flash(f"Account successfully updated.")
                        return redirect(url_for('users.show', username=user.username))
                else:
                        return render_template('users/edit.html', errors=user.errors)
        else:
                return render_template('users/show.html', errors={'Access': 'You do not have access to this page.'})


