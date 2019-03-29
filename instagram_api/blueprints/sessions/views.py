from flask import Blueprint

sessions_api_blueprint = Blueprint('sessions_api',
                                __name__,
                                template_folder='templates')


@sessions_api_blueprint.route('/', methods=['GET'])
def index():
    return "SESSIONS API"
