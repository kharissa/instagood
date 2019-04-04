from app import app
from flask import Blueprint, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from models.user import User
from models.image import Image
from models.relationship import Relationship
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import helpers
from models.task import Task

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

@users_blueprint.route('/edit', methods=['GET'])
@login_required
def edit():
        return render_template('users/edit.html', user=current_user)


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


@users_blueprint.route('/follow/<follower_id>/<following_id>')
@login_required
def follow(follower_id, following_id):
        follower = User.get_by_id(follower_id)
        following = User.get_by_id(following_id)

        if following.is_public:
                r = Relationship(follower=follower, following=following, is_approved=True)
        else:
                r = Relationship(follower=follower, following=following, is_approved=False)
                
        if r.save():
                if following.is_public:
                        flash(f"You are now following {following.name}.")
                        return redirect(url_for('users.show', username=following.username))
                else:
                        flash(f"A follow request has been sent to {following.name}.")    
                        rq_job = app.task_queue.enqueue(
                            'tasks.' + 'send_follow_request_email', following, follower, url_for('users.requests'))
                        task = Task(redis_job_id=rq_job.get_id(), name='send_follow_request_email',
                    description='Send user a follow request email.', relationship=r)
                        task.save()
                        return redirect(url_for('users.show', username=following.username))
        else:
                return render_template('users/show.html', user=following, photos=Image.select().where(Image.user_id == following.id), errors=r.errors)


@users_blueprint.route('/unfollow/<follower_id>/<following_id>')
@login_required
def unfollow(follower_id, following_id):
        from models.relationship import Relationship

        following = User.get_by_id(following_id)
        relationship = Relationship.get(Relationship.follower_id == follower_id, Relationship.following_id == following_id)
        t = Task.get(Task.relationship_id == relationship.id)
        t.delete_instance()
        relationship.delete_instance()
        flash(f"You have unfollowed {following.name}.")
        
        return render_template('users/show.html', user=following, photos=Image.select().where(Image.user_id == following.id))


@users_blueprint.route('/requests')
@login_required
def requests():
        from models.relationship import Relationship

        requests = [follower for follower in current_user.followers if not current_user.is_approved(follower.id)]

        return render_template('users/requests.html', requests=requests)


@users_blueprint.route('/approve/<user_id>')
@login_required
def approve(user_id):
        from models.relationship import Relationship

        follower = User.get_by_id(user_id)
        r = Relationship.get(Relationship.follower_id == user_id, Relationship.following_id == current_user.id)
        r.is_approved = True

        if r.save():
                flash(f"You have approved {follower.name}'s follow request.")
                return redirect(url_for('users.show', username=follower.username))
        else:
                return render_template('users/show.html', user=current_user, photos=Image.select().where(Image.user_id == current_user.id), errors=r.errors)


@users_blueprint.route('/reject/<user_id>')
@login_required
def reject(user_id):
        from models.relationship import Relationship

        follower = User.get_by_id(user_id)
        r = Relationship.get(Relationship.follower_id == user_id,
                             Relationship.following_id == current_user.id)
        t = Task.get(Task.relationship_id == relationship.id)
        t.delete_instance()
        r.delete_instance()
        flash(f"You have rejected {follower.name}'s follow request.")
        return redirect(url_for('users.show', username=current_user.username))
