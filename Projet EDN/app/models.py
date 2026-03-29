"""
Modèles de base de données SQLAlchemy
ENSA Béni Mellal - Système IA Responsable
"""

from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Index


class User(UserMixin, db.Model):
    """Modèle utilisateur avec fonctionnalités complètes"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Rôle et permissions
    role = db.Column(db.String(20), default='user')  # 'user', 'admin', 'validator'
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # RGPD et consentements
    consent_given = db.Column(db.Boolean, default=False)
    consent_date = db.Column(db.DateTime)
    consent_version = db.Column(db.String(10), default='1.0')
    data_processing_consent = db.Column(db.Boolean, default=False)
    marketing_consent = db.Column(db.Boolean, default=False)
    
    # Informations personnelles (optionnelles)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime)
    
    # Sécurité
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime)
    
    # Relations
    requests = db.relationship('Request', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convertit en dictionnaire pour JSON"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def has_role(self, role):
        """Vérifie si l'utilisateur a un rôle spécifique"""
        return self.role == role
    
    def is_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'admin'


class Request(db.Model):
    """Modèle pour les demandes IA des utilisateurs"""
    
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Type et contenu
    request_type = db.Column(db.String(50), nullable=False)  # 'question', 'resume', 'generation'
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    
    # Métadonnées IA
    model_used = db.Column(db.String(100))
    prompt_tokens = db.Column(db.Integer)
    completion_tokens = db.Column(db.Integer)
    processing_time_ms = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)
    
    # Validation humaine
    validated_by_human = db.Column(db.Boolean, default=False)
    validator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validation_date = db.Column(db.DateTime)
    validation_comment = db.Column(db.Text)
    validation_status = db.Column(db.String(20))  # 'approved', 'rejected', 'needs_review'
    
    # Sécurité et traçabilité
    contains_sensitive_data = db.Column(db.Boolean, default=False)
    sensitive_data_types = db.Column(db.String(200))
    anonymized = db.Column(db.Boolean, default=False)
    
    # Feedback utilisateur
    user_rating = db.Column(db.Integer)  # 1-5
    user_feedback = db.Column(db.Text)
    is_helpful = db.Column(db.Boolean)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(256))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    error_message = db.Column(db.Text)
    
    # Relation avec le validateur
    validator = db.relationship('User', foreign_keys=[validator_id], backref='validated_requests')
    
    # Index composé pour performances
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_status_created', 'status', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Request {self.id} - {self.request_type}>'
    
    def to_dict(self):
        """Convertit en dictionnaire pour JSON"""
        return {
            'id': self.id,
            'request_type': self.request_type,
            'title': self.title,
            'content': self.content[:100] + '...' if len(self.content) > 100 else self.content,
            'status': self.status,
            'validated': self.validated_by_human,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(db.Model):
    """Journal d'audit pour traçabilité complète"""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    # Action effectuée
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50))  # 'user', 'request', 'system'
    resource_id = db.Column(db.Integer)
    
    # Détails
    details = db.Column(db.Text)
    severity = db.Column(db.String(20), default='info')  # 'info', 'warning', 'error', 'critical'
    
    # Contexte
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(256))
    endpoint = db.Column(db.String(200))
    method = db.Column(db.String(10))
    
    # Métadonnées
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    session_id = db.Column(db.String(100))
    
    # Données avant/après (pour audit complet)
    before_data = db.Column(db.Text)
    after_data = db.Column(db.Text)
    
    __table_args__ = (
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'
    
    @staticmethod
    def log_action(user_id, action, details=None, severity='info', **kwargs):
        """Méthode statique pour créer un log facilement"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            severity=severity,
            **kwargs
        )
        db.session.add(log)
        db.session.commit()
        return log


class CacheEntry(db.Model):
    """Cache pour les réponses IA fréquentes"""
    
    __tablename__ = 'cache_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Clé de cache (hash du contenu)
    cache_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    request_type = db.Column(db.String(50), nullable=False)
    
    # Données en cache
    content_hash = db.Column(db.String(64), nullable=False)
    cached_response = db.Column(db.Text, nullable=False)
    
    # Métadonnées
    hit_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Qualité
    average_rating = db.Column(db.Float)
    is_validated = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<CacheEntry {self.cache_key} - hits: {self.hit_count}>'
    
    def is_expired(self):
        """Vérifie si l'entrée de cache a expiré"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class ConsentLog(db.Model):
    """Historique des consentements RGPD"""
    
    __tablename__ = 'consent_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Type de consentement
    consent_type = db.Column(db.String(50), nullable=False)  # 'data_processing', 'marketing', 'analytics'
    consent_version = db.Column(db.String(10), nullable=False)
    
    # Statut
    consent_given = db.Column(db.Boolean, nullable=False)
    consent_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Contexte
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(256))
    
    # Révocation
    revoked = db.Column(db.Boolean, default=False)
    revoked_date = db.Column(db.DateTime)
    
    def __repr__(self):
        status = 'Accordé' if self.consent_given else 'Refusé'
        return f'<ConsentLog {self.consent_type} - {status}>'


class SystemConfig(db.Model):
    """Configuration système dynamique"""
    
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')  # 'string', 'int', 'bool', 'json'
    description = db.Column(db.Text)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<SystemConfig {self.key}>'
    
    @staticmethod
    def get_value(key, default=None):
        """Récupère une valeur de configuration"""
        config = SystemConfig.query.filter_by(key=key).first()
        if not config:
            return default
        
        # Convertir selon le type
        if config.value_type == 'int':
            return int(config.value)
        elif config.value_type == 'bool':
            return config.value.lower() == 'true'
        elif config.value_type == 'json':
            import json
            return json.loads(config.value)
        return config.value
    
    @staticmethod
    def set_value(key, value, value_type='string', user_id=None):
        """Définit une valeur de configuration"""
        config = SystemConfig.query.filter_by(key=key).first()
        if not config:
            config = SystemConfig(key=key)
        
        config.value = str(value)
        config.value_type = value_type
        config.updated_by = user_id
        
        db.session.add(config)
        db.session.commit()
        return config