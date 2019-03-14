# Db stuff
from project import db
from project.api.models import decode_auth_token, MLStatus

# Machine learning
import json
import pandas as pd
import requests
from sklearn import preprocessing
from collections import defaultdict
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# jsonInput format
# { <file_name1> :  [col_name1, col_name2, ....],
def matchSport(jsonInput, auth_token, app):

    """
    f = open('lookforme!!!!!!',"w+")
    for i in range(10):
        f.write("This is line %d\r\n" % (i+1))
    f.close()
    """

    # Load data.json
    with open('project/data.json') as f:
        data = json.load(f)

    X = []
    Y = []
    for element in data:
        for key in element.keys():
            X.append(key)
        for value in element.values():
            Y.append(value)

    # Reshap the dataframe to be ['sport', 'col_name']
    data = pd.DataFrame(X, columns=['sport'])
    data['col'] = Y
    data['cop'] = data.sport

    # Place the json_input into a dataframe df
    X = []
    Y = []
    json_in = json.loads(jsonInput)
    for key in json_in:
        X.append(key)
        for value in json_in[key]:
            Y.append(value)


    df = pd.DataFrame(Y, columns=['col'])

    # Create the Labelencoder object
    le = preprocessing.LabelEncoder()


    # Convert the categorical columns into numeric
    encode_value = le.fit_transform(data.columns)
    # encode_value

    # Convert the categorical columns into numeric
    for column in ['sport', 'col']:
        data[column] = le.fit_transform(data[column])


    # Create a hashmap of transformed data
    # {encode_val : "sport"}
    sport_id = {}
    for name, group in data.groupby(['sport', 'cop']):
        sport_id[name[0]] = name[1]


    # Set the desired output into a separate dataframe
    target = data.sport


    # Remove the predictive output from the originial dataset
    data = data.col

    # Reshape data
    data = data.values.reshape(-1, 1)


    # Train test and split
    from sklearn.model_selection import train_test_split


    # Split data set into train and test sets
    data_train, data_test, target_train, target_test = train_test_split(data, target, test_size = 0.30, random_state = 10)


    # Create object of the classifier
    neigh = KNeighborsClassifier(n_neighbors=3)

    #Train the algorithm
    neigh.fit(data_train, target_train)


    # Predict the response
    pred = neigh.predict(data_test)

    #cols = pd.read_csv('../../../Downloads/MOCK_DATA_ALT_COLUMN_NAMES.csv').columns
    cols = df.columns

    # Convert the categorical columns into numeric
    encode_value = le.fit_transform(cols)


    # Reshape data
    encode_value = encode_value.reshape(-1, 1)

    # Load K-Nearest Neighbors
    neigh = KNeighborsClassifier(n_neighbors=4)

    # Use k_nearest neighbors to predict sport
    pred = neigh.fit(data_train, target_train).predict(encode_value)

    # Reverse map the integer -> sport to reveal prediction
    predicted_sport = sport_id[max(pred)]

    # get the current working directory
    cwd = get_cwd(auth_token, app)

    # Get the file location
    df_file = cwd + '/' + X[0]
    #df_file = cwd + X[0]

    # Load the csv file into a pandas dataframe
    df = pd.read_csv(df_file)

    # append a sport column with the predicted sport
    df['sport'] = predicted_sport

    # save the dataframe into a json object
    json_frame = df.to_json()

    # Save the classified file to the cwd
    filepath = cwd + '/' + 'classified.json'
    with open(filepath, 'w+') as json_file:
        json.dump(json_frame, json_file)

    # Open the saved file
    files = {'classifed': open(filepath, 'rb')}

    # Get selected files from db
    selected_files = get_values(auth_token, app)

    # Can loop to produce multiple files
    values = {'file1': selected_files[0]}

    # Hit s3/uploadClassified
    jake_point(files, values, auth_token)

    # update the status with the json_frame
    update_status(auth_token, app, json_frame)




def jake_point(files, values, auth_token):
    g_headers = {"Authorization": 'Bearer ' + auth_token}
    url = 'http://file_system:5000/s3/uploadClassified'
    r = requests.post(url, files=files, data=values, headers=g_headers)


# Retrieves selected files from the db
def get_values(auth_token, app):
    with app.app_context():
        resp = decode_auth_token(auth_token)
        if isinstance(resp):
            # Auth token invalid
            print(resp, flush=True)
        # Is a user_id
        row = MLStatus.query.filter_by(user_id=resp).first()
        if not row:
            # Cannot find use in the status DB. No bueno
            print('Cannot find user in the status DB')
        # Return the selected files from the user
        return row.selected_files;


# Retrieves current working directory from the db
def get_cwd(auth_token, app):
    with app.app_context():
        resp = decode_auth_token(auth_token)
        if isinstance(resp, str):
            # Auth token invalid
            print(resp)
        # Is a user_id
        row = MLStatus.query.filter_by(user_id=resp).first()
        if not row:
            # Cannot find use in the status DB. No bueno
            print('Cannot find user in the status DB')
        # Return the location of the original file
        return row.working_directory;


# Updates the users status to Complete.
def update_status(auth_token, app, j_frame):
    with app.app_context():
        resp = decode_auth_token(auth_token)
        if isinstance(resp, str):
            # Auth token invalid
            print(resp)
        # Is a user_id
        row = MLStatus.query.filter_by(user_id=resp).first()
        if not row:
            # Cannot find use in the status DB. No bueno
            print('Cannot find user in the status DB')

        # update the user status
        row.status = 'Completed.'
        # Update the status field
        row.classified_json = j_frame
        # send to db
        db.session.commit()
