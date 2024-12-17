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

@app.route("/staff/<int:id>", methods=['GET'])
@jwt_required()
@role_required('admin')
def get_single_staff(id):
    staff= db.session.get(Staff, id)
    if not staff:
        return jsonify(
            {
                "success": False,
                "error": "Staff not found"
            }
        ), 404
    return jsonify(
        {
            "success": True,
            "data": staff.to_dict()
        }
    ), 200

@app.route("/staff", methods=['POST'])
@jwt_required()
@role_required('admin')
def add_staff():
    if not request.is_json:
        return jsonify(
            {
                "success": False,
                "error": "Content-type must be application/json"
            }
        ), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    required_fields = ["BLOOD_BANKS_id", "ADDRESS_id", "category", "gender","job_title", "name", "birthdate" ]
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "success": False,
                    "error": f"Missing field: {field}"
                }
            ), 400

    try:
        new_staff = Staff(
            BLOOD_BANKS_id = data['BLOOD_BANKS_id'],
            ADDRESS_id = data['ADDRESS_id'],
            category = data['category'],
            gender = data['gender'],
            job_title = data['job_title'],
            name = data['name'],
            birthdate=data["birthdate"]
       )
        db.session.add(new_staff)
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "data": new_staff.to_dict()
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "error": str(e)
            }
        ), 500
    
@app.route("/staff/<int:id>", methods=["PUT"])
@jwt_required()
@role_required('admin')
def update_staff(id):
    staff = db.session.get(Staff, id)
    if not staff:
        return jsonify(
            {
                "success": False,
                "error": "Staff not found"
            }
        ), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    updatable_fields = ["BLOOD_BANKS_id", "ADDRESS_id", "category", "gender","job_title", "name", "birthdate" ]
    for field in updatable_fields:
        if field in data:
            setattr(staff, field, data[field])

    db.session.commit()
    return jsonify(
        {
            "success": True,
            "data": staff.to_dict()
        }
    ), 200

@app.route("/staff/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required('admin')
def delete_staff(id):
    staff= db.session.get(Staff, id)
    if not staff:
        return jsonify(
            {
                "success": False,
                "error": "Staff not found"
            }
        ), 404

    db.session.delete(staff)
    db.session.commit()
    return jsonify(
        {
            "success": True,
            "message": "Staff successfully deleted"
        }
    ), 200