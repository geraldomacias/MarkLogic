# services/users/project/api/manage_s3.py

import boto3
from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from project.api.models import User
from project import db

s3_blueprint = Blueprint('s3', __name__)


@s3_blueprint.route('/s3/upload/<bucket_name, file_name, user_name>', methods=['POST'])
def upload_to_bucket():
    bucket_name = request.args.get('bucket_name', None) 
    file_name = request.args.get('file_name', None) 
    user_name = request.args.get('user_name', None) 
    
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    
    client.upload_file(
        Bucket=bucket_name, # name of the bucket
        Filename=file_name, # this is the name of the file that is being uploaded
        Key=file_name + user_name # this is the name of the file that will be stored in the bucket
    )


@s3_blueprint.route('/s3/download/<bucket_name, file_name, orig_file_name, user_name>', methods=['GET'])
def download_from_bucket():
    bucket_name = request.args.get('bucket_name', None) 
    file_name = request.args.get('file_name', None) 
    orig_file_name = request.args.get('orig_file_name', None) 
    user_name = request.args.get('user_name', None)
    
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    
    client.download_file( 
        Bucket=bucket_name, # name of the bucket
        Filename=file_name, # this is the name you want the downloaded file saved as
        Key=orig_file_name+user_name # this is the key that was used to upload the file. use same format
    )

#if __name__ == '__main__':
    #upload_to_bucket('csc402uploads', 'Basic_Stats.csv', 'veazey-test')
    #download_from_bucket('csc402uploads', 'Basic_Stats_new.csv', 'Basic_Stats.csv', 'veazey-test')
