"""
Chiffrement des données sensibles
ENSA Béni Mellal - Système IA Responsable
"""

import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import hashlib

# Générer une clé de chiffrement à partir de la clé secrète Flask
def get_cipher_key():
    """Génère une clé Fernet à partir de la clé secrète"""
    secret = os.environ.get('SECRET_KEY', 'default-key')
    key = urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return key


def encrypt_data(text):
    """Chiffre une chaîne de texte"""
    if not text:
        return None
    key = get_cipher_key()
    cipher = Fernet(key)
    return cipher.encrypt(text.encode()).decode()


def decrypt_data(encrypted_text):
    """Déchiffre une chaîne de texte"""
    if not encrypted_text:
        return None
    try:
        key = get_cipher_key()
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception as e:
        return f"[Erreur déchiffrement: {str(e)}]"
