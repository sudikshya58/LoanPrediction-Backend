from flask import Flask,request,jsonify, redirect
from models import db,User,Register,AdminUser
from datetime import datetime, timedelta, timezone
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, decode_token, revoke_token
app=Flask(__name__)
CORS(app, origins=["*"], methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Content-Type", "Authorization"])
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
        return jsonify({"error": "Wrong email or password"}), 401
    if not bcrypt.check_password_hash(user.userpassword, userpassword):
        return jsonify({"error": "Wrong email or password"}), 401

    access_token = create_access_token(identity=useremail)
    return jsonify({"useremail": useremail, "access_token": access_token, "message": "Logged in successfully"})

@app.route('/admin_login', methods=["POST"])
@cross_origin()
def admin_login():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    useremail = request.json.get("useremail", None)
    userpassword = request.json.get("userpassword", None)

    if not useremail or not userpassword:
        return jsonify({"error": "Missing email or password"}), 400

    user = AdminUser.query.filter_by(useremail=useremail).first()
    
    if user is None or user.userpassword != userpassword:
         return jsonify({"error": "Wrong email or password"}), 401

    access_token = create_access_token(identity=useremail)
    return jsonify({"useremail": useremail, "admin_token": access_token, "message": "Admin logged in successfully"})
@app.route('/admin_users', methods=["GET"])
def get_admin_users():
    # Query all admin users from the database
    admin_users = AdminUser.query.all()
    
    # Convert the SQLAlchemy objects to a list of dictionaries
    admin_users_list = []
    for user in admin_users:
        user_data = {
            "id": user.id,
            "useremail": user.useremail,
            "userpassword":user.userpassword,
            "role":"admin"
            # Add more fields as needed
        }
        admin_users_list.append(user_data)
    
    # Return the admin user data as JSON
    # return jsonify(admin_users_list)

    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    useremail = request.json.get("useremail", None)
    userpassword = request.json.get("userpassword", None)

    if not useremail or not userpassword:
        return jsonify({"error": "Missing email or password"}), 400

    user = AdminUser.query.filter_by(useremail=useremail).first()
    if user is None:
        return jsonify({"error": "Wrong email or password"}), 401

 

    access_token = create_access_token(identity=useremail)
    return jsonify({"useremail": useremail, "admin_token": access_token, "message": "Admin logged in successfully"})
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
    
    
from flask import request
from flask_cors import cross_origin
import numpy as np
import pandas as pd
from Algorithm.LogisticRegression import Logistic_Regression
    
class loan_prediction_result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    married = db.Column(db.String(3))
    dependents = db.Column(db.String(5))
    education = db.Column(db.String(20))
    self_employed = db.Column(db.String(20))
    credit_history = db.Column(db.Integer)
    property_area = db.Column(db.String(10))
    applicant_income = db.Column(db.Integer)
    loan_amount = db.Column(db.Integer)
    loan_amount_term = db.Column(db.Integer)
    total_income = db.Column(db.Integer)
    prediction_result = db.Column(db.String(100))
 # Adjust import as needed

@app.route('/api/send-data', methods=['POST', 'OPTIONS'])
@cross_origin()
def send_data():
    data = request.json['data']
    new_prediction = None
    
    # Load the trained model
    model = load_model()
    
    # Data preprocessing and model prediction
    gender = 0 if data['Gender'] == "Female" else 1
    married = 0 if data['married'] == "No" else 1 
    dependent = int(data['dependents'].split(" ")[0]) 
    education = 0 if data['education'] == "Not Graduate" else 1 
    self_employed = 0 if data['selfEmployed'] == "No" else 1
    credit_history = int(data['creditHistory'])
    if data['Area'] == 'Urban':
        propertyArea = 2
    elif data['Area'] == 'semiUrban':
        propertyArea = 1
    else:
        propertyArea = 0
    applicationIncomelog = np.log(int(data['applicantIncome']))
    loanamountlog = np.log(int(data['loanAmount']))
    loanamounttermlog = np.log(int(data['loanAmountTerm']))
    totalincomelog = np.log(int(data['totalIncome']))
    
    # Prepare data for prediction
    data_list = [gender, married, dependent, education, self_employed, credit_history, propertyArea, applicationIncomelog, loanamountlog, loanamounttermlog, totalincomelog] 
    data_numpy = np.array(data_list)
    
    # Make prediction
    y_pred = model.predict_for_one(data_numpy)
    if y_pred[0] == 1:
        y_predictions = "Loan is acceptable!"
    else:
        y_predictions = "Loan is not acceptable"
    
    # Data validation
    if int(data['loanAmount']) > 10000000:
        return {"Remarks": 'Loan Amount should be in range Rs.10,000 - Rs.1,00,00,000'}
    
    # Save prediction to database
    if condition_met(data):
        new_prediction = create_new_prediction(data, y_predictions)
        if new_prediction is not None:
            db.session.add(new_prediction)
            db.session.commit()
    
    return {"Remarks": y_predictions}

def load_model():
    # Load and return the trained model
    train_data = pd.read_csv(r'A:\Flask\datasets\testdata.csv')
    test_data = pd.read_csv(r'A:\Flask\datasets\traindata.csv')
    xtrain, ytrain = train_data.drop(columns='Loan_Status', axis=1), train_data['Loan_Status']
    xtest, ytest = test_data.drop(columns='Loan_Status', axis=1), test_data['Loan_Status']
    xtrain = np.array(xtrain)
    ytrain = np.array(ytrain)
    xtest = np.array(xtest)
    ytest = np.array(ytest)
    model = Logistic_Regression(lr=0.01, n_iters=50000)
    model.fit(xtrain, ytrain)
    return model

def condition_met(data):
    # Define your condition here
    return True

def create_new_prediction(data, prediction_result):
    # Create and return new prediction based on data
    return loan_prediction_result(
        gender=data.get('Gender'),
        married=data.get('married'),
        dependents=data.get('dependents'),
        education=data.get('education'),
        self_employed=data.get('selfEmployed'),
        credit_history=int(data.get('creditHistory')),
        property_area=data.get('Area'),
        applicant_income=int(data.get('applicantIncome')),
        loan_amount=int(data.get('loanAmount')),
        loan_amount_term=int(data.get('loanAmountTerm')),
        total_income=int(data.get('totalIncome')),
        prediction_result=prediction_result
    )
@app.route('/registered_users', methods=['GET'])
def get_registered_users():
    # Query the database to fetch all registered users
    registered_users = Register.query.all()

    # Serialize the user data into JSON format
    users_data = []
    for user in registered_users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'useremail': user.useremail,
            'userphone': user.userphone
            # Add more fields as needed
        }
        users_data.append(user_data)

    # Return the serialized user data as JSON response
    return jsonify(users_data)

@app.route('/api/predictions', methods=['GET'])
@cross_origin()
def get_predictions():
    predictions = loan_prediction_result.query.all()
    prediction_data = []
    for prediction in predictions:
        prediction_data.append({
            'id': prediction.id,
            'gender': prediction.gender,
            'married': prediction.married,
            'dependents': prediction.dependents,
            'education': prediction.education,
            'selfEmployed': prediction.self_employed,
            'creditHistory': prediction.credit_history,
            'propertyArea': prediction.property_area,
            'applicantIncome': prediction.applicant_income,
            'loanAmount': prediction.loan_amount,
            'loanAmountTerm': prediction.loan_amount_term,
            'totalIncome': prediction.total_income,
            'predictionResult': prediction.prediction_result
        })
    return jsonify(prediction_data)
@app.route('/api/predictions/<int:prediction_id>', methods=['DELETE'])
@cross_origin()
def delete_prediction(prediction_id):
    prediction = loan_prediction_result.query.get(prediction_id)
    
    if prediction:
        db.session.delete(prediction)
        db.session.commit()
        return jsonify({'message': 'Prediction deleted successfully'}), 200
    else:
        return jsonify({'error': 'Prediction not found'}), 404
    
@app.route('/registered_users/<string:user_id>', methods=['DELETE'])
@cross_origin()
def delete_registered_user(user_id):
    # Query the database to find the user with the given ID
    user = Register.query.get(user_id)

    if user:
        # If user exists, delete it from the database
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        # If user does not exist, return a 404 error
        return jsonify({'error': 'User not found'}), 404
    
    

@app.route('/registered_users/<string:user_id>', methods=['PUT'])
@cross_origin()
def edit_registered_user(user_id):
    # Query the database to find the user with the given ID
    user = Register.query.get(user_id)

    if user:
        # Parse the request data to update the user information
        data = request.get_json()
        
        if 'username' in data:
            user.username = data['username']
        if 'useremail' in data:
            user.useremail = data['useremail']
        if 'userphone' in data:
            user.userphone = data['userphone']
        # Add more fields to update as needed

        # Commit the changes to the database
        db.session.commit()
        
        # Return a success message
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        # If user does not exist, return a 404 error
        return jsonify({'error': 'User not found'}), 404



if __name__=="__main__":
    app.run(debug=True)