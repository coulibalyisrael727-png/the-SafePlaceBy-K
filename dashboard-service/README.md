# Dashboard Microservice — The SafePlace

## 📋 Vue d'ensemble

Ce microservice est une application Django indépendante qui sert de tableau de bord administratif pour The SafePlace. Il communique avec l'application principale via des API REST.

## 🏗️ Architecture

### Séparation des services
- **Application principale** (port 8000) : Gestion des podcasts, épisodes, donations
- **Dashboard microservice** (port 8001) : Interface d'administration et analytics

### Communication
- Le dashboard fait des appels API vers l'application principale
- Authentification via tokens de session
- CORS configuré pour la communication inter-services

## 🚀 Installation

### Prérequis
- Python 3.11+
- pip

### Installation
```bash
# Cloner le projet
cd dashboard-service

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows
venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur
python manage.py runserver 8001
```

## 🔧 Configuration

### Variables d'environnement
```env
SECRET_KEY=votre-clé-secrète-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MAIN_APP_API_URL=http://localhost:8000/api/v1/
```

### Ports par défaut
- Dashboard : http://localhost:8001
- API principale : http://localhost:8000/api/v1/

## 📊 Fonctionnalités

### Dashboard principal
- Statistiques en temps réel
- Épisodes récents
- Analytics détaillées
- Gestion des donations

### Points d'accès API
- `/` : Dashboard principal
- `/analytics/` : Analytics détaillées
- `/episodes/` : Gestion des épisodes
- `/donations/` : Gestion des donations
- `/health/` : Health check

## 🔐 Sécurité

### Authentification
- Login requis pour accéder au dashboard
- Tokens de session pour l'API
- CORS configuré pour les origines autorisées

### Permissions
- Seuls les utilisateurs authentifiés peuvent accéder aux données
- Validation des entrées API
- Protection contre les injections

## 🌐 API Endpoints

### Données du dashboard
```
GET /api/v1/dashboard-data/
Authorization: Bearer <token>
```

### Analytics
```
GET /api/v1/analytics/?days=30
Authorization: Bearer <token>
```

### Épisodes
```
GET /api/v1/episodes/?page=1&status=published&search=terme
Authorization: Bearer <token>
```

### Donations
```
GET /api/v1/donations/?page=1&status=completed
Authorization: Bearer <token>
```

## 🔄 Déploiement

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  dashboard:
    build: ./dashboard-service
    ports:
      - "8001:8001"
    environment:
      - MAIN_APP_API_URL=http://main-app:8000/api/v1/
    depends_on:
      - main-app
```

## 📝 Développement

### Structure du projet
```
dashboard-service/
├── dashboard/              # Application Django
│   ├── views.py          # Vues du dashboard
│   ├── templates/        # Templates HTML
│   └── models.py        # Modèles (si nécessaire)
├── dashboard_project/     # Configuration du projet
│   ├── settings.py       # Paramètres Django
│   ├── urls.py          # Routes URL
│   └── wsgi.py         # WSGI application
├── static/              # Fichiers statiques
├── media/               # Fichiers médias
├── requirements.txt      # Dépendances Python
└── manage.py           # Script de gestion Django
```

### Ajouter de nouvelles fonctionnalités
1. Créer les vues dans `dashboard/views.py`
2. Ajouter les routes dans `dashboard_project/urls.py`
3. Créer les templates dans `dashboard/templates/`
4. Ajouter les endpoints API dans l'application principale

## 🐛 Debugging

### Problèmes courants
- **Connexion API refusée** : Vérifier CORS et URLs
- **Données vides** : Vérifier l'authentification
- **Erreur 404** : Vérifier les routes URL

### Logs
```bash
# Logs Django
python manage.py runserver --verbosity=2

# Logs détaillés
tail -f logs/django.log
```

## 📈 Monitoring

### Health check
```bash
curl http://localhost:8001/health/
```

### Métriques
- Temps de réponse API
- Taux de succès/échec
- Utilisation mémoire/CPU

## 🔗 Intégration

### Avec l'application principale
1. L'application principale expose les endpoints API
2. Le dashboard consomme ces endpoints
3. Authentification partagée via tokens

### Services externes
- Stripe (pour les donations)
- Analytics (Google Analytics, etc.)
- Stockage (AWS S3, etc.)

## 📞 Support

### Documentation
- API REST : Documentation des endpoints
- Frontend : Guide des composants
- Backend : Architecture et modèles

### Contact
- Issues GitHub : Signaler les bugs
- Documentation : Wiki du projet
