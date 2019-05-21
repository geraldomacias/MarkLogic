# services/file_system/project/api/manage_s3.py
    #from project.api.upload_s3 import s3_upload_blueprint
    #app.register_blueprint(s3_upload_blueprint)

import os
import boto3
from boto3.s3.transfer import S3Transfer
from flask import Blueprint, jsonify, request, make_response, send_file
from flask.views import MethodView
from flask_cors import CORS
import json
import zipfile

from project import db
from project.api.models import decode_auth_token, S3InputFiles, S3ClassifiedFiles

s3_blueprint = Blueprint('s3', __name__)

CORS(s3_blueprint)


def get_authentication(auth_header):
    responseObject = {
        'status': 'fail',
        'message': '',
        'status_code': 401,
        'user_id': -1
    }

    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            responseObject['message'] = 'Bearer token malformed.'
            return responseObject
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
            return responseObject
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return responseObject

    if isinstance(user_id, int):
        user_id = str(user_id)

    if user_id == None or user_id == '' :
        responseObject['message'] = "No user_id found"
        responseObject['status_code'] = 400
        return responseObject

    responseObject['user_id'] = user_id
    responseObject['status_code'] = 200
    return responseObject


def uploads(user_id, all_files):
    client = boto3.client('s3')
    uploads_response = {
        'status': 'fail',
        'message': '',
        'status_code': 401
    }
    
    bucket_name = os.getenv('S3_UPLOAD')
    file_type = "uploads"
    uploads_response['bucket'] = bucket_name
    download_url = "https://s3-us-west-2.amazonaws.com/capstone.upload/"

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

        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key_name
            }
        )

        uploads_response[files + "_URL"] = url.replace("//s3", "//s3-us-west-2")
        # uploads_response[files + "_URL"] = (download_url + key_name).replace(" ", "+")
        uploads_response[files] = cur_name
        
        new_row = S3InputFiles(
            user_id = user_id,
            filename = cur_name,
            url = (download_url + key_name).replace(" ", "+")
        )
        
        try:
            cur_row = S3InputFiles.query.filter(S3InputFiles.user_id == user_id, 
                                    S3InputFiles.filename == cur_name).one()
            if (cur_row.deleted == True):
                cur_row.deleted = False
            db.session.flush()
        except:
            db.session.add(new_row)
        finally:
            db.session.commit()

    uploads_response['status'] = 'success'
    uploads_response['status_code'] = 200
    uploads_response['message'] = 'Everything is okay :)'

    return uploads_response


def classified(user_id, values, all_files):
    client = boto3.client('s3')
    classified_response = {
        'status': 'fail',
        'message': '',
        'status_code': 401
    }

    bucket_name = os.getenv('S3_CLASSIFIED')
    file_type = "classified"
    classified_response['bucket'] = bucket_name
    download_url = "https://s3-us-west-2.amazonaws.com/capstone.classified/"

    classified_name = ""
    classified_key = ""

    if (len(all_files) != 1):
        classified_response['message'] = 'For classified files, only submit one'
        classified_response['status_code'] = 400
        return classified_response
        

    for files in all_files:
        cur_file = all_files[files]
        cur_name = all_files[files].filename

        if (cur_name == ''):
            classified_response['message'] = 'no file selected'
            classified_response['status_code'] = 400
            classified_response['status'] = 'fail'
            return classified_response

        key_name = cur_name + '.' + user_id + '.' + file_type 

        client.upload_fileobj(
            Bucket=bucket_name, # name of the bucket
            Fileobj=cur_file, # this is the name of the file that is being uploaded
            Key=key_name
        )

        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key_name
            }
        )

        classified_response[files + "_URL"] = url.replace("//s3", "//s3-us-west-2")
        # classified_response[files + "_URL"] = (download_url + key_name).replace(" ", "+")
        classified_response[files] = cur_name
        
        classified_name = cur_name
        classified_url = (download_url + key_name).replace(" ", "+")
        
    inputs = []
    for values in request.values:
        orig_file = request.values.get(values)
        current = S3InputFiles.query.filter_by(filename = orig_file, deleted = False).first()
        inputs.append(current.file_id)
    
    
    new_row = S3ClassifiedFiles(
        user_id = user_id,
        filename = cur_name,
        url = classified_url,
        input_files = inputs
    )


    try:
        cur_row = S3ClassifiedFiles.query.filter(S3ClassifiedFiles.user_id == user_id, 
                                S3ClassifiedFiles.filename == cur_name).one()
        if (cur_row.deleted == True):
            cur_row.deleted = False
        if (cur_row.input_files != inputs):
            cur_row.input_files = inputs
        db.session.flush()
    except:
        db.session.add(new_row)
    finally:
        db.session.commit()


    classified_response['status'] = 'success'
    classified_response['status_code'] = 200
    classified_response['message'] = 'Everything is okay :)'
    return classified_response

class UploadOriginalAPI(MethodView):

    def post(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }

        status_code = 401

        auth_dict = get_authentication(auth_header)

        if (auth_dict.get('status_code') != 200):
            return make_response(jsonify(auth_dict)), auth_dict.get('status_code')
        
        user_id = auth_dict['user_id']

        uploads_response = uploads(user_id, request.files)
        responseObject['uploads_response'] = uploads_response
        responseObject['status'] = uploads_response['status']
        responseObject['message'] = uploads_response['message']
        status_code = uploads_response['status_code']
        
        response_object = {
            'status': responseObject['status'],
            'data': responseObject
        }
        return make_response(jsonify(response_object)), status_code


class UploadClassifiedAPI(MethodView):

    def post(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }

        status_code = 401

        auth_dict = get_authentication(auth_header)

        if (auth_dict.get('status_code') != 200):
            return make_response(jsonify(auth_dict)), auth_dict.get('status_code')
        
        user_id = auth_dict['user_id']

        classified_response = classified(user_id, request.values, request.files)
        responseObject['classified_response'] = classified_response
        responseObject['status'] = classified_response['status']
        responseObject['message'] = classified_response['message']
        status_code = classified_response['status_code']

        response_object = {
            'status': responseObject['status'],
            'data': responseObject
        }
        return make_response(jsonify(response_object)), status_code




def downloadUploaded(user_id, values):
# Given a classified file, get all files that were used to build this file
# given original file names, download them to user
    bucket_name = os.getenv('S3_UPLOAD')
    file_type = "uploads"
    download_url = "https://s3-us-west-2.amazonaws.com/capstone.upload/"
    
    # Get the service client.
    s3 = boto3.client('s3')

    responseObject = {
        'status': 'fail',
        'status_code': 400,
        'message': 'failed'
    }


    if "classified" in values: #Look for classified in DB and get original files
        #make list of file_names

        files = S3ClassifiedFiles.query.filter(S3ClassifiedFiles.user_id == user_id, 
                                S3ClassifiedFiles.filename == values.get('classified'), 
                                S3ClassifiedFiles.deleted == False).one()

        orig_list = list()
        id_list = files.input_files

        for row in id_list:
            cur_file = S3InputFiles.query.filter(S3InputFiles.user_id == user_id, 
                                                S3InputFiles.file_id == row).one()

            if (cur_file.deleted == False):
                orig_list.append(cur_file.filename)

        for orig_file in orig_list:
            responseObject[orig_file] = orig_file
            key_name = orig_file + '.' + user_id + '.' + file_type

            # Generate the URL to get 'key-name' from 'bucket-name'	    
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': key_name
                }
            )

            # responseObject[orig_file + '_download_url'] = (download_url + key_name).replace(" ", "+")
            # responseObject[orig_file + '_key_name'] = key_name

            responseObject[orig_file + '_download_url'] = url.replace("//s3", "//s3-us-west-2")
            responseObject[orig_file + '_key_name'] = key_name

    else:
        for value in values:
            orig_file = values.get(value)
            cur_file = S3InputFiles.query.filter(S3InputFiles.user_id == user_id, 
                                                S3InputFiles.filename == orig_file, 
                                                S3InputFiles.deleted == False).all()
            if (len(cur_file) == 0):
                responseObject['status'] = 'failure'
                responseObject['status_code'] = '404'
                responseObject['message'] = 'At least one file does not exist'

                return responseObject

            responseObject[value] = orig_file
            key_name = orig_file + '.' + user_id + '.' + file_type

            # Generate the URL to get 'key-name' from 'bucket-name'	    
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': key_name
                }
            )

            # responseObject[orig_file + '_download_url'] = (download_url + key_name).replace(" ", "+")
            # responseObject[orig_file + '_key_name'] = key_name
            responseObject[orig_file + '_download_url'] = url.replace("//s3", "//s3-us-west-2")
            responseObject[orig_file + '_key_name'] = key_name

    responseObject['status'] = 'success'
    responseObject['status_code'] = '200'
    responseObject['message'] = 'Everything is okay :)'

    return responseObject


def downloadClassified(user_id, values):
# Given a classified filename, download them to user
    # Get the service client.
    s3 = boto3.client('s3')
    bucket_name = os.getenv('S3_CLASSIFIED')
    file_type = "classified"
    download_url = "https://s3-us-west-2.amazonaws.com/capstone.classified/"
    responseObject = {
        'status': 'fail',
        'status_code': 400,
        'message': 'failed'
    }
    client = boto3.client('s3')

    for value in values:
        orig_file = values.get(value)
        #FIXME: Not getting the file right. Need to look at DB
        cur_file = S3ClassifiedFiles.query.filter(S3ClassifiedFiles.user_id == user_id, 
                                            S3ClassifiedFiles.filename == orig_file, 
                                            S3ClassifiedFiles.deleted == False).all()
        if (len(cur_file) == -1):
            responseObject['status'] = 'failure'
            responseObject['status_code'] = '404'
            responseObject['message'] = 'At least one file does not exist'

            return responseObject


        responseObject[value] = orig_file
        key_name = orig_file + '.' + user_id + '.' + file_type

        # Generate the URL to get 'key-name' from 'bucket-name'	    
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key_name
            }
        )

        # responseObject[orig_file + '_download_url'] = (download_url + key_name).replace(" ", "+")
        # responseObject[orig_file + '_key_name'] = key_name
        responseObject[orig_file + '_download_url'] = url.replace("//s3", "//s3-us-west-2")
        responseObject[orig_file + '_key_name'] = key_name

        folder_loc = os.getenv('HOLD_FOLDER')

        # Attemps to get file from S3 in memory and send_file. Both methods work for getting file from S3. Send_file just sends empty 
        """
        #with open('./temporary_folder/temporary2.csv', 'wb') as data:
        with open('./temporary_folder/' + orig_file, 'wb') as data:
            client.download_fileobj(  # stores in /../../.
                Bucket=bucket_name, # name of the bucket
                Fileobj=data, # this is the name you want the downloaded file saved as
                Key=key_name # generated key name
            )
        """
    """
    return send_file('../temporary_folder/'+ 'Basic_Stats.csv', 
    #return send_file('../temporary_folder/'+ orig_file, 
        as_attachment=True, 
        attachment_filename=orig_file
    ) 
    """

    responseObject['status'] = 'success'
    responseObject['status_code'] = '200'
    responseObject['message'] = 'Everything is okay :)'

    return responseObject

class DownloadUploadedAPI(MethodView):

    def get(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }

        status_code = 401

        auth_dict = get_authentication(auth_header)
        if (auth_dict.get('status_code') != 200):
            return make_response(jsonify(auth_dict)), auth_dict.get('status_code')

        user_id = auth_dict['user_id']

        downloaded_response = downloadUploaded(user_id, request.values)
        responseObject['uploads_response'] = downloaded_response
        responseObject['status'] = downloaded_response['status']
        responseObject['message'] = downloaded_response['message']
        status_code = downloaded_response['status_code']
        
        response_object = {
            'status': responseObject['status'],
            'data': responseObject
        }
        return make_response(jsonify(response_object)), status_code

        


class DownloadClassifiedAPI(MethodView):

    def get(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }

        status_code = 401

        auth_dict = get_authentication(auth_header)
        if (auth_dict.get('status_code') != 200):
            return make_response(jsonify(auth_dict)), auth_dict.get('status_code')

        user_id = auth_dict['user_id']

        downloaded_response = downloadClassified(user_id, request.values)
        #return downloaded_response # testing purposes
        responseObject['classified_response'] = downloaded_response
        responseObject['status'] = downloaded_response['status']
        responseObject['message'] = downloaded_response['message']
        status_code = downloaded_response['status_code']
        
        response_object = {
            'status': responseObject['status'],
            'data': responseObject
        }

        return make_response(jsonify(response_object)), status_code


class DeleteOriginalAPI(MethodView):
    
    def get(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }

        status_code = 401

        auth_dict = get_authentication(auth_header)
        if (auth_dict.get('status_code') != 200):
            return make_response(jsonify(auth_dict)), auth_dict.get('status_code')

        user_id = auth_dict['user_id']
       
        if (len(request.values) == 0):
            return make_response(jsonify(responseObject)), status_code
        
        for value in request.values:
            fileName = request.values.get(value)
            responseObject[fileName] = "deleted"
        


        deleted_files = []
        for value in request.values:
            fileName = request.values.get(value)

            files = S3InputFiles.query.filter(S3InputFiles.user_id == user_id, 
            S3InputFiles.filename == fileName, 
            S3InputFiles.deleted == False).one()
        
            files.deleted = True
            #files.url = "deleted" + files.url + str(files.file_id)
            responseObject[fileName] = "deleted"

            deleted_files.append(fileName)
            db.session.commit()
            file_type = "uploads"
            bucket_name = os.getenv('S3_UPLOAD')

            key_name = fileName + '.' + user_id + '.' + file_type 
            
            client = boto3.client('s3')
            client.delete_object(
                Bucket=bucket_name, # name of the bucket
                Key=key_name
            )


        responseObject['message'] = "Everything is okay :)"
        responseObject['status'] = "success"
        responseObject['deleted_files'] = deleted_files

        response_object = {
            'status': 200,
            'data': responseObject
        }
               
       
        return make_response(jsonify(response_object)), status_code


class DeleteClassifiedAPI(MethodView):
    
    def get(self):
        auth_header = request.headers.get('Authorization')

        responseObject = {
            'status': 'fail',
            'message': ''
        }

        status_code = 401

        auth_dict = get_authentication(auth_header)
        if (auth_dict.get('status_code') != 200):
            return make_response(jsonify(auth_dict)), auth_dict.get('status_code')

        user_id = auth_dict['user_id']
       
        if (len(request.values) == 0):
            return make_response(jsonify(responseObject)), status_code
        
        for value in request.values:
            fileName = request.values.get(value)
            responseObject[fileName] = "deleted"
        

        deleted_files = []
        for value in request.values:
            fileName = request.values.get(value)

            files = S3ClassifiedFiles.query.filter(S3ClassifiedFiles.user_id == user_id, 
            S3ClassifiedFiles.filename == fileName, 
            S3ClassifiedFiles.deleted == False).one()
        
            files.deleted = True
            #files.url = "deleted" + files.url + str(files.file_id)
            responseObject[fileName] = "deleted"

            deleted_files.append(fileName)
            db.session.commit()
            file_type = "classified"
            bucket_name = os.getenv('S3_CLASSIFIED')

            key_name = fileName + '.' + user_id + '.' + file_type 
            
            client = boto3.client('s3')
            client.delete_object(
                Bucket=bucket_name, # name of the bucket
                Key=key_name
            )


        responseObject['message'] = "Everything is okay :)"
        responseObject['status'] = "success"
        responseObject['deleted_files'] = deleted_files

        response_object = {
            'status': 200,
            'data': responseObject
        }
               
       
        return make_response(jsonify(response_object)), status_code

        
class UploadedListAPI(MethodView):
    """
    Returns list of files the user has uploaded
    """

    def get(self):
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
            if not isinstance(resp, str):
                files = S3InputFiles.query.filter_by(user_id=resp).all()
                file_names = list()
                file_links = list()
                for row in files:
                    if row.deleted == False:
                        file_names.append(row.filename)
                        file_links.append(row.url)
                file_json = [{"file_names": n, "file_links": l} for n, l in zip(file_names, file_links)]
                responseObject = {
                    'status': 'success',
                    'message': 'Listing ' + str(len(file_json)) + ' files.',
                    'data': file_json
                }
                return make_response(jsonify(responseObject)), 200
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

class ClassifiedListAPI(MethodView):
    """
    Returns list of classified files for the user
    """

    def get(self):
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
            if not isinstance(resp, str):
                files = S3ClassifiedFiles.query.filter_by(user_id=resp).all()
                classified_names = list()
                classified_links = list()
                for row in files:
                    if row.deleted == False:
                        classified_names.append(row.filename)
                        classified_links.append(row.url)
                file_json = [{"classified_names": n, "classified_links": l} for n, l in zip(classified_names, classified_links)]
                responseObject = {
                    'status': 'success',
                    'message': 'Listing ' + str(len(file_json)) + ' classified files.',
                    'data': file_json
                }
                return make_response(jsonify(responseObject)), 200
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

upload_original_view = UploadOriginalAPI.as_view('upload_original_api')
upload_classified_view = UploadClassifiedAPI.as_view('upload_classified_api')
download_uploaded_view = DownloadUploadedAPI.as_view('download_uploaded_api')
download_classified_view = DownloadClassifiedAPI.as_view('download_classified_api')
upload_list_view = UploadedListAPI.as_view('upload_list_api')
classified_list_view = ClassifiedListAPI.as_view('classified_list_api')
delete_original_view = DeleteOriginalAPI.as_view('delete_original_view')
delete_classified_view = DeleteClassifiedAPI.as_view('delete_classified_view')

s3_blueprint.add_url_rule(
    '/s3/uploadClassified',
    view_func=upload_classified_view,
    methods=['POST']
)
s3_blueprint.add_url_rule(
    '/s3/uploadOriginal',
    view_func=upload_original_view,
    methods=['POST']
)
s3_blueprint.add_url_rule(
    '/s3/downloadUploaded',
    view_func=download_uploaded_view,
    methods=['GET']
)
s3_blueprint.add_url_rule(
    '/s3/downloadClassified',
    view_func=download_classified_view,
    methods=['GET']
)
s3_blueprint.add_url_rule(
    '/s3/file_list',
    view_func=upload_list_view,
    methods=['GET']
)
s3_blueprint.add_url_rule(
    '/s3/classified_list',
    view_func=classified_list_view,
    methods=['GET']
)
s3_blueprint.add_url_rule(
    '/s3/deleteFileOriginal',
    view_func=delete_original_view,
    methods=['GET']
)
s3_blueprint.add_url_rule(
    '/s3/deleteFileClassified',
    view_func=delete_classified_view,
    methods=['GET']
)
