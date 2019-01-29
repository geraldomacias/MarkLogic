# services/file_system/project/api/manage_s3.py

import os
import boto3
from flask import Blueprint, jsonify, request, Flask, make_response
from flask.views import MethodView
from flask_cors import CORS

# from project import bcrypt, db
from models import decode_auth_token


s3_blueprint = Blueprint('s3', __name__)

CORS(s3_blueprint)

class UploadAPI(MethodView):
    
    def post(self):
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



        # TODO: need to change to make it get user_id from token
        user_id = decode_auth_token()

        if 'file' not in request.files:
            print('no file passed')
            return jsonify(response_object), 400

        file_passed = request.files['file'] 
        file_name = file_passed.filename

        if (file_name == ''):
            print('no file selected')
            return jsonify(response_object), 400

        # saves to a temp location
        file_passed.save(os.path.join(os.getenv('UPLOAD_FOLDER'), file_name))

        if (requests.args.get('bucket_name', None) == 'uploads'):
            bucket_name = os.getenv('S3_UPLOAD')
            file_type = "uploads"
        else:
            bucket_name = os.getenv('S3_CLASSIFIED')
            file_type = "classified"

        client = boto3.client('s3')
        key_name = file_name + '.' + user_id + '.' + file_type # this is the name of the file that will be stored in the bucket
    
        client.upload_file(
            Bucket=bucket_name, # name of the bucket
            Filename=os.getenv('UPLOAD_FOLDER') + file_name, # this is the name of the file that is being uploaded
            Key=key_name
        )

        # TODO: Check to see if user and file exist in DB
        # TODO: if yes, update with URL. else create new item

        response_object = {
            'status': 'success',
            'data': {
                'bucket_name': bucket_name,
                'file_name': file_name,
                'user_id': user_id,
                'key_name': key_name
            }
        }
        return make_response(jsonify(response_object)), 200


class DownloadAPI(MethodView):

    def get(self):
        file_name = request.args.get('file_name', None) 
        orig_file_name = request.args.get('orig_file_name', None) 
        user_id = request.args.get('user_id', None)

        if (requests.args.get('bucket_name', None) == 'uploads'):
            bucket_name = os.getenv('S3_UPLOAD')
            file_type = "uploads"
        else:
            bucket_name = os.getenv('S3_CLASSIFIED')
            file_type = "classified"

        client = boto3.client('s3')
        key_name = orig_file_name + '.' + user_id + '.' + file_type # this is the name of the file that was stored in the bucket

        client.download_file( 
            Bucket=bucket_name, # name of the bucket
            Filename=file_name, # this is the name you want the downloaded file saved as
            Key=key_name
        )

        response_object = {
            'status': 'success',
            'data': {
                'bucket_name': bucket_name,
                'file_name': file_name,
                'orig_file_name': orig_file_name,
                'user_id': user_id
            }
        }
        return make_response(jsonify(response_object)), 200

upload_view = UploadAPI.as_view('upload_api')
download_view = DownloadAPI.as_view('download_api')

s3_blueprint.add_url_rule(
    '/users/upload',
    view_func=upload_view,
    methods=['POST']
)
s3_blueprint.add_url_rule(
    '/users/download',
    view_func=download_view,
    methods=['GET']
)

