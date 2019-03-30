import os
from app import app
from flask import render_template, url_for, request, redirect
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager,login_required
from models.user import User
from helpers import *
from werkzeug.utils import secure_filename


assets = Environment(app)
assets.register(bundles)
csrf = CSRFProtect(app)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(sessions_blueprint, url_prefix="/sessions")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('home.html', errors={'Access': 'You do not have access.'}), 404

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sessions.new"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route("/")
@login_required
def home():
    return render_template('home.html')

# Wrap CSS files with unique ID to prevent browser caching errors
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# app.config.from_object("config")

# @app.route("/", methods=["POST"])
# def upload_file():

#     if "user_file" not in request.files:
#         return "No user_file key in request.files"

#     file = request.files["user_file"]

#     if file.filename == "":
#         return "Please select a file"

#     if file and allowed_file(file.filename):
#         file.filename = secure_filename(file.filename)
#         output = upload_file_to_s3(file, app.config["S3_BUCKET"])
#         return str(output)

#     else:
#         return redirect("/")
