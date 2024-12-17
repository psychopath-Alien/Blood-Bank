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
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'staff' and password == 'password':
        token = create_access_token(identity="staff",additional_claims={"role": "admin"})
        return jsonify({"Token": token}), 200
    elif username == 'donor' and password == 'donorpass':
        token = create_access_token(identity="donor", additional_claims={"role": "donor"})
        return jsonify({"Token": token}), 200
    else:
        return jsonify({"msg": "Invalid username or password"}), 401
    
def role_required(*required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in required_role:
                return jsonify({"success": False, "msg": "Access forbidden."}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@app.route("/staff", methods=["GET"])
@jwt_required()
@role_required('admin')
def get_all_staff():
    staffs = Staff.query.all()
    return jsonify(
        {
            "success": True,
            "data": [staff.to_dict() for staff in staffs]
        }
    ), 200
