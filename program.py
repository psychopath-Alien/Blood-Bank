from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps


app = Flask(__name__)
jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/bloodbank'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'sknabdoolb'

db = SQLAlchemy(app)



class Staff(db.Model):
    __tablename__='staff'
    id = db.Column(db.Integer, primary_key=True)
    BLOOD_BANKS_id = db.Column(db.Integer,  nullable=False)
    ADDRESS_id = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(45), nullable=False)
    birthdate = db.Column(db.String(45), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "BLOOD_BANKS_id": self.BLOOD_BANKS_id,
            "ADDRESS_id": self.ADDRESS_id,
            "category": self.category,
            "gender": self.gender,
            "job_title": self.job_title,
            "name": self.name,
            "birthdate": self.birthdate
        }
    
class Donors(db.Model):
    __tablename__='donors'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(15), nullable=False)
    birthdate = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(45), nullable=False)
    BLOOD_BANKS_id = db.Column(db.Integer, nullable=False)
    MEDICATIONS_code = db.Column(db.Integer, nullable=False)
    MEDICAL_CONDITIONS_code = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "gender": self.gender,
            "birthdate": self.birthdate,
            "name":  self.name,
            "contact": self.contact,
            "BLOOD_BANKS_id": self.BLOOD_BANKS_id,
            "MEDICATIONS_code": self.MEDICAL_CONDITIONS_code,
            "MEDICAL_CONDITIONS_code": self.MEDICAL_CONDITIONS_code
        }
        