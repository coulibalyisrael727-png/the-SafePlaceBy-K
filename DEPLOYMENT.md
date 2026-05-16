# [ROCKET] Guide de Déploiement - The SafePlace by K

## [LIST] Checklist Pre-Déploiement

### Sécurité
- [ ] Générer une nouvelle `SECRET_KEY`
- [ ] Activer `DEBUG=False`
- [ ] Configurer `ALLOWED_HOSTS` avec votre domaine
- [ ] Certificats SSL/TLS (HTTPS)
- [ ] Mots de passe sécurisés pour DB et Redis
- [ ] Clés Stripe en production (mode Live)

### Application
- [ ] Tester tous les endpoints
- [ ] Vérifier les emails
- [ ] Tester les paiements Stripe
- [ ] Sauvegarder la base de données
- [ ] Vérifier les logs

### Infrastructure
- [ ] CPU/RAM suffisant
- [ ] Espace disque pour les uploads
- [ ] Bande passante suffisante
- [ ] Backups automatiques

## [GLOBE] Options de Déploiement

## [SPLIT] Architecture Séparée: Site Principal + Dashboard

Le projet utilise une architecture microservice où le site principal et le dashboard peuvent être hébergés séparément tout en communiquant via API.

### Architecture
- **Site Principal** (port 8000): Application Django principale avec API REST
- **Dashboard Service** (port 8001): Microservice Django indépendant pour l'administration

### Communication Inter-Services
- Le dashboard consomme les API du site principal via `MAIN_API_URL`
- Authentification via `DASHBOARD_API_KEY` (doit être identique sur les deux services)
- CORS configuré pour autoriser les requêtes cross-origin

### Configuration Site Principal
```env
# Dans .env du site principal
DASHBOARD_URL=http://localhost:8001
DASHBOARD_API_KEY=safeplace_secret_dashboard_key_2026
```

### Configuration Dashboard
```env
# Dans .env du dashboard-service
MAIN_API_URL=http://localhost:8000/api/v1/
MAIN_SITE_URL=http://localhost:8000
DASHBOARD_API_KEY=safeplace_secret_dashboard_key_2026
MOCK_API_DATA=False  # True pour Vercel sans site principal
```

### Déploiement Séparé

#### Option 1: Même serveur, ports différents
```bash
# Site principal
cd /path/to/main-site
python manage.py runserver 0.0.0.0:8000

# Dashboard (autre terminal)
cd /path/to/dashboard-service
python manage.py runserver 0.0.0.0:8001
```

#### Option 2: Serveurs différents
```bash
# Site principal sur server1.com
MAIN_API_URL=https://server1.com/api/v1/
MAIN_SITE_URL=https://server1.com

# Dashboard sur dashboard.server1.com
DASHBOARD_URL=https://dashboard.server1.com
```

#### Option 3: Vercel (Dashboard) + Autre hébergeur (Site Principal)
```bash
# Dashboard sur Vercel
MOCK_API_DATA=False  # Si le site principal est accessible
MAIN_API_URL=https://main-app-production.com/api/v1/
MAIN_SITE_URL=https://main-app-production.com

# Site principal sur Railway/Heroku/AWS
DASHBOARD_URL=https://dashboard-safeplace.vercel.app
```

### API Endpoints Disponibles
Le dashboard peut accéder à ces endpoints du site principal:
- `GET /api/v1/dashboard-data/` - Statistiques globales
- `GET /api/v1/analytics/` - Analytics détaillées
- `GET /api/v1/episodes/` - Liste des épisodes
- `POST /api/v1/episodes/create/` - Créer un épisode
- `DELETE /api/v1/episodes/<pk>/delete/` - Supprimer un épisode
- `GET /api/v1/livestreams/` - Liste des live streams
- `GET /api/v1/donations/` - Liste des donations
- `GET /api/v1/messages/` - Messages de contact
- `GET /api/v1/subscriptions/` - Liste des abonnements

Tous les endpoints nécessitent l'en-tête:
```
X-API-KEY: safeplace_secret_dashboard_key_2026
```

### 1. **AWS** (Recommandé)

```bash
# Créer une instance EC2 Ubuntu 22.04

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Cloner le projet
git clone <repo>
cd safeplace

# Configurer
cp .env.example .env
# Éditer .env avec les vraies valeurs

# Déployer
docker-compose -f docker-compose.yml up -d

# Mettre en place un reverse proxy (HAProxy/Nginx)
```

### 2. **Heroku** 

```bash
# Installer Heroku CLI
npm i -g heroku

# Login
heroku login

# Créer app
heroku create your-app-name

# Configurer variables d'environnement
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-key
heroku config:set STRIPE_SECRET_KEY=sk_live_...

# Déployer
git push heroku main

# Voir les logs
heroku logs --tail
```

### 3. **Digital Ocean** (Budget friendly)

```bash
# Créer un Droplet (Ubuntu 22.04)

# SSH dans la VM
ssh root@your_ip

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configurer DNS pointer vers votre IP

# Cloner et déployer (voir AWS ci-dessus)
```

### 4. **Render** (Alternative moderne)

1. Connecter votre repo GitHub
2. Créer un Web Service
3. Configurer les environment variables
4. Déployer automatiquement

## [LOCK] Configuration SSL/HTTPS

### Option 1: Let's Encrypt (Gratuit)

```bash
# Installer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Générer les certificats
sudo certbot certonly --standalone -d votre-domaine.com

# Copier les certificats
sudo cp /etc/letsencrypt/live/votre-domaine.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/votre-domaine.com/privkey.pem ./ssl/key.pem

# Autorités automatiques
sudo certbot renew --dry-run
```

### Option 2: AWS Certificate Manager

1. Aller dans AWS Certificate Manager
2. Demander un certificat
3. Valider le domaine
4. Utiliser dans CloudFront

## [CHART] Configuration Nginx avancée

```nginx
# Décommenter dans nginx.conf pour HTTPS

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;
    charset utf-8;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... reste de la config
}

# Redirection HTTP vers HTTPS
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    return 301 https://$server_name$request_uri;
}
```

## [RELOAD] Mise à Jour Continue

### Déploiement d'une nouvelle version

```bash
# Pull les changements
git pull origin main

# Construire les nouvelles images
docker-compose build

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Redémarrer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### Rollback en cas de problème

```bash
# Voir l'historique des images
docker images

# Redémarrer avec une ancienne image
docker-compose down
# Éditer docker-compose.yml avec l'ancienne image
docker-compose up -d

# Vérifier que ça fonctionne
docker-compose logs -f
```

## [CHART] Performance & Monitoring

### Optimisations

```bash
# Réduire les images Docker
docker image prune -a

# Nettoyer les volumes inutilisés
docker volume prune

# Augmenter les workers Gunicorn si CPU élevé
# Dans Dockerfile: gunicorn --workers 8 (basé sur CPU cores)
```

### Monitoring recommandé

- **Datadog** - APM complet
- **New Relic** - Performance
- **Sentry** - Error tracking
- **CloudWatch** (AWS) - Logs et métriques
- **Prometheus + Grafana** - Stack open source

### Installation Prometheus

```yaml
# Ajouter à docker-compose.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

## [SAFE] Sécurité Production

### Checklist

```bash
# 1. Firewall
# - Autoriser: 80, 443
# - Bloquer le reste

# 2. SSH
# - Désactiver root login
# - Utiliser clés SSH uniquement

# 3. Fail2Ban
sudo apt-get install fail2ban
sudo systemctl start fail2ban

# 4. Updates
sudo apt-get update && sudo apt-get upgrade -y

# 5. Backups
# - Sauvegarder DB quotidiennement
# - Tester les restaurations
# - Stocker off-site
```

## [PHONE] Support & Monitoring

### Services recommandés

1. **Status Page** - Uptime Robot, Status.io
2. **Alertes** - PagerDuty
3. **Logs centralisés** - ELK Stack, Splunk
4. **Backups** - AWS Backup, Backblaze

### Exemple Uptime Robot

```
URL: https://votre-domaine.com/health/
Fréquence: 5 minutes
Alertes: Email, SMS
```

## [TARGET] Étapes finales

```bash
# 1. Tester tous les endpoints
curl -I https://votre-domaine.com
curl -I https://votre-domaine.com/admin

# 2. Tester les paiements
# Utiliser cartes de test Stripe en mode live

# 3. Vérifier la performance
# Utiliser tools comme GTmetrix, Google PageSpeed

# 4. Configurer les emails
# Vérifier que les notifications sont envoyées

# 5. Activer les logs
# Configurer les alertes

# 6. Documenter
# Créer des runbooks d'opération
```

## [SOS] Troubleshooting Production

### Erreur 502 Bad Gateway

```bash
# Vérifier que Django fonctionne
docker-compose logs web

# Redémarrer Gunicorn
docker-compose restart web

# Vérifier la connexion DB
docker-compose logs db
```

### Haute utilisation CPU

```bash
# Augmenter les workers
docker-compose exec web gunicorn --workers 8

# Optimiser les requêtes DB
docker-compose exec web python manage.py dbshell
```

### Disque plein

```bash
# Nettoyer les logs
docker system prune

# Archiver les anciennes données
docker-compose exec web python manage.py cleanup_old_donations

# Vérifier les uploads
du -sh /path/to/media
```

---

**Votre application est maintenant en production!** [PARTY]

Pour les mises à jour futures, suivez le processus de déploiement ci-dessus.
