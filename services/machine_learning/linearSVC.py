from sklearn import preprocessing
import pandas as pd
import json


# Import json file
with open('data.json') as f:
    data = json.load(f)


# Load json file into pandas dataframe
df = pd.read_json('data.json')
df = df.fillna('')


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


# Create the Labelencoder object
le = preprocessing.LabelEncoder()


# Convert the categorical columns into numeric
encode_value = le.fit_transform(data.columns)
encode_value


# Convert the categorical columns into numeric
for column in data.columns:
    data[column] = le.fit_transform(data[column])


# Set the desired output into a separate dataframe
target = data.sport


# Remove the predictive output from the originial dataset
data = data.col


# Reshape data
data = data.reshape(-1, 1)


# Train test and split
from sklearn.model_selection import train_test_split


# Split data set into train and test sets
data_train, data_test, target_train, target_test = train_test_split(data, target, test_size = 0.30, random_state = 10)


# ## Naive Bayes

from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score


# Create an object of the type GaussianNB
gnb = GaussianNB()


# Train the algorithm on training data and predict using the testing data
pred = gnb.fit(data_train, target_train).predict(data_test)


# Print accuracy
print("Naive-Bayes accuracy: ", accuracy_score(target_test, pred, normalize=True))


# ## LinearSVC
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score


# Create an object of the type LinearSVC
svc_model = LinearSVC(random_state=0)


# Train the algorithm on training data and predict using the testing data
pred = svc_model.fit(data_train, target_train).predict(data_test)

# Print accuracy
print("LinearSVC accuracy: ", accuracy_score(target_test, pred, normalize=True))


# ## K-Neighbors Classifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


# Create object of the classifier
neigh = KNeighborsClassifier(n_neighbors=3)


#Train the algorithm
neigh.fit(data_train, target_train)


# Predict the response
pred = neigh.predict(data_test)

# Print accuracy
print('KNeighbors accuracy score: ', accuracy_score(target_test, pred))
