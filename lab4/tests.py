import pytest
from app import app, db, User, Role
from werkzeug.security import generate_password_hash

# todo figure out how fixture works, lifecycle and how to manipulate it (gets generated for each test or for all tests at once). when it gets generated and how to achieve test isolation if we work with database
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            role = Role(name='Admin', description='Administrator')
            db.session.add(role)
            user = User(
                login='testuser',
                first_name='Test',
                last_name='User',
                role=role
            )
            user.set_password('Test123!')
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Users' in response.data
    assert b'testuser' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(client):
    response = client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data

def test_login_failure(client):
    response = client.post('/login', data={
        'login': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid login or password' in response.data

def test_create_user(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/user/create', data={
        'login': 'newuser',
        'password': 'NewPass123!',
        'first_name': 'New',
        'last_name': 'User',
        'role_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'User created successfully' in response.data

def test_create_user_validation(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/user/create', data={
        'login': 'user',
        'password': 'NewPass123!',
        'first_name': 'New',
        'last_name': 'User'
    }, follow_redirects=True)
    assert b'Login must be at least 5 characters long' in response.data

    response = client.post('/user/create', data={
        'login': 'newuser',
        'password': 'short',
        'first_name': 'New',
        'last_name': 'User'
    }, follow_redirects=True)
    assert b'Password must be between 8 and 128 characters' in response.data

def test_edit_user(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/user/1/edit', data={
        'first_name': 'Updated',
        'last_name': 'User',
        'role_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'User updated successfully' in response.data

def test_delete_user(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    client.post('/user/create', data={
        'login': 'todelete',
        'password': 'Test123!',
        'first_name': 'To',
        'last_name': 'Delete'
    })
    
    response = client.post('/user/2/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'User deleted successfully' in response.data

def test_change_password(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/change-password', data={
        'old_password': 'Test123!',
        'new_password': 'NewPass123!',
        'confirm_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password changed successfully' in response.data

# todo put into different tests
# todo add tests that test that view users work correctly
# add unit tests for validation function
def test_change_password_validation(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/change-password', data={
        'old_password': 'wrongpass',
        'new_password': 'NewPass123!',
        'confirm_password': 'NewPass123!'
    }, follow_redirects=True)
    assert b'Current password is incorrect' in response.data

    response = client.post('/change-password', data={
        'old_password': 'Test123!',
        'new_password': 'NewPass123!',
        'confirm_password': 'DifferentPass123!'
    }, follow_redirects=True)
    assert b'New passwords do not match' in response.data

def test_unauthorized_access(client):
    response = client.get('/user/create', follow_redirects=True)
    assert b'Login' in response.data

    response = client.get('/user/1/edit', follow_redirects=True)
    assert b'Login' in response.data

    response = client.post('/user/1/delete', follow_redirects=True)
    assert b'Login' in response.data 