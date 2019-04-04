import helpers
from app import app
from models.user import User
from models.image import Image
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, redirect, flash, url_for

images_blueprint = Blueprint('images', __name__, template_folder='templates')

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

def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(
               ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
