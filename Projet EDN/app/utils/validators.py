"""
Validateurs de données
ENSA Béni Mellal - Système IA Responsable
"""

import re
from datetime import datetime


# ==================== VALIDATION D'EMAIL ====================

def is_valid_email(email):
    """Valide un email selon RFC 5322"""
    if not email or len(email) > 254:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_academic_email(email):
    """Valide un email académique (.edu, .ac, etc.)"""
    if not is_valid_email(email):
        return False
    
    academic_domains = ['.edu', '.ac.', '.ensa.', '.university', '.univ']
    return any(domain in email.lower() for domain in academic_domains)


# ==================== VALIDATION DE USERNAME ====================

def is_valid_username(username):
    """
    Valide un nom d'utilisateur
    - 3-80 caractères
    - Alphanumériques, tirets et underscores uniquement
    - Ne commence pas par un chiffre
    """
    if not username or len(username) < 3 or len(username) > 80:
        return False
    
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{2,79}$'
    return bool(re.match(pattern, username))


# ==================== VALIDATION DE TÉLÉPHONE ====================

def is_valid_phone_maroc(phone):
    """Valide un numéro de téléphone marocain"""
    # Formats acceptés:
    # +212612345678
    # 0612345678
    # +212 6 12 34 56 78
    
    # Nettoyer le numéro
    clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Patterns marocains
    patterns = [
        r'^\+212[5-7]\d{8}$',  # Format international
        r'^0[5-7]\d{8}$',      # Format national
    ]
    
    return any(re.match(pattern, clean) for pattern in patterns)


def normalize_phone_maroc(phone):
    """Normalise un numéro marocain au format international"""
    clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    if clean.startswith('0'):
        return '+212' + clean[1:]
    elif clean.startswith('+212'):
        return clean
    elif len(clean) == 9:
        return '+212' + clean
    
    return phone


# ==================== VALIDATION DE TEXTE ====================

def is_valid_text_length(text, min_length=1, max_length=10000):
    """Valide la longueur d'un texte"""
    if not text:
        return False
    
    length = len(text.strip())
    return min_length <= length <= max_length


def contains_only_allowed_chars(text, allowed_pattern=None):
    """Vérifie que le texte ne contient que des caractères autorisés"""
    if allowed_pattern is None:
        # Par défaut: lettres, chiffres, espaces, ponctuation courante
        allowed_pattern = r'^[a-zA-Zàâäéèêëïîôùûüÿç0-9\s\.,;:!?\-\'\"()]+$'
    
    return bool(re.match(allowed_pattern, text))


def has_minimum_words(text, min_words=3):
    """Vérifie qu'un texte contient un nombre minimum de mots"""
    if not text:
        return False
    
    words = text.split()
    return len(words) >= min_words


# ==================== VALIDATION DE DEMANDES IA ====================

def validate_ai_request(content, request_type):
    """
    Valide une demande IA
    Retourne (is_valid, error_message)
    """
    
    # Vérifier que le contenu n'est pas vide
    if not content or not content.strip():
        return False, "Le contenu ne peut pas être vide"
    
    # Vérifier la longueur
    if len(content) < 10:
        return False, "Le contenu doit contenir au moins 10 caractères"
    
    if len(content) > 10000:
        return False, "Le contenu ne doit pas dépasser 10000 caractères"
    
    # Vérifier le type de requête
    valid_types = ['question', 'resume', 'generation', 'analysis']
    if request_type not in valid_types:
        return False, f"Type de requête invalide. Types autorisés: {', '.join(valid_types)}"
    
    # Vérifier qu'il y a des mots (pas que des caractères spéciaux)
    if not has_minimum_words(content, min_words=3):
        return False, "Le contenu doit contenir au moins 3 mots"
    
    # Vérifier qu'il n'y a pas que des majuscules (spam potentiel)
    upper_count = sum(1 for c in content if c.isupper())
    if upper_count > len(content) * 0.7:
        return False, "Trop de majuscules détectées"
    
    # Vérifier la répétition excessive de caractères
    if re.search(r'(.)\1{10,}', content):
        return False, "Répétition excessive de caractères détectée"
    
    return True, None


# ==================== VALIDATION DE FEEDBACK ====================

def validate_rating(rating):
    """Valide une note (1-5)"""
    try:
        rating = int(rating)
        return 1 <= rating <= 5
    except (ValueError, TypeError):
        return False


def validate_feedback_text(feedback):
    """Valide un texte de feedback"""
    if not feedback:
        return True  # Feedback optionnel
    
    if len(feedback) > 1000:
        return False
    
    # Vérifier qu'il n'y a pas de spam évident
    if re.search(r'(http|www\.)', feedback, re.IGNORECASE):
        return False
    
    return True


# ==================== VALIDATION DE DATES ====================

def is_valid_date(date_string, format='%Y-%m-%d'):
    """Valide une date"""
    try:
        datetime.strptime(date_string, format)
        return True
    except (ValueError, TypeError):
        return False


def is_future_date(date_obj):
    """Vérifie si une date est dans le futur"""
    if not isinstance(date_obj, datetime):
        return False
    return date_obj > datetime.utcnow()


def is_date_in_range(date_obj, min_date=None, max_date=None):
    """Vérifie si une date est dans une plage"""
    if not isinstance(date_obj, datetime):
        return False
    
    if min_date and date_obj < min_date:
        return False
    
    if max_date and date_obj > max_date:
        return False
    
    return True


# ==================== VALIDATION DE FICHIERS ====================

def is_allowed_file(filename, allowed_extensions=None):
    """Vérifie si une extension de fichier est autorisée"""
    if allowed_extensions is None:
        allowed_extensions = {'txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg'}
    
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def is_safe_filename(filename):
    """Vérifie qu'un nom de fichier est sûr (pas de caractères dangereux)"""
    # Interdire les caractères de chemin
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    return not any(char in filename for char in dangerous_chars)


# ==================== VALIDATION DE FORMULAIRES ====================

def validate_registration_form(username, email, password, confirm_password, consent):
    """
    Valide un formulaire d'inscription
    Retourne (is_valid, errors_dict)
    """
    errors = {}
    
    # Username
    if not is_valid_username(username):
        errors['username'] = "Nom d'utilisateur invalide (3-80 caractères, alphanumériques uniquement)"
    
    # Email
    if not is_valid_email(email):
        errors['email'] = "Adresse email invalide"
    
    # Password
    from app.utils.security import validate_password_strength
    is_strong, pwd_errors = validate_password_strength(password)
    if not is_strong:
        errors['password'] = pwd_errors
    
    # Confirm password
    if password != confirm_password:
        errors['confirm_password'] = "Les mots de passe ne correspondent pas"
    
    # Consent
    if not consent:
        errors['consent'] = "Vous devez accepter les conditions d'utilisation"
    
    return len(errors) == 0, errors


def validate_login_form(username, password):
    """
    Valide un formulaire de connexion
    Retourne (is_valid, error_message)
    """
    if not username or not password:
        return False, "Nom d'utilisateur et mot de passe requis"
    
    if len(username) < 3 or len(password) < 6:
        return False, "Identifiants invalides"
    
    return True, None


# ==================== VALIDATION SPÉCIFIQUE RGPD ====================

def validate_consent_version(version):
    """Valide une version de consentement"""
    pattern = r'^\d+\.\d+$'  # Format: 1.0, 2.1, etc.
    return bool(re.match(pattern, version))


def validate_data_retention_period(days):
    """Valide une période de rétention de données"""
    try:
        days = int(days)
        return 1 <= days <= 3650  # Max 10 ans
    except (ValueError, TypeError):
        return False


# ==================== VALIDATION ANTI-SPAM ====================

def is_spam_like(text):
    """
    Détecte du contenu potentiellement spam
    Retourne (is_spam, reason)
    """
    if not text:
        return False, None
    
    text_lower = text.lower()
    
    # Trop de liens
    url_count = len(re.findall(r'http[s]?://|www\.', text_lower))
    if url_count > 3:
        return True, "Trop de liens détectés"
    
    # Mots-clés spam courants
    spam_keywords = [
        'click here', 'buy now', 'limited offer', 'act now',
        'viagra', 'casino', 'lottery', 'winner', 'congratulations',
        'free money', 'get rich', 'work from home'
    ]
    
    for keyword in spam_keywords:
        if keyword in text_lower:
            return True, f"Mot-clé spam détecté: {keyword}"
    
    # Répétition excessive du même mot
    words = text_lower.split()
    if words:
        from collections import Counter
        word_counts = Counter(words)
        most_common = word_counts.most_common(1)[0]
        if most_common[1] > len(words) * 0.3:
            return True, "Répétition excessive du même mot"
    
    return False, None


# ==================== VALIDATION MÉTIER ====================

def validate_department(department):
    """Valide un département universitaire"""
    valid_departments = [
        'Informatique',
        'Génie Civil',
        'Génie Électrique',
        'Génie Mécanique',
        'Génie Industriel',
        'Mathématiques Appliquées',
        'Autre'
    ]
    
    return department in valid_departments


def validate_academic_year(year):
    """Valide une année académique"""
    try:
        year = int(year)
        current_year = datetime.now().year
        return current_year - 10 <= year <= current_year + 5
    except (ValueError, TypeError):
        return False