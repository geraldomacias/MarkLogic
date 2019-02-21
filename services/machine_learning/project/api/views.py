# services/machine_learning/project/api/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from flask_cors import CORS 

from project import db 
from project.api.models import BlacklistToken, MLStatus, decode_auth_token
from project.api.csv_parser import extract_columns

from threading import Thread

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
                    # Get the current user status
                    status = MLStatus.query.filter_by(user_id=resp).first()
                    if not status:
                        # User not in status table - add them now
                        try:
                            user = MLStatus(
                                user_id = resp,
                                status = "Waiting for files."
                            )

                            # insert the user
                            db.session.add(user)
                            db.session.commit()

                            # update status object to reference newly created user
                            status = MLStatus.query.filter_by(user_id=resp).first()
                            if not status:
                                responseObject = {
                                    'status': 'fail',
                                    'message': 'User could not be added to status database.'
                                }
                                return make_response(jsonify(responseObject)), 401
                        except Exception as e:
                            responseObject = {
                                'status': 'fail',
                                'message': 'Some error occurred. Please try again.'
                            }
                            return make_response(jsonify(responseObject)), 401
                    # Check the user's status - make sure its "Waiting for files."
                    if status.status == 'Waiting for files.':
                        status.selected_files = files
                        status.status = 'Processing.'
                        db.session.commit()
                        # TODO: @D3lta - Trigger your method here
                        parseThread = Thread(target=csv_parser.extract_columns, args=(auth_token, files))
                        parseThread.start()
                        parseThread.join()
                    else:
                        # User is not ready for files - still processing?
                        responseObject = {
                            'status': 'fail',
                            'message': 'Already processing files for this user.'
                        }
                        return make_response(jsonify(responseObject)), 401
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
                # Check the ml status for the user
                status = MLStatus.query.filter_by(user_id=resp).first()
                if not status:
                    # User not in status table - add them now
                    try:
                        user = MLStatus(
                            user_id = resp,
                            status = "Waiting for files."
                        )

                        # insert the user
                        db.session.add(user)
                        db.session.commit()

                        # update status object to reference newly created user
                        status = MLStatus.query.filter_by(user_id=resp).first()
                        if not status:
                            responseObject = {
                                'status': 'fail',
                                'message': 'User could not be added to status database.'
                            }
                            return make_response(jsonify(responseObject)), 401
                    except Exception as e:
                        responseObject = {
                            'status': 'fail',
                            'message': 'Some error occurred. Please try again.'
                        }
                        return make_response(jsonify(responseObject)), 401
                responseObject = {
                    'status': 'success',
                    'message': status.status
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