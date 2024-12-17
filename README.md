# Blood Bank Management System

## Description

A Flask-based web application for managing blood bank staff and donor information. The system provides RESTful API endpoints for user authentication, staff management, and donor management with role-based access control.

## Key Features
- JWT-based authentication
- Role-based access control (admin and donor roles)
- CRUD operations for staff and donors
- Secure API endpoints
- MySQL database integration

## Technologies Used
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- MySQL
- Python 3.8+

## Prerequisites

- Python 3.8+
- MySQL
- pip
- virtualenv (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/psychopath-Alien/BloodBankAPI.git
cd <local directory>
```

2. Create a virtual environment:
```bash
pip install virtualenv ( do it if the virtual environment is not installed)
python -m venv venv
source venv/bin/activate 
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Database Setup

1. Create a MySQL database:
```sql
CREATE DATABASE bloodbank;
DATABASE URL: 
SECRET KEY: sknabdoolb
```

2. Update database configuration in the application:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/bloodbank'
```

### Environment Variables

Create a `.env` file with the following variables:
```
DATABASE_URL=mysql+mysqlconnector://root:root@localhost/bloodbank
SECRET_KEY=sknabdoolb
JWT_SECRET_KEY=sknabdoolb
```

## API Endpoints

### Authentication
| Endpoint | Method | Description | Roles |
|----------|--------|-------------|-------|
| `/login` | POST | User authentication | All |

### Staff Endpoints
| Endpoint | Method | Description | Roles |
|----------|--------|-------------|-------|
| `/staff` | GET    | List all staff | Admin |
| `/staff/<id>` | GET | Get single staff | Admin |
| `/staff` | POST | Add new staff | Admin |
| `/staff/<id>` | PUT | Update staff | Admin |
| `/staff/<id>` | DELETE | Delete staff | Admin |

### Donor Endpoints
| Endpoint | Method | Description | Roles |
|----------|--------|-------------|-------|
| `/donor` | GET | List all donors | Admin |
| `/donor/<id>` | GET | Get single donor | Admin |
| `/donor` | POST | Add new donor | Admin, Donor |
| `/donor/<id>` | PUT | Update donor | Admin |
| `/donor/<id>` | DELETE | Delete donor | Admin |

## Authentication

The system uses JWT (JSON Web Tokens) for authentication:
- Admin credentials: 
  - Username: `staff`
  - Password: `password`
- Donor credentials:
  - Username: `donor`
  - Password: `donorpass`

## Running the Application

```bash
set FLASK_APP=program.py

flask run
```

## Testing

### Running Tests

```bash
pytest test.py

```

## Git Commit Guidelines

We use Conventional Commits for commit messages.

### Commit Types
- `feat`: test for every instance
- `fix`: library update

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/BloodBankFeature`)
3. Commit your changes (`git commit -m 'feat: add new donor management feature'`)
4. Push to the branch (`git push origin feature/BloodBankFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Ricky Castillo - castrikcy28@gmail.com

Project Link: https://github.com/psychopath-Alien/BloodBankAPI.git