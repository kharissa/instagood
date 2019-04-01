from app import app
from flask import Blueprint, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from models.user import User
from models.image import Image
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import helpers

images_blueprint = Blueprint('images',
                            __name__,
                            template_folder='templates')

@images_blueprint.route('/new', methods=['GET'])
def new():
        pass

@images_blueprint.route('/', methods=['POST'])
@login_required
def create():
        user = User.get_by_id(current_user.id)
        if current_user == user:
                file = request.files["photo-post"]

                if file and allowed_file(file.filename):
                        file.filename = secure_filename(file.filename)
                        helpers.upload_images_to_s3(file, app.config["S3_BUCKET"], user.id)
                        i = Image(image_path=file.filename,
                                        caption=request.form.get('caption'), user=user)
                        if i.save():
                                flash(f"Image successfully uploaded.")
                                return redirect(url_for('users.show', username=user.username))
                        else:
                                return render_template('users/show.html', errors=user.errors)
        else:
                return render_template('users/show.html', errors={'Access': 'You do not have access to this page.'})


@images_blueprint.route('/<image_id>', methods=["GET"])
def show(image_id):
        image = Image.get_by_id(image_id)
        return render_template('images/show.html', image=image)

@images_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"

@images_blueprint.route('/<user_id>/edit', methods=['GET'])
@login_required
def edit(user_id):
    pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(
               ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@images_blueprint.route('/<user_id>/edit/profile/submit', methods=['POST'])
@login_required
def update(user_id):
    pass
