import pytest
from app import app, db, User, Role
from modelses import VisitLog
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
            admin_role = Role(name='Admin', description='Administrator')
            user_role = Role(name='User', description='Regular User')
            db.session.add(admin_role)
            db.session.add(user_role)
            user = User(
                login='testuser',
                first_name='Test',
                last_name='User',
                role=admin_role
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

# Rights tests
def test_admin_rights(client):
    with app.app_context():
        # Get existing admin role
        admin_role = Role.query.filter_by(name='Admin').first()
        admin = User(login='admin', first_name='Admin', last_name='User', role=admin_role)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        client.post('/login', data={
            'login': 'admin',
            'password': 'admin123'
        })

        assert admin.has_right('create_user')
        assert admin.has_right('edit_user')
        assert admin.has_right('delete_user')
        assert admin.has_right('view_own_logs')

def test_user_rights(client):
    with app.app_context():
        # Create regular user
        role = Role.query.filter_by(name='User').first()
        user = User(login='testuser1', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        db.session.add(role)
        db.session.add(user)
        db.session.commit()

        client.post('/login', data={
            'login': 'testuser1',
            'password': 'password123'
        })

        assert not user.has_right('create_user')
        assert not user.has_right('edit_user')
        assert not user.has_right('delete_user')
        assert user.has_right('edit_self')
        assert user.has_right('view_self')
        assert user.has_right('view_own_logs')

def test_visit_logging(client):
    with app.app_context():
        # Ensure statistics blueprint is registered
        if 'statistics' not in app.blueprints:
            from statistics import bp as statistics_bp
            app.register_blueprint(statistics_bp)

        role = Role.query.filter_by(name='User').first()
        user = User(login='testuser1', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        client.post('/login', data={
            'login': 'testuser1',
            'password': 'password123'
        })

        client.get('/')
        client.get('/user/1')
        
        logs = VisitLog.query.filter_by(user_id=user.id).all()
        assert len(logs) == 2
        assert logs[0].path == '/user/1'
        assert logs[1].path == '/'

# def test_page_stats(client):
#     with app.app_context():
#         role = Role(name='User', description='Regular User')
#         user = User(login='testuser', first_name='Test', last_name='User', role=role)
#         user.set_password('password123')
#         db.session.add(role)
#         db.session.add(user)
#         db.session.commit()

#         for _ in range(3):
#             log = VisitLog(path='/test', user_id=user.id)
#             db.session.add(log)
#         db.session.commit()

#         client.post('/login', data={
#             'login': 'testuser',
#             'password': 'password123'
#         })

#         response = client.get('/stats/pages')
#         assert response.status_code == 200
#         assert b'/test' in response.data
#         assert b'3' in response.data

# def test_user_stats(client):
#     with app.app_context():
#         # Create test users
#         role = Role(name='User', description='Regular User')
#         user1 = User(login='testuser1', first_name='Test1', last_name='User', role=role)
#         user2 = User(login='testuser2', first_name='Test2', last_name='User', role=role)
#         user1.set_password('password123')
#         user2.set_password('password123')
#         db.session.add(role)
#         db.session.add(user1)
#         db.session.add(user2)
#         db.session.commit()

#         for _ in range(2):
#             log = VisitLog(path='/test', user_id=user1.id)
#             db.session.add(log)
#         log = VisitLog(path='/test', user_id=user2.id)
#         db.session.add(log)
#         db.session.commit()

#         # Login as admin
#         admin_role = Role(name='Admin', description='Administrator')
#         admin = User(login='admin', first_name='Admin', last_name='User', role=admin_role)
#         admin.set_password('admin123')
#         db.session.add(admin_role)
#         db.session.add(admin)
#         db.session.commit()

#         client.post('/login', data={
#             'login': 'admin',
#             'password': 'admin123'
#         })

#         response = client.get('/stats/users')
#         assert response.status_code == 200
#         assert b'Test1 User' in response.data
#         assert b'Test2 User' in response.data
#         assert b'2' in response.data
#         assert b'1' in response.data

# def test_export_stats(client):
#     with app.app_context():
#         role = Role(name='User', description='Regular User')
#         user = User(login='testuser', first_name='Test', last_name='User', role=role)
#         user.set_password('password123')
#         db.session.add(role)
#         db.session.add(user)
#         db.session.commit()

#         for _ in range(3):
#             log = VisitLog(path='/test', user_id=user.id)
#             db.session.add(log)
#         db.session.commit()

#         client.post('/login', data={
#             'login': 'testuser',
#             'password': 'password123'
#         })

#         response = client.get('/stats/pages/export')
#         assert response.status_code == 200
#         assert response.mimetype == 'text/csv'
#         assert b'Page' in response.data
#         assert b'/test' in response.data
        