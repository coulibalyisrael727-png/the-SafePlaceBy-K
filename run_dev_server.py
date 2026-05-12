#!/usr/bin/env python
"""
Script pour lancer le serveur de développement avec SQLite
Permet de tester le système Stripe sans dépendances complexes
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configuration Django pour développement
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Safeplace.settings')

# Configuration minimale pour le développement
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='dev-secret-key-for-testing-only-change-in-production',
        ALLOWED_HOSTS=['localhost', '127.0.0.1'],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'safeplace_dev.db',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'corsheaders',
            'podcastSafe',
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
        ROOT_URLCONF='Safeplace.urls',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': ['podcastSafe/template'],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        STATIC_URL='/static/',
        STATICFILES_DIRS=['static'],
        USE_TZ=True,
        TIME_ZONE='Europe/Paris',
        LANGUAGE_CODE='fr-fr',
        # Configuration Stripe (à remplir avec vos vraies clés)
        STRIPE_PUBLIC_KEY=os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_placeholder'),
        STRIPE_SECRET_KEY=os.getenv('STRIPE_SECRET_KEY', 'sk_test_placeholder'),
        STRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_placeholder'),
        # Configuration email (optionnel)
        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@safeplace.com',
        ADMINS=[('Admin', 'admin@safeplace.com')],
    )

def main():
    """Lancer le serveur de développement"""
    print("🚀 Lancement du serveur de développement SafePlace")
    print("📍 URL: http://localhost:8000")
    print("🔧 Configuration: SQLite (développement)")
    print("💰 Stripe: Configuré (clés de test requises)")
    print("\n⚠️  Pour tester les paiements:")
    print("   1. Configurez STRIPE_PUBLIC_KEY et STRIPE_SECRET_KEY")
    print("   2. Allez sur http://localhost:8000/donate/")
    print("   3. Utilisez les cartes de test Stripe")
    
    try:
        # Lancer les migrations
        print("\n📦 Exécution des migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Créer un superutilisateur si n'existe pas
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("\n👤 Création du superutilisateur...")
            execute_from_command_line(['manage.py', 'createsuperuser', 
                                    '--username', 'admin', 
                                    '--email', 'admin@safeplace.com',
                                    '--noinput'])
        
        # Lancer le serveur
        print("\n🌐 Démarrage du serveur...")
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
        
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
