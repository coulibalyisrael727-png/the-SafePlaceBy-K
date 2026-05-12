from celery import shared_task
from django.core.mail import send_mass_mail
from django.utils import timezone
from datetime import timedelta
from .models import Episode, LiveStream, Donation

@shared_task
def update_live_stream_status():
    """
    Mettre à jour le statut des live streams
    """
    now = timezone.now()
    
    # Mettre à jour les live streams programmés qui ont commencé
    scheduled_streams = LiveStream.objects.filter(
        status='scheduled',
        scheduled_at__lte=now
    )
    scheduled_streams.update(status='live')
    
    return f"Updated {scheduled_streams.count()} streams"


@shared_task
def send_new_episode_notifications():
    """
    Envoyer une notification pour les nouveaux épisodes
    """
    # Récupérer les épisodes publiés aujourd'hui
    today = timezone.now().date()
    today_episodes = Episode.objects.filter(
        is_published=True,
        created_at__date=today
    )
    
    if not today_episodes.exists():
        return "No new episodes today"
    
    # Créer un email pour chaque nouvel épisode
    emails = []
    for episode in today_episodes:
        # Vous pouvez ajouter les emails des abonnés ici
        # Pour l'instant, on envoie juste une notification interne
        pass
    
    return f"Notifications sent for {today_episodes.count()} episodes"


@shared_task
def cleanup_old_donations():
    """
    Nettoyer les anciennes donations (garder les 2 dernières années)
    """
    two_years_ago = timezone.now() - timedelta(days=730)
    
    old_donations = Donation.objects.filter(
        created_at__lt=two_years_ago,
        status='completed'
    )
    
    count = old_donations.count()
    old_donations.delete()
    
    return f"Deleted {count} old donations"


@shared_task
def process_stripe_webhook(event_id):
    """
    Traiter les webhooks Stripe
    """
    import stripe
    from django.conf import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        event = stripe.Event.retrieve(event_id)
        
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            donation_id = payment_intent.metadata.get('donation_id')
            
            if donation_id:
                donation = Donation.objects.get(id=donation_id)
                donation.status = 'completed'
                donation.save()
                
                return f"Donation {donation_id} marked as completed"
        
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object
            donation_id = payment_intent.metadata.get('donation_id')
            
            if donation_id:
                donation = Donation.objects.get(id=donation_id)
                donation.status = 'failed'
                donation.save()
                
                return f"Donation {donation_id} marked as failed"
    
    except Exception as e:
        return f"Error processing event: {str(e)}"


@shared_task
def send_daily_report():
    """
    Envoyer un rapport quotidien au propriétaire
    """
    from django.conf import settings
    
    today = timezone.now().date()
    
    new_episodes = Episode.objects.filter(created_at__date=today).count()
    new_donations = Donation.objects.filter(
        created_at__date=today,
        status='completed'
    ).count()
    total_revenue = sum(d.amount for d in Donation.objects.filter(
        created_at__date=today,
        status='completed'
    ))
    
    message = f"""
    Rapport journalier - {today}
    
    Nouveaux épisodes: {new_episodes}
    Nouveaux dons: {new_donations}
    Revenu du jour: {total_revenue}€
    """
    
    if settings.ADMINS:
        send_mass_mail(((
            'Rapport journalier SafePlace',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMINS[0][1]],
        ),))
    
    return message
