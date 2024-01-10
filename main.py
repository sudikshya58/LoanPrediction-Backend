from flask import Flask,request,jsonify, redirect
from models import db,User,Register
from flask_cors import CORS, cross_origin

from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
CORS(app, origins=["*"] )
app.config["SECRET KEY"] = "SUDIKSHYA"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/loanprediction"
SQLALCHEMY_TRACK_NOTIFICATIONS=False
SQLALCHEMY_ECHO=True
db.init_app(app)
with app.app_context():
    db.create_all() 
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
@app.route("/registers",methods=["POST"])
def register():
    if request.method=="POST":
        data=request.get_json()
        username=data.get('username')
        useremail=data.get('useremail')
        userphone=data.get('userphone')
        userpassword=data.get('userpassword')
        confirmpassword=data.get('confirmpassword')
        new_Register = Register(username=username, useremail=useremail, userpassword=userpassword, userphone=userphone, confirmpassword=confirmpassword)
         # Add user to the database session
        db.session.add(new_Register)

        # Commit changes to the database
        db.session.commit()

        return jsonify({"message": "User registered in successfully"})

if __name__=="__main__":
    app.run(debug=True)