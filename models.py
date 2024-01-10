from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.Text, nullable=False)
class Register(db.Model):
    __tablename__ = "register"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    username = db.Column(db.String(150), unique=False)
    useremail = db.Column(db.String(150), unique=True)
    userpassword = db.Column(db.Text, nullable=False)
    userphone = db.Column(db.Text, nullable=False)
    confirmpassword = db.Column(db.Text, nullable=False)
