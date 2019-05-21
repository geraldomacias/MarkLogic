# Db stuff
from project import db
from project.api.models import decode_auth_token, MLStatus

# Machine learning
import json
import pandas as pd
import requests
from sklearn import preprocessing
from collections import defaultdict
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import HashingVectorizer

"""
    jsonInput format
    { <file_name1> :  [col_name1, col_name2, ....], }
"""
def matchSport(jsonInput, auth_token, app):

    # Load data.json
    with open('project/data2.json') as f:
        data = json.load(f)

    X = []
    Y = []
    for element in data:
        for key in element.keys():
            X.append(key)
        for value in element.values():
            Y.append(value)

    # Reshape the dataframe to be ['sport', 'col_name']
    data = pd.DataFrame(X, columns=['sport'])
    data['col'] = Y
    data['cop'] = data.sport


    # Hashing Vectorizer
    vectorizer = HashingVectorizer(n_features=(2 ** 5))
    vec_data = vectorizer.fit_transform(data.col)

    # Set the desired output into a separate dataframe
    target = data.sport

    # Split data set into train and test sets
    data_train, data_test, target_train, target_test = \
                                            train_test_split(\
                                            vec_data, target,\
                                            test_size = 0.30,\
                                            random_state = 10)


    # Create an object of the type LinearSVC
    svc_model = LinearSVC(random_state=0)

    # Train the algorithm on training data
    trainer = svc_model.fit(data_train, target_train)


    # Place the json_input into a dataframe df
    # Create the shape and data for the df
    X = []
    Y = []
    json_in = json.loads(jsonInput)
    for key in json_in:
        X.append(key)
        for value in json_in[key]:
            Y.append(value)

    # Create the dataframe df and places Y-values
    df = pd.DataFrame(Y, columns=['col'])

    # Vectorize the users column names
    vec_data = vectorizer.fit_transform(df.columns)

    # Store the results
    results = trainer.predict(vec_data)


    # Sum all the predictions
    counts = {}
    for res in results:
        if res in counts:
            counts[res] += 1
        else:
            counts[res] = 0

    # Get the max prediction occurance
    predicted_sport = max(counts, key=counts.get)

    # get the current working directory
    cwd = get_cwd(auth_token, app)

    # Get the file location
    df_file = cwd + '/' + X[0]
    #df_file = cwd + X[0]

    # Load the csv file into a pandas dataframe
    df = pd.read_csv(df_file).dropna()

    # append a sport column with the predicted sport
    df['sport'] = predicted_sport

    # Formatting for player cards
    rows = df.shape[0]
    columns = df.columns
    spec_cols = []
    players = []

    # Get all special int64 columns
    for col in columns:
        if df[col].dtype == 'int64':
            spec_cols.append(col)

    # Make a dictiionary which contains all players
    # For each player
    for i in range(rows):
        player = {}
        # For each field
        for col in columns:
            # Typecast int64 to int
            if col in spec_cols:
                player[col] = int(df.loc[i][col])
            else:
                player[col] = df.loc[i][col]
        players.append(player)

    # save the dataframe into a json object
    json_frame = json.dumps(players)

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
        if isinstance(resp, str):
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
