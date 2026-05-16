# [SAFE] The SafePlace by K - Architecture Découplée

Plateforme de podcast chrétienne moderne utilisant une architecture microservices/découplée. Le backend gère la logique métier et les APIs, tandis que le tableau de bord est un service indépendant optimisé pour un hébergement séparé (ex: Netlify).

## [LIST] Architecture Système

```
      ┌──────────────────────────────────┐
      │      Dashboard (Frontend)        │
      │      Hébergé sur Netlify         │
      └──────────────┬───────────────────┘
                     │
                     │ Appels API REST
                     ▼
      ┌──────────────────────────────────┐
      │      Backend (Django App)        │
      │      Hébergé sur Cloud / VPS     │
      └──────────────┬───────────────────┘
                     │
    ┌────────────────┼────────────────┬──────────────┐
    │                │                │              │
┌───▼──────┐   ┌────▼────┐      ┌───▼──────┐  ┌───▼──────┐
│PostgreSQL│   │  Redis  │      │ Celery   │  │ Celery   │
│   DB     │   │  Cache  │      │ Worker   │  │  Beat    │
└──────────┘   └─────────┘      └──────────┘  └──────────┘
```

## [ROCKET] Composants du Projet

1. **`podcastSafe` (Backend)** : Application Django 6.0+ gérant les podcasts, vidéos, lives et l'API REST.
2. **`dashboard-service` (Frontend)** : Interface d'administration indépendante communicant via API.
3. **Services de données** : PostgreSQL (Données), Redis (Cache/Broker).
4. **Traitement de fond** : Celery & Celery Beat pour les tâches planifiées.

## [INSTALL] Installation Rapide (Local)

Le projet est conçu pour être lancé via Docker pour le développement local complet (Backend + Dashboard).

1. **Cloner le projet**
```bash
git clone https://github.com/coulibalyisrael727-png/the-SafePlaceBy-K.git
cd the-SafePlaceBy-K
```

2. **Configurer l'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos configurations (clés Stripe, Wave, etc.)
```

3. **Démarrer tous les services**
```bash
docker-compose up -d
```
Ceci lance le backend (8000), le dashboard (8001), PostgreSQL, Redis et Nginx.

4. **Initialiser la base de données**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Usage

### Pour les Utilisateurs
1. **Accéder au site** : `http://localhost` (via Nginx) ou `http://localhost:8000` (Direct Django).
2. **Explorer** : Navigation fluide entre podcasts, vidéos et lives.

### Pour les Administrateurs (Dashboard)
Le tableau de bord est une application indépendante.
1. **Local** : Accédez à `http://localhost:8001` ou via la route `/dashboard/` du site principal qui vous redirigera.
2. **Production** : Accédez à l'URL Netlify fournie lors du déploiement.
3. **Actions** : Publiez des épisodes, gérez les lives, suivez les analytics et les donations.

### Commandes de Base

```bash
# Voir les logs
docker-compose logs -f

# Redémarrer les services
docker-compose restart

# Accéder au shell Django
docker-compose exec web python manage.py shell

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser
```

## API

### Base URL
```
http://localhost/api/
```

### Endpoints Disponibles

#### Épisodes
```http
GET    /api/episodes/              # Liste tous les épisodes
GET    /api/episodes/{id}/         # Détails d'un épisode
POST   /api/episodes/              # Créer un épisode (admin)
PUT    /api/episodes/{id}/         # Modifier un épisode (admin)
DELETE /api/episodes/{id}/         # Supprimer un épisode (admin)
```

#### Live Streams
```http
GET    /api/livestreams/           # Liste tous les lives
GET    /api/livestreams/{id}/      # Détails d'un live
POST   /api/livestreams/           # Créer un live (admin)
PUT    /api/livestreams/{id}/      # Modifier un live (admin)
DELETE /api/livestreams/{id}/      # Supprimer un live (admin)
```

#### Donations
```http
POST   /api/donation/create/        # Créer une donation
POST   /api/donation/confirm/       # Confirmer une donation
GET    /api/donation/list/          # Liste des donations (admin)
```

#### Abonnements
```http
POST   /api/subscription/create/     # Créer un abonnement
GET    /api/subscription/list/       # Liste des abonnés (admin)
```

#### Webhooks Stripe
```http
POST   /api/stripe/webhook/         # Webhook Stripe
```

### Exemples d'Utilisation

#### Créer une Donation
```bash
curl -X POST http://localhost/api/donation/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jean Dupont",
    "email": "jean@example.com",
    "amount": 25.00,
    "message": "Merci pour votre travail"
  }'
```

#### Lister les Épisodes
```bash
curl -X GET http://localhost/api/episodes/ \
  -H "Content-Type: application/json"
```

#### Créer un Abonnement
```bash
curl -X POST http://localhost/api/subscription/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean@example.com",
    "notify_podcasts": true,
    "notify_live": true,
    "notify_videos": false
  }'
```

### Format des Réponses

**Succès (200 OK)**
```json
{
  "success": true,
  "data": {...}
}
```

**Erreur (400/500)**
```json
{
  "success": false,
  "error": "Message d'erreur"
}
```

### Authentification API

Pour les endpoints protégés, inclure le token:
```bash
curl -X GET http://localhost/api/episodes/ \
  -H "Authorization: Token votre-token-api"
```

## [PAGE] Configuration Importante

### Stripe

1. Créer un compte sur https://stripe.com
2. Récupérer les clés API (Test et Production)
3. Ajouter les clés à `.env`

```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Email

Pour les notifications et les confirmations:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

### Base de Données

L'application utilise PostgreSQL par défaut:

```env
DB_NAME=safeplace_db
DB_USER=safeplace_user
DB_PASSWORD=votre_mot_de_passe_securise
DB_HOST=db
DB_PORT=5432
```

## [KEY] Authentification

Le dashboard est accessible **uniquement au propriétaire du site** (superutilisateur).

Pour accéder:
1. Se connecter sur `/admin`
2. Vérifier que votre compte est un superutilisateur
3. Accéder à `/studio/`

## [CARD] Système de Paiement

### Fonctionnalités

- [CHECK] Donations via Stripe
- [CHECK] Confirmation automatique
- [CHECK] Emails de remerciement
- [CHECK] Webhooks Stripe (optionnel)
- [CHECK] Historique des donations

### Implémentation

Les donations sont traitées via des endpoints API:

```bash
POST /api/donation/create/
# Corps:
{
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "amount": 25.00,
  "message": "Merci pour votre travail"
}

POST /api/donation/confirm/
# Corps:
{
  "donation_id": 1
}
```

## [LIST] Pages Implémentées

- [CHECK] Accueil avec épisodes recommandés
- [CHECK] Galerie de podcasts
- [CHECK] Détails d'épisode
- [CHECK] Live streams
- [CHECK] Dashboard admin (propriétaire uniquement)
- [CHECK] Publication d'épisodes
- [CHECK] Gestion des lives
- [CHECK] Gestion des donations
- [CHECK] Page de contact (emails fonctionnels)
- [CHECK] À propos
- [CHECK] Page d'accès refusé

## [TOOLS] Commandes Utiles

### Gestion Docker

```bash
# Voir les logs
docker-compose logs -f web

# Accéder au shell Django
docker-compose exec web python manage.py shell

# Exécuter des commandes
docker-compose exec web python manage.py [commande]

# Redémarrer les services
docker-compose restart

# Arrêter tous les services
docker-compose down

# Supprimer les volumes (données)
docker-compose down -v
```

### Gestion de Base de Données

```bash
# Accès direct à PostgreSQL
docker-compose exec db psql -U safeplace_user -d safeplace_db

# Sauvegarde
docker-compose exec db pg_dump -U safeplace_user safeplace_db > backup.sql

# Restauration
docker-compose exec -T db psql -U safeplace_user safeplace_db < backup.sql
```

### Celery

```bash
# Voir les tâches Celery
docker-compose logs -f celery

# Purger les tâches
docker-compose exec celery celery -A Safeplace purge

# Vérifier le statut
docker-compose exec celery celery -A Safeplace inspect active
```

## [SECURE] Sécurité

### Production

Avant de déployer en production:

1. **Générer une nouvelle SECRET_KEY**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Activer HTTPS**:
```bash
# Générer des certificats SSL
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/key.pem -out ssl/cert.pem
```

3. **Configurer les variables de production** dans `.env`:
```env
DEBUG=False
ALLOWED_HOSTS=safeplace.com,www.safeplace.com
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

4. **Mettre à jour nginx.conf** (décommenter la section SSL)

## [CHART] Monitoring

### Logs

```bash
# Tous les logs
docker-compose logs

# Logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f web
```

### Health Checks

Chaque service a des vérifications de santé:

```bash
# Vérifier l'état
docker-compose ps
```

## [BUG] Dépannage

### Erreur: "permission denied"

```bash
chmod +x init.sh
```

### Erreur: "Port already in use"

Modifier les ports dans `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Utiliser le port 8080
```

### Base de données ne se connecte pas

```bash
# Vérifier les logs
docker-compose logs db

# Redémarrer la base de données
docker-compose restart db
```

### Celery ne traite pas les tâches

```bash
# Vérifier Redis
docker-compose exec redis redis-cli ping

# Redémarrer Celery
docker-compose restart celery celery_beat
```

## [GLOBE] Déploiement en Production

### Options recommandées

1. **Heroku** - Deployment facile (supporté par Procfile)
2. **AWS** - ECS, RDS, ElastiCache
3. **Digital Ocean** - App Platform
4. **Render** - Alternative moderne

### Variables d'environnement requises

- `DEBUG=False`
- `SECRET_KEY=<clé générée>`
- `ALLOWED_HOSTS=votre-domaine.com`
- `DB_PASSWORD=<mot de passe sécurisé>`
- `REDIS_PASSWORD=<mot de passe sécurisé>`
- `STRIPE_SECRET_KEY=<clé Stripe production>`
- `STRIPE_PUBLIC_KEY=<clé Stripe production>`

## [BOOKS] Ressources

- [Django Documentation](https://docs.djangoproject.com)
- [Docker Documentation](https://docs.docker.com)
- [Stripe Documentation](https://stripe.com/docs)
- [Celery Documentation](https://docs.celeryproject.io)
- [PostgreSQL Documentation](https://www.postgresql.org/docs)

## [PHONE] Support

Pour l'aide et le support:
- [EMAIL] Email: support@safeplace.com
- [GLOBE] Site: https://safeplace.com
- [PHONE] Réseaux sociaux: @safeplacebyk

## [PAGE] Licence

© 2024 The SafePlace by K. Tous droits réservés.

---

**Prêt à lancer?** Exécutez `./init.sh` et commencez à diffuser! [ROCKET]
#   P r o j e t - S a f e P l a c e B y - K 
 
 # SafePlaceBy-k
# SafePlaceBy-k
