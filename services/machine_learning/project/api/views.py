# services/machine_learning/project/api/views.py

import json, requests
from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from flask_cors import CORS 

from project import db 
from project.api.models import BlacklistToken, MLStatus, decode_auth_token
from project.csv_parser import extract_columns

from flask import current_app

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
                    if status.status == 'Waiting for files.' or status.status == 'Completed.' or status.status == "Failed to process files.":
                        status.selected_files = files
                        status.status = 'Processing.'
                        db.session.commit()
                        # TODO: @D3lta - Trigger your method here
                        print("Creating Parse Thread\n")
                        parseThread = Thread(target=extract_columns, args=(current_app._get_current_object(), auth_token, files))
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
                if status == 'Failed to process files.':
                    responseObject = {
                        'status': 'success',
                        'message': status.status,
                        'error_msg': status.error_msg
                    }
                    return make_response(jsonify(responseObject)), 200
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

class MLGetClassifiedJson(MethodView):
    """
    Return Classified JSON
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
            # Check if decode_auth_token returned a string (which means it failed)
            # If it succeeded, resp now holds the user_id value
            if not isinstance(resp, str):
                # Get a status row for the user
                status = MLStatus.query.filter_by(user_id=resp).first()
                if not status:
                    # User not in status table - error
                    responseObject = {
                        'status': 'fail',
                        'message': 'User has not classified any data.'
                    }
                    return make_response(jsonify(responseObject)), 404
                else:
                    if status.status == "Completed.":
                        # make sure row has JSON value
                        resp_json = status.classified_json
                        if resp_json:
                            responseObject = {
                                'status': 'success',
                                'message': 'Returning classified information.',
                                'data': resp_json
                            }
                            return make_response(jsonify(responseObject)), 200
                        else:
                            # No json object in db for user
                            responseObject = {
                                'status': 'fail',
                                'message': 'No classified data found for given user.'
                            }
                            return make_response(jsonify(responseObject)), 404
                    else:
                        # ML has not yet completed for user
                        responseObject = {
                            'status': 'fail',
                            'message': 'Classification not yet completed for given user. Current status: ' + status.status
                        }
                        return make_response(jsonify(responseObject)), 401
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

class MLGetPastClassifiedAsJson(MethodView):
    """
    Return a Past Classification as JSON
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
                # Get the filename from the post
                post_data = request.get_json()
                if post_data:
                    file_name = post_data.get('file_name')
                    if file_name:
                        download_url = ""
                        # check if config is TESTING
                        if current_app.config.get('TESTING'):
                            if file_name == 'bad_download_code':
                                # Simulate a bad download code
                                download_url = "https://raw.githubusercontent.com/geraldomacias/MarkLogic/non_existant_branch/"
                            else:
                                # Set download_url to a test json file on repo
                                download_url = "https://raw.githubusercontent.com/geraldomacias/MarkLogic/spencer-dev/services/machine_learning/project/tests/test.json"
                        else:
                            # Get download_url from file_system endpoint
                            file_system_url = "http://file_system:5000/s3/downloadClassified"
                            file_system_headers = {"Authorization": 'Bearer ' + auth_token}
                            file_system_params = {"classified": file_name}

                            url_response = requests.get(url = file_system_url, headers = file_system_headers, params = file_system_params)
                            if url_response.status_code == 200:
                                url_key = file_name + '_download_url'
                                download_url = (url_response.json())['data']['classified_response'][url_key]
                            else:
                                responseObject = {
                                    'status': 'fail',
                                    'message': 'Error connecting to file_system.'
                                }
                                return make_response(jsonify(responseObject)), 500
                        download_response = requests.get(download_url)
                        if download_response.status_code == 200:
                            responseObject = {
                                'status': 'success',
                                'message': 'Returning classified information.',
                                'data': download_response.json()
                            }
                            return make_response(jsonify(responseObject)), 200
                        else:
                            responseObject = {
                                'status': 'fail',
                                'message': 'Bad response from download url. Please try downloading again, or classify your csv again.'
                            }
                            return make_response(jsonify(responseObject)), 404
                    else:
                        responseObject = {
                        'status': 'fail',
                        'message': 'File name not provided.'
                    }
                    return make_response(jsonify(responseObject)), 400
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'File name not provided.'
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

# Define the API resources
ml_start_view = MLStartAPI.as_view('startml_api')
ml_status_view = MLStatusAPI.as_view('statusml_api')
ml_get_classified_view = MLGetClassifiedJson.as_view('getclassified_api')
ml_get_past_classified_json_view = MLGetPastClassifiedAsJson.as_view('getpastclassificationasjson_api')

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
ml_blueprint.add_url_rule(
    '/ml/classified',
    view_func=ml_get_classified_view,
    methods=['GET']
)
ml_blueprint.add_url_rule(
    '/ml/past_classified_json',
    view_func=ml_get_past_classified_json_view,
    methods=['POST']
)