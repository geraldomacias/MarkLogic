import os
import io
import random
import json
import requests
from io import StringIO
from project.api.models import decode_auth_token, MLStatus
from project.linearSVC import matchSport
from project import db

#pass user ID (Auth token) and FileNames => output list of lists? dictionary?
#need duplicates to help confidence to matching to a sport
def extract_columns(app, auth_token, file_names) :
    files_with_names = {}
    cur_path = os.getcwd()
    #generate random number for temp csv storage folder
    rand_file_num = random.randint(1000, 9999)
    create_folder = str(rand_file_num)+ "_temp_files/"
    #print("Create Folder: " + create_folder + "\n")
    abs_path = "/temp/" + create_folder
    #create directory
    try:
        os.makedirs(abs_path)
    except OSError:
        print ("Creation of the directory %s failed\n" % create_folder)
        set_status_error(app, auth_token, "Creation of temporary local directory has failed")
    else:
        #print ("Successfully created the directory, adding it to the db %s\n" % create_folder)
        insert_cwd(app, auth_token, abs_path)

    #download files from s3. Make a get request from s3 endpoint
    g_url = "http://file_system:5000/s3/downloadUploaded"
    g_headers = {"Authorization" : 'Bearer ' + auth_token}
    #get only the data for first file in file name list
    if not file_names:
        set_status_error(app, auth_token, "List of files to operate on is empty")
    else:
        #iterate through all files in given file list and parse column names for each
        for file in file_names:
            cur_file_column_names = []
            g_param = {file : file}
            cur_dl_response = requests.get(url = g_url, headers = g_headers, params = g_param)
            cur_dl_data = cur_dl_response.json()
            cur_upload_response = cur_dl_data['data']['uploads_response']
            cur_dl_key = file + "_download_url"
            cur_r = requests.get(url = cur_upload_response[cur_dl_key])
            cur_file_data = cur_r.text
            #parse file data and gather column names while file is open, if valid
            if cur_file_data == None:
                set_status_error(app, auth_token, "No valid file data found in response")
            else:
                cur_file_column_names = []
                cur_buf = StringIO(cur_file_data)
                cur_first_line = cur_buf.readline()
                cur_splitted = cur_first_line.split(',')
                for word in cur_splitted:
                    cur_processed = (word.strip()).lower()
                    cur_file_column_names.append(cur_processed)
                files_with_names[file] = cur_file_column_names
                write_file_loc = abs_path + file
                with open(write_file_loc, 'w') as wFile:
                    wFile.write()
    matchSport(json.dumps(file_with_names), auth_token, app)
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