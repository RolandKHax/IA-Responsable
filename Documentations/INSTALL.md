# Guide d'Installation - IA Responsable ENSA

Guide complet pour installer et déployer le système IA Responsable.

## Table des matières

- [Prérequis](#prérequis)
- [Installation locale](#installation-locale)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Déploiement Production](#déploiement-production)
- [Dépannage](#dépannage)

## ✅ Prérequis

### Logiciels requis

- **Python** 3.8 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **virtualenv** (recommandé)
- **Git** (pour cloner le projet)

### Systèmes supportés

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, CentOS, etc.)

### Vérification des prérequis

```bash
# Vérifier Python
python --version  # Doit afficher Python 3.8+

# Vérifier pip
pip --version

# Vérifier Git
git --version
```

## Installation locale

### Étape 1 : Cloner le projet

```bash
# Cloner depuis GitHub
git clone https://github.com/ensa-bm/ia-responsable.git
cd ia-responsable

# OU télécharger et extraire le ZIP
# puis naviguer dans le dossier
```

### Étape 2 : Créer un environnement virtuel

#### Sur Windows

```cmd
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
venv\Scripts\activate
```

#### Sur macOS/Linux

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate
```

Votre invite de commande devrait maintenant afficher `(venv)` au début.

### Étape 3 : Installer les dépendances

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer toutes les dépendances
pip install -r requirements.txt
```

Cette commande installe :
- Flask et extensions
- SQLAlchemy (ORM)
- Flask-Login (authentification)
- Flask-Limiter (rate limiting)
- Et toutes les autres dépendances

### Étape 4 : Configuration initiale

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos paramètres
# Sur Windows: notepad .env
# Sur macOS/Linux: nano .env
```

**Configuration minimale requise :**

```env
SECRET_KEY=votre-cle-secrete-unique
DATABASE_URL=sqlite:///ia_system.db
DEBUG=True
```

**⚠️ Important :** Générez une clé secrète forte :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Étape 5 : Initialiser la base de données

```bash
# Lancer l'application une première fois
# Cela créera automatiquement la base de données
python run.py
```

La base de données SQLite `ia_system.db` sera créée automatiquement.

### Étape 6 : Accéder à l'application

Ouvrez votre navigateur et allez sur :

```
http://localhost:5000
```

**Identifiants admin par défaut :**
- Username: `admin`
- Password: `admin123`

**⚠️ CHANGEZ-LES IMMÉDIATEMENT !**

## ⚙️ Configuration avancée

### Structure des dossiers créés automatiquement

```
ia_system/
├── logs/              # Logs du système
├── uploads/           # Fichiers uploadés
├── backups/           # Sauvegardes
└── ia_system.db       # Base de données SQLite
```

### Configuration PostgreSQL (Recommandé pour production)

1. Installer PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS (avec Homebrew)
brew install postgresql
```

2. Créer la base de données

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base et l'utilisateur
CREATE DATABASE ia_system;
CREATE USER ia_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE ia_system TO ia_user;
\q
```

3. Modifier `.env`

```env
DATABASE_URL=postgresql://ia_user:votre_mot_de_passe@localhost:5432/ia_system
```

4. Installer le driver

```bash
pip install psycopg2-binary
```

### Configuration Email (Optionnel)

Pour activer les notifications par email :

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-application
```

**Note Gmail :** Utilisez un mot de passe d'application, pas votre mot de passe principal.

## Lancement

### Mode développement

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# OU
venv\Scripts\activate      # Windows

# Lancer l'application
python run.py
```

L'application sera accessible sur `http://localhost:5000`

### Mode production (avec Gunicorn)

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer avec 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 'run:create_app("production")'
```

## Déploiement Production

### Option 1 : Heroku

1. Créer un compte sur [Heroku](https://heroku.com)

2. Installer Heroku CLI

3. Déployer

```bash
# Se connecter
heroku login

# Créer l'application
heroku create votre-app-ia

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Configurer les variables
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_ENV=production

# Déployer
git push heroku main

# Ouvrir l'app
heroku open
```

**Fichiers nécessaires (déjà inclus) :**
- `Procfile` : `web: gunicorn 'run:create_app("production")'`
- `requirements.txt`

### Option 2 : VPS (DigitalOcean, AWS, etc.)

1. Créer un serveur Ubuntu 20.04+

2. Se connecter en SSH

```bash
ssh root@votre-ip
```

3. Installer les dépendances

```bash
# Mettre à jour le système
apt update && apt upgrade -y

# Installer Python et dépendances
apt install python3-pip python3-venv nginx postgresql -y

# Créer un utilisateur pour l'app
adduser iaapp
su - iaapp
```

4. Cloner et installer

```bash
# Cloner le projet
git clone https://github.com/ensa-bm/ia-responsable.git
cd ia-responsable

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install gunicorn
```

5. Configurer PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE ia_system;
CREATE USER ia_user WITH PASSWORD 'mot_de_passe_fort';
GRANT ALL PRIVILEGES ON DATABASE ia_system TO ia_user;
\q
```

6. Créer un fichier `.env`

```bash
nano .env
```

Contenu :

```env
SECRET_KEY=generer_une_cle_forte
DATABASE_URL=postgresql://ia_user:mot_de_passe@localhost:5432/ia_system
FLASK_ENV=production
DEBUG=False
SESSION_COOKIE_SECURE=True
```

7. Créer un service systemd

```bash
sudo nano /etc/systemd/system/iaapp.service
```

Contenu :

```ini
[Unit]
Description=IA Responsable - ENSA
After=network.target

[Service]
User=iaapp
WorkingDirectory=/home/iaapp/ia-responsable
Environment="PATH=/home/iaapp/ia-responsable/venv/bin"
ExecStart=/home/iaapp/ia-responsable/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 'run:create_app("production")'

[Install]
WantedBy=multi-user.target
```

8. Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/iaapp
```

Contenu :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

9. Activer et démarrer

```bash
# Activer le site Nginx
sudo ln -s /etc/nginx/sites-available/iaapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Démarrer le service
sudo systemctl start iaapp
sudo systemctl enable iaapp
sudo systemctl status iaapp
```

10. Installer SSL (HTTPS) avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d votre-domaine.com
```

### Option 3 : Docker

```bash
# Construire l'image
docker build -t ia-responsable .

# Lancer le conteneur
docker run -d -p 5000:5000 \
  -e SECRET_KEY=votre_cle \
  -e DATABASE_URL=postgresql://... \
  --name iaapp \
  ia-responsable
```

## 🔧 Dépannage

### Problème : "ModuleNotFoundError"

**Solution :**

```bash
# Vérifier que l'environnement virtuel est activé
which python  # Doit pointer vers venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : "Unable to open database file"

**Solution :**

```bash
# Créer le dossier si nécessaire
mkdir -p instance

# Vérifier les permissions
chmod 755 .
```

### Problème : Port 5000 déjà utilisé

**Solution :**

```bash
# Utiliser un autre port
python run.py --port 5001

# OU tuer le processus utilisant le port 5000
# Sur Linux/macOS
lsof -ti:5000 | xargs kill -9

# Sur Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Problème : Erreur de connexion PostgreSQL

**Solution :**

```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql

# Tester la connexion
psql -U ia_user -d ia_system -h localhost

# Vérifier l'URL dans .env
DATABASE_URL=postgresql://user:password@host:port/database
```

## Commandes utiles

```bash
# Sauvegarder la base de données
cp ia_system.db backups/ia_system_$(date +%Y%m%d).db

# Voir les logs en temps réel
tail -f logs/system.log

# Créer un nouvel administrateur
python -c "from app import create_app, db; from app.models import User; from app.utils.security import hash_password; app = create_app(); app.app_context().push(); u = User(username='admin2', email='admin2@ensa.ma', password_hash=hash_password('password'), role='admin', is_active=True, consent_given=True); db.session.add(u); db.session.commit()"

# Vider le cache
rm -rf __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +

# Mettre à jour l'application
git pull origin main
pip install -r requirements.txt
sudo systemctl restart iaapp
```

## Support

Pour toute question ou problème :

- Email : support@ensa.ma
- Issues : [GitHub Issues](https://github.com/ensa-bm/ia-responsable/issues)
- Documentation : [Wiki](https://github.com/ensa-bm/ia-responsable/wiki)

---

**Bonne installation ! 🚀**