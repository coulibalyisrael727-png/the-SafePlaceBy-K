# [SAFE] The SafePlace by K - Architecture Microservices avec Docker

Architecture containerisée complète pour la plateforme de podcast SafePlace avec microservices, base de données PostgreSQL, cache Redis, paiements Stripe et tâches asynchrones Celery.

## [LIST] Architecture

```
┌─────────────────────────────────────────────────┐
│           Nginx (Reverse Proxy)                 │
│        Port 80 (HTTP) / 443 (HTTPS)             │
└────────┬──────────────────────────────────┬─────┘
         │                                  │
    ┌────▼─────────────┐          ┌────────▼──────┐
    │  Django Web App  │          │  Nginx Static │
    │  (Gunicorn)      │          │  & Media      │
    │  Port 8000       │          │               │
    └────┬─────────────┘          └───────────────┘
         │
    ┌────┴──────────────┬──────────────┬──────────────┐
    │                   │              │              │
┌───▼──────┐      ┌────▼────┐    ┌───▼──────┐  ┌───▼──────┐
│PostgreSQL│      │  Redis  │    │ Celery   │  │ Celery   │
│   DB     │      │  Cache  │    │ Worker   │  │  Beat    │
│ Port5432 │      │ Port6379│    │          │  │Scheduler │
└──────────┘      └─────────┘    └──────────┘  └──────────┘
```

## [ROCKET] Services Inclus

1. **PostgreSQL** - Base de données relationnelle
2. **Redis** - Cache et broker pour Celery
3. **Django Web** - Application principale
4. **Celery Worker** - Traitement des tâches asynchrones
5. **Celery Beat** - Scheduler pour tâches planifiées
6. **Nginx** - Reverse proxy et serveur statique

## [PACKAGE] Prérequis

- Docker ≥ 20.10
- Docker Compose ≥ 2.0
- Git

## [TOOLS] Installation Rapide

### 1. Cloner ou télécharger le projet

```bash
git clone <repository>
cd safeplace
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Éditer `.env` et configurer:
- Clés Stripe (créer un compte sur https://stripe.com)
- Identifiants email
- Clé secrète Django
- Mots de passe database et Redis

### 3. Démarrer l'application

**Automatique (recommandé):**
```bash
chmod +x init.sh
./init.sh
```

**Manuel:**
```bash
# Construire les images
docker-compose build

# Démarrer les services
docker-compose up -d

# Exécuter les migrations
docker-compose exec web python manage.py migrate

# Créer le superutilisateur
docker-compose exec web python manage.py createsuperuser

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Accéder à l'application

- **Site**: http://localhost
- **Admin Django**: http://localhost/admin
- **API**: http://localhost/api/

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
#   P r o j e t - S a f e P l a c e B y - K  
 # SafePlaceBy-k
# SafePlaceBy-k
