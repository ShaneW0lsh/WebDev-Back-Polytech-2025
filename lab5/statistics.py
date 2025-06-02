from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from .modelses import db, VisitLog, User
from datetime import datetime
import csv
import io

bp = Blueprint('statistics', __name__)

def check_rights(right):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_right(right):
                flash('У вас недостаточно прав для доступа к данной странице')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@bp.before_request
def log_visit():
    if request.endpoint and 'static' not in request.endpoint:
        log = VisitLog(
            path=request.path,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(log)
        db.session.commit()

@bp.route('/logs')
@login_required
@check_rights('view_own_logs')
def view_logs():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if current_user.role.name == 'Admin':
        logs = VisitLog.query.order_by(VisitLog.created_at.desc())
    else:
        logs = VisitLog.query.filter_by(user_id=current_user.id).order_by(VisitLog.created_at.desc())
    
    pagination = logs.paginate(page=page, per_page=per_page)
    return render_template('logs.html', pagination=pagination)

@bp.route('/stats/pages')
@login_required
@check_rights('view_own_logs')
def page_stats():
    stats = db.session.query(
        VisitLog.path,
        db.func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.path).order_by(db.desc('count')).all()
    
    return render_template('page_stats.html', stats=stats)

@bp.route('/stats/users')
@login_required
@check_rights('view_own_logs')
def user_stats():
    stats = db.session.query(
        User,
        db.func.count(VisitLog.id).label('count')
    ).outerjoin(VisitLog).group_by(User.id).order_by(db.desc('count')).all()
    
    return render_template('user_stats.html', stats=stats)

@bp.route('/stats/pages/export')
@login_required
@check_rights('view_own_logs')
def export_page_stats():
    stats = db.session.query(
        VisitLog.path,
        db.func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.path).order_by(db.desc('count')).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    
    for i, (path, count) in enumerate(stats, 1):
        writer.writerow([i, path, count])
    
    output.seek(0)
    # Добавляем BOM для корректного отображения в Excel
    bom = '\ufeff'.encode('utf-8')
    return send_file(
        io.BytesIO(bom + output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'page_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@bp.route('/stats/users/export')
@login_required
@check_rights('view_own_logs')
def export_user_stats():
    stats = db.session.query(
        User,
        db.func.count(VisitLog.id).label('count')
    ).outerjoin(VisitLog).group_by(User.id).order_by(db.desc('count')).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    
    for i, (user, count) in enumerate(stats, 1):
        writer.writerow([i, user.full_name or 'Неаутентифицированный пользователь', count])
    
    output.seek(0)
    # Добавляем BOM для корректного отображения в Excel
    bom = '\ufeff'.encode('utf-8')
    return send_file(
        io.BytesIO(bom + output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'user_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    ) 