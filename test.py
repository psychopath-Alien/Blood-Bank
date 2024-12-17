import pytest
from program import app, Donors, db, Staff
from flask_jwt_extended import create_access_token

def test_sqlalchemy_database_uri():
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'mysql+mysqlconnector://root:root@localhost/bloodbank'
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

@pytest.fixture
def staff_data():
    return {
        "BLOOD_BANKS_id": 1,
        "ADDRESS_id": 1,
        "category": "Nurse",
        "gender": "Female",
        "job_title": "Staff Nurse",
        "name": "Jane Doe",
        "birthdate": "1990-01-01"
    }

@pytest.fixture
def donor_data():
    return {
        "gender": "Male",
        "birthdate": "1985-05-15",
        "name": "John Smith",
        "contact": "1234567890",
        "BLOOD_BANKS_id": 1,
        "MEDICATIONS_code": 2,
        "MEDICAL_CONDITIONS_code": 2
    }

def test_staff_to_dict(staff_data):
    staff = Staff(**staff_data)
    staff_dict = staff.to_dict()
    assert staff_dict["id"] is None
    assert staff_dict["BLOOD_BANKS_id"] == staff_data["BLOOD_BANKS_id"]
    assert staff_dict["category"] == staff_data["category"]
    assert staff_dict["gender"] == staff_data["gender"]
    assert staff_dict["job_title"] == staff_data["job_title"]
    assert staff_dict["name"] == staff_data["name"]
    assert staff_dict["birthdate"] == staff_data["birthdate"]

def test_donor_to_dict(donor_data):
    donor = Donors(**donor_data)
    donor_dict = donor.to_dict()
    assert donor_dict["id"] is None
    assert donor_dict["gender"] == donor_data["gender"]
    assert donor_dict["birthdate"] == donor_data["birthdate"]
    assert donor_dict["name"] == donor_data["name"]
    assert donor_dict["contact"] == donor_data["contact"]
    assert donor_dict["BLOOD_BANKS_id"] == donor_data["BLOOD_BANKS_id"]
    assert donor_dict["MEDICATIONS_code"] == donor_data["MEDICATIONS_code"]
    assert donor_dict["MEDICAL_CONDITIONS_code"] == donor_data["MEDICAL_CONDITIONS_code"]

def test_staff_empty_fields():
    staff_data = {
        "BLOOD_BANKS_id": 1,
        "ADDRESS_id": 1,
        "category": "",
        "gender": "",
        "job_title": "",
        "name": "",
        "birthdate": ""
    }
    staff = Staff(**staff_data)
    staff_dict = staff.to_dict()
    
    assert staff_dict["category"] == ""
    assert staff_dict["gender"] == ""
    assert staff_dict["job_title"] == ""
    assert staff_dict["name"] == ""
    assert staff_dict["birthdate"] == ""

def test_donor_empty_fields():
    donor_data = {
        "gender": "",
        "birthdate": "",
        "name": "",
        "contact": "",
        "BLOOD_BANKS_id": 1,
        "MEDICATIONS_code": 0,
        "MEDICAL_CONDITIONS_code": 0
    }
    
    donor = Donors(**donor_data)
    donor_dict = donor.to_dict()
    
    assert donor_dict["gender"] == ""
    assert donor_dict["birthdate"] == ""
    assert donor_dict["name"] == ""
    assert donor_dict["contact"] == ""

def test_staff_max_length():
    long_string = "a" * 51
    staff_data = {
        "BLOOD_BANKS_id": 1,
        "ADDRESS_id": 1,
        "category": long_string,
        "gender": long_string,
        "job_title": long_string,
        "name": long_string,
        "birthdate": "1990-01-01"
    }
    
    staff = Staff(**staff_data)
    staff_dict = staff.to_dict()
    
    assert len(staff_dict["category"]) > 50
    assert len(staff_dict["gender"]) > 20
    assert len(staff_dict["job_title"]) > 50
    assert len(staff_dict["name"]) > 45

def test_donor_max_length():
    long_string = "a" * 51
    donor_data = {
        "gender": "Male",
        "birthdate": "1985-05-15",
        "name": long_string,
        "contact": long_string,
        "BLOOD_BANKS_id": 1,
        "MEDICATIONS_code": 2,
        "MEDICAL_CONDITIONS_code": 3
    }
    
    donor = Donors(**donor_data)
    donor_dict = donor.to_dict()
    
    assert len(donor_dict["name"]) > 50
    assert len(donor_dict["contact"]) > 45
    assert len(donor_dict["gender"]) < 15

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_login_staff(client):
    response = client.post('/login', json={'username': 'staff', 'password': 'password'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'Token' in data
    assert data["Token"] is not None

def test_login_donor(client):
    response = client.post('/login', json={'username': 'donor', 'password': 'donorpass'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'Token' in data
    assert data["Token"] is not None

def test_login_invalid_credentials(client):
    response = client.post('/login', json={'username': 'wronguser', 'password': 'wrongpass'})
    
    assert response.status_code == 401
    data = response.get_json()
    assert data["msg"] == "Invalid username or password"

def test_login_missing_username(client):
    response = client.post('/login', json={'password': 'password'})
    
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data

def test_login_missing_password(client):
    response = client.post('/login', json={'username': 'staff'})
    
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data

@pytest.fixture
def admin_token():
    return create_access_token(identity="admin", additional_claims={"role": "admin"})

@pytest.fixture
def donor_token():
    return create_access_token(identity="donor", additional_claims={"role": "donor"})

def test_get_all_staff_admin(client, admin_token):
    response = client.get('/staff', headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data


def test_get_all_staff_forbidden(client, donor_token):
    response = client.get('/staff', headers={'Authorization': f'Bearer {donor_token}'})
    
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["msg"] == "Access forbidden."

def test_get_all_staff_no_token(client):
    response = client.get('/staff')
    
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data
    assert data["msg"] == "Missing Authorization Header"

def test_get_all_staff_invalid_token(client):
    response = client.get('/staff', headers={'Authorization': 'Bearer invalid_token'})
    
    assert response.status_code == 422
    data = response.get_json()
    assert "msg" in data
    assert data["msg"] == "Not enough segments"

@pytest.fixture
def sample_staff():
    staff = Staff(
        BLOOD_BANKS_id=1,
        ADDRESS_id=1,
        category="Nurse",
        gender="Female",
        job_title="Head Nurse",
        name="John Doe",
        birthdate="1985-07-15"
    )
    db.session.add(staff)
    db.session.commit()
    return staff

@pytest.fixture
def admin_token():
    return create_access_token(identity="admin", additional_claims={"role": "admin"})

@pytest.fixture
def donor_token():
    return create_access_token(identity="donor", additional_claims={"role": "donor"})

def test_get_single_staff_valid(client, admin_token, sample_staff):
    response = client.get(f'/staff/{sample_staff.id}', headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["id"] == sample_staff.id
    assert data["data"]["name"] == sample_staff.name

def test_get_single_staff_not_found(client, admin_token):
    response = client.get('/staff/9999', headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Staff not found"

def test_get_single_staff_forbidden(client, donor_token, sample_staff):
    response = client.get(f'/staff/{sample_staff.id}', headers={'Authorization': f'Bearer {donor_token}'})
    
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["msg"] == "Access forbidden."

def test_get_single_staff_no_token(client):
    response = client.get('/staff/1')
    
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data
    assert data["msg"] == "Missing Authorization Header"

def test_get_single_staff_invalid_token(client):
    response = client.get('/staff/1', headers={'Authorization': 'Bearer invalid_token'})
    
    assert response.status_code == 422
    data = response.get_json()
    assert "msg" in data
    assert data["msg"] == "Not enough segments"

def test_get_single_staff_valid(client, admin_token, sample_staff):
    response = client.get(f'/staff/{sample_staff.id}', headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["id"] == sample_staff.id
    assert data["data"]["name"] == sample_staff.name

def test_get_single_staff_not_found(client, admin_token):
    response = client.get('/staff/9999', headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Staff not found"

def test_get_single_staff_forbidden(client, donor_token, sample_staff):
    response = client.get(f'/staff/{sample_staff.id}', headers={'Authorization': f'Bearer {donor_token}'})
    
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["msg"] == "Access forbidden."

def test_add_staff_valid(client, admin_token):
    new_staff_data = {
        "BLOOD_BANKS_id": 1,
        "ADDRESS_id": 1,
        "category": "Nurse",
        "gender": "Male",
        "job_title": "Nurse",
        "name": "Jane Doe",
        "birthdate": "1990-08-20"
    }

    response = client.post('/staff', json=new_staff_data, headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data

def test_add_staff_missing_field(client, admin_token):
    new_staff_data = {
        "BLOOD_BANKS_id": 1,
        "ADDRESS_id": 1,
        "category": "Nurse",
        "gender": "Male",
        "job_title": "Nurse",
        "name": "Jane Doe"
    }

    response = client.post('/staff', json=new_staff_data, headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Missing field: birthdate"

def test_add_staff_invalid_json(client, admin_token):
    response = client.post('/staff', data="invalid_json", headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Content-type must be application/json"

def test_add_staff_forbidden(client, donor_token):
    new_staff_data = {
        "BLOOD_BANKS_id": 1,
        "ADDRESS_id": 1,
        "category": "Nurse",
        "gender": "Female",
        "job_title": "Nurse",
        "name": "John Smith",
        "birthdate": "1995-02-15"
    }

    response = client.post('/staff', json=new_staff_data, headers={'Authorization': f'Bearer {donor_token}'})
    
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["msg"] == "Access forbidden."

def test_add_staff_no_token(client):
    new_staff_data = {
        "BLOOD_BANKS_id": 1,
        "ADDRESS_id": 1,
        "category": "Nurse",
        "gender": "Female",
        "job_title": "Nurse",
        "name": "John Smith",
        "birthdate": "1995-02-15"
    }
    response = client.post('/staff', json=new_staff_data)
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data
    assert data["msg"] == "Missing Authorization Header"

def test_update_staff_success(client, admin_token, sample_staff):
    update_data = {
        "category": "Doctor",
        "job_title": "Senior Doctor",
        "name": "John Smith"
    }
    response = client.put(
        f"/staff/{sample_staff.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["category"] == "Doctor"
    assert data["data"]["job_title"] == "Senior Doctor"
    assert data["data"]["name"] == "John Smith"

def test_update_staff_invalid_json(client, admin_token, sample_staff):
    response = client.put(
        f"/staff/{sample_staff.id}",
        data="invalid_json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Invalid JSON"

def test_update_staff_not_found(client, admin_token):
    update_data = {
        "category": "Doctor"
    }
    response = client.put(
        "/staff/9999",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Staff not found"

def test_update_staff_no_fields(client, admin_token, sample_staff):
    response = client.put(
        f"/staff/{sample_staff.id}",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400 
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Invalid JSON"

def test_update_staff_forbidden(client, donor_token, sample_staff):
    update_data = {
        "category": "Doctor"
    }
    response = client.put(
        f"/staff/{sample_staff.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["msg"] == "Access forbidden."

def test_update_staff_unauthorized(client, sample_staff):
    update_data = {
        "category": "Doctor"
    }
    response = client.put(f"/staff/{sample_staff.id}", json=update_data)
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data
    assert data["msg"] == "Missing Authorization Header"

def test_delete_staff_success(client, admin_token, sample_staff):
    response = client.delete(
        f"/staff/{sample_staff.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["message"] == "Staff successfully deleted"

    response_check = client.get(
        f"/staff/{sample_staff.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response_check.status_code == 404
    data_check = response_check.get_json()
    assert data_check["success"] is False
    assert data_check["error"] == "Staff not found"


def test_delete_staff_not_found(client, admin_token):
    response = client.delete(
        "/staff/9999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Staff not found"


def test_delete_staff_forbidden(client, donor_token, sample_staff):
    response = client.delete(
        f"/staff/{sample_staff.id}",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert data["msg"] == "Access forbidden."


def test_delete_staff_unauthorized(client, sample_staff):
    response = client.delete(f"/staff/{sample_staff.id}")
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data
    assert data["msg"] == "Missing Authorization Header"