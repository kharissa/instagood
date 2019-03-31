from flask import Blueprint

images_api_blueprint = Blueprint('images_api',
                                   __name__,
                                   template_folder='templates')


@images_api_blueprint.route('/', methods=['GET'])
def index():
    return "IMAGES API"
