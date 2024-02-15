from . import db  # Import the database instance
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    firstname = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)