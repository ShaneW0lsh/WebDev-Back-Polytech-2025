# User Management System

A Flask-based web application for managing user accounts with authentication and role-based access control.

## Features

- User authentication (login/logout)
- User management (create, read, update, delete)
- Role-based access control
- Password change functionality
- Input validation
- Responsive Bootstrap UI

## Requirements

- Python 3.8+
- Flask and other dependencies listed in requirements.txt

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

2. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5000

## Running Tests

To run the test suite:
```bash
pytest
```

## Project Structure

- `app.py` - Main application file
- `models.py` - Database models
- `config.py` - Application configuration
- `templates/` - HTML templates
- `tests.py` - Test suite
- `requirements.txt` - Project dependencies 