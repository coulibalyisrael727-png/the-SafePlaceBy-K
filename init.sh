#!/bin/bash

# Script d'initialisation du projet SafePlace

echo "🚀 Initialisation du projet SafePlace..."

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

# Vérifier si docker-compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

# Copier .env.example en .env s'il n'existe pas
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Fichier .env créé à partir de .env.example"
    echo "⚠️  Veuillez configurer les variables d'environnement dans .env"
fi

# Créer les répertoires nécessaires
mkdir -p ssl media staticfiles logs

# Construire les images Docker
echo "🔨 Construction des images Docker..."
docker-compose build

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attendre que la base de données soit prête
echo "⏳ Attente de la base de données..."
docker-compose exec -T db pg_isready -U safeplace_user > /dev/null 2>&1
while [ $? -ne 0 ]; do
    sleep 1
    docker-compose exec -T db pg_isready -U safeplace_user > /dev/null 2>&1
done

echo "✓ Base de données prête"

# Exécuter les migrations
echo "📦 Exécution des migrations..."
docker-compose exec -T web python manage.py migrate

# Créer un superutilisateur
echo "👤 Création du superutilisateur..."
docker-compose exec -T web python manage.py createsuperuser

# Charger les données initiales
echo "📊 Chargement des données initiales..."
docker-compose exec -T web python manage.py loaddata initial_data 2>/dev/null || echo "Aucune donnée initiale trouvée"

# Afficher les logs
echo "📋 Affichage des logs..."
docker-compose logs -f
