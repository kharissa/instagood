import os
import rq
import config
import helpers
from app import app
from redis import Redis
from models.user import User
from models.image import Image
from .util.assets import bundles
from instagram_web.helpers.google_oauth import oauth
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from flask_assets import Environment, Bundle
from flask_login import LoginManager, login_required, current_user
from flask import render_template, url_for, request, redirect
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.images.views import images_blueprint
from instagram_web.blueprints.relationships.views import relationships_blueprint
from instagram_web.blueprints.transactions.views import transactions_blueprint
from instagram_api.blueprints.users.views import users_api_blueprint
from instagram_api.blueprints.sessions.views import sessions_api_blueprint
from instagram_api.blueprints.images.views import images_api_blueprint

assets = Environment(app)
assets.register(bundles)
csrf = CSRFProtect(app)
oauth.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sessions.new"
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue(connection=app.redis)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(sessions_blueprint, url_prefix="/sessions")
app.register_blueprint(images_blueprint, url_prefix="/images")
app.register_blueprint(transactions_blueprint, url_prefix="/transactions")
app.register_blueprint(relationships_blueprint, url_prefix="/requests")
csrf.exempt(users_api_blueprint)
csrf.exempt(sessions_api_blueprint)
csrf.exempt(images_api_blueprint)

@app.errorhandler(500)
def internal_server_error(e):
        return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
        return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
        return render_template('users/new.html', errors={'Access': 'You do not have access.'}), 404

@login_manager.user_loader
def load_user(user_id):
        return User.get_by_id(user_id)

@app.route("/")
@login_required
def home():
        # Add all photos from users that current_user is following
        photos = []
        for user in current_user.following:
                gallery = Image.select().where(Image.user_id == user.id)
                photos.extend(gallery)   

        # Add user's image's as well
        current_user_photos = Image.select().where(Image.user_id == current_user.id)
        photos.extend(current_user_photos)

        # Suggested users to follow
        users = User.select().where(User.id != current_user.id)
        users = [user for user in users if user not in current_user.following]

        # If long users list, slice 5
        if len(users) > 5:
                users = users[0:5]

        return render_template('home.html', photos=photos, users=users)

# Wrap CSS files with unique ID to prevent browser caching errors
@app.context_processor
def override_url_for():
        return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
        if endpoint == 'static':
                filename = values.get('filename', None)
                if filename:
                        file_path = os.path.join(app.root_path, endpoint, filename)
                        values['q'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)

