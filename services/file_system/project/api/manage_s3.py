# services/file_system/project/api/manage_s3.py

import boto3
from flask import Blueprint, jsonify, request, Flask

s3_blueprint = Blueprint('s3', 's3', url_prefix='/s3')

@s3_blueprint.route('/upload', methods=['GET'])
def upload_to_bucket():
    bucket_name = request.args.get('bucket_name', None) 
    file_name = request.args.get('file_name', None) 
    user_name = request.args.get('user_name', None) 
    
    client = boto3.client('s3')
    
    client.upload_file(
        Bucket=bucket_name, # name of the bucket
        Filename=file_name, # this is the name of the file that is being uploaded
        Key=file_name + user_name # this is the name of the file that will be stored in the bucket
    )

    response_object = {
        'status': 'success',
        'data': {
            'bucket_name': bucket_name,
            'file_name': file_name,
            'user_name': user_name
        }
    }
    return jsonify(response_object), 200


@s3_blueprint.route('/download', methods=['GET'])
def download_from_bucket():
    bucket_name = request.args.get('bucket_name', None) 
    file_name = request.args.get('file_name', None) 
    orig_file_name = request.args.get('orig_file_name', None) 
    user_name = request.args.get('user_name', None)
    
    client = boto3.client('s3')
    
    client.download_file( 
        Bucket=bucket_name, # name of the bucket
        Filename=file_name, # this is the name you want the downloaded file saved as
        Key=orig_file_name+user_name # this is the key that was used to upload the file. use same format
    )
    
    response_object = {
        'status': 'success',
        'data': {
            'bucket_name': bucket_name,
            'file_name': file_name,
            'orig_file_name': orig_file_name,
            'user_name': user_name
        }
    }
    return jsonify(response_object), 200
