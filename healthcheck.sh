#!/bin/bash
# Script de vérification de la santé de l'application

set -e

# Vérifier Django
echo "Vérification de Django..."
curl -f http://localhost:8000/health/ || exit 1

# Vérifier PostgreSQL
echo "Vérification de PostgreSQL..."
python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" || exit 1

# Vérifier Redis
echo "Vérification de Redis..."
redis-cli ping || exit 1

echo "✓ Tous les services sont en bonne santé!"
