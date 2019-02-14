import os
import requests

file_name_list = ["stub1", "stub2", "stub3" ]#get from s3
#pass user ID (Auth token) and FileNames => output list of lists? dictionary?
#need duplicates to help confidence to matching to a sport
def extract_columns(file_name_list, auth_token) :
    column_names = {}

    cur_path = os.getcwd()
    print("The current working directory is %s" % cur_path)

    create_folder = "temp_files"

    try:
        os.mkdir(create_folder)
    except OSError:
        print ("Creation of the directory %s failed" % create_folder)
    else:
        print ("Successfully created the directory %s " % create_folder)

    #download files from s3. Make a get request from s3 endpoint
    r = requests.get()

    for root, dirs, files in os.walk("./temp_files"):  
        for file_name in files:
            with open(file_name) as f:
            first_line = f.readline()
            splitted = first_line.split(',')
            for word in splitted:
                trimmed = word.strip()
                lowercase = trimmed.lower()
                if not lowercase in column_names:
                    column_names[lowercase] = lowercase

#remove temp files after all the files are parsed

    return column_names

