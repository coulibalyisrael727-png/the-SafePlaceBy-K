from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth import get_user_model, login
import os
import json

from .models import Episode, LiveStream, Category, Subscription, ContactMessage
from .auth import owner_required, subscriber_required


User = get_user_model()

from django.http import Http404, HttpResponse
import mimetypes
from urllib.parse import urlparse



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
            episodes_filtered = episodes.filter(category__id=selected_cat)
        else:
            slug = slugify(str(selected_cat).replace('_', '-'))
            cat_ids = [
                c.id for c in categories
                if slugify(c.name) == slug
            ]
            episodes_filtered = episodes.filter(category_id__in=cat_ids) if cat_ids else episodes.none()
    else:
        episodes_filtered = episodes
    context = {'episodes': episodes_filtered, 'categories': categories, 'selected_cat': selected_cat}
    return render(request, 'podcasts.html', context)


def videos(request):
    episodes = Episode.objects.filter(is_published=True, episode_type='video')
    categories = Category.objects.all()
    selected_cat = request.GET.get('categorie')
    if selected_cat:
        if str(selected_cat).isdigit():
            episodes_filtered = episodes.filter(category__id=selected_cat)
        else:
            slug = slugify(str(selected_cat).replace('_', '-'))
            cat_ids = [c.id for c in categories if slugify(c.name) == slug]
            episodes_filtered = episodes.filter(category_id__in=cat_ids) if cat_ids else episodes.none()
    else:
        episodes_filtered = episodes
    context = {'episodes': episodes_filtered, 'categories': categories, 'selected_cat': selected_cat}
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
    total_subscribers = Subscription.objects.filter(is_active=True).count()
    recent_subscribers = Subscription.objects.filter(is_active=True).order_by('-created_at')[:5]

    context = {
        'episodes': episodes,
        'total_episodes': total_episodes,
        'total_views': total_views,
        'total_subscribers': total_subscribers,
        'recent_subscribers': recent_subscribers,
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
    """Return a dict from JSON body or form POST."""
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


def _parse_bool(value):
    return str(value).lower() in ('true', '1', 'yes', 'on', 'checked')


def register(request):
    """Page d'inscription gratuite à la communauté SafePlace."""
    subscriber_count = Subscription.objects.filter(is_active=True).count()

    if request.method == 'POST':
        data = _parse_post_or_json(request)
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        password_confirm = data.get('password_confirm') or ''
        notify_podcasts = _parse_bool(data.get('notify_podcasts'))
        notify_live = _parse_bool(data.get('notify_live'))
        notify_videos = _parse_bool(data.get('notify_videos'))
        photo_url = (data.get('photo_url') or '').strip()

        errors = []
        if not first_name:
            errors.append('Le prénom est obligatoire.')
        if not email or '@' not in email:
            errors.append('Une adresse e-mail valide est requise.')
        if not password or len(password) < 8:
            errors.append('Le mot de passe doit contenir au moins 8 caractères.')
        if password != password_confirm:
            errors.append('Les mots de passe ne correspondent pas.')

        existing_user = User.objects.filter(username=email).first()
        if existing_user:
            errors.append('Un compte existe déjà avec cette adresse e-mail.')

        if errors:
            response_data = {'success': False, 'error': ' '.join(errors)}
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in (request.META.get('CONTENT_TYPE') or ''):
                return JsonResponse(response_data)
            return render(request, 'register.html', {
                'subscriber_count': subscriber_count,
                'error_message': response_data['error'],
                'form_data': data,
            })

        # Créer le compte utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)

        # Enregistrer ou mettre à jour l'abonnement
        Subscription.objects.update_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'photo_url': photo_url,
                'notify_podcasts': notify_podcasts,
                'notify_live': notify_live,
                'notify_videos': notify_videos,
                'is_active': True,
            }
        )

        response_data = {'success': True, 'message': 'Compte créé avec succès. Bienvenue !'}
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in (request.META.get('CONTENT_TYPE') or ''):
            return JsonResponse(response_data)

        return render(request, 'register.html', {
            'subscriber_count': subscriber_count,
            'success_message': response_data['message'],
        })

    return render(request, 'register.html', {'subscriber_count': subscriber_count})


def about(request):
    return render(request, 'about.html')


def contact(request):
    """Traiter les demandes de contact"""
    success = False
    error = None

    if request.method == 'POST':
        try:
            first_name   = request.POST.get('first_name', '')
            last_name    = request.POST.get('last_name', '')
            email        = request.POST.get('email', '')
            subject      = request.POST.get('subject', 'Question générale')
            message_text = request.POST.get('message', '')

            if not email or not message_text:
                error = "Veuillez remplir tous les champs obligatoires"
            else:
                full_name = f"{first_name} {last_name}".strip()

                ContactMessage.objects.create(
                    name=full_name,
                    email=email,
                    subject=subject,
                    message=message_text,
                )

                try:
                    send_mail(
                        f'Nouveau message de contact: {subject}',
                        f'De: {full_name} ({email})\n\n{message_text}',
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.ADMINS[0][1]] if settings.ADMINS else ['admin@safeplace.com'],
                        fail_silently=True
                    )
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning("Erreur envoi email: %s", str(e))

                try:
                    send_mail(
                        'Votre message a été reçu',
                        f'Bonjour {first_name},\n\nMerci de nous avoir contacté. Nous vous répondrons dans les plus brefs délais.\n\nThe SafePlace by K',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=True
                    )
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning("Erreur envoi email confirmation: %s", str(e))

                success = True
        except Exception as e:
            error = f"Erreur lors de l'envoi du message: {str(e)}"

    context = {'success': success, 'error': error}
    return render(request, 'contact.html', context)


def access_denied(request):
    """Page d'accès refusé"""
    return render(request, 'access_denied.html', status=403)


def download_episode(request, pk):
    """Télécharger (forcé) un épisode (audio) ou une vidéo depuis une URL hébergée.

    Comme audio_url/video_url sont des URL externes, on ne peut pas toujours "proxy" le contenu.
    Ici on renvoie une redirection vers l’URL source tout en forçant un filename si possible.
    """
    episode = get_object_or_404(Episode, pk=pk, is_published=True)

    # Détermine le fichier à télécharger
    source_url = (episode.audio_url or '').strip() if episode.episode_type == 'podcast' else (episode.video_url or '').strip()
    if not source_url:
        raise Http404("Fichier non disponible")

    # Tentative d’un nom de fichier à partir de l’URL
    parsed = urlparse(source_url)
    filename = parsed.path.split('/')[-1] or ''
    if not filename:
        filename = f"{episode.title}.mp3" if episode.episode_type == 'podcast' else f"{episode.title}.mp4"

    content_type, _ = mimetypes.guess_type(filename)

    # Redirection + headers de téléchargement : certains navigateurs ignorent ces headers sur redirection.
    # On utilise donc un petit body HttpResponse pour appliquer les headers.
    resp = HttpResponse(status=302)
    if content_type:
        resp['Content-Type'] = content_type
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    resp['Location'] = source_url
    return resp


def loading(request):
    return render(request, 'loading.html')
