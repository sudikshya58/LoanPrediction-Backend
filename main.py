from flask import Flask,request,jsonify, redirect
from models import db,User,Register
from datetime import datetime, timedelta, timezone
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, decode_token, revoke_token


app=Flask(__name__)


CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type", "Authorization"])

app.config['JWT_SECRET_KEY'] = '123456'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/loanprediction"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

SQLALCHEMY_TRACK_NOTIFICATIONS=False
SQLALCHEMY_ECHO=True
bcrypt = Bcrypt(app)
db.init_app(app)
with app.app_context():
    db.create_all() 

@app.route('/logintoken', methods=["POST"])
def create_token():
    useremail = request.json.get("useremail", None)
    userpassword = request.json.get("userpassword", None)

    user = Register.query.filter_by(useremail=useremail).first()
    if user is None:
        return jsonify({"error": "Wrong email or passwords"}), 401
     
    if not bcrypt.check_password_hash(user.userpassword, userpassword):
        return jsonify({"error": "Wrong email or password"}), 401

    access_token = create_access_token(identity=useremail)
    return jsonify({"useremail": useremail, "access_token": access_token,"message": "Logged in successfully"})


@app.route('/')
def hello():
    return "hello everyone"
@app.route("/login",methods=["POST"])
def login():
    email=request.json['email']
    password=request.json['password']
    return jsonify({
    "id": "1",
        "email": email,
        "password": password 
    })
@app.route("/signin", methods=["POST"])
@cross_origin()
def signin():
    if request.method == "POST":
        data = request.get_json()  # Retrieve JSON data from the request

        # Get email and password from the JSON data
        email = data.get('email')
        password = data.get('password')

        # Create a new user instance
        new_user = User(email=email, password=password)

        # Add user to the database session
        db.session.add(new_user)

        # Commit changes to the database
        db.session.commit()

        return jsonify({"message": "User logged in successfully"})
        
@app.route("/registers", methods=["POST"])
def register():
    if request.method == "POST":
        data = request.get_json()
        username = data.get('username')
        useremail = data.get('useremail')
        userphone = data.get('userphone')
        userpassword = data.get('userpassword')
        confirmpassword = data.get('confirmpassword')

        # Check if the passwords match
        # if userpassword != confirmpassword:
        #     return jsonify({"error": "Passwords do not match"}), 400

        user_exists = Register.query.filter_by(useremail=useremail).first() is not None
        if user_exists:
            return jsonify({"error": "Email already exists"}), 409

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(userpassword).decode('utf-8')

        new_Register = Register(username=username, useremail=useremail, userpassword=hashed_password, userphone=userphone, confirmpassword=confirmpassword)
        
        # Add user to the database session
        db.session.add(new_Register)
        
        # Commit changes to the database
        db.session.commit()

        return jsonify({
             
            "message": "User registered successfully"}), 201


@app.route('/api/send-data', methods=['POST', 'OPTIONS'])
@cross_origin()
def send_data():

  data = request.json['data']
  # if __name__ == '__main__':
    # app.run(port=5000)
  import pickle
#Importing the necessary modules
  import numpy as np
  import pandas as pd
  from Algorithm.LogisticRegression import Logistic_Regression



  #Reading the test and train dataset
  train_data = pd.read_csv(r'A:\Flask\datasets\testdata.csv')
  test_data = pd.read_csv(r'A:\Flask\datasets\traindata.csv')

  #Splitting the data into features and outputs
  xtrain, ytrain = train_data.drop(columns = 'Loan_Status', axis = 1), train_data['Loan_Status']
  xtest, ytest = test_data.drop(columns = 'Loan_Status', axis =1), test_data['Loan_Status']

  #Converting the csv files into numpy ndarrays for Logistic_Regression module
  xtrain = np.array(xtrain)
  ytrain = np.array(ytrain)

  xtest= np.array(xtest)
  ytest =  np.array(ytest)

  model = Logistic_Regression(lr = 0.01, n_iters = 50_000)
  model.fit(xtrain, ytrain)
  class_pred = model.predict(xtest)
  # print('\n')
  print(model.ConfusionMatrix(ytest, class_pred))
  # print('\n')
  print(f'Accuracy = {model.Accuracy(ytest, class_pred)}')

  #data validation
  if int(data['loanAmount']) > 10000000:
    return {"Remarks":'Loan Amount should be in range Rs.10,000 - Rs.1,00,00,000'}


  gender = 0 if data['Gender'] == "Female" else 1
  married = 0 if data['married'] == "No" else 1 
  dependent = int(data['dependents'].split(" ")[0]) 
  education= 0 if data['education'] == "Not Graduate" else 1 
  selfemployed= 0 if data['selfEmployed'] == "No" else 1
  creditHistory = int(data['creditHistory'])
  if data['Area']=='Urban':
    propertyArea=2
  elif data['Area']=='semiUrban':
    propertyArea=1
  else:
    propertyArea=0
  applicationIncomelog=np.log(int(data['applicantIncome']))
  loanamountlog=np.log(int(data['loanAmount']))
  loanamounttermlog=np.log(int(data['loanAmountTerm']))
  totalincomelog= np.log(int(data['totalIncome']))






  # Process the data and return a response
  data_list = [gender,married,dependent,education,selfemployed,creditHistory, propertyArea,applicationIncomelog,loanamountlog, loanamounttermlog,totalincomelog] 
  data_numpy = np.array(data_list)
#   data_numpy=np.reshape (1,11)


  print("-------------Data---------")
  print(data_numpy)
  print("---------------------prediction-------------------")
  y_pred = model.predict_for_one(data_numpy)
  print(y_pred)
  if y_pred[0] == 1:
    y_predictions = "Loan is acceptable!"
  else:
    y_predictions = "Loan is not acceptable"
  print(y_predictions)
  return {"Remarks":y_predictions}
  

if __name__=="__main__":
    app.run(debug=True)