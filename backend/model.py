import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle

data = pd.read_csv("../dataset/health_data.csv")

X = data[['Age','BP','Sugar','Cholesterol']]
y = data['Risk']

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)

model = LogisticRegression()

model.fit(X_train,y_train)

pickle.dump(model, open("model.pkl","wb"))

print("Model trained successfully")