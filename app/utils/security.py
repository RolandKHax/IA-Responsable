"""
Utilitaires de sécurité
ENSA Béni Mellal - Système IA Responsable
"""

import hashlib
import secrets
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import session, flash, redirect, url_for, request, abort
from flask_login import current_user


# ==================== HACHAGE DE MOTS DE PASSE ====================

def hash_password(password):
    """
    Hache un mot de passe avec SHA-256 + salt
    En production, utiliser bcrypt ou argon2
    """
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password, stored_hash):
    """Vérifie un mot de passe contre son hash"""
    try:
        salt, pwd_hash = stored_hash.split('$')
        test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return secrets.compare_digest(pwd_hash, test_hash)
    except:
        return False


def generate_strong_password(length=16):
    """Génère un mot de passe fort"""
    import string
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))


# ==================== VALIDATION DE MOTS DE PASSE ====================

def validate_password_strength(password):
    """
    Valide la force d'un mot de passe
    Retourne (is_valid, errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Le mot de passe doit contenir au moins une majuscule")
    
    if not re.search(r'[a-z]', password):
        errors.append("Le mot de passe doit contenir au moins une minuscule")
    
    if not re.search(r'\d', password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial")
    
    # Vérifier les mots de passe communs
    common_passwords = ['password', '123456', 'qwerty', 'admin', '12345678']
    if password.lower() in common_passwords:
        errors.append("Ce mot de passe est trop courant")
    
    return len(errors) == 0, errors


# ==================== SANITIZATION ====================

def sanitize_input(text, max_length=1000):
    """Nettoie une entrée utilisateur"""
    if not text:
        return ""
    
    # Limiter la longueur
    text = text[:max_length]
    
    # Supprimer les caractères de contrôle
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Encoder les caractères HTML dangereux
    text = (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;'))
    
    return text.strip()


def sanitize_sql_identifier(identifier):
    """Nettoie un identifiant SQL (nom de table, colonne, etc.)"""
    # Autoriser uniquement alphanumériques et underscore
    return re.sub(r'[^a-zA-Z0-9_]', '', identifier)


# ==================== DÉTECTION DE DONNÉES SENSIBLES ====================

SENSITIVE_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone_maroc': r'\b(?:\+212|0)[5-7]\d{8}\b',
    'phone_international': r'\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,9}',
    'cin': r'\b[A-Z]{1,2}\d{5,7}\b',
    'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
    'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b',
    'carte_credit': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    'carte_bancaire': r'\b\d{16}\b',
    'cvv': r'\b\d{3,4}\b',
    'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
}

SENSITIVE_KEYWORDS = [
    # Informations personnelles
    'mot de passe', 'password', 'secret', 'clé', 'token',
    'confidentiel', 'privé', 'personnel',
    
    # Données de santé
    'santé', 'maladie', 'médical', 'diagnostic', 'traitement',
    'handicap', 'pathologie', 'symptôme', 'médicament',
    
    # Données sensibles RGPD
    'religion', 'religieux', 'politique', 'syndical',
    'orientation sexuelle', 'identité de genre',
    'origine ethnique', 'race',
    'casier judiciaire', 'infraction', 'condamnation',
    
    # Données financières
    'salaire', 'revenu', 'compte bancaire', 'dette',
]


def detect_sensitive_data(text):
    """
    Détecte la présence de données sensibles
    Retourne (has_sensitive, detected_types, details)
    """
    detected_types = set()
    details = []
    
    if not text:
        return False, [], []
    
    text_lower = text.lower()
    
    # Vérification des patterns regex
    for data_type, pattern in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            detected_types.add(data_type)
            # Ne pas inclure les données réelles dans les détails (sécurité)
            details.append(f"Type détecté : {data_type} ({len(matches)} occurrence(s))")
    
    # Vérification des mots-clés
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in text_lower:
            detected_types.add('keyword_sensitive')
            details.append(f"Mot-clé sensible : {keyword}")
    
    has_sensitive = len(detected_types) > 0
    
    return has_sensitive, list(detected_types), details


def anonymize_text(text):
    """
    Anonymise un texte en masquant les données sensibles
    """
    anonymized = text
    
    # Masquer les emails
    anonymized = re.sub(
        SENSITIVE_PATTERNS['email'],
        '[EMAIL ANONYMISÉ]',
        anonymized,
        flags=re.IGNORECASE
    )
    
    # Masquer les téléphones
    anonymized = re.sub(
        SENSITIVE_PATTERNS['phone_maroc'],
        '[TÉLÉPHONE ANONYMISÉ]',
        anonymized
    )
    
    # Masquer les cartes bancaires
    anonymized = re.sub(
        SENSITIVE_PATTERNS['carte_credit'],
        '[CARTE BANCAIRE ANONYMISÉE]',
        anonymized
    )
    
    # Masquer les CINs
    anonymized = re.sub(
        SENSITIVE_PATTERNS['cin'],
        '[CIN ANONYMISÉ]',
        anonymized,
        flags=re.IGNORECASE
    )
    
    return anonymized


# ==================== DÉCORATEURS DE SÉCURITÉ ====================

def role_required(role):
    """Décorateur pour restreindre l'accès par rôle"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Veuillez vous connecter.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role != role and current_user.role != 'admin':
                flash('Accès non autorisé.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Décorateur pour restreindre l'accès aux admins"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Accès réservé aux administrateurs.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def check_account_locked(user):
    """Vérifie si un compte est verrouillé"""
    if user.account_locked_until:
        if datetime.utcnow() < user.account_locked_until:
            remaining = user.account_locked_until - datetime.utcnow()
            minutes = int(remaining.total_seconds() / 60)
            return True, f"Compte verrouillé. Réessayez dans {minutes} minutes."
        else:
            # Déverrouiller le compte
            user.account_locked_until = None
            user.failed_login_attempts = 0
    
    return False, None


def handle_failed_login(user):
    """Gère les tentatives de connexion échouées"""
    from app import db
    
    user.failed_login_attempts += 1
    
    # Verrouiller après 5 tentatives
    if user.failed_login_attempts >= 5:
        user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        return "Trop de tentatives échouées. Compte verrouillé pour 30 minutes."
    
    db.session.commit()
    remaining = 5 - user.failed_login_attempts
    return f"Identifiants incorrects. {remaining} tentative(s) restante(s)."


# ==================== TOKENS SÉCURISÉS ====================

def generate_token(length=32):
    """Génère un token sécurisé"""
    return secrets.token_urlsafe(length)


def verify_token_age(token_date, max_age_hours=24):
    """Vérifie si un token n'est pas expiré"""
    if not token_date:
        return False
    
    age = datetime.utcnow() - token_date
    return age < timedelta(hours=max_age_hours)


# ==================== VALIDATION IP ====================

def is_valid_ip(ip):
    """Valide une adresse IP"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def get_client_ip():
    """Récupère l'IP réelle du client (même derrière un proxy)"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


# ==================== JOURNALISATION SÉCURISÉE ====================

def log_security_event(event_type, user_id=None, details=None, severity='warning'):
    """Journalise un événement de sécurité"""
    from app.models import AuditLog
    from app import db
    
    log = AuditLog(
        user_id=user_id,
        action=f'SECURITY_{event_type}',
        details=details,
        severity=severity,
        ip_address=get_client_ip(),
        user_agent=request.headers.get('User-Agent')
    )
    
    db.session.add(log)
    db.session.commit()
    
    # Log également dans le fichier système
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Security Event [{event_type}]: {details}")


# ==================== PROTECTION CSRF ====================

def generate_csrf_token():
    """Génère un token CSRF"""
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_token()
    return session['csrf_token']


def validate_csrf_token(token):
    """Valide un token CSRF"""
    return token == session.get('csrf_token')