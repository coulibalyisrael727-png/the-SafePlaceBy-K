import stripe
import os
from django.conf import settings

# Configuration Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else '')

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', settings.STRIPE_PUBLIC_KEY if hasattr(settings, 'STRIPE_PUBLIC_KEY') else '')
STRIPE_SECRET_KEY = stripe.api_key

class StripePaymentHandler:
    """
    Gestionnaire des paiements Stripe
    """
    
    @staticmethod
    def create_payment_intent(amount, currency='eur', metadata=None, email=None):
        """
        Créer un Payment Intent Stripe
        amount: en centimes (ex: 1000 = 10€)
        """
        try:
            intent_data = {
                'amount': int(amount),
                'currency': currency,
                'metadata': metadata or {},
                'automatic_payment_methods': {
                    'enabled': True,
                    'allow_redirects': 'never'
                },
                'confirmation_method': 'manual'
            }
            
            # Ajouter l'email si fourni
            if email:
                intent_data['receipt_email'] = email
            elif metadata and metadata.get('email'):
                intent_data['receipt_email'] = metadata.get('email')
            
            intent = stripe.PaymentIntent.create(**intent_data)
            return intent
            
        except stripe.error.CardError as e:
            return {'error': f"Erreur carte: {e.user_message}"}
        except stripe.error.RateLimitError as e:
            return {'error': "Trop de requêtes. Veuillez réessayer dans quelques minutes."}
        except stripe.error.InvalidRequestError as e:
            return {'error': f"Requête invalide: {e.message}"}
        except stripe.error.AuthenticationError as e:
            return {'error': "Erreur d'authentification Stripe. Vérifiez vos clés API."}
        except stripe.error.APIConnectionError as e:
            return {'error': "Erreur de connexion Stripe. Vérifiez votre connexion internet."}
        except stripe.error.StripeError as e:
            return {'error': f"Erreur Stripe: {e.message}"}
        except Exception as e:
            return {'error': f"Erreur inattendue: {str(e)}"}
    
    @staticmethod
    def retrieve_payment_intent(intent_id):
        """Récupérer les détails d'un Payment Intent"""
        try:
            return stripe.PaymentIntent.retrieve(intent_id)
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def confirm_payment_intent(intent_id, payment_method_id):
        """Confirmer un Payment Intent"""
        try:
            intent = stripe.PaymentIntent.confirm(
                intent_id,
                payment_method=payment_method_id,
                return_url=True
            )
            return intent
        except stripe.error.CardError as e:
            return {'error': f"Erreur carte: {e.user_message}"}
        except stripe.error.InvalidRequestError as e:
            return {'error': f"Requête invalide: {e.message}"}
        except stripe.error.AuthenticationError as e:
            return {'error': "Erreur d'authentification Stripe"}
        except stripe.error.APIConnectionError as e:
            return {'error': "Erreur de connexion Stripe"}
        except stripe.error.StripeError as e:
            return {'error': f"Erreur Stripe: {e.message}"}
        except Exception as e:
            return {'error': f"Erreur: {str(e)}"}
    
    @staticmethod
    def create_customer(email, name=None, metadata=None):
        """Créer un client Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name or 'Donateur',
                metadata=metadata or {}
            )
            return customer
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def create_subscription(customer_id, price_id):
        """Créer un abonnement"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}]
            )
            return subscription
        except Exception as e:
            return {'error': str(e)}


def process_donation(donation_obj, payment_method_id=None):
    """
    Traiter une donation via Stripe
    """
    handler = StripePaymentHandler()
    
    # Convertir en centimes
    amount_cents = int(donation_obj.amount * 100)
    
    # Créer le Payment Intent
    intent_data = {
        'email': donation_obj.email,
        'name': donation_obj.name,
        'donation_id': str(donation_obj.id)
    }
    
    intent = handler.create_payment_intent(
        amount_cents, 
        metadata=intent_data,
        email=donation_obj.email
    )
    
    if 'error' in intent:
        donation_obj.status = 'failed'
        donation_obj.save()
        return False, intent['error']
    
    donation_obj.stripe_payment_intent = intent.id
    donation_obj.save()
    
    # Si payment_method_id est fourni, confirmer immédiatement
    if payment_method_id:
        confirmed = handler.confirm_payment_intent(intent.id, payment_method_id)
        
        if 'error' in confirmed:
            donation_obj.status = 'failed'
            donation_obj.save()
            return False, confirmed['error']
        
        if confirmed.status == 'succeeded':
            donation_obj.status = 'completed'
            donation_obj.save()
            return True, "Paiement réussi"
        
        return False, "Paiement en attente"
    
    # Sinon, retourner le client_secret pour confirmation frontend
    return True, intent.client_secret
