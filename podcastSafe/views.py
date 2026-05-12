from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
import os
import json

from .models import Episode, LiveStream, Category, Donation, Subscription, ContactMessage
from .auth import owner_required
from .stripe_handler import StripePaymentHandler


def send_donation_confirmation_email(donation):
    """Helper function to send donation confirmation email"""
    try:
        send_mail(
            'Merci pour votre don!',
            f'Bonjour {donation.name},\n\nMerci beaucoup pour votre don de {donation.amount}€ à The SafePlace by K.\n\nVotre aide nous permet de continuer notre mission.\n\nDieu vous bénisse!\n\nThe SafePlace by K',
            settings.DEFAULT_FROM_EMAIL,
            [donation.email],
            fail_silently=True
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to send donation confirmation email to {donation.email}: {str(e)}")


def home(request):
    published = Episode.objects.filter(is_published=True)
    latest_episodes = published.filter(episode_type='podcast')[:6]
    latest_videos = published.filter(episode_type='video')[:4]
    live_streams = LiveStream.objects.filter(status='live')[:4]
    featured = published.first()
    categories = Category.objects.all()
    category_ids_by_slug = {}
    for cat in categories:
        category_ids_by_slug[slugify(cat.name)] = str(cat.id)
    context = {
        'latest_episodes': latest_episodes,
        'latest_videos': latest_videos,
        'live_streams': live_streams,
        'featured': featured,
        'categories': categories,
        'category_ids_by_slug': category_ids_by_slug,
    }
    return render(request, 'Accueil.html', context)


def podcasts(request):
    episodes = Episode.objects.filter(is_published=True, episode_type='podcast')
    categories = Category.objects.all()
    selected_cat = request.GET.get('categorie')
    if selected_cat:
        if str(selected_cat).isdigit():
            filtered_episodes = episodes.filter(category__id=selected_cat)
        else:
            slug = slugify(str(selected_cat).replace('_', '-'))
            cat_ids = [
                c.id for c in categories
                if slugify(c.name) == slug
            ]
            filtered_episodes = episodes.filter(category_id__in=cat_ids) if cat_ids else episodes.none()
    else:
        filtered_episodes = episodes
    context = {'episodes': filtered_episodes, 'categories': categories, 'selected_cat': selected_cat}
    return render(request, 'podcasts.html', context)


def videos(request):
    episodes = Episode.objects.filter(is_published=True, episode_type='video')
    categories = Category.objects.all()
    selected_cat = request.GET.get('categorie')
    if selected_cat:
        if str(selected_cat).isdigit():
            filtered_episodes = episodes.filter(category__id=selected_cat)
        else:
            slug = slugify(str(selected_cat).replace('_', '-'))
            cat_ids = [c.id for c in categories if slugify(c.name) == slug]
            filtered_episodes = episodes.filter(category_id__in=cat_ids) if cat_ids else episodes.none()
    else:
        filtered_episodes = episodes
    context = {'episodes': filtered_episodes, 'categories': categories, 'selected_cat': selected_cat}
    return render(request, 'videos.html', context)


def podcast_detail(request, pk):
    episode = get_object_or_404(Episode, pk=pk, is_published=True)
    similar = (
        Episode.objects.filter(
            is_published=True,
            episode_type=episode.episode_type,
            category=episode.category,
        )
        .exclude(pk=pk)[:3]
    )
    context = {
        'episode': episode,
        'similar_episodes': similar,
        'youtube_embed_url': episode.get_youtube_embed_url(),
    }
    return render(request, 'podcast_detail.html', context)


def live(request):
    streams = LiveStream.objects.filter(status='live')
    scheduled = LiveStream.objects.filter(status='scheduled')
    context = {'streams': streams, 'scheduled': scheduled}
    return render(request, 'live.html', context)


@owner_required
def dashboard(request):
    """Dashboard accessible uniquement au propriétaire du site"""
    episodes = Episode.objects.all()[:10]
    total_episodes = Episode.objects.count()
    total_views = sum(e.views_count for e in Episode.objects.all())
    total_donations = Donation.objects.filter(status='completed').count()
    total_revenue = sum(d.amount for d in Donation.objects.filter(status='completed'))
    
    context = {
        'episodes': episodes,
        'total_episodes': total_episodes,
        'total_views': total_views,
        'total_donations': total_donations,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard.html', context)


@owner_required
def publish_episode(request):
    """Créer ou éditer un épisode"""
    if request.method == 'POST':
        try:
            title = (request.POST.get('title') or '').strip()
            description = (request.POST.get('description') or '').strip()
            episode_type = request.POST.get('episode_type', 'podcast')
            if episode_type not in ('podcast', 'video'):
                episode_type = 'podcast'
            category_id = request.POST.get('category')
            audio_url = (request.POST.get('audio_url') or '').strip()
            video_url = (request.POST.get('video_url') or '').strip()
            duration = (request.POST.get('duration') or '').strip()
            cover_color = request.POST.get('cover_color', '#00261b') or '#00261b'

            if not title or not description:
                raise ValueError('Le titre et la description sont obligatoires.')
            if episode_type == 'podcast' and not audio_url:
                raise ValueError('Pour un podcast, renseignez une URL audio (fichier MP3 ou hébergeur).')
            if episode_type == 'video' and not video_url:
                raise ValueError('Pour une vidéo, renseignez une URL (YouTube, lien direct, etc.).')

            category = Category.objects.get(id=category_id) if category_id else None

            episode = Episode(
                title=title,
                description=description,
                episode_type=episode_type,
                category=category,
                audio_url=audio_url,
                video_url=video_url,
                duration=duration,
                cover_color=cover_color,
                is_published=True,
            )
            episode.save()

            return redirect('podcast_detail', pk=episode.id)
        except Exception as e:
            context = {'error': str(e), 'categories': Category.objects.all()}
            return render(request, 'publish_episode.html', context)
    
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'publish_episode.html', context)


def _parse_post_or_json(request):
    """Return a dict from JSON body or form POST (for studio forms)."""
    ct = (request.META.get('CONTENT_TYPE') or '').lower()
    if 'application/json' in ct and request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    return request.POST


@owner_required
def manage_live_streams(request):
    """Gérer les Live Streams"""
    if request.method == 'POST':
        try:
            data = _parse_post_or_json(request)
            title = (data.get('title') or '').strip()
            description = (data.get('description') or '').strip()
            platform = (data.get('platform') or '').strip()
            stream_url = (data.get('stream_url') or '').strip()
            embed_url = (data.get('embed_url') or '').strip()
            status = (data.get('status') or 'scheduled').strip()
            
            if not title:
                return JsonResponse({'success': False, 'error': 'Le titre est obligatoire.'})
            if not platform:
                return JsonResponse({'success': False, 'error': 'Choisissez une plateforme.'})

            live_stream = LiveStream(
                title=title,
                description=description,
                platform=platform,
                stream_url=stream_url,
                embed_url=embed_url,
                status=status,
            )
            live_stream.save()

            return JsonResponse({'success': True, 'message': 'Live Stream créé avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    live_streams = LiveStream.objects.all()
    context = {
        'live_streams': live_streams,
        'platforms': LiveStream._meta.get_field('platform').choices,
        'statuses': LiveStream._meta.get_field('status').choices,
    }
    return render(request, 'manage_live_streams.html', context)


def subscriptions(request):
    """Voir les donations et abonnements"""
    donations = Donation.objects.filter(status='completed')[:20]
    context = {'donations': donations}
    return render(request, 'subscriptions.html', context)


def donate(request):
    """Page abonnement gratuit + dons (liens gratuits, virement, option Stripe)."""
    from django.conf import settings as dj_settings

    channel_defs = [
        ('paypal', 'PayPal', dj_settings.DONATION_PAYPAL_URL, 'Paiement sécurisé via votre compte PayPal', 'payments'),
        ('kofi', 'Ko-fi', dj_settings.DONATION_KOFI_URL, 'Café virtuel, sans abonnement pour le site', 'local_cafe'),
        ('tipeee', 'Tipeee', dj_settings.DONATION_TIPEEE_URL, 'Soutien récurrent ou ponctuel', 'favorite'),
        ('utip', 'uTip', dj_settings.DONATION_UTIP_URL, 'Pourboires et objectifs', 'savings'),
        ('buymeacoffee', 'Buy Me a Coffee', dj_settings.DONATION_BUYMEACOFFEE_URL, 'Petit don international', 'coffee'),
    ]
    donation_channels = []
    for key, label, url, desc, icon in channel_defs:
        u = (url or '').strip()
        if u:
            donation_channels.append(
                {'key': key, 'label': label, 'url': u, 'description': desc, 'icon': icon}
            )

    stripe_pub = (getattr(dj_settings, 'STRIPE_PUBLIC_KEY', None) or '').strip()
    stripe_on = bool(
        getattr(dj_settings, 'STRIPE_DONATIONS_ENABLED', False)
        and stripe_pub
        and stripe_pub.startswith(('pk_live_', 'pk_test_'))
    )

    context = {
        'donation_channels': donation_channels,
        'donation_iban': (getattr(dj_settings, 'DONATION_BANK_IBAN', '') or '').strip(),
        'donation_bank_label': getattr(dj_settings, 'DONATION_BANK_LABEL', 'The SafePlace by K'),
        'stripe_donations_enabled': stripe_on,
        'stripe_public_key': stripe_pub,
    }
    return render(request, 'donate.html', context)


@require_http_methods(["POST"])
def pledge_donation_notify(request):
    """Signalement gratuit d'un don (virement ou autre) — e-mail à l'équipe, sans passerelle payante."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Requête invalide'}, status=400)

    name = (data.get('name') or '').strip() or 'Anonyme'
    email = (data.get('email') or '').strip()
    amount_hint = (data.get('amount_hint') or '').strip()
    method = (data.get('method') or 'virement').strip()
    message = (data.get('message') or '').strip()

    if not email or '@' not in email:
        return JsonResponse({'success': False, 'error': 'Une adresse e-mail valide est obligatoire.'}, status=400)

    to_addr = getattr(settings, 'DONATION_NOTIFY_EMAIL', None) or (
        settings.ADMINS[0][1] if settings.ADMINS else None
    )
    if not to_addr:
        to_addr = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'admin@safeplace.com'

    body = (
        f'Notification de don (hors carte intégrée au site)\n\n'
        f'Nom : {name}\n'
        f'E-mail : {email}\n'
        f'Moyen indiqué : {method}\n'
        f'Montant annoncé : {amount_hint or "non précisé"}\n\n'
        f'Message :\n{message or "(aucun)"}\n'
    )
    try:
        send_mail(
            f'[SafePlace] Intent de don — {name}',
            body,
            settings.DEFAULT_FROM_EMAIL,
            [to_addr],
            fail_silently=False,
        )
    except Exception as exc:
        return JsonResponse({'success': False, 'error': f"Impossible d'envoyer la notification : {exc}"}, status=500)

    return JsonResponse({'success': True, 'message': 'Merci ! Nous avons bien reçu votre signalement.'})


@require_http_methods(["POST"])
def create_subscription(request):
    """Créer un abonnement gratuit aux notifications"""
    try:
        data = json.loads(request.body)
        
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        
        if not first_name or not email:
            return JsonResponse({'success': False, 'error': 'Prénom et email sont obligatoires'})
        
        # Vérifier si l'email existe déjà
        if Subscription.objects.filter(email=email).exists():
            # Si existe, mettre à jour les préférences
            subscription = Subscription.objects.get(email=email)
        else:
            # Créer nouveau
            subscription = Subscription(first_name=first_name, last_name=last_name, email=email)
        
        # Mettre à jour les préférences de notification
        subscription.notify_podcasts = data.get('notify_podcasts', True)
        subscription.notify_live = data.get('notify_live', True)
        subscription.notify_videos = data.get('notify_videos', False)
        subscription.is_active = True
        subscription.save()
        
        # Envoyer un email de confirmation
        try:
            send_mail(
                'Bienvenue dans la communauté SafePlace!',
                f'''Bonjour {first_name},

Merci de vous être abonné à The SafePlace by K!

Vous recevrez désormais des notifications pour:
{'✓ Nouveaux podcasts' if subscription.notify_podcasts else ''}
{'✓ Émissions live' if subscription.notify_live else ''}
{'✓ Nouvelles vidéos' if subscription.notify_videos else ''}

Vous pouvez modifier vos préférences à tout moment en vous réabonnant.

Que Dieu vous bénisse!

The SafePlace by K''',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True
            )
        except:
            pass
        
        return JsonResponse({'success': True, 'message': 'Abonnement réussi!'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def create_donation(request):
    """Créer une donation via Stripe (uniquement si activé dans les réglages)."""
    if not getattr(settings, 'STRIPE_DONATIONS_ENABLED', False):
        return JsonResponse(
            {
                'success': False,
                'error': 'Les dons par carte sont désactivés. Utilisez PayPal, Ko-fi, le virement ou le formulaire de signalement sur la page Dons.',
            },
            status=400,
        )
    if not (getattr(settings, 'STRIPE_PUBLIC_KEY', '') or '').strip().startswith(('pk_live_', 'pk_test_')):
        return JsonResponse({'success': False, 'error': 'Paiement par carte non configuré.'}, status=503)
    try:
        data = json.loads(request.body)
        
        amount = float(data.get('amount', 0))
        email = data.get('email', '')
        name = data.get('name', 'Anonyme')
        message = data.get('message', '')
        
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Le montant doit être positif'})
        
        if not email or '@' not in email:
            return JsonResponse({'success': False, 'error': 'Email invalide'})
        
        # Créer la donation en base de données
        donation = Donation(
            name=name,
            email=email,
            amount=amount,
            message=message,
            status='pending'
        )
        donation.save()
        
        # Traiter avec le gestionnaire Stripe amélioré
        from .stripe_handler import process_donation
        success, result = process_donation(donation)
        
        if not success:
            return JsonResponse({'success': False, 'error': result})
        
        # Si result est un client_secret, le retourner pour confirmation frontend
        if isinstance(result, str) and result.startswith('pi_'):
            return JsonResponse({
                'success': True,
                'client_secret': result,
                'donation_id': donation.id
            })
        
        # Sinon, c'est un message de succès
        return JsonResponse({'success': True, 'message': result})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'})


@require_http_methods(["POST"])
def confirm_donation(request):
    """Confirmer une donation après paiement Stripe"""
    if not getattr(settings, 'STRIPE_DONATIONS_ENABLED', False):
        return JsonResponse({'success': False, 'error': 'Paiement par carte désactivé.'}, status=400)
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        
        donation = get_object_or_404(Donation, id=donation_id)
        
        # Récupérer l'état du Payment Intent
        handler = StripePaymentHandler()
        intent = handler.retrieve_payment_intent(donation.stripe_payment_intent)
        
        if 'error' in intent:
            return JsonResponse({'success': False, 'error': 'Erreur lors de la vérification du paiement'})
        
        if intent.status == 'succeeded':
            donation.status = 'completed'
            donation.save()
            
            # Envoyer un email de confirmation
            send_donation_confirmation_email(donation)
            
            return JsonResponse({'success': True, 'message': 'Merci pour votre donation!'})
        
        return JsonResponse({'success': False, 'error': 'Paiement non confirmé'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def stripe_webhook(request):
    """Webhook Stripe pour gérer les événements de paiement automatiquement"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        # Vérifier la signature du webhook
        try:
            import stripe
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET', '')
            )
        except ValueError as e:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Traiter les événements pertinents
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            donation_id = payment_intent.metadata.get('donation_id')
            
            if donation_id:
                try:
                    donation = Donation.objects.get(id=donation_id)
                    if donation.status == 'pending':
                        donation.status = 'completed'
                        donation.save()
                        
                        # Envoyer email de confirmation
                        send_donation_confirmation_email(donation)
                except Donation.DoesNotExist:
                    pass
        
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object
            donation_id = payment_intent.metadata.get('donation_id')
            
            if donation_id:
                try:
                    donation = Donation.objects.get(id=donation_id)
                    donation.status = 'failed'
                    donation.save()
                except Donation.DoesNotExist:
                    # Log the error but don't fail the webhook processing
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Donation with id {donation_id} not found for payment_failed event")
                except Exception as e:
                    # Log unexpected errors
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing payment_failed event for donation {donation_id}: {str(e)}")
        
        return JsonResponse({'status': 'success'}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def about(request):
    return render(request, 'about.html')


def contact(request):
    """Traiter les demandes de contact"""
    success = False
    error = None
    
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            subject = request.POST.get('subject', 'Question générale')
            message_text = request.POST.get('message', '')
            
            if not email or not message_text:
                error = "Veuillez remplir tous les champs obligatoires"
            else:
                full_name = f"{first_name} {last_name}".strip()

                # Sauvegarder en base de données
                ContactMessage.objects.create(
                    name=full_name,
                    email=email,
                    subject=subject,
                    message=message_text,
                )

                # Envoyer l'email au propriétaire du site
                try:
                    send_mail(
                        f'Nouveau message de contact: {subject}',
                        f'De: {full_name} ({email})\n\n{message_text}',
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.ADMINS[0][1]] if settings.ADMINS else ['admin@safeplace.com'],
                        fail_silently=True
                    )
                except Exception:
                    pass
                
                # Envoyer une confirmation à l'utilisateur
                try:
                    send_mail(
                        'Votre message a été reçu',
                        f'Bonjour {first_name},\n\nMerci de nous avoir contacté. Nous vous répondrons dans les plus brefs délais.\n\nThe SafePlace by K',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=True
                    )
                except Exception:
                    pass
                
                success = True
        except Exception as e:
            error = f"Erreur lors de l'envoi du message: {str(e)}"
    
    context = {'success': success, 'error': error}
    return render(request, 'contact.html', context)


def access_denied(request):
    """Page d'accès refusé"""
    return render(request, 'access_denied.html', status=403)


def loading(request):
    return render(request, 'loading.html')
