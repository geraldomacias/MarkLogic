# services/file_system/project/api/manage_s3.py

import os
import boto3
from flask import Blueprint, jsonify, request, make_response
from flask.views import MethodView
from flask_cors import CORS

# from project import bcrypt, db
from project.api.models import decode_auth_token
from project.api.AWSCreds import *

s3_blueprint = Blueprint('s3', __name__)

CORS(s3_blueprint)

class UploadAPI(MethodView):
    
    def post(self):
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
            return jsonify(responseObject), 400

        client = boto3.client('s3',
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key= ACCESS_KEY)

        if (request.values.get('bucket_name') == 'uploads'):
            bucket_name = os.getenv('S3_UPLOAD')
            file_type = "uploads"
        elif (request.values.get('bucket_name') == 'classified'):
            bucket_name = os.getenv('S3_CLASSIFIED')
            file_type = "classified"
        else:
            responseObject['message'] = "Incorrect bucket name passed"
            return make_response(jsonify(responseObject)), 401
        responseObject['bucket'] = bucket_name
        responseObject['user_id'] = user_id


        for files in request.files:
            cur_file = request.files[files]
            cur_name = request.files[files].filename
            responseObject[files] = cur_name


            if (cur_name == ''):
                print('no file selected')
                return jsonify(responseObject), 400

            key_name = cur_name + '.' + user_id + '.' + file_type # this is the name of the file that will be stored in the bucket

            client.upload_fileobj(
                Bucket=bucket_name, # name of the bucket
                Fileobj=cur_file, # this is the name of the file that is being uploaded
                Key=key_name
            )

            responseObject[files] = key_name


        # TODO: Check to see if user and file exist in DB
        # TODO: if yes, update with URL. else create new item

        responseObject['status'] = 'success'
        responseObject['message'] = 'Everything is okay :)'

        response_object = {
            'status': 'success',
            'data': responseObject
        }
        return make_response(jsonify(response_object)), 200


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
            return jsonify(responseObject), 400

        # Get Key_name
        if 'key_name' not in request.values:
            responseObject['message'] = "No key name given"
            return jsonify(responseObject), 400
        elif request.values.get('key_name') == '':
            responseObject['message'] = "No key name given"
            return jsonify(responseObject), 400
        else:
            key_name = request.values.get('key_name')

        # Get file_name
        if 'file_name' not in request.values:
            responseObject['message'] = "No file name to save as"
            return jsonify(responseObject), 400
        elif request.values.get('file_name') == '':
            responseObject['message'] = "No file name to save as"
            return jsonify(responseObject), 400
        else:
            file_name = request.values.get('file_name')

        # Get bucket_name
        if (request.values.get('bucket_name') == 'uploads'):
            bucket_name = os.getenv('S3_UPLOAD')
            file_type = "uploads"
        elif (request.values.get('bucket_name') == 'classified'):
            bucket_name = os.getenv('S3_CLASSIFIED')
            file_type = "classified"
        else:
            responseObject['message'] = "passed: " + request.values.get('bucket_name')
            return make_response(jsonify(responseObject)), 401
        responseObject['key_name'] = key_name
        responseObject['file_name'] = file_name
        responseObject['bucket'] = bucket_name
        responseObject['user_id'] = user_id

        client = boto3.client('s3',
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key= ACCESS_KEY)

        with open (file_name, 'wb') as data:
            client.download_fileobj( 
                Bucket=bucket_name, # name of the bucket
                Fileobj=data, # this is the name you want the downloaded file saved as
                Key=key_name
            )
            responseObject['data'] = data

        responseObject['new_file'] = file_name
        responseObject['message'] = 'Everything is okay :)'
        responseObject['status'] = 'success'

        response_object = {
            'status': 'success',
            'data': responseObject
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

