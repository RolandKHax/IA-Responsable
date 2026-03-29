"""
Point d'entrée de l'application
ENSA Béni Mellal - Système IA Responsable

Usage:
    python run.py                    # Mode développement
    python run.py --production       # Mode production
    python run.py --test             # Mode test
"""

import os
import sys
from app import create_app, db

def main():
    """Point d'entrée principal"""
    
    # Déterminer l'environnement
    config_name = 'development'
    
    if '--production' in sys.argv:
        config_name = 'production'
    elif '--test' in sys.argv:
        config_name = 'testing'
    
    # Créer l'application
    app = create_app(config_name)
    
    # Afficher les informations de démarrage
    print("=" * 70)
    print("SYSTÈME IA RESPONSABLE - ENSA BÉNI MELLAL")
    print("=" * 70)
    print(f"Environnement: {config_name.upper()}")
    print(f"Mode debug: {app.debug}")
    print(f"Base de données: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"URL: http://localhost:5000")
    print("=" * 70)
    print("\n Fonctionnalités activées:")
    print("  • Authentification sécurisée")
    print("  • Détection de données sensibles")
    print("  • Validation humaine des réponses IA")
    print("  • Conformité RGPD (droits d'accès et d'effacement)")
    print("  • Journalisation complète (audit trail)")
    print("  • API REST pour intégrations")
    print("  • Rate limiting et protection CSRF")
    print("  • Cache intelligent des réponses")
    print("\n Documentation:")
    print("  • Interface admin: http://localhost:5000/admin/dashboard")
    print("  • API docs: http://localhost:5000/api/health")
    print("  • Politique RGPD: http://localhost:5000/privacy-policy")
    print("\n Identifiants admin par défaut:")
    print("  • Username: admin")
    print("  • Password: admin123")
    print("   CHANGEZ-LES EN PRODUCTION!")
    print("=" * 70)
    print("\n Démarrage du serveur...")
    print("Appuyez sur CTRL+C pour arrêter\n")
    
    # Lancer l'application
    if config_name == 'production':
        # En production, utiliser gunicorn
        print(" Pour la production, utilisez gunicorn:")
        print("   gunicorn -w 4 -b 0.0.0.0:5000 'run:create_app(\"production\")'")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(config_name == 'development')
    )


if __name__ == '__main__':
    main()