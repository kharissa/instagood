from models.user import User
import datetime
import os
from flask import Blueprint, jsonify, request, redirect, url_for
from models.image import Image
from flask import Blueprint
from app import app
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_required, current_user, login_user
import jwt
from helpers import encode_auth_token, decode_auth_token

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        users = User.select()
        return jsonify(
            [{'userId': user.id,
            'username': user.username,
            'profileImage':user.profile_image_url} for user in users]
        )
    elif request.method == "POST":
        req_data = request.get_json()
        name = req_data['data']['name']
        email = req_data['data']['email']
        username = req_data['data']['username']
        password = req_data['data']['password']
        hashed_password = generate_password_hash(password)

        u = User(name=name, email=email, username=username, password=hashed_password)
        if u.save():
            login_user(u)
            token = encode_auth_token(u)
            return jsonify([{
                'auth_token': token,
                'message': 'Successfully created a user and signed in.',
                'status': 'success',
                'user': {
                    'id': u.id,
                    'profile_picture': u.profile_image_url,
                    'username': u.username
            }}])
        else:
            errors = u.errors
            return jsonify([{
                'status': 'failed',
                'message': errors
            }])
    else:
        return jsonify([{
            'message': 'Not correct method.', 
            'status': 'failed'
        }])
