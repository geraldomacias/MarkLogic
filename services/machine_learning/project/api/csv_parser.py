import os
import io
import random
from project.api.models import decode_auth_token

file_name_list = ["stub1", "stub2", "stub3" ]#get from s3
#pass user ID (Auth token) and FileNames => output list of lists? dictionary?
#need duplicates to help confidence to matching to a sport
def extract_columns(auth_token, file_names) :
    files_with_names = {}


    cur_path = os.getcwd()
    print("The current working directory is %s\n" % cur_path)

    rand_file_num = random.ranint(1000, 9999)
    create_folder = str(rand_file_num)+ "_temp_files"
    print("Create Folder: " + create_folder + "\n")
    #create directory
    try:
        os.mkdir(create_folder)
    except OSError:
        print ("Creation of the directory %s failed\n" % create_folder)
    else:
        print ("Successfully created the directory %s\n" % create_folder)

    #download files from s3. Make a get request from s3 endpoint
    g_url = "http://file_system:5000/s3/download"
    g_headers = {"Authorization" : 'Bearer ' + auth_token.decode()}
    for f in file_names:
        g_param = {"address" : f}
        r = requests.get(url = g_url, headers = g_headers, params = g_param)
        #parse data and gather column names while file is open, if valid
        file_data = r.text
        if file_data = None:
            print("No valid file data found\n")
        else:
            print("File data retrieved writing to directory\n")
            col_names = []
            buf = StringIO.StringIO(file_data)
            first_line = buf.readline()
            splitted = first_line.split(',')
            for word in splitted:
                processed = (word.strip()).lower()
                col_names.append(processed)
            files_with_names[f] = col_names

            with open(f,mode='wb') as wFile
                wFile.write(file_data.content)
#remove temp files after all the files are parsed
#call G's ML stuff

