from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
  
db = SQLAlchemy()
  
def get_uuid():
    return uuid4().hex
  
class User(db.Model):
    __tablename__ = "Newuser"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)
    class Users(db.Model):
     __tablename__ = "loginusers"
     id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
     email = db.Column(db.String(150), unique=True)
     password = db.Column(db.Text, nullable=False)