import re
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate
from models import db, User, Role
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin role if it doesn't exist
        if not Role.query.filter_by(name='Admin').first():
            admin_role = Role(name='Admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_password(password):
    if len(password) < 8 or len(password) > 128:
        return False, "Password must be between 8 and 128 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    if re.search(r'\s', password):
        return False, "Password must not contain spaces"
    if not re.match(r'^[a-zA-Zа-яА-Я0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\',.:;]+$', password):
        return False, "Password contains invalid characters"
    return True, ""

def validate_login(login):
    if not login:
        return False, "Login cannot be empty"
    if len(login) < 5:
        return False, "Login must be at least 5 characters long"
    if not re.match(r'^[a-zA-Z0-9]+$', login):
        return False, "Login must contain only Latin letters and numbers"
    return True, ""

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(login=login).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid login or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)

@app.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        role_id = request.form.get('role_id')

        login_valid, login_msg = validate_login(login)
        password_valid, password_msg = validate_password(password)

        if not login_valid:
            flash(login_msg)
            return render_template('user_form.html', roles=Role.query.all())
        if not password_valid:
            flash(password_msg)
            return render_template('user_form.html', roles=Role.query.all())
        if not first_name:
            flash("First name cannot be empty")
            return render_template('user_form.html', roles=Role.query.all())

        try:
            user = User(
                login=login,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                role_id=role_id if role_id else None
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('User created successfully')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating user')
            return render_template('user_form.html', roles=Role.query.all())

    return render_template('user_form.html', roles=Role.query.all())

@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        role_id = request.form.get('role_id')

        if not first_name:
            flash("First name cannot be empty")
            return render_template('user_form.html', user=user, roles=Role.query.all())

        try:
            user.first_name = first_name
            user.last_name = last_name
            user.middle_name = middle_name
            user.role_id = role_id if role_id else None
            db.session.commit()
            flash('User updated successfully')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating user')
            return render_template('user_form.html', user=user, roles=Role.query.all())

    return render_template('user_form.html', user=user, roles=Role.query.all())

@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user')
    return redirect(url_for('index'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(old_password):
            flash('Current password is incorrect')
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match')
            return render_template('change_password.html')

        password_valid, password_msg = validate_password(new_password)
        if not password_valid:
            flash(password_msg)
            return render_template('change_password.html')

        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error changing password')
            return render_template('change_password.html')

    return render_template('change_password.html') 