# Db stuff
from project import db
from project.api.models import decode_auth_token, MLStatus

# Machine learning
import sys
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
    current_classification = classifier(jsonInput, auth_token, app)
    data = current_classification.get_data()
    vectorizer = current_classification.get_vectorizer(data)
    trainer = current_classification.train_classifier(vectorizer, data)
    df = current_classification.create_user_dataframe(jsonInput)
    results = current_classification.calculate_results(trainer)
    (predicted_sport, confidence) = current_classification.get_predicted_sport(results)
    cwd = current_classification.get_current_working_directory(auth_token, app)
    file = current_classification.get_uploaded_file(cwd)
    json_frame = current_classification.append_classified_field(predicted_sport, confidence, file)
    filepath = current_classification.save_classified_file(cwd, json_frame, auth_token, app)
    current_classification.update_endpoints(filepath, auth_token, app, json_frame)




# Moved function logic to a class so the current_classification
# object can be testable
# Welc: Break out method object
class classifier:
    # Python contrusctor
    def __init__(self, jsonInput, auth_token, app):
        self.jsonInput = jsonInput
        self.auth_token = auth_token
        self.app = app

    def get_data(self):
        # Load data.json
        with open('project/data2.json') as f:
            data = json.load(f)

            # Convert json objects into python matrix
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
            return data

    def get_vectorizer(self, data):
        return HashingVectorizer(n_features=2**4)


    def train_classifier(self, vectorizer, data):
        # Hashing Vectorizer
        vec_data = vectorizer.fit_transform(data.col)
        self.vec_data = vec_data

        # Set the desired output into a separate dataframe
        target = data.sport

        # Split data set into train and test sets
        data_train, data_test, target_train, target_test = \
                                                train_test_split(\
                                                vec_data, target,\
                                                test_size = 0.30,\
                                                random_state = 3)

        # Create an object of the type LinearSVC
        svc_model = LinearSVC(random_state=0)

        # Train the algorithm on training data
        # Returns trainer
        return svc_model.fit(data_train, target_train)



    def create_user_dataframe(self, jsonInput):
        # Place the json_input into a dataframe df
        # Create the shape and data for the df
        X = []
        Y = []
        json_in = json.loads(jsonInput)
        for key in json_in:
            X.append(key)
            for value in json_in[key]:
                Y.append(value)

        self.X = X
        # Create the dataframe df and places Y-values
        return pd.DataFrame(Y, columns=['col'])



    def calculate_results(self, trainer):
        # Store the results
        return trainer.predict(self.vec_data)



    def get_predicted_sport(self, results):
        # Sum all the predictions
        counts = {}
        for res in results:
            if res in counts:
                counts[res] += 1
            else:
                counts[res] = 0

        # Get the sum, max, and confidence get_values
        # for the predicted results
        summation = sum(counts.values())
        maximum = max(counts.values())
        if maximum == 0:
            confidence = 0
        else:
            confidence = maximum / summation * 100

        # Get the predicted sport
        predicted_sport = max(counts, key=counts.get)

        # Get the max prediction occurance
        return (predicted_sport, confidence)


    def get_current_working_directory(self, auth_token, app):
        # get the current working directory
        return get_cwd(auth_token, app)


    def get_uploaded_file(self, cwd):
        # Get the file location
        return cwd + '/' + self.X[0]


    def append_classified_field(self, predicted_sport, confidence, df_file):
        # Load the csv file into a pandas dataframe
        df = pd.read_csv(df_file).dropna()

        # append a sport column with the predicted sport
        df['predicted_sport'] = predicted_sport

        # append the confidence level with the predicted
        df['prediction_confidence%'] = confidence

        # Formatting for player cards
        rows = df.shape[0]
        columns = df.columns
        spec_cols = []
        players = []

        # Get all special int64 column names
        for col in columns:
            if df[col].dtype == 'int64':
                spec_cols.append(col)

        # Make a dictionary which contains all players
        # For each player
        for i in range(rows):
            player = {}
            # For each field
            for col in columns:
                # Typecast int64 to int
                if col in spec_cols:
                    player[col] = int(df.iloc[i][col])
                else:
                    player[col] = df.iloc[i][col]
            players.append(player)

        # save the dataframe into a json object
        return json.dumps(players)


    def save_classified_file(self, cwd, json_frame, auth_token, app):
        # Save the classified file to the cwd
        selected_files = get_values(auth_token, app)

        # Build name from selected_files
        filepath = cwd + '/' + 'classified'
        for file_name in selected_files:
            filepath = filepath + '_' + file_name
        filepath = filepath + '.json'

        with open(filepath, 'w+') as json_file:
            json.dump(json_frame, json_file)
        return filepath


    def update_endpoints(self, filepath, auth_token, app, json_frame):
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
    g_headers = {'Authorization': 'Bearer ' + auth_token}
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
