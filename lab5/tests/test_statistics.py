import pytest
from flask import url_for
from lab5.modelses import User, Role, VisitLog
from datetime import datetime

def test_visit_logging(client, app):
    with app.app_context():
        # Create test user
        role = Role(name='User', description='Regular User')
        user = User(login='testuser', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        app.db.session.add(role)
        app.db.session.add(user)
        app.db.session.commit()

        # Login
        client.post('/login', data={
            'login': 'testuser',
            'password': 'password123'
        })

        # Visit some pages
        client.get('/')
        client.get('/user/1')
        
        # Check logs
        logs = VisitLog.query.filter_by(user_id=user.id).all()
        assert len(logs) == 2
        assert logs[0].path == '/user/1'
        assert logs[1].path == '/'

def test_page_stats(client, app):
    with app.app_context():
        # Create test user
        role = Role(name='User', description='Regular User')
        user = User(login='testuser', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        app.db.session.add(role)
        app.db.session.add(user)
        app.db.session.commit()

        # Create some visit logs
        for _ in range(3):
            log = VisitLog(path='/test', user_id=user.id)
            app.db.session.add(log)
        app.db.session.commit()

        # Login
        client.post('/login', data={
            'login': 'testuser',
            'password': 'password123'
        })

        # Check stats page
        response = client.get('/stats/pages')
        assert response.status_code == 200
        assert b'/test' in response.data
        assert b'3' in response.data

def test_user_stats(client, app):
    with app.app_context():
        # Create test users
        role = Role(name='User', description='Regular User')
        user1 = User(login='testuser1', first_name='Test1', last_name='User', role=role)
        user2 = User(login='testuser2', first_name='Test2', last_name='User', role=role)
        user1.set_password('password123')
        user2.set_password('password123')
        app.db.session.add(role)
        app.db.session.add(user1)
        app.db.session.add(user2)
        app.db.session.commit()

        # Create some visit logs
        for _ in range(2):
            log = VisitLog(path='/test', user_id=user1.id)
            app.db.session.add(log)
        log = VisitLog(path='/test', user_id=user2.id)
        app.db.session.add(log)
        app.db.session.commit()

        # Login as admin
        admin_role = Role(name='Admin', description='Administrator')
        admin = User(login='admin', first_name='Admin', last_name='User', role=admin_role)
        admin.set_password('admin123')
        app.db.session.add(admin_role)
        app.db.session.add(admin)
        app.db.session.commit()

        client.post('/login', data={
            'login': 'admin',
            'password': 'admin123'
        })

        # Check stats page
        response = client.get('/stats/users')
        assert response.status_code == 200
        assert b'Test1 User' in response.data
        assert b'Test2 User' in response.data
        assert b'2' in response.data
        assert b'1' in response.data

def test_export_stats(client, app):
    with app.app_context():
        # Create test user
        role = Role(name='User', description='Regular User')
        user = User(login='testuser', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        app.db.session.add(role)
        app.db.session.add(user)
        app.db.session.commit()

        # Create some visit logs
        for _ in range(3):
            log = VisitLog(path='/test', user_id=user.id)
            app.db.session.add(log)
        app.db.session.commit()

        # Login
        client.post('/login', data={
            'login': 'testuser',
            'password': 'password123'
        })

        # Check CSV export
        response = client.get('/stats/pages/export')
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert b'Page' in response.data
        assert b'/test' in response.data
        assert b'3' in response.data 