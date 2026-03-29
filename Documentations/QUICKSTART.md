# ⚡ DÉMARRAGE RAPIDE - 5 Minutes

Guide ultra-rapide pour lancer le système IA Responsable.

## Objectif

Avoir l'application fonctionnelle en **5 minutes**.

---

## 📋 Checklist Rapide

```bash
# ✅ Étape 1 : Python installé ?
python --version  # Doit afficher 3.8+

# ✅ Étape 2 : Télécharger le projet
# (décompresser le ZIP ou git clone)

# ✅ Étape 3 : Ouvrir le terminal dans le dossier
cd ia_responsable

# ✅ Étape 4 : Créer l'environnement virtuel
python -m venv venv

# ✅ Étape 5 : Activer l'environnement
# Windows :
venv\Scripts\activate
# macOS/Linux :
source venv/bin/activate

# ✅ Étape 6 : Installer les dépendances
pip install -r requirements.txt

# ✅ Étape 7 : LANCER !
python run.py
```

---

## Accès

Ouvrir le navigateur :

```
http://localhost:5000
```

**Identifiants par défaut :**
- Username : `admin`
- Password : `admin123`

---

## 🎨 Interface

### Pages Disponibles

1. **Accueil** : http://localhost:5000
2. **Inscription** : http://localhost:5000/auth/register
3. **Connexion** : http://localhost:5000/auth/login
4. **Dashboard** : http://localhost:5000/dashboard
5. **Nouvelle demande** : http://localhost:5000/new-request
6. **Mes données RGPD** : http://localhost:5000/my-data
7. **Admin** : http://localhost:5000/admin/dashboard
8. **API Health** : http://localhost:5000/api/health
9. **À propos** : http://localhost:5000/about

---

## 🔧 Configuration (Optionnel)

### Changer le port

```bash
# Éditer run.py, ligne ~60
app.run(port=5001)  # Au lieu de 5000
```

### Utiliser PostgreSQL

```bash
# 1. Installer PostgreSQL
# 2. Créer la base de données
# 3. Modifier .env :
DATABASE_URL=postgresql://user:pass@localhost:5432/ia_system

# 4. Installer le driver
pip install psycopg2-binary

# 5. Relancer
python run.py
```

---

## Tester les Fonctionnalités

### 1. Créer un compte

```
1. Aller sur http://localhost:5000/auth/register
2. Remplir le formulaire
3. Accepter les CGU RGPD
4. Se connecter
```

### 2. Faire une demande IA

```
1. Aller sur "Nouvelle demande"
2. Choisir le type (Question/Résumé/etc.)
3. Saisir le contenu
4. Soumettre
5. Voir la réponse générée
```

### 3. Accéder aux données RGPD

```
1. Menu "Mes données"
2. Voir toutes vos informations
3. Exporter en JSON
4. Supprimer le compte (si besoin)
```

### 4. Administration

```
1. Se connecter avec admin/admin123
2. Aller sur /admin/dashboard
3. Voir les statistiques
4. Gérer les utilisateurs
5. Valider les réponses IA
```

---

## Commandes Utiles

```bash
# Arrêter l'application
CTRL + C

# Relancer
python run.py

# Voir les logs
tail -f logs/system.log

# Sauvegarder la base de données
cp ia_system.db backups/backup_$(date +%Y%m%d).db

# Créer un nouvel admin
# (Utiliser la console Python)
python
>>> from app import create_app, db
>>> from app.models import User
>>> from app.utils.security import hash_password
>>> app = create_app()
>>> with app.app_context():
...     u = User(username='admin2', email='admin2@ensa.ma', 
...              password_hash=hash_password('password'), 
...              role='admin', is_active=True, consent_given=True)
...     db.session.add(u)
...     db.session.commit()
>>> exit()
```

---

## 🚨 Problèmes Fréquents

### Port 5000 déjà utilisé

```bash
# Solution 1 : Utiliser un autre port
# Éditer run.py, changer le port

# Solution 2 : Tuer le processus
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### ModuleNotFoundError

```bash
# Vérifier que l'environnement est activé
which python  # Doit pointer vers venv/bin/python

# Réinstaller
pip install -r requirements.txt
```

### Erreur de base de données

```bash
# Supprimer et recréer
rm ia_system.db
python run.py
```

---

## Documentation Complète

Pour plus de détails :

- **Installation complète** : Voir `INSTALL.md`
- **Documentation** : Voir `README.md`
- **Structure** : Voir `STRUCTURE_COMPLETE.md`
- **API** : http://localhost:5000/api/health

---

## Prochaines Étapes

Après le démarrage :

1. ✅ **Changer le mot de passe admin**
2. ✅ **Créer des utilisateurs de test**
3. ✅ **Tester toutes les fonctionnalités**
4. ✅ **Personnaliser la configuration**
5. 🚀 **Déployer en production** (voir INSTALL.md)

---

## C'est Tout !

Votre système IA Responsable est opérationnel.

**Bon développement !**

---

## Aide

Besoin d'aide ?

- support@ensa.ma
- Lire INSTALL.md
- Créer une Issue GitHub