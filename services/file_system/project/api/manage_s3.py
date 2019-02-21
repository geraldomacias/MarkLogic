# services/file_system/project/api/manage_s3.py

import os
import boto3
from flask import Blueprint, jsonify, request, make_response, send_file
from flask.views import MethodView
from flask_cors import CORS

#from project import bcrypt, db
from project.api.models import decode_auth_token, S3Files

s3_blueprint = Blueprint('s3', __name__)

CORS(s3_blueprint)

def uploads(user_id, all_files):
    client = boto3.client('s3')
    uploads_response = {
        'status': 'fail',
        'message': ''
    }
    
    bucket_name = os.getenv('S3_UPLOAD')
    file_type = "uploads"
    uploads_response['bucket'] = bucket_name
    uploads_response['user_id'] = user_id
    db_entry = {
        'user_id': user_id,
        'bucket_name': bucket_name
    }

    for files in all_files:
        cur_file = all_files[files]
        cur_name = all_files[files].filename

        if (cur_name == ''):
            uploads_response['message'] = 'no file selected'
            uploads_response['status_code'] = 400
            return (uploads_response)

        key_name = cur_name + '.' + user_id + '.' + file_type 

        client.upload_fileobj(
            Bucket=bucket_name, # name of the bucket
            Fileobj=cur_file, # this is the name of the file that is being uploaded
            Key=key_name
        )

        uploads_response[files + "_URL"] = key_name
        uploads_response[files] = cur_name

        db_entry['original_filename'] = cur_name
        db_entry['input_filename'] = cur_name
        db_entry['input_url'] = key_name
        
        S3Files(user_id = db_entry['user_id'],
                input_filename = db_entry['input_filename'],
                input_url = db_entry['input_url'],
                )
        
        db_entry['input_filename'] = ''
        db_entry['input_url'] = ''

    uploads_response['status'] = 'success'
    uploads_response['status_code'] = 200
    uploads_response['message'] = 'Everything is okay :)'

    return uploads_response


def classified(user_id, values, all_files):
    client = boto3.client('s3')
    classified_response = {
        'status': 'fail',
        'message': ''
    }

    bucket_name = os.getenv('S3_CLASSIFIED')
    file_type = "classified"
    classified_response['bucket'] = bucket_name
    classified_response['user_id'] = user_id
    db_entry = {
        'user_id': user_id,
        'bucket_name': bucket_name
    }

    if (len(all_files) != 1):
        classified_response['message'] = 'For classified files, only submit one'
        classified_response['status'] = 400
        return classified_response
        

    for files in all_files:
        cur_file = all_files[files]
        cur_name = all_files[files].filename

        if (cur_name == ''):
            classified_response['message'] = 'no file selected'
            classified_response['status'] = 400
            return classified_response

        key_name = cur_name + '.' + user_id + '.' + file_type 

        client.upload_fileobj(
            Bucket=bucket_name, # name of the bucket
            Fileobj=cur_file, # this is the name of the file that is being uploaded
            Key=key_name
        )

        classified_response[files + "_URL"] = key_name
        classified_response[files] = cur_name

        db_entry['input_filename'] = cur_name
        db_entry['input_url'] = key_name
        
    for values in request.values:
        if "orig_file" in values:
            orig_file = request.values.get(values)
            db_entry['original_filename'] = orig_file

            # TODO: Query and find which row to add to
            S3Files(user_id = db_entry['user_id'],
                    input_filename = db_entry['input_filename'],
                    input_url = db_entry['input_url'],
                    )


    classified_response['status'] = 'success'
    classified_response['status_code'] = 200
    classified_response['message'] = 'Everything is okay :)'
    return classified_response

class UploadAPI(MethodView):

    def post(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }

        status_code = 401

        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject['message'] = 'Bearer token malformed.'
                return make_response(jsonify(responseObject)), status_code
        else:
            auth_token = ''
        if auth_token:
            resp = decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user_id = resp
                responseObject['user_id'] = user_id
            else:
                responseObject = {
                    'status': 'fail',
                    'message': "Issue with auth_token: " + resp
                }
                return make_response(jsonify(responseObject)), status_code
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), status_code

        if isinstance(user_id, int):
            user_id = str(user_id)

        if user_id == None or user_id == '' :
            responseObject['message'] = "No user_id found"
            status_code = 400
            return jsonify(responseObject), status_code


        if (request.values.get('bucket_name') == 'uploads'):
            uploads_response = uploads(user_id, request.files)
            responseObject['uploads_response'] = uploads_response
            responseObject['status'] = uploads_response['status']
            responseObject['message'] = uploads_response['message']
            status_code = uploads_response['message']

        elif (request.values.get('bucket_name') == 'classified'):
            classified_response = classified(user_id, request.values, request.files)
            responseObject['classified_response'] = classified_response
            responseObject['status'] = classified_response['status']
            responseObject['message'] = classified_response['message']
            status_code = classified_response['message']

        else:
            responseObject['message'] = "Incorrect bucket name passed"
            return make_response(jsonify(responseObject)), 401
        
        response_object = {
            'status': responseObject['status'],
            'data': responseObject
        }
        return make_response(jsonify(response_object)), status_code


class DownloadAPI(MethodView):

    def get(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }


        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject['message'] = 'Bearer token malformed.'
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user_id = resp
                responseObject['user_id'] = user_id
            else:
                responseObject = {
                    'status': 'fail',
                    'message': "Issue with auth_token: " + resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

        if isinstance(user_id, int):
            user_id = str(user_id)

        if user_id == None or user_id == '' :
            responseObject['message'] = "No user_id found"
            return make_response(jsonify(responseObject)), 400


        # Get bucket_name
        if (request.values.get('bucket_name') == 'uploads'):
            bucket_name = os.getenv('S3_UPLOAD')
            file_type = "uploads"
            download_url = "https://s3-us-west-2.amazonaws.com/capstone.upload/"
        elif (request.values.get('bucket_name') == 'classified'):
            bucket_name = os.getenv('S3_CLASSIFIED')
            file_type = "classified"
            download_url = "https://s3-us-west-2.amazonaws.com/capstone.classified/"
        else:
            responseObject['message'] = "passed: " + request.values.get('bucket_name')
            return make_response(jsonify(responseObject)), 401

        if ("classified_filename" in request.values) and (file_type == "classified"): # Given classified, get all orig files
            orig_file_list = [] # orig_filenames
            orig_file_type = "uploads"

            # TODO: Query for all orig files
            for values in orig_file_list:
                key_name = values + '.' + user_id + '.' + orig_file_type
                responseObject[values + '_download_url'] = (download_url + key_name).replace(" ", "+")
                responseObject[values + '_key_name'] = key_name


        else:
            for values in request.values:
                if "orig_file" in values:
                    orig_file = request.values.get(values)
                    responseObject[values] = orig_file
                    key_name = orig_file + '.' + user_id + '.' + file_type
                    responseObject[values + '_download_url'] = (download_url + key_name).replace(" ", "+")
                    responseObject[values + '_key_name'] = key_name

        # Commented section: Gets a file name to save the downloaded file as
        # Get file_name
        """
        if 'file_name' not in request.values:
            responseObject['message'] = "No file name to save as"
            return make_response(jsonify(responseObject)), 400
        elif request.values.get('file_name') == '':
            responseObject['message'] = "No file name to save as"
            return make_response(jsonify(responseObject)), 400
        else:
            file_name = request.values.get('file_name')
        """

        
        # Commented section: Attemps to get file from S3 in memory and send_file. Both methods work for getting file from S3. Send_file just sends empty 
        """
        client = boto3.client('s3')
        with open('temporary.csv', 'wb') as data:
            client.download_fileobj(  # stores in /../../.
                Bucket=bucket_name, # name of the bucket
                Fileobj=data, # this is the name you want the downloaded file saved as
                Key=key_name # generated key name
            )

        data = open ('temporary.csv', 'r') 
        return send_file(data, 
            as_attachment=True, 
            attachment_filename=file_name
        ) 
        """
        
        responseObject['bucket'] = bucket_name
        responseObject['user_id'] = user_id
        responseObject['status'] = 'success'

        response_object = {
            'status': 'success',
            'data': responseObject,
            'message': 'Everything is okay :)'
        }
        
        return make_response(jsonify(response_object)), 200

upload_view = UploadAPI.as_view('upload_api')
download_view = DownloadAPI.as_view('download_api')

s3_blueprint.add_url_rule(
    '/s3/upload',
    view_func=upload_view,
    methods=['POST']
)
s3_blueprint.add_url_rule(
    '/s3/download',
    view_func=download_view,
    methods=['GET']
)

