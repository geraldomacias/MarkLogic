# services/file_system/project/api/manage_s3.py

import boto3
from flask import Blueprint, jsonify, request, Flask
import bucketNames

s3_blueprint = Blueprint('s3', 's3', url_prefix='/s3')

@s3_blueprint.route('/upload', methods=['GET'])
def upload_to_bucket(*argv):
    if (len(argv) == 0): # This is for prod.
        file_name = request.args.get('file_name', None) 
        user_name = request.args.get('user_name', None) 
    elif (len(argv) == 2): # This is for testing (inputting own values)
        file_name = argv[0]
        user_name = argv[1]
    else:
        print("Incorrect Function call.")
        return

    if (requests.args.get('bucket_name', None) == 'uploads'):
        bucket_name = bucketNames.S3UPLOAD
    else:
        bucket_name = bucketNames.S3CLASSIFIED

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
    file_name = request.args.get('file_name', None) 
    orig_file_name = request.args.get('orig_file_name', None) 
    user_name = request.args.get('user_name', None)
    
    bucket_name = bucketNames.S3CLASSIFIED
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

# For testing
#if __name__ == '__main__':
   #upload_to_bucket('Basic_Stats.csv', 'veazey-test')
   #download_from_bucket('csc402uploads', 'Basic_Stats_new.csv', 'Basic_Stats.csv', 'veazey-test')

