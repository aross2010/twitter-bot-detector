import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib


# file is for creating and loading the model, more detailed version in notebook

df = pd.read_csv('dataset.csv')

# replace null values with 0
df.fillna(0, inplace=True)

# drop columns that are not needed
df.drop(columns=['user_id', 'screen_name'], inplace=True)

# isolate target variable is_bot
Y = df.is_bot
df.drop('is_bot', axis=1, inplace=True)
X = df

# split data into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=0)

# train the model
model = RandomForestClassifier(n_estimators=200, random_state=0, criterion='entropy')
model.fit(X_train, Y_train)

# save the model
joblib.dump(model, 'bot_model.joblib')

# load the model
loaded_model = joblib.load('bot_model.joblib')

# get the first row of the dataset
user = X.iloc[0]

# make a prediction
prediction = loaded_model.predict([user])
probabilities = loaded_model.predict_proba([user])

print(f"Prediction: {prediction}")
print(f"Probabilities: {probabilities}")