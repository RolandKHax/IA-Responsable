# Système IA Responsable - ENSA Béni Mellal

Système d'intelligence artificielle conforme RGPD et éthique IA pour le campus intelligent.

## Table des Matières

- [Caractéristiques](#caractéristiques)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API REST](#api-rest)
- [Sécurité](#sécurité)
- [Conformité RGPD](#conformité-rgpd)
- [Licence](#licence)

## Caractéristiques

### Fonctionnalités IA
- ✅ **Questions & Réponses** - Assistant pédagogique contextuel
- ✅ **Résumés automatiques** - Génération de résumés de cours et documents
- ✅ **Analyse de contenu** - Métriques linguistiques et recommandations
- ✅ **Génération de contenu** - Aide à la rédaction (avec validation humaine)

### Sécurité & Conformité
- **Chiffrement AES-256** - Protection des données sensibles
- **Authentification sécurisée** - Hash SHA-256 avec salt
- **Audit complet** - Traçabilité de toutes les actions
- **Conformité RGPD** - Droits d'accès et d'effacement
- **Validation humaine** - Supervision des réponses IA
- **Détection de données sensibles** - Protection automatique

### Performances
- **Cache intelligent** - Réduction du temps de réponse
- **Monitoring** - Tableaux de bord et statistiques
- **Rate limiting** - Protection contre les abus
- **Base de données SQLite** - Légère et performante

## Architecture

```
ia_system/
├── app/
│   ├── __init__.py              # Initialisation de l'application
│   ├── models.py                # Modèles de base de données
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Routes d'authentification
│   │   ├── main.py              # Routes principales
│   │   ├── admin.py             # Routes d'administration
│   │   └── api.py               # API REST
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py          # Sécurité et chiffrement
│   │   ├── validators.py        # Validation des données
│   │   └── ai_engine.py         # Moteur IA
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # CSS personnalisé
│   │   └── js/
│   │       └── main.js          # JavaScript
│   └── templates/
│       ├── base.html            # Template de base
│       ├── index.html           # Page d'accueil
│       ├── auth/                # Templates authentification
│       ├── user/                # Templates utilisateur
│       ├── admin/               # Templates admin
│       └── legal/               # Templates légaux
├── config.py                    # Configuration
├── requirements.txt             # Dépendances
├── run.py                       # Point d'entrée
└── README.md                    # Documentation
```

## Installation

### Prérequis

- Python 3.8+
- pip
- virtualenv (recommandé)

### Installation rapide

```bash
# 1. Cloner le projet
git clone https://github.com/ensa-bm/ia-responsable.git
cd ia-responsable

# 2. Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
python run.py

# 5. Lancer l'application
python run.py
```

L'application sera accessible sur : http://localhost:5000

### Identifiants par défaut

**À CHANGER EN PRODUCTION !**

- **Username**: `admin`
- **Password**: `admin123`

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Sécurité
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire

# Base de données (optionnel - SQLite par défaut)
DATABASE_URL=sqlite:///ia_system.db
# DATABASE_URL=postgresql://user:pass@localhost/dbname
# DATABASE_URL=mysql://user:pass@localhost/dbname

# Email (optionnel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-application

# Configuration IA
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.7
ENABLE_HUMAN_VALIDATION=True
```

### Configuration de production

Pour déployer en production :

```bash
# 1. Modifier config.py
# Utiliser ProductionConfig

# 2. Utiliser gunicorn
pip install gunicorn

# 3. Lancer avec gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'run:create_app("production")'
```

## Utilisation

### Interface utilisateur

1. **Inscription** : Créez un compte avec consentement RGPD
2. **Connexion** : Authentification sécurisée
3. **Nouvelle demande** : Posez une question ou demandez un résumé
4. **Mes données** : Consultez vos données (droit d'accès RGPD)
5. **Suppression** : Exercez votre droit à l'effacement

### Interface administrateur

Accessible à `/admin/dashboard` pour les utilisateurs admin :

- **Statistiques globales**
- **Gestion des utilisateurs**
- **Validation des réponses IA**
- **Logs d'audit**
- **Gestion du cache**
- **Configuration système**

## 🔌 API REST

### Authentification

Toutes les routes API nécessitent une authentification via session Flask-Login.

### Endpoints principaux

#### Vérifier l'état du système
```bash
GET /api/health
```

Réponse :
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

#### Soumettre une question
```bash
POST /api/ask
Content-Type: application/json

{
  "content": "Explique-moi le RGPD",
  "request_type": "question"
}
```

Réponse :
```json
{
  "success": true,
  "request_id": 123,
  "response": "Le RGPD est...",
  "from_cache": false,
  "processing_time_ms": 850,
  "requires_validation": true,
  "created_at": "2024-01-15T10:35:00Z"
}
```

#### Récupérer les demandes
```bash
GET /api/requests?page=1&per_page=20&type=question
```

#### Soumettre un feedback
```bash
POST /api/request/123/feedback
Content-Type: application/json

{
  "rating": 5,
  "feedback": "Très utile !",
  "is_helpful": true
}
```

#### Statistiques utilisateur
```bash
GET /api/stats
```

### Codes de statut HTTP

- `200` - Succès
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Accès refusé
- `404` - Ressource non trouvée
- `429` - Trop de requêtes (rate limiting)
- `500` - Erreur serveur

## Sécurité

### Mesures implémentées

1. **Authentification**
   - Hachage SHA-256 avec salt
   - Verrouillage après 5 tentatives échouées
   - Expiration de session configurable

2. **Protection des données**
   - Chiffrement AES-256 en base de données
   - TLS/HTTPS obligatoire en production
   - Détection automatique de données sensibles

3. **Protection contre les attaques**
   - CSRF tokens (Flask-WTF)
   - Rate limiting (Flask-Limiter)
   - Sanitization des entrées
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection

4. **Audit et traçabilité**
   - Logs immuables de toutes les actions
   - IP et User-Agent enregistrés
   - Historique des consentements RGPD

## Conformité RGPD

### Droits des utilisateurs

1. **Droit d'accès** (Art. 15)
   - Consultation de toutes les données personnelles
   - Export possible en JSON

2. **Droit d'effacement** (Art. 17)
   - Suppression complète du compte
   - Anonymisation des logs d'audit

3. **Droit à la portabilité** (Art. 20)
   - Export des données en format JSON

4. **Droit d'opposition** (Art. 21)
   - Retrait du consentement possible

### Transparence

- ✅ Politique de confidentialité accessible
- ✅ Conditions d'utilisation claires
- ✅ Consentement explicite à l'inscription
- ✅ Information sur l'utilisation de l'IA
- ✅ Validation humaine des réponses critiques

### Base légale

- Consentement de l'utilisateur (Art. 6.1.a RGPD)
- Intérêt légitime pour l'amélioration du service (Art. 6.1.f RGPD)

## Base de données

### Modèles principaux

- **User** : Utilisateurs et consentements
- **Request** : Demandes et réponses IA
- **AuditLog** : Journalisation complète
- **CacheEntry** : Cache des réponses
- **ConsentLog** : Historique des consentements
- **SystemConfig** : Configuration dynamique

### Migrations

```bash
# Initialiser les migrations
flask db init

# Créer une migration
flask db migrate -m "Description"

# Appliquer les migrations
flask db upgrade
```

## Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-flask

# Lancer les tests
pytest

# Avec couverture
pytest --cov=app
```

## Déploiement

### Docker (optionnel)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:create_app('production')"]
```

### Heroku

```bash
# Créer un Procfile
echo "web: gunicorn 'run:create_app(\"production\")'" > Procfile

# Déployer
git push heroku main
```

## 🛠️ Maintenance

### Nettoyage du cache

```python
# Dans la console Python
from app import create_app, db
from app.models import CacheEntry
from datetime import datetime

app = create_app()
with app.app_context():
    # Supprimer les entrées expirées
    CacheEntry.query.filter(
        CacheEntry.expires_at < datetime.utcnow()
    ).delete()
    db.session.commit()
```

### Backup de la base de données

```bash
# SQLite
cp ia_system.db ia_system_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump dbname > backup_$(date +%Y%m%d).sql
```

## Changelog

### Version 1.0.0 (2024-01-15)
- Première version stable
- Conformité RGPD complète
- Sécurité renforcée
- Interface d'administration
- API REST complète

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est développé dans le cadre du module "Ethique et Droit Numérique" 
à l'ENSA Béni Mellal.

## Auteurs

- **ENSA Béni Mellal** - Module Éthique et Droit du Numérique
- **Encadrant** : Pr. TOUIL

## Support

Pour toute question ou problème :

- Email : support@ensa.ma
- Issues : [GitHub Issues](https://github.com/ensa-bm/ia-responsable/issues)
- Documentation : [Wiki](https://github.com/ensa-bm/ia-responsable/wiki)

---

**Note importante** : Ce système est conçu à des fins pédagogiques et de recherche. 
Pour une utilisation en production, assurez-vous de :
- Changer tous les mots de passe par défaut
- Utiliser HTTPS (TLS/SSL)
- Configurer correctement les variables d'environnement
- Effectuer des tests de sécurité
- Consulter un expert en conformité RGPD
