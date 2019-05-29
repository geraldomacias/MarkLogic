import os
import io
import random
import json
import requests
from io import StringIO
from project.api.models import decode_auth_token, MLStatus
from project.linearSVC import matchSport
from project import db
from flask import current_app

def get_fake_response_link(*args, key, g_headers, file):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    if (args[0] == 'http://file_system:5000/s3/downloadUploaded') and (g_headers['Authorization'] == "Bearer 123456789") and (g_params == {file : file}):
        return MockResponse({"key1": "http://fakeurl"}, 200)
    else:
        return MockResponse(None, 404)

def get_fake_response_file(*args, key):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.test = "first name, last name, jersey number, position, hometown, tackles, touchdowns, rushing yards, passing yards"

        def json(self):
            return self.json_data
    if (args[0] == 'http://someurl.com/downloadFile') and (key == "test_file_download_url"):
        return MockResponse({"key1": "value1"}, 200)
    else:
        return MockResponse(None, 404)

def get_dl_link(g_url, g_headers, g_param, app, auth_token):
    if app.config.get('TESTING'):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data
    else:
        link = requests.get(url = g_url, headers = g_headers, params = g_param)
        if link:
            link_data = link.json()
            link_response = link_data['data']['uploads_response']
            return link_response
        else:
            set_status_error(app, auth_token, "No valid file url found in response")

def get_dl_file(url_data, cur_dl_key, app, auth_token):
    if app.config.get('TESTING'):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data
    else:
        file =  requests.get(url = url_data[cur_dl_key])
        if file:
            return file.text
        else:
            set_status_error(app, auth_token, "No valid file data found in response")

def process_and_write_file(cur_file_data, file, abs_path, files_with_names, app, auth_token):
    cur_file_column_names = []
    cur_buf = StringIO(cur_file_data)
    cur_first_line = cur_buf.readline()
    cur_splitted = cur_first_line.split(',')
    if len(cur_splitted) == 0:
        set_status_error(app, auth_token, "Given CSV is empty")
    for word in cur_splitted:
        cur_processed = (word.strip()).lower()
        cur_file_column_names.append(cur_processed)
    files_with_names[file] = cur_file_column_names
    write_file_loc = abs_path + file
    with open(write_file_loc, 'w') as wFile:
        wFile.write(cur_file_data)

def extract_file(file, g_url, g_headers, app, auth_token, abs_path, files_with_names):
    cur_file_column_names = []
    g_param = {file : file}
    url_data = get_dl_link(g_url, g_headers, g_param, app, auth_token)
    cur_dl_key = file + "_download_url"
    cur_r = get_dl_file(url_data, cur_dl_key, app, auth_token)
    #parse file data and gather column names while file is open, if valid
    if cur_r == None:
        set_status_error(app, auth_token, "No valid file data found in response")
    else:
        process_and_write_file(cur_r, file, abs_path, files_with_names, app, auth_token)

def create_temp_directory(abs_path, create_folder, app, auth_token):
    #create directory
    try:
        os.makedirs(abs_path)
    except OSError:
        print ("Creation of the directory %s failed\n" % create_folder)
        set_status_error(app, auth_token, "Creation of temporary local directory has failed")
    else:
        #print ("Successfully created the directory, adding it to the db %s\n" % create_folder)
        insert_cwd(app, auth_token, abs_path)


#pass user ID (Auth token) and FileNames => output list of lists? dictionary?
#need duplicates to help confidence to matching to a sport
def extract_columns(app, auth_token, file_names):
    files_with_names = {}
    cur_path = os.getcwd()
    #generate random number for temp csv storage folder
    rand_file_num = random.randint(1000, 9999)
    create_folder = str(rand_file_num)+ "_temp_files/"
    #print("Create Folder: " + create_folder + "\n")
    abs_path = "/temp/" + create_folder
    create_temp_directory(abs_path, create_folder, app, auth_token)
    #get only the data for first file in file name list
    if not file_names:
        set_status_error(app, auth_token, "List of files to operate on is empty")
    else:
        #download files from s3. Make a get request from s3 endpoint
        g_url = "http://file_system:5000/s3/downloadUploaded"
        g_headers = {"Authorization" : 'Bearer ' + auth_token}
        #iterate through all files in given file list and parse column names for each
        for file in file_names: 
            files_with_names[file] = extract_file(file, g_url, g_headers, app, auth_token, abs_path, files_with_names)
    matchSport(json.dumps(files_with_names), auth_token, app)
    #remove temp files after all the files are parsed

def insert_cwd(app, auth_token, cwd):
    with app.app_context():
        resp = decode_auth_token(auth_token)
        if isinstance(resp, str):
            # auth_token isn't valid anymore - that's not good
            print(resp)
        # If its not a string, its a user_id
        status = MLStatus.query.filter_by(user_id=resp).first()
        if not status:
            # Can't find user in status DB - that's not good
            print("Cannot find user in status DB")
        status.working_directory = cwd

        db.session.commit()

def fake_aws_get():
    the_response = Response()
    the_response.code = "expired"
    the_response.error_type = "expired"
    the_response.status_code = 400
    the_response._content = b'{ "key" : "a" }'

def set_status_error(app, auth_token, error):
    with app.app_context():
        resp = decode_auth_token(auth_token)
        if isinstance(resp, str):
            # auth_token isn't valid anymore - that's not good
            print(resp)
        status = MLStatus.query.filter_by(user_id=resp).first()
        if not status:
            # Can't find user in status DB - that's not good
            print("Cannot find user in status DB")
        status.status = "Failed to process files."
        status.error_msg = error 

        db.session.commit()
        return