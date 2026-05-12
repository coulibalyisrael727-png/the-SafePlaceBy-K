# [BOLT] Démarrage Rapide - The SafePlace by K

## [ROCKET] Lancer en 5 minutes

### 1. **Prérequis**
- Docker Desktop installé
- Terminal/PowerShell ouvert

### 2. **Configuration initiale**

```bash
# Copier la configuration
cp .env.example .env

# Éditer .env et ajouter:
# - STRIPE_PUBLIC_KEY (obtenir sur https://stripe.com)
# - STRIPE_SECRET_KEY
# - Email (optionnel pour les notifications)
```

### 3. **Démarrer l'application**

**Automatique (recommandé):**
```bash
chmod +x init.sh
./init.sh
```

**Avec Make:**
```bash
make init
```

**Manuel:**
```bash
# Construire
docker-compose build

# Démarrer
docker-compose up -d

# Migrations
docker-compose exec web python manage.py migrate

# Admin
docker-compose exec web python manage.py createsuperuser

# Statiques
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. **Accéder à l'application**

| Service | URL |
|---------|-----|
| [GLOBE] Site | http://localhost |
| [USER] Admin | http://localhost/admin |
| [BROADCAST] API | http://localhost/api/ |

## [PAGE] Configuration Stripe

### Test Mode (recommandé d'abord)

1. Aller sur https://stripe.com/docs/payments/test
2. Utiliser ces numéros de test:
   - **Carte**: `4242 4242 4242 4242`
   - **Date**: `12/25`
   - **CVC**: `123`

### Production

1. Passer en mode Live dans Stripe Dashboard
2. Mettre à jour `.env` avec les clés Live
3. Changer `DEBUG=False` dans `.env`

## [KEY] Pages Admin

| Page | URL | Fonction |
|------|-----|----------|
| Dashboard | `/studio/` | Analytics (propriétaire uniquement) |
| Publier | `/studio/publish/` | Créer un épisode |
| Lives | `/studio/live-streams/` | Gérer les directs |
| Donations | `/abonnements/` | Voir les donations |

## [PHONE] Tester les Donations

1. Aller à `/abonnements/`
2. Remplir le formulaire
3. Utiliser une carte de test
4. Confirmé! [CHECK]

## [BUG] Dépannage Rapide

**Port occupé?**
```bash
# Modifier docker-compose.yml
# ports:
#   - "8080:8000"  # Utilisez le port 8080
docker-compose up -d
```

**Base de données ne démarre pas?**
```bash
docker-compose logs db
docker-compose restart db
```

**Celery ne fonctionne pas?**
```bash
docker-compose logs celery
docker-compose restart celery
```

## [CHART] Commandes Utiles

```bash
# Voir les logs en direct
docker-compose logs -f web

# Accès shell Django
docker-compose exec web python manage.py shell

# Redémarrer les services
docker-compose restart

# Tout arrêter
docker-compose down

# Sauvegarder la DB
docker-compose exec db pg_dump -U safeplace_user safeplace_db > backup.sql
```

## [TARGET] Prochaines étapes

- [ ] Configurer Stripe
- [ ] Créer des catégories dans l'admin
- [ ] Ajouter des épisodes
- [ ] Tester les donations
- [ ] Configurer les emails
- [ ] Déployer en production

## [PHONE] Besoin d'aide?

1. Vérifier les logs: `docker-compose logs -f`
2. Consulter README.md pour plus de détails
3. Contacter le support

---

**C'est tout!** Vous êtes prêt à diffuser du contenu! [MIC][BROADCAST][CROSS]
