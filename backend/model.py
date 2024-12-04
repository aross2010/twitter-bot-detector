import pandas as pd 
import shap 
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Code from Jupyter Notebook - quick creation of the model

df = pd.read_csv('dataset.csv')
df.fillna(0, inplace=True)
df.drop(columns=['user_id', 'screen_name', 'parsed_owned_tweets_count', 'parsed_owned_text_tweets_count', 'parsed_retweets_count', 'is_verified'], inplace=True)
Y = df.is_bot
df.drop('is_bot', inplace=True, axis=1)
X = df
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=82)
model = RandomForestClassifier(n_estimators = 100, criterion = 'entropy', random_state = 0)
model.fit(X_train.values, Y_train.values)
y_pred = model.predict(X_test.values)
print('Model 1 Classification Report: \n', classification_report(Y_test, y_pred))
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
joblib.dump(model, 'model.joblib')
loaded_model = joblib.load('model.joblib')
user = X_test.iloc[0]
prediction = loaded_model.predict([user])
probabilities = loaded_model.predict_proba([user])
print(f"Prediction: {prediction}")
print(f"Probabilities: {probabilities}")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(user)
feature_names = X_test.columns.tolist() 
feature_contributions = list(zip(feature_names, shap_values[:, 1]))
print(feature_contributions)
feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)
print("Feature Contributions for Class 1 (Bot):")
for feature, contribution in feature_contributions:
    print(f"{feature}: {contribution}")
