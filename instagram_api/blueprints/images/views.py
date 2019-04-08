from models.user import User
from models.image import Image
from flask import Blueprint, jsonify, request
from helpers import decode_auth_token
from flask_login import current_user

images_api_blueprint = Blueprint('images_api',
                                   __name__,
                                   template_folder='templates')


@images_api_blueprint.route('/', methods=['GET'])
def index():
    user_id = request.args.get('userId')
    if user_id:
        try:
            user = User.get_by_id(user_id)
            images = Image.select().where(Image.user_id == user.id)
            return jsonify([image.url for image in images])
        except:
            return jsonify([{
                'status': 'failed',
                'message': 'User cannot be found.'
            }])
    else: 
        images = Image.select()
        return jsonify([image.url for image in images])


@images_api_blueprint.route('/me', methods=['GET'])
def show():

    auth_header = request.headers.get('Authorization')

    if auth_header:
        token = auth_header.split(" ")[1]
    else:
        return jsonify([{
            'status': 'failed',
            'message': 'Not authorization header.'
        }])

    decoded = decode_auth_token(token)

    try: 
        user = User.get(User.id == decoded)
        images = Image.select().where(Image.user_id == user.id)
        return jsonify([image.url for image in images])
    except:
        return jsonify([{
            'status': 'failed',
            'message': 'Authentication failed.'
        }])
