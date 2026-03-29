"""
Routes d'administration
ENSA Béni Mellal - Système IA Responsable
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from app.models import User, Request, AuditLog, CacheEntry, SystemConfig
from app.utils.security import admin_required, get_client_ip
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Tableau de bord administrateur"""
    
    # Statistiques globales
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_requests = Request.query.count()
    pending_validation = Request.query.filter_by(validated_by_human=False).count()
    
    # Statistiques des 7 derniers jours
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()
    new_requests_week = Request.query.filter(Request.created_at >= week_ago).count()
    
    # Logs d'audit récents
    recent_logs = AuditLog.query\
        .order_by(AuditLog.timestamp.desc())\
        .limit(20)\
        .all()
    
    # Requêtes par type
    requests_by_type = db.session.query(
        Request.request_type,
        func.count(Request.id).label('count')
    ).group_by(Request.request_type).all()
    
    # Performance du cache
    cache_stats = {
        'total_entries': CacheEntry.query.count(),
        'total_hits': db.session.query(func.sum(CacheEntry.hit_count)).scalar() or 0
    }
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_requests=total_requests,
                         pending_validation=pending_validation,
                         new_users_week=new_users_week,
                         new_requests_week=new_requests_week,
                         logs=recent_logs,
                         requests_by_type=requests_by_type,
                         cache_stats=cache_stats)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Liste des utilisateurs"""
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtres
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    # Query de base
    query = User.query
    
    # Appliquer les filtres
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    # Pagination
    users_pagination = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('admin/users.html',
                         users=users_pagination.items,
                         pagination=users_pagination,
                         search=search,
                         role_filter=role_filter,
                         status_filter=status_filter)


@admin_bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Activer/Désactiver un utilisateur"""
    
    user = User.query.get_or_404(user_id)
    
    # Ne pas se désactiver soi-même
    from flask_login import current_user
    if user.id == current_user.id:
        flash('Vous ne pouvez pas désactiver votre propre compte.', 'warning')
        return redirect(url_for('admin.users'))
    
    # Inverser le statut
    user.is_active = not user.is_active
    action = 'UTILISATEUR_ACTIVE' if user.is_active else 'UTILISATEUR_DESACTIVE'
    
    db.session.commit()
    
    # Log
    AuditLog.log_action(
        user_id=current_user.id,
        action=action,
        details=f"Utilisateur {user.username} (ID: {user.id})",
        severity='warning',
        resource_type='user',
        resource_id=user.id
    )
    
    status = 'activé' if user.is_active else 'désactivé'
    flash(f'Utilisateur {user.username} {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/requests')
@login_required
@admin_required
def requests():
    """Liste des demandes"""
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtres
    request_type = request.args.get('type', '')
    validation_status = request.args.get('validation', '')
    
    # Query de base
    query = Request.query
    
    # Appliquer les filtres
    if request_type:
        query = query.filter_by(request_type=request_type)
    
    if validation_status == 'validated':
        query = query.filter_by(validated_by_human=True)
    elif validation_status == 'pending':
        query = query.filter_by(validated_by_human=False)
    
    # Pagination
    requests_pagination = query.order_by(Request.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('admin/requests.html',
                         requests=requests_pagination.items,
                         pagination=requests_pagination,
                         request_type=request_type,
                         validation_status=validation_status)


@admin_bp.route('/request/<int:request_id>/validate', methods=['GET', 'POST'])
@login_required
@admin_required
def validate_request(request_id):
    """Valider une demande"""
    
    req = Request.query.get_or_404(request_id)
    
    if request.method == 'POST':
        from flask_login import current_user
        
        validation_status = request.form.get('status')  # 'approved', 'rejected', 'needs_review'
        comment = request.form.get('comment', '').strip()
        
        req.validated_by_human = (validation_status == 'approved')
        req.validator_id = current_user.id
        req.validation_date = datetime.utcnow()
        req.validation_comment = comment
        req.validation_status = validation_status
        
        db.session.commit()
        
        # Log
        AuditLog.log_action(
            user_id=current_user.id,
            action='VALIDATION_DEMANDE',
            details=f"Demande {request_id}: {validation_status}",
            severity='info',
            resource_type='request',
            resource_id=request_id
        )
        
        flash(f'Demande {validation_status}.', 'success')
        return redirect(url_for('admin.requests'))
    
    return render_template('admin/validate_request.html', req=req)


@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    """Consulter les logs d'audit"""
    
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Filtres
    action_filter = request.args.get('action', '')
    severity_filter = request.args.get('severity', '')
    user_id = request.args.get('user_id', type=int)
    
    # Query de base
    query = AuditLog.query
    
    # Appliquer les filtres
    if action_filter:
        query = query.filter(AuditLog.action.ilike(f'%{action_filter}%'))
    
    if severity_filter:
        query = query.filter_by(severity=severity_filter)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # Pagination
    logs_pagination = query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('admin/logs.html',
                         logs=logs_pagination.items,
                         pagination=logs_pagination,
                         action_filter=action_filter,
                         severity_filter=severity_filter,
                         user_id=user_id)


@admin_bp.route('/cache')
@login_required
@admin_required
def cache():
    """Gestion du cache"""
    
    # Statistiques du cache
    total_entries = CacheEntry.query.count()
    total_hits = db.session.query(func.sum(CacheEntry.hit_count)).scalar() or 0
    
    # Top 10 entrées par hits
    top_entries = CacheEntry.query\
        .order_by(CacheEntry.hit_count.desc())\
        .limit(10)\
        .all()
    
    # Entrées par type
    entries_by_type = db.session.query(
        CacheEntry.request_type,
        func.count(CacheEntry.id).label('count')
    ).group_by(CacheEntry.request_type).all()
    
    return render_template('admin/cache.html',
                         total_entries=total_entries,
                         total_hits=total_hits,
                         top_entries=top_entries,
                         entries_by_type=entries_by_type)


@admin_bp.route('/cache/clear', methods=['POST'])
@login_required
@admin_required
def clear_cache():
    """Vider le cache"""
    
    from flask_login import current_user
    
    # Supprimer toutes les entrées expirées
    expired = CacheEntry.query.filter(
        CacheEntry.expires_at < datetime.utcnow()
    ).delete()
    
    # Option: vider tout le cache
    clear_all = request.form.get('clear_all') == 'true'
    if clear_all:
        total_deleted = CacheEntry.query.delete()
        db.session.commit()
        
        # Log
        AuditLog.log_action(
            user_id=current_user.id,
            action='CACHE_VIDE',
            details=f'{total_deleted} entrées supprimées',
            severity='warning'
        )
        
        flash(f'Cache vidé: {total_deleted} entrées supprimées.', 'success')
    else:
        db.session.commit()
        flash(f'{expired} entrées expirées supprimées.', 'info')
    
    return redirect(url_for('admin.cache'))


@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    """Statistiques avancées"""
    
    # Requêtes par jour (30 derniers jours)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_requests = db.session.query(
        func.date(Request.created_at).label('date'),
        func.count(Request.id).label('count')
    ).filter(Request.created_at >= thirty_days_ago)\
     .group_by(func.date(Request.created_at))\
     .all()
    
    # Taux de validation
    total_requests = Request.query.count()
    validated_requests = Request.query.filter_by(validated_by_human=True).count()
    validation_rate = (validated_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Temps de traitement moyen
    avg_processing_time = db.session.query(
        func.avg(Request.processing_time_ms)
    ).scalar() or 0
    
    # Notes moyennes par type de requête
    avg_ratings = db.session.query(
        Request.request_type,
        func.avg(Request.user_rating).label('avg_rating'),
        func.count(Request.user_rating).label('count')
    ).filter(Request.user_rating.isnot(None))\
     .group_by(Request.request_type)\
     .all()
    
    return render_template('admin/stats.html',
                         daily_requests=daily_requests,
                         validation_rate=round(validation_rate, 2),
                         avg_processing_time=round(avg_processing_time, 2),
                         avg_ratings=avg_ratings)


@admin_bp.route('/config', methods=['GET', 'POST'])
@login_required
@admin_required
def config():
    """Configuration système"""
    
    if request.method == 'POST':
        from flask_login import current_user
        
        # Récupérer les paramètres du formulaire
        for key in request.form:
            if key.startswith('config_'):
                config_key = key.replace('config_', '')
                value = request.form.get(key)
                
                SystemConfig.set_value(
                    key=config_key,
                    value=value,
                    user_id=current_user.id
                )
        
        flash('Configuration mise à jour.', 'success')
        return redirect(url_for('admin.config'))
    
    # Récupérer la configuration actuelle
    configs = SystemConfig.query.all()
    
    return render_template('admin/config.html', configs=configs)