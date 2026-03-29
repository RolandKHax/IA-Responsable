"""
Initialisation de l'application Flask
ENSA Béni Mellal - Système IA Responsable
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()


def create_app(config_name='default'):
    """Factory pattern pour créer l'application"""
    
    app = Flask(__name__)
    
    # Charger la configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    
    # Configuration du login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'warning'
    
    # Configuration du logging
    configure_logging(app)
    
    # Enregistrer les blueprints
    register_blueprints(app)
    
    # Enregistrer les gestionnaires d'erreurs
    register_error_handlers(app)
    
    # Contexte du template
    register_template_context(app)
    
    # Créer les dossiers nécessaires
    create_directories(app)
    
    # Initialiser la base de données
    with app.app_context():
        db.create_all()
        init_default_data()
    
    return app


def configure_logging(app):
    """Configure le système de logging"""
    
    if not app.debug and not app.testing:
        # Créer le dossier logs s'il n'existe pas
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Handler pour fichier avec rotation
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10 MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        app.logger.info('Application IA Responsable démarrée')


def register_blueprints(app):
    """Enregistre tous les blueprints"""
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')


def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs personnalisés"""
    
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Erreur serveur: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return render_template('errors/429.html'), 429


def register_template_context(app):
    """Ajoute des variables globales aux templates"""
    
    from datetime import datetime
    
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.utcnow(),
            'app_name': 'IA Responsable - ENSA BM',
            'app_version': '1.0.0'
        }


def create_directories(app):
    """Crée les dossiers nécessaires"""
    
    directories = ['logs', 'uploads', 'backups']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def init_default_data():
    """Initialise les données par défaut"""
    
    from app.models import User
    from app.utils.security import hash_password
    
    # Créer un admin par défaut si inexistant
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=hash_password('admin123'),
            email='admin@ensa.ma',
            role='admin',
            consent_given=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Administrateur créé : admin / admin123")


@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur pour Flask-Login"""
    from app.models import User
    return User.query.get(int(user_id))