import pytest
from flask import url_for
from lab5.modelses import User, Role

def test_admin_rights(client, app):
    with app.app_context():
        # Create admin user
        admin_role = Role(name='Admin', description='Administrator')
        admin = User(login='admin', first_name='Admin', last_name='User', role=admin_role)
        admin.set_password('admin123')
        app.db.session.add(admin_role)
        app.db.session.add(admin)
        app.db.session.commit()

        # Login as admin
        client.post('/login', data={
            'login': 'admin',
            'password': 'admin123'
        })

        # Test admin rights
        assert admin.has_right('create_user')
        assert admin.has_right('edit_user')
        assert admin.has_right('delete_user')
        assert admin.has_right('view_own_logs')

def test_user_rights(client, app):
    with app.app_context():
        # Create regular user
        role = Role(name='User', description='Regular User')
        user = User(login='testuser', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        app.db.session.add(role)
        app.db.session.add(user)
        app.db.session.commit()

        # Login as user
        client.post('/login', data={
            'login': 'testuser',
            'password': 'password123'
        })

        # Test user rights
        assert not user.has_right('create_user')
        assert not user.has_right('edit_user')
        assert not user.has_right('delete_user')
        assert user.has_right('edit_self')
        assert user.has_right('view_self')
        assert user.has_right('view_own_logs')

def test_restricted_access(client, app):
    with app.app_context():
        # Create regular user
        role = Role(name='User', description='Regular User')
        user = User(login='testuser', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        app.db.session.add(role)
        app.db.session.add(user)
        app.db.session.commit()

        # Login as user
        client.post('/login', data={
            'login': 'testuser',
            'password': 'password123'
        })

        # Test restricted access
        response = client.get('/user/create')
        assert response.status_code == 403

        response = client.get('/user/1/delete')
        assert response.status_code == 403

def test_self_edit_access(client, app):
    with app.app_context():
        # Create regular user
        role = Role(name='User', description='Regular User')
        user = User(login='testuser', first_name='Test', last_name='User', role=role)
        user.set_password('password123')
        app.db.session.add(role)
        app.db.session.add(user)
        app.db.session.commit()

        # Login as user
        client.post('/login', data={
            'login': 'testuser',
            'password': 'password123'
        })

        # Test self-edit access
        response = client.get(f'/user/{user.id}/edit')
        assert response.status_code == 200

        # Test editing another user
        other_user = User(login='other', first_name='Other', last_name='User', role=role)
        app.db.session.add(other_user)
        app.db.session.commit()

        response = client.get(f'/user/{other_user.id}/edit')
        assert response.status_code == 403 