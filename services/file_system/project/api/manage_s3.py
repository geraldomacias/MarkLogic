# services/file_system/project/api/manage_s3.py

import boto3
from flask import Blueprint, jsonify, request, Flask
import bucketNames

s3_blueprint = Blueprint('s3', 's3', url_prefix='/s3')

@s3_blueprint.route('/upload', methods=['GET'])
def upload_to_bucket(*argv):
    if (len(argv) == 0): # This is for prod.
        file_name = request.args.get('file_name', None) 
        user_id = request.args.get('user_id', None) 
    elif (len(argv) == 2): # This is for testing (inputting own values)
        file_name = argv[0]
        user_id = argv[1]
    else:
        print("Incorrect Function call.")
        return

    if (requests.args.get('bucket_name', None) == 'uploads'):
        bucket_name = bucketNames.S3UPLOAD
        file_type = "uploads"
    else:
        bucket_name = bucketNames.S3CLASSIFIED
        file_type = "classified"

    client = boto3.client('s3')
    key_name = file_name + '.' + user_id + '.' + file_type # this is the name of the file that will be stored in the bucket
    
    client.upload_file(
        Bucket=bucket_name, # name of the bucket
        Filename=file_name, # this is the name of the file that is being uploaded
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
    return jsonify(response_object), 200


@s3_blueprint.route('/download', methods=['GET'])
def download_from_bucket():
    file_name = request.args.get('file_name', None) 
    orig_file_name = request.args.get('orig_file_name', None) 
    user_id = request.args.get('user_id', None)

    if (requests.args.get('bucket_name', None) == 'uploads'):
        bucket_name = bucketNames.S3UPLOAD
        file_type = "uploads"
    else:
        bucket_name = bucketNames.S3CLASSIFIED
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
    return jsonify(response_object), 200

# For testing
#if __name__ == '__main__':
   #upload_to_bucket('Basic_Stats.csv', 'veazey-test')
   #download_from_bucket('csc402uploads', 'Basic_Stats_new.csv', 'Basic_Stats.csv', 'veazey-test')

