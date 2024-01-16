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



CORS(app, origins=["*"] )
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
    return jsonify({"useremail": useremail, "access_token": access_token})


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
if __name__=="__main__":
    app.run(debug=True)