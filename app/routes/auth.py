"""
Routes d'authentification
ENSA Béni Mellal - Système IA Responsable
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import db, limiter
from app.models import User, AuditLog, ConsentLog
from app.utils.security import (
    hash_password, verify_password, check_account_locked,
    handle_failed_login, get_client_ip
)
from app.utils.validators import validate_registration_form, validate_login_form
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """Inscription avec consentement RGPD"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        consent = request.form.get('consent') == 'on'
        
        # Validation
        is_valid, errors = validate_registration_form(
            username, email, password, confirm_password, consent
        )
        
        if not is_valid:
            for field, error_list in errors.items():
                if isinstance(error_list, list):
                    for error in error_list:
                        flash(error, 'danger')
                else:
                    flash(error_list, 'danger')
            return render_template('auth/register.html')
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà utilisé.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Cette adresse email est déjà utilisée.', 'danger')
            return render_template('auth/register.html')
        
        # Créer l'utilisateur
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            consent_given=True,
            consent_date=datetime.utcnow(),
            consent_version='1.0',
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Enregistrer le consentement
        consent_log = ConsentLog(
            user_id=user.id,
            consent_type='terms_and_conditions',
            consent_version='1.0',
            consent_given=True,
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(consent_log)
        
        # Log d'audit
        AuditLog.log_action(
            user_id=user.id,
            action='INSCRIPTION',
            details=f'Nouvel utilisateur : {username}',
            severity='info',
            ip_address=get_client_ip()
        )
        
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Authentification sécurisée"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        # Validation basique
        is_valid, error = validate_login_form(username, password)
        if not is_valid:
            flash(error, 'danger')
            return render_template('auth/login.html')
        
        # Chercher l'utilisateur
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash('Identifiants incorrects.', 'danger')
            return render_template('auth/login.html')
        
        # Vérifier si le compte est verrouillé
        is_locked, lock_message = check_account_locked(user)
        if is_locked:
            flash(lock_message, 'warning')
            return render_template('auth/login.html')
        
        # Vérifier le mot de passe
        if not verify_password(password, user.password_hash):
            error_msg = handle_failed_login(user)
            flash(error_msg, 'danger')
            
            # Log de tentative échouée
            AuditLog.log_action(
                user_id=user.id,
                action='CONNEXION_ECHOUEE',
                details=f'Tentative de connexion échouée',
                severity='warning',
                ip_address=get_client_ip()
            )
            
            return render_template('auth/login.html')
        
        # Vérifier si le compte est actif
        if not user.is_active:
            flash('Votre compte a été désactivé. Contactez un administrateur.', 'warning')
            return render_template('auth/login.html')
        
        # Connexion réussie
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        login_user(user, remember=remember)
        db.session.commit()
        
        # Log de connexion réussie
        AuditLog.log_action(
            user_id=user.id,
            action='CONNEXION',
            details='Connexion réussie',
            severity='info',
            ip_address=get_client_ip()
        )
        
        flash(f'Bienvenue {user.username} !', 'success')
        
        # Rediriger vers la page demandée ou le dashboard
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Déconnexion"""
    
    if current_user.is_authenticated:
        # Log de déconnexion
        AuditLog.log_action(
            user_id=current_user.id,
            action='DECONNEXION',
            details='Utilisateur déconnecté',
            severity='info',
            ip_address=get_client_ip()
        )
        
        logout_user()
    
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Changement de mot de passe"""
    
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Vérifier le mot de passe actuel
        if not verify_password(current_password, current_user.password_hash):
            flash('Mot de passe actuel incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        # Vérifier que les nouveaux mots de passe correspondent
        if new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
            return render_template('auth/change_password.html')
        
        # Valider la force du nouveau mot de passe
        from app.utils.security import validate_password_strength
        is_strong, errors = validate_password_strength(new_password)
        if not is_strong:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/change_password.html')
        
        # Changer le mot de passe
        current_user.password_hash = hash_password(new_password)
        current_user.password_changed_at = datetime.utcnow()
        db.session.commit()
        
        # Log de l'action
        AuditLog.log_action(
            user_id=current_user.id,
            action='CHANGEMENT_MOT_DE_PASSE',
            details='Mot de passe changé avec succès',
            severity='info',
            ip_address=get_client_ip()
        )
        
        flash('Votre mot de passe a été changé avec succès.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/change_password.html')