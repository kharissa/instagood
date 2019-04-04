import os
from app import app
from models.user import User
from models.task import Task
from models.image import Image
from models.transaction import Transaction
from models.relationship import Relationship
from flask_login import current_user, login_required
from helpers import generate_client_token, transact, find_transaction
from flask import Blueprint, Flask, redirect, url_for, render_template, request, flash

relationships_blueprint = Blueprint('relationships', __name__, template_folder='templates')

@relationships_blueprint.route('/<following_id>/new')
@login_required
def new(following_id):
    follower = User.get_by_id(current_user.id)
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
            flash(
                f"A follow request has been sent to {following.name}.")
            rq_job = app.task_queue.enqueue(
                'tasks.' + 'send_follow_request_email', following, follower, url_for('relationships.index'))
            task = Task(redis_job_id=rq_job.get_id(), name='send_follow_request_email',
                        description='Send user a follow request email.', relationship=r)
            task.save()
            return redirect(url_for('users.show', username=following.username))
    else:
        return render_template('users/show.html', user=following, photos=Image.select().where(Image.user_id == following.id), errors=r.errors)


@relationships_blueprint.route('/<following_id>/delete')
@login_required
def destroy(following_id):
    following = User.get_by_id(following_id)
    relationship = Relationship.get(
        Relationship.follower_id == current_user.id, Relationship.following_id == following_id)

    if relationship.id in Task.select():
        t = Task.get(Task.relationship_id == relationship.id)
        t.delete_instance()

    relationship.delete_instance()
    flash(f"You have unfollowed {following.name}.")

    return render_template('users/show.html', user=following, photos=Image.select().where(Image.user_id == following.id))


@relationships_blueprint.route('/')
@login_required
def index():
    requests = [follower for follower in current_user.followers if not current_user.is_approved(follower.id)]

    return render_template('relationships/index.html', requests=requests)


@relationships_blueprint.route('<user_id>/approve/')
@login_required
def approve(user_id):
    follower = User.get_by_id(user_id)
    r = Relationship.get(Relationship.follower_id == user_id, Relationship.following_id == current_user.id)
    r.is_approved = True

    if r.save():
            flash(f"You have approved {follower.name}'s follow request.")
            return redirect(url_for('users.show', username=follower.username))
    else:
            return render_template('users/show.html', user=current_user, photos=Image.select().where(Image.user_id == current_user.id), errors=r.errors)


@relationships_blueprint.route('/<user_id>/reject')
@login_required
def reject(user_id):
    follower = User.get_by_id(user_id)
    r = Relationship.get(Relationship.follower_id == user_id, Relationship.following_id == current_user.id)

    if r.id in Task.select():
        t = Task.get(Task.relationship_id == r.id)
        t.delete_instance()

    r.delete_instance()
    flash(f"You have rejected {follower.name}'s follow request.")
    return redirect(url_for('users.show', username=current_user.username))
