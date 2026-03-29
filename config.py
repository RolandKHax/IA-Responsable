"""
Configuration de l'application Flask
ENSA Béni Mellal - Système IA Responsable
"""

import os
from datetime import timedelta

class Config:
    """Configuration de base"""
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ia_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # True pour debug SQL
    
    # Session
    SESSION_COOKIE_SECURE = True  # HTTPS uniquement en production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Upload de fichiers
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging
    LOG_FILE = 'logs/system.log'
    LOG_LEVEL = 'INFO'
    
    # RGPD
    DATA_RETENTION_DAYS = 365
    CONSENT_REQUIRED = True
    
    # IA Configuration
    AI_MAX_TOKENS = 1000
    AI_TEMPERATURE = 0.7
    ENABLE_HUMAN_VALIDATION = True
    
    # Emails (optionnel)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False  # HTTP en développement


class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    TESTING = False
    
    # Sécurité renforcée
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Base de données production (PostgreSQL recommandé)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """Configuration de test"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False


# Dictionnaire de configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}