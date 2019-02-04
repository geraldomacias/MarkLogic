# services/machine_learning/project/api/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from flask_cors import CORS 

from project import db 
from project.api.models import BlacklistToken, decode_auth_token

ml_blueprint = Blueprint('ml', __name__)

CORS(ml_blueprint)

# Starts the ml component and provides filenames
class MLStartAPI(MethodView):
    """
    Machine-Learning Starter
    """

    def post(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = decode_auth_token(auth_token)
            # Check if decode_auth_token returned a string (which means it failed)
            # If it succeeded, resp now holds the user_id value
            if not isinstance(resp, str):
                # Get the filenames from the post
                post_data = request.get_json()
                if post_data:
                    files = post_data.get('files')
                    if len(files) <= 0:
                        responseObject = {
                            'status': 'fail',
                            'message': 'No files provided.'
                        }
                        return make_response(jsonify(responseObject)), 400
                    else:
                        for file_name in files:
                            # TODO : Do something with these filenames (they are strings) @D3LTA
                            print(file_name)
                        responseObject = {
                            'status': 'success',
                            'message': 'Successfully started ML on ' + str(len(files)) + ' files.'
                        }
                        return make_response(jsonify(responseObject)), 200
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'No files provided.'
                    }
                    return make_response(jsonify(responseObject)), 400
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

class MLStatusAPI(MethodView):
    """
    Machine-Learning Status
    """

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = decode_auth_token(auth_token)
            # Check if decode_auth_token returnned a string (which means it failed)
            # If it succeeded, resp now holds the user_id value
            if not isinstance(resp, str):
                # TODO : Return the actual status (completed, maybe % complete?? Put this info in the 'message')
                responseObject = {
                    'status': 'success',
                    'message': 'ThE mAcHiNe MiGhT bE lEaRnInG.'
                }
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

# Define the API resources
ml_start_view = MLStartAPI.as_view('startml_api')
ml_status_view = MLStatusAPI.as_view('statusml_api')

# Add rules for API endpoints
ml_blueprint.add_url_rule(
    '/ml/start',
    view_func=ml_start_view,
    methods=['POST']
)
ml_blueprint.add_url_rule(
    '/ml/status',
    view_func=ml_status_view,
    methods=['GET']
)