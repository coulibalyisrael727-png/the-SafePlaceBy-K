#!/usr/bin/env python
"""
Script de test pour vérifier le système de paiement Stripe
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Safeplace.settings')
django.setup()

from podcastSafe.stripe_handler import StripePaymentHandler, process_donation
from podcastSafe.models import Donation

def test_stripe_connection():
    """Test la connexion à Stripe"""
    print("🔍 Test de connexion à Stripe...")
    
    try:
        # Test simple: créer un Payment Intent de 1€
        handler = StripePaymentHandler()
        result = handler.create_payment_intent(
            amount=100,  # 1€ en centimes
            metadata={
                'test': True,
                'email': 'test@example.com'
            }
        )
        
        if 'error' in result:
            print(f"❌ Erreur de connexion Stripe: {result['error']}")
            return False
        
        print(f"✅ Connexion Stripe réussie - Payment Intent ID: {result.id}")
        
        # Nettoyer le test
        try:
            import stripe
            stripe.PaymentIntent.cancel(result.id)
            print("✅ Payment Intent de test annulé")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to cancel test Payment Intent: {str(e)}")
            print(f"⚠️ Impossible d'annuler le Payment Intent de test: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return False

def test_donation_creation():
    """Test la création d'une donation"""
    print("\n🔍 Test de création de donation...")
    
    try:
        # Créer une donation de test
        donation = Donation.objects.create(
            name="Test User",
            email="test@example.com",
            amount=10.00,
            message="Don de test",
            status="pending"
        )
        
        print(f"✅ Donation créée - ID: {donation.id}")
        
        # Tester le traitement
        success, result = process_donation(donation)
        
        if success:
            print(f"✅ Traitement réussi - Client Secret: {result[:20]}...")
        else:
            print(f"❌ Erreur de traitement: {result}")
        
        # Nettoyer
        donation.delete()
        print("✅ Donation de test supprimée")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_webhook_security():
    """Test la sécurité du webhook"""
    print("\n🔍 Test de sécurité du webhook...")
    
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    if not webhook_secret:
        print("❌ STRIPE_WEBHOOK_SECRET non configuré")
        return False
    
    if webhook_secret.startswith('whsec_'):
        print("✅ Webhook secret configuré correctement")
        return True
    else:
        print("❌ Format du webhook secret invalide")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du système de paiement Stripe\n")
    
    # Vérifier les clés Stripe
    stripe_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe_key:
        print("❌ STRIPE_SECRET_KEY non configuré")
        return False
    
    if not stripe_key.startswith('sk_'):
        print("❌ Format de la clé secrète Stripe invalide")
        return False
    
    print("✅ Clés Stripe configurées")
    
    # Lancer les tests
    tests = [
        test_stripe_connection,
        test_donation_creation,
        test_webhook_security
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur inattendue dans {test.__name__}: {str(e)}")
            results.append(False)
    
    # Résumé
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Résumé des tests: {success_count}/{total_count} réussis")
    
    if success_count == total_count:
        print("🎉 Tous les tests passés! Le système Stripe est fonctionnel.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
