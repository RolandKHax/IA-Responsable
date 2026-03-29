# Système IA Responsable — ENSA Béni Mellal

> Projet pédagogique — Module Éthique et Droit du Numérique
> Filière Intelligence Artificielle et Cybersécurité
> Encadrant : Pr. TOUIL | Université Sultan Moulay Slimane

Application web Flask implémentant un assistant IA conforme au RGPD, avec gouvernance éthique, supervision humaine et traçabilité complète.

---

## Démarrage rapide

```bash
cd Projet_EDN
venv/bin/python3 run.py
```

Ouvrir **http://localhost:5000**

| Compte | Identifiant | Mot de passe |
|--------|-------------|--------------|
| Admin  | `admin`     | `admin123`   |

> Changer ces identifiants avant tout déploiement.

---

## Structure du projet

```
Projet_EDN/
├── app/
│   ├── __init__.py          # Factory Flask, extensions, création admin
│   ├── models.py            # Modèles BDD (User, Request, AuditLog, ...)
│   ├── routes/
│   │   ├── auth.py          # Inscription, connexion, déconnexion
│   │   ├── main.py          # Dashboard, nouvelle demande, mes données
│   │   ├── admin.py         # Administration, validation, logs
│   │   └── api.py           # API REST JSON
│   ├── utils/
│   │   ├── ai_engine.py     # Moteur IA (rule-based) + détecteur de stress
│   │   ├── security.py      # Hash mots de passe, détection données sensibles
│   │   └── validators.py    # Validation formulaires et contenu
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/           # Jinja2 — Tailwind CSS + Alpine.js
│       ├── base.html
│       ├── index.html
│       ├── auth/
│       ├── user/
│       ├── admin/
│       ├── legal/
│       └── errors/
├── config.py                # DevelopmentConfig / ProductionConfig
├── requirements.txt
├── run.py                   # Point d'entrée
└── instance/
    └── ia_system.db         # Base de données SQLite (auto-créée)
```

---

## Installation (environnement existant)

Le venv est déjà configuré. Si vous repartez de zéro :

```bash
cd Projet_EDN

# Créer le venv
python3 -m venv venv

# Installer les dépendances
venv/bin/pip install -r requirements.txt

# Lancer
venv/bin/python3 run.py
```

> **Note Linux :** Ne pas utiliser `pip install` global (bloqué par PEP 668).
> Toujours passer par `venv/bin/pip` et `venv/bin/python3`.

---

## Fonctionnalités

### Pour les utilisateurs
| Fonctionnalité | Route | Description |
|----------------|-------|-------------|
| Nouvelle demande | `/new-request` | Question, résumé, génération, analyse de texte |
| Voir une réponse | `/request/<id>` | Réponse IA + statut de validation + feedback |
| Mes données | `/my-data` | Accès RGPD — export JSON, suppression compte |
| Tableau de bord | `/dashboard` | Historique des demandes |

### Pour les administrateurs (`/admin/`)
| Fonctionnalité | Description |
|----------------|-------------|
| Dashboard | Statistiques globales, activité récente |
| Gestion utilisateurs | Activer / désactiver des comptes |
| Validation IA | Approuver ou rejeter les réponses générées |
| Logs d'audit | Traçabilité complète de toutes les actions |
| Cache | Statistiques et nettoyage du cache |

### API REST (`/api/`)
```
GET  /api/health              État du système
POST /api/ask                 Soumettre une demande IA (JSON)
GET  /api/requests            Liste des demandes de l'utilisateur
GET  /api/request/<id>        Détail d'une demande
POST /api/request/<id>/feedback  Envoyer un feedback
GET  /api/stats               Statistiques utilisateur
GET  /api/model-info          Informations sur le modèle IA
```

---

## Architecture technique

### Stack
- **Backend** : Python 3.11, Flask 3.0, SQLAlchemy 2.0, SQLite
- **Frontend** : Tailwind CSS (CDN), Alpine.js (CDN), Jinja2
- **Sécurité** : Flask-WTF (CSRF), Flask-Limiter (rate limiting), Flask-Login

### Modèles de données
| Modèle | Rôle |
|--------|------|
| `User` | Compte, rôle, consentement RGPD, verrouillage |
| `Request` | Demandes IA, réponses, statut de validation |
| `AuditLog` | Journal immuable de toutes les actions |
| `CacheEntry` | Cache des réponses (expiration 30 jours) |
| `ConsentLog` | Historique versionné des consentements |
| `SystemConfig` | Configuration dynamique clé/valeur |

### Moteur IA
Le moteur actuel est **rule-based** (pas de LLM externe). Il gère 4 types de demandes :
- `question` — classification de la question + réponse structurée
- `resume` — statistiques du texte (mots, phrases, temps de lecture)
- `generation` — squelette de contenu avec avertissements éthiques
- `analysis` — métriques linguistiques (richesse lexicale, longueur moyenne)

Pour intégrer un vrai LLM (OpenAI, Claude, Ollama...), remplacer `_generate_response()` dans `app/utils/ai_engine.py`.

---

## Conformité RGPD

### Droits implémentés
| Droit | Article | Implémentation |
|-------|---------|----------------|
| Information | Art. 13-14 | Politique de confidentialité + notice à l'inscription |
| Accès | Art. 15 | `/my-data` — consultation et export JSON |
| Rectification | Art. 16 | Changement de mot de passe |
| Effacement | Art. 17 | `/delete-account` — suppression complète + anonymisation des logs |
| Opposition | Art. 21 | Retrait de consentement possible |
| Ne pas faire l'objet d'une décision automatisée | Art. 22 | Validation humaine obligatoire |

### Base légale
- Consentement explicite recueilli à l'inscription (Art. 6.1.a)
- Versionnage des consentements enregistré dans `ConsentLog`

### Mesures de sécurité
- Mots de passe hachés SHA-256 + salt
- Protection CSRF sur tous les formulaires POST
- Rate limiting par route (ex : 5 inscriptions/heure, 20 demandes IA/heure)
- Détection et blocage des données sensibles (email, téléphone, CIN, IBAN...)
- Verrouillage de compte après 5 échecs de connexion
- Journalisation de toutes les actions avec IP et User-Agent

---

## Gouvernance éthique

- **Supervision humaine** : toute réponse IA est marquée "en attente" jusqu'à validation admin
- **Transparence** : les utilisateurs sont informés de l'usage de l'IA à chaque étape
- **Traçabilité** : audit log complet, non modifiable, avec niveaux de sévérité
- **Détecteur de stress** : analyse les messages pour détecter les étudiants en difficulté
- **Disclaimers** : chaque réponse IA inclut des avertissements sur ses limites

---

## Variables d'environnement (optionnel)

Créer un fichier `.env` à la racine de `Projet_EDN/` :

```env
SECRET_KEY=changez-cette-cle-en-production
DATABASE_URL=sqlite:///ia_system.db
FLASK_ENV=development
```

---

## Projet académique

Ce système a été développé dans le cadre du module **Éthique et Droit du Numérique** à l'ENSA Béni Mellal. Il vise à démontrer concrètement :

1. L'application des principes RGPD (licéité, minimisation, limitation, sécurité, responsabilisation)
2. La mise en place d'une gouvernance IA éthique
3. L'identification et la réduction des risques algorithmiques
4. La supervision humaine des systèmes automatisés
